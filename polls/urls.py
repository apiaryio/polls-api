from django.conf.urls import patterns, include, url
from polls.views import (RootResource, QuestionCollectionResource,
                         QuestionResource, ReportQuestionResource,
                         ChoiceResource)


urlpatterns = patterns('',
    url(r'^$', RootResource.as_view()),
    url(r'^questions$', QuestionCollectionResource.as_view()),
    url(r'^questions/(?P<pk>[\d]+)$', QuestionResource.as_view()),
    url(r'^questions/(?P<pk>[\d]+)/report$', ReportQuestionResource.as_view()),
    url(r'^questions/(?P<question_pk>[\d]+)/choices/(?P<pk>[\d]+)$', ChoiceResource.as_view()),
)
