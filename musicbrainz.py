import musicbrainzngs
from musicbrainzngs import WebServiceError
import math
import pandas as pd
from datetime import datetime
import calendar

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
    _release_groups_columns=['id',
                        'title',
                        'date',
                        'primary-type',
                        'type']
    _interesting_albums_type = ['Album',
                                #'Single',
                                'EP']
    _release_columns= ['id',
                       'title',
                       'status',
                       'date',
                       'primary-type',
                       'type']
    
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
    
    def _release_groups_list_to_df(self, release_groups_list):
        result_release_groups_df = pd.DataFrame(columns = self._release_groups_columns)
        for i in range(len(release_groups_list)):
            for j in range(len(release_groups_list[i]['release-group-list'])):
                current_release_group = release_groups_list[i]['release-group-list'][j]
                if ('primary-type' in current_release_group):
                    if (current_release_group['primary-type'] in self._interesting_albums_type and current_release_group['type'] != 'Live'):
                        result_release_groups_df = result_release_groups_df.append(
                        {
                            'id': current_release_group['id'],
                            'title': current_release_group['title'],
                            'type': current_release_group['type'],
                            'primary-type': current_release_group['primary-type']
                        }, ignore_index=True)
        return result_release_groups_df
    
    def _releases_list_to_df(self, releases_list):
        result_release_df = pd.DataFrame(columns=self._release_columns)
        for i in range(len(releases_list)):
            for j in range(len(releases_list[i]['release-list'])):
                current_release = releases_list[i]['release-list'][j]
                current_row = {}
                if ('status' in current_release):
                    current_row['status'] = current_release['status']
                current_row['id'] = current_release['release-group']['id']
                if ('type' in current_release['release-group']):
                    current_row['type'] = current_release['release-group']['type']
                if ('primary-type' in current_release['release-group']):
                    current_row['primary-type'] = current_release['release-group']['primary-type']
                if ('date' in current_release):
                    current_row['date'] = current_release['date']
                current_row['title'] = current_release['title']
                result_release_df = result_release_df.append(current_row, ignore_index=True)
        return result_release_df[result_release_df['date'].notnull()].drop_duplicates()
                
    def _get_date_from_release_str(self, release_date_str, fill_date_mode='min'):
        splitted_date_str = release_date_str.split('-')
        splitted_count = len(splitted_date_str)
        if (fill_date_mode == 'max'):
            if (splitted_count == 1):
                days = calendar.monthrange(int(splitted_date_str[0]), 12)[1]
                formated_date_str = '{}-12-{}'.format(release_date_str, days)
            elif (splitted_count == 2):
                days = calendar.monthrange(int(splitted_date_str[0]), int(splitted_date_str[1]))[1]
                formated_date_str = '{}-{}'.format(release_date_str, days)
            else:
                formated_date_str = release_date_str
            return datetime.strptime(formated_date_str, '%Y-%m-%d')
        elif (fill_date_mode == 'min'):
            splitted_count_to_format = {
                1: '%Y',
                2: '%Y-%m',
                3: '%Y-%m-%d'}
            return datetime.strptime(release_date_str, splitted_count_to_format[splitted_count])
    
    def _get_earliest_releases(self, releases_df):
        releases_df['date_tmp'] = releases_df['date'].apply(lambda x: self._get_date_from_release_str(x, 'max'))
        earliset_releases = releases_df[releases_df.groupby(['id'])['date_tmp'].transform(min) == releases_df['date_tmp']].drop_duplicates()
        earliset_releases['date'] = earliset_releases['date'].apply(lambda x: self._get_date_from_release_str(x, 'min'))
        return earliset_releases.drop(['date_tmp'], axis=1)
    
    def _merge_release_groups_with_releases(self, release_groups_df, releases_df):
        interesting_releases_df = releases_df[['id', 'date']]
        return pd.merge(release_groups_df.drop(['date'], axis = 1), interesting_releases_df, on='id')
    """
                        df_date = recordings_df.loc[recordings_df['id']==current_release_id, 'date']
                        if (pd.isnull(df_date).bool()):
                            last_dates_priorities[current_release_id] = date_prioritydf
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
       """ 
       
    def get_musicbrainz_albums(self, artist_id):
        release_groups_list = self._get_release_groups(artist_id)
        releases_list = self._get_releases(artist_id)
        release_groups_df = self._release_groups_list_to_df(release_groups_list)
        releases_df = self._releases_list_to_df(releases_list)
        earliest_releases_df = self._get_earliest_releases(releases_df)
        return self._merge_release_groups_with_releases(release_groups_df, earliest_releases_df).drop(['id'], axis=1).sort_values(by=['date'], ascending=False)
        