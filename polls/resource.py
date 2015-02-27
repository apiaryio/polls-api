import json

from django.views.generic import View
from django.http import HttpResponse

from negotiator import ContentType, ContentNegotiator, AcceptParameters


class SingleObjectMixin(object):
    model = None

    def get_object(self):
        if hasattr(self, 'obj'):
            return self.obj

        return self.model.objects.get(pk=self.kwargs['pk'])


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

    def get_uri(self):
        return self.uri

    def content_handlers(self):
        return {
            'application/json': to_json,
            'application/hal+json': to_hal,
        }

    def get(self, request, *args, **kwargs):
        content_type = self.determine_content_type(request)
        handlers = self.content_handlers()
        handler = handlers[str(content_type)]
        return HttpResponse(json.dumps(handler(self)), content_type)

    def determine_content_type(self, request):
        acceptable = (
            AcceptParameters(ContentType('application/json')),
            AcceptParameters(ContentType('application/hal+json')),
        )

        negotiator = ContentNegotiator(acceptable[0], acceptable)
        accept = request.META.get('HTTP_ACCEPT')
        negotiated_type = negotiator.negotiate(accept=request.META.get('HTTP_ACCEPT'))
        if negotiated_type:
            return negotiated_type.content_type

        return acceptable[0].content_type


class CollectionResource(Resource):
    model = None
    resource = None
    relation = 'objects'

    def get_objects(self):
        return self.model.objects.all()

    def get_resources(self):
        def to_resource(model):
            resource = self.resource()
            resource.obj = model
            return resource

        return map(to_resource, self.get_objects())

    def get_relations(self):
        return {
            self.relation: self.get_resources()
        }

    def content_handlers(self):
        """
        Override `content_handlers` to change JSON handler to return arrays
        """
        handlers = super(CollectionResource, self).content_handlers()
        handlers['application/json'] = lambda resource: map(to_json, resource.get_resources())
        return handlers


def to_json(resource):
    document = resource.get_attributes()
    document['url'] = resource.get_uri()

    for relation, related_resource in resource.get_relations().items():
        if isinstance(related_resource, list):
            if resource.can_embed(relation):
                document[relation] = map(to_json, related_resource)
            else:
                document[relation] = map(lambda r: { 'url': r.get_uri() },
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
            links[relation] = { 'href': href }

    links['self'] = resource.get_uri()

    document['_links'] = links
    if len(embed):
        document['_embed'] = embed

    return document

