import json
from collections import namedtuple

from django.views.generic import View
from django.http import HttpResponse
from django.core.paginator import Paginator

from negotiator import ContentType, ContentNegotiator, AcceptParameters


Attribute = namedtuple('Attribute', ('name', 'category'))
Action = namedtuple('Action', ('method', 'attributes'))


class SingleObjectMixin(object):
    model = None

    def get_object(self):
        if not getattr(self, 'obj', None):
            self.obj = self.model.objects.get(pk=self.kwargs['pk'])

        return self.obj


class Resource(View):
    uri = None

    def get_attributes(self):
        return {}

    def get_relations(self):
        """
        Returns a dictionary of relations, key must be a string and the value
        should be another resource or a list of resources.
        """
        return {}

    def can_embed(self, relation):
        """
        When this method returns `True` for a given relation, we will embed it in
        the response when applicable.
        """
        return True

    def get_actions(self):
        """
        Returns a dictionary of actions
        """
        return {}

    def get_uri(self):
        return self.uri

    def content_handlers(self):
        return {
            'application/json': to_json,
            'application/hal+json': to_hal,
            'application/vnd.siren+json': to_siren,
        }

    def get(self, request, *args, **kwargs):
        content_type = self.determine_content_type(request)
        handlers = self.content_handlers()
        handler = handlers[str(content_type)]
        response = HttpResponse(json.dumps(handler(self)), content_type)

        if str(content_type) == 'application/json':
            can_embed_relation = lambda relation: not self.can_embed(relation[0])
            relations = filter(can_embed_relation, self.get_relations().items())
            relation_to_link = lambda relation: '<{}>; rel="{}"'.format(relation[1].get_uri(), relation[0])
            links = map(relation_to_link, relations)
            if len(links) > 0:
                response['Link'] = ', '.join(links)

        return response

    def determine_content_type(self, request):
        acceptable = (
            AcceptParameters(ContentType('application/json')),
            AcceptParameters(ContentType('application/hal+json')),
            AcceptParameters(ContentType('application/vnd.siren+json')),
        )

        negotiator = ContentNegotiator(acceptable[0], acceptable)
        accept = request.META.get('HTTP_ACCEPT')
        negotiated_type = negotiator.negotiate(accept=request.META.get('HTTP_ACCEPT'))
        if negotiated_type:
            return negotiated_type.content_type

        return acceptable[0].content_type


class CollectionResource(Resource):
    model = None
    resource = None  # A resource class that inherits from SingleObjectMixin
    relation = 'objects'
    paginate_by = 20

    def __init__(self, page=None):
        self.page = page
        super(CollectionResource, self).__init__()

    def get_uri(self):
        if self.page is not None:
            return '{}?page={}'.format(self.uri, self.page)
        return self.uri

    def get_objects(self):
        return self.model.objects.all()

    def get_paginator(self):
        return Paginator(self.get_objects(), self.paginate_by)

    def get_resources(self, objects):
        def to_resource(obj):
            resource = self.resource()
            resource.obj = obj
            resource.request = self.request
            return resource

        return map(to_resource, objects)

    def get_relations(self):
        paginator = self.get_paginator()
        page = paginator.page(int(self.request.GET.get('page', 1)))
        objects = page.object_list
        relations = {
            self.relation: self.get_resources(page)
        }

        if page.has_next():
            relations['next'] = self.__class__(page.next_page_number())

        if page.has_previous():
            relations['prev'] = self.__class__(page.previous_page_number())

        if page.has_other_pages():
            relations['last'] = self.__class__(paginator.num_pages)

        return relations

    def content_handlers(self):
        """
        Override `content_handlers` to change JSON handler to return arrays
        """

        def json_handler(resource):
            relations = self.get_relations()
        handlers = super(CollectionResource, self).content_handlers()
        handlers['application/json'] = lambda resource: map(to_json, self.get_relations()[self.relation])
        return handlers

    def can_embed(self, relation):
        return relation not in ('next', 'prev', 'last')


def to_json(resource):
    document = resource.get_attributes()
    document['url'] = resource.get_uri()

    for relation, related_resource in resource.get_relations().items():
        if isinstance(related_resource, list):
            if resource.can_embed(relation):
                document[relation] = map(to_json, related_resource)
            else:
                document[relation] = map(lambda r: {'url': r.get_uri()},
                                         related_resource)
        else:
            if resource.can_embed(relation):
                document[relation] = to_json(related_resource)
            else:
                document['{}_url'.format(relation)] = related_resource.get_uri()

    return document


def to_hal(resource):
    document = resource.get_attributes()
    relations = resource.get_relations()

    embed = {}
    links = {}

    for relation in relations:
        related_resource = relations[relation]

        if resource.can_embed(relation) or isinstance(related_resource, list):
            if isinstance(related_resource, list):
                embed[relation] = map(to_hal, related_resource)
            else:
                embed[relation] = to_hal(related_resource)
        else:
            href = related_resource.get_uri()
            links[relation] = {'href': href}

    links['self'] = {'href': resource.get_uri()}

    document['_links'] = links
    if len(embed):
        document['_embed'] = embed

    return document


def to_siren_relation(relation):
    def inner(resource):
        document = to_siren(resource)
        document['rel'] = [relation]
        return document
    return inner


def to_siren(resource):
    def to_siren_link(relation):
        def inner(resource):
            return {'rel': [relation], 'href': resource.get_uri()}
        return inner

    document = {}

    attributes = resource.get_attributes()
    if len(attributes):
        document['properties'] = attributes

    links = []
    entities = []
    for relation, related_resource in resource.get_relations().items():
        if resource.can_embed(relation):
            if isinstance(related_resource, list):
                entities += map(to_siren_relation(relation), related_resource)
            else:
                entity = to_siren_relation(relation)(related_resource)
                entities.append(entity)
        else:
            if isinstance(related_resource, list):
                items = map(to_siren_link(relation), related_resource)
                links += items
            else:
                links.append(to_siren_link(relation)(related_resource))

    links.append(to_siren_link('self')(resource))
    document['links'] = links

    if len(entities):
        document['entities'] = entities

    actions = []

    for name, action in resource.get_actions().items():
        action_dict = {
            'name': name,
            'method': action.method,
            'href': resource.get_uri(),
            'type': 'application/json',
        }

        if action.attributes:
            def to_field(attribute):
                return {
                    'name': attribute.name,
                    'type': attribute.category,
                    'title': attribute.name.capitalize(),
                }
            action_dict['fields'] = map(to_field, action.attributes)

        actions.append(action_dict)

    if len(actions):
        document['actions'] = actions

    return document
