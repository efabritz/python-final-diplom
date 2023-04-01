from django.core.exceptions import ObjectDoesNotExist

from .models import User

# класс для пользовательского login
class CustomAuthBackend():
    def authenticate(self, request, email, password):
        try:
            user = User.objects.get(email=email)
            success = user.check_password(password)
            if success:
                return user
        except ObjectDoesNotExist:
            pass
        return None


    def get_user(self, uid):
        try:
            return User.objects.get(id=uid)
        except:
            return None