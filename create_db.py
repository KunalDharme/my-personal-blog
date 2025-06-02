from app import app, db
from admin.models import AdminUser, BlogPost, Photo, Comment

with app.app_context():
    db.create_all()
    print("Database tables created successfully.")
