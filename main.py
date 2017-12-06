import sys
import argparse
import musicbrainzngs
from musicbrainzngs import WebServiceError

musicbrainzngs.set_useragent(
        "SetlistPrediction",
        "0.1",
        "https://github.com/skuill/SetlistPrediction"
)

if __name__ == '__main__':    
    parser = argparse.ArgumentParser(prog="SetlistPrediction")
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-u', '--username', type=str, help="Specify username", action="store", required=True)
    requiredNamed.add_argument('-p', '--password', type=str, help="Specify password", action="store", required=True)
    
    args = parser.parse_args(['-h'])
    
    if args.username and args.password:
        print ("User: {}. Password: {}".format(args.username, args.password))
        
        musicbrainzngs.auth(args.username, args.password)
    
        artist_id = "c5c2ea1c-4bde-4f4d-bd0b-47b200bf99d6"
        try:
            result = musicbrainzngs.get_artist_by_id(artist_id)
        except WebServiceError as exc:
            print("Something went wrong with the request: %s" % exc)
        else:
            artist = result["artist"]
            print("name:\t\t%s" % artist["name"])
            print("sort name:\t%s" % artist["sort-name"])
    else:
        parser.print_help()