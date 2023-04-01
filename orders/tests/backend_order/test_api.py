import pytest
from rest_framework.test import APIClient
from backend_order.models import *


@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_superuser(username='admin', email='katja.belova@gmail.com', password='admin')

@pytest.fixture
def user_alternative():
    return User.objects.create_user(username='alt', email='katya-belova@inbox.ru', password='alt')

@pytest.mark.django_db
def test_shoplist(client, user):
    client.post('/auth/', data={"username": 'admin', "password": 'admin'})
    response = client.post('/api/shoplist/', data={ "shop": "test", "url":"", "file":"/home/ekaterina/PycharmProjects/final/python-final-diplom/orders/data/shop1.yaml"},
    **{ "HTTP_AUTHORIZATION": f"Token {user.auth_token}" })
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_products(client, user):
    client.post('/api/shoplist/', data={"shop": "test", "url": "",
                                        "file": "/home/ekaterina/PycharmProjects/final/python-final-diplom/orders/data/shop1.yaml"})
    response = client.get('/api/products/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_product_id(client, user):
    client.post('/auth/', data={"username": 'admin', "password": 'admin'})
    client.post('/api/shoplist/', data={"shop": "test", "url": "",
                                                   "file": "/home/ekaterina/PycharmProjects/final/python-final-diplom/orders/data/shop1.yaml"},
                           **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    response = client.get('/api/products/1/')
    assert response.data['name'] == 'Смартфон Apple iPhone XS Max 512GB (золотистый)'

@pytest.mark.django_db
def test_user_login(client, user):
    response = client.post('/api/login/', data={"email":"katja.belova@gmail.com", "password": "admin"})
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_false_email_login(client, user):
    response = client.post('/api/login/', data={"email":"k@gmail.com", "password": "admin"})
    json_response = response.json()
    assert json_response['Error']  == "False email or password"

@pytest.mark.django_db
def test_register(client):
    client.post('/api/register/', data={ "first_name": "Firstname", "last_name":"Lastname", "third_name":"-", "username": "testuser", "email": "katya-belova@inbox.ru", "password": "1234",
                                                   "type": "customer", "company":"-", "position": "-" })
    response_same_username = client.post('/api/register/',
               data={"first_name": "Firstname", "last_name": "Lastname", "third_name": "-", "username": "testuser",
                     "email": "katya-belova@inbox.ru", "password": "1234",
                     "type": "customer", "company": "-", "position": "-"})
    response_same_username_json = response_same_username.json()
    response_less_params = client.post('/api/register/',
               data={"first_name": "Firstname", "username": "testuser",
                     "email": "katya-belova@inbox.ru", "password": "1234",
                     "type": "customer", "company": "-", "position": "-"})
    response_less_params_json = response_less_params.json()
    user_found = User.objects.filter(email='katya-belova@inbox.ru')[0]
    assert user_found.username == 'testuser'
    assert response_same_username_json['Details'] == "Имя или эл.почта пользователя уже существует"
    assert response_less_params_json['Details'] == "Заполнены не все поля"

@pytest.mark.django_db
def test_basket(client, user):
    client.post('/auth/', data={"username": 'admin', "password": 'admin'})
    client.post('/api/shoplist/', data={"shop": "test", "url": "",
                                                   "file": "/home/ekaterina/PycharmProjects/final/python-final-diplom/orders/data/shop1.yaml"},
                           **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    response = client.post('/api/basket/', data={"user_id": 1, "quantity": 2, "product": 1}, **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    assert response.status_code == 200
    assert Order.objects.filter(user=user.id).count() == 1


@pytest.mark.django_db
def test_confirm(client, user):
    client.post('/auth/', data={"username": 'admin', "password": 'admin'})
    client.post('/api/shoplist/', data={"shop": "test", "url": "",
                                                   "file": "/home/ekaterina/PycharmProjects/final/python-final-diplom/orders/data/shop1.yaml"},
                           **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    client.post('/api/basket/', data={"user_id": 1, "quantity": 2, "product": 1},
                **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    response = client.patch('/api/confirm/', data={"order_id": 1, "country": "Russia", "city": "Moscow", "street": "street11", "house": "11", "building": "1",
                                                  "apartment": "11", "index": "1111"}, **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    assert response.status_code == 200
    assert Order.objects.filter(id=1)[0].state == 'confirmed'

@pytest.mark.django_db
def test_thanks(client, user):
    client.post('/auth/', data={"username": 'admin', "password": 'admin'})
    respone_auth = client.get('/api/thanks/', **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    respone_un_auth = client.get('/api/thanks/')
    respone_auth_json = respone_auth.json()

    assert respone_auth_json['Message'] == "admin , спасибо за Ваш заказ"
    assert respone_un_auth.status_code == 401

@pytest.mark.django_db
def test_order(client, user, user_alternative):
    client.post('/auth/', data={"username": 'admin', "password": 'admin'})
    client.post('/api/shoplist/', data={"shop": "test", "url": "",
                                        "file": "/home/ekaterina/PycharmProjects/final/python-final-diplom/orders/data/shop1.yaml"},
                **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    client.post('/api/basket/', data={"user_id": 1, "quantity": 2, "product": 1},
                **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    client.patch('/api/confirm/',
                            data={"order_id": 1, "country": "Russia", "city": "Moscow", "street": "street11",
                                  "house": "11", "building": "1",
                                  "apartment": "11", "index": "1111"},
                            **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    client.post('/auth/', data={"username": 'alt', "password": 'alt'})

    client.post('/api/basket/', data={"user_id": 2, "quantity": 1, "product": 1},
                **{"HTTP_AUTHORIZATION": f"Token {user_alternative.auth_token}"})
    client.patch('/api/confirm/',
                            data={"order_id": 2, "country": "Russia", "city": "Moscow", "street": "street11",
                                  "house": "11", "building": "1",
                                  "apartment": "11", "index": "1111"},
                            **{"HTTP_AUTHORIZATION": f"Token {user_alternative.auth_token}"})

    response_user = client.get('/api/orders/1/', **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})
    response_user_alt = client.get('/api/orders/1/', **{"HTTP_AUTHORIZATION": f"Token {user_alternative.auth_token}"})
    response_user_admin = client.get('/api/orders/2/', **{"HTTP_AUTHORIZATION": f"Token {user.auth_token}"})

    assert response_user.status_code == 200
    assert response_user_alt.status_code != 200
    assert response_user_admin.status_code == 200