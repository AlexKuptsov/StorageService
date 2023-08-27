import os

from flask import Flask
from flask.cli import load_dotenv
from flask_login import UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy

from auth import auth as auth_blueprint
from main import main as main_blueprint
from storage import storage as storage_blueprint

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')

app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)
app.register_blueprint(storage_blueprint)

# ------------------------------------------ database configuration ---------------------------------------------------
app.config.from_object("db_config.Config")
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(500))
    price = db.Column(db.Float)
    count = db.Column(db.Integer)


class Buy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.Integer)
    user = db.Column(db.Integer)
    data = db.Column(db.DateTime)


class Sell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.Integer)
    comment = db.Column(db.String(100))
    user = db.Column(db.Integer)
    count = db.Column(db.Integer)
    summ = db.Column(db.Float)
    margin = db.Column(db.Float)
    additional_expanses = db.Column(db.Float)
    data = db.Column(db.DateTime)

    @property
    def product_name(self):
        product = Product.query.get(self.product)
        return product.title if product else None


# Check if the database file doesn't exist
if not os.path.exists('instance/db.sqlite'):
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()

# ---------------------------------------- Initialize Flask Login Manager ---------------------------------------------
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

# ---------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
