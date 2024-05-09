from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import unquote, quote
from config import Config

import logging
from flask_migrate import Migrate
from flask_session import Session
from datetime import datetime
from logging.handlers import RotatingFileHandler
import traceback

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stors.db'
application.config['SECRET_KEY'] = '@dsfdsghsaw2436edgrq'
application.config['SESSION_TYPE'] = 'sqlalchemy'  # Тип сессии
db = SQLAlchemy(application)
handler = RotatingFileHandler('errors.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
application.logger.addHandler(handler)

application.config['SESSION_SQLALCHEMY'] = db
application.config.from_object(Config)
migrate = Migrate(application, db)
Session(application)

# Определение модели для таблицы Product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    volume = db.Column(db.Float, nullable=False)
    article = db.Column(db.String(100), nullable=False)
    strength = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    сountry = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(200), nullable=True)
    def __init__(self,id,name,type,volume,article,strength,price,сountry,photo):
        self.id=id
        self.name=name
        self.type=type
        self.volume=volume
        self.article=article
        self.strength=strength
        self.price=price
        self.сountry=сountry
        self.photo=photo

# Определение модели для таблицы Purchase
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.String(200), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IP-адрес может быть длиннее, если вы используете IPv6
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=True)

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, product_id, user_id):
        self.product_id = product_id
        self.user_id = user_id

