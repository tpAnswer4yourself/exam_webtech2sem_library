from flask import Blueprint, render_template, request
from models import db, Book, Genre

main_bp = Blueprint('main', __name__)

# главная страница
# в рамках 3 варианта реализована реализщована фильтрация для поиска книг
@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    query = Book.query

    title_search = request.args.get('title', '').strip()
    author_search = request.args.get('author', '').strip()
    genres_search = request.args.getlist('genres') 
    years_search = request.args.getlist('years')
    pages_from = request.args.get('pages_from', type=int)
    pages_to = request.args.get('pages_to', type=int)

    if title_search:
        query = query.filter(Book.title.ilike(f'%{title_search}%'))
    if author_search:
        query = query.filter(Book.author.ilike(f'%{author_search}%'))
    if genres_search:
        query = query.filter(Book.genres.any(Genre.id.in_([int(g) for g in genres_search])))
    if years_search:
        query = query.filter(Book.year.in_([int(y) for y in years_search]))
    if pages_from is not None:
        query = query.filter(Book.pages >= pages_from)
    if pages_to is not None:
        query = query.filter(Book.pages <= pages_to)

    pagination = query.order_by(Book.year.desc()).paginate(page=page, per_page=10, error_out=False)
    
    all_genres = Genre.query.all()
    distinct_years_query = db.session.query(Book.year).distinct().order_by(Book.year.desc()).all()
    distinct_years = [y[0] for y in distinct_years_query]

    return render_template('index.html', pagination=pagination, genres=all_genres, years=distinct_years, search_args=request.args)