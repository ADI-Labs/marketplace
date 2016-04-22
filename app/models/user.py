from .. import db
from wtforms import validators

class User(db.Document):
    name = db.StringField(validators=[validators.Email(), validators.Regexp(".*@columbia.edu")],required=True,unique=True)
    password = db.StringField(required=True)
    contact_info = db.StringField(required=False)
    def is_authenticated(self):
        users = User.objects(name=self.name, password=self.password)
        return len(users) != 0
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.name
