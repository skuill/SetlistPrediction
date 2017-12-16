
from musicbrainz import Artist
try:
	import ujson as json
except:
	import json
import requests
import pandas as pd
import math

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

    def get_artist_events(self, artist, events_count=None):
        # Call Setlist.fm API
        url = 'https://api.setlist.fm/rest/1.0/artist/' + artist._mbid + '/setlists?p=1'
        headers = {'Accept': 'application/json', 'x-api-key': self._api_key}
        r = requests.get(url, headers=headers)	
        # Get .json Data
        data = r.json()
        # Get total number of shows
        total_events = int(data['total'])
        if (events_count is not None):
            if (total_events < events_count):
                events_count = total_events
        else: 
            events_count = total_events
        # Total Number of Pages needed to load
        pages_count = math.ceil(events_count/20)
        result_events_df = pd.DataFrame(columns = self._events_columns)
        processed_events = 0
        for page in range(pages_count):
            url = 'https://api.setlist.fm/rest/1.0/artist/' + artist._mbid + '/setlists?p=' + str(page+1)
            headers = {'Accept': 'application/json', 'x-api-key': self._api_key}
            r = requests.get(url, headers=headers)	
            # Get .json Data
            data = r.json()
            #print (data)
            # Read .json file line per line
            for i in range(len(data['setlist'])):
                if (processed_events == events_count):
                    break
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
                        }, ignore_index=True)
                processed_events += 1
        result_events_df['eventdate'] = pd.to_datetime(result_events_df['eventdate'], format='%d-%m-%Y')
        return result_events_df.sort_values(by=['eventdate'], ascending=False)