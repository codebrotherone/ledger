"""
Simple config file used to validate the features and metrics that
are allowed to be used for querying the insurance policy API.

Note:
    Ideally, a better method would be to implement middleware
    such as Marshmellow which would validate all data requests
    sent to the API. However, due to time constraints, I am using
    a simple module level config to run checks.

Database (sqlite3)
    Table
        policies
    File
        auto_insurance.db

Schema:
    - year
    - month
    - driver_age
    - driver_gender
    - driver_employment
    - driver_marital
    - driver_location
    - vehicle_age
    - vehicle_model
    - insurance_premium
    - insurance_claims
    - insurance_losses

"""
# Filters to use for Year and Month
CAT_FEATURES = [
    'driver_gender',
    'driver_employment',
    'driver_marital',
    'driver_location'
]
# Features are prefixed by driver_
NUM_FEATURES = [
    'year',
    'month',
    'driver_age',
    'vehicle_age',
    'vehicle_model',
    'year',
    'month',
    'insurance_premium',
    'insurance_claims',
    'insurance_losses'
]
# Metrics are prefixed by insurance
METRICS = [
    'insurance_premium',
    'insurance_claims',
    'insurance_losses'
]

# FILTER FEATS can be of any type
FILTER_FEATS = NUM_FEATURES + METRICS + CAT_FEATURES
