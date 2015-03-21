import re
from django.conf.urls import patterns, include, url
from polls.views import (RootResource, QuestionCollectionResource,
                         QuestionResource, ChoiceResource)


EXTRACT_VARIABLE_REGEX = re.compile(r'\{([\w]+)\}')

def as_pattern(uri_template):
    escaped_uri_template = re.escape(uri_template[1:]).replace('\{', '{').replace('\}', '}')

    def replace(match):
        return '(?P<{}>[\d]+)'.format(match.group(1))

    pattern = '^{}$'.format(re.sub(EXTRACT_VARIABLE_REGEX, replace, escaped_uri_template))
    return pattern


def urlpattern(resource):
    return url(as_pattern(resource.uri), resource.as_view())


urlpatterns = patterns('',
    urlpattern(RootResource),
    urlpattern(QuestionCollectionResource),
    urlpattern(QuestionResource),
    urlpattern(ChoiceResource),
)

