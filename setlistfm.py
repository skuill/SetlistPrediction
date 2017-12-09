
from musicbrainz import Artist

try:
	import ujson as json
except:
	import json

import requests
import csv
import sys

class SetlistGetter:
    columns = ['eventID',
	                'artist',
	                'eventdate',
	                'tourname',
	                'venue',
	                'venue_id',
	                'city',
	                'city_id',
	                'city_lat',
	                'city_lon',
	                'state',
	                'state_id',
	                'country',
	                'country_id']
    
    def __init__(self, api_key):
        self._api_key = api_key
    