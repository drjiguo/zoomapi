###############################################################################
#
#
#
#
#
#           Zoom API
#
#            Ji Guo 
#
#
###############################################################################

###############################################################################
# Import packages
###############################################################################

import pandas as pd
import numpy as np
import requests
import json
import html
from datetime import datetime
from urllib.parse import quote
from datetime import date
from dateutil import tz
import pickle
import os



###############################################################################
# get token
###############################################################################


def get_token(token = False, refresh_token = False):
    file = open('token.txt', 'r')
    jfile = json.load(file)
    if token == True:
        new_token = jfile['access_token']
        return new_token
    if refresh_token == True:
        new_refresh = jfile['refresh_token']
        return new_refresh

###############################################################################
# get meeting daily report
###############################################################################


def get_meeting_daily_report(year, month):
    
    meeting_url = 'https://api.zoom.us/v2/report/daily?month={}&year={}'.format(month, year)
    # headers
    headers = { 'authorization': "Bearer {}".format(get_token(token = True)) }
    # get meetings
    meetings = requests.get(meeting_url, headers = headers)
    # load json
    meeting_data = meetings.json()
    # create lists
    date = []
    new_users = [] 
    meetings = []
    participants = []
    meeting_minutes = []
    # add components to lists
    for i in meeting_data['dates']:
        date.append(i['date'])
        new_users.append(i['new_users'])
        meetings.append(i['meetings'])
        participants.append(i['participants'])
        meeting_minutes.append(i['meeting_minutes'])
    # create a dataframe
    meeting_daily_report = pd.DataFrame({'date': date,
                                         'new_users': new_users,
                                         'meetings': meetings,
                                         'participants': participants,
                                         'meeting_minutes': meeting_minutes})
    return meeting_daily_report





###############################################################################
# get meeting history
###############################################################################


def get_meeting_history(meeting_id):
    """
    

    Parameters
    ----------
    meeting_id : string but numbers
        numerical ids.

    Returns
    -------
    data : dataframe
        list of uuids and associated meeting information. 

    """
    #load headers
    headers = { 'authorization': "Bearer {}".format(get_token(token = True))}
    # get meeting uuids
    m_url = 'https://api.zoom.us/v2/past_meetings/{}/instances'.format(meeting_id)
    ms = requests.get(m_url, headers = headers)
    m_data = ms.json()
    uuids = []
    for i in m_data['meetings']:
        print(i)
        uuids.append(i['uuid'])

    # create lists
    uuid = []
    dept = []
    start_time = []
    end_time = []
    topic = []
    participants = []
    duration = []
    third_party_audio = []
    pstn = []
    recording = []
    screen_share = []
    sip = []
    video = []
    voip = []
    host_id = []
    host_name = []
    host_email = []
    
    # loop uuid
    for i in uuids:
        print(i)
        # if uuid starts with '/' or '//', quote 2 times
        if i[0] == '/' or '//' in i:
            k = quote(quote(i, safe=""), safe="")
            print(k)
            print('Weird UUID with / or // as the start')
            print('')
            print('Pay attention!!!!')
            print('')
        else:
            k = i
        # get data
        meeting_url = 'https://api.zoom.us/v2/metrics/meetings/{}?type=past'.format(k)
        meeting = requests.get(meeting_url, headers = headers)
        meeting_data = meeting.json()
        # add data  
        uuid.append(meeting_data['uuid'])
        dept.append(meeting_data['dept'])
        start_time.append(meeting_data['start_time'])
        end_time.append(meeting_data['end_time'])
        topic.append(meeting_data['topic'])
        participants.append(meeting_data['participants'])
        duration.append(meeting_data['duration'])
        third_party_audio.append(meeting_data['has_3rd_party_audio'])
        pstn.append(meeting_data['has_pstn'])
        recording.append(meeting_data['has_recording'])
        screen_share.append(meeting_data['has_screen_share'])
        sip.append(meeting_data['has_sip'])
        video.append(meeting_data['has_video'])
        voip.append(meeting_data['has_voip'])
        host_id.append(meeting_data['id'])
        host_name.append(meeting_data['host'])
        host_email.append(meeting_data['email'])
            
    # create df
    data = pd.DataFrame({'meeting_uuid':uuid, 
                         'meeting_department':dept,
                         'meeting_start_time':start_time,
                         'meeting_end_time':end_time,
                         'meeting_duration':duration,
                         'meeting_topic':topic,
                         'meeting_participants':participants,
                         'meeting_third_party_audio':third_party_audio,
                         'meeting_pstn':pstn,
                         'meeting_recording':recording,
                         'meeting_screen_share':screen_share,
                         'meeting_sip':sip,
                         'meeting_video':video,
                         'meeting_voip':voip,
                         'meeting_host_id':host_id,
                         'meeting_host_name':host_name,
                         'meeting_host_email':host_email})
    data['meeting_id'] = meeting_id
    return data


