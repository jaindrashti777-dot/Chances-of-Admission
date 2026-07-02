import pytest
from backend.app.models.college import College
from backend.app.schemas.college import CollegeCreate
from backend.app.repositories.college import college_repo

def test_create_college(db_session):
    college_in = CollegeCreate(
        name="Test NIT",
        state="Test State",
        institute_type="NIT",
        is_active=True
    )
    college = college_repo.create(db_session, obj_in=college_in)
    
    assert college.id is not None
    assert college.name == "Test NIT"
    assert college.institute_type == "NIT"

def test_get_college(db_session):
    college_in = CollegeCreate(name="Test IIIT", state="Test State", institute_type="IIIT")
    college = college_repo.create(db_session, obj_in=college_in)
    
    college_fetched = college_repo.get(db_session, id=college.id)
    assert college_fetched is not None
    assert college_fetched.name == "Test IIIT"

def test_get_by_name(db_session):
    college_in = CollegeCreate(name="Unique NIT", state="Test State", institute_type="NIT")
    college_repo.create(db_session, obj_in=college_in)
    
    college_fetched = college_repo.get_by_name(db_session, name="Unique NIT")
    assert college_fetched is not None
    assert college_fetched.id is not None
