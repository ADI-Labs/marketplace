from __future__ import absolute_import

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask.ext.mongoengine.wtf import model_form
from wtforms import PasswordField
from werkzeug import secure_filename
import requests
import os

UPLOAD_FOLDER = 'C:/Users/Public/' # This must be changed to your directory
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF'])

app = Flask(__name__)
app.config["DEBUG"] = True      
app.config['MONGODB_SETTINGS'] = { 'db' : 'books' }
app.config['SECRET_KEY'] = 'secretkey'
app.config['WTF_CSRF_ENABLED'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    # If the username is unique...
    if(load_user(form.name.data) == None):
      form.save()
      return redirect("/")
    else:
      return redirect("/register")
  return render_template("register.html", form=form)

@app.route("/booklist", methods = ["POST", "GET"])
@login_required
def getBooks():
  if request.method == "POST":
    id=request.form["search"]
    return redirect("/booklist/" + id)
  else:
    listOfBooks = Book.objects()
    return render_template("booklist.html", listOfBooks = listOfBooks)


@login_required
def search():
  return render_template("booklist.html")

@app.route("/book/<id>")
@login_required
def book(id):
  data=id
  return render_template("book.html",api_data=data)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/sell/",methods=["POST","GET"])
def sell():
  form = BookForm(request.form)
  if request.method=="POST":
    form.user_name.data = current_user.name
    form.contact_info.data = current_user.contact_info
  if form.validate():
    book = Book(user_name=form.user_name.data, book_name=form.book_name.data, price=form.price.data,
                contact_info=form.contact_info.data, description=form.description.data)

    file = request.files['file']
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      book.image = url_for('uploaded_file', filename=filename)

    book.save()
    return redirect('/booklist')
  else:
    return render_template("sell.html",form=form)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename) 


@app.route("/bookinfo/<id>")
def bookinfo(id):
  books=Book.objects(book_name = id)
  return render_template("bookinfo.html",book=books[0])

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
    for book in listOfBooks:
        if(book not in items and id.lower() in book.description.lower()):
            items.append(book)

    return render_template("booklist.html",listOfBooks = items)

@app.route("/myBooks/", methods=["POST","GET"])
@login_required
def myBooks():
  list_of_my_books = Book.objects()
  return render_template("myBooks.html", list_of_my_books = list_of_my_books)

@app.route("/delete/<id>")
@login_required
def delete(id):
  deleted_book = Book.objects(book_name=id)[0].book_name
  Book.objects(book_name=id).delete()
  return render_template("delete.html", deleted_book = deleted_book)

"""
for text in Book.objects():
  text.delete()

for guy in User.objects():
  guy.delete()
"""

app.run(debug=True)
