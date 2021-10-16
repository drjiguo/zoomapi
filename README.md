Zoom API

This is particularly useful for those who conduct learning analytics research. 

In this file, with token, you will be able to pull data from zoom API. 

Here are the functions you can use:

1. get_tokens() -- use this token to read and refresh to zoom api token. 
2. save_token(token, location) -- save token to the target location. 
3. refresh_token(refreshtoken) -- refresh the zoom token
4. get_meeting_daily_reports(year, month) -- use this function to get the report for a specfic month of the year. 
5. meeting_meta_data(meeting_id) -- use the numeric meeting ids to get the meta data of the meeting.
6. get_meeting_history(meeting_id) -- use the numeric meeting ids, like 9254128951, as string to get all the unique meeting instances under this meeting id.  
7. get_meeting_participants_dashboard(muuid) -- use unique meeting instances to get the participation. 
8. get_meeting_participants_report(muuid) -- use unique meeting instances to get the participation (the data might be different from the dashboard data)
9. get_all_zoom_users() -- use this one to get the all active and inactive zoom users. 
10. user_time_conversion(dataframe) -- convert UTC time to local time for zoom user part. 
11. meeting_time_conversion(dataframe) -- convert UTC time to local time for zoom meeting part. 


