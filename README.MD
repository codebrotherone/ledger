# LEDGER TAKE HOME 
This project will take insurance policy data for automobiles and create a simple
RESTFUL API that will respond to certain queries for metrics and features. 

## Project Structure
```bash
├── README.MD
├── data
│   ├── auto_insurance.db        #  Sqlite Database containing data
│   └── auto_policies.csv        #  Original source file for data
├── dist                         # Wheel file for manual installation 
│   └── example_pkg_jae_han-0.0.1-py3-none-any.whl   
├── docs                         # original documentation for assignment
│   └── Software\ Engineer\ Case\ Study.pdf
├── insurance                    # project directory storing app/api files
│   ├── __init__.py 
│   ├── app.py                   # application script that falcon uses to register endpoings
│   ├── config.py                # configuration file for the api
│   ├── query.py                 # resource file for the falcon api 
│   ├── query_builder.py         # [incomplete] class for structuring queries
│   └── sqlite_conn.py           # class for providing a sqlite connection
├── notebooks
│   ├── auto_policy_dive.html    # Example Facets Dive Visualization
│   └── insurance_eda.ipynb      # Exploratory data analysis of the data.
├── requirements.txt             # requirements file
└── setup.py                     # setup.py for built and src distros
```

## Project Setup
This project has a provided python wheel file under the `dist/` repository, 
as well as a requirements.txt file and a conda environment file. 

Major dependencies include falcon, gunicorn, httpie, with a complete list found
in the conda `environment.yml` or `requirements.txt` file. 

A SQLite database was used to store the insurance data - and a file has already 
been preloaded with this information under `data/auto_insurance.db`. 

#### Notes
Since the dataset was not too large, a `sqlite` backend was used to store the 
data, while `falcon` was as the web framework for building the API. `gunicorn`
was leveraged as a WSGI, while `httpie` was used to test the API calls. 

The idea was to use lightweight frameworks that were fast to deploy, 
while providing flexibility in terms of design and setup. 

#### Author's Notes
I wanted to mention some drawbacks associated with sqlite as it does not
support advanced dynamic querying. 
There are also security issues with SQL injection attacks outside fo using `?` 
to for binding arguments to queries. 
In retrospect, I would have chosen a different backend and also implemented
middleware for the request body validation so that I could check requests
for form and data (Marshmallow is a good choice). 
However, due to time constraints I was not able to implement this functionality. 


## Installation
#### Installing Dependencies
1. Install via pip
```bash
pip install -r requirements.txt
```
2. Install via conda
```bash
conda env create -f environment.yml
```
3. Install from wheel
```bash
pip install dist/example_pkg_jae_han-0.0.1-py3-none-any.whl
```

To generate a wheel file:
```python
python setup.py bdist_wheel
```
#### Starting the API Service
1. Start gunicorn (--reload flag is optional)
```bash
gunicorn --reload insurance.app
```
2. Run queries via `httpie`

## Usage
##### Example of obtaining count for drivers who are 21
```bash
http "localhost:8000/policies/query/metrics?metrics=count&for=driver_age&filter_feat=driver_age&filter_val=21"
```
Output
```bash
{
    "data": {
        "count": 4783
    },
    "qs": "metrics=count&for=driver_age&filter_feat=driver_age&filter_val=21"
}
```
##### Example of obtaining loss ratio
```bash
http "localhost:8000/policies/query/metrics?metrics=sum,count&for=insurance_losses&by=insurance_premium&filter_feat=driver_age&filter_val=21"
```
Output
```bash
HTTP/1.1 200 OK
Connection: close
Date: Sun, 14 Feb 2021 17:55:12 GMT
Server: gunicorn/20.0.4
content-length: 175
content-type: application/json

{
    "data": {
        "insurance_losses_by_insurance_premium_sum": 0.7631478929903907
    },
    "qs": "metrics=sum&for=insurance_losses&by=insurance_premium&filter_feat=driver_age&filter_val=21"
}
```

## API Endpoints and Query Parameters
Endpoints

    - policies/query/metrics

Query Parameters

*Note: Only the `=` operator is available via the `filter_val` query parameter.*

    metrics - query metrics, one of ['count', 'sum']
    for - the feature you want to run the metric against
    by - the feature you want to divide against for the `sum` metric.
    filter_feat - the feature you want to filter against (i.e. vehicle_age).
    filter_val - the value you want the feature to be filtered against. 

## Final Notes
There were a few things I would have liked to change, but could not due to time
constraints. First and foremost, would be to choose a better backend that can
support a model based approach to *dynamically querying* a table based on
inputs parsed from API Requests.

*Other API Design Concerns*
Another issue is that the `for` and `by` query parameters do not
work for metrics such as severity, but do work for metrics such as loss ratio.

This is because the query to the db (in the query api) does not build the queries
in a way where the metrics for the numerator and denominator are distinct. Rather,
if a `sum` query parameter is detected in the url request, then it will sum the
for and by fields - while a `count` query parameter will simply count the `for`
features. 

A better design would be to have the API with endpoints:
- `policies/query/count?filter_feat={}&filter_val={}&filter_op={}`
    - simple api endpoint to query counts with optional query parameters to 
    allow for filtering records based on comparison operators (<, >, = etc..)

- `policies/query/sum?filter_feat={}&filter_val={}&filter_op={}`
    - simple api endpoint to query sums with optional query parameters to 
    allow for filtering records based on comparison operators (<, >, = etc..)
      
- `policies/query`
    - used to query the policy database with simple selects and filters (where 
    statements).
      
- policies/query/metrics
    - query_params
        - `for_metric`: count, or sum. Required
        - `by_metric`: count, or sum. Required
        - `for_feature`: feature to run against the `for_metric`
        - `by_feature`: feature to run against the `for_metric`
        - `filter_feat`: Name of the feature to filter against
        - `filter_op`: Type of operation for the filter to use. 
          i.e. vehicle_age < 10
          
An API that separates endpoints into logically separate operations is a much better
approach, and would have been what I wanted to accomplish had I not spent so much time
fighting against the querying capabilities of sqlite :(

*Additionally, I would have liked to implement*:
1. Added support for handling all boolean comparisons on the features themselves. 
2. Custom exception handling to avoid having to repeat code when raising issues. 
3. Query Builder that would consolidate all query syntax formatting and building 
to one class file.
4. More robust db connection handling - perhaps a metaclass or a module that can 
   manage a pool of connections without having to re-instantiate them. In this case,
   I used a module class that will instantiate one connection each time it is called. 
   
