import json
from typing import Dict, List, Literal
import requests

from py_optional import Optional

URL_TRENDS_MAIN = "https://trends.google.com/?geo={}"
URL_EXPLORE = "https://trends.google.com/trends/api/explore"
URL_WIDGET_DATA_MULTILINE = "https://trends.google.com/trends/api/widgetdata/multiline"


TOKEN_EXTRACT_METHODS = {
    'interest_over_time': lambda widget: Optional.of(widget)
    .filter(lambda w: w['id'] == 'TIMESERIES')
    .or_else(None),

    'interest_by_region': lambda widget: Optional.of(widget)
    .filter(lambda w: w['id'] == 'GEO_MAP')
    .or_else(None),

    'related_topics': lambda widget: Optional.of(widget)
    .filter(lambda w: 'RELATED_TOPICS' in w['id'])
    .or_else(None),

    'related_queries': lambda widget: Optional.of(widget)
    .filter(lambda w: 'RELATED_QUERIES' in w['id'])
    .or_else(None),
}


class TimeRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def to_google_format(self):
        return "{} {}".format(self.start.strftime("%Y-%m-%d"), self.end.strftime("%Y-%m-%d"))


class GoogleTrendRequest:
    def __init__(self):
        self._payload = {}
        self._widgets = {}

    def _get_cookie(self, session: requests.Session) -> None:
        assert self._payload['hl'] is not None

        response = session.get(
            URL_TRENDS_MAIN.format(self._payload['hl'][-2:]))
        assert response.status_code == 200, response.text + \
            '\n' + str(response.status_code)

    def _get_token(self, session: requests.Session) -> None:
        assert self._payload['hl'] is not None
        assert self._payload['tz'] is not None
        assert self._payload['req'] is not None

        session.headers.update({'accept-language': self._payload['hl'],
                                'content-type': 'application/json',
                                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
                                })

        self._get_cookie(session)

        response = session.get(URL_EXPLORE,
                               params=self._payload)
        assert response.status_code == 200, response.text + \
            '\n' + str(response.status_code)

        text = response.text[4:]
        data = json.loads(text)

        self._widgets.clear()
        for widget in data['widgets']:
            for name, fn in TOKEN_EXTRACT_METHODS.items():
                if fn(widget) is not None:
                    self._widgets[name] = widget
                    continue

    def interest_over_time(self, session: requests.Session) -> requests.Response:
        self._get_token(session)
        assert self._widgets['interest_over_time'] is not None

        widget = self._widgets['interest_over_time']
        payload = {
            'req': json.dumps(widget['request']),
            'token': widget['token'],
            'tz': self._payload['tz'],
        }

        response = session.get(URL_WIDGET_DATA_MULTILINE, params=payload)
        assert response.status_code == 200, response.text + \
            '\n' + str(response.status_code)

        data = json.loads(response.text[5:])

        default = data['default']
        timelineData = default['timelineData']
        for each in timelineData:
            yield int(each['time']), each['value']


class GoogleTrendRequestBuilder:
    def __init__(self):
        self._hl = "en-US"
        self._tz = 360
        self._geo = ""
        self._keywords = []
        self._time_range = None
        self._category = 0
        self._property = ""

        self._request = GoogleTrendRequest()

    def language(self, lang: str = 'en-US'):
        self._request._hl = lang
        return self

    def geographic(self, geo: str = 'US'):
        self._request._geo = geo
        return self

    def time_zone(self, tz: int = 360):
        self._request._tz = tz
        return self

    def intent(self,
               keywords: List[str],
               time_range: TimeRange,
               category: int = 0,
               property: Literal['', 'images', 'news', 'youtube', 'froogle'] = '') -> GoogleTrendRequest:

        self._keywords = keywords
        self._time_range = time_range
        self._category = category
        self._property = property

        return self

    def build(self) -> GoogleTrendRequest:
        self._request._payload['hl'] = self._hl
        self._request._payload['tz'] = self._tz
        self._request._payload['req'] = {}
        self._request._payload['req']['comparisonItem'] = [{'keyword': k,
                                                            'time': self._time_range.to_google_format(),
                                                            'geo': self._geo} for k in self._keywords]
        self._request._payload['req']['category'] = self._category
        self._request._payload['req']['property'] = self._property
        self._request._payload['req'] = json.dumps(
            self._request._payload['req'])

        return self._request
