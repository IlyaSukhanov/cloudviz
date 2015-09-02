"""
Provides view of cloudwatch metric data
"""

import logging
from pytz import utc
from datetime import datetime, timedelta
from collections import OrderedDict
import simplejson as json

from pyramid.response import Response
from iso8601 import parse_date
from boto.ec2.cloudwatch import CloudWatchConnection

JSON_TYPE = 'application/json'
DEFAULT_PERIOD = 60
DEFAULT_STATISTIC = 'Average'
DEFAULT_UNIT = 'None'

AWS_STATISTICS = ['Average', 'Sum', 'SampleCount', 'Maximum', 'Minimum']
AWS_UNITS = [
    'None', 'Seconds', 'Microseconds', 'Milliseconds', 'Bytes', 'Kilobytes',
    'Megabytes', 'Gigabytes', 'Terabytes', 'Bits', 'Kilobits', 'Megabits',
    'Gigabits', 'Terabits', 'Percent', 'Count', 'Bytes/Second',
    'Kilobytes/Second', 'Megabytes/Second', 'Gigabytes/Second',
    'Terabytes/Second', 'Bits/Second', 'Kilobits/Second', 'Megabits/Second',
    'Gigabits/Second', 'Terabits/Second', 'Count/Second',
]


class Datapoints(object):
    """
    Provides view of cloudwatch metrics
    """

    def __init__(self, connection=None):
        self._connection = connection

    @property
    def connection(self):
        """
        Lazy cloudwatch connection object
        """
        if not self._connection:
            self._connection = CloudWatchConnection()
        return self._connection

    @staticmethod
    def extract_data_format(sample_row):
        """
        Return dict describing what type of fields we have and what units they are.
        """
        data_format = OrderedDict()
        data_format["Timestamp"] = ("datetime", "Time")
        for statistic in AWS_STATISTICS:
            if statistic in sample_row:
                if statistic == "SampleCount":
                    label = statistic
                else:
                    label = "{0} {1}".format(statistic, sample_row["Unit"])
                data_format[statistic] = ("number", label)
        return data_format

    @staticmethod
    def date_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    def get_points(self, namespace, dimensions, metric, period,
                   start_time, end_time, statistic, unit):
        """
        Return nvd3 friendly representation of cloudwatch data
        looks something like:
        [
         {
           "key":"Series name"
           "units":"Unit"
           "values":[ {"x":x0, "y":y0}, {"x":x1, "y":y1} ... ]
         }, {
           "key":"Another series"
           ...
         }
        ]
        """
        unit = unit if unit != "None" else None
        records = self.connection.get_metric_statistics(
            period, start_time, end_time, metric,
            namespace, [statistic], dimensions, unit
        )
        if len(records) > 0:
            data_format = Datapoints.extract_data_format(records[0])
            record_units = data_format[statistic][1]
            data_values = [
                {"x":record[u'Timestamp'], "y":record[statistic]}
                for record in sorted(records, key=lambda k: k[u'Timestamp'])
            ]
        else:
            record_units = None
            data_values = []
        return {
            "key":".".join([namespace, dimensions.values()[0], metric]),
            "units": record_units,
            "statistic":statistic,
            "values":data_values,
        }

    def points(self, request):
        """
        Return d3 compatible data within specified parameters
        """
        namespace = request.matchdict.get("namespace")
        namespace = namespace.replace("~", "/")
        dimension_name = request.matchdict.get("dimension_name")
        dimension_value = request.matchdict.get("dimension_value")
        dimensions = {dimension_name: dimension_value}
        metric = request.matchdict.get("metric")

        try:
            period = request.params.get("period", DEFAULT_PERIOD)
        except ValueError:
            return Response(
                "Period ({0}) must be integer value.".format(period),
                status_code=400
            )

        end_time = request.params.get("end_time")
        if end_time:
            end_time = parse_date(end_time)
        else:
            end_time = datetime.now(utc)

        start_time = request.params.get("start_time")
        if start_time:
            start_time = parse_date(start_time)
        else:
            start_time = end_time+timedelta(hours=-1)

        statistic = request.params.get("statistic", AWS_STATISTICS[0])
        if statistic not in AWS_STATISTICS:
            return Response(
                "Not valid statistic parameter {0}".format(statistic),
                status_code=400
            )
        unit = request.params.get("unit", AWS_UNITS[0])
        if unit not in AWS_UNITS:
            return Response(
                "Not valid unit parameter {0}".format(unit),
                status_code=400
            )

        try:
            series_data = self.get_points(
                namespace, dimensions, metric, period,
                start_time, end_time, statistic, unit
            )
        except:
            logging.exception("Failed to fetch points")
            return Response(
                "Failed to fetch data points".format(unit),
                status_code=500
            )
        data= [series_data]
        json_data = json.dumps(data, default=Datapoints.date_serializer)
        logging.debug(json_data)
        return Response(body=json_data, content_type=JSON_TYPE)