###############################################################################
# get meeting participants from dashboard
###############################################################################
# duration, join time, left time, email maybe different from report
# missing some speaker or info. 
def get_meeting_participants_dashboard(muuid):
    """
    

    Parameters
    ----------
    muuid : string
        meeting uuid

    Returns
    -------
    data : dataframe
        user information associated to the meetings. 

    """
# if uuid starts with '/' or '//', quote 2 times
    if muuid[0] == '/' or '//' in muuid:
        k = quote(quote(muuid, safe=""), safe="")
        print(k)
        print('Weird UUID with / or // as the start')
        print('')
        print('Pay attention!!!!')
        print('')
    else:
            k = muuid    

# get data
   
    headers = { 'authorization': "Bearer {}".format(get_token(token = True))}
    meeting_url = 'https://api.zoom.us/v2/metrics/meetings/{}/participants?type=past&page_size=300'.format(k)
       
    initial_meeting = requests.get(meeting_url, headers = headers)
    data = []
    total = initial_meeting.json()['total_records']
    while True:
        raw = json.loads(initial_meeting.text)
        for i in raw['participants']:
            data.append(i)
        try:
            raw['next_page_token'] != ''
            new_link = 'https://api.zoom.us/v2/metrics/meetings/{}/participants?type=past&page_size=300&next_page_token={}'.format(k, raw['next_page_token'])
            new_meeting = requests.get(new_link, headers = headers)
            initial_meeting = new_meeting
        except KeyError:
            break  
        
        if len(data) == total:
            print('total records = {}. We have {}'.format(total, len(data)))
            k = 2 * 10 - 2  # It is used for number of spaces  
            for i in range(0, 10):  
                for j in range(0, k):  
                    print(end=" ")  
                k = k - 2   # decrement k value after each iteration  
                for j in range(0, i + 1):  
                    print("* ", end="")  # printing star  
                print("")  
            break
    
    meeting_data = data
    
    # create lists 
    user_zoom_id = []
    user_id = []
    user_name = []
    device = []
    ip = []
    location = []
    network = []
    data_center = []
    conn_type = []
    join_time = []
    left_time = []
    share_application = []
    share_desktop = []
    share_whiteboard = []
    recording = []
    leave_reason = []
    email = []
    duration = []
    camera = []
    mic = []
    speaker = []

#every for loop to determine whether there is data associated to the variable.
# if True, yes, else, assigned value. 

    for info in meeting_data:
        if info.get('id'):
            user_zoom_id.append(info['id'])
        else:
            user_zoom_id.append('NoZoomUserID')
           
    for info in meeting_data:
        if info.get('connection_type'):
            conn_type.append(info['connection_type'])
        else:
            conn_type.append('NoData')    
            
    
    for info in meeting_data:    
        # if email is in the dict or not
        if info.get('email'):
            user_id.append(info['user_id'])
            user_name.append(info['user_name'])
            email.append(info['email'])
            device.append(info['device'])
            ip.append(info['ip_address'])
            location.append(info['location'])
            network.append(info['network_type'])
            data_center.append(info['data_center'])
            share_application.append(info['share_application'])
            share_desktop.append(info['share_desktop'])
            share_whiteboard.append(info['share_whiteboard'])
            recording.append(info['recording'])
            
        else:
            user_id.append(info['user_id'])
            user_name.append(info['user_name'])
            email.append('NoEmail')
            device.append(info['device'])
            ip.append(info['ip_address'])
            location.append(info['location'])
            network.append(info['network_type'])
            data_center.append(info['data_center'])
            share_application.append(info['share_application'])
            share_desktop.append(info['share_desktop'])
            share_whiteboard.append(info['share_whiteboard'])
            recording.append(info['recording'])

    for info in meeting_data:
        if info.get('leave_time'):
            join_time.append(info['join_time'])
            left_time.append(info['leave_time'])
            duration_seconds = datetime.strptime(info['leave_time'], "%Y-%m-%dT%H:%M:%SZ") - datetime.strptime(info['join_time'], "%Y-%m-%dT%H:%M:%SZ")
            duration.append(duration_seconds.seconds)
        else:
            join_time.append(info['join_time'])
            left_time.append(info['join_time'])
            duration.append(int(0))
            
    for info in meeting_data:
        if info.get('leave_reason'):
            leave_reason.append(info['leave_reason'].split('Reason: ')[1])
        else:
            leave_reason.append('NotAvailable')
        
    for info in meeting_data:
        if info.get('camera'):
            camera.append(info['camera'])
        else:
            camera.append('NoCameraInfo')

    for info in meeting_data:
        if info.get('microphone'):
            mic.append(info['microphone'])
        else:
            mic.append('NoMicInfo')
            
    for info in meeting_data:
        if info.get('speaker'):
            speaker.append(info['speaker'])
        else:
            speaker.append('NoSpeakerInfo')
        
