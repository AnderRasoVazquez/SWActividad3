import json
import resources.httplib2 as httplib2


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
