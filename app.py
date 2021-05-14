import os
from datetime import datetime

from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user


# Flask initialization
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///testdb.db'
db = SQLAlchemy(app)


# Flask Admin and Login initialization
class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect("/login")
        return super().index()


admin = Admin(app, name="testWork", index_view=MyAdminIndex())
login = LoginManager(app)


# Get User by user.id
@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Models
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    books = db.relationship("Book", backref="author", lazy=True)

    def __repr__(self):
        return f"Author -> {self.name}"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    author_name = db.Column(db.String(20), db.ForeignKey("author.name"), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"Book -> {self.name}"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))


# db.create_all()


# Add ModelView to Admin panel
class MyModelView(ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return True


admin.add_view(MyModelView(Author, db.session))
admin.add_view(MyModelView(Book, db.session))
admin.add_view(MyModelView(User, db.session))


# Routes
@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/login')
def login_u():
    user = User.query.get(1)
    login_user(user)
    return 'Logged as admin!'


@app.route('/logout')
def logout_u():
    logout_user()
    return "Logged Out"


if __name__ == '__main__':
    app.run(debug=True)
