from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created (or already existed).")

    existing_admin = User.query.filter_by(username='admin').first()
    if not existing_admin:
        admin = User(username='admin', role='admin')
        admin.set_password('changeme123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: username='admin', password='changeme123'")
    else:
        print("Admin user already exists, skipping.")