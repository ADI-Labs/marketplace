from __future__ import absolute_import

from flask import Flask,  render_template, request, redirect
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager, login_user, logout_user, login_required
from flask.ext.mongoengine.wtf import model_form
from wtforms import PasswordField
from flask import redirect
import requests


app = Flask(__name__)
app.config["DEBUG"] = True      
app.config['MONGODB_SETTINGS'] = { 'db' : 'books' }
app.config['SECRET_KEY'] = 'secretkey'
app.config['WTF_CSRF_ENABLED'] = True
db = MongoEngine(app)

from .models.user import User
from .models.book import Book
login_manager = LoginManager()
login_manager.init_app(app)

UserForm = model_form(User)
UserForm.password = PasswordField('password')

BookForm = model_form(Book)

@login_manager.user_loader
def load_user(name):
  users = User.objects(name=name)
  if len(users) != 0:
    return users[0]
  else:
    return None

@app.route("/", methods=['GET','POST'])
def home():
  form = UserForm(request.form)
  print('before if')
  if request.method == 'POST' and form.validate():
    user = User.objects(name=form.name.data,password=form.password.data).first()
    if user:
      login_user(user)
      return redirect('/booklist')

  return render_template('login.html', form=form)


@app.route("/register", methods=["POST","GET"])
def registration():
  form = UserForm(request.form)
  if request.method == "POST" and form.validate():
    form.save()
    return redirect("/")

  return render_template("register.html", form=form)

@app.route("/booklist", methods = ["POST", "GET"])
@login_required
def getBooks():
  if request.method == "POST":
    id=request.form["search"]
    return redirect("/booklist/" + id)
  else:
    print("books")
    listOfBooks = Book.objects()
    return render_template("booklist.html", listOfBooks = listOfBooks)


@login_required
def search():
  return render_template("booklist.html")

@app.route("/sell/",methods=["POST","GET"])
def sell():
  form = BookForm(request.form)
  if request.method=="POST" and form.validate():
    book = Book(user_name=form.user_name.data, book_name=form.book_name.data, price=form.price.data,
                contact_info=form.contact_info.data, description=form.description.data)
    book.save()
    return redirect('/booklist')
  else:
    return render_template("sell.html",form=form)

@app.route("/bookinfo/<id>")
def bookinfo(id):
  books=Book.objects(book_name = id)
  return render_template("bookinfo.html",book=books[0])


@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect("/")

@app.route("/booklist/<id>",methods=["POST","GET"])
@login_required
def search(id):
  if request.method == "POST":
    id=request.form["search"]
    return redirect("/booklist/" + id)

  else:
    listOfBooks = Book.objects()
    items=[]
    for book in listOfBooks:
        if(id.lower() in book.book_name.lower()):
            items.append(book)
    for book in listOfBooks:
        if(book not in items and id.lower() in book.description.lower()):
            items.append(book)

    return render_template("booklist.html",listOfBooks = items)

@app.route("/mybooks")
@login_required
def mybooks():
    listOfBooks = Book.objects()
    items=[]
    for book in listOfBooks:
        if(book.username.lower()==User.name.lower()):
            items.append(book)

    return render_template("books.html",listOfBooks = items)

app.run(debug=True)


