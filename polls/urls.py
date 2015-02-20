from rivr import Router
from polls.views import RootView, QuestionListView, QuestionDetailView, ChoiceDetailView


router = Router(
    (r'^$', RootView.as_view()),
    (r'^questions$', QuestionListView.as_view()),
    (r'^questions/(?P<pk>[\d]+)$', QuestionDetailView.as_view()),
    (r'^questions/(?P<question_pk>[\d]+)/choices/(?P<pk>[\d]+)$', ChoiceDetailView.as_view()),
)

