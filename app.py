from flask import Flask,  render_template, request
import requests

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register/", methods=["POST","GET"])
def registration():
    if request.method=="POST":
        name=request.form["name"]
        phone_number=request.form["number"]
        email=request.form["email"]
        return render_template("index.html")

@app.route("/search/<id>",methods=["POST,GET"])
def search():
    if request.method=="POST":
        data=request.form["book_search"]
        return render_template("search.html",api_data=data)
    else:
        return render_template("search.html")

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
app.run(debug=True)
