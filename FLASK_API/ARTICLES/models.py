from ARTICLES import db, login_manager
#from ARTICLES import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id            = db.Column(db.Integer(),primary_key=True)
    username      = db.Column(db.String(length=30),nullable=False,unique=True)
    email_address = db.Column(db.String(length=50),nullable=False,unique=True)
    password_hash = db.Column(db.String(length=60),nullable=False)
    #items         = db.relationship('Item', backref='read_article',lazy=True)


class Item(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    Heading  = db.Column(db.String(length=100), nullable=False, unique=True)
    Summary  = db.Column(db.String(length=1000), nullable=False)
    Date     = db.Column(db.String(),nullable = False)
    Category = db.Column(db.String(),nullable=False)
    #reader   = db.Column(db.Integer(),db.ForeignKey('user.id'))


    def __repr__(self):
        return f'Item {self.Heading}'