# create the dataframe   
    data = pd.DataFrame({'user_zoom_id':user_zoom_id,
                         'user_id':user_id,
                         'user_name':user_name,
                         'user_email': email,
                         'user_device':device,
                         'user_camera':camera,
                         'user_speaker':speaker,
                         'user_mic':mic,
                         'user_ip':ip,
                         'user_location':location,
                         'user_data_center':data_center,
                         'user_conn_type':conn_type,
                         'user_join_time':join_time,
                         'user_left_time':left_time,
                         'user_attendance_duration':duration,
                         'user_share_application':share_application,
                         'user_share_desktop':share_desktop,
                         'user_share_whiteboard':share_whiteboard,
                         'user_recording':recording,
                         'user_leave_reason':leave_reason})
    
    data['meeting_uuid'] = muuid
    if 'NoEmail' in list(data.user_email):
        no_email = data[data.user_email == 'NoEmail']
        print('No Email Exists: {}, Check report'.format(len(no_email)))
        print(no_email)
        
    return data

###############################################################################
# merge meeting users
###############################################################################



def merge_meeting_user(meetings):
    """
    
    Parameters
    ----------
    meetings : dataframe
        meeting history

    Returns
    -------
    meeting_user : dataframe
        merged users and meetings

    """
    data_list = []
    #loop to get data
    for id in meetings.meeting_uuid:
        print(id)
        x = matching_emails(id)
        data_list.append(x)
    #combine multiple dfs
    final = pd.concat(data_list)
    # merge data
    meeting_user = pd.merge(meetings, final)
    return meeting_user

###############################################################################
# get all zoom user
###############################################################################

def get_all_zoom_users():
    """
    

    Returns
    -------
    user_data : dataframe
        DESCRIPTION.

    """
# create new lists
    user_zoom_id = []
    user_first_name = []
    user_last_name = []
    user_email = []
    user_type = []
    user_pmi = []
    user_verified = []
    user_status = []
    user_created = []
    user_last_login = []
    # get the pages 
    #load headers
    headers = { 'authorization': "Bearer {}".format(get_token(token = True))}
    pre = 'https://api.zoom.us/v2/users?page_size=300'
    pre_d = requests.get(pre, headers = headers)
    pre_j = pre_d.json()
    # for loop
    for j in range(1, (pre_j['page_count']+1)):
        print(j)
        # get each page
        url = 'https://api.zoom.us/v2/users?page_size=300&page_number={}'.format(j)
        print(url)
        user = requests.get(url, headers = headers)
        users = user.json()
        # if no first name, then no name
        # else first / last name
        for i in range(len(users['users'])):
            print(i)
            if not users['users'][i].get('first_name'):
                user_zoom_id.append(users['users'][i]['id'])
                user_first_name.append('NoFirst')
                user_last_name.append('NoLast')
                user_email.append(users['users'][i]['email'])
                user_type.append(users['users'][i]['type'])
                user_pmi.append(users['users'][i]['pmi'])
                user_verified.append(users['users'][i]['verified'])
                user_created.append(users['users'][i]['created_at'])
                user_status.append(users['users'][i]['status'])
                if not users['users'][i].get('last_login_time'):
                    user_last_login.append('NoInfo')
                else:
                    user_last_login.append(users['users'][i]['last_login_time'])
            
        
            else:
                user_zoom_id.append(users['users'][i]['id'])
                user_first_name.append(users['users'][i]['first_name'])
                user_last_name.append(users['users'][i]['last_name'])
                user_email.append(users['users'][i]['email'])
                user_type.append(users['users'][i]['type'])
                user_pmi.append(users['users'][i]['pmi'])
                user_verified.append(users['users'][i]['verified'])
                user_created.append(users['users'][i]['created_at'])
                user_status.append(users['users'][i]['status'])
                if not users['users'][i].get('last_login_time'):
                    user_last_login.append('NoInfo')
                else:
                    user_last_login.append(users['users'][i]['last_login_time'])
    # create the dataframe
    user_data = pd.DataFrame({'user_zoom_id':user_zoom_id,
                              'user_first_name':user_first_name,
                              'user_last_name':user_last_name ,
                              'user_email':user_email ,
                              'user_type':user_type ,
                              'user_pmi':user_pmi ,
                              'user_verified': user_verified,
                              'user_status':user_status ,
                              'user_created':user_created,
                              'user_last_login': user_last_login})
    # export csv
    user_data.to_csv('user_data_{}.csv'.format(str(datetime.today())[:10]), index = False)
    return user_data


