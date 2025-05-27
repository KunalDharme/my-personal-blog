from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import AdminUser, BlogPost
from extensions import db

# Set the template folder so Flask can find templates under admin/templates
admin_routes = Blueprint('admin', __name__, template_folder='templates')

@admin_routes.route('/')
def admin_root():
    return redirect(url_for('admin.dashboard'))

@admin_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = AdminUser.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['admin_logged_in'] = True
            session['admin_id'] = user.id
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('admin/login.html')  # ✅ Correct path

@admin_routes.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    return render_template('admin/admin_dashboard.html')  # ✅ Move the file

@admin_routes.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

@admin_routes.route('/posts')
def posts():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    all_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/admin_posts.html', posts=all_posts)  # ✅ Correct template path

@admin_routes.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug']
        content = request.form['content']

        post = BlogPost(title=title, slug=slug, content=content)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('admin.posts'))

    return render_template('admin/new_post.html')  # ✅ Correct path

@admin_routes.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))

    admin = AdminUser.query.get(session.get('admin_id'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not check_password_hash(admin.password, current_password):
            flash('Current password is incorrect.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        else:
            admin.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))

    return render_template('admin/change_password.html')