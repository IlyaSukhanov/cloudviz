"""
Provides view of cloudwatch metrics
"""

import logging
from pytz import utc
from datetime import datetime, timedelta
from collections import OrderedDict

from pyramid.response import Response
from iso8601 import parse_date
import gviz_api
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
        Evaluate data format to be passed in as description to gviz
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
    def drop_column(data, column_name):
        """
        Drop column from data returned by cloudwatch
        """
        for row in data:
            del(row[column_name])
        return data

    def get_points(self, namespace, dimensions, metric, period,
                   start_time, end_time, statistic, unit, tqx):
        """
        Return gviz friendly representation of cloudwatch data
        """
        unit = unit if unit != "None" else None
        results = self.connection.get_metric_statistics(
            period, start_time, end_time, metric,
            namespace, [statistic], dimensions, unit
        )

        data_format = Datapoints.extract_data_format(results[0])
        data = Datapoints.drop_column(results, u'Unit')

        data_table = gviz_api.DataTable(data_format)
        data_table.LoadData(data)
        return data_table.ToJSonResponse(
            columns_order=data_format.keys(),
            order_by=u'Timestamp',
            req_id=tqx['reqId']
        )

    def points(self, request):
        """
        Return gviz compatible data within specified parameters
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

        # tqx is documented here: http://goo.gl/BHMzVx
        tqx = dict(
            pair.split(":") for pair in request.params.get("tqx").split(";")
        )

        try:
            data = self.get_points(
                namespace, dimensions, metric, period,
                start_time, end_time, statistic, unit, tqx
            )
            return Response(body=data, content_type=JSON_TYPE)
        except:
            logging.exception("Failed to fetch points")
            return Response(
                "Failed to fetch data points".format(unit),
                status_code=500
            )
