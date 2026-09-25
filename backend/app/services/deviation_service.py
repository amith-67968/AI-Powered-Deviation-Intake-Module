from sqlalchemy.orm import Session
from app.models.deviation import Deviation
from app.schemas.deviation import DeviationCreate, DeviationUpdate


def create_deviation(db: Session, payload: DeviationCreate) -> Deviation:
    deviation = Deviation(**payload.model_dump())
    db.add(deviation)
    db.commit()
    db.refresh(deviation)
    return deviation


def list_deviations(db: Session, query: str | None = None) -> list[Deviation]:
    statement = db.query(Deviation)
    if query:
        term = f"%{query.strip()}%"
        statement = statement.filter(Deviation.title.ilike(term) | Deviation.batch_lot_number.ilike(term) | Deviation.site.ilike(term))
    return statement.order_by(Deviation.created_at.desc()).all()


def get_deviation(db: Session, deviation_id: int) -> Deviation | None:
    return db.get(Deviation, deviation_id)


def update_deviation(db: Session, record: Deviation, payload: DeviationUpdate) -> Deviation:
    for field, value in payload.model_dump().items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def delete_deviation(db: Session, record: Deviation) -> None:
    db.delete(record)
    db.commit()
