"""
Simple APIs for interacting with sqlite3

● Give me the <metric_name1>,<metric_name2> by specific <feature_name> where
    <feature_name> is <feature_value>
● Allow me to filter policy records with certain values for <metric_name>,
    <feature_name>
● Show me metrics for policies than belong to certain feature clusters.

Definitions:
General:
    Feature: is an attribute of an insurance policy
    Metric: can be a count or amount
Commonly requested calculated metrics:
    Severity: == sum_of_losses(feature) / total_claims_count(feature)
    Frequency: == total_claims_count(feature) / policy_count(feature)
    Loss ratio: == sum_of_losses(feature) / sum_of_premium(feature)



"""
import falcon
import json
from insurance.sqlite_conn import SQLiteConnection

from insurance.config import *


# class FilterResource:
#     """
#     Simple API Resource defined for returning query responses from the Sqlite3
#     db containing insurance policy data.
#     Given a filter_feat and filter_val url params.
#     http get "localhost:8000/policies/query/count?filter_feat=age_vehicle&
#     feat_val=10"
#     """
#
#     def on_get(self, req, resp):
#         """Handles GET requests, where req represents a query"""
#         params = req.params
#         # for k, v in params.items():
#         #     if k not in FILTER_FEATS:
#         #         raise falcon.HTTPBadRequest(
#         #             title="400 Bad Request",
#         #             description="Filter field {} is not available in the db "
#         #                         "schema Please check the query params: "
#         #                         "{} ".format(k, req.query_string),
#         #             code=400
#         #         )
#         #     else:
#         #         continue
#         #
#         filter_feat, filter_val = None, None
#         if req.get_param('filter_feat'):
#             filter_feat = req.params['filter_feat']
#         if req.get_param('filter_val'):
#             filter_val = req.params['filter_val']
#
#         if not all([filter_feat, filter_val]):
#             raise falcon.HTTPBadRequest(
#                 title="400 Bad Request",
#                 description="Filter field {} is not available in the db "
#                             "schema Please check the query params: "
#                             "{} ".format(k, req.query_string),
#                 code=400
#             )
#         else:
#
#
#         resp.body = json.dumps({
#             "qs": req.query_string,
#             "params": req.params,
#         })


class MetricsResource:
    """
    Simple class defined for returning query responses from Sqlite3
    which will contain data regarding insurance policies.

    The aggregated data returned will have the following structure:

    http get "localhost:8000/policies/query/count?metrics=[sum, count]
    &by=feats&feat=total_claims&feature_value=2"

    """

    def on_get(self, req, resp):
        """
        Handles GET requests, where req represents a query that requires
        metrics and feature parameters.

        For example grabbing the loss_ratio (sum losses / sum premiums)

        """
        metrics = None
        q = tuple()
        #
        # Extract operations (metrics can be either count or sum)
        #
        if req.get_param("metrics"):
            metrics = req.params['metrics'].split(",")
            print(metrics)
            if len(metrics) > 1:
                # strip values from
                metrics = [m.replace('[', '').replace("]", '') for m in metrics]
                # simple data validation
                for m in metrics:
                    if m not in ['count', 'sum']:
                        raise falcon.HTTPBadRequest(
                            title="400 Bad Request",
                            description="metric value can only be one or both "
                                        "values from [count, sum]. Please Check"
                                        " the query params: {}".format(
                                            req.query_string
                                        ),
                            code=400
                        )

        # Extract the fields that metrics must be calculated for
        if req.get_param("for"):
            metric_feat = req.params['for']
            if metric_feat not in NUM_FEATURES:
                raise falcon.HTTPBadRequest(
                    title="400 Bad Request",
                    description="The query parameter: for does not map to an "
                                "available numerical feature/field in the db."
                                " Please Check the query params: "
                                "{}".format(req.query_string),
                    code=400
                )
        else:
            metric_feat = ''

        if req.get_param("by"):
            by_feat = req.params['by']
            if by_feat not in NUM_FEATURES:
                raise falcon.HTTPBadRequest(
                    title="400 Bad Request",
                    description="By query parameter must be a numerical field "
                                "that exists in the policies database. "
                                "Please Check the query params: {}".format(
                                    req.query_string),
                    code=400
                )
        else:
            by_feat = None

        # Extract where statement
        if req.get_param("filter_feat"):
            where_feat = req.params['filter_feat']
            if where_feat not in FILTER_FEATS or not req.get_param(
                    "filter_val"):
                raise falcon.HTTPBadRequest(
                    title="400 Bad Request",
                    description="If feature name filter is passed, then a value"
                                "must also be passed with it. Please Check the "
                                "query params: {}".format(req.query_string),
                    code=400
                )
            feat_value = req.get_param("filter_val")
        else:
            where_feat, feat_value = '', ''

        # assemble query
        select_query, where_query = [], []

        if by_feat:
            for m in metrics:
                if m == 'count':
                    select_query += ['{}({}) as {}_{}'.format(
                        m, metric_feat, metric_feat, 'count')
                    ]
                else:
                    select_query += [
                        "{}({})/{}({}) as {}_by_{}_{} ".format(
                        m, metric_feat, m, by_feat, metric_feat, by_feat, m)
                    ]

        else:
            select_query = ["{}({}) as {}_{} ".format(m, metric_feat,
                                                      m, metric_feat) for m in
                            metrics]
        # join select query statement
        select_query = ', '.join(select_query)

        # build where statement
        if where_feat and feat_value:
            if feat_value in CAT_FEATURES:
                # need to wrap strings
                feat_value = '`{}`'.format(feat_value)

            where_query += F" WHERE {where_feat}='{feat_value}'"

        # assemble final query
        q = F"""SELECT {select_query} FROM policies {where_query}"""
        print(F"Final query is {q}")

        if not all([metrics, metric_feat]):
            print(F"Calculating {metrics}, for {metric_feat}")
            raise falcon.HTTPBadRequest(
                title="400 Bad Request",
                description="Request must include query parameters: [metrics, "
                            "for] More than one metric may be passed, "
                            "but only one for query is accepted. Please Check "
                            "the query params: {}".format(req.query_string),

                code=400,
            )
        else:
            # query db with final query
            # Construct db conn
            db = SQLiteConnection()
            cursor = db.conn.cursor()
            cursor.execute(q)
            rows = cursor.fetchall()
            desc = [i for c in cursor.description for i in c if i]
            resp.body = json.dumps({
                "qs": req.query_string,
                "data": {desc[i]: r[i] for r in rows for i, m in
                         enumerate(r)},
            })
