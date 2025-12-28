"""Tests for Database ORM Stage 3 - Relationships"""
import pytest
from solution import Model, StringField, IntField, ForeignKey


class Author(Model):
    name = StringField()


class Book(Model):
    title = StringField()
    author_id = ForeignKey("Author")


class OptionalBook(Model):
    title = StringField()
    author_id = ForeignKey("Author", required=False)


class TestORMStage3:
    def setup_method(self):
        Author.clear()
        Book.clear()
        OptionalBook.clear()

    def test_foreign_key(self):
        author = Author(name="J.K. Rowling")
        author.save()

        book = Book(title="Harry Potter", author_id=author.id)
        book.save()

        assert book.author_id == author.id

    def test_get_foreign(self):
        author = Author(name="Tolkien")
        author.save()

        book = Book(title="The Hobbit", author_id=author.id)
        book.save()

        related_author = book.get_foreign("author_id")
        assert related_author is not None
        assert related_author.name == "Tolkien"

    def test_get_related(self):
        author = Author(name="Asimov")
        author.save()

        Book(title="Foundation", author_id=author.id).save()
        Book(title="I, Robot", author_id=author.id).save()

        books = author.get_related(Book, "author_id")
        assert len(books) == 2

    def test_cascade_delete(self):
        author = Author(name="Hemingway")
        author.save()

        Book(title="The Old Man", author_id=author.id).save()
        Book(title="A Farewell", author_id=author.id).save()

        author.delete(cascade=True)

        assert Author.count() == 0
        assert Book.count() == 0

    def test_non_cascade_delete(self):
        author = Author(name="Orwell")
        author.save()

        Book(title="1984", author_id=author.id).save()
        author.delete(cascade=False)

        assert Author.count() == 0
        assert Book.count() == 1

    def test_optional_foreign_key(self):
        book = OptionalBook(title="Anonymous", author_id=None)
        # Should not raise since foreign key is optional
        book.save()
        assert book.author_id is None

    def test_filter_by_foreign_key(self):
        author1 = Author(name="Author1").save()
        author2 = Author(name="Author2").save()

        Book(title="Book1", author_id=author1.id).save()
        Book(title="Book2", author_id=author1.id).save()
        Book(title="Book3", author_id=author2.id).save()

        books = Book.query().filter(author_id=author1.id).all()
        assert len(books) == 2
