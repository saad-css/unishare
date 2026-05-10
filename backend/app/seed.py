from .extensions import db
from .models import Major, Course

def seed_data():
    # Prevent duplicate data (only seed once)
    if Major.query.first():
        return

    # Create sample majors
    cs = Major(name="Computer Science")
    it = Major(name="Information Technology")
    
    db.session.add_all([cs, it])
    db.session.commit()


    # Create sample courses
    db.session.add_all([
        Course(name="Data Structures", major_id=cs.id),
        Course(name="Algorithms", major_id=cs.id),
        Course(name="Networks", major_id=it.id),
    ])

    db.session.commit()
