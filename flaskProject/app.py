from datetime import timedelta

import shortuuid
from flask import Flask, request, session
from flask_cors import CORS
from sqlalchemy import or_

from config import Config
from models import database, User, Book, Rating, Comments, RecommendBook
from result import Result

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config.from_object(Config)
database.init_app(app)
CORS(app, origin="*")


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    ID = data.get('id')
    password = data.get('password')
    if ID is None or password is None:
        return Result.fail('Missing fields')

    if User.query.filter_by(id=ID).first():
        return Result.fail('User already exists')

    shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123")
    username = shortuuid.uuid()[1:11]
    user = User(id=ID, username=username, password=password)
    user.set_password(password)
    database.session.add(user)

    try:
        database.session.commit()
        return Result.ok('registered successfully')
    except Exception as e:
        database.session.rollback()
        return Result.fail('Database error: ' + str(e))


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    ID = data["id"]
    password = data["password"]
    user = User.query.filter_by(id=ID).first()

    if user is None or not user.check_password(password):
        return Result.fail('Invalid credentials')

    session['user_id'] = user.id
    print(session)
    data = [{
        "id": user.id,
        "username": user.username
    }]
    return Result.ok('Logged in successful', data)


@app.route('/api/logout', methods=['POST'])
def logout():
    print(session)
    session.pop('user_id', None)
    return Result.ok('Logged out successfully')


@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query')

    if not query:
        return Result.fail('Empty query')

    searched_book = Book.query.filter(
        or_(
            Book.bookTitle.like(f'%{query}%'),
            Book.bookAuthor.like(f'%{query}%')
        )).all()

    books_list = [{
        'ISBN': the_book.ISBN,
        'imageURL': the_book.imageURL,
        'bookTitle': the_book.bookTitle,
        'bookAuthor': the_book.bookAuthor,
        'bookPublisher': the_book.bookPublisher,
        'yearOfPublication': the_book.yearOfPublication
    } for the_book in searched_book]

    return Result.ok(message="Search successfully", data=books_list)


@app.route('/api/book', methods=['POST'])
def book():
    isbn = request.args.get('isbn')
    # print(isbn)
    found_book = Book.query.filter_by(ISBN=isbn).first()
    # print(found_book.to_dict())
    if not found_book:
        return Result.fail('Book not found')

    return Result.ok(message="find book successfully", data=found_book.to_dict())


@app.route('/api/books', methods=['POST'])
def books():
    all_books = Book.query.all()
    books_list = [{
        'ISBN': show_book.ISBN,
        'bookTitle': show_book.bookTitle,
        'bookAuthor': show_book.bookAuthor,
        'bookPublisher': show_book.bookPublisher,
        'yearOfPublication': show_book.yearOfPublication,
        'imageURL': show_book.imageURL,
        'introduction': show_book.introduction
    } for show_book in all_books]

    return Result.ok(message="all books show successfully", data=books_list)


@app.route('/api/book/rating', methods=['POST'])
def book_rating():
    data = request.get_json()
    isbn = data.get('ISBN')
    rating_value = data.get('rating')
    userid = data.get('userid')

    existing_rating = Rating.query.filter_by(id=userid, ISBN=isbn).first()
    if existing_rating:
        existing_rating.rating = rating_value
    else:
        rating = Rating(id=userid, ISBN=isbn, rating=rating_value)
        database.session.add(rating)

    rated_book = Book.query.filter_by(ISBN=isbn).first()
    if rated_book:
        rated_book.update_total_rating()
        database.session.add(rated_book)

    try:
        database.session.commit()
        return Result.ok('Book ratings successfully')
    except Exception as e:
        database.session.rollback()
        return Result.fail('Database error: ' + str(e))


@app.route("/api/books/hot", methods=['POST'])
def hot_books():
    ten_books = Book.query.filter(Book.ratingCount > 0).order_by(
        Book.ratingCount.desc(),
        Book.totalRating.desc()
    ).limit(12).all()

    hot_book_list = [{
        'ISBN': hot_book.ISBN,
        'bookTitle': hot_book.bookTitle,
        'bookAuthor': hot_book.bookAuthor,
        'bookPublisher': hot_book.bookPublisher,
        'yearOfPublication': hot_book.yearOfPublication,
        'totalRating': hot_book.totalRating,
        'imageURL': hot_book.imageURL,
        'introduction': hot_book.introduction
    } for hot_book in ten_books]

    return Result.ok(message="Fetched hot books successfully", data=hot_book_list)


@app.route('/api/comment/update', methods=['POST'])
def update_comment():
    data = request.get_json()
    isbn = data.get('ISBN')
    ID = data.get('id')
    newComment = data.get('comment')

    existing_comment = Comments.query.filter_by(id=ID, ISBN=isbn).first()
    if existing_comment:
        existing_comment.comment = newComment
    else:
        comment = Comments(id=ID, ISBN=isbn, comment=newComment)
        database.session.add(comment)

    try:
        database.session.commit()
        return Result.ok('Comment updated successfully')
    except Exception as e:
        database.session.rollback()
        return Result.fail('Database error: ' + str(e))


@app.route('/api/comments', methods=['POST'])
def comments():
    data = request.get_json()
    isbn = data.get("ISBN")
    all_comments = Comments.query.filter_by(ISBN=isbn).all()
    comments_list = []

    for show_comment in all_comments:
        user = User.query.get(show_comment.id)
        comments_list.append({
            "id": show_comment.id,
            "ISBN": show_comment.ISBN,
            "comment": show_comment.comment,
            "username": user.username if user else "Unknown"
        })

    return Result.ok(message="all comments show successfully", data=comments_list)


@app.route("/api/recommend", methods=['POST'])
def recommend():
    data = request.get_json()
    ID = data.get('id')
    recommend_books = RecommendBook.query.filter_by(id=ID).limit(4).all()
    recommend_books_list = []
    for recommend_book in recommend_books:
        the_book = Book.query.get(recommend_book.ISBN)
        recommend_books_list.append({
            "ISBN": the_book.ISBN,
            "bookTitle": the_book.bookTitle,
            "bookAuthor": the_book.bookAuthor,
            "bookPublisher": the_book.bookPublisher,
            "yearOfPublication": the_book.yearOfPublication,
            "totalRating": the_book.totalRating,
            "imageURL": the_book.imageURL,
            "introduction": the_book.introduction
        })

    return Result.ok(message="Fetched recommend books successfully", data=recommend_books_list)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
