import sys
import argparse
from setlistfm import SetlistGetter
import pandas as pd

from musicbrainz import MusicbrainzSearcher

if (__name__ == '__main__'):    
    parser = argparse.ArgumentParser(prog="SetlistPrediction")
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
        print ("User: {}. Password: {}. Setlistfm API key: {}.".format(args.username, args.password, args.setlistfm_key))
    else:
        parser.print_help()   
        sys.exit("Good Bye!")     
    
    #search_artist = input("Prompt artist or group name: ")
    #search_artist = "Parkway drive"
    search_artist = "Parkway Drive"
    print ("Search for artist:", search_artist)
    if search_artist:
        musicbrainz_searcher = MusicbrainzSearcher(args.username, args.password)       
        interesting_artist = musicbrainz_searcher.get_musicbrainz_artist_info(search_artist)
        print(interesting_artist)
        setlistGetter = SetlistGetter(args.setlistfm_key)
        events = setlistGetter.get_artist_events(interesting_artist, 5)
        print (events)
        
            
            
        
        
        
                