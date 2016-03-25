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

#this should actually be called login
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


#rename this to booklist
@app.route("/booklist/<id>")
@login_required
def booklist(id):
  book = Book.objects(book_name=id).first()
  #id = Book.objects(name=Book.book_name)
  if book:
    return render_template("bookinfo.html", book=book)
  else:
    return 'not found'


@app.route("/book/<id>")
@login_required
def book(id):
  data=id
  return render_template("book.html",api_data=data)

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

# @app.route("/bookinfo/<id>")
# @login_required
# def bookinfo(id):
#   id = Book.objects(book_name=book_name)
#   return render_template("bookinfo.html", api_data = id)


@app.route("/logout")
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
    return render_template("booklist.html",listOfBooks = items)

# @app.route("/booklist/<id>", meththod = ["POST", "GET"])
# @login_required
# def bookInfo(id):



app.run(debug=True)