###############################################################################
# get meeting meta data
###############################################################################

def meeting_meta_data(meeting_id):
    """
    

    Parameters
    ----------
    meeting_id : string
        numerical meeting id

    Returns
    -------
    meeting : dataframe
        meeting meta data

    """    
    url = 'https://api.zoom.us/v2/meetings/{}'.format(meeting_id)
    #load headers
    headers = { 'authorization': "Bearer {}".format(get_token(token = True))}
    m = requests.get(url, headers = headers)
    m_meta = m.json()

    
    # create lists
    id = []
    created_at = []
    started_at = []
    end_date_time = []
    join_url = []
    topic = []
    status = []
    host_id = []
    join_before_host = []
    waiting_room = []
    auto_recording = []
    meeting_authentication = []
    repeat_interval = []
    repeated_days = []
    repeated_type = []
    occurrences = []
    
    if m_meta.get('occurrences'):
            # append to list
        id.append(m_meta['id'])
        created_at.append(m_meta['created_at'])
        started_at.append(m_meta['occurrences'][0]['start_time'])
        end_date_time.append(m_meta['recurrence']['end_date_time'])
        join_url.append(m_meta['join_url'])
        topic.append(m_meta['topic'])
        status.append(m_meta['status'])
        host_id.append(m_meta['host_id'])
        join_before_host.append(m_meta['settings']['join_before_host'])
        waiting_room.append(m_meta['settings']['waiting_room'])
        auto_recording.append(m_meta['settings']['auto_recording'])
        meeting_authentication.append(m_meta['settings']['meeting_authentication'])
        occurrences.append(len(m_meta['occurrences']))
        repeat_interval.append(m_meta['recurrence']['repeat_interval'])
        repeated_days.append(m_meta['recurrence']['weekly_days'])
        repeated_type.append(m_meta['recurrence']['type'])
        
    else:
        id.append(m_meta['id'])
        created_at.append(m_meta['created_at'])
        started_at.append('NoStartTime')
        end_date_time.append('NoEndTime')
        join_url.append(m_meta['join_url'])
        topic.append(m_meta['topic'])
        status.append(m_meta['status'])
        host_id.append(m_meta['host_id'])
        join_before_host.append(m_meta['settings']['join_before_host'])
        waiting_room.append(m_meta['settings']['waiting_room'])
        auto_recording.append(m_meta['settings']['auto_recording'])
        meeting_authentication.append(m_meta['settings']['meeting_authentication'])
        occurrences.append('NoOccurences')
        repeat_interval.append('NoInterval')
        repeated_days.append('NoRepeatedDays')
        repeated_type.append('NoType')

    

    
    #create a data frame
    meeting = pd.DataFrame({'meeting_id':id,
                            'meeting_created_at':created_at,
                            'meeting_started_at':started_at,
                            'meeting_ended_at':end_date_time,
                            'meeting_url':join_url,
                            'meeting_topic':topic,
                            'meeting_status':status,
                            'meeting_host_id':host_id,
                            'meeting_pre_join':join_before_host,
                            'meeting_waiting_room':waiting_room,
                            'meeting_auto_recording':auto_recording,
                            'meeting_required_hawkid':meeting_authentication,
                            'meeting_total_occurrences':occurrences,
                            'meeting_repeat_interval':repeat_interval,
                            'meeting_days':repeated_days,
                            'meeting_repeat_type':repeated_type})
    return meeting


