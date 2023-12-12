'''
Goal of Flask Microservice:
1. Flask will take the repository_name such as angular, angular-cli, material-design, D3 from the body of the api sent from React app and 
   will utilize the GitHub API to fetch the created and closed issues. Additionally, it will also fetch the author_name and other 
   information for the created and closed issues.
2. It will use group_by to group the data (created and closed issues) by month and will return the grouped data to client (i.e. React app).
3. It will then use the data obtained from the GitHub API (i.e Repository information from GitHub) and pass it as a input request in the 
   POST body to LSTM microservice to predict and forecast the data.
4. The response obtained from LSTM microservice is also return back to client (i.e. React app).

Use Python/GitHub API to retrieve Issues/Repos information of the past 1 year for the following repositories:
- https: // github.com/angular/angular
- https: // github.com/angular/material
- https: // github.com/angular/angular-cli
- https: // github.com/d3/d3
'''
# Import all the required packages 
import os
from flask import Flask, jsonify, request, make_response, Response,  url_for
from flask_cors import CORS
import json
import dateutil.relativedelta
from dateutil import *
from datetime import date
import pandas as pd
import requests
import logging

# Initilize flask app
app = Flask(__name__)
# Handles CORS (cross-origin resource sharing)
CORS(app)

# Add response headers to accept all types of  requests
def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response

