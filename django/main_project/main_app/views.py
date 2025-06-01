from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache


from .tasks import send_user_created_email
from main_app.serializers import GroupSerializer, UserSerializer


@method_decorator(cache_page(60 * 15), name='list')
@method_decorator(cache_page(60 * 15), name='retrieve')
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.delete("views.decorators.cache.cache_page./users/")
        if response.status_code == 201:
            user = response.data
            send_user_created_email.delay(user['email'], user['username'])
        return response


    def update(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        cache.delete(f"views.decorators.cache.cache_page./users/{user_id}/")
        cache.delete("views.decorators.cache.cache_page./users/")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        cache.delete(f"views.decorators.cache.cache_page./users/{user_id}/")
        cache.delete("views.decorators.cache.cache_page./users/")
        return super().destroy(request, *args, **kwargs)

@method_decorator(cache_page(60 * 15), name='list')
@method_decorator(cache_page(60 * 15), name='retrieve')
class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        cache.delete("views.decorators.cache.cache_page./groups/")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        group_id = kwargs.get("pk")
        cache.delete(f"views.decorators.cache.cache_page./groups/{group_id}/")
        cache.delete("views.decorators.cache.cache_page./groups/")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        group_id = kwargs.get("pk")
        cache.delete(f"views.decorators.cache.cache_page./groups/{group_id}/")
        cache.delete("views.decorators.cache.cache_page./groups/")
        return super().destroy(request, *args, **kwargs)