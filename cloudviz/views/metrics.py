"""
Query available cloudwatch metric names
"""

from collections import defaultdict

from pyramid.response import Response
from beaker.cache import cache_region
import simplejson as json

from boto.ec2.cloudwatch import CloudWatchConnection

JSON_TYPE = 'application/json'


class Metrics(object):
    """
    Query available cloudwatch metric names
    """

    def __init__(self, connection=None):
        self._connection = connection

    @property
    def connection(self):
        """
        lazy cloudwatch connection object
        """
        if not self._connection:
            self._connection = CloudWatchConnection()
        return self._connection

    def _get_metric(self, *args, **kwargs):
        """
        Yield one metric at a time until all are exhausted or
        the apocalypse is upon us
        """
        print("getting data")
        next_token = None
        while True:
            metrics = self.connection.list_metrics(
                *args, next_token=next_token, **kwargs
            )
            for metric in metrics:
                yield metric
            next_token = metrics.next_token
            if not next_token:
                break

    @cache_region('long_term')
    def get_metrics(self):
        """ Cached list of all available metrics """
        return [metric for metric in self._get_metric()]

    @cache_region('long_term')
    def _dimensions(self):
        """ Return all dimensions name/value pairs """
        dimension_set = defaultdict(set)
        for metric in self.get_metrics():
            for dname, dvalue in metric.dimensions.iteritems():
                dimension_set[dname].update(dvalue)

        dimension_list = {}
        for dname, dvalues in dimension_set.iteritems():
            dimension_list[dname] = list(dvalues)
        return dimension_list

    # TODO break here into model /\ and view \/

    def dimension_names(self, request):
        """ JSON representation of all dimension names """
        data = {"dimension_names": self._dimensions().keys()}
        return Response(
            body=json.dumps(data, indent=2),
            content_type=JSON_TYPE
        )

    def dimension_values(self, request):
        """ JSON representation of all dimension values for particular name """
        dimension_name = request.matchdict.get("dimension_name")
        if not dimension_name:
            return Response("dimension_name unknown", status_code=500)
        dimensions = self._dimensions()
        if dimension_name not in dimensions:
            return Response(
                "dimension_name ${0} not found".format(dimension_name),
                status_code=400
            )

        data = {
            "dimension_name": dimension_name,
            "dimension_values": dimensions[dimension_name]
        }
        return Response(
            body=json.dumps(data, indent=2),
            content_type=JSON_TYPE
        )

    def metrics(self, request):
        """
        Handle metrics request and generate appropriate restful reply
        """
        dimension_name = request.matchdict.get("dimension_name")
        dimension_value = request.matchdict.get("dimension_value")
        if not dimension_name or not dimension_value:
            return Response(
                "dimension_name / dimension_value unknown",
                status_code=500
            )
        metrics = [
            {"name": metric.name, "namespace": metric.namespace}
            for metric in self.get_metrics()
            if dimension_name in metric.dimensions
            and dimension_value in metric.dimensions[dimension_name]
        ]
        data = {
            "dimension_name": dimension_name,
            "dimension_value": dimension_value,
            "metrics": metrics
        }
        return Response(
            body=json.dumps(data, indent=2),
            content_type=JSON_TYPE
        )
