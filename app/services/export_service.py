from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import FuelEstimateLog
from app.schemas.exports import EstimateLogRow


def estimate_log_rows(db: Session, limit: int = 250) -> list[EstimateLogRow]:
    logs = db.scalars(select(FuelEstimateLog).order_by(desc(FuelEstimateLog.created_at)).limit(limit)).all()
    return [
        EstimateLogRow(
            created_at=log.created_at.isoformat(),
            origin=log.origin_icao,
            destination=log.destination_icao,
            aircraft_profile=log.aircraft_profile,
            estimated_total_fuel_kg=round(log.estimated_total_fuel_kg, 2),
            estimated_cost=round(log.estimated_cost, 2) if log.estimated_cost is not None else None,
            predicted_burn_kg=round(log.predicted_burn_kg, 2) if log.predicted_burn_kg is not None else None,
            anomaly_flag=log.anomaly_flag,
            note=log.note,
        )
        for log in logs
    ]
