from turtle import st
from click import pass_context
import pandas as pd
import json
from datetime import datetime
import os

import data_processing as dp

def download_data(id_device: str, start_date: str, end_date: str, sample_rate: str, token: str, format:str = None):
    
    start = int((datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") - datetime(1970, 1, 1)).total_seconds())
    end = int((datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S") -  datetime(1970, 1, 1)).total_seconds())

    file_names = []
    if 'makesens_data' in os.listdir():
        missing, file_names = pd.in_backup(id_device, start, end, sample_rate)
        if len(missing) == 0:
            pass
        else:
            for range in missing:
                name = pd.download(id_device,range[0],range[1],sample_rate,token)
                file_names.append(name)
        
    else:
        name = pd.download(id_device, start, end, sample_rate, token)
        file_names.append(name)

    data = pd.DataFrame()
    for i in file_names:
        dat = pd.read_csv('makesens_data/'+i)
        dat.index = dat.iloc[:,0]
        dat = dat.drop([dat.columns[0]],axis=1)
        data = pd.concat([data,dat],axis=0)
    
    data = data.sort_index()
    data = data.drop_duplicates()

    if len(file_names) == 1:
        pass
    else:
        for i in file_names:
            os.remove('makesens_data/'+ i)

        with open('makesens_data/registro.json', 'r') as fp:
            registro = json.load(fp)


        index = [registro[id_device].index(i) for i in registro[id_device] if i[3] in file_names]

        for i in sorted(index,reverse=True):
              del registro[id_device][i]
            
        with open('makesens_data/registro.json', 'w') as fp:
            json.dump(registro, fp)
        
        pd.save_in_backup(data, id_device, start, end, sample_rate)
    
    start_ = start_date.replace(':','_') 
    end_ = end_date.replace(':','_')
    
    if format == None:
        pass
    elif format == 'csv':
        data.to_csv(id_device + '_'+ start_  +'_' + end_ + '_ ' + sample_rate  +'.csv')
    elif format == 'xlsx':
        data.to_excel(id_device + '_'+ start_  +'_' + end_ + '_ ' + sample_rate  +'.xlsx')
    else:
        print('El formato no es valido. Formatos validos: csv y xlsx')
        
    data_ = data
    data_ = pd.cutdata(data,start_date,end_date)
    return data_

