# https://vodsbeta.netlify.app
# Notes

### 1. crawler

This contains a python script([`crawl.py`](./crawler/crawl.py)) that fetches and parses video description, and posts results to the github gist, which can be used as API from the frontend site. This also includes a utility script that packages this script to a aws-lamda deployment package.

#### ENVIRONMENT VARIABLES

```python
# youtube data API key to fetch videos and their description
SECRET_YOUTUBE_API_KEY="YOUTUBE_API_KEY"

# github personal API token, to post the parsed data to a gist to host the JSON for free
SECRET_GITHUB_GIST_TOKEN="GITHUB_PERSONAL_TOKEN"

# your channel id
CHANNEL_ID="YOUTUBE_CHANNEL_ID"

# github gist's id to which we post the data to,
# you might have to create two empty files called `data.json` and
# `processed.json` while creating the gist
# github's personal token created above should have perms to creating/updating gists
DB_GIST_ID="GIST_ID"
```

Ideally, if we create an AWS CloudWatch event that triggers this lambda every day, we can stay within AWS free tier forever.

### 2. Site

This is just a simple html-css-js frontend that gets data from the gist, and shows it to user.

Ideally, this can be dragged-and-dropped to netlify or deployed to github pages, so that we can stay within free tier forever.
