from flask import Flask, render_template, redirect, url_for, request, session, flash
from extensions import db  # ✅ use extensions here
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)  # ✅ Properly loads class-based config


db.init_app(app)  # ✅ initialize here

from admin.routes import admin_routes
from admin.models import BlogPost, Comment  # ✅ Add this line

app.register_blueprint(admin_routes, url_prefix='/admin')

# Public pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/index.html")
def home():
    return render_template("index.html")

@app.route('/blog.html')
def blog():
    return render_template('blog.html')

@app.route('/blog-baskerville.html')
def blog_baskerville():
    return render_template('blog-baskerville.html')

@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        # Optionally: process/save/send email/etc.
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route("/admin/templates/admin/admin.html")
def admin_panel():
    return render_template("admin.html")

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/post/<slug>', methods=['GET', 'POST'])
def post(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()

    if request.method == 'POST':
        name = request.form['name']
        text = request.form['text']
        comment = Comment(blog=post, name=name, text=text)
        db.session.add(comment)
        db.session.commit()

    comments = Comment.query.filter_by(blog=post, approved=True).order_by(Comment.created_at.desc()).all()
    return render_template('post.html', post=post, comments=comments)
