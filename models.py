from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    budget = db.Column(db.Integer)
    users = db.relationship('User', backref='group', lazy=True)
    cart_items = db.relationship('CartItem', backref='group', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    quantity = db.Column(db.Integer)
    category = db.Column(db.String)
    contributor = db.Column(db.String)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
