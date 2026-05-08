import csv
import io

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_api_key
from app.schemas.exports import EstimateLogRow
from app.services.export_service import estimate_log_rows

router = APIRouter(prefix="/exports", tags=["exports"], dependencies=[Depends(require_api_key)])


@router.get("/estimates", response_model=None)
def export_estimates(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    limit: int = Query(default=250, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> list[EstimateLogRow] | Response:
    rows = estimate_log_rows(db, limit=limit)
    if format == "json":
        return rows

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(EstimateLogRow.model_fields))
    writer.writeheader()
    writer.writerows(row.model_dump() for row in rows)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fuel_estimates.csv"},
    )
