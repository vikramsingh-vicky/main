from flask import Flask, render_template, url_for, redirect, session, request, jsonify, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from markupsafe import Markup
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, SubmitField, validators, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_bcrypt import Bcrypt
import calendar
from sqlalchemy import extract, or_
import json
from flask_mail import Mail
import re
import os
from werkzeug.utils import secure_filename


# Open config.json file in readonly mode
with open('config.json','r') as con:
    params = json.load(con)["params"]

# Define App
app = Flask(__name__, static_folder='static', static_url_path='/static')

## Configuration Declaration Starts Here ---------------------------------------------------------------------
# Email Config
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    # MAIL_USE_SSL = True,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
# Email Configuration Send Email
mail = Mail(app)
if(params["local_server"]==True):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]
app.secret_key = "any-string-you-want-just-keep-it-secret"
db = SQLAlchemy(app)

# Password Hashing
bcrypt = Bcrypt(app)

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

## Configuration Declaration Ends Here ---------------------------------------------------------------------

## Class Declaration For DB Starts Here ---------------------------------------------------------------------
# Contact Us page DB Definition
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    phone_num = db.Column(db.String(15), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12))

# Counter model - To Count Unique Visitor
class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)

# Model: Posts - Defining the Posts Database
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.VARCHAR(100),nullable=False)
    content = db.Column(db.Text, nullable=False)
    img_file = db.Column(db.VARCHAR(50), nullable=True)
    posted_by = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

