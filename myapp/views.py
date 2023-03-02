from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.views import View
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json


class GoogleCalendarInitView(View):
    def get(self, request, *args, **kwargs):
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=[
                'https://www.googleapis.com/auth/calendar.readonly',
        
              'https://www.googleapis.com/auth/calendar.events'
            ],
            redirect_uri=
            'https://PrimaryTurquoiseRecords.rajneeshkhare.repl.co/accounts/google/login/callback/'
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true')
        request.session['google_calendar_state'] = state
        return HttpResponseRedirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request, *args, **kwargs):
        state = request.GET.get('state')
        if state != request.session.get('google_calendar_state'):
            return JsonResponse({'error': 'Invalid state parameter'},
                                status=400)

        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=[
                'https://www.googleapis.com/auth/calendar.readonly',
              'https://www.googleapis.com/auth/calendar.events'
            ],
            redirect_uri=
            'https://PrimaryTurquoiseRecords.rajneeshkhare.repl.co/accounts/google/login/callback/'
        )
        flow.fetch_token(authorization_response=request.build_absolute_uri(),
                         state=state)
        credentials = flow.credentials
        request.session['google_calendar_credentials'] = credentials.to_json()
        return HttpResponseRedirect(reverse('google-calendar-events'))


class GoogleCalendarEventsView(View):
    def get(self, request, *args, **kwargs):

        json_string = request.session.get('google_calendar_credentials')
        credentials_info = json.loads(json_string)
        credentials = Credentials.from_authorized_user_info(
            info=credentials_info)
        service = build('calendar', 'v3', credentials=credentials, static_discovery=False)
        events_result = service.events().list(calendarId='primary',
                                              maxResults=10,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        return JsonResponse({'events': events})


def home(response):
    return render(response, "myapp/home.html")
