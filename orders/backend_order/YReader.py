import yaml
from .models import Shop, Category, Product, ProductsInShop, Parameter, ProductParameter, Order, OrderItem
from .tasks import insert_to_db_task

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
        result = insert_to_db_task.delay(json_file)
        return result