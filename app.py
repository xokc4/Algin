from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
from flask_session import Session
from datetime import datetime


application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stors.db'
application.config['SECRET_KEY'] = '@dsfdsghsaw2436edgrq'
application.config['SESSION_TYPE'] = 'sqlalchemy'  # Тип сессии
db = SQLAlchemy(application)
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
    cleaned_string = type.replace('<', '').replace('>', '')
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
@application.route('/filtrAl/<type>')
def filtrAl(type):
    if type=="<Вино>":
        cleaned_string = type.replace('<', '').replace('>', '')
        products = Product.query.filter_by(type=cleaned_string).all()

        return render_template("FiltrAl.html", products=products)

    if type == "<Виски>":
        cleaned_string = type.replace('<', '').replace('>', '')
        products = Product.query.filter_by(type=cleaned_string).all()

        return render_template("FiltrAl.html", products=products)


    if type=="<Ром>":
        cleaned_string = type.replace('<', '').replace('>', '')
        products = Product.query.filter_by(type=cleaned_string).all()

        return render_template("FiltrAl.html", products=products)


    if type == "<Коньяк>":
        cleaned_string = type.replace('<', '').replace('>', '')
        productsOne = Product.query.filter_by(type=cleaned_string).all()
        productsTwo= Product.query.filter_by(type="Арманьяк").all()
        productsThri= Product.query.filter_by(type="Бренди").all()
        products=productsOne + productsTwo + productsThri

        return render_template("FiltrAl.html", products=products)


    if type=="<Текила>":
        cleaned_string = type.replace('<', '').replace('>', '')
        products = Product.query.filter_by(type=cleaned_string).all()

        return render_template("FiltrAl.html", products=products)

    if type == "<Джин>":
        cleaned_string = type.replace('<', '').replace('>', '')
        products = Product.query.filter_by(type=cleaned_string).all()

        return render_template("FiltrAl.html", products=products)


    if type=="<Водка>":
        cleaned_string = type.replace('<', '').replace('>', '')
        products = Product.query.filter_by(type=cleaned_string).all()

        return render_template("FiltrAl.html", products=products)

    if type == "<Ликеры>":
        cleaned_string = type.replace('<', '').replace('>', '')
        productsOne = Product.query.filter_by(type=cleaned_string).all()
        productsTwo = Product.query.filter_by(type='Вермуты').all()
        products= productsOne + productsTwo

        return render_template("FiltrAl.html", products=products)


    if type=="<Пиво. Сидр. Слабоалкогольные напитки>":
        cleaned_string = type.replace('<', '').replace('>', '')
        products = Product.query.filter_by(type=cleaned_string).all()

        return render_template("FiltrAl.html", products=products)

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
    application.run(host='0.0.0.0')