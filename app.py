from flask import Flask,  render_template, request
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager
from flask.ext.mongoengine.wtf import model_form
from wtforms import PasswordField
import requests

app = Flask(__name__)
app.config["DEBUG"] = True      
app.config['MONGODB_SETTINGS'] = { 'db' : 'books' }
app.config['SECRET_KEY'] = 'secretkey'
db = MongoEngine(app)

login_manager = LoginManager()
login_manager.init_app(app)


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

UserForm = model_form(User)
UserForm.password = PasswordField('password')

@login_manager.user_loader
def load_user(name):
  users = User.objects(name=name)
  if len(users) != 0:
    return users[0]
  else:
    return None

@app.route("/")
def home():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(name=form.name.data,password=form.password.data)
        login_user(user)
        return render_template("booklist.html")

    return render_template('login.html', form=form)


@app.route("/register/", methods=["POST","GET"])
def registration():
  form = UserForm(request.form)
  if request.method == "POST" and form.validate():
    form.save()
    return redirect("/login")

  return render_template("register.html", form=form)

@app.route("/booklist/")
def search():
        return render_template("booklist.html")

@app.route("/booklist/<id>")
def s(id):
    if request.method=="POST":
        data=id
        return render_template("booklist.html",api_data=data)
    return redirect("/booklist")

@app.route("/book/<id>")
def book(id):
    data=id
    return render_template("book.html",api_data=data)

@app.route("/sell/",methods=["POST,GET"])
def sell():
    if request.method=="POST":
        name=request.form["name"]
        department=request.form["dep"]
        price=request.form("price")
        isbn=request.form("price")
        return render_template("confirm.html")
    else:
        return render_template("sell.html")

@app.route("/bookinfo/")
def bookinfo():
    return render_template("bookinfo.html")


app.run(debug=True)