###############################################################################
# get meeting participants from report
###############################################################################
# duration, join time, left time, email maybe different from dashboard
# missing some speaker or info. 

def get_meeting_participants_report(muuid):
    """
    
    Parameters
    ----------
    muuid : string
        meeting uuid

    Returns
    -------
    data : dataframe
        user information associated to the meetings. 

    """
# if uuid starts with '/' or '//', quote 2 times
    if muuid[0] == '/' or '//' in muuid:
        k = quote(quote(muuid, safe=""), safe="")
        print(k)
        print('Weird UUID with / or // as the start')
        print('')
        print('Pay attention!!!!')
        print('')
    else:
            k = muuid    

# get data
    headers = { 'authorization': "Bearer {}".format(get_token(token = True))}
    meeting_url = 'https://api.zoom.us/v2/report/meetings/{}/participants?type=past&page_size=300'.format(k)
       
    initial_meeting = requests.get(meeting_url, headers = headers)
    data = []
    total = initial_meeting.json()['total_records']
    while True:
        raw = json.loads(initial_meeting.text)
        for i in raw['participants']:
            data.append(i)
        try:
            raw['next_page_token'] != ''
            new_link = 'https://api.zoom.us/v2/report/meetings/{}/participants?type=past&page_size=300&next_page_token={}'.format(k, raw['next_page_token'])
            new_meeting = requests.get(new_link, headers = headers)
            initial_meeting = new_meeting
        except KeyError:
            break  
        
        if len(data) == total:
            print('total records = {}. We have {}'.format(total, len(data)))
            k = 2 * 10 - 2  # It is used for number of spaces  
            for i in range(0, 10):  
                for j in range(0, k):  
                    print(end=" ")  
                k = k - 2   # decrement k value after each iteration  
                for j in range(0, i + 1):  
                    print("* ", end="")  # printing star  
                print("")  
            break
        
# reassign
    meeting_data = data
    
    # create lists 
    user_zoom_id = []
    user_id = []
    user_name = []
    email = []
    join_time = []
    left_time = []
    duration = []

#every for loop to determine whether there is data associated to the variable.
# if True, yes, else, assigned value. 

    for info in meeting_data:
        if info.get('user_email'):
            user_zoom_id.append(info['id'])
            user_id.append(info['user_id'])
            user_name.append(info['name'])
            email.append(info['user_email'])
            join_time.append(info['join_time'])
            left_time.append(info['leave_time'])
            duration.append(info['duration'])
            
        if not info.get('user_email'):
            user_zoom_id.append(info['id'])
            user_id.append(info['user_id'])
            user_name.append(info['name'])
            email.append('NoEmail')
            join_time.append(info['join_time'])
            left_time.append(info['leave_time'])
            duration.append(info['duration'])
        
    data = pd.DataFrame({'user_zoom_id':user_zoom_id,
                         'user_id':user_id,
                         'user_name':user_name,
                         'user_email': email,
                         'user_join_time':join_time,
                         'user_left_time':left_time,
                         'user_attendance_duration':duration})
    

    data['meeting_uuid'] = muuid
    return data

###############################################################################
# convert time to local time
###############################################################################


def time_conversion(dataframe):
    df = dataframe.copy()
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    for i in range(len(df)):
        print(i)
        ms = df.meeting_start_time[i]
        me = df.meeting_end_time[i]
        uj = df.user_join_time[i]
        ul = df.user_left_time[i]
        utc_ms= datetime.strptime(ms, '%Y-%m-%dT%H:%M:%SZ')
        utc_me= datetime.strptime(me, '%Y-%m-%dT%H:%M:%SZ')
        utc_uj= datetime.strptime(uj, '%Y-%m-%dT%H:%M:%SZ')
        utc_ul= datetime.strptime(ul, '%Y-%m-%dT%H:%M:%SZ')
        c_ms = utc_ms.replace(tzinfo=from_zone).astimezone(to_zone)
        c_me = utc_me.replace(tzinfo=from_zone).astimezone(to_zone)
        c_uj = utc_uj.replace(tzinfo=from_zone).astimezone(to_zone)
        c_ul = utc_ul.replace(tzinfo=from_zone).astimezone(to_zone)
        df.meeting_start_time[i] = c_ms
        df.meeting_end_time[i] = c_me
        df.user_join_time[i] = c_uj
        df.user_left_time[i] = c_ul
    return df

