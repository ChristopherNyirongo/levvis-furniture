import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# If RENDER_DISK_PATH is set (only true when running on Render with a
# persistent disk attached), store the database and uploads there instead
# of the normal local folders. Locally, this variable won't exist, so
# everything falls back to behaving exactly as it does today.
DATA_DIR = os.environ.get('RENDER_DISK_PATH', BASE_DIR)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(DATA_DIR, 'instance', 'levvis.sqlite3')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload size
    WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '260979369001')