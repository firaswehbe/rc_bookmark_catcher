import requests
import json
from flask import current_app
from rc_bookmark_catcher import models
from rc_bookmark_catcher import db

redcap_url = current_app.config['REDCAP_URL']

class REDCapError(RuntimeError):
    """REDCap connection related errors"""
    pass

#TODO: REFACTOR
def make_project_from_token( token,stu ):
    mypayload = dict( format = 'json')
    mypayload['content'] = 'project'
    mypayload['token'] = token

    myrequest = requests.post(redcap_url, mypayload)
    if not myrequest.ok:
        raise REDCapError('REDCap request failed')
    
    myrequestjson = json.loads(myrequest.text)
    
    myproject = models.Project(
        pid = myrequestjson.get('project_id', None),
        project_title = myrequestjson.get('project_title', None),
        api_token = token,
        stu = stu,
        is_longitudinal = myrequestjson.get('is_longitudinal', None),
        has_repeating_instruments_or_events = myrequestjson.get('has_repeating_instruments_or_events', None),
        surveys_enabled = myrequestjson.get('surveys_enabled', None)
    )

    return myproject

#TODO: REFACTOR
def fetch_project_instruments( myproject ):
    if not isinstance(myproject, models.Project):
        raise REDCapError(f'Cannot laod instruments because a Project object was not passed')

    mypayload = dict( format = 'json')
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

#TODO: REFACTOR -- make select2
def fetch_project_fields( myproject ):
    if not isinstance(myproject, models.Project):
        raise REDCapError(f'Cannot laod variables because a Project object was not passed')

    mypayload = dict( format = 'json')
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

def fetch_advanced_link_info ( authkey ):
    '''
    The advanced link feature in project bookmarks only sends an authentication token. You will need to send that back to REDCap to get the other information.
    '''
    mypayload = dict( format = 'json' )
    mypayload['authkey'] = authkey
    myresponse = requests.post(redcap_url, mypayload)
    if not myresponse.ok:
        raise REDCapError('Could not finalize REDCap authentication key validation')
    myresponsejson = json.loads(myresponse.text)

    return myresponsejson

def fetch_advanced_link_records( project, advancedlinkinfo ):
    """
    The function takes as input the information passed from the lookup from redcap.fetch_advanced_link_info()
    Appended to it the record number and the event name passed as part of the URL parameters
    """
    if not isinstance(project, models.Project):
        raise REDCapError(f'Cannot laod instruments because a Project object was not passed')
    mypayload = dict( format = 'json' )
    mypayload['content'] = 'record'
    mypayload['token'] = project.api_token
    if advancedlinkinfo.get( 'get_record', None) is not None: 
        mypayload['records[0]'] = advancedlinkinfo['get_record']
    if advancedlinkinfo.get( 'get_event', None) is not None: 
        mypayload['events[0]'] = advancedlinkinfo['get_event']
    
    myresponse = requests.post(redcap_url, mypayload)
    if not myresponse.ok:
        raise REDCapError('Could not fetch records associated with this project and key')
    myresponsejson = json.loads(myresponse.text)

    return myresponsejson



