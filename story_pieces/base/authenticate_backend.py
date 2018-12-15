from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()

class MyModelBackend(ModelBackend):
    """
    similar with ModelBackend but differ from user existence.
    """

    def authenticate(self, request, username=None, password=None, differ=None, **kwargs):
        try:
            user = UserModel._default_manager.get(mobile=username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
            if differ is not None:
                differ['exist'] = False
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user