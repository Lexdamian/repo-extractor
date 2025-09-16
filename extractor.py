import requests
from requests.auth import HTTPBasicAuth
import re
import os

import urllib3

# Suppress InsecureRequestWarning (Not Recommended)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIG ---
JIRA_BASE = "https://lightspeedsystems.atlassian.net"
USERNAME = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")

if not USERNAME or not API_TOKEN:
    raise RuntimeError("Environment variables JIRA_USERNAME or JIRA_API_TOKEN are not set.")

fix_version = input("Enter fixVersion (e.g., 'Release 1.2.3'): ")
JQL = f'fixVersion = "{fix_version}" AND type IN (Story, Bug)'  # or "Epic Link" = EPIC-123

# --- AUTH & HEADERS ---
auth = HTTPBasicAuth(USERNAME, API_TOKEN)
headers = {"Accept": "application/json"}

# --- HELPERS ---
def get_issue_keys():
    url = f"{JIRA_BASE}/rest/api/3/search/jql"
    params = {"jql": JQL, "fields": "key", "maxResults": 100}
    try:
        resp = requests.get(url, headers=headers, auth=auth, params=params, verify=False)

        if resp.status_code != 200:
            print(f"Failed to fetch issues. Status Code: {resp.status_code}")
            print(f"Response: {resp.text}")
            return []

        data = resp.json()
        return [issue["key"] for issue in data.get("issues", [])]

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_pull_requests(issue_key):
    url = f"{JIRA_BASE}/rest/dev-status/1.0/issue/detail"
    params = {
        "issueId": get_issue_id(issue_key),
        "applicationType": "GitHub",  # Or Bitbucket, GitLab
        "dataType": "pullrequest"
    }
    resp = requests.get(url, headers=headers, auth=auth, params=params, verify=False)
    resp.raise_for_status()
    pr_data = resp.json()
    prs = []
    for detail in pr_data.get("detail", []):
        for pr in detail.get("pullRequests", []):
            prs.append(pr.get("url"))
    return prs

def get_issue_id(issue_key):
    url = f"{JIRA_BASE}/rest/api/2/issue/{issue_key}"
    resp = requests.get(url, headers=headers, auth=auth, verify=False)
    resp.raise_for_status()
    return resp.json()["id"]

def extract_repo_from_url(url):
    match = re.search(r"github\.com[:/](.+?/.+?)(?:/|$)", url)
    return match.group(1) if match else None

# --- MAIN ---
def main():
    issue_keys = get_issue_keys()
    repos = set()
    for key in issue_keys:
        pr_urls = get_pull_requests(key)
        for url in pr_urls:
            repo = extract_repo_from_url(url)
            if repo:
                repos.add(repo)
    print("Repos involved:")
    for r in sorted(repos):
        print("-", r)

if __name__ == "__main__":
    main()
