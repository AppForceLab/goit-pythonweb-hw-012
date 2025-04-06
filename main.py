# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.api.auth import router as auth_router
from src.api.contacts import router as contacts_router
from src.database.db import engine
from src.database.models import Base
from src.services.limiter import limiter
templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔥 STARTING LIFESPAN")

    from sqlalchemy.exc import OperationalError
    import asyncio

    for i in range(10):
        try:
            async with engine.begin() as conn:
                print("📦 Creating tables...")
                await conn.run_sync(Base.metadata.create_all)
                print("✅ Tables created.")
                break
        except OperationalError:
            print(f"⏳ Attempt {i + 1}/10: Waiting for the database...")
            await asyncio.sleep(2)
    else:
        raise RuntimeError("❌ Could not connect to the database after 10 attempts.")

    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(contacts_router, prefix="/contacts")
