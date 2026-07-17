from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created (or already existed).")

    # Safely add new columns if they don't exist yet (for databases created
    # before these fields were introduced).
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    existing_columns = [col['name'] for col in inspector.get_columns('user')]

    with db.engine.connect() as conn:
        if 'email' not in existing_columns:
            conn.execute(text('ALTER TABLE user ADD COLUMN email VARCHAR(150)'))
            print("Added 'email' column to user table.")
        if 'reset_token' not in existing_columns:
            conn.execute(text('ALTER TABLE user ADD COLUMN reset_token VARCHAR(100)'))
            print("Added 'reset_token' column to user table.")
        if 'reset_token_expiry' not in existing_columns:
            conn.execute(text('ALTER TABLE user ADD COLUMN reset_token_expiry DATETIME'))
            print("Added 'reset_token_expiry' column to user table.")
        conn.commit()

    existing_admin = User.query.filter_by(username='admin').first()
    if not existing_admin:
        admin = User(username='admin', role='admin')
        admin.set_password('changeme123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: username='admin', password='changeme123'")
    else:
        print("Admin user already exists, skipping.")