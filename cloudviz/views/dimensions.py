from collections import defaultdict

from pyramid.response import Response
from beaker.cache import cache_region
import simplejson as json

from boto.ec2.cloudwatch import CloudWatchConnection

JSON_TYPE = 'application/json'


class Dimensions(object):

    def __init__(self, connection=None):
        self.connection = connection or CloudWatchConnection()

    def _list_metrics(self, *args, **kwargs):
        """
        Yield one metric at a time until all are exhausted or
        the apocalypse is upon us
        """
        next_token = None
        while True:
            metrics = self.connection.list_metrics(*args, next_token=next_token, **kwargs)
            for metric in metrics:
                yield metric
            next_token = metrics.next_token
            if not next_token:
                break

    @cache_region('long_term')
    def fetch(self):
        """ Return all dimensions and their instances """
        dimension_set = defaultdict(set)
        for metric in self._list_metrics():
            for dname, dvalue in metric.dimensions.iteritems():
                dimension_set[dname].update(dvalue)

        dimension_list = {}
        for dname, dvalues in dimension_set.iteritems():
            dimension_list[dname] = list(dvalues)
        return dimension_list


    def view(self, request):
        """ JSON representation of all dimensions """
        data = self.fetch()
        return Response(body=json.dumps(data, indent=2), content_type=JSON_TYPE)
