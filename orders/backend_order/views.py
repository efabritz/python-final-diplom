import datetime
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import *
from .exceptions import *
from django.http import JsonResponse
from .permissions import *
from rest_framework.views import APIView
from .YReader import Shop_YReader
from .serializers import *
from .EmailBackend import *
from .tasks import registration_email_task, confirmation_order_email_task
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

# не получилось обычной генерации токен через админ
# path('auth/', obtain_auth_token)
# module_dir = os.getcwd() # get current directory
# file_path = os.path.join(module_dir, 'data', 'shop1.yaml')

###
# TODO:

# c1. Создано Celery-приложение c методами:
#    - send_email
#    - do_import
# 2. Создан view для запуска Celery-задачи do_import из админки.elery

###

# dockerize

###

# tests (?)



# POST http://localhost:8000/api/login/
# Content-Type: application/json
#
# {
#   "email": "katja.belova@gmail.com",
#   "password": "1234"
# }

# вход в приложение с помощью адреса эл. почты и пароля



class UserLogin(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    def post(self, request):
        user = authenticate(email=request.data.get('email'), password=request.data.get('password'))
        if not user:
            return JsonResponse({'Error': 'False email or password'})
        return JsonResponse({'Status': True})

# POST http://localhost:8000/api/register/
# Content-Type: application/json
#
# { "first_name": "Firstname",
#   "last_name":"Lastname",
#   "third_name":"-",
#   "username": "testuser",
#   "email": "katya-belova@inbox.ru",
#   "password": "1234",
#   "type": "-",
#   "company":"-",
#   "position": "-"
# }

# регистрация пользователя с необходимымы параметрами
class UserRegister(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    def post(self, request):
        if not {'first_name', 'last_name', 'third_name', 'email', 'password', 'username', 'company', 'position', 'type'}.issubset(request.data):
            return JsonResponse({'Status':'Error', 'Details':'Заполнены не все поля'})
        try:
            username = request.data['username']
            email = request.data['email']
            # проверка, существует ли пользователь с передаваемыми почтой и именем
            if User.objects.filter(username=username) or User.objects.filter(email=email):
                return JsonResponse({'Status': 'Error', 'Details': 'Имя или эл.почта пользователя уже существует'})
            # если не указан тип пользвателя, то установи тип "покупатель"
            if not (request.data['type'] in ['admin', 'shop', 'customer']):
                request.data['type'] = 'customer'
            user_serializer = UserSerializer(data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                user.set_password(request.data['password'])
                user.save()
               # registration_email(user.username, user.email)
                registration_email_task.delay(user.username, user.email)
                return JsonResponse({'Status': 'True', 'Details': f'Пользователь {user.username} создан'})
            else:
                return JsonResponse({'Status': 'Error', 'Details': 'Ошибка в базе данных'})
        except DatabaseTransferError:
            return JsonResponse({'Status': 'Error', 'Details': 'Ошибка при регистрации'})


# Products list


#
# GET http://localhost:8000/api/products/
# Content-Type: application/json

###
# Product
#
# GET http://localhost:8000/api/products/1/
# Content-Type: application/json

# классы для обрабоки товаров,
# просмотр доступен всем пользователя,
# остальные действия разрешены только админам

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsProductActionAllowed,)
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

class ProductInShopViewSet(ModelViewSet):
    queryset = ProductsInShop.objects.all()
    serializer_class = ProductsInShopSerializer
    permission_classes = (IsProductActionAllowed,)
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

# POST http://localhost:8000/api/basket/
# Content-Type: application/json
#
# {
#   "user_id": 1,
#   "quantity": 2,
#   "product": 1
# }

# товары добавляются в таблицу  Order, OrderItem
#
class BasketView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    def post(self, request):
        user_id = request.data['user_id']

        # проверка, существует ли пользователм с id
        if not user_id:
            raise UserNotFoundError
        try:
            # выборка пользователя
            user = User.objects.filter(id=user_id)[0]
        except DatabaseTransferError:
            return JsonResponse({'Status':'Error', 'Detail':'Пользователь не существует'})

        #количество и данные о продукте
        quantity = int(request.data['quantity'])
        product_id = request.data['product']

        # проверка, существует ли товар с данным id
        if not product_id:
            return JsonResponse({'Status': 'Error', 'Detail':'Товар не найден'})
        try:
            # выбор товара
            product = Product.objects.filter(id=product_id)[0]
            product_name = product.name
        except DatabaseTransferError:
            return JsonResponse({'Status':'Error', 'Detail':'Товар не существует'})
        # если количество товара не определено или меньше, равно нуля
        if not quantity or quantity <= 0:
            return JsonResponse({'Status': 'Error', 'Detail': 'Количество не определено'})
        try:
            # выбор деталям по товару
            products_in_shop = ProductsInShop.objects.filter(product=product_id)
        except DatabaseTransferError:
            return JsonResponse({'Status': 'Error', 'Detail':'Информация по товару не найдена'})

        # согласно БД только одно поле "товара в магазине" соотвествует одному "товару"
        product_in_shop = products_in_shop[0]

        # сколько товара доступно в магазине
        exs_quantity = int(product_in_shop.quantity)
        # если товара нет в наличии - ошибка
        if exs_quantity == 0:
            return JsonResponse({'Status': 'Error', 'Detail': 'Product is sold out'})
        # если желаемое количество товара превышает количество товара в наличии,
        # количество устанавливается на доступное
        order_quantity = exs_quantity if quantity > exs_quantity else quantity
        # рассчет цены товара
        price = float(product_in_shop.price) * order_quantity
        shop = product_in_shop.shop

        try:
            # создание заказа
            order, created = Order.objects.get_or_create(user=user, state='basket')
            OrderItem.objects.get_or_create(quantity=order_quantity, order=order, product=product, shop=shop)
        except DatabaseTransferError:
            return JsonResponse({'Status': 'Error', 'Detail':'Заказ не может быть добавлен в корзину'})
        return JsonResponse({'Status': 'True', 'Detail': f'Заказ нормер {order.id} был добавлен в корзину',
                            'Name': f'{product_name}', 'Quantity':f'{order_quantity}', 'Price': f'{price}'})

###
# POST http://localhost:8000/api/contact/
# Content-Type: application/json; charset=utf-8
# Authorization: Token 5cc7a17a5fed348b4a4023a112443c3d382aacb6
#
#
#  {
#  "country":"Russia",
#  "city":"Moscow",
#  "street":"street11",
#  "house":"11",
#  "building":"1",
#  "apartment":"11",
#  "index":"1111"
#  }

# класс для создания пользовательского адреса
# 
class AddUserAddressView(APIView):
    permission_classes = (IsAuthenticated,)
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    def post(self, request):
        user_id = request.user.id

        address_data = {"country": request.data['country'], "city": request.data['city'], "street": request.data['street'],
                        "house": request.data['house'], "building": request.data['building'],
                        "apartment": request.data['apartment'], "index": request.data['index'], 'user': user_id}

        address = None
        address_obj = UserAddress.objects.filter(user=user_id)

        if address_obj:
            address = address_obj[0]
        # проверка, существует ли адрес пользотеля, с переданным id, в таблице
        # если существует, то адрес нужно обновить
        if address:
            user_serializer = UserAddressSerializer(address, data=address_data, partial=True)
        else:
            user_serializer = UserAddressSerializer(data=address_data)

        if user_serializer.is_valid():
            # сохранение адреса в БД
            user_address = user_serializer.save()
            user_address.save()
            return JsonResponse({'Status': 'True', 'Detail': 'Aдрес сохранен'})
        else:
            return JsonResponse({'Status': 'Error', 'Detail': 'Неверно заполнен адрес'})

# функция сохранения адреса пользователя
def confirm_user_address(request):
    user_id = request.user.id
    # проверка адреса пользователя, который вводится
    address_data = {"country": request.data['country'], "city": request.data['city'], "street": request.data['street'],
                    "house": request.data['house'], "building": request.data['building'],
                    "apartment": request.data['apartment'], "index": request.data['index'], 'user': user_id}

    address = None
    address_obj = UserAddress.objects.filter(user=user_id)

    if address_obj:
        address = address_obj[0]
    # проверка, существует ли адрес пользотеля, с переданным id, в таблице
    # если существует, то адрес нужно обновить
    if address:
        user_serializer = UserAddressSerializer(address, data=address_data, partial=True)
    else:
        user_serializer = UserAddressSerializer(data=address_data)

    if user_serializer.is_valid():
        # сохранение адреса в БД
        user_address = user_serializer.save()
        user_address.save()
        return True
    else:
        return False


#
# PATCH http://localhost:8000/api/confirm/
# Content-Type: application/json
# Authorization: Token 5cc7a17a5fed348b4a4023a112443c3d382aacb6

#
# {
# "order_id": 1,
#  "country":"Russia",
#  "city":"Moscow",
#  "street":"street11",
#  "house":"11",
#  "building":"1",
#  "apartment":"11",
#  "index":"1111"
# }
# подтверждение пользовательского заказа
class OrderConfirmationView(APIView):
    # пользователь должен быть авторизован
    permission_classes = (IsAuthenticated,)
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    def patch(self, request):
        user_id = request.user.id
        # поиск пользователя по id
        user = User.objects.filter(id=user_id)[0]
        username = f'{user.last_name} {user.first_name}'

        # вызов функции, кот. сохраняет/обновляет адрес пользователя
        if not confirm_user_address(request):
            return JsonResponse({'Status': 'Error', 'Detail': 'Неверно заполнен адрес'})

        # адрес пользователя из БД
        address_obj = UserAddress.objects.filter(user=user_id)

        order_id = request.data['order_id']
        if not order_id:
            raise OrderNotFoundError

        try:
            # поиск заказа по id
            order = Order.objects.filter(id=order_id)[0]
            order_items = OrderItem.objects.filter(order=order_id)
        except OrderNotFoundError:
            print("Error: Заказ не существует")
            return JsonResponse({'Status': 'Error', 'Detail': 'Заказа не существует'})

        # проверка, совпадает ли id авторизированного пользователя с id, который был указан в заказе
        if order.user_id != user_id:
            return JsonResponse({'Status': 'Error', 'Detail': 'Ошибка пользователя'})

        if address_obj:
            address = address_obj[0]
        else:
            return JsonResponse({'Status': 'Error', 'Detail': 'Адрес не указан'})

        # формируется адресный словарь
        address_dict = UserAddressSerializer(address).data

        product_infos = {}

        # по каждому полю деталей заказа
        for item in order_items:
            # поиск информации по товару
            product = Product.objects.get(id=item.product_id)
            product_in_shop = ProductsInShop.objects.filter(product=product.id)[0]
            # проверка существующего количества
            exs_quantity = int(product_in_shop.quantity)
            # количества товара в заказе
            quantity = item.quantity
            # проверка, есть ли товар в наличии
            if exs_quantity == 0:
                return JsonResponse({'Status': 'Error', 'Detail': 'Товар раскуплен'})
            # если товара в наличии меньше, чем в заказе, выбери количество в наличии
            order_quantity = exs_quantity if quantity > exs_quantity else quantity

            # если настоящее количество товара в заказе отличается от рассчитаного, то выбери рассчитаную
            if quantity != order_quantity:
                item.quantity = order_quantity
                item.save()
            # рассчет цены
            price = float(product_in_shop.price) * order_quantity
            # информация по товарам записывается в словарь
            product_infos[product.id] = (product.name, product.model, order_quantity, price,)

        try:
            # изменение статуса заказа
            Order.objects.filter(id=order_id).update(state='confirmed', date=datetime.datetime.now(), user=user_id)

            # обновление количества в таблице товаров
            product_in_shop.quantity = exs_quantity - order_quantity
            product_in_shop.save()

            # подтверждение заказа с необходимыми параметрами
            # confirmation_order_email(request.user.email, username, order_id, product_infos, address_dict)
            confirmation_order_email_task.delay(request.user.email, username, order_id, product_infos, address_dict)
            return JsonResponse({'Status': 'True', 'Detail': f'Заказ {order_id} подтвержден'})
        except DatabaseTransferError:
            print('Database error during order confirmation')


        return JsonResponse({'Status': 'Error', 'Detail': 'Ошибка во время подтверждения заказа'})


# GET http://localhost:8000/api/thanks/
# Content-Type: application/json
# Authorization: Token 5cc7a17a5fed348b4a4023a112443c3d382aacb6

# отправление сообщения "Спасибо за заказ" авторизированному пользователю
class ThankForOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id

        if not user_id:
            raise UserNotFoundError

        try:
            user = User.objects.get(id=user_id)
            username = user.username
            message = f'{username} , спасибо за Ваш заказ'

            return JsonResponse({'Status': True, 'Message': f'{message}'})
        except UserNotFoundError:
            return JsonResponse({'Status': 'Error', 'Message': 'Пользователь не найден'})


# CL1 09 225 162 RU
# GET http://localhost:8000/api/orders/
# Content-Type: application/json
# Authorization: Token 5cc7a17a5fed348b4a4023a112443c3d382aacb6

# GET http://localhost:8000/api/orders/1/
# Content-Type: application/json
# Authorization: Token 5cc7a17a5fed348b4a4023a112443c3d382aacb6

# классы для просмотра товаров и конкретного товара
# пользователь должен быть авторизован
# просмотр заказа разрешен только пользователям, их создавшим или админу

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsOrderActionAllowed)
    throttle_classes = [AnonRateThrottle, UserRateThrottle]


# GET http://localhost:8000/api/order_detail/
# Content-Type: application/json
# Authorization: Token 5cc7a17a5fed348b4a4023a112443c3d382aacb6

# GET http://localhost:8000/api/order_detail/3/
# Content-Type: application/json
# Authorization: Token 5cc7a17a5fed348b4a4023a112443c3d382aacb6

class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = (IsAuthenticated, IsOrderActionAllowed)
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

# POST http://localhost:8000/api/shoplist/
# Content-Type: application/json
# Authorization: Token 444663674e877925a935be5884e8b5d630ffd6fc
#
# {
#     "shop": "test",
#     "url":"",
#     "file":"/home/ekaterina/PycharmProjects/final/python-final-diplom/orders/data/shop1.yaml"
# }

class SendShopList(APIView):
    # проверка на авторизированного супер-пользователя и разрешение транзакции
    permission_classes = (IsAuthenticated, IsTransferAllowed, )

    def post(self, request):
        # путь к файлу, содержащему информацию по магазину
        file = request.data.get('file')

        # создание объекта для парсинга yaml файла в json формат
        # и добавление данных в БД
        reader = Shop_YReader(file)
        json_file = reader.parse_yaml()

        # если возникло исключение во время чередачи данных в БД
        # переменная result будет False и вызовет исключение
        result = reader.insert_to_db(json_file)

        if result:
            return JsonResponse({'Status': True})
        else:
            raise DatabaseTransferError()