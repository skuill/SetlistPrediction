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
        return df
    else:
        return None
    
def dataframe_group_by_column(df, column_name):
    return df.groupby([column_name])[column_name] \
              .count() \
              .reset_index(name='count') \
              .sort_values(['count'], ascending=False)
              
def add_recordings_to_events_df(events_df, recordings):
    sorted_recordings = recordings.sort_values(by=['date'], ascending=True)
    sorted_events_df = events_df.sort_values(by=['eventdate'], ascending=True)
    sorted_events_df['last_recording_date'] = np.nan
    for index, row in sorted_events_df.iterrows():
        last_recording_date = sorted_recordings[sorted_recordings['date'] <= sorted_events_df.loc[index,'eventdate']]['date'].iloc[-1]
        sorted_events_df.loc[index, 'last_recording_date'] = last_recording_date
    return sorted_events_df