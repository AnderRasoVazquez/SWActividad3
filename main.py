# -*- coding: utf-8 -*-

import httplib
from resources import httplib2 as httplib2
import urllib
import json
import logging
import webapp2
from webapp2_extras import sessions
import jinja2
import os

from calendar_mgr import CalendarManager


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'html')),
    extensions=['jinja2.ext.autoescape', 'jinja2.ext.loopcontrols'],
    autoescape=True)


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template("index.html")
        data = {}
        self.response.out.write(template.render(data))


cliente_id = '598778698756-8d90gr52eqgnn5lv90loa5dookra7k0a.apps.googleusercontent.com'
cliente_secret = 'VAUirY5cDs7EtM4NuibNMry3'
api_key = 'AIzaSyBK8NhJ7xM9D12RFRb-krQpMtc06b4nWE0'
redirect_uri = 'http://swactividad3.appspot.com/callback_uri'
config = {'webapp2_extras.sessions': {'secret_key': 'my-super-secret-key'}}


class LoginAndAuthorize(BaseHandler):
    def get(self):
        servidor = 'accounts.google.com'
        conn = httplib.HTTPSConnection(servidor)
        conn.connect()
        params = {'client_id': cliente_id,
                  'redirect_uri': redirect_uri,
                  'response_type': 'code',
                  'scope': 'https://www.googleapis.com/auth/calendar',
                  'approval_prompt': 'auto',
                  'access_type': 'offline'}
        params_coded = urllib.urlencode(params)
        uri = '/o/oauth2/v2/auth' + '?' + params_coded
        self.redirect('https://' + servidor + uri)

        logging.debug(params)


class OAuthHandler(BaseHandler):
    def get(self):
        servidor = 'accounts.google.com'
        metodo = 'POST'
        uri = '/o/oauth2/token'
        auth_code = self.request.get('code')
        params = {'code': auth_code,
                  'client_id': cliente_id,
                  'client_secret': cliente_secret,
                  'redirect_uri': redirect_uri,
                  'grant_type': 'authorization_code'}
        params_encoded = urllib.urlencode(params)
        cabeceras = {'Host': servidor,
                     'User-Agent': 'Python bezeroa',
                     'Content-Type': 'application/x-www-form-urlencoded',
                     'Content-Length': str(len(params_encoded))}
        http = httplib2.Http()
        respuesta, cuerpo = http.request('https://' + servidor + uri, method=metodo, headers=cabeceras,
                                         body=params_encoded)

        json_cuerpo = json.loads(cuerpo)

        access_token = json_cuerpo['access_token']
        self.session['access_token'] = access_token
        self.redirect('/calendars')


class CalendarHandler(BaseHandler):
    def get(self):
        calendar_mgr = CalendarManager(self.session['access_token'], api_key)
        data = calendar_mgr.get_calendars()
        template = JINJA_ENVIRONMENT.get_template("calendarios.html")
        self.response.out.write(template.render(data))


class EventHandler(BaseHandler):
    def get(self):
        self.redirect("/")

    def post(self):
        calendars = self.request.get('calendarios[]', allow_multiple=True)
        calendar_mgr = CalendarManager(self.session['access_token'], api_key)
        data = calendar_mgr.get_calendars_and_events(calendars)
        template = JINJA_ENVIRONMENT.get_template("eventos.html")
        self.response.out.write(template.render(data))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/login', LoginAndAuthorize),
    ('/callback_uri', OAuthHandler),
    ('/calendars', CalendarHandler),
    ('/events', EventHandler)
], config=config, debug=True)