# Model: User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(12), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)  # Hashed password
    date = db.Column(db.DateTime,nullable=True)
    mem_type = db.Column(db.String,nullable=False)
    
    # Add a relationship to Posts (one-to-many)
    # posts = db.relationship('Posts', backref='author', lazy=True)

    # Add these methods for Flask-Login
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# Signup Form
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    name = StringField('Name', validators=[DataRequired(), Length(min=10, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = PageDownField('Content', validators=[DataRequired()])
    submit = SubmitField('Create Post')

# Blog Filteration Form
class FilterForm(FlaskForm):
    year = SelectField('Year', coerce=int, choices=[], default='', validate_choice=False)
    month = SelectField('Month', coerce=int, choices=[], default='', validate_choice=False)
    author = SelectField('Author', coerce=int, choices=[], default='', validate_choice=False)
    search = StringField('Search')
    submit = SubmitField('Filter')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.author.choices = [(author.id, author.username) for author in User.query.all()]

## Class Declaration For DB Ends Here ---------------------------------------------------------------------

## Function Declaration Starts Here ---------------------------------------------------------------------
# Initializing Counter on Site Load
def initialize_counter():
    with app.app_context():
        counter = Counter.query.first()
        if not counter:
            counter = Counter(value=1547)
            db.session.add(counter)
            db.session.commit()

# Call the initialization function
initialize_counter()

# Login Initializer
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
with app.app_context():
    db.create_all()
# Function To Create slug from post title
def create_slug(input_string):
    # Convert to lowercase
    slug = input_string.lower()

    # Remove special characters and replace with hyphens
    slug = re.sub(r'[^a-zA-Z0-9\-]', '-', slug)

    # Remove consecutive hyphens
    slug = re.sub(r'[-]+', '-', slug)

    # Remove leading and trailing hyphens
    slug = slug.strip('-')

    return slug
# Function to get Current Logged In User
def get_current_year():
    return datetime.now().year

## Route Declaration Starts Here ---------------------------------------------------------------------

# Route for Home Page
@app.route('/')
def home():
    images = [
        "/static/business_automation.gif",
        "/static/banner.jpg",
        "/static/social.YouTube.png"
        # "static/images/image3.jpg",
    ]
    projects_completed = params['projects_completed']
    happy_clients = params['happy_clients']
    application_users = params['application_users']
    css_file=url_for('static', filename='styles.css')
    script_file = url_for('static',filename='script.js')
    counter = Counter.query.first()
    if 'counted' not in session:
        counter.value += 1  # Increment the counter value
        session['counted'] = True  # Mark user's session as counted
        db.session.commit()
    return render_template('index.html', images=images, current_year=get_current_year(),css_file=css_file,script_file = script_file,counter=counter.value,projects_completed=projects_completed,happy_clients=happy_clients,application_users=application_users)

# Rout for About Us Page 
@app.route('/about')
def about():
    return render_template('about.html', current_year=get_current_year(),css_file=url_for('static', filename='styles.css'),script_file = url_for('static',filename='script.js'))

# Route for Profile Page
@app.route('/profile')
def profile():
    return render_template('profile.html', current_year=get_current_year(),css_file=url_for('static', filename='styles.css'),script_file = url_for('static',filename='script.js'))

# Route for Services Page
@app.route('/services')
def services():
    return render_template('services.html', current_year=get_current_year(),css_file=url_for('static', filename='styles.css'),script_file = url_for('static',filename='script.js'))

# Route for Contact Us Page
@app.route('/contact', methods=["GET","POST"])
def contact():
    if(request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, phone_num=phone, email=email, message=message, date = datetime.now() )
        db.session.add(entry)
        db.session.commit()

        mail.send_message('New Message From '+ name,
                            sender = email,
                            recipients = [params['gmail-user'],'unrealautomation@gmail.com'],
                            body = message + '\n\n' + phone
        )
    return render_template("contact.html", current_year=get_current_year())
    # return render_template('contact.html', current_year=get_current_year(),css_file=url_for('static', filename='styles.css'),script_file = url_for('static',filename='script.js'))

# Route for Blogs Page
@app.route('/blogs', methods=['GET', 'POST'])

def blogs():
    page = request.args.get('page', 1, type=int)
    per_page = params["blogs_per_page"]  # Adjust the number of posts per page as needed
    
    post = Posts.query.order_by(Posts.date.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('blogs.html', current_year=get_current_year(), post=post, css_file=url_for('static', filename='styles.css'), script_file=url_for('static', filename='script.js'))
# Route to Filter Blogs based on Search Criteria
@app.route('/filter_blogs', methods=['POST'])
def filter_blogs():
    year = request.form.get('year')
    month = request.form.get('month')
    author = request.form.get('author')
    search = request.form.get('search')

    # Query the Posts model based on the selected filters
    filtered_blogs = Posts.query

    if year:
        filtered_blogs = filtered_blogs.filter(extract('year', Posts.timestamp) == int(year))

    if month:
        filtered_blogs = filtered_blogs.filter(extract('month', Posts.timestamp) == int(month))

    if author:
        filtered_blogs = filtered_blogs.filter(Posts.author_id == int(author))

    if search:
        # Apply a text-based filter to the title or content
        filtered_blogs = filtered_blogs.filter(
            or_(
                Posts.title.ilike(f'%{search}%'),
                Posts.content.ilike(f'%{search}%')
            )
        )

    filtered_blogs = filtered_blogs.all()

    # Convert the filtered blog posts to a list of dictionaries
    blog_data = [
        {
            'id': blog.id,
            'title': blog.title,
            'author': {
                'username': blog.author.username
            },
            'highlight': blog.content[:200],  # You can customize how the content is displayed
            'timestamp': blog.timestamp.strftime('%B %d, %Y')
        }
        for blog in filtered_blogs
    ]

    return jsonify(blog_data)


# Route for Create Post Page
@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if current_user.mem_type in ['Admin', 'Blogger']:
        if(request.method == 'POST'):
            title = request.form.get('title')
            content = request.form.get('content')
            new_post = Posts(title=title, content=content, posted_by=current_user.name, slug=create_slug(title))
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('blogs'))
    
        return render_template('create_post.html', current_year=get_current_year(), css_file=url_for('static', filename='styles.css'),script_file = url_for('static',filename='script.js'))
    else:
        flask.flash('You do not have permission to access this page.', 'warning')
        return redirect(url_for('blogs'))

# To Short the Content of the post to 150 characters
@app.template_filter('highlight')
def post_highlight(content, max_chars=150):
    # Split content into paragraphs
    paragraphs = content.split('\n\n')
    
    # Extract the first paragraph as a highlight
    highlight = paragraphs[0]
    
    # If the highlight is too long, truncate it
    if len(highlight) > max_chars:
        highlight = highlight[:max_chars] + '...'
    
    return Markup(highlight)  # Mark the output as safe HTML

# Route for individual Blog Page
@app.route('/blog_post/<string:post_slug>', methods=['GET'])
def blog_post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    content = Markup(post.content)
    return render_template('blog_post.html', post=post, content=content, current_year=get_current_year(), css_file=url_for('static', filename='styles.css'),script_file = url_for('static',filename='script.js'))

# Route for Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html', current_year=get_current_year(), css_file=url_for('static', filename='styles.css'),script_file = url_for('static',filename='script.js'))

# Route for Logout Page
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Route for Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # form = SignupForm()
    if(request.method == 'POST'):
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')


        hashed_password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        new_user = User(username=username, name=name, email=email, phone=phone, password=hashed_password, date=datetime.now(),mem_type="Subscriber")
        db.session.add(new_user)
        db.session.commit()
        flask.flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html', current_year=get_current_year(), css_file=url_for('static', filename='styles.css'),script_file = url_for('static',filename='script.js'))

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('static', 'uploads', filename)
        file.save(file_path)

        uploaded_url = url_for('static', filename='uploads/' + filename)

        return jsonify({'location': uploaded_url})


# Initiation of the Application/Website
if __name__ == '__main__':
    app.run(debug=True)
