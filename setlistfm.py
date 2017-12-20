
from musicbrainz import Artist
try:
	import ujson as json
except:
	import json
import requests
import pandas as pd
import math

class SetlistGetter:
    _events_columns = ['event_id',
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
    _set_columns = ['event_id',
                    'song_num',
                    'name',
                    'encore',
                    'tape',
                    'info',
                    ]

    def __init__(self, api_key):
        self._api_key = api_key

    def parse_events_dictionary(self, events_dictionary):
        result_events_df = pd.DataFrame(columns = self._events_columns)
        tourName = ''
        tour = events_dictionary.get('tour')
        if tour is not None:
            tourName = tour['name']
        result_events_df = result_events_df.append(
            {
                # Event ID
                'event_id': str(events_dictionary['id']),
                # Artist
                'artist': str(events_dictionary['artist']['name']),
                # Eventdate
                'eventdate': str(events_dictionary['eventDate']),
                # TourName
                'tourname': tourName,
                # Venue
                'venue': str(events_dictionary['venue'].get('name')),
                # Venue ID
                'venue_id': str(events_dictionary['venue'].get('id')),
                # City
                'city': str(events_dictionary['venue']['city'].get('name')),
                # City ID
                'city_id': str(events_dictionary['venue']['city'].get('id')),
                # City Latitude
                'city_lat': float(events_dictionary['venue']['city']['coords'].get('lat')),
                # City Longitude
                'city_lon': float(events_dictionary['venue']['city']['coords'].get('long')),
                # State
                'state': str(events_dictionary['venue']['city'].get('state')),
                # State Code
                'state_id': str(events_dictionary['venue']['city'].get('stateCode')),
                # Country
                'country': str(events_dictionary['venue']['city']['country'].get('name')),
                # Country Code
                'country_id': str(events_dictionary['venue']['city']['country'].get('code'))
            }, ignore_index=True)
        return result_events_df

    def get_artist_events(self, artist, events_count=None):
        # Call Setlist.fm API
        url = 'https://api.setlist.fm/rest/1.0/artist/' + artist.mbid + '/setlists?p=1'
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
        result_setlist_df = pd.DataFrame(columns = self._set_columns)
        processed_events = 0
        
        for page in range(pages_count):
            url = 'https://api.setlist.fm/rest/1.0/artist/' + artist.mbid + '/setlists?p=' + str(page+1)
            headers = {'Accept': 'application/json', 'x-api-key': self._api_key}
            r = requests.get(url, headers=headers)	
            # Get .json Data
            data = r.json()
            #print (data)
            # Read .json file line per line
            for i in range(len(data['setlist'])):
                if (processed_events == events_count):
                    break
                current_sets_df = self.parse_events_dictionary(data['setlist'][i])
                result_events_df = pd.concat([result_events_df, current_sets_df], ignore_index=True)
                event_id = str(data['setlist'][i]['id'])
                if ('sets' in data['setlist'][i]):
                    current_sets_df = self.parse_sets_dictionary(data['setlist'][i]['sets'])
                    current_sets_df['event_id']=event_id
                    result_setlist_df = pd.concat([result_setlist_df, current_sets_df], ignore_index=True)                
                
                processed_events += 1
        result_events_df['eventdate'] = pd.to_datetime(result_events_df['eventdate'], format='%d-%m-%Y')
        return (result_events_df.sort_values(by=['eventdate'], ascending=False), result_setlist_df)
    
    def parse_sets_dictionary(self, sets_dictionary):
        result_setlist_df = pd.DataFrame(columns = self._set_columns)        
        song_num = 0
        for i in range(len(sets_dictionary['set'])):
            encore = 0
            if 'encore' in sets_dictionary['set'][i]:
                encore = 1
            for j in range(len(sets_dictionary['set'][i]['song'])):
                result_setlist_df = result_setlist_df.append( 
                    {
                        'song_num': song_num,
                        'name': sets_dictionary['set'][i]['song'][j].get('name'),
                        'encore': encore,
                        'tape': sets_dictionary['set'][i]['song'][j].get('tape', False),
                        'info': sets_dictionary['set'][i]['song'][j].get('info', ''),   
                    }, ignore_index = True)
                song_num+=1
        return result_setlist_df
    
    def get_setlist_for_event(self, event_id):
        # Call Setlist.fm API
        url = 'https://api.setlist.fm/rest/1.0/setlist/' + event_id
        headers = {'Accept': 'application/json', 'x-api-key': self._api_key}
        r = requests.get(url, headers=headers)	
        # Get .json Data
        data = r.json()
        result_setlist_df = pd.DataFrame(columns = self._set_columns)
        if ('sets' in data):
            result_setlist_df = pd.concat([result_setlist_df, self.parse_sets_dictionary(data['sets'])], ignore_index=True)
        result_setlist_df['event_id']=event_id
        return result_setlist_df
                