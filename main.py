import sys
import argparse
from setlistfm import SetlistGetter
import pandas as pd
import utils

from musicbrainz import MusicbrainzSearcher

if (__name__ == '__main__'):    
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
        print ('User: {}. Password: {}. Setlistfm API key: {}.'.format(args.username, args.password, args.setlistfm_key))
    else:
        parser.print_help()   
        sys.exit('Good Bye!')     
    
    #search_artist = input('Prompt artist or group name: ')
    #search_artist = 'Parkway drive'
    search_artist = 'red hot chili peppers'
    #search_artist = 'rise against'
    print ('Search for artist:', search_artist)
    if search_artist:
        musicbrainz_searcher = MusicbrainzSearcher(args.username, args.password)       
        interesting_artist = musicbrainz_searcher.get_musicbrainz_artist_info(search_artist)
        recordings = musicbrainz_searcher.get_musicbrainz_albums(interesting_artist.mbid)
        print(interesting_artist)
        events_df = utils.load_csv(interesting_artist.name, 'events')
        setlists_df = utils.load_csv(interesting_artist.name, 'setlists')
        if events_df is None or setlists_df is None:
            setlistGetter = SetlistGetter(args.setlistfm_key)
            events_df, setlists_df = setlistGetter.get_artist_events(interesting_artist)
            utils.save_to_csv(interesting_artist.name, events_df, 'events')
            utils.save_to_csv(interesting_artist.name, setlists_df, 'setlists')
            
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
