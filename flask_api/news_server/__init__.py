from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news-db.sqlite'
app.config['SECRET_KEY'] = '894a198b6633d0974e266367'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# URI = Uniform Resource Identifier
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page" 
login_manager.login_message_category = "info"

from news_server import routes