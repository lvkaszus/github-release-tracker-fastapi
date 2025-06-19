import httpx
import version
from logger import logger

async def fetch_github_release(owner: str, repo: str) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": f"FastAPI-GitHub-Releases-API-Proxy-by-@lvkaszus/{version.__version__}"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers=headers,
            )
            
            if response.status_code == 404:
                return {"error": "Repository or Release Not Found!"}

            elif response.status_code == 403:
                return {"error": "GitHub API Ratelimit Exceeded!"}

            elif response.status_code >= 400:
                return {"error": f"GitHub API Error! - {response.status_code} - {response.text}"}
                
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"GitHub API error: {str(e)}")
        return {"error": f"HTTP Error occurred: {e.response.status_code}"}
        
    except httpx.TimeoutException:
        logger.error("GitHub API Request Timed out")
        return {"error": "Request to GitHub API Timed out"}
        
    except httpx.RequestError as e:
        logger.error(f"Network Error: {str(e)}")
        return {"error": f"Network Error: {str(e)}"}
        
    except (ValueError, TypeError) as e:
        logger.error(f"Data Parsing Error: {str(e)}")
        return {"error": "Invalid Response Format from GitHub API"}
        
    except Exception as e:
        logger.exception("Unexpected Error in fetch_github_release()")
        return {"error": f"Unexpected Error: {str(e)}"}
