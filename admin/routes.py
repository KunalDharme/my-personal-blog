import os
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from extensions import db 
from .models import AdminUser, BlogPost, Photo, ContactMessage, Comment


admin_routes = Blueprint('admin', __name__, template_folder='templates')

# Use absolute path for uploads folder inside your Flask project
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

    return render_template('admin/login.html')


@admin_routes.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    total_posts = BlogPost.query.count()
    recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(5).all()
    return render_template('admin/admin_dashboard.html', total_posts=total_posts, recent_posts=recent_posts)


@admin_routes.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    return redirect(url_for('admin.login'))


@admin_routes.route('/posts')
def posts():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    all_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/admin_posts.html', posts=all_posts)


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

    return render_template('admin/new_post.html')


@admin_routes.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    post = BlogPost.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.slug = request.form['slug']
        post.content = request.form['content']

        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin.posts'))

    return render_template('admin/edit_post.html', post=post)


@admin_routes.route('/post/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin.posts'))


@admin_routes.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))

    admin = AdminUser.query.get(session.get('admin_id'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not check_password_hash(admin.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        else:
            admin.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))

    return render_template('admin/change_password.html')


@admin_routes.route('/photos', methods=['GET', 'POST'])
def upload_photos():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Ensure UPLOAD_FOLDER exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # Save photo record in DB
            photo = Photo(filename=filename)
            db.session.add(photo)
            db.session.commit()

            flash('Photo uploaded successfully!', 'success')
            return redirect(url_for('admin.upload_photos'))
        else:
            flash('File type not allowed.', 'danger')

    photos = Photo.query.order_by(Photo.id.desc()).all()
    return render_template('admin/photos.html', photos=photos)


@admin_routes.route('/photo/delete/<int:photo_id>', methods=['POST'])
def delete_photo(photo_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    photo = Photo.query.get_or_404(photo_id)

    # Delete file from static/uploads folder
    file_path = os.path.join(current_app.root_path, 'static/uploads', photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(photo)
    db.session.commit()
    flash('Photo deleted successfully!', 'success')
    return redirect(url_for('admin.upload_photos'))

@admin_routes.route('/messages')
def view_messages():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@admin_routes.route('/message/read/<int:message_id>')
def mark_as_read(message_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    msg = ContactMessage.query.get_or_404(message_id)
    msg.read = not msg.read  # Toggle read status
    db.session.commit()
    return redirect(url_for('admin.view_messages'))

# View all comments (with blog post info)
@admin_routes.route('/comments')
def view_comments():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # Get all comments ordered by newest first
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=comments)

# Delete comment by ID
@admin_routes.route('/comment/delete/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('admin.view_comments'))

@admin_routes.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    post.likes = post.likes + 1 if post.likes else 1
    db.session.commit()
    return redirect(request.referrer or url_for('admin.dashboard'))
