from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    outstanding_debt = db.Column(db.Float, default=0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date_issued = db.Column(db.Date, nullable=False)
    date_returned = db.Column(db.Date, nullable=True)
    rent_fee = db.Column(db.Float, nullable=True)
@app.route('/')
def home():
    return render_template('index.html')

# Routes for Books
@app.route('/books')
def books():
    books = Book.query.all()
    return render_template('books.html', books=books)

@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        name = request.form['name']
        author = request.form['author']
        stock = request.form['stock']

        book = Book(name=name, author=author, stock=stock)
        db.session.add(book)
        db.session.commit()
        return redirect('/books')

    return render_template('add_book.html')

@app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get(id)

    if request.method == 'POST':
        book.name = request.form['name']
        book.author = request.form['author']
        book.stock = request.form['stock']

        db.session.commit()
        return redirect('/books')

    return render_template('edit_book.html', book=book)

@app.route('/books/delete/<int:id>', methods=['POST'])
def delete_book(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return redirect('/books')

# Routes for Members
@app.route('/members')
def members():
    members = Member.query.all()
    return render_template('members.html', members=members)

# Routes for Transactions
@app.route('/transactions')
def transactions():
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)

@app.route('/transactions/issue', methods=['GET', 'POST'])
def issue_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        date_issued = request.form['date_issued']

        book = Book.query.get(book_id)
        member = Member.query.get(member_id)

        if book.stock > 0:
            transaction = Transaction(book_id=book_id, member_id=member_id, date_issued=date_issued)
            book.stock -= 1
            db.session.add(transaction)
            db.session.commit()
            return redirect('/transactions')
        else:
            return 'Book out of stock'

    books = Book.query.all()
    members = Member.query.all()
    return render_template('issue_book.html', books=books, members=members)

@app.route('/transactions/return/<int:id>', methods=['GET', 'POST'])
def return_book(id):
    transaction = Transaction.query.get(id)

    if request.method == 'POST':
        transaction.date_returned = request.form['date_returned']
        transaction.rent_fee = request.form['rent_fee']

        book = Book.query.get(transaction.book_id)
        book.stock += 1

        member = Member.query.get(transaction.member_id)
        member.outstanding_debt += float(request.form['rent_fee'])

        db.session.commit()
        return redirect('/transactions')

    return render_template('return_book.html', transaction=transaction)
if __name__ == '__main__':
    app.run(debug=True)
