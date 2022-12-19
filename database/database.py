# Импорты
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

# Подключение к базе данных
import sqlite3
path=r'database\dbForLS.db'
connect = sqlite3.connect(path, check_same_thread=False)
cursor = connect.cursor()

# Создание таблицы с пользователями
cursor.execute('''CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER NOT NULL UNIQUE,
    "login" TEXT NOT NULL UNIQUE,
    "password" TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
    );''')
connect.commit()

# Создание таблицы для ссылок
cursor.execute('''CREATE TABLE IF NOT EXISTS "links" (
    "id" INTEGER UNIQUE NOT NULL,
    "user_id" INTEGER NOT NULL REFERENCES users (id),
    "initial_link" TEXT NOT NULL,
    "short_link" TEXT NOT NULL,
    "access" TEXT NOT NULL,
    "number_of_transitions" INTEGER NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
    );''')
connect.commit()

# РАБОТА С БАЗОЙ ДАННЫХ

# Добавление пользователя в базу данных
def registration_user (login, password):
    reg = cursor.execute('SELECT login FROM users').fetchall()
    users = []
    for item in reg:
        users.append(item[0])
    if (login in users):
        return "Такой пользователь уже есть!"
    else:
        cursor.execute('INSERT INTO users(login, password) VALUES(?, ?)', (login, generate_password_hash(password)))
        connect.commit()
        return "Вы успешно зарегистрировались!"

# Проверка пользователя
def userCheck (login) :
    data = "SELECT users.* FROM users WHERE login= :login"
    result = cursor.execute(data, {'login': login}).fetchone()
    connect.commit()
    return result

# Авторизация пользователя
def authorization_user (user, login, password):
    if check_password_hash(user[2], password):
        token = create_access_token(identity=login)
        return f"Пользователь с логином, {login}, авторизован! Ваш токен - {token}"
    else:
        return "Данные указаны неверно!"

# Добавление ссылки
def add_links (user_id, initial_link, short_link, access, number_of_transitions):
    action = "INSERT INTO links (user_id, initial_link, short_link, access, number_of_transitions) VALUES (:user_id, :initial_link, :short_link, :access, :number_of_transitions)"
    cursor.execute(action, {'user_id':user_id, 'initial_link':initial_link, 'short_link':short_link, 'access':access, 'number_of_transitions':number_of_transitions})
    connect.commit()

# Вывод ссылок пользователя
def all_links_of_user (user_id):
    action = "SELECT links.short_link FROM links WHERE user_id= :user_id"
    result = cursor.execute(action, {'user_id': user_id}).fetchall()
    connect.commit()
    return result

# Удаление ссылки
def delete_links (user_id, short_link):
    action = "DELETE FROM links WHERE user_id=:user_id AND short_link=:short_link"
    cursor.execute(action, {'user_id': user_id, 'short_link': short_link})
    connect.commit()

# Изменение сокращенной ссылки
def change_short_link (user_id, old_short_link, new_short_link):
    action = "UPDATE links SET short_link=:new_short_link WHERE short_link=:old_short_link AND user_id=:user_id"
    cursor.execute(action, {'old_short_link': old_short_link, 'new_short_link': new_short_link, 'user_id': user_id})
    connect.commit()

# Изменение доступа ссылки
def change_access_links (user_id, short_link, access) :
    action = "UPDATE links SET access=:access WHERE short_link=:short_link AND user_id=:user_id"
    cursor.execute(action, {'short_link': short_link, 'access': access, 'user_id': user_id})
    connect.commit()

# Поиск сокращенной ссылки ????????
def get_link (short_link) :
    result = cursor.execute("SELECT links.* FROM links WHERE short_link=:short_link", {'short_link': short_link}).fetchone()
    connect.commit()
    return result

# Подсчет переходов по ссылке
def counting_clicks_on_the_link(short_link, number_of_transitions) :
    result = cursor.execute('''UPDATE links SET number_of_transitions=? WHERE short_link=?''', (number_of_transitions + 1, short_link,))
    connect.commit()
    return result
