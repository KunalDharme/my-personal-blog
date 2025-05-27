from extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Run this once in Python shell to create admin user
def create_admin():
    from app import db
    db.create_all()
    if not AdminUser.query.filter_by(username='watson').first():
        admin = AdminUser(username='watson', password_hash=generate_password_hash('blog221B'))
        db.session.add(admin)
        db.session.commit()
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'))
    name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    blog = db.relationship('BlogPost', backref=db.backref('comments', lazy=True))