Global_product=[
    Product(1, 'Виски шотл. односолод. SN "Гленфиддик Экспер.ИПА" 43% 0,7л туба', 'Виски', 0.7, '314645', 43.0, 8700.0, 'Соединенное Королевство', '/static/image/ViskiIPA.jpg'),
    Product(2, 'Виски шотл. односол. DL "Макаллан" 12 лет', 'Виски', 0.7, '304529', 40.0, 17990.0, 'Соединенное Королевство', '/static/image/viskiMagallan.jpg'),
    Product(3, 'Виски шотланд. купаж. PR "Баллантайнс Файнест"', 'Виски', 0.7, '114674', 40.0, 2690.0, 'Соединенное Королевство', '/static/image/viskiBalland.jpg'),
    Product(4, 'Виски шотланд. купаж. DG "Джонни Уокер" Black 12 лет', 'Виски', 0.7, '305096', 40.0, 3590.0, 'Соединенное Королевство', '/static/image/viskiBalland.jpg'),
    Product(5, 'Вино SN "Поместье Голубицкое Резерв Каберне-Совиньон"', 'Вино', 0.75, '316369', 13.7, 3590.0, 'Россия', '/static/image/vinoSn.jpg'),
    Product(6, 'Вино ISSI "Эль Аутоктоно" Паис Секано Интерьор', 'Вино', 0.75, '320655', 13.5, 890.0, 'ЧИЛИ', '/static/image/VinoISSI.jpg'),
    Product(7, 'Вино SM "Гуидальберто" IGT Тоскана красное сухое', 'Вино', 0.75, '307629', 14.0, 8490.0, 'ИТАЛИЯ', '/static/image/VinoSM.jpg'),
    Product(8, 'Ром "Captain Morgan" Original Spiced Rum', 'Ром', 0.7, '123456', 40.0, 1200.0, 'США', '/static/image/CaptainMorgan.jpg'),
    Product(9, 'Ром "Bacardi" Gold', 'Ром', 0.7, '234567', 38.0, 1100.0, 'Куба', '/static/image/Bacardi.jpg'),
    Product(10, 'Ром "Diplomatico Reserva Exclusiva" 0.7 л', 'Ром', 0.7, '16825', 40.0, 3449.0, 'Венесуэла', '/static/image/DonQCristal.jpg'),
    Product(11, 'Ром "Havana Club 7 Years" 0.7 л', 'Ром', 0.7, '38481', 40.0, 1699.0, 'Куба', '/static/image/Cruzan.jpg'),
    Product(12, 'Коньяк "Hennessy VS" 0.7 л', 'Коньяк', 0.7, '16836', 40.0, 1499.0, 'Франция', '/static/image/hennessi.jpg'),
    Product(13, 'Бренди "St. Remy XO" 0.7 л', 'Бренди', 0.7, '5450', 40.0, 1199.0, 'Франция', '/static/image/StRemyXO.jpg'),
    Product(14, 'Арманьяк "Janneau VSOP" 0.7 л', 'Арманьяк', 0.7, '32459', 40.0, 1199.0, 'Франция', '/static/image/JanneauVSOP.jpg'),
    Product(15, 'Коньяк "Courvoisier VS" 0.5 л', 'Коньяк', 0.5, '375', 40.0, 1499.0, 'Франция', '/static/image/Courvoisier.jpg'),
    Product(16, 'Текила "Jose Cuervo Especial" Blanco 0.7 л', 'Текила', 0.7, '17994', 38.0, 939.0, 'Мексика', '/static/image/JoseCuervoEspecial.jpg'),
    Product(17, 'Текила "Patron Reposado" 0.75 л', 'Текила', 0.75, '15794', 40.0, 4299.0, 'Мексика', '/static/image/PatronReposado.jpg'),
    Product(18, 'Текила "Sauza Gold" 0.7 л', 'Текила', 0.7, '12976', 38.0, 749.0, 'Мексика', '/static/image/SauzaGold.jpg'),
    Product(19, 'Текила "El Jimador Blanco" 0.7 л', 'Текила', 0.7, '17988', 38.0, 999.0, 'Мексика', '/static/image/ElJimadorBlanco.jpg'),
    Product(20, 'Джин "Bombay Sapphire" 0.75 л', 'Джин', 0.75, '15406', 47.0, 1669.0, 'Англия', '/static/image/BombaySapphire.jpg'),
    Product(21, 'Джин "Beefeater London Dry" 0.7 л', 'Джин', 0.7, '16437', 40.0, 1279.0, 'Англия', '/static/image/BeefeaterLondonDry.jpg'),
    Product(22, 'Джин "Tanqueray London Dry" 0.7 л', 'Джин', 0.7, '12525', 47.3, 1289.0, 'Англия', '/static/image/TanquerayLondonDry.jpg'),
    Product(23, 'Джин "Gordon''s London Dry" 0.7 л', 'Джин', 0.7, '11419', 37.5, 899.0, 'Англия', '/static/image/sLondonDry.jpg'),
    Product(24, 'Водка "Absolut" 0.7 л', 'Водка', 0.7, '19217', 40.0, 869.0, 'Швеция', '/static/image/Absolut.jpg'),
    Product(25, 'Водка "Russian Standard" 0.5 л', 'Водка', 0.5, '20426', 40.0, 359.0, 'Россия','/static/image/RussianStandard.jpg'),
    Product(26, 'Водка "Finlandia" 0.7 л', 'Водка', 0.7, '19234', 40.0, 739.0, 'Финляндия', '/static/image/Finlandia.jpg'),
    Product(27, 'Водка "Beluga" 0.5 л', 'Водка', 0.5, '20426', 40.0, 869.0, 'Россия', '/static/image/Beluga.jpg'),
    Product(28, 'Ликер "Бэйлиз" Original 0.7 л', 'Ликеры', 0.7, '19329', 17.0, 1199.0, 'Ирландия', '/static/image/Belis.jpg'),
    Product(29, 'Ликер "Амаретто Дисаронно" 0.7 л', 'Ликеры', 0.7, '19271', 28.0, 1399.0, 'Италия', '/static/image/Amaretto.jpg'),
    Product(30, 'Вермут "Martini Rosso" 0.5 л', 'Вермуты', 0.5, '19423', 16.0, 799.0, 'Италия', '/static/image/Rosso.jpg'),
    Product(31, 'Вермут "Martini Bianco" 0.5 л', 'Вермуты', 0.5, '19267', 16.0, 799.0, 'Италия', '/static/image/Bianco.jpg'),
    Product(32, 'Пиво "Heineken" светлое 0.5 л', 'Пиво. Сидр. Слабоалкогольные напитки', 0.5, '19153', 5.0, 119.0, 'Голландия', '/static/image/Heineken.jpg'),
    Product(33, 'Пиво "Stella Artois" светлое 0.5 л', 'Пиво. Сидр. Слабоалкогольные напитки', 0.5, '19027', 5.0, 110.0, 'Бельгия', '/static/image/StellaArtois.jpg'),
    Product(34, 'Сидр "Somersby" яблочный 0.5 л', 'Пиво. Сидр. Слабоалкогольные напитки', 0.5, '18575', 4.5, 99.0, 'Дания', '/static/image/Somersby.jpg'),
    Product(35, 'Сидр "Strongbow Gold" яблочный 0.5 л', 'Пиво. Сидр. Слабоалкогольные напитки', 0.5, '19629', 4.5, 139.0, 'Англия', '/static/image/StrongbowGold.jpg'),
    Product(36, 'Пиво "Heineken" светлое 0.5 л', 'Пиво. Сидр. Слабоалкогольные напитки', 0.5, '19153', 5.0, 119.0, 'Голландия', '/static/image/Heineken.jpg'),
    Product(37, 'Пиво "Stella Artois" светлое 0.5 л', 'Пиво. Сидр. Слабоалкогольные напитки', 0.5, '19027', 5.0, 110.0, 'Бельгия', '/static/image/StellaArtois.jpg'),
    Product(38, 'Сидр "Somersby" яблочный 0.5 л', 'Пиво. Сидр. Слабоалкогольные напитки', 0.5, '18575', 4.5, 99.0, 'Дания', '/static/image/Somersby.jpg'),
    Product(39, 'Сидр "Strongbow Gold" яблочный 0.5 л', 'Пиво. Сидр. Слабоалкогольные напитки', 0.5, '19629', 4.5, 139.0, 'Англия', '/static/image/StrongbowGold.jpg')
]
global_User_id=None
@application.route('/')
def main():
    global global_User_id
    client_ip = request.remote_addr
    if 'user_id' not in session:
        # Если сессии нет, создаем новую сессию и связываем ее с пользователем
        user = find_user_by_ip(client_ip)
        if user:
            session['user_id'] = user.id
            global_User_id = user.id
        else:
            user = add_user(client_ip)
            session['user_id'] = user.id
            global_User_id=user.id
    else:
        # Если сессия уже есть, просто получаем пользователя по идентификатору
        user_id = session['user_id']
        user = User.query.get(user_id)
        # Обновляем IP-адрес пользователя, если он изменился
        if user.ip_address != client_ip:
            user.ip_address = client_ip
            db.session.commit()
        global_User_id=user.id
    return render_template("main.html")
