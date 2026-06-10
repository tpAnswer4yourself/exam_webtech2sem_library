from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from models import db, Book, Genre, Cover
from auth import check_rights
import os
import hashlib
import bleach
import markdown
from werkzeug.utils import secure_filename

books_bp = Blueprint('books', __name__)

BASE_DIR = os.path.abspath(os.path.dirname(__name__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'covers')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# добавление новой книги
@books_bp.route('/books/add', methods=['GET', 'POST'])
@check_rights(['Администратор'])
def add_book():
    genres = Genre.query.all()
    if request.method == 'POST':
        try:
            title = request.form['title']
            year = request.form['year']
            pages = request.form['pages']
            publisher = request.form['publisher']
            author = request.form['author']
            clean_description = bleach.clean(request.form['short_description'])

            file = request.files.get('cover_img')
            if not file or not file.filename:
                flash('Обложка обязательна!', 'danger')
                return render_template('books/add.html', genres=genres)
            
            file_content = file.read()
            md5_hash = hashlib.md5(file_content).hexdigest()
            file.seek(0)
            
            existing_cover = Cover.query.filter_by(md5_hash=md5_hash).first()

            book = Book(title=title, short_description=clean_description, year=year, pages=pages, publisher=publisher, author=author)
            db.session.add(book)
            db.session.flush()

            genre_ids = request.form.getlist('genres')
            for genre_id in genre_ids:
                genre = db.session.get(Genre, int(genre_id))
                if genre:
                    book.genres.append(genre)

            new_cover = Cover(mime_type=file.mimetype, md5_hash=md5_hash, book_id=book.id, file_name='temp')
            db.session.add(new_cover)
            db.session.flush()

            if existing_cover:
                new_cover.file_name = existing_cover.file_name
            else:
                ext = os.path.splitext(secure_filename(file.filename))[1]
                new_cover.file_name = f"{new_cover.id}{ext}"
            
            db.session.commit()

            if not existing_cover:
                file_path = os.path.join(UPLOAD_FOLDER, new_cover.file_name)
                file.save(file_path)

            flash('Книга успешно добавлена!', 'success')
            return redirect(url_for('books.view_book', id=book.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"ОШИБКА БД ПРИ СОХРАНЕНИИ: {e}") 
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
    
    return render_template('books/add.html', genres=genres)

# редактирование существующей книги
@books_bp.route('/books/<int:id>/edit', methods=['GET', 'POST'])
@check_rights(['Администратор', 'Модератор'])
def edit_book(id):
    book = db.session.get(Book, id)
    if not book:
        return redirect(url_for('main.index'))
    genres = Genre.query.all()

    if request.method == 'POST':
        try:
            book.title = request.form['title']
            book.year = request.form['year']
            book.pages = request.form['pages']
            book.publisher = request.form['publisher']
            book.author = request.form['author']
            book.short_description = bleach.clean(request.form['short_description'])

            book.genres.clear()
            for genre_id in request.form.getlist('genres'):
                genre = db.session.get(Genre, int(genre_id))
                if genre:
                    book.genres.append(genre)

            db.session.commit()
            flash('Данные книги успешно обновлены!', 'success')
            return redirect(url_for('books.view_book', id=book.id))
        except Exception:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка.', 'danger')

    return render_template('books/edit.html', book=book, genres=genres)

# просмотр отдельной книги по айдишнику
@books_bp.route('/books/<int:id>')
def view_book(id):
    book = db.session.get(Book, id)
    if not book:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('main.index'))
    
    description_html = markdown.markdown(book.short_description)
    
    user_review = None
    if current_user.is_authenticated:
        for r in book.reviews:
            if r.user_id == current_user.id:
                user_review = r
                break
    
    return render_template('books/view.html', book=book, description_html=description_html, user_review=user_review)

# удаление книги
@books_bp.route('/books/<int:id>/delete', methods=['POST'])
@check_rights(['Администратор'])
def delete_book(id):
    book = db.session.get(Book, id)
    if not book:
        flash('Книга не найдена!', 'danger')
        return redirect(url_for('main.index'))
    try:
        title = book.title
        file_path = os.path.join(UPLOAD_FOLDER, book.cover.file_name) if book.cover else None
        
        db.session.delete(book)
        db.session.commit()
        
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            
        flash(f'Книга "{title}" успешно удалена!', 'success')
    except Exception:
        db.session.rollback()
        flash('Произошла ошибка при удалении книги.', 'danger')
        
    return redirect(url_for('main.index'))