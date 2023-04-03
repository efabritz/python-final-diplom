from rest_framework import serializers
from .models import User, UserAddress, Shop, Category, Product, ProductsInShop, Parameter, ProductParameter, \
    Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'third_name', 'email', 'username', 'company', 'position', 'type')

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ('id', 'country', 'city', 'street', 'house', 'building', 'apartment', 'index', 'user')

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'filename',)

class CategorySerializer(serializers.ModelSerializer):
    shops = ShopSerializer(many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'shops',)

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ('id', 'name', 'model', 'category',)

class ProductsInShopSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    shop = ShopSerializer()

    class Meta:
        model = ProductsInShop
        fields = ('id', 'quantity', 'price', 'price_rcc', 'product', 'shop',)

class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('id', 'name',)

class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = Parameter()

    class Meta:
        model = ProductParameter
        fields = ('id', 'value', 'product_in_shop', 'parameter',)

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'date', 'state', 'user',)

class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    class Meta:
        model = OrderItem
        fields = ('id', 'quantity', 'order', 'product', 'shop',)