def add_user(ip):
    new_user = User(ip_address=ip)
    db.session.add(new_user)
    db.session.commit()
    session['user_id'] = new_user.id  # Сохраняем идентификатор пользователя в сессии
    return new_user
def find_user_by_ip(ip_address):
    user = User.query.filter_by(ip_address=ip_address).first()
    return user
@application.route('/store')
def store():
    global global_User_id
    client_ip = request.remote_addr
    if 'user_id' not in session:
        # Если сессии нет, создаем новую сессию и связываем ее с пользователем
        user = find_user_by_ip(client_ip)
        if user:
            session['user_id'] = user.id
            global_User_id = user.id
        else:
            user = add_user(client_ip)
            session['user_id'] = user.id
            global_User_id = user.id
    else:
        # Если сессия уже есть, просто получаем пользователя по идентификатору
        user_id = session['user_id']
        user = User.query.get(user_id)
        # Обновляем IP-адрес пользователя, если он изменился
        if user.ip_address != client_ip:
            user.ip_address = client_ip
            db.session.commit()
        global_User_id = user.id
    return render_template("store.html")
@application.route('/filtr/<type>', methods=['GET', 'POST'])
def filtr(type):
    cleaned_string = type.replace('<', '').replace('>', '')
    cleaned_string = str(cleaned_string)
    productsTypre = Product.query.filter_by(type=cleaned_string)

    price_min = request.form.get('price-min', type=float)
    price_max = request.form.get('price-max', type=float)
    volume_min = request.form.get('volume-min', type=float)
    volume_max = request.form.get('volume-max', type=float)

    # Применяем фильтры, если они не None
    if price_min is not None:
        productsTypre = productsTypre.filter(Product.price >= price_min)
    if price_max is not None:
        productsTypre = productsTypre.filter(Product.price <= price_max)
    if volume_min is not None:
        productsTypre = productsTypre.filter(Product.volume >= volume_min)
    if volume_max is not None:
        productsTypre = productsTypre.filter(Product.volume <= volume_max)
    # Получение результатов фильтрации
    productsTypre = productsTypre.all()

    return render_template('FiltrAl.html', products=productsTypre)
