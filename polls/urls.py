from django.urls import path
from django.http import JsonResponse
from polls.views import (RootResource, QuestionCollectionResource,
                         QuestionResource, ChoiceResource)


def healthcheck_view(request):
    return JsonResponse({ 'status': 'ok' }, content_type='application/health+json')


def error_view(request):
    raise Exception('Test exception')


urlpatterns = [
    path('', RootResource.as_view()),
    path('questions', QuestionCollectionResource.as_view()),
    path('questions/<int:pk>', QuestionResource.as_view()),
    path('questions/<int:question_pk>/choices/<int:pk>', ChoiceResource.as_view()),
    path('healthcheck', healthcheck_view),
    path('500', error_view),
]
