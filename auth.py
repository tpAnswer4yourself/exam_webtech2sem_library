from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from functools import wraps
from models import User

auth_bp = Blueprint('auth', __name__)

# декоратор прав доступа для ролей
def check_rights(role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Для выполнения данного действия необходимо пройти процедуру аутентификации!', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role.name not in role_names:
                flash('У вас недостаточно прав для выполнения данного действия!', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# вход в аккаунт
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        login_val = request.form.get('login')
        password_val = request.form.get('password')
        remember_val = request.form.get('remember') == 'on'

        user = User.query.filter_by(login=login_val).first()

        if user and check_password_hash(user.password_hash, password_val):
            login_user(user, remember=remember_val)
            flash('Вы успешно вошли в систему!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')

    return render_template('login.html')

# выход из аккаунта
@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно вышли из системы!', 'success')
    return redirect(url_for('main.index'))