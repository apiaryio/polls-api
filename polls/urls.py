from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.urls import path

from polls.views import (
    ChoiceResource,
    QuestionCollectionResource,
    QuestionResource,
    RootResource,
)


def healthcheck_view(request):
    content_type = 'application/health+json'
    database_accessible = True

    try:
        connections['default'].cursor()
    except ImproperlyConfigured:
        # Database is not configured (DATABASE_URL may not be set)
        database_accessible = False
    except OperationalError:
        # Database is not accessible
        database_accessible = False

    if database_accessible:
        return JsonResponse({'status': 'ok'}, content_type=content_type)

    return JsonResponse({'status': 'fail'}, status=503, content_type=content_type)


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
