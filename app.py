from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_manager,login_required,logout_user, current_user
from flask_ckeditor import CKEditor
from webforms import PasswordForm, UserForm, LoginForm, PostForm, PasswordForm, ContactForm, SearchForm


#create a flask instance
app = Flask(__name__)

db = SQLAlchemy()
#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#Create a Form Class (CSRF TOKEN CREATE A SECRET KEY)
app.config['SECRET_KEY'] = "my kokoro"
#Add CKEditor
ckeditor = CKEditor(app)
# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Creating a Global Variable


# Some Flask Login Stuff That helps us to Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Passed stuff to Nav-bar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form = form)

# Setting up the password hash
@property
def password(self):
    raise AttributeError('password is not a readeable attribute!')
    
@password.setter
def password(self, password):
    self.password_hash = generate_password_hash(password)
        
def verify_password(self, password):
    return check_password_hash(self.password_hash, password)
    
    
    #Create A String
def __repr__(self):
    return '<Name %r>' % self.name

# Create a route decorator
@app.route('/')
def index():
    # Grab all the posts from the database 
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('index.html', posts=posts)

#Create custom error Pages in cases where error occurs
#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server error
@app.errorhandler(500)
def page_not_found(e):
        return render_template("500.html"), 404
#Creating an about route decorator
@app.route('/about')
def about():
    return render_template('about.html')

#Creating a contact route decorator
@app.route('/contact', methods=['GET','POST'])
def contact():
     firstname = None
     form = ContactForm()
     if form.validate_on_submit():
        complain = Complain(firstname=form.firstname.data, lastname = form.lastname.data, complain = form.complain.data)
        db.session.add(complain)
        db.session.commit()
        firstname = form.firstname.data
        form.firstname.data = ""
        form.lastname.data = ""
        form.complain.data = ""
        flash("Your Complain is Submitted Successfully!, Will get back to you soonest!")
     our_complains = Complain.query.order_by(Complain.date_of_complain)
     return render_template('contact.html', form=form, firstname=firstname, our_complains=our_complains)

#Delete route decorator for the admin
@app.route('/delete/<int:id>')
def deleteComplain(id):
    user_to_delete = Complain.query.get_or_404(id)
    firstname = None
    form = ContactForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("Complains Deleted Successfully!")
        our_complains = Complain.query.order_by(Complain.date_of_complain)
        return render_template('admin.html', form=form, firstname=firstname, our_complains=our_complains)
    except:
        flash('Whoops! There was a problem deleting user... try again!')
        our_complains = Complain.query.order_by(Complain.date_of_complain)
        return render_template('admin.html', form=form, firstname=firstname, our_complains=our_complains)

#Creating a login route decorator
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    #Check if form is submitted and validate
    if form.validate_on_submit():
            # check if username exists and returns the first one seen
            user = Users.query.filter_by(username=form.username.data).first()
            if user:
                #if found
                #Check the Hash
                if check_password_hash(user.password_hash, form.password.data):
                    login_user(user) 
                    flash("Login Successful!!")
                    return redirect(url_for('index')) 
                else:
                    flash("Wrong Password - Try Again!")
            else:
                flash("That User Dosen't exists -- Try Again!")
    return render_template('login.html', form = form)

# Create Logout Page or Function
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("You have been Logged Out!  Thanks for visiting DBlog")
    return redirect(url_for('login'))

