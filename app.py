from flask import Flask, render_template, redirect, url_for, request, session, flash
from extensions import db
from werkzeug.utils import secure_filename
from datetime import datetime
import os

# Import config and models
from config import Config
from admin.models import ContactMessage, BlogPost, Comment

# Initialize Flask app and config
app = Flask(__name__)
app.config.from_object(Config)

# Upload folder configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()

# Register admin blueprint
from admin.routes import admin_routes
app.register_blueprint(admin_routes, url_prefix='/admin')

# ------------------ Public Routes ------------------

@app.route('/')
@app.route("/index.html")
def home():
    """Homepage showing recent blogs"""
    recent_blogs = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('index.html', blogs=recent_blogs)

@app.route('/blog.html')
def all_blogs():
    """All blog posts"""
    all_blogs = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', blogs=all_blogs)

@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    """Fallback blog detail page if needed (uses dummy data)"""
    # Optional: could remove if not using dummy blogs
    return redirect(url_for('all_blogs'))

@app.route('/photos.html', methods=['GET', 'POST'])
def photos():
    """Photo upload and display page"""
    if request.method == 'POST':
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Photo uploaded successfully!', 'success')
                return redirect(url_for('photos'))
            else:
                flash('Invalid file type.', 'danger')

    uploaded_photos = os.listdir(app.config['UPLOAD_FOLDER'])
    uploaded_photos = [f for f in uploaded_photos if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('photos.html', photo_list=uploaded_photos)

@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    """Contact form handling"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        contact_message = ContactMessage(name=name, email=email, message=message)
        db.session.add(contact_message)
        db.session.commit()

        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/help.html')
def help():
    """help"""
    return render_template(url_for('help'))

# ------------------ Blog Detail + Comments ------------------

@app.route('/post/<slug>', methods=['GET', 'POST'])
def post(slug):
    """Detailed blog post view with comments"""
    post = BlogPost.query.filter_by(slug=slug).first_or_404()

    if request.method == 'POST':
        name = request.form['name']
        text = request.form['text']
        comment = Comment(blog=post, name=name, text=text)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post', slug=slug))  # PRG pattern

    comments = Comment.query.filter_by(blog=post).order_by(Comment.created_at.desc()).all()
    return render_template('post.html', post=post, comments=comments)

# ------------------ Admin Access Shortcut ------------------

@app.route("/admin/templates/admin/admin.html")
def admin_panel():
    """Shortcut route to admin panel (optional)"""
    return render_template("admin.html")

# ------------------ Run App ------------------

if __name__ == '__main__':
    app.run(debug=True)
