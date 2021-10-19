import requests
import json
from flask import current_app
from rc_bookmark_catcher import models

redcap_url = current_app.config['REDCAP_URL']
_payload_skel = dict( format = 'json')

class REDCapError(RuntimeError):
    """REDCap connection related errors"""
    pass

def make_project_from_token( token ):
    mypayload = _payload_skel
    mypayload['content'] = 'project'
    mypayload['token'] = token

    myrequest = requests.post(redcap_url, mypayload)
    if not myrequest.ok:
        raise REDCapError('REDCap request failed')
    
    myrequestjson = json.loads(myrequest.text)
    
    myproject = models.Project(
        project_id = myrequestjson.get('project_id', None),
        project_title = myrequestjson.get('project_title', None),
        api_token = token
    )

    return myproject
