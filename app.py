import csv
import os
import io
from flask import Flask, make_response, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# Initialize Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['JWT_SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    isbn = db.Column(db.String(120), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class BorrowRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    hashed_password = generate_password_hash(password)
    user = User(email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={'id': user.id, 'role': user.role})
    return jsonify({'access_token': access_token}), 200

@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{'id': book.id, 'title': book.title, 'author': book.author, 'quantity': book.quantity} for book in books])

@app.route('/borrow-requests', methods=['POST'])
@jwt_required()
def borrow_request():
    data = request.json
    book_id = data.get('book_id')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    
    current_user = get_jwt_identity()
    user_id = current_user['id']

    book = Book.query.get(book_id)
    if not book or book.quantity <= 0:
        return jsonify({'message': 'Book not available'}), 400

    overlapping_request = BorrowRequest.query.filter(
        BorrowRequest.book_id == book_id,
        BorrowRequest.status == 'approved',
        BorrowRequest.start_date <= end_date,
        BorrowRequest.end_date >= start_date
    ).first()

    if overlapping_request:
        return jsonify({'message': 'Book is already borrowed during this period'}), 400

    borrow_request = BorrowRequest(user_id=user_id, book_id=book_id, start_date=start_date, end_date=end_date)
    db.session.add(borrow_request)
    db.session.commit()
    return jsonify({'message': 'Borrow request submitted'}), 201

@app.route('/borrow-requests', methods=['GET'])
@jwt_required()
def view_borrow_requests():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Access forbidden'}), 403

    requests = BorrowRequest.query.all()
    return jsonify([{
        'id': req.id,
        'user_id': req.user_id,
        'book_id': req.book_id,
        'start_date': req.start_date,
        'end_date': req.end_date,
        'status': req.status
    } for req in requests])

@app.route('/borrow-requests/<int:request_id>', methods=['PATCH'])
@jwt_required()
def approve_or_deny_request(request_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Access forbidden'}), 403

    data = request.json
    status = data.get('status')

    borrow_request = BorrowRequest.query.get(request_id)
    if not borrow_request:
        return jsonify({'message': 'Request not found'}), 404

    if status == 'approved':
        book = Book.query.get(borrow_request.book_id)
        if book.quantity <= 0:
            return jsonify({'message': 'Book not available'}), 400

        book.quantity -= 1

    if status == 'denied' and borrow_request.status == 'approved':
        book = Book.query.get(borrow_request.book_id)
        book.quantity += 1

    borrow_request.status = status
    db.session.commit()
    return jsonify({'message': 'Request updated successfully'}), 200

@app.route('/download-history', methods=['GET'])
@jwt_required()
def download_history():
    current_user = get_jwt_identity()
    borrow_requests = BorrowRequest.query.filter_by(user_id=current_user['id']).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Borrow ID', 'Book Title', 'Start Date', 'End Date', 'Status'])
    for request in borrow_requests:
        book = Book.query.get(request.book_id)
        writer.writerow([request.id, book.title, request.start_date, request.end_date, request.status])
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=borrow_history.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)

