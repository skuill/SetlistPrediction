
from musicbrainz import Artist

try:
	import ujson as json
except:
	import json

import requests
import pandas as pd

class SetlistGetter:
    _events_columns = ['eventID',
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
    
    def get_artist_events(self, artist, pages_count = 1):
        # Call Setlist.fm API
        url = 'https://api.setlist.fm/rest/1.0/artist/' + artist._mbid + '/setlists?p=1'
        headers = {'Accept': 'application/json', 'x-api-key': self._api_key}
        r = requests.get(url, headers=headers)	
        # Get .json Data
        data = r.json()
        # Get total number of shows
        totalshows = int(data['total'])
        # Total Number of Pages needed to load
        pages_exists = int(totalshows/20)
        if (pages_exists < pages_count):
            pages = pages_exists
        else:
            pages = pages_count
        result_events_df = pd.DataFrame(columns = self._events_columns)
        for page in range(1,pages):
            url = 'https://api.setlist.fm/rest/1.0/artist/' + artist._mbid + '/setlists?p=' + str(page)
            headers = {'Accept': 'application/json', 'x-api-key': self._api_key}
            r = requests.get(url, headers=headers)	
    		  # Get .json Data
            data = r.json()
            #print (data)
    		  # Read .json file line per line
            for line in data:
                for i in range(len(data['setlist'])):
                    tourName = ''
                    tour = data['setlist'][i].get('tour')
                    if tour is not None:
                        tourName = tour['name']
                    result_events_df = result_events_df.append(
				                {
				                # Event ID
				                'eventID': str(data['setlist'][i]['id']),
				                # Artist
				                'artist': str(data['setlist'][i]['artist']['name']),
				                # Eventdate
				                'eventdate': str(data['setlist'][i]['eventDate']),
				                # TourName
				                'tourname': tourName,
				                # Venue
				                'venue': str(data['setlist'][i]['venue'].get('name')),
				                # Venue ID
				                'venue_id': str(data['setlist'][i]['venue'].get('id')),
				                # City
				                'city': str(data['setlist'][i]['venue']['city'].get('name')),
				                # City ID
				                'city_id': str(data['setlist'][i]['venue']['city'].get('id')),
				                # City Latitude
				                'city_lat': float(data['setlist'][i]['venue']['city']['coords'].get('lat')),
				                # City Longitude
				                'city_lon': float(data['setlist'][i]['venue']['city']['coords'].get('long')),
				                # State
				                'state': str(data['setlist'][i]['venue']['city'].get('state')),
				                # State Code
				                'state_id': str(data['setlist'][i]['venue']['city'].get('stateCode')),
				                # Country
				                'country': str(data['setlist'][i]['venue']['city']['country'].get('name')),
				                # Country Code
				                'country_id': str(data['setlist'][i]['venue']['city']['country'].get('code'))
				                }, ignore_index=True
				                )
        return result_events_df