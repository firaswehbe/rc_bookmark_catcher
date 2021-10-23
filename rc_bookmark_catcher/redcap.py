import requests
import json
from flask import current_app
from rc_bookmark_catcher import models
from rc_bookmark_catcher import db

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

def fetch_project_instruments( pid ):
    # The pid needs to be in the database
    myproject = models.Project.query.get( pid )
    if myproject is None:
        raise REDCapError(f'Cannot laod instruments because project_id [{pid}] is not present in the database')

    mypayload = _payload_skel
    mypayload['content'] = 'instrument'
    mypayload['token'] = myproject.api_token
    myrequest = requests.post(redcap_url, mypayload)
    if not myrequest.ok:
        raise REDCapError('REDCap request failed')
    myrequestjson = json.loads(myrequest.text)

    myinstruments = list()
    for i in range(len(myrequestjson)):
        myinstruments.append( models.Instrument (
            project_id = pid,
            instrument_name = myrequestjson[i]['instrument_name'],
            instrument_label = myrequestjson[i]['instrument_label'],
            order_num = i
        ))

    return myinstruments

    # TODO: Instantiate instruments objects based on their name and label

    # TODO: descend to variable level

    return myrequestjson