#Creating a Register route decorator
@app.route('/user/add', methods=['GET','POST'])
def Register():
    fullname = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user is None:
            # Hash the password!!!
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(fullname=form.fullname.data, username = form.username.data, email = form.email.data, about_author = form.about_author.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        fullname = form.fullname.data
        form.fullname.data = ""
        form.username.data = ""
        form.email.data = ""
        form.about_author.data = ""
        form.password_hash = ""
        flash("Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('Register.html', form=form, fullname=fullname, our_users=our_users)

#Delete route decorator
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    fullname = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('Register.html', form=form, fullname=fullname, our_users=our_users)
    except:
        flash('Whoops! There was a problem deleting user... try again!')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('Register.html', form=form, fullname=fullname, our_users=our_users)

#Update database record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    #Check if we are dealing with a post request if yes then get the listed info's from the form and save to the designated variable before updating to database
    if request.method == "POST":
        name_to_update.fullname = request.form['fullname']
        name_to_update.email = request.form['email']
        name_to_update.about_author = request.form['about_author']
        name_to_update.username = request.form['username']
        try:
            #commit changes made
            db.session.commit()
            flash("User updated successfully!")
            return render_template('update.html',form = form, name_to_update = name_to_update)
        except:
            flash("Error looks like there was a problem... try again!")
            return render_template('update.html',form = form, name_to_update = name_to_update)
    else:
        return render_template('update.html',form = form, name_to_update = name_to_update,id=id)

# Create a User Dahboard Page Route
@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.fullname = request.form['fullname']
        name_to_update.email = request.form['email']
        name_to_update.about_author = request.form['about_author']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User updated successfully!")
            return render_template('dashboard.html',form = form, name_to_update = name_to_update)
        except:
            flash("Error looks like there was a problem... try again!")
            return render_template('dashboard.html',form = form, name_to_update = name_to_update)
    else:
        return render_template('dashboard.html',form = form, name_to_update = name_to_update,id=id)


#Creating an add_post route decorator
# Add Post Page
@app.route('/add-post', methods=['GET','POST'])
#@login_required
def add_post():
    form = PostForm()
    
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title = form.title.data, content = form.content.data, poster_id = poster, slug = form.slug.data)
        # Clear the form
        form.title.data = ""
        form.content.data = ""
        form.author.data = ""
        form.slug.data = ""
        
        # Add post data to database
        db.session.add(post)
        db.session.commit()
        
        # Return a Message
        flash("Blog Post Submitted Successfully!")
        
        #Redirect to the webpage
    return render_template("add_post.html", form=form)
@app.route('/posts')
def posts():
    # Grab all the posts from the database 
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts = posts)

@app.route('/posts/<int:id>')
def post(id):
    # Grab all posts with refrence to its ID
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post = post)

#Creating an edit_post route decorator
#Edit Post
@app.route('/posts/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post has been Updated")
        return redirect(url_for('post', id=post.id))

    if current_user.id == post.poster_id:
            
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You Aren't Authorized to Edit This Post!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts = posts)
    
# Delete Post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            
            # Return a message if id's match
            flash("Blog Post was Deleted!")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts = posts)
        except:
            # Return an error message
            flash("Whoops! There was a problem deleting post, try again...")

            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts = posts)
    else:
        # Return a message if id's  don't match
            flash("You Aren't Authorized to Delete This Post!")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts = posts)

#Creating a Search route decorator
# Create a Search Function Page
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        # Query the database and filter by search term
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", form=form, searched = post.searched, posts = posts)

# Create Admin Page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1 :
        our_users = Users.query.order_by(Users.date_added)
        our_complains = Complain.query.order_by(Complain.date_of_complain)
        return render_template('admin.html', our_users=our_users, our_complains=our_complains)
    else:
        flash('Sorry you must be the Admin to access the Admin Page...')
        return redirect(url_for('dashboard'))

        
        



#Define our app within the application db context to create our table
with app.app_context():
    db.create_all() 
    
    

#Create a Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    fullname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    #Do some password stuff!
    password_hash = db.Column(db.String(128))
      # Users can have many posts
    posts = db.relationship('Posts', backref='poster')
    
    # Setting up the password hash
    @property
    def password(self):
        raise AttributeError('password is not a readeable attribute!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return '<Name %r' & self.fullname
    
# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default = datetime.utcnow)
    slug = db.Column(db.String(255))
    # Create a Foreign Key to link Users(refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
#Create a  Contact Us Model to store all complains
class Complain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(200), nullable=False)
    complain = db.Column(db.Text(500), nullable=False)
    date_of_complain = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Name %r' & self.firstname
    
#Create an Admin Model to store Admins  
class Admin(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    
    # Setting up the password hash
    @property
    def password(self):
        raise AttributeError('password is not a readeable attribute!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    def __repr__(self):
        return '<Name %r' & self.username
    