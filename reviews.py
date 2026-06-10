from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from models import db, Book, Review
from auth import check_rights
import bleach

reviews_bp = Blueprint('reviews', __name__)

# добавление отзыва к книге
@reviews_bp.route('/books/<int:id>/review', methods=['GET', 'POST'])
@check_rights(['Администратор', 'Модератор', 'Пользователь'])
def add_review(id):
    book = db.session.get(Book, id)
    if not book:
        return redirect(url_for('main.index'))
    
    existing_review = Review.query.filter_by(book_id=id, user_id=current_user.id).first()
    if existing_review:
        flash('Вы уже оставили рецензию на эту книгу.', 'warning')
        return redirect(url_for('books.view_book', id=id))

    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        raw_text = request.form.get('text', '').strip()
        
        if not raw_text:
            flash('Текст рецензии не может быть пустым!', 'danger')
            return render_template('books/review.html', book=book)

        clean_text = bleach.clean(raw_text)

        try:
            review = Review(book_id=id, user_id=current_user.id, rating=rating, text=clean_text)
            db.session.add(review)
            db.session.commit()
            flash('Рецензия успешно добавлена!', 'success')
            
            return redirect(url_for('books.view_book', id=id))
        except Exception:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка.', 'danger')
            return render_template('books/review.html', book=book)

    return render_template('books/review.html', book=book)