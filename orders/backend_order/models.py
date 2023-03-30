from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('confirmed', 'Подтвержден'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('customer', 'Покупатель'),
    ('admin', 'Админ'),


)

class OrdersUserManager(BaseUserManager):
    def create_user(self, email, username, password, first_name, last_name):
        if not email:
            raise ValueError('Введите адрес эл.почты')
        if not username:
            raise ValueError('Введите имя пользователя')
        if not first_name:
            raise ValueError('Введите полное имя пользователя')
        if not last_name:
            raise ValueError('Введите фамилию пользователя')

        user = self.model(email=self.normalize_email(
            email), username=username, password=password)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email=self.normalize_email(
            email), username=username, password=password, type='admin')


class User(AbstractUser):

    first_name = models.CharField(max_length=50, verbose_name='Имя', null=False)
    last_name = models.CharField(max_length=30, verbose_name='Фамилия', null=False)
    third_name = models.CharField(max_length=50, verbose_name='Отчество', default='-')
    password = models.CharField(max_length=100, verbose_name='Пароль')
    email = models.EmailField(max_length=254, verbose_name='Эл.почта', unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True, default='-')
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True, default='-')
    type = models.CharField(verbose_name="Тип пользователя", choices=USER_TYPE_CHOICES, max_length=20, default='customer')


    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)

class UserAddress(models.Model):
    country = models.CharField(max_length=40, verbose_name="Страна", null=False)
    city = models.CharField(max_length=40, verbose_name="Город", null=False)
    street = models.CharField(max_length=40, verbose_name="Город", null=False)
    house = models.CharField(max_length=20, verbose_name="Дом", null=False)
    building = models.CharField(max_length=20, verbose_name="Строение")
    apartment = models.CharField(max_length=20, verbose_name="Квартира")
    index = models.IntegerField(verbose_name="Индекс", null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = "Адреса пользователей"

class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    filename = models.CharField(max_length=50, verbose_name='Имя файла', null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Магазины"

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name="categories")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = "Категории товаров"

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    model = models.CharField(max_length=100, verbose_name='Модель')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return self.name

class ProductsInShop(models.Model):
    quantity = models.IntegerField(verbose_name='Количество')
    price = models.FloatField(verbose_name='Цена')
    price_rcc = models.FloatField(verbose_name='Рекомендуемая цена')

    product = models.ForeignKey(Product, verbose_name='Товар', related_name='products_in_shop', blank=True,
                                 on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='products_in_shop', blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукты в магазине'
        verbose_name_plural = "Список продуктов в магазине"

class Parameter(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Параметры"

class ProductParameter(models.Model):
    value = models.CharField(max_length=50, verbose_name='Значение')

    product_in_shop = models.ForeignKey(ProductsInShop, verbose_name='Товар в магазине', related_name='product_parameters', blank=True,
                                on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', related_name='product_parameters', blank=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Параметр товара'
        verbose_name_plural = "Параметры товара"


class Order(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    state = models.CharField(verbose_name='Статус', choices=STATE_CHOICES, max_length=15)

    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='orders', blank=True,
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Заказы"

class OrderItem(models.Model):
    quantity = models.IntegerField(verbose_name='Количество')

    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='order_items', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='order_items', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказ в деталях'
        verbose_name_plural = "Заказы в деталях"