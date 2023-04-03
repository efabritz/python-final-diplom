from time import sleep

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Shop, Category, Product, ProductsInShop, Parameter, ProductParameter, Order, OrderItem

# отправление сообщения на эл. почту после регистрации
@shared_task()
def registration_email_task(username, recipient_email):
    subject = 'Регистрация на ORDERS сайте'
    message = f'Добро пожаловать на сайт, {username}'
    recipient_list = [recipient_email]
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

# отправление сообщения на эл. почту после подтверждения заказа
@shared_task()
def confirmation_order_email_task(recipient_email, username, order_id, product_infos, address_dict):
    address_str = f'{address_dict["country"]}, {address_dict["city"]}, {address_dict["street"]}, ' \
                  f'{address_dict["house"]},{address_dict["building"]}, {address_dict["apartment"]}, ' \
                  f'{address_dict["index"]}'
    subject = f'Ваш заказ Nr. {order_id} подтвержден'

    product_info_str = ""
    for item in product_infos:
        product_info_str += f'Информация о заказе:' \
                            f'\nНазвание: {product_infos[item][0]} \nМодель {product_infos[item][1]} \nКоличество: {product_infos[item][2]}  \n' \
                            f'Цена: {product_infos[item][3]}'
    message = f'{username}, Ваш заказ подтвержден.\n' \
              f'Details: Номер заказа: {order_id}, {product_info_str}\n' \
              f'Адрес доставки: {address_str}'
    recipient_list = [recipient_email]
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=recipient_list)



@shared_task()
def insert_to_db_task(json_file):
    try:
        ''' добавление названия магазина '''
        shop, created = Shop.objects.get_or_create(name=json_file['shop'])

        ''' добавление всех категорий товара '''
        for category in json_file['categories']:
            category_object, created = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()

        ''' удаление старых товаров '''
        ProductsInShop.objects.filter(shop_id=shop.id).delete()

        ''' добавление товаров с подробной информацией о них '''
        for item in json_file['goods']:
            product, created = Product.objects.get_or_create(name=item['name'], model=item['model'],
                                                             category_id=item['category'])

            products_in_shop = ProductsInShop.objects.create(product_id=product.id,
                                                             shop_id=shop.id,
                                                             price=item['price'],
                                                             price_rcc=item['price_rrc'],
                                                             quantity=item['quantity'])
            ''' добавление параметров товара '''
            for name, value in item['parameters'].items():
                parameter_object, created = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(product_in_shop_id=products_in_shop.id,
                                                parameter_id=parameter_object.id,
                                                value=value)
    except:
        return False
    else:
        return True