###############################################################################
# matching emails
###############################################################################



def matching_emails(uuid):
    """

    Parameters
    ----------
    uuid : string
        Unique meeting id for each meeting.

    Returns
    -------
    dashboard : dataframe
        matching emails

    """

    report = get_meeting_participants_report(uuid)
    dashboard = get_meeting_participants_dashboard(uuid)
    for i in range(len(report)):
        for j in range(len(dashboard)):
            if report.user_name[i] == dashboard.user_name[j] and report.user_id[i] == dashboard.user_id[j]:
                dashboard.user_email[j] = report.user_email[i]
    return dashboard




###############################################################################
# save tokens
###############################################################################


def save_token(token, location):
    text_file = open(f'{location}', 'w')
    text_file.write(token)
    text_file.close()
    print('Zoom folder Token has been saved')

###############################################################################
# refresh_token
###############################################################################

b64 = pickle.load(open('b64.pickle', 'rb'))
        
def refresh_token(refreshtoken):
    # header with cliend id and client pass
    h = {"Authorization": "Basic {}".format(b64)}
    # refresh url
    refresh_url = 'https://zoom.us/oauth/token?grant_type=refresh_token&refresh_token={}'.format(refreshtoken)
    # get a new token   
    get_new_token = requests.post(refresh_url, headers = h)
    tokens = get_new_token.text
    return tokens



###############################################################################
# meeting time conversion
###############################################################################



def meeting_time_conversion(dataframe):
    df = dataframe.copy()
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    for i in range(len(df)):
        print(i)
        ms = df.meeting_start_time[i]
        me = df.meeting_end_time[i]
        utc_ms= datetime.strptime(ms, '%Y-%m-%dT%H:%M:%SZ')
        utc_me= datetime.strptime(me, '%Y-%m-%dT%H:%M:%SZ')
        c_ms = utc_ms.replace(tzinfo=from_zone).astimezone(to_zone)
        c_me = utc_me.replace(tzinfo=from_zone).astimezone(to_zone)
        df.meeting_start_time[i] = c_ms.replace(tzinfo=None)
        df.meeting_end_time[i] = c_me.replace(tzinfo=None)
    return df


###############################################################################
# user time conversion
###############################################################################



def user_time_conversion(dataframe):
    df = dataframe.copy()
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    for i in range(len(df)):
        print(i)
        uj = df.user_join_time[i]
        ul = df.user_left_time[i]
        utc_uj= datetime.strptime(uj, '%Y-%m-%dT%H:%M:%SZ')
        utc_ul= datetime.strptime(ul, '%Y-%m-%dT%H:%M:%SZ')
        c_uj = utc_uj.replace(tzinfo=from_zone).astimezone(to_zone)
        c_ul = utc_ul.replace(tzinfo=from_zone).astimezone(to_zone)
        df.user_join_time[i] = c_uj.replace(tzinfo=None)
        df.user_left_time[i] = c_ul.replace(tzinfo=None)
    return df


###############################################################################
# zoom user engagement
###############################################################################

