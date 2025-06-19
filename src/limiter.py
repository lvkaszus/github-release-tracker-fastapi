from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import os

limiter = Limiter(key_func=get_remote_address, storage_uri=os.getenv("REDIS_URI"))

async def init_limiter(app):    
    app.state.limiter = limiter
    
    return limiter
