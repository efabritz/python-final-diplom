from django.contrib import admin

from .models import User, Shop, Category, Product, ProductsInShop, Parameter, ProductParameter, Order, OrderItem, UserAddress

class ProductsInShopInline(admin.TabularInline):
    model = ProductsInShop
    extra = 3

class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 3

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 3

class ShopInline(admin.TabularInline):
    model = Shop
    extra = 3

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'third_name', 'email', 'password', 'company', 'position']


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'country', 'city', 'street', 'house', 'building', 'apartment', 'index', 'user']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url', 'filename']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_shops']

    def get_shops(self, db_obj):
        return [shop.name for shop in db_obj.shops.all()]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'model', 'category']
    inlines = [ProductsInShopInline, ]


@admin.register(ProductsInShop)
class ProductsInShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'quantity', 'price', 'price_rcc', 'product', 'shop']
    inlines = [ProductParameterInline, ]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ['id', 'value', 'parameter']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'state', 'user']
    inlines = [OrderItemInline, ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'quantity', 'order', 'product', 'shop']

