# create_db.py
from app import app, db
from admin.models import AdminUser, BlogPost, Comment, ContactMessage, Photo

def initialize_database():
    with app.app_context():
        db.drop_all()  # Drop all tables (optional, for full reset)
        db.create_all()
        print("✅ Fresh database created.")

        # Create default admin user
        if not AdminUser.query.filter_by(username='watson').first():
            admin = AdminUser(username='watson')
            admin.set_password('blog221B')
            db.session.add(admin)
            db.session.commit()
            print("🛡️ Default admin 'watson' created with password 'blog221B'.")

if __name__ == "__main__":
    initialize_database()