@application.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        if len(search_query)<=0:
            return render_template("main.html")
        if (len(Product.query.filter_by(type=search_query).all()) >= 1
                or search_query=="Коньяк" or search_query=="Бренди" or search_query=="Арманьяк"or
        search_query=="Пиво" or search_query=="Сидр" or search_query=="Слабоалкогольные напитки"):
                if search_query=="Коньяк" or search_query=="Бренди" or search_query=="Арманьяк":
                    product = Product.query.filter_by(type="Коньяк").all()
                if search_query=="Пиво" or search_query=="Сидр" or search_query=="Слабоалкогольные напитки":
                    product = Product.query.filter_by(type="Пиво. Сидр. Слабоалкогольные напитки").all()
                else:
                    product = Product.query.filter_by(type=search_query).all()
                return render_template("FiltrAl.html", products=product)

        if len(Product.query.filter_by(name=search_query).all()) >= 1:
            product = Product.query.filter_by(name=search_query).all()
            return render_template("FiltrAl.html", products=product)

        if  Product.query.filter_by(article=search_query).first():
            product = Product.query.filter_by(article=search_query).first()
            return render_template("Product.html",products=product)
        else:
            return render_template("ProductNone.html")
@application.route('/filtrAl/<type>', methods=['GET', 'POST'])
def filtrAl(type):
    # Encode the type parameter for use in a URL
    global Global_product
    encoded_type = quote(type)
    cleaned_string = type.replace('<', '').replace('>', '')
    cleaned_string = str(cleaned_string)
    try:
        # Use the decoded_type in your database query
        products = Product.query.filter_by(type=cleaned_string).all()
        if products:
            return render_template("FiltrAl.html", products=products)
        else:
            for productOne in Global_product:
                if productOne.type==cleaned_string:
                    products.append(productOne)
            return render_template("FiltrAl.html", products=products)
    except Exception as e:
        # Decode the encoded_type back to the original string
        decoded_type = unquote(encoded_type)
        # If there's an error, re-encode the original type to show in the error message
        encoded_type = quote(type)
        encod=quote(cleaned_string)
        raise Exception(f"This is a sample error: --   {encoded_type} --- {decoded_type} -- {encod}")
@application.errorhandler(Exception)
def handle_exception(e):
    trace = traceback.format_exc()
    # Запись ошибки в лог с трассировкой стека
    application.logger.error(f"An error occurred: {e}\nTraceback:\n{trace}")
    # Возврат сообщения об ошибке пользователю
    return "An internal server error occurred", 500
@application.route('/discounts')
def discounts():
    global global_User_id
    client_ip = request.remote_addr
    if 'user_id' not in session:
        # Если сессии нет, создаем новую сессию и связываем ее с пользователем
        user = find_user_by_ip(client_ip)
        if user:
            session['user_id'] = user.id
            global_User_id = user.id
        else:
            user = add_user(client_ip)
            session['user_id'] = user.id
            global_User_id = user.id
    else:
        # Если сессия уже есть, просто получаем пользователя по идентификатору
        user_id = session['user_id']
        user = User.query.get(user_id)
        # Обновляем IP-адрес пользователя, если он изменился
        if user.ip_address != client_ip:
            user.ip_address = client_ip
            db.session.commit()
        global_User_id = user.id
    return render_template("discounts.html")

