from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

database = SQLAlchemy()


class User(database.Model):
    id = database.Column(database.String, primary_key=True, unique=True, nullable=False)
    username = database.Column(database.String, nullable=False, unique=True)
    password = database.Column(database.String, nullable=False)
    passwordHash = database.Column(database.String, nullable=False)

    def set_password(self, password):
        self.passwordHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwordHash, password)


class Book(database.Model):
    ISBN = database.Column(database.String, primary_key=True, unique=True, nullable=False)
    bookTitle = database.Column(database.String, nullable=False)
    bookAuthor = database.Column(database.String, nullable=False)
    bookPublisher = database.Column(database.String, nullable=False)
    yearOfPublication = database.Column(database.String, nullable=False)
    imageURL = database.Column(database.String, nullable=False)
    introduction = database.Column(database.String, nullable=False)
    totalRating = database.Column(database.Float, nullable=False, default=0)
    ratingCount = database.Column(database.Integer, nullable=False, default=0)

    def calculate_total_rating(self):
        ratings = Rating.query.filter_by(ISBN=self.ISBN).all()
        self.ratingCount = len(ratings)
        if ratings:
            self.totalRating = sum(r.rating for r in ratings) / len(ratings)
        else:
            self.totalRating = 0.0

    def update_total_rating(self):
        ratings = Rating.query.filter_by(ISBN=self.ISBN).all()
        self.ratingCount = len(ratings)
        if ratings:
            self.totalRating = sum(r.rating for r in ratings) / self.ratingCount
        else:
            self.totalRating = 0.0

    def to_dict(self):
        return {
            'ISBN': self.ISBN,
            'bookTitle': self.bookTitle,
            'bookAuthor': self.bookAuthor,
            'bookPublisher': self.bookPublisher,
            'yearOfPublication': self.yearOfPublication,
            'imageURL': self.imageURL,
            'introduction': self.introduction,
            'totalRating': self.totalRating,
            'ratingCount': self.ratingCount
        }


class Rating(database.Model):
    id = database.Column(database.String, database.ForeignKey('user.id'), primary_key=True, unique=True, nullable=False)
    ISBN = database.Column(database.String, database.ForeignKey('book.ISBN'), primary_key=True, nullable=False)
    rating = database.Column(database.Integer, nullable=False)

    user = database.relationship('User', backref=database.backref('ratings', lazy=True))
    book = database.relationship('Book', backref=database.backref('ratings', lazy=True))


class Comments(database.Model):
    id = database.Column(database.String, database.ForeignKey('user.id'), primary_key=True, unique=True, nullable=False)
    ISBN = database.Column(database.String, database.ForeignKey('book.ISBN'), primary_key=True, nullable=False)
    comment = database.Column(database.String, nullable=False)

    user = database.relationship('User', backref=database.backref('comments', lazy=True))
    book = database.relationship('Book', backref=database.backref('comments', lazy=True))


class RecommendBook(database.Model):
    id = database.Column(database.String, database.ForeignKey('user.id'), primary_key=True, unique=True, nullable=False)
    ISBN = database.Column(database.String, database.ForeignKey('book.ISBN'), primary_key=True, nullable=False)
    score = database.Column(database.Float, nullable=False)

    user = database.relationship('User', backref=database.backref('scores', lazy=True))
    book = database.relationship('Book', backref=database.backref('scores', lazy=True))