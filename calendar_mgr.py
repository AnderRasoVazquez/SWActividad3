# -*- coding: utf-8 -*-

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
        event_list = []
        for event in json_response['items']:
            tmp_event = {}

            if 'summary' in event:
                tmp_event['summary'] = event['summary']
            else:
                tmp_event['summary'] = '(Sin título)'

            if 'date' in event['start']:
                # evento de día completo (festivos, etc.)
                tmp_event['start'] = event['start']['date']
            elif 'dateTime' in event['start']:
                # con hora de comienzo
                # nos quedamos con los 10 primeros caracteres (yyyy-mm-dd)
                tmp_event['start'] = event['start']['dateTime'][0:11]
            else:
                tmp_event['start'] = ''

            if 'location' in event:
                # TODO: encontrar forma de pasar a coordenadas
                tmp_event['location'] = event['location']
            else:
                tmp_event['location'] = ''

            event_list.append(tmp_event)

        return {"eventos": event_list}
