# -*- coding: utf-8 -*-

import json
import datetime
import resources.httplib2 as httplib2
import urllib


class CalendarManager:

    def __init__(self, auth_token, api_key):
        self.token = auth_token
        self.api_key = api_key
        self.calendar_colors = {}
        self.event_colors = {}

    def get_calendars(self):
        """Devuelve un json con una lista de calendarios.

        json:
        {
            "calendarios":  [
                                {
                                    "id": value,
                                    "summary": value (nombre)
                                },
                                {
                                    "id": value,
                                    "summary": value (nombre)
                                },
                                ...
                            ]
        }
        """
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

    def get_calendars_and_events(self, calendar_list):
        """Devuelve un json con información acerca de cada uno de los calendarios correspondientes
        a los ids pasados. Por cada calendario se devuelve su nombre, color y lista de eventos futuros.

        json:
        {
            "calendarios":  [
                                {
                                    "summary": value (nombre),
                                    "description": value
                                    "color": value (hex),
                                    "events":   [
                                                   {
                                                        "summary": value (nombre),
                                                        "start": value,
                                                        "location": {
                                                                        "address": value,
                                                                        "lat": value,
                                                                        "lng": value
                                                                    }
                                                    },
                                                    {
                                                        "summary": value (nombre),
                                                        "start": value,
                                                        ...
                                                    },
                                                    ...
                                                ]
                                },
                                ...
                            ]
        }
        """
        calendars = []

        main_uri = 'https://www.googleapis.com/calendar/v3/users/me/calendarList/'
        method = 'GET'
        headers = {'User-Agent': 'Python Client',
                   'Authorization': 'Bearer ' + self.token}

        if not self.calendar_colors:
            self._get_color_map()

        for id in calendar_list:
            uri = main_uri + urllib.quote(id)
            conn = httplib2.Http()
            response, body = conn.request(uri, method=method, headers=headers)

            json_response = json.loads(body)
            tmp_calendar = {'summary': json_response['summary'],
                            'color': self.calendar_colors[json_response['colorId']]['background'],
                            'events': self._get_events(id)['eventos']}
            if 'description' in json_response:
                description = json_response['description']
            else:
                description = ''
            tmp_calendar['description'] = description
            calendars.append(tmp_calendar)

        return {'calendarios': calendars}

    def _get_events(self, calendar_id, time_min=datetime.datetime.utcnow(), months=6):
        """Devuelve un json con la lista de eventos pertenecientes al calendario con id calendar_id.

        time_min se utiliza para indicar la fecha mínima de finalización que deben tener los eventos.
        Cualquier evento que termine antes de la fecha time_min no será incluido en el resultado.
        Valor por defecto de time_min: fecha actual. Para no filtrar por fecha, pasar time_min como None.

        months, en caso de que time_min != None, indica el número de meses después de time_min en los
        que recogerán los eventos. Cualquier evento que termine month meses después de time_min
        no será incluido en el resultado.

        json:
        {
            "eventos":  [
                            {
                                "summary": value (nombre),
                                "start": value,
                                "location": value,
                            },
                            {
                                "summary": value (nombre),
                                "start": value,
                                "location": value,
                            },
                            ...
                        ]
        }
        """
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
                tmp_event['location'] = self._get_coordinates(event['location'])
            else:
                tmp_event['location'] = ''

            event_list.append(tmp_event)

        return {"eventos": event_list}

    def _get_color_map(self):
        uri = 'https://www.googleapis.com/calendar/v3/colors'
        method = 'GET'
        headers = {'User-Agent': 'Python Client',
                   'Authorization': 'Bearer ' + self.token}

        conn = httplib2.Http()
        response, body = conn.request(uri, method=method, headers=headers)

        json_response = json.loads(body)
        if 'calendar' in json_response:
            self.calendar_colors = json_response['calendar']
        if 'event' in json_response:
            self.event_colors = json_response['event']

    def _get_coordinates(self, address):
        """Devuelve un diccionario con la longitud y latitud de la dirección dada.

        formato:
        {
            "address": value,
            "lat": value (latitud),
            "lng": value (longitud)
        }
        """
        uri = 'https://maps.googleapis.com/maps/api/geocode/json'
        method = 'GET'
        lang = 'language=' + urllib.quote('es')
        key = 'key=' + urllib.quote(self.api_key)
        addr = 'address=' + urllib.quote(address.encode('utf8'))
        param = key + '&' + addr + '&' + lang

        conn = httplib2.Http()
        response, body = conn.request(uri + '?' + param, method=method)

        json_response = json.loads(body)
        try:
            obj = json_response['results'][0]['geometry']
            address_json = {'address': address,
                            'lat': obj['location']['lat'],
                            'lng': obj['location']['lng']}
        except KeyError:
            address_json = {'address': address,
                            'lat': '',
                            'lng': ''}

        return address_json
