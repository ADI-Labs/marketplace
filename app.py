from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager, login_user, logout_user, login_required
from flask.ext.mongoengine.wtf import model_form
from wtforms import PasswordField
from flask import redirect
import requests
import os
from werkzeug import secure_filename

UPLOAD_FOLDER = 'C:/Users/james/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF'])


app = Flask(__name__)
app.config["DEBUG"] = True      
app.config['MONGODB_SETTINGS'] = { 'db' : 'books' }
app.config['SECRET_KEY'] = 'secretkey'
app.config['WTF_CSRF_ENABLED'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = MongoEngine(app)

login_manager = LoginManager()
login_manager.init_app(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONSs

#Move to another file
class User(db.Document):
  name = db.StringField(required=True,unique=True)
  password = db.StringField(required=True)
  def is_authenticated(self):
    users = User.objects(name=self.name, password=self.password)
    return len(users) != 0
  def is_active(self):
    return True
  def is_anonymous(self):
    return False
  def get_id(self):
    return self.name

class Book(db.Document):
    user_name = db.StringField(required=True)
    book_name = db.StringField(required=True)
    price = db.StringField(required=True)
    contact_info = db.StringField(required=True)
<<<<<<< HEAD
    description = db.StringField()
    image = db.StringField()

=======
    description = db.StringField(required=True)
>>>>>>> 5016468f7acc03772652ba871dae629d2e19aa4e

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

@app.route("/sell/",methods=["POST","GET"])
def sell():
    form = BookForm(request.form)
    if request.method=="POST" and form.validate():
      file = request.files['file']
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = url_for('uploaded_file', filename=filename)

      book = Book(user_name=form.user_name.data, book_name=form.book_name.data, price=form.price.data,
                contact_info=form.contact_info.data, description=form.description.data,
                image=image_url)
      book.save()
      return render_template("confirm.html")
    else:
      return render_template("sell.html",form=form)
        
    

@app.route('/upload/<filename>')
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


