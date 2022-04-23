from requests import Session
from news_server import app
from flask import render_template, redirect, url_for, flash, Response, g, request, jsonify
from news_server.models import RawArticle, User, SessionLog

from news_server.forms import RegisterForm, LoginForm
from news_server import db
from flask_login import login_user, logout_user, login_required, current_user
from news_server.recommender import get_user_vector, content_based_recommend, collab_based_recommend, LSA, get_engagement
from random import shuffle 
import numpy as np

# query processed corpus from SQLite
corpus = [elt[0] for elt in list(db.session.execute("SELECT content from articles_processed")) if not(elt[0] is None)]
# note document lengths for estimating average reading time
corpus_lengths = [len(doc) for doc in corpus]
# extract latent topics from corpus using LSA
corpus = LSA(corpus, 25)
# normalize all documents to 1 using L2 norm
corpus = corpus / np.linalg.norm(corpus, axis = 1)[:, None]
# get number of unique users registered in the database
num_users = len([elt[0] for elt in db.session.execute("SELECT DISTINCT user_id from session_log").fetchall()])

# function to compute two dictionaries (used in collaborative filtering):
# user_doc_dict    = {user_id: [ids of articles read]}
# user_rating_dict = {user_id: [ratings given to the articles read]}

def get_user_dicts(db, corpus_lengths):
  user_ids = [elt[0] for elt in db.session.execute("SELECT DISTINCT user_id from session_log").fetchall()]
  user_data = {user: [elt for elt in db.session.execute(f"SELECT article_id, time_spent, rating FROM session_log WHERE user_id == {user} AND rating IS NOT NULL GROUP BY article_id").fetchall()] for user in user_ids}
  user_doc_dict = {id:[elt[0] for elt in user_data[id]] for id in user_ids}
  user_rating_dict = {id:[get_engagement(elt[1], corpus_lengths[elt[0]], elt[2]) for elt in user_data[id]] for id in user_ids}

  return user_doc_dict, user_rating_dict

@app.route('/')  # Decorator 
@app.route('/home')
def home_page(): 
  return render_template('home.html')

@app.route('/articles/pg/<pg>')
@login_required
def articles_page(pg):
  categories = User.query.filter_by(id = current_user.id)[0].categories
  if(categories is None or categories == "None"): categories = "science-and-technology,entertainment,business,sports,india,world"

  if(SessionLog.query.filter_by(user_id = current_user.id)[-1].session_id <= 5):
    items = db.session.query(RawArticle).filter(RawArticle.category.in_(categories.split(","))).all()
  else:
    items = RawArticle.query.all()

  shuffle(items)
  return render_template('news_feed.html', items = items, pg = int(pg))
 
@app.route('/articles/<id>')
def display_article(id):
  items = RawArticle.query.all()
  
  user_doc_dict, user_rating_dict = get_user_dicts(db, corpus_lengths)
  article_history = user_doc_dict[current_user.id] if(current_user.id in user_doc_dict) else []

  if(len(article_history) >= 5): # only do content based recommendation if user has read atleast 5 articles
    user = get_user_vector(corpus[article_history], user_rating_dict[current_user.id])
    content_recommended_ids = content_based_recommend(corpus, user, 5)
  else:
    content_recommended_ids = -1
  
  if(num_users > 10): # only do collaborative filtering is more than 10 users are registered
    collab_recommended_ids = collab_based_recommend(user, corpus, user_doc_dict, user_rating_dict, 5)
  else: 
    collab_recommended_ids = -1

  # in any case, find 5 similar articles to the one being read by the user at the moment
  similar_ids = content_based_recommend(corpus, corpus[int(id)].reshape(1, -1), 6)
  similar_ids = np.delete(similar_ids, np.where(similar_ids == int(id)))

  if(id.isdigit() and int(id) < len(items)):

    db.session.add(
      SessionLog(
        session_id = SessionLog.query.filter_by(user_id = current_user.id)[-1].session_id, 
        user_id = current_user.id, 
        article_id = int(id)))  

    db.session.commit()

    log_id = SessionLog.query.order_by(-SessionLog.log_id).first().log_id
    
    return render_template(
      'article.html',
      id = int(id), 
      log_id = log_id,
      item = items[int(id)], 
      recommended_articles = [items[elt] for elt in content_recommended_ids] if isinstance(content_recommended_ids, np.ndarray) else [None],
      similar_articles = [items[elt] for elt in similar_ids])
  else:
    return render_template('404.html'), 404

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
    return redirect(url_for('preferences'))

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

@app.route('/preferences')
def preferences():
  return render_template('preferences.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
    
# get analytics about the user's interaction with the article
@app.route("/analytics", methods=["GET", "POST"])
def analytics():
    data = request.data.decode("utf-8").split(",")
    article_id, log_id, time_spent, rating = int(data[0]), int(data[1]), float(data[2]), int(data[3])
    db.session.execute(f"UPDATE session_log SET time_spent = {time_spent}, rating = {rating} WHERE log_id = {log_id}")
    db.session.commit()
    return ('', 204)

# get information about preferred categories to solve cold-start problem
@app.route('/category_data', methods=["GET", "POST"])
def category_data():
  data = request.data.decode("utf-8")
  if(data == ""):
    data = None

  db.session.execute(f"UPDATE users SET categories = '{data}' WHERE id = {current_user.id}")
  db.session.commit()
  return ('', 204)
