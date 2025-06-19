from fastapi import APIRouter, Request, Depends
import os, version
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db_models import Release
from models import ReleaseResponse
from fastapi_cache.decorator import cache
from limiter import limiter
from database import get_db
from utils import fetch_github_release
from datetime import datetime
from logger import logger
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.get("/")
@cache(expire=3600)
@limiter.limit(os.getenv('FETCH_RATELIMIT_INTERVAL', '25/minute'))
async def get_latest_release(request: Request, db = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Release).order_by(Release.id.desc()))
        release_data = result.scalars().first()

        if not release_data:
            repository_owner = os.getenv('GITHUB_REPOSITORY_OWNER')
            repository_name = os.getenv('GITHUB_REPOSITORY_NAME')

            if repository_owner and repository_name:
                github_api_data = await fetch_github_release(repository_owner, repository_name)

                if "error" in github_api_data:
                    logger.error(
                        "Fetching fallback release data from GitHub API failed: %s", 
                        github_api_data["error"]
                    )
                
                elif github_api_data:
                    try:
                        published_datetime = datetime.fromisoformat(github_api_data['published_at'].replace('Z', '+00:00'))
                        
                        new_fallback_release = Release(
                            name=github_api_data.get('name', ''),
                            tag_name=github_api_data['tag_name'],
                            published_at=published_datetime,
                            html_url=github_api_data['html_url']
                        )
                        
                        session.add(new_fallback_release)
                        await session.commit()

                        release_data = new_fallback_release

                        logger.info("Fetched fallback initial release from GitHub API: %s", github_api_data['tag_name'])
                        
                    except (ValueError, TypeError) as date_error:
                        logger.error("Invalid date format from GitHub API: %s", str(date_error))

            else:
                logger.warning("Fetching fallback release data from GitHub API is disabled: Missing GITHUB_REPOSITORY_OWNER or GITHUB_REPOSITORY_NAME environment variables!")

        response_data = None

        if release_data:
            response_data = ReleaseResponse(
                name=release_data.name,
                tag_name=release_data.tag_name,
                published_at=release_data.published_at.isoformat(),
                html_url=release_data.html_url
            )
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "application_name": "FastAPI GitHub Release Tracker",
                "application_description": (
                    "A lightweight API that tracks the latest GitHub releases with webhook support and caching to optimize GitHub API usage."
                ),
                "application_version": version.__version__,
                "data": response_data,
            })
        )
