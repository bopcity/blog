from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1500))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password 

@app.before_request
def require_login():
    allowed_routes = ['login', 'user', 'register', 'index', 'blog', 'blogpost']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/home')

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/home')

@app.route('/home')
def user():
    users = User.query.all()
    return render_template('home.html', users=users, title='Blogz Home!')


@app.route('/blogpost')
def blog():
    blog_id = request.args.get('id')
    username = request.args.get('user')

    ### if we have blog_id, post just that blog
    if blog_id:
        post = Blog.query.get(blog_id)
        return render_template('Blog.html', post=post, title='Blog Entry')
    ### else if we have a username, post the blogs from that user only
    elif username:       
        user = User.query.filter_by(username=username).first()
        posts = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('Blogpost.html', posts=posts, title='Build-a-blog')
    ### else post all the blogs
    else:
        posts = Blog.query.all()
        return render_template('Blogpost.html', posts=posts, title='Build-a-blog')


@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_name = request.form['blog-name']
        blog_body = request.form['blog-text']
        new_post = Blog(blog_name, blog_body,owner)
        db.session.add(new_post)
        db.session.commit()
        session['username'] = owner.username
    
        return redirect('/blogpost?id={}'.format(new_post.id))  
    else:
        return render_template('new_post.html', title="build a blog", 
        blog=blog)

# login and register validation informaion
@app.route('/login', methods=['POST', 'GET'])
def login(): 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/new-post') 
        else:
            return '<h1>Error</h1>'

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        print(request.form)
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/home')
        else:
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')

def validate_username(username):  # username validation
    username_error = ""
    if username == "":
        username_error = "Username name must not be blank."
    elif (len(username) < 3) or (len(username) > 20):
        username_error = "username does not meet lenght requirements"                
    elif "" in username:
        username_error = "username cannot have spaces"  
    return username_error

def validate_password(password):  # password validation
    password_error = ""
    if password == "":
        password_error = "password must not be blank."
    elif (len(password) < 3) or (len(password) > 20):
        password_error = "password does not meet lenght requirements"                
    elif "" in password:
        password_error = "password cannot have spaces"  
    return password_error

def validate_verify(password, verify):
    verify_error = ""
    if verify != password:
        verify_error = "password does not match"
    return verify_error  


@app.route("/", methods=['POST'])
def index2():
    title = 'Sign up!'

    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']
    username_error = validate_username(username)
    password_error = validate_password(password)
    verify_error = validate_verify(password, verify)

    if (username_error == '') and (password_error == '') and (verify_error == ''):
        return redirect('/new_post?username={0}'.format(username))
            
    return render_template('register.html', title=title, username=username,
                           username_error=username_error, password_error=password_error,
                           verify_error=verify_error) 

@app.route('/')
def get():
    return render_template('register.html')


@app.route('/')
def welcome():
    title = "Blogz Home!"
    return render_template('home.html', title=title, username=username)


if __name__ == '__main__':
    app.run()