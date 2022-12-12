# Импорты
import database.database as db
from flask import Flask, request, redirect, make_response
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
import hashlib, random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Ваш секретный ключ'
jwt = JWTManager(app)

# Регистрация
@app.route('/register', methods = ["post"])
def registration():
    if request.method == 'POST':
        login = str(request.json.get('login', None))
        password = str(request.json.get('password', None))
        if (login != '') and (password != ''):
            return make_response(db.registration_user(login, password))
        else:
            return make_response("Введите данные!")

# Авторизация
@app.route('/auth', methods = ["post"])
def authorization():
    if request.method == 'POST':
        login = str(request.json.get('login', None))
        password = str(request.json.get('password', None))
        if (login != '') and (password != ''):
            user = db.userCheck(login)
            if user != None:
                return make_response(db.authorization_user(user, login, password))
        else:
            return make_response("Введите данные!")

# Добавление ссылки
@app.route("/linkRed", methods=['POST'])
@jwt_required()
def link_reduction():
    if request.method == 'POST':
        login = str(get_jwt_identity())
        initial_link = str(request.json.get("initial_link", None))
        short_link = str(request.json.get('short_link'))
        number_of_transitions = 0
        if short_link == "":
            short_link = hashlib.md5(initial_link.encode()).hexdigest()[:random.randint(8,12)]
        access = 'public'
        db.add_links(login, initial_link, short_link, access, number_of_transitions)
        return make_response(f'Ссылка успешно добавлена. Ваша сокращенная ссылка - {short_link}')

# Удаление ссылки
@app.route("/delete_link", methods=['POST'])
@jwt_required()
def delete_link():
    login = str(get_jwt_identity())
    short_link = str(request.json.get("short_link", None))
    db.delete_links(login, short_link)
    return make_response('Ссылка успешно удалена!')

# Изменение псевдонима ссылки
@app.route("/change_short_link", methods=['POST'])
@jwt_required()
def change_short_link():
    login = str(get_jwt_identity())
    old_short_link = str(request.json.get("old_short_link", None))
    new_short_link = str(request.json.get("new_short_link", None))
    db.change_short_link(login, old_short_link, new_short_link)
    return make_response('Ваша сокращенная ссылка успешно изменена!')

# Изменение доступа
@app.route("/change_access_link", methods=['POST'])
@jwt_required()
def change_access_link():
    login = str(get_jwt_identity())
    short_link = str(request.json.get("short_link", None))
    access = str(request.json.get("access", None))
    db.change_access_links(login, short_link, access)
    return make_response('Доступ успешно изменен!')

# Переход по ссылке
@app.route("/linking", methods=['POST'])
def red(short_link):
    link = db.get_link(short_link)
    short_link_count = link[5]
    # Подсчет переходов
    db.counting_clicks_on_the_link(short_link, short_link_count)
    return redirect(link[2])

# Возврат полной ссылки для зарегистрированного пользователя
@app.route("/return_link_for_reg_user", methods=['POST'])
@jwt_required()
def return_link_for_reg_user():
    login = str(get_jwt_identity())
    short_link = str(request.json.get("short_link", None))
    user = db.userCheck(login)
    link = db.get_link(short_link)
    if link != None:
        if user[1] == link[1] and link[4] == 'private':
            if short_link == link[3]:
                return red(short_link)
            else:
                return make_response("Такой ссылки не существует!")
        else:
            if short_link == link[3]:
                return red(short_link)
            else:
                return make_response("Такой ссылки не существует или она Вам недоступна!")
    else:
        return make_response("Ссылки не существует в базе данных!")

# Возврат полной ссылки для незарегистрированного пользователя
@app.route("/return_link_for_unreg_user", methods=['POST'])
def return_link_for_unreg_user():
    short_link = str(request.json.get("short_link", None))
    link = db.get_link(short_link)
    if link != None and link[4] == 'public':
        return red(short_link)
    else:
        return make_response("Такой ссылки не существует или она вам недоступна!")

# Возврат ссылок авторизованного пользователя
@app.route("/get_links_auth_user", methods=['POST'])
@jwt_required()
def get_links_auth_user():
    login = str(get_jwt_identity())
    links = db.all_links_of_user(login)
    if links != []:
        return make_response(f"Ваши сокращенные ссылки: \n {links}")
    else:
        return make_response("У вас нет сокращенных ссылок!")

if __name__ == '__main__':
    app.run()