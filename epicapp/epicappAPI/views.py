from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# from django.http import JsonResponse
import jwt
import datetime

from .models import Author
from .serializers import AuthorSerializer


@api_view((['POST']))
def register(request):
    if request.method == 'POST':
        author = AuthorSerializer(data=request.data)

        if not author.is_valid():
            return Response(data=author.errors, status=status.HTTP_400_BAD_REQUEST)

        author.save()

        return Response(author.data)


@api_view((['POST']))
def authenticate(request):
    if request.method == 'POST':
        # get first author with username
        author = Author.objects.filter(
            displayName=request.data["displayName"]).first()

        # no user with that display name
        if author is None:
            return Response(data="Author not found!", status=status.HTTP_401_UNAUTHORIZED)

        # if hash passwords aren't the same
        if not author.check_password(request.data["password"]):
            return Response(data="Invalid credentials!", status=status.HTTP_401_UNAUTHORIZED)

        # create token with 60 min expiry
        token = jwt.encode(
            {
                'id': AuthorSerializer(author).data['id'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                'iat': datetime.datetime.utcnow()
            }, "SECRET_NOT_USING_ENV_CAUSE_WHO_CARES", algorithm='HS256')

        # return an http only cookie, but if needed to make it easier, we can not do http only cookies so JS can use it.
        response = Response(data="Login successful!",
                            status=status.HTTP_200_OK)
        response.set_cookie(key='token', value=token, httponly=True)
        return response


@api_view((['POST']))
def logout(request):
    if request.method == 'POST':
        response = Response(data="Logout successful!",
                            status=status.HTTP_200_OK)
        response.delete_cookie('token')
        return response


@api_view(['GET'])
def get_author_details(request):
    if request.method == 'GET':
        token = request.COOKIES.get('token')

        if not token:
            return Response(data="Unauthenticated!", status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(
                token, 'SECRET_NOT_USING_ENV_CAUSE_WHO_CARES', algorithms=['HS256'])
            print(payload)
            author = Author.objects.filter(id=payload['id']).first()
            return Response(data=AuthorSerializer(author).data, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response(data="Token expired!", status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_author(request, id):
    return Response(data="get single author")


@api_view(['GET'])
def get_authors(request):
    return Response(data="get many authors")