def engagement(temp_meeting):
  
    end_time = datetime.strptime(temp_meeting.meeting_end_time[0][:19], '%Y-%m-%d %H:%M:%S')
    start_time = datetime.strptime(temp_meeting.meeting_start_time[0][:19], '%Y-%m-%d %H:%M:%S')
    difference = end_time - start_time
    # get the total seconds
    temp_meeting['meeting_length'] = difference.total_seconds()
    # reduce the columns 
    temp_meeting_use = temp_meeting[['meeting_uuid', 'meeting_start_time', 'meeting_end_time',
                                     'meeting_length', 'meeting_host_email', 'user_email', 'user_join_time',
                                     'user_left_time', 'user_attendance_duration', 'user_leave_reason']]
    
    
    # lower case all the emails
    temp_meeting_use.meeting_host_email = temp_meeting_use.meeting_host_email.str.lower()
    temp_meeting_use.user_email = temp_meeting_use.user_email.str.lower()
    # get the host email
    host = temp_meeting_use.meeting_host_email[0]
    # create a column for identifying the host
    temp_meeting_use['host'] = np.nan
    # convert to array
    temp_array = temp_meeting_use.to_numpy()
    # identify host of the meeting
    for i in range(len(temp_array)):
        if temp_array[i][5] == host:
            temp_array[i][10] = 'yes'
        else:
            temp_array[i][10] = 'no'
    temp_meetings = pd.DataFrame(temp_array, columns = temp_meeting_use.columns)
    # keep non host users
    temp_meeting_users = temp_meetings[temp_meetings.host == 'no']
    if len(temp_meeting_users) != 0:
        # get aggregated duration
        users = temp_meeting_users.groupby('user_email')['user_attendance_duration'].sum().reset_index()
        counts = temp_meeting_users.groupby('user_email')['user_attendance_duration'].count().reset_index()
        users = pd.merge(users, counts, on = 'user_email')
        users.columns = ['user_email', 'agg_duration', 'agg_activities']
        # combine original to aggregated duration
        # outer join = keep all records for time selection
        agg_users = pd.merge(temp_meeting_users, users, how = 'outer')
        
        # get the earilest join time
        start_full = agg_users.sort_values('user_join_time').drop_duplicates(subset = 'user_email', keep = 'first')
        start = start_full[['user_email', 'user_join_time']]
        # get the latest end time
        end_full = agg_users.sort_values('user_left_time').drop_duplicates(subset = 'user_email', keep = 'last')
        end = end_full[['user_email', 'user_left_time']]
        # create user time with earlies and latest time
        user_time = pd.merge(start, end)
        user_time.columns = ['user_email', 'join_time', 'leave_time']
        # merge back to the orginal set
        new_agg_users = pd.merge(agg_users, user_time)
        # keep unique users
        final_agg_users = new_agg_users.drop_duplicates(subset = 'user_email').reset_index(drop = True)
        # remove some duplicated columns
        final_agg_users = final_agg_users[['meeting_uuid', 'meeting_start_time', 'meeting_end_time',
                                           'meeting_length', 'meeting_host_email', 'user_email', 
                                           'user_leave_reason', 'agg_duration', 'join_time', 'leave_time',
                                           'agg_activities']]
        
        # calculate meeting percent
        final_agg_users['meeting_percent'] = round(final_agg_users.agg_duration / temp_meeting.meeting_length, 4)
        
        #get meeting early or late
        end_time = datetime.strptime(final_agg_users.meeting_end_time[0][:19], '%Y-%m-%d %H:%M:%S')
        start_time = datetime.strptime(final_agg_users.meeting_start_time[0][:19], '%Y-%m-%d %H:%M:%S')
        
        # create engaged, join and leave variables
        final_agg_users['engaged'] = np.nan 
        final_agg_users['join_late'] = np.nan
        final_agg_users['leave_early'] = np.nan
        
        # convert to array for fast speed
        final_agg_array = final_agg_users.to_numpy()
        
        # get the average late join time and early leave time
        class_late_join = []
        class_early_leave = []
        for i in range(len(final_agg_array)):
            user_join_time = datetime.strptime(final_agg_array[i][8][:19], '%Y-%m-%d %H:%M:%S')
            user_leave_time = datetime.strptime(final_agg_array[i][9][:19], '%Y-%m-%d %H:%M:%S')
            # append a list
            class_late_join.append((user_join_time - start_time).total_seconds())
            class_early_leave.append((end_time - user_leave_time).total_seconds())
        
        # calculate the mean for join time and leave time   
        mean_late_join = sum(class_late_join)/len(class_late_join)
        mean_early_leave = sum(class_early_leave)/len(class_early_leave)
        
        for i in range(len(final_agg_array)):
            user_join_time = datetime.strptime(final_agg_array[i][8][:19], '%Y-%m-%d %H:%M:%S')
            user_leave_time = datetime.strptime(final_agg_array[i][9][:19], '%Y-%m-%d %H:%M:%S')
            # calculate difference
            if (((user_join_time - start_time).total_seconds()) > mean_late_join):
                final_agg_array[i][13] = 'late'
            if (mean_early_leave < ((end_time - user_leave_time).total_seconds())):
                final_agg_array[i][14] = 'early'
            if final_agg_array[i][11] > 0.7:
                final_agg_array[i][12] = 'engaged'
        
        # create back dataframe
        result = pd.DataFrame(final_agg_array, columns = final_agg_users.columns)
        # fillna with no
        result = result.fillna('no')
        return result
