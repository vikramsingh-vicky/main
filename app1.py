from flask import Flask, render_template, url_for, redirect, session, request, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from markupsafe import Markup
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///counter.db'
app.secret_key = "any-string-you-want-just-keep-it-secret"
db = SQLAlchemy(app)

# Password Hashing
bcrypt = Bcrypt(app)

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Counter model (unchanged)
class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)

# ContactForm (unchanged)
class ContactForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired()])
    message = StringField(label='Message')
    submit = SubmitField(label="Submit")

# Model: BlogPost
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Model: User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)  # Hashed password
    
    # Add a relationship to BlogPost (one-to-many)
    posts = db.relationship('BlogPost', backref='author', lazy=True)

    # Add these methods for Flask-Login
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# Signup Form
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

# Initialize database
with app.app_context():
    db.create_all()

def get_current_year():
    return datetime.now().year

@app.route('/')
def home():
    images = [
        "/static/business_automation.gif",
        "/static/banner.jpg",
        "/static/social.YouTube.png"
        # "static/images/image3.jpg",
    ]
    counter = Counter.query.first()
    if 'counted' not in session:
        counter.value += 1  # Increment the counter value
        session['counted'] = True  # Mark user's session as counted
        db.session.commit()
    return render_template('index.html', images=images, current_year=get_current_year(),css_file=url_for('static', filename='style.css'),script_file = url_for('static',filename='script.js'),counter=counter.value)


@app.route('/about')
def about():
    return render_template('about.html', current_year=get_current_year(),css_file=url_for('static', filename='style.css'),script_file = url_for('static',filename='script.js'))

@app.route('/services')
def services():
    return render_template('services.html', current_year=get_current_year(),css_file=url_for('static', filename='style.css'),script_file = url_for('static',filename='script.js'))

@app.route('/contact', methods=["GET","POST"])
def contact():
    cform = contactForm()
    if cform.validate_on_submit():
        print(f"""Name:{cform.name.data}, 
              E-mail:{cform.email.data}, 
              message:{cform.message.data}""")
    else:
        print("Invalid Credentials")
    return render_template("contact.html", form=cform, current_year=get_current_year())
    # return render_template('contact.html', current_year=get_current_year(),css_file=url_for('static', filename='style.css'),script_file = url_for('static',filename='script.js'))


@app.route('/blogs')
def blogs():
    blog_posts = BlogPost.query.order_by(BlogPost.timestamp.desc()).all()
    return render_template('blogs.html', current_year=get_current_year(),blog_posts=blog_posts,css_file=url_for('static', filename='style.css'),script_file = url_for('static',filename='script.js'))

class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = PageDownField('Content', validators=[DataRequired()])
    submit = SubmitField('Create Post')

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePostForm()
    
    if form.validate_on_submit():
        new_post = BlogPost(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('blogs'))
    
    return render_template('create_post.html', form=form, current_year=get_current_year(), css_file=url_for('static', filename='style.css'),script_file = url_for('static',filename='script.js'))


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

@app.route('/blog_post/<int:post_id>')
def blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('blog_post.html', post=post, current_year=get_current_year(), css_file=url_for('static', filename='style.css'),script_file = url_for('static',filename='script.js'))

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

    return render_template('login.html', current_year=get_current_year(), css_file=url_for('static', filename='style.css'),script_file = url_for('static',filename='script.js'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form, current_year=get_current_year(), css_file=url_for('static', filename='style.css'),script_file = url_for('static',filename='script.js'))

@app.route('/filter_blogs', methods=['POST'])
def filter_blogs():
    year = request.form.get('year')
    month = request.form.get('month')
    author_id = request.form.get('author')
    search = request.form.get('search')

    # Build the query based on the selected filters
    query = BlogPost.query

    if year:
        query = query.filter(db.extract('year', BlogPost.timestamp) == year)
    if month:
        query = query.filter(db.extract('month', BlogPost.timestamp) == month)
    if author_id:
        query = query.filter(BlogPost.author_id == author_id)
    if search:
        query = query.filter(BlogPost.title.ilike(f'%{search}%'))

    filtered_blogs = query.order_by(BlogPost.timestamp.desc()).all()

    # Prepare the response data
    response_data = []
    for blog in filtered_blogs:
        response_data.append({
            'id': blog.id,
            'title': blog.title,
            'author': {
                'id': blog.author.id,
                'username': blog.author.username
            },
            'highlight': post_highlight(blog.content),  # Use the post_highlight function you defined earlier
            'timestamp': blog.timestamp.strftime('%B %d, %Y')
        })

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
