import yaml
from .models import Shop, Category, Product, ProductsInShop, Parameter, ProductParameter, Order, OrderItem

# класс для yaml файла: считывание, конвертация в JSON формат,
# добавление дааных yaml файла в базу данных
class Shop_YReader():

    def __init__(self, yfile):
        self.yfile = yfile

    def parse_yaml(self):
        with open(self.yfile, 'r') as f:
            json_file = yaml.load(f, Loader=yaml.Loader)
            return json_file

    def insert_to_db(self, json_file):
        try:
            # добавление названия магазина
            shop, created = Shop.objects.get_or_create(name=json_file['shop'])

            # добавление всех категорий товара
            for category in json_file['categories']:
                category_object, created = Category.objects.get_or_create(id=category['id'], name=category['name'])
                category_object.shops.add(shop.id)
                category_object.save()

            # удаление старых товаров
            ProductsInShop.objects.filter(shop_id=shop.id).delete()

            # добавление товаров с подробной информацией о них
            for item in json_file['goods']:
                product, created = Product.objects.get_or_create(name=item['name'], model=item['model'],
                                                           category_id=item['category'])

                products_in_shop = ProductsInShop.objects.create(product_id=product.id,
                                                                 shop_id=shop.id,
                                                                 price=item['price'],
                                                                 price_rcc=item['price_rrc'],
                                                               quantity=item['quantity'])
                # добавление параметров товара
                for name, value in item['parameters'].items():
                    parameter_object, created = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.create(product_in_shop_id=products_in_shop.id,
                                                    parameter_id=parameter_object.id,
                                                    value=value)
        except:
            return False
        else:
            return True