from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app, abort
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

admin_routes = Blueprint('admin', __name__, template_folder='templates')

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Run this once in Python shell to create admin user
def create_admin():
    from app import db
    db.create_all()
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0) 

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def delete_file(self, upload_folder):
        """
        Helper method to delete the photo file from the filesystem.
        Pass the folder where files are saved, e.g., 'static/uploads'.
        """
        file_path = os.path.join(upload_folder, self.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    blog = db.relationship('BlogPost', backref=db.backref('comments', lazy=True))


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)  # To mark message as read/unread

# Post detail with comments and comment form (viewer side)
@admin_routes.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = BlogPost.query.get_or_404(post_id)

    if request.method == 'POST':
        name = request.form.get('name')
        text = request.form.get('text')

        if not name or not text:
            flash('Name and Comment text are required.', 'danger')
            return redirect(url_for('admin.post_detail', post_id=post_id))

        # Save comment but mark as unapproved initially
        comment = Comment(blog_id=post.id, name=name, text=text, approved=False)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been submitted for review.', 'success')
        return redirect(url_for('admin.post_detail', post_id=post_id))

    # Show only approved comments
    approved_comments = Comment.query.filter_by(blog_id=post.id, approved=True).order_by(Comment.created_at.desc()).all()
    return render_template('admin/post_detail.html', post=post, comments=approved_comments)

# Like post (can be via POST form or AJAX)
@admin_routes.route('/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    post.likes = (post.likes or 0) + 1
    db.session.commit()
    # Redirect back to post detail or referrer
    return redirect(request.referrer or url_for('admin.post_detail', post_id=post_id))

# Admin: View all comments (with blog post info)
@admin_routes.route('/comments')
def view_comments():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=comments)

# Admin: Approve comment
@admin_routes.route('/comment/approve/<int:comment_id>', methods=['POST'])
def approve_comment(comment_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    comment = Comment.query.get_or_404(comment_id)
    comment.approved = True
    db.session.commit()
    flash('Comment approved successfully.', 'success')
    return redirect(url_for('admin.view_comments'))

# Admin: Delete comment
@admin_routes.route('/comment/delete/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.', 'success')
    return redirect(url_for('admin.view_comments'))
