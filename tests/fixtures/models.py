from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ENUM, ARRAY
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


STORE_MANAGER = 1
SHIFT_MANAGER = 2
HOURLY_EMPLOYEE = 3

EMPLOYEE_JOBS = {
    STORE_MANAGER: 'store manager',
    SHIFT_MANAGER: 'shift manager',
    HOURLY_EMPLOYEE: 'hourly employee',
}


class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True)
    years_experience = Column(Integer)
    first_name = Column(String(length=50))
    last_name = Column(String(length=50))
    job = Column(ENUM(*EMPLOYEE_JOBS.values(), name='job_types'))
    dob = Column(DateTime)
    is_active = Column(Boolean)
    preferred_shift_ids = Column(ARRAY(Integer))
