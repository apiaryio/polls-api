from django.conf.urls import url
from polls.views import (RootResource, QuestionCollectionResource,
                         QuestionResource, ChoiceResource)


def error_view(request):
    raise Exception('Test exception')


urlpatterns = [
    url(r'^$', RootResource.as_view()),
    url(r'^questions$', QuestionCollectionResource.as_view()),
    url(r'^questions/(?P<pk>[\d]+)$', QuestionResource.as_view()),
    url(r'^questions/(?P<question_pk>[\d]+)/choices/(?P<pk>[\d]+)$', ChoiceResource.as_view()),
    url(r'^500/$', error_view),
]
