import pandas as pd
import numpy as np
from pandas import ExcelWriter
import os

def save_to_csv(dir_path, df, file_name, index_label = False, index = False, sep = ';', nan_rep = ''):
    if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    df.index = df.index.map(str)
    df.to_csv('{}/{}.csv'.format(dir_path,file_name), index_label = index_label, index=index, sep = sep, encoding='utf-8-sig')
    writer = ExcelWriter('{}/{}.xlsx'.format(dir_path,file_name))
    df.to_excel(writer,'Sheet1', index_label = index_label, index=index, na_rep=nan_rep)
    writer.save()
    
def load_csv(dir_path, file_name):
    interesting_file = "{}/{}.csv".format(dir_path, file_name) 
    if (os.path.exists(interesting_file)):
        df = pd.read_csv(filepath_or_buffer = interesting_file, sep = ';', header=0, encoding='utf-8-sig')
        fix_dataframe_column_types(df)
        return df
    else:
        return None
    
def dataframe_group_by_column(df, column_name):
    return df.groupby([column_name])[column_name] \
              .count() \
              .reset_index(name='count') \
              .sort_values(['count'], ascending=False)
              
_columns_types = {'event_id':'str',
	                'artist':'str',
	                'eventdate':'datetime64[ns]',
	                'tourname':'str',
	                'venue':'str',
	                'venue_id':'str',
	                'city':'str',
	                'city_id':'str',
	                'city_lat':'float64',
	                'city_lon':'float64',
	                'state':'str',
	                'state_id':'str',
	                'country':'str',
	                'country_id':'str',
                    'song_num':'int64',
                    'name':'str',
                    'encore':'int64',
                    'tape':'bool',
                    'info':'str',
                    'id':'int64',
                    'title':'str',
                    'date':'datetime64[ns]',
                    'primary-type':'str',
                    'type':'str',
                    'status':'str',
                    'last_recording_date':'datetime64[ns]'
            }
def fix_dataframe_column_types(df):
    for column in df:
        df[column] = df[column].astype(_columns_types[column])    
              
def add_recordings_to_events_df(events_df, recordings):
    sorted_recordings = recordings.sort_values(by=['date'], ascending=True)
    sorted_events_df = events_df.sort_values(by=['eventdate'], ascending=True)
    sorted_events_df['last_recording_date'] = np.nan
    sorted_events_df['last_recording_date'] = sorted_events_df['last_recording_date'].astype('datetime64[ns]')
    for index, row in sorted_events_df.iterrows():
        released_recordings = sorted_recordings[sorted_recordings['date'] <= sorted_events_df.loc[index,'eventdate']]['date']
        if (len(released_recordings) > 0):
            last_released_recording_date = released_recordings.iloc[-1]
            sorted_events_df.loc[index, 'last_recording_date'] = last_released_recording_date
    return sorted_events_df