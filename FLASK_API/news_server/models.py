from news_server import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id            = db.Column(db.Integer(),primary_key=True)
    username      = db.Column(db.String(length=30),nullable=False,unique=True)
    email_address = db.Column(db.String(length=50),nullable=False,unique=True)
    password_hash = db.Column(db.String(length=60),nullable=False)

class SessionLog(db.Model):
    __tablename__ = 'session_log'
    log_id        = db.Column(db.Integer(), primary_key=True)
    session_id    = db.Column(db.Integer())
    user_id       = db.Column(db.Integer())
    article_id    = db.Column(db.Integer())
    
class Item(db.Model):
    __tablename__ = 'articles'
    article_id = db.Column(db.Integer(), primary_key=True)
    headline = db.Column(db.String(length=100), nullable=False, unique=True)
    date     = db.Column(db.String(),nullable = False)
    url     = db.Column(db.String(),nullable = False)
    category = db.Column(db.String(),nullable=False)
    summary  = db.Column(db.String(length=1000), nullable=False)
    content  = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'Item {self.Heading}'