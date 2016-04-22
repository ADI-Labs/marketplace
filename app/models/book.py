from .. import db


class Book(db.Document):
    user_name = db.StringField(required=False)
    book_name = db.StringField(required=True)
    price = db.StringField(required=True)
    contact_info = db.StringField(required=False)
    description = db.StringField(required=False)
    image = db.StringField(required=False)
