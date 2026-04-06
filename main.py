from fastapi import FastAPI, Path, HTTPException, Query, Depends
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import PatientDB

app = FastAPI()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



class Patient(BaseModel):

    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(...)]
    city: Annotated[str, Field(...)]
    age: Annotated[int, Field(..., gt=0, lt=120)]
    gender: Annotated[Literal['male', 'female', 'others'], Field(...)]
    height: Annotated[float, Field(..., gt=0)]
    weight: Annotated[float, Field(..., gt=0)]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Literal['male', 'female', 'others']] = None
    height: Optional[float] = None
    weight: Optional[float] = None




@app.get("/")
def hello():
    return {'message': 'Patient Management System API'}

@app.get("/about")
def about():
    return {'message': 'A fully functional API to manage your patient records'}



@app.get("/view")
def view(db: Session = Depends(get_db)):
    patients = db.query(PatientDB).all()
    return patients



@app.get('/patient/{patient_id}')
def view_patient(
    patient_id: str = Path(..., description='ID of the patient', examples={"ex": {"value": "P001"}}),
    db: Session = Depends(get_db)
):

    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')

    return patient



@app.get('/sort')
def sort_patients(
    sort_by: str = Query(...),
    order: str = Query('asc'),
    db: Session = Depends(get_db)
):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Select from {valid_fields}')

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order')

    patients = db.query(PatientDB).all()

    reverse = True if order == 'desc' else False

    sorted_data = sorted(patients, key=lambda x: getattr(x, sort_by), reverse=reverse)

    return sorted_data



@app.post('/create')
def create_patient(patient: Patient, db: Session = Depends(get_db)):

    existing = db.query(PatientDB).filter(PatientDB.id == patient.id).first()

    if existing:
        raise HTTPException(status_code=400, detail='Patient already exists')

    new_patient = PatientDB(**patient.model_dump())

    db.add(new_patient)
    db.commit()

    return {'message': 'patient created successfully'}



@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate, db: Session = Depends(get_db)):

    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')

    update_data = patient_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(patient, key, value)

    # Recalculate BMI & verdict using Pydantic model
    temp = Patient(
        id=patient_id,
        name=patient.name,
        city=patient.city,
        age=patient.age,
        gender=patient.gender,
        height=patient.height,
        weight=patient.weight
    )

    patient.bmi = temp.bmi
    patient.verdict = temp.verdict

    db.commit()

    return {'message': 'patient updated'}



@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str, db: Session = Depends(get_db)):

    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')

    db.delete(patient)
    db.commit()

    return {'message': 'patient deleted successfully'}