"""
Add cloudviz documentation here.
"""

import os.path

import pyramid
from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_whoauth.auth import WhoAuthenticationPolicy
from pyramid_beaker import set_cache_regions_from_settings
from repoze.who.config import make_api_factory_with_config

from .security import appauth, RootFactory
from .version import __version__, __rpm_version__, __git_hash__
from cloudviz.views import metrics
from cloudviz.views import datapoints


def add_service(config, url_pattern, view_callable,
                request_method='GET', **kwargs):
    """ Convenience function combining add_route and add_view
    """
    route_name = "route:%s:%s" % (url_pattern, request_method)
    config.add_route(route_name, url_pattern, request_method=request_method)
    config.add_view(view_callable, route_name=route_name, **kwargs)


def main(_global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # The next line creates a 'here' setting pointing to the directory
    # containing the repoze.who.ini file.
    # There should be a better way to do this.
    settings['here'] = os.path.dirname(settings['repoze.who.ini'])

    # Create the Pyramid config
    config = Configurator(settings=settings)
    set_cache_regions_from_settings(settings)

    # Authentication
    config.include("pyramid_whoauth")
    repoze_who_factory = make_api_factory_with_config(
        settings,
        settings['repoze.who.ini']
    )
    config.set_authentication_policy(
        WhoAuthenticationPolicy(repoze_who_factory, callback=appauth)
    )
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_root_factory(RootFactory)

    cw_metrics = metrics.Metrics()
    add_service(config, "metrics", cw_metrics.dimension_names, 'GET')
    add_service(
        config,
        "metrics/{dimension_name}",
        cw_metrics.dimension_values,
        'GET'
    )
    add_service(
        config,
        "metrics/{dimension_name}/{dimension_value}",
        cw_metrics.metrics,
        'GET'
    )

    cw_points = datapoints.Datapoints()
    add_service(
        config,
        "datapoints/{namespace}/{dimension_name}/{dimension_value}/{metric}",
        cw_points.points,
        'GET'
    )

    config.add_static_view('/', 'static', cache_max_age=3600)
    return config.make_wsgi_app()
