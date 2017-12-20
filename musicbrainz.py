
import musicbrainzngs
from musicbrainzngs import WebServiceError

class Artist:
    def __init__(self, name, mbid):
        self._name = name
        self._mbid = mbid
    
    name = property()
    @name.getter
    def name(self):
        return self._name
        
    mbid = property()
    @mbid.getter
    def mbid(self):
        return self._mbid
    
    def __str__(self):
        return 'Artist name: {}, MBID: {}'.format(self.name, self.mbid)

class MusicbrainzSearcher:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        musicbrainzngs.set_useragent(
                'SetlistPrediction',
                '0.1',
                'https://github.com/skuill/SetlistPrediction'
        )
        musicbrainzngs.auth(self._username, self._password)
    
    def get_musicbrainz_artist_info(self, artist_name):
        try:
            search_artist_lower = artist_name.lower()
            result = musicbrainzngs.search_artists(artist=search_artist_lower)#, type="group")
        except WebServiceError as exc:
            raise Exception('Something went wrong with the request to musicbrainz: %s' % exc)
        else:            
            for artist in result['artist-list']:
                if (artist['name'].lower() == search_artist_lower):
                    return Artist(artist['name'], artist['id'])
        return None
    