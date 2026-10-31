from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.core.database.session import get_db
from app.core.dependencies.integration import require_admin
from app.models.scenario import Scenario
from app.api.v1.schemas.scenario import (
    ScenarioCreate, ScenarioUpdate, ScenarioToggle, ScenarioResponse, ScenarioPage,
)
from app.services.scenario_validation import validate_definition

router = APIRouter(prefix="/scenarios", tags=["scenarios"], dependencies=[Depends(require_admin)])


def find(db, scenario_id, lock=False):
    query = db.query(Scenario).filter(Scenario.id == scenario_id)
    if lock:
        query = query.with_for_update()
    scenario = query.first()
    if scenario is None:
        raise HTTPException(404, "Scenario not found")
    return scenario


def check_revision(scenario, expected):
    if scenario.revision != expected:
        raise HTTPException(409, "Scenario was changed. Reload before saving")


@router.get("/", response_model=ScenarioPage)
def list_scenarios(object_id: UUID, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    query = db.query(Scenario).filter(Scenario.object_id == object_id)
    return {"items": query.order_by(Scenario.created_at.desc(), Scenario.id).offset(skip).limit(limit).all(), "total": query.count()}


@router.post("/", response_model=ScenarioResponse, status_code=201)
def create_scenario(payload: ScenarioCreate, db: Session = Depends(get_db), user: dict = Depends(require_admin)):
    validate_definition(db, payload)
    scenario = Scenario(**payload.model_dump(mode="json"), created_by=user["user_id"])
    # SQLAlchemy UUID columns require UUID values, while JSON references use strings.
    scenario.object_id = payload.object_id
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.get("/{scenario_id}", response_model=ScenarioResponse)
def read_scenario(scenario_id: UUID, db: Session = Depends(get_db)):
    return find(db, scenario_id)


@router.put("/{scenario_id}", response_model=ScenarioResponse)
def update_scenario(scenario_id: UUID, payload: ScenarioUpdate, db: Session = Depends(get_db)):
    scenario = find(db, scenario_id, lock=True)
    check_revision(scenario, payload.expected_revision)
    validate_definition(db, payload)
    for key, value in payload.model_dump(mode="json", exclude={"expected_revision", "object_id"}).items():
        setattr(scenario, key, value)
    scenario.object_id = payload.object_id
    scenario.revision += 1
    db.commit()
    db.refresh(scenario)
    return scenario


@router.patch("/{scenario_id}", response_model=ScenarioResponse)
def toggle_scenario(scenario_id: UUID, payload: ScenarioToggle, db: Session = Depends(get_db)):
    scenario = find(db, scenario_id, lock=True)
    check_revision(scenario, payload.expected_revision)
    if payload.enabled:
        validate_definition(db, ScenarioCreate.model_validate(scenario, from_attributes=True))
    scenario.enabled = payload.enabled
    scenario.revision += 1
    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/{scenario_id}", status_code=204)
def delete_scenario(scenario_id: UUID, expected_revision: int = Query(..., ge=1), db: Session = Depends(get_db)):
    scenario = find(db, scenario_id, lock=True)
    check_revision(scenario, expected_revision)
    db.delete(scenario)
    db.commit()
    return Response(status_code=204)