@application.route('/company')
def company():
    global global_User_id
    client_ip = request.remote_addr
    if 'user_id' not in session:
        # Если сессии нет, создаем новую сессию и связываем ее с пользователем
        user = find_user_by_ip(client_ip)
        if user:
            session['user_id'] = user.id
            global_User_id = user.id
        else:
            user = add_user(client_ip)
            session['user_id'] = user.id
            global_User_id = user.id
    else:
        # Если сессия уже есть, просто получаем пользователя по идентификатору
        user_id = session['user_id']
        user = User.query.get(user_id)
        # Обновляем IP-адрес пользователя, если он изменился
        if user.ip_address != client_ip:
            user.ip_address = client_ip
            db.session.commit()
        global_User_id = user.id
    return render_template("Company.html")

@application.route('/buyer')
def buyer():
    return render_template("buyer.html")

@application.route('/Product/<id>')
def product(id):
    global global_User_id
    client_ip = request.remote_addr
    if 'user_id' not in session:
        # Если сессии нет, создаем новую сессию и связываем ее с пользователем
        user = find_user_by_ip(client_ip)
        if user:
            session['user_id'] = user.id
            global_User_id = user.id
        else:
            user = add_user(client_ip)
            session['user_id'] = user.id
            global_User_id = user.id
    else:
        # Если сессия уже есть, просто получаем пользователя по идентификатору
        user_id = session['user_id']
        user = User.query.get(user_id)
        # Обновляем IP-адрес пользователя, если он изменился
        if user.ip_address != client_ip:
            user.ip_address = client_ip
            db.session.commit()
        global_User_id = user.id
    StringId = id.replace('<', '').replace('>', '')
    id=int(StringId)
    products = Product.query.filter_by(id=id).first()

    return render_template("Product.html",products=products)

@application.route('/Product/buy/<id>')
def product_byu(id):
    global global_User_id
    client_ip = request.remote_addr
    if 'user_id' not in session:
        # Если сессии нет, создаем новую сессию и связываем ее с пользователем
        user = find_user_by_ip(client_ip)
        if user:
            session['user_id'] = user.id
            global_User_id = user.id
        else:
            user = add_user(client_ip)
            session['user_id'] = user.id
            global_User_id = user.id
    else:
        # Если сессия уже есть, просто получаем пользователя по идентификатору
        user_id = session['user_id']
        user = User.query.get(user_id)
        # Обновляем IP-адрес пользователя, если он изменился
        if user.ip_address != client_ip:
            user.ip_address = client_ip
            db.session.commit()
        global_User_id = user.id
    StringId = id.replace('<', '').replace('>', '')
    product_id = int(StringId)
    products = Product.query.filter_by(id=product_id).first()

    cart_buy=Cart(product_id,global_User_id)

    db.session.add(cart_buy)
    db.session.commit()
    return render_template("Product.html",products=products)

@application.route('/basket')
def basket():
    cart_products = db.session.query(Product).join(Cart, Product.id == Cart.product_id).filter(
    Cart.user_id == global_User_id).all()

    return render_template("basket.html",products=cart_products)

@application.route('/buy_product/<int:product_id>', methods=['GET', 'POST'])
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        delivery_address = request.form.get('delivery_address')
        delivery_date = datetime.strptime(request.form.get('delivery_date'), '%Y-%m-%dT%H:%M')

        purchase = Purchase(product_id=product_id, price=product.price, delivery_address=delivery_address,
                            order_date=datetime.now(), delivery_date=delivery_date)
        db.session.add(purchase)
        db.session.commit()
        cart_item = Cart.query.filter_by(product_id=product_id, user_id=global_User_id).first()
        if cart_item:
            # Удаляем товар из корзины
            db.session.delete(cart_item)
            db.session.commit()

        flash('Покупка совершена успешно!', 'success')
        return redirect(url_for('main'))
    else:
        return render_template('buy_product.html', product=product)


if __name__ == "__main__":
    with application.app_context():
        db.create_all()
    application.run(debug=True,host='0.0.0.0')