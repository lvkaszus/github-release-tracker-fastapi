from fastapi import APIRouter, Request, HTTPException, Depends
from limiter import limiter
import hmac, hashlib, os, logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal, get_db
from logger import logger
from db_models import Release
from models import GitHubRelease
from fastapi_cache import FastAPICache
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger("security")

@router.post(f"/api/{os.getenv('CUSTOM_WEBHOOK_URL_PATH', 'webhook')}")
@limiter.limit(os.getenv('UPDATE_RATELIMIT_INTERVAL', '25/minute'))
async def handle_webhook(request: Request, db = Depends(get_db)):
    async with db as session:
        body = await request.body()

        signature = request.headers.get("X-Hub-Signature-256", "")
        
        secret = os.getenv("WEBHOOK_SECRET").encode()
        digest = hmac.new(secret, body, hashlib.sha256).hexdigest()
        expected_signature = f"sha256={digest}"

        if not hmac.compare_digest(expected_signature, signature):
            logger.warning("Invalid HMAC Signature from %s!", request.client.host)

            return JSONResponse(
                status_code=403,
                content={
                    "error": "Invalid HMAC Signature!"
                }
            )


        event_type = request.headers.get("X-GitHub-Event")

        if event_type != "release":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "Ignored!"
                }
            )

        payload = await request.json()

        if payload.get("action") != "published":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "Ignored!"
                }
            )

        release_data = payload["release"]
        release = GitHubRelease(**release_data)
        published_at_datetime = datetime.fromisoformat(release.published_at.replace('Z', '+00:00'))

        new_release = Release(
            name=release.name,
            tag_name=release.tag_name,
            published_at=published_at_datetime,
            html_url=release.html_url
        )

        session.add(new_release)
        await session.commit()

        await FastAPICache.clear(key="get_latest_release")


        logger.info("Webhook processed successfully! %s", release.tag_name)

        return JSONResponse(
            status_code=202,
            content={
                "success": "Accepted!"
            }
        )
