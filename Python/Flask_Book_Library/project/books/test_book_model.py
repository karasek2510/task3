import unittest
from project import app, db
from project.books.models import Book
from sqlalchemy.exc import DataError, IntegrityError

class BookModelTestCase(unittest.TestCase):

    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        # Drop all tables after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_valid_book_creation(self):
        with app.app_context():
            book = Book(
                name='Valid Book',
                author='Author Name',
                year_published=2021,
                book_type='Fiction',
                status='available'
            )
            db.session.add(book)
            db.session.commit()

            retrieved_book = Book.query.filter_by(name='Valid Book').first()
            self.assertIsNotNone(retrieved_book)
            self.assertEqual(retrieved_book.author, 'Author Name')
            self.assertEqual(retrieved_book.year_published, 2021)
            self.assertEqual(retrieved_book.book_type, 'Fiction')
            self.assertEqual(retrieved_book.status, 'available')

    def test_missing_required_fields(self):
        with app.app_context():
            book = Book(
                name=None,
                author='Author Name',
                year_published=2021,
                book_type='Fiction'
            )
            db.session.add(book)
            with self.assertRaises(IntegrityError):
                db.session.commit()

    def test_invalid_year_published_type(self):
        with app.app_context():
            book = Book(
                name='Book with Invalid Year',
                author='Author Name',
                year_published='Two Thousand Twenty-One',
                book_type='Fiction'
            )
            db.session.add(book)
            with self.assertRaises(DataError):
                db.session.commit()
                
    def test_negative_year_published(self):
        with app.app_context():
            book = Book(
                name='Book with Negative Year',
                author='Author Name',
                year_published=-100,
                book_type='Fiction'
            )
            db.session.add(book)
            db.session.commit()

            retrieved_book = Book.query.filter_by(name='Book with Negative Year').first()
            self.assertIsNotNone(retrieved_book)
            self.assertEqual(retrieved_book.year_published, -100)

    def test_extremely_long_name(self):
        with app.app_context():
            long_name = 'a' * 1000
            book = Book(
                name=long_name,
                author='Author Name',
                year_published=2021,
                book_type='Fiction'
            )
            db.session.add(book)
            with self.assertRaises(DataError):
                db.session.commit()

    def test_sql_injection_in_name(self):
        with app.app_context():
            malicious_input = "'; DROP TABLE books; --"
            book = Book(
                name=malicious_input,
                author='Author Name',
                year_published=2021,
                book_type='Fiction'
            )
            db.session.add(book)
            with self.assertRaises(DataError):
                db.session.commit()

    def test_javascript_injection_in_name(self):
        with app.app_context():
            malicious_input = "<script>alert('hack');</script>"
            book = Book(
                name=malicious_input,
                author='Author Name',
                year_published=2021,
                book_type='Fiction'
            )
            db.session.add(book)
            with self.assertRaises(DataError):
                db.session.commit()

if __name__ == '__main__':
    unittest.main()
