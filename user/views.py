from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from user.serializer import UserSerializer, AuthTokenSerializer

from app01 import models
from app01.authentication import token_expire_handler, \
    ExpiringTokenAuthentication
# Create your views here.
class CreateUserView(generics.CreateAPIView):
    serializer_class=UserSerializer

class ManageUserView(generics.RetrieveAPIView):
    serializer_class=UserSerializer
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes=(permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class ListUserView(generics.ListAPIView):
    serializer_class=UserSerializer
    queryset=models.User.objects.all()
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        is_expired, token, token_expired_timestamp = token_expire_handler(
            token)
        return Response({
            'user_id': user.id,
            'token': token.key,
            'token_expired_timestamp': token_expired_timestamp})
