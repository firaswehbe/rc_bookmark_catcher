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

def fetch_project_instruments( myproject = None ):
    if not isinstance(myproject, models.Project):
        raise REDCapError(f'Cannot laod instruments because a Project object was not passed')

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
            project_id = myproject.project_id,
            instrument_name = myrequestjson[i]['instrument_name'],
            instrument_label = myrequestjson[i]['instrument_label'],
            order_num = i
        ))

    return myinstruments

def fetch_project_fields( myproject = None ):
    if not isinstance(myproject, models.Project):
        raise REDCapError(f'Cannot laod variables because a Project object was not passed')

    mypayload = _payload_skel
    mypayload['content'] = 'metadata'
    mypayload['token'] = myproject.api_token
    myrequest = requests.post(redcap_url, mypayload)
    if not myrequest.ok:
        raise REDCapError('REDCap request failed')
    myrequestjson = json.loads(myrequest.text)

    myvariables = list()
    for i in range(len(myrequestjson)):
        myvariables.append( models.Field (
            project_id = myproject.project_id,
            field_name = myrequestjson[i]['field_name'],
            form_name = myrequestjson[i]['form_name'],
            field_label = myrequestjson[i]['field_label'],
            order_num = i
        ))

    return myvariables

