import sys
import argparse
from setlistfm import SetlistGetter
from musicbrainz import MusicbrainzSearcher
import pandas as pd
import utils
import matplotlib.pyplot as plt

class UserInformation():
    def __init__(self, username, password, setlistfm_key):
        self._username = username
        self._password = password
        self._setlistfm_key = setlistfm_key
        
    username = property()
    @username.getter
    def username(self):
        return self._username
    
    password = property()
    @password.getter
    def password(self):
        return self._password
    
    setlistfm_key = property()
    @setlistfm_key.getter
    def setlistfm_key(self):
        return self._setlistfm_key
    
    def __str__(self):
        return 'User: {}. Password: {}. Setlistfm API key: {}.'.format(self._username, self._password, self._setlistfm_key)

class ArtistData():
    def __init__(self, artist_information, events, setlists, recordings):
        self._artist_information = artist_information
        self._events = events
        self._setlists = setlists
        self._recordings = recordings
    
    events = property()
    @events.getter
    def events(self):
        return self._events
        
    setlists = property()
    @setlists.getter
    def setlists(self):
        return self._setlists
        
    recordings = property()
    @recordings.getter
    def recordings(self):
        return self._recordings
    
    artist_information = property()
    @artist_information.getter
    def artist_information(self):
        return self._artist_information
    
    def is_nan(self):
        return self._events is None or self._setlists is None or self._recordings is None

class ArtistManager():    
    def __init__(self, user_information):
        self._user_information = user_information
        self._musicbrainz_searcher = MusicbrainzSearcher(user_information.username, user_information.password)
        self._setlist_getter = SetlistGetter(user_information.setlistfm_key)
    
    def get_artist_data(self, artist_name):
        artist_information = self._musicbrainz_searcher.get_musicbrainz_artist_info(artist_name)
        print('Process artist:', artist_information)
        recordings_df = self._musicbrainz_searcher.get_musicbrainz_albums(artist_information.mbid)
        events_df, setlists_df = self._setlist_getter.get_artist_events(artist_information)
        return ArtistData(artist_information, events_df, setlists_df, recordings_df)
    
    def save_artist_data(self, artist_data):
        print('Save artist data:', artist_data.artist_information)
        utils.save_to_csv(artist_data.artist_information.name, artist_data.events, 'events')
        utils.save_to_csv(artist_data.artist_information.name, artist_data.setlists, 'setlists')
        utils.save_to_csv(artist_data.artist_information.name, artist_data.recordings, 'recordings')

    def load_artist_data(self, artist_name):
        artist_information = self._musicbrainz_searcher.get_musicbrainz_artist_info(artist_name)
        print('Load artist data:', artist_information)
        events_df = utils.load_csv(artist_information.name, 'events')
        setlists_df = utils.load_csv(artist_information.name, 'setlists')
        recordings_df = utils.load_csv(artist_information.name, 'recordings')
        if events_df is not None:
            events_df['eventdate'] = pd.to_datetime(events_df['eventdate'], format='%Y-%m-%d')
        if recordings_df is not None:
            recordings_df['date'] = pd.to_datetime(recordings_df['date'], format='%Y-%m-%d')
        return ArtistData(artist_information, events_df, setlists_df, recordings_df)

def parse_input_arguments():
    parser = argparse.ArgumentParser(prog='SetlistPrediction')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-u', '--username', 
                               type=str, help="Specify username", 
                               action="store", required=True)
    requiredNamed.add_argument('-p', '--password', 
                               type=str, help="Specify password", 
                               action="store", required=True)
    requiredNamed.add_argument('-sfmk', '--setlistfm_key', 
                               type=str, help="Specify setlistfm API key", 
                               action="store", required=True)    
    args = parser.parse_args()    
    if args.username and args.password and args.setlistfm_key:
        return UserInformation(args.username, args.password, args.setlistfm_key)
    else:
        parser.print_help()   
        sys.exit('Good Bye!')     

if (__name__ == '__main__'):
    
    user_information = parse_input_arguments()
    print (user_information)
    
    artist_manager = ArtistManager(user_information)
    
    #interesting_artists = ['metallica', 'Bury Tomorrow', 'Rise Against', 'Red Hot Chili Peppers', 'In Fear and Faith', 'Parkway Drive'] 
    interesting_artists = ['Parkway Drive']
    artist_setlists_with_events = {}
    for artist_name in interesting_artists:
        #Load artist from database or csv
        artist_data = artist_manager.load_artist_data(artist_name)
        if artist_data.is_nan():
            #Process if artist don't exist in local storage
            print ('artist not processed yet', artist_name)
            artist_data = artist_manager.get_artist_data(artist_name)
            artist_manager.save_artist_data(artist_data)

        #Add last recording date to events
        events_with_recordings_df = utils.add_recordings_to_events_df(artist_data.events, artist_data.recordings)
        #Drop events not important features
        events_with_recordings_df.drop(['venue','venue_id','city','city_id','city_lat','city_lon','state_id','country_id'], axis=1, inplace=True)
        #Drop setlist not important features
        artist_data.setlists.drop(['info'], axis=1, inplace=True)
        #Merge setlist with events info
        artist_setlists_with_events_df = artist_data.setlists.merge(events_with_recordings_df, how='outer', on='event_id')
        
        #Events without setlist
        setlists_counts = utils.dataframe_group_by_column(artist_data.setlists, 'event_id')
        notIncluding = artist_data.events[~artist_data.events['event_id'].isin(setlists_counts['event_id'])]
        
        #NaN Count statistics in dataframe:
        #artist_data.setlists.isnull().sum()
        #Select rows with any Nan in row
        #artist_data.setlists[artist_data.setlists.isnull().any(axis=1)]
        
        #Drop setlists without event_id information
        artist_setlists_with_events_df.dropna(subset=['song_num','name'],inplace=True)
        
        utils.fix_dataframe_column_types(artist_setlists_with_events_df)
        
        artist_setlists_with_events[artist_name] = artist_setlists_with_events_df
        
        '''
        #Events statistics
        city_events_counts = utils.dataframe_group_by_column(events_df, 'city')
        country_events_counts = utils.dataframe_group_by_column(events_df,'country')
        russian_events = events_df[events_df['country']=='Russia']
        
        #Setlists statistics
        city_setlists_counts = utils.dataframe_group_by_column(setlists_df, 'name')
        russian_setlist = setlists_df[setlists_df['event_id'].isin(russian_events['event_id'])]
        russian_setlist_counts = utils.dataframe_group_by_column(russian_setlist, 'name')
        
        # events have many TourName NAN. Ignore this. Maybe it's important feature
        events_df_nan = events_df[pd.isnull(events_df.drop(['tourname'], axis=1)).any(axis=1)]
        # setlists have many INFO NAN. Ignore this.
        setlists_df_nan = setlists_df[pd.isnull(setlists_df.drop(['info'], axis=1)).any(axis=1)]
        '''
    for artist_name in interesting_artists:
        print("\r\nArtist dataframe information {}:".format(artist_name))
        print(artist_setlists_with_events[artist_name].info())
        print("Artist dataframe describe:")
        print(artist_setlists_with_events[artist_name].describe(include=['object', 'bool']))
        fig, ax = plt.subplots(figsize=(25,14))
        artist_setlists_with_events[artist_name].groupby(['eventdate','event_id']).size().reset_index(name='count').plot(ax=ax, x='eventdate', y='count', style=['ro--'])
        last_recording_dates = artist_setlists_with_events[artist_name]['last_recording_date'].unique()
        for lrd in last_recording_dates:
            plt.axvline(x=lrd, color='g', linestyle=':')
    print ('Process Complete!')