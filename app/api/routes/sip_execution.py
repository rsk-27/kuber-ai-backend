from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.sip_service import execute_due_sips


router = APIRouter()


@router.post("/sips/execute-due")
def execute_sips(
    db: Session = Depends(get_db)
):
    results = execute_due_sips(
        db=db,
        today=date.today()
    )

    return {
        "executed": len(results),
        "installments": results
    }