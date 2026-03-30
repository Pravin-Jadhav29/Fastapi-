from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):

    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)

    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)
        

@app.get("/")
def hello():
    return {'message':'Patient Management System API'}

@app.get('/about')
def about():
    return {'message': 'A fully functional API to manage your patient records'}

@app.get('/view')
def view():
    data = load_data()

    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', example='P001')):
    # load all the patients
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    
    data = load_data()

    sort_order = True if order=='desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):

    # load existing data
    data = load_data()

    # check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # new patient add to the database
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save into the json file
    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient created successfully'})


# @app.put('/edit/{patient_id}')
# def update_patient(patient_id:str,patient_update:PatientUpdate):

#    data=load_data()

# #    check if patient exists ornot
#    if patient_id not in data:
#        raise HTTPException(status_code=404,detail='patient not')
   
#         # get current patient details
# existing_patient_details=data[patient_id]
# update_patient_info=Patient_update.model_dump(exclude_unset=True)

# for key,value in update_patient_info.items():
#     existing_patient_details[key]=value
   
# existing_patient_details['id']=Patient_id
# Patient_pydantic_obj=Patient(**existing_patient_details)

# existing_patient_details=Patient_pydantic_obj.model_dump(exclude='id')

# data[patient_id]=existing_patient_details

# save_data(data)

# return JSONResponse(status_code=200, content={'message':'patient updated'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    # Load data from JSON
    data = load_data()

    # Check if patient exists
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    # Get existing patient details
    existing_patient_details = data[patient_id]

    # Convert incoming data (only provided fields)
    update_patient_info = patient_update.model_dump(exclude_unset=True)

    # Update existing data with new values
    for key, value in update_patient_info.items():
        existing_patient_details[key] = value

    # Add id temporarily for validation
    existing_patient_details['id'] = patient_id

    # Convert dict → Pydantic model (validation + recalculation)
    patient_pydantic_obj = Patient(**existing_patient_details)

    # Convert back to dict (remove id)
    existing_patient_details = patient_pydantic_obj.model_dump(exclude='id')
# 
    data[patient_id] = existing_patient_details

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):

    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,details='patient not found')
    del data[patient_id]
    save_data(data)

    return JSONResponse(status_code=200,content={'message':'patient deleted succesfully'})




    