# Modify response headers when returning to the origin
def build_actual_response(response):
    response.headers.set("Access-Control-Allow-Origin", "*")
    response.headers.set("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response

'''
API route path is  "/api/forecast"
This API will accept only POST request
'''
@app.route('/api/github', methods=['POST'])
def github():
    body = request.get_json()
    # Extract the choosen repositories from the request
    repo_name = body['repository']
    # Add your own GitHub Token to run it local
    token = os.environ.get(
        'GITHUB_TOKEN', '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')
    GITHUB_URL = f"https://api.github.com/"
    headers = {
        "Authorization": f'token {token}'
    }
    params = {
        "state": "open"
    }
    repository_url = GITHUB_URL + "repos/" + repo_name
    # Fetch GitHub data from GitHub API
    repository = requests.get(repository_url, headers=headers)
    # Convert the data obtained from GitHub API to JSON format
    repository = repository.json()

    today = date.today()

    issues_reponse = []
    # Iterating to get issues for every month for the past 12 months
    for i in range(2):
        last_month = today + dateutil.relativedelta.relativedelta(months=-i-1)
        types = 'type:issue'
        repo = 'repo:' + repo_name
        ranges = 'created:' + str(last_month) + '..' + str(today)
        # By default GitHub API returns only 30 results per page
        # The maximum number of results per page is 100
        # For more info, visit https://docs.github.com/en/rest/reference/repos 
        per_page = 'per_page=100'
        # Search query will create a query to fetch data for a given repository in a given time range
        search_query = types + ' ' + repo + ' ' + ranges

        # Append the search query to the GitHub API URL 
        query_url = GITHUB_URL + "search/issues?q=" + search_query + "&" + per_page
        # requsets.get will fetch requested query_url from the GitHub API
        search_issues = requests.get(query_url, headers=headers, params=params)
        # Convert the data obtained from GitHub API to JSON format
        search_issues = search_issues.json()
        issues_items = []
        try:
            # Extract "items" from search issues
            issues_items = search_issues.get("items")
        except KeyError:
            error = {"error": "Data Not Available"}
            resp = Response(json.dumps(error), mimetype='application/json')
            resp.status_code = 500
            return resp
        if issues_items is None:
            continue
        for issue in issues_items:
            label_name = []
            data = {}
            current_issue = issue
            # Get issue number
            data['issue_number'] = current_issue["number"]
            # Get created date of issue
            data['created_at'] = current_issue["created_at"][0:10]
            if current_issue["closed_at"] == None:
                data['closed_at'] = current_issue["closed_at"]
            else:
                # Get closed date of issue
                data['closed_at'] = current_issue["closed_at"][0:10]
            for label in current_issue["labels"]:
                # Get label name of issue
                label_name.append(label["name"])
            data['labels'] = label_name
            # It gives state of issue like closed or open
            data['State'] = current_issue["state"]
            # Get Author of issue
            data['Author'] = current_issue["user"]["login"]
            issues_reponse.append(data)

        today = last_month

    df = pd.DataFrame(issues_reponse)

    # Daily Created Issues
    df_created_at = df.groupby(['created_at'], as_index=False).count()
    dataFrameCreated = df_created_at[['created_at', 'issue_number']]
    dataFrameCreated.columns = ['date', 'count']

    '''
    Monthly Created Issues
    Format the data by grouping the data by month
    ''' 
    created_at = df['created_at']
    month_issue_created = pd.to_datetime(
        pd.Series(created_at), format='%Y-%m-%d')
    month_issue_created.index = month_issue_created.dt.to_period('m')
    month_issue_created = month_issue_created.groupby(level=0).size()
    month_issue_created = month_issue_created.reindex(pd.period_range(
        month_issue_created.index.min(), month_issue_created.index.max(), freq='m'), fill_value=0)
    month_issue_created_dict = month_issue_created.to_dict()
    created_at_issues = []
    for key in month_issue_created_dict.keys():
        array = [str(key), month_issue_created_dict[key]]
        created_at_issues.append(array)

    '''
    Monthly Closed Issues
    Format the data by grouping the data by month
    ''' 
    
    closed_at = df['closed_at'].sort_values(ascending=True)
    month_issue_closed = pd.to_datetime(
        pd.Series(closed_at), format='%Y-%m-%d')
    month_issue_closed.index = month_issue_closed.dt.to_period('m')
    month_issue_closed = month_issue_closed.groupby(level=0).size()
    month_issue_closed = month_issue_closed.reindex(pd.period_range(
        month_issue_closed.index.min(), month_issue_closed.index.max(), freq='m'), fill_value=0)
    month_issue_closed_dict = month_issue_closed.to_dict()
    closed_at_issues = []
    for key in month_issue_closed_dict.keys():
        array = [str(key), month_issue_closed_dict[key]]
        closed_at_issues.append(array)


    closed_at = df['closed_at'].sort_values(ascending=True)
    # Convert 'closed_at' to datetime
    closed_at = pd.to_datetime(closed_at)
    # # Group closed issues by week
    weekly_closed_issues = closed_at.groupby(closed_at.dt.to_period("W")).size()
    # Reindex to fill missing weeks
    weekly_closed_issues = weekly_closed_issues.reindex(pd.period_range(
        weekly_closed_issues.index.min(), weekly_closed_issues.index.max(), freq='W'), fill_value=0)
    # Convert to a list of lists
    weekly_issue_closed_dict = weekly_closed_issues.to_dict()
    weeklu_closed_issues = []
    for key in weekly_issue_closed_dict.keys():
        array = [str(key), weekly_issue_closed_dict[key]]
        weeklu_closed_issues.append(array)

    '''
        1. Hit LSTM Microservice by passing issues_response as body
        2. LSTM Microservice will give a list of string containing image paths hosted on google cloud storage
        3. On recieving a valid response from LSTM Microservice, append the above json_response with the response from
            LSTM microservice
    '''
    ''''''
    created_at_body = {
        "issues": issues_reponse,
        "type": "created_at",
        "repo": repo_name.split("/")[1]
    }
    closed_at_body = {
        "issues": issues_reponse,
        "type": "closed_at",
        "repo": repo_name.split("/")[1]
    }

    forecastRequest = {
        "repo_key": repo_name,
        "repo_name": repo_name.split("/")[1],
        "start_date" : "2023-09-21",
        "end_date" : "2023-11-21"
    }


    # Update your Google cloud deployed LSTM app URL (NOTE: DO NOT REMOVE "/")
    LSTM_API_URL = "https://lstm-2c3jrgnz2a-uc.a.run.app/" + "api/forecast/lstm"

    # Update your Google cloud deployed PROPHET app URL (NOTE: DO NOT REMOVE "/")
    PROPHET_URL = "http://localhost:8081/" + "api/forecast/prophet"


     # Update your Google cloud deployed STATSMODEL app URL (NOTE: DO NOT REMOVE "/")
    STATSMODEL_URL = "http://localhost:8085/" + "api/forecast/statsmodel"

    '''
    Trigger the LSTM microservice to forecasted the created issues
    The request body consists of created issues obtained from GitHub API in JSON format
    The response body consists of Google cloud storage path of the images generated by LSTM microservice
    '''
    createdAt_lstm = requests.post(LSTM_API_URL,
                                         json=created_at_body,
                                         headers={'content-type': 'application/json'})
    
    '''
    Trigger the LSTM microservice to forecasted the closed issues
    The request body consists of closed issues obtained from GitHub API in JSON format
    The response body consists of Google cloud storage path of the images generated by LSTM microservice
    '''    
    closedAt_lstm = requests.post(LSTM_API_URL,
                                        json=closed_at_body,
                                        headers={'content-type': 'application/json'})
    
    '''
    Create the final response that consists of:
        1. GitHub repository data obtained from GitHub API
        2. Google cloud image urls of created and closed issues obtained from LSTM microservice
    '''

    '''
    Trigger the Prophet microservice to forecasted the created issues
    The request body consists of created issues obtained from GitHub API in JSON format
    The response body consists of Google cloud storage path of the images generated by Prophet microservice
    '''
    prophetResponse = requests.post(PROPHET_URL,
                                        json=forecastRequest,
                                         headers={'content-type': 'application/json'})
    
    statsModelResponse = requests.post(STATSMODEL_URL,
                                         json=forecastRequest,
                                         headers={'content-type': 'application/json'})


    json_response = {
        "created": created_at_issues,
        "closed": closed_at_issues,
        "weeklyClosed" : weeklu_closed_issues,
        "starCount": repository["stargazers_count"],
        "forkCount": repository["forks_count"],
        "createdAt_lstm": {
            **createdAt_lstm.json(),
        },
        "closedAt_lstm": {
            **closedAt_lstm.json(),
        },
        "prophetForecastData":{
            **prophetResponse.json(),
        },
        "statsModelForecastData":{
            **statsModelResponse.json(),
        }
    }

    # Return the response back to client (React app)
    return jsonify(json_response)

@app.route('/api/github/allreposdata', methods=['POST'])
def all_repo_data():
    logging.info("In all_repo_data method")
    body = request.get_json()
    # Extract the list of repositories from the request
    repo_dict = body.get('repositories', {})

    all_repo_data = []
    for repo_name, repo_key in repo_dict.items():
        logging.info(repo_key)
        repo_data = get_repo_data(repo_key, repo_name)
        all_repo_data.append(repo_data)

    # Process responses for all repositories and form the final response
    final_response = {
        "items": [
            {
                "reponame": repo["reponame"],
                "issuesCreated": sum([count for _, count in repo["issuesCreated"]]),
                "issuesClosed": sum([count for _, count in repo["issuesClosed"]]),
                "starCount": repo["starCount"],
                "forkCount": repo["forkCount"],
            }
            for repo in all_repo_data
        ]
    }

    # Return the final response back to the client (React app)
    return jsonify(final_response)

# Function to get repository data for a given repository
def get_repo_data(repo_key, repo_name):
    # givedeployed flask url
    REPO_DATA_URL = "http://localhost:5001/" + "api/github"
    
    logging.info("In get_repo_data method")
    logging.info(REPO_DATA_URL)


    headers = {"Content-Type": "application/json"}

    # Send a POST request to /api/github with the repository key
    response = requests.post(REPO_DATA_URL, json={"repository": repo_key}, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON data
        repo_data = response.json()

        # Return relevant repository data
        return {
            "reponame": repo_name,
            "issuesCreated": repo_data.get("created", []),
            "issuesClosed": repo_data.get("closed", []),
            "starCount": repo_data.get("starCount", 0),
            "forkCount": repo_data.get("forkCount", 0),
        }
    else:
        # Handle the case where the request was not successful
        print(f"Failed to fetch data for repository {repo_name}. Status code: {response.status_code}")
        return {
            "reponame": repo_name,
            "issuesCreated": [],
            "issuesClosed": [],
            "starCount": 0,
            "forkCount": 0,
        }



# Run flask app server on port 5000
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)