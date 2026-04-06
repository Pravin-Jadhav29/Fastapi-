from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.orm import declarative_base
from database import engine

Base = declarative_base()

class PatientDB(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True)
    name = Column(String)
    city = Column(String)
    age = Column(Integer)
    gender = Column(String)
    height = Column(Float)
    weight = Column(Float)
    bmi = Column(Float)
    verdict = Column(String)

Base.metadata.create_all(bind=engine)