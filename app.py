from flask import Flask,  render_template, request, redirect
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager, login_user, logout_user
from flask.ext.mongoengine.wtf import model_form
from wtforms import PasswordField
import requests

app = Flask(__name__)
app.config["DEBUG"] = True      
app.config['MONGODB_SETTINGS'] = { 'db' : 'books' }
app.config['SECRET_KEY'] = 'secretkey'
app.config['WTF_CSRF_ENABLED'] = True
db = MongoEngine(app)

login_manager = LoginManager()
login_manager.init_app(app)

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

#move to another file
class Book(db.Document):
	name = db.StringField(required=True)
	department = db.StringField(required=True)
	price = db.StringField(required=True)
	isbn = db.StringField(required=True)

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
    if request.method == 'POST' and form.validate():
        user = User(name=form.name.data,password=form.password.data)
        login_user(user)
        return redirect('/booklist')

    return render_template('login.html', form=form)


@app.route("/register", methods=["POST","GET"])
def registration():
  form = UserForm(request.form)
  if request.method == "POST" and form.validate():
    form.save()
    return redirect("/login")

  return render_template("register.html", form=form)

@app.route("/booklist/")
@login_required
def search():
        return render_template("booklist.html")

@app.route("/booklist/<id>")
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

@app.route("/sell/",methods=["POST,GET"])
@login_required
def sell():
	form = BookForm(request.form)
  if request.method=="POST" and form.validate():
    book = Book(name=form.name.data,department=form.department.data,price=form.price.data,isbn=form.department.data)
    book.save()
    return render_template("confirm.html")
  else:
    return render_template("sell.html")

@app.route("/bookinfo/")
@login_required
def bookinfo():
    return render_template("bookinfo.html")

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect("/")



app.run(debug=True)



