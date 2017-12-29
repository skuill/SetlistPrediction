import musicbrainzngs
from musicbrainzngs import WebServiceError
import math
import pandas as pd
from datetime import datetime

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
    _albums_columns=['id',
                        'title',
                        'date',
                        'type']
    _interesting_albums_type = ['Album',
                                #'Single',
                                'EP']
    
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
    
    def _get_release_groups(self, artist_id):
        limit = 100
        offset = 0
        total_pages_to_process = 1
        release_groups_list = []
        try:
            release_groups = musicbrainzngs.search_release_groups(arid=artist_id, limit=limit)
            release_groups_list.append(release_groups)            
            release_groups_count = int(release_groups['release-group-count'])
            if (release_groups_count > limit):
                total_pages_to_process = math.ceil(release_groups_count / limit) - 1
                offset += limit
                for i in range(total_pages_to_process):
                    release_groups = musicbrainzngs.search_release_groups(arid=artist_id, limit=limit, offset=offset)
                    release_groups_list.append(release_groups)
        except WebServiceError as exc:
            raise Exception('Something went wrong with the request to musicbrainz: %s' % exc)
        else:
            return release_groups_list
        
    def _get_releases(self, artist_id):
        limit = 100
        offset = 0
        total_pages_to_process = 1
        releases_list = []
        try:        
            offset = 0        
            releases = musicbrainzngs.search_releases(arid=artist_id, limit=limit)
            releases_list.append(releases)            
            releases_count = int(releases['release-count'])
            if (releases_count > limit):
                total_pages_to_process = math.ceil(releases_count / limit) - 1
                offset += limit
                for i in range(total_pages_to_process):
                    releases = musicbrainzngs.search_releases(arid=artist_id, limit=limit, offset=offset)
                    releases_list.append(releases)
        except WebServiceError as exc:
            raise Exception('Something went wrong with the request to musicbrainz: %s' % exc)
        else:
            return releases_list
    
    def _get_recordings_from_release_groups(self, release_groups_list):
        result_recordings_df = pd.DataFrame(columns = self._albums_columns)
        for i in range(len(release_groups_list)):
            for j in range(len(release_groups_list[i]['release-group-list'])):
                current_release_group = release_groups_list[i]['release-group-list'][j]
                if ('primary-type' in current_release_group):
                    if (current_release_group['primary-type'] in self._interesting_albums_type and current_release_group['type'] != 'Live'):
                        result_recordings_df = result_recordings_df.append(
                        {
                            'id': current_release_group['id'],
                            'title': current_release_group['title'],
                            'type': current_release_group['primary-type']
                        }, ignore_index=True)
        return result_recordings_df
    
    def _get_date_from_release_str(self, release_date_str):
        separater_count = release_date_str.count('-')
        separater_to_format = {
                0: '%Y',
                1: '%Y-%m',
                2: '%Y-%m-%d'}
        return (separater_count, datetime.strptime(release_date_str, separater_to_format[separater_count]))
    
    def _fill_recordings_with_release_data(self, recordings_df, releases_list):
        last_dates_priorities={}
        for i in range(len(releases_list)):
            for j in range(len(releases_list[i]['release-list'])):
                current_release = releases_list[i]['release-list'][j]
                if ('status' in current_release and current_release['status'] == 'Official'):
                    current_release_id = current_release['release-group']['id']
                    if (current_release_id in recordings_df['id'].values and 'date' in current_release):
                        (date_priority, current_release_date) = self._get_date_from_release_str(current_release['date'])
                        df_date = recordings_df.loc[recordings_df['id']==current_release_id, 'date']
                        if (pd.isnull(df_date).bool()):
                            last_dates_priorities[current_release_id] = date_priority
                            recordings_df.loc[recordings_df['id']==current_release_id, 'date'] = current_release_date
                        else:
                            change_date = False
                            if ((df_date > current_release_date).bool() and date_priority >= last_dates_priorities[current_release_id]):
                                change_date = True
                            elif (date_priority > last_dates_priorities[current_release_id]):
                                change_date = True
                            if (change_date):
                                recordings_df.loc[recordings_df['id']==current_release_id, 'date'] = current_release_date
                                last_dates_priorities[current_release_id] = date_priority
        
    def get_musicbrainz_albums(self, artist_id):
        release_groups_list = self._get_release_groups(artist_id)
        releases_list = self._get_releases(artist_id)
        recordings_df = self._get_recordings_from_release_groups(release_groups_list)
        self._fill_recordings_with_release_data(recordings_df, releases_list)
        return recordings_df.drop(['id'], axis=1)
        
        