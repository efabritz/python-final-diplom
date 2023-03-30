from rest_framework.permissions import BasePermission

TRANSFER_ALLOWED = True

# разрешение доступа для передачи yaml файла магазинов
class IsTransferAllowed(BasePermission):
    def has_permission(self, request, view):
        if TRANSFER_ALLOWED:
            return True
        else:
            return False

# разрешение на десвтия с заказами
# возвращает True, если действие совершает админ или пользователь, автор заказа
class IsOrderActionAllowed(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return request.user == obj.user

# разрешение на просмотр товаров доступно всем пользователям
# обработка товаров разрешена только админам
class IsProductActionAllowed(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        return request.user.is_staff


