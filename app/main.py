from fastapi import FastAPI

from app.config import settings
from app.api.routes.chat import router as chat_router
from app.api.routes.users import router as users_router
from app.api.routes.purchases import router as purchases_router
from app.api.routes.ledger import router as ledger_router
from app.api.routes.sips import router as sips_router
from app.api.routes.sip_execution import router as sip_execution_router
from app.database import engine, Base
from app.logging_config import configure_logging
from app import models


app = FastAPI(title=settings.app_name)
configure_logging()
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Simplify Money backend is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(chat_router)
app.include_router(users_router)
app.include_router(purchases_router)
app.include_router(ledger_router)
app.include_router(sips_router)
app.include_router(sip_execution_router)