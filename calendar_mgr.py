import json
import datetime
import resources.httplib2 as httplib2
import urllib


class CalendarManager:

    def __init__(self, auth_token):
        self.token = auth_token

    def get_calendars(self):
        uri = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
        method = 'GET'
        headers = {'User-Agent': 'Python Client',
                   'Authorization': 'Bearer ' + self.token}

        conn = httplib2.Http()
        response, body = conn.request(uri, method=method, headers=headers)

        json_response = json.loads(body)
        calendar_list = []
        for calendar in json_response['items']:
            calendar_list.append({'id': calendar['id'], 'summary': calendar['summary']})

        return {"calendarios": calendar_list}

    def get_events(self, calendar_id, time_min=datetime.datetime.utcnow(), months=6):
        uri = 'https://www.googleapis.com/calendar/v3/calendars/' + urllib.quote(calendar_id) + '/events'
        method = 'GET'
        headers = {'User-Agent': 'Python Client',
                   'Authorization': 'Bearer ' + self.token}
        if time_min is not None:
            time_max = time_min + datetime.timedelta(30*months)
            time_min_param = 'timeMin=' + urllib.quote(time_min.isoformat('T') + '+00:00')
            time_max_param = 'timeMax=' + urllib.quote(time_max.isoformat('T') + '+00:00')
            param = time_min_param + '&' + time_max_param
        else:
            param = ''

        conn = httplib2.Http()
        response, body = conn.request(uri + '?' + param,
                                      method=method, headers=headers)

        json_response = json.loads(body)
        return json_response['items']
        # event_list = []
        # try:
        #     for event in json_response['items']:
        #         new_event = {}
        #         keys = ['id', 'summary', 'description', 'start', 'end', 'location']
        #         for key in keys:
        #             if key in event:
        #                 new_event[key] = event[key]
        #             else:
        #                 new_event[key] = ''
        #         keys = ['start', 'end']
        #         for key in keys:
        #             if key in event and 'date' in event[key]:
        #                 new_event[key] = event[key]['date']
        #             else:
        #                 new_event[key] = ''
        #         event_list.append(new_event)
        #     return event_list
        # except KeyError:
        #     return []
