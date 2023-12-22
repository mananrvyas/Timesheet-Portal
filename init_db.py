from main import app, db
from models import User

with app.app_context():
    db.create_all()
