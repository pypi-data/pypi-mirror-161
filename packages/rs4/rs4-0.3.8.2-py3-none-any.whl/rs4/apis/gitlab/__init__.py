import requests
import json
import os

TOKEN = None
config = os.path.expanduser ('~/.config/gitlab/api-token.json')
if os.path.isfile (config):
    with open (config) as f:
        cf = json.loads (f.read ())
        TOKEN = cf ['token']

def build_header (token, content_type = 'application/json'):
    assert token, "token not provided"
    h = {"PRIVATE-TOKEN": token}
    if content_type:
        h ["Content-Type"] = content_type
    return h


def post_issue (proejct_id, title, content, assignee_ids = [], token = TOKEN):
    payload = {
        'title': title,
        'description': content,
        'assignee_ids': assignee_ids
    }
    r = requests.post (
        'https://gitlab.com/api/v4/projects/{}/issues'.format (proejct_id),
        json.dumps (payload),
        headers = build_header (token)
    )
    return r.json ()

def post_note (proejct_id, issue_iid, content, token = TOKEN):
    payload = {
        'body': content
    }
    r = requests.post (
        'https://gitlab.com/api/v4/projects/{}/issues/{}/notes'.format (proejct_id, issue_iid),
        json.dumps (payload),
        headers = build_header (token)
    )
    return r.json ()

def upload (proejct_id, path, token = TOKEN):
    r = requests.post (
        'https://gitlab.com/api/v4/projects/{}/uploads'.format (proejct_id),
        files = dict (file = open (path, 'rb')),
        headers = build_header (token, None)
    )
    return r.json ()
