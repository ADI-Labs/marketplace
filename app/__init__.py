from __future__ import absolute_import

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager, login_user, logout_user, login_required
from flask.ext.mongoengine.wtf import model_form
from wtforms import PasswordField
from werkzeug import secure_filename
import requests
import os

UPLOAD_FOLDER = 'C:/Users/james/uploads/'
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

@app.route("/booklist")
@login_required
def getBooks():
  print("books")
  listOfBooks = Book.objects()
  return render_template("booklist.html", listOfBooks = listOfBooks)


@login_required
def search():
  return render_template("booklist.html")

@app.route("/booklist/<id>")
@login_required
def s(id):
  if request.method=="POST":
    data=id
    return render_template("booklist.html",api_data=data)
  return redirect("/booklist")

@app.route("/book/<id>")
@login_required
def book(id):
  data=id
  return render_template("book.html",api_data=data)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/uplooad/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''   


@app.route("/sell/",methods=["POST","GET"])
def sell():
  form = BookForm(request.form)
  if request.method=="POST" and form.validate():
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


@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect("/")

app.run(debug=True)
