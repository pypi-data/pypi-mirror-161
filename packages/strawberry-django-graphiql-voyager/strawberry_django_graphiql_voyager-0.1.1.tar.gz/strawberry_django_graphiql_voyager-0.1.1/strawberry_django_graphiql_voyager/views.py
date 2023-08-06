import os
import json
import strawberry
from django.conf import settings
from django.shortcuts import render
from django.http import Http404, HttpRequest
from django.template import RequestContext, Template
from django.template.loader import render_to_string
from django.template.exceptions import TemplateDoesNotExist
from django.template.response import TemplateResponse
from django.views.generic import TemplateView as GenericTemplateView
from strawberry.django.views import AsyncGraphQLView as GraphQLView


class AsyncGraphQLView(GraphQLView):
    graphiql_html_file = "strawberry_django_graphiql_voyager/graphiql.html"

    def _render_graphiql(self, request: HttpRequest, context=None):
        if not self.graphiql:
            raise Http404()
        template1 = Template(render_to_string(self.graphiql_html_file))
        try:
            template = Template(render_to_string(self.graphiql_html_file))
        except TemplateDoesNotExist:
            template = Template(
                open(
                    os.path.join(
                        os.path.dirname(os.path.abspath(strawberry.__file__)),
                        "static/graphiql.html",
                    ),
                    "r",
                ).read()
            )

        context = context or {}
        context.update(
            {"SUBSCRIPTION_ENABLED": json.dumps(self.subscriptions_enabled)})

        response = TemplateResponse(
            request=request, template=None, context=context)
        response.content = template.render(RequestContext(request, context))

        return response


class TemplateView(GenericTemplateView):
    template_name = "strawberry_django_graphiql_voyager/voyager.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        graphql_endpoint = settings.GRAPHENE_VOYAGER['GRAPHQL_ENDPOINT']
        context['graphql_endpoint'] = graphql_endpoint
        return context
