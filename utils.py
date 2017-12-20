import pandas as pd
from pandas import ExcelWriter
import os

def save_to_csv(dir_path, df, file_name, index_label = False, index = False, sep = ';', nan_rep = ''):
    if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    df.index = df.index.map(str)
    df.to_csv('{}/{}.csv'.format(dir_path,file_name), index_label = index_label, index=index, sep = sep)
    writer = ExcelWriter('{}/{}.xlsx'.format(dir_path,file_name))
    df.to_excel(writer,'Sheet1', index_label = index_label, index=index, na_rep=nan_rep)
    writer.save()
    
def load_csv(dir_path, file_name):
    interesting_file = "{}/{}.csv".format(dir_path, file_name) 
    if (os.path.exists(interesting_file)):
        df = pd.read_csv(filepath_or_buffer = interesting_file, sep = ';', header=0)
        return df
    else:
        return None