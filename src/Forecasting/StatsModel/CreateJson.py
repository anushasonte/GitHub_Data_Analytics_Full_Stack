import github3
import json

def build_json_file(repo_name,repo_key, start_date, end_date):
    GITHUB_TOKEN = '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' 
    BASE_PATH= '/Users/anushasp/Desktop/HW5_Sonte_Parameshwar,Anusha/src/Forecasting/Prophet/static/repofiles/'
    REPO_FILENAME=  BASE_PATH + repo_name + '.json'
    print("Full Path:", REPO_FILENAME)
    gh = github3.login(token=GITHUB_TOKEN)  # No authentication needed for public repositories
    
    f = open(REPO_FILENAME, 'w')
        # Issues
    issue_query = f'type:issue repo:{repo_key} created:{start_date}..{end_date}'
    for issue in gh.search_issues(issue_query):  
            label_name = []
            data = {}
            current_issue = issue.as_json()
            current_issue = json.loads(current_issue)
            data['type'] = 'issue'
            data['issue_number'] = current_issue["number"] 
            data['created_at'] = current_issue["created_at"][0:10]  
            if current_issue["closed_at"] is None:
                data['closed_at'] = current_issue["closed_at"]
            else:
                data['closed_at'] = current_issue["closed_at"][0:10]  
            for label in current_issue["labels"]:
                label_name.append(label["name"])  
            data['labels'] = label_name
            data['state'] = current_issue["state"]  
            data['author'] = current_issue["user"]["login"]  
            out = json.dumps(data)  
            f.write(out + '\n')

        
    # Pull Requests
    f = open(REPO_FILENAME, 'a')
    pr_query = f'type:pr repo:{repo_key} created:{start_date}..{end_date}'
    print(pr_query)
    for issue in gh.search_issues(pr_query):
            pr_data = {}
            current_pr = issue.as_json()
            current_pr = json.loads(current_pr)
            pr_data['type'] = 'pull_request'
            pr_data['pr_number'] = current_pr["number"]
            pr_data['created_at'] = current_pr["created_at"][0:10]
            if current_pr["closed_at"] is None:
                pr_data['closed_at'] = current_pr["closed_at"]
            else:
                pr_data['closed_at'] = current_pr["closed_at"][0:10]
            pr_data['state'] = current_pr["state"]
            pr_data['author'] = current_pr["user"]["login"]
            out = json.dumps(pr_data)
            f.write(out + '\n')

    # Commits
    f = open(REPO_FILENAME, 'a')
    commit_query = f'repo:{repo_key} author-date:{start_date}..{end_date}'
    print(commit_query)
    for commit in gh.iter_commits(commit_query):
            commit_data = {}
            commit_data['type'] = 'commit'
            commit_data['sha'] = commit.sha
            commit_data['author'] = commit.author['login']
            commit_data['date'] = commit.commit.author['date'][0:10]
            out = json.dumps(commit_data)
            f.write(out + '\n')

    repo = gh.repository(*repo_key.split('/'))
    # Iterate over commits
    for commit in repo.commits():
         print(commit.sha, commit.author.login, commit.commit.message)


    # Branches
    f = open(REPO_FILENAME, 'a')
    branches = [branch.name for branch in gh.repository(repo_key).iter_branches()]
    branch_data = {'type': 'branch', 'branches': branches}
    f.write(json.dumps(branch_data) + '\n')

    # Contributors
    f = open(REPO_FILENAME, 'a')
    contributors = [contributor.login for contributor in gh.repository(repo_key).iter_contributors()]
    contributor_data = {'type': 'contributor', 'contributors': contributors}
    f.write(json.dumps(contributor_data) + '\n')

     # Releases
    f = open(REPO_FILENAME, 'a')
    releases = [release.tag_name for release in gh.repository(repo_key).iter_releases()]
    release_data = {'type': 'release', 'releases': releases}
    f.write(json.dumps(release_data) + '\n')

    print("File Generated Successfully!")

# Replace 'your_repo_name' with the actual public repository name
repo_key = 'angular/angular'
repo_name = "Angular"
# Replace 'start_date' and 'end_date' with the desired time range in the format 'YYYY-MM-DD'
start_date = '2023-01-01'
end_date = '2023-11-20'

# Call the method
build_json_file(repo_name, repo_key, start_date, end_date)
