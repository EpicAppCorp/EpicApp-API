from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .serializers import QuestionSerializer

@api_view((['POST']))
def create_author(request): 
    return Response(data="create author")

@api_view(['GET'])
def get_author(request, id):
    return Response(data="get single author")

@api_view(['GET'])
def get_authors(request):
    return Response(data="get many authors")
