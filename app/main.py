from fastapi import FastAPI
from app.routers import links, auth
from app.database import Base, engine
import time

time.sleep(30)
app = FastAPI(
    title="URL Shortener API",
    description="Сервис для сокращения ссылок с аналитикой, авторизацией и кэшированием.",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="", tags=["Auth"])
app.include_router(links.router, prefix="", tags=["Links"])