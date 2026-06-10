from flask import Flask
from models import db, User
from flask_login import LoginManager
from sqlalchemy.engine import Engine
from sqlalchemy import event
import markdown
from auth import auth_bp
from main import main_bp
from books import books_bp
from reviews import reviews_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = '123123123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# поддержка каскадного удаления, поскольку в качестве СУБД используется SQLite 
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Для выполнения данного действия необходимо пройти процедуру аутентификации!"
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# фильтр для JINJA
@app.template_filter('markdown')
def render_markdown(text):
    return markdown.markdown(text)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(books_bp)
app.register_blueprint(reviews_bp)

if __name__ == '__main__':
    app.run(debug=True)