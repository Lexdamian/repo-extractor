This tool can be used to connet cu JIRA api and extract all the repos that are involved in a release. 

Requirements: 

You need to set up two environment variables: 
  JIRA_EMAIL  - the email you are using to login in Jira
  JIRA_API_TOKEN  - generated token in Jira

Runinig the script will return a list of repositories that need to be deployed for the specified Jira release plan. 
