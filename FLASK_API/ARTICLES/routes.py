from ARTICLES import app
from flask import render_template, redirect, url_for, flash, Response, g
from ARTICLES.models import Item,User

from ARTICLES.forms import RegisterForm, LoginForm
from ARTICLES import db
from flask_login import login_user, logout_user, login_required
import time

# ------------Experimental----------------

@app.before_request
def before_request_func():
    g.timings = {}


from functools import wraps
def time_this(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        r = func(*args, **kwargs)
        end = time.time()
        g.timings[func._name_] = end - start
        return r
    return wrapper

# ------------Experimental----------------

@app.route('/')  # Decorator 
@app.route('/home')
def home_page(): 
  return render_template('home.html')

@app.route('/articles/pg/<pg>')
@login_required
def articles_page(pg):
  items=Item.query.all()
  return render_template('articles.html',items=items, pg = int(pg))
 
@time_this
@app.route('/articles/<id>')
def display_article(id):
  items=Item.query.all()
  return render_template('page.html', item = items[int(id)])

@app.route('/recommender_system')
def recommender_page():
  return render_template('recommender.html')


@app.route('/register',methods=['GET','POST'])
def register_page():
  form = RegisterForm()

  if form.validate_on_submit():
    user_to_create = User(username=form.username.data,
                          email_address=form.email_address.data,
                          password_hash=form.password1.data)
    db.session.add(user_to_create)
    db.session.commit()

    login_user(user_to_create)
    flash(f"Account created successfully! You are now logged in as: {user_to_create.username}", category='success')
    return redirect(url_for('articles_page', pg = 1))

  if form.errors!={}: # This means that if there are no errors in validators
    for err_msg in form.errors.values():
      flash(f'There was an error with creating a user: {err_msg}', category='danger')

  return render_template('register.html', form=form)


@app.route('/login',methods=['GET','POST'])
def login_page():
  form = LoginForm()
  if form.validate_on_submit():
    attempted_user     = User.query.filter_by(username=form.username.data).first()
    attempted_password = User.query.filter_by(password_hash=form.password.data).first()
    if attempted_user and attempted_password:
      
      login_user(attempted_user)
      flash(f"Success! You are logged in as: {attempted_user.username}", category='success')
      return redirect(url_for('articles_page', pg = 1))
    else:
      flash(f"Username and password do not match! Please try again", category='danger')      
  return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
  logout_user()
  flash("You have been logged out!", category='info')
  return redirect(url_for("home_page"))

# ------------Experimental----------------
@app.route('/timings',methods=['GET','POST'])
def hello2():
    articles_page()
    return Response('Hello World: ' + str(g.timings), mimetype='text/plain')
# ------------Experimental----------------
