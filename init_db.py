from app import app
from models import db, Role, User, Genre
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    if not Role.query.first():
        role_admin = Role(name='Администратор', description='Суперпользователь, имеет полный доступ к системе, в том числе к созданию и удалению книг')
        role_moder = Role(name='Модератор', description='Может редактировать данные книг и производить модерацию рецензий')
        role_user = Role(name='Пользователь', description='Может оставлять рецензии')
        db.session.add(role_admin)
        db.session.add(role_moder)
        db.session.add(role_user)
        db.session.commit()

        # создание пользователей
        admin = User(
            login='admin123',
            password_hash=generate_password_hash('123123'),
            last_name='Админов',
            first_name='Админ',
            middle_name='Проверяевич',
            role_id=role_admin.id
        )
        moder = User(
            login='moder123',
            password_hash=generate_password_hash('123123'),
            last_name='Редакторов',
            first_name='Модер',
            middle_name='Евгеньевич',
            role_id=role_moder.id
        )
        user_one = User(
            login='user1',
            password_hash=generate_password_hash('123123'),
            last_name='Иванов',
            first_name='Борис',
            middle_name='Харитонович',
            role_id=role_user.id
        )
        user_two = User(
            login='user2',
            password_hash=generate_password_hash('123123'),
            last_name='Петров',
            first_name='Александр',
            middle_name='Алексеевич',
            role_id=role_user.id
        )
        user_three = User(
            login='user3',
            password_hash=generate_password_hash('123123'),
            last_name='Лесовой',
            first_name='Аркадий',
            middle_name='Ильич',
            role_id=role_user.id
        )
        
        db.session.add(admin)
        db.session.add(moder)
        db.session.add(user_one)
        db.session.add(user_two)
        db.session.add(user_three)

        # наполнение жанрами
        g1 = Genre(name='Фантастика')
        g2 = Genre(name='Детектив')
        g3 = Genre(name='Триллер')
        g4 = Genre(name='Роман')
        g5 = Genre(name='Лирика')
        
        db.session.add(g1)
        db.session.add(g2)
        db.session.add(g3)
        db.session.add(g4)
        db.session.add(g5)

        db.session.commit()
        
        print("Успешная инициализация БД!")
    else:
        print("БД уже содержит данные!")