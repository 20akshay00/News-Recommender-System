from requests import Session
from news_server import app
from flask import render_template, redirect, url_for, flash, Response, g, request, jsonify
from news_server.models import RawArticle, User, SessionLog

from news_server.forms import RegisterForm, LoginForm
from news_server import db
from flask_login import login_user, logout_user, login_required, current_user
from news_server.recommender import get_user_vector, content_based_recommend
import numpy as np

from news_server.recommender import LSA

corpus = db.session.execute("SELECT content from articles_processed")
corpus = LSA([elt[0] for elt in list(corpus) if not(elt[0] is None)], 25)

@app.route('/')  # Decorator 
@app.route('/home')
def home_page(): 
  return render_template('home.html')

@app.route('/articles/pg/<pg>')
@login_required
def articles_page(pg):
  items = RawArticle.query.all()
  return render_template('news_feed.html',items=items, pg = int(pg))
 
@app.route('/articles/<id>')
def display_article(id):
  items = RawArticle.query.all()

  article_history = SessionLog.query.with_entities(SessionLog.article_id).filter_by(user_id = current_user.id)
  article_history = np.array([elt[0] for elt in list(article_history) if not(elt[0] is None)])
  if(len(article_history) >= 5):
    user = get_user_vector(corpus[article_history])
    recommended_ids = content_based_recommend(corpus, user, 5)
  else:
    recommended_ids = -1
  
  similar_ids = content_based_recommend(corpus, corpus[int(id) - 1].reshape(1, -1), 5)

  if(id.isdigit() and int(id) < len(items)):

    db.session.add(
      SessionLog(
        session_id = SessionLog.query.filter_by(user_id = current_user.id)[-1].session_id, 
        user_id = current_user.id, 
        article_id = int(id)))  

    db.session.commit()
    
    return render_template(
      'article.html', 
      item = items[int(id) - 1], 
      recommended_articles = [items[elt] for elt in recommended_ids] if isinstance(recommended_ids, np.ndarray) else [None],
      similar_articles = [items[elt] for elt in similar_ids])
  else:
    return render_template('404.html'), 404

# @app.route("/handleClick")
# def handleClick():
#   app.logger.info("Click registered")
#   return ('', 202)

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
    
