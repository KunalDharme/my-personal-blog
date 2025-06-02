from flask import Flask, render_template, redirect, url_for, request, session, flash
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from admin.models import ContactMessage, BlogPost, Comment  # Ensure all models are imported
from config import Config
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Register admin blueprint
from admin.routes import admin_routes
app.register_blueprint(admin_routes, url_prefix='/admin')

# Upload folder config
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create tables manually (Option A fix)
with app.app_context():
    db.create_all()

# Dummy blog list for demo — replace with DB queries if needed
blogs = [
    {
        'id': 1,
        'title': "The Hounds of Baskerville",
        'content': "This is a mystery about an ancient curse...",
        'date': datetime(2025, 5, 31)
    },
    {
        'id': 2,
        'title': "The Reichenbach Fall",
        'content': "Sherlock faces his greatest enemy...",
        'date': datetime(2025, 5, 28)
    }
]

# Public pages
@app.route('/')
@app.route("/index.html")
def home():
    recent_blogs = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('index.html', blogs=recent_blogs)

@app.route('/blog.html')
def all_blogs():
    all_blogs = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', blogs=all_blogs)

@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    blog = next((b for b in blogs if b['id'] == blog_id), None)
    return render_template('blog_detail.html', blog=blog)

@app.route('/blog-baskerville.html')
def blog_baskerville():
    return render_template('blog-baskerville.html')

@app.route('/photos.html', methods=['GET', 'POST'])
def photos():
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

@app.route("/admin/templates/admin/admin.html")
def admin_panel():
    return render_template("admin.html")

@app.route('/post/<slug>', methods=['GET', 'POST'])
def post(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()

    if request.method == 'POST':
        name = request.form['name']
        text = request.form['text']
        comment = Comment(blog=post, name=name, text=text)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post', slug=slug))  # Redirect after POST to show new comment

    comments = Comment.query.filter_by(blog=post).order_by(Comment.created_at.desc()).all()
    return render_template('post.html', post=post, comments=comments)


if __name__ == '__main__':
    app.run(debug=True)
