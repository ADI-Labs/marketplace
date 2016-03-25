from .. import db

class Book(db.Document):
    user_name = db.StringField(required=True)
    book_name = db.StringField(required=True)
    price = db.StringField(required=True)
    contact_info = db.StringField(required=True)
    description = db.StringField(required=True)