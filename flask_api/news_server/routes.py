from news_server import app
from flask import render_template, redirect, url_for, flash, Response, g
from news_server.models import Item, User, SessionLog

from news_server.forms import RegisterForm, LoginForm
from news_server import db
from flask_login import login_user, logout_user, login_required, current_user
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
  return render_template('news_feed.html',items=items, pg = int(pg))
 
@time_this
@app.route('/articles/<id>')
def display_article(id):
  items=Item.query.all()

  if(id.isdigit() and int(id) < len(items)):
    db.session.add(
      SessionLog(
        session_id = SessionLog.query.filter_by(user_id = current_user.id)[-1].session_id, 
        user_id = current_user.id, 
        article_id = int(id)))  
    db.session.commit()

    return render_template('article.html', item = items[int(id) - 1])
  else:
    return render_template('404.html'), 404

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

    db.session.add(
      SessionLog(
        session_id = 0, 
        user_id = current_user.id, 
        article_id = None))
    db.session.commit()
    
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
      db.session.add(
      SessionLog(
        session_id = SessionLog.query.filter_by(user_id = current_user.id)[-1].session_id + 1, 
        user_id = current_user.id, 
        article_id = None))
      db.session.commit()

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
    
# ------------Experimental----------------
@app.route('/timings',methods=['GET','POST'])
def hello2():
    articles_page()
    return Response('Hello World: ' + str(g.timings), mimetype='text/plain')
# ------------Experimental----------------
