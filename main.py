
import argparse
import musicbrainzngs
from musicbrainzngs import WebServiceError

musicbrainzngs.set_useragent(
        "SetlistPrediction",
        "0.1",
        "https://github.com/skuill/SetlistPrediction"
)

if (__name__ == '__main__'):    
    parser = argparse.ArgumentParser(prog="SetlistPrediction")
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-u', '--username', type=str, help="Specify username", action="store", required=True)
    requiredNamed.add_argument('-p', '--password', type=str, help="Specify password", action="store", required=True)
    
    args = parser.parse_args()
    
    if args.username and args.password:
        print ("User: {}. Password: {}".format(args.username, args.password))
        
        musicbrainzngs.auth(args.username, args.password)
    
        try:
            result = musicbrainzngs.search_artists(artist="parkway drive", type="group")
        except WebServiceError as exc:
            print("Something went wrong with the request: %s" % exc)
        else:
            for artist in result['artist-list']:
                print(u"{id}: {name}".format(id=artist['id'], name=artist["name"]))
    else:
        parser.print_help()