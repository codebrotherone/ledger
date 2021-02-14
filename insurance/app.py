"""
Simple app.py file used for Falcon to register different resources and
endpoints. This file will define routes for each endpoint.
"""

from insurance.query import *

# setup wsgi, so unicorn can recognize it
api = application = falcon.API()

# attach query resource to the api
metrics = MetricsResource()

# add the query/metrics endpoint to the api
api.add_route('/policies/query/metrics', metrics)
