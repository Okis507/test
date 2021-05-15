import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore, login_required, UserMixin, current_user
from flask_security.utils import hash_password


# Flask initialization
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///testdb.db'
app.config["SECURITY_PASSWORD_SALT"] = "desterdester"
db = SQLAlchemy(app)


# Flask Admin and Login initialization
class MyAdminIndex(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        return super().index()


admin = Admin(app, name="testWork", index_view=MyAdminIndex())


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


perms = db.Table("perms",
                 db.Column("users_id", db.Integer, db.ForeignKey("user.id")),
                 db.Column("perm_id", db.Integer, db.ForeignKey("perm.id")))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean)
    roles = db.relationship('Perm', secondary=perms,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return f"User -> {self.username}"


class Perm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    desc = db.Column(db.String(255))


# Login System
user_ds = SQLAlchemyUserDatastore(db, User, Perm)
security = Security(app, user_ds)


# Add ModelView to Admin panel
class MyModelView(ModelView):

    def is_accessible(self):
        if not current_user.is_authenticated:
            return False
        return True


admin.add_view(MyModelView(Author, db.session))
admin.add_view(MyModelView(Book, db.session))
admin.add_view(MyModelView(User, db.session))


# Routes
@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            user_ds.create_user(email=request.form.get('email'),
                                password=hash_password(request.form.get('password')))
            db.session.commit()
            return redirect('/login-user')
        except Exception:
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route("/login-user")
@login_required
def login():
    return 'Logged in!'


@app.route('/logout-user')
def logout():
    current_user.logout()
    return "Logged Out"


if __name__ == '__main__':
    app.run(debug=True)
