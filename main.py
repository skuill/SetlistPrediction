import sys
import argparse

from musicbrainz import MusicbrainzSearcher

if (__name__ == '__main__'):    
    parser = argparse.ArgumentParser(prog="SetlistPrediction")
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-u', '--username', type=str, help="Specify username", action="store", required=True)
    requiredNamed.add_argument('-p', '--password', type=str, help="Specify password", action="store", required=True)
    
    args = parser.parse_args()
    
    if args.username and args.password:
        print ("User: {}. Password: {}".format(args.username, args.password))
    else:
        parser.print_help()   
        sys.exit("Good Bye!")     
    
    #search_artist = input("Prompt artist or group name: ")
    #search_artist = "Parkway drive"
    search_artist = "iron maiden"
    print ("Search for artist:", search_artist)
    if search_artist:
        musicbrainz_searcher = MusicbrainzSearcher(args.username, args.password)       
        interesting_artist = musicbrainz_searcher.get_musicbrainz_artist_info(search_artist)
        print(interesting_artist)
            
            
        
        
        
                