#!/usr/bin/env python3
import pickle
import numpy as np
import pandas as pd
from idtxl.data import Data
from idtxl.multivariate_te import MultivariateTE

#data directory:
datadir = '/Users/rptkiddle/Desktop/Network-Toxicity/data/'

#0. CONFIGURATION:
network_analysis = MultivariateTE()

#settings for sliding window:
start_day = 0 #start here
stop_day = 165 #stop here
day_size = 288 #number of samples per day.
window_size = 96 #number of samples in window.

#settings for IDTxl estimator (see docs):
settings = {'cmi_estimator': 'JidtGaussianCMI',
            'max_lag_sources': 6, 
            'min_lag_sources': 1,
            'alpha_max_stat': 0.01,
            'alpha_min_stat': 0.01,
            'permute_in_time': True,
            'verbose': False}


#1. LOAD AND REFORMAT DATA:

#load resampled data
resampled = pd.read_csv(datadir+'resampled.csv')

#reformat date column (str -> datetime): 
resampled['date']= pd.to_datetime(resampled['date'])

#set datetimeindex (time series data):
resampled = resampled.set_index('date').sort_index()

#pivot long into wide (sparse) format:
pivoted = pd.pivot(resampled, columns='source', values='retox')


#2. GENERATE GLOBAL ID LIST FROM RESAMPLED DATA:
global_IDs = dict(zip(pivoted.columns.to_list(), range(pivoted.shape[1])))

#dump global IDs to pkl file:
with open(f'{datadir}global_IDs.pkl', 'wb') as f:
    pickle.dump(global_IDs, f)


#3. PERFORM ESTIMATIONS

#outputs:
results_ts = {}
convert_ID = {} 

#set head:
begin, end  = start_day*window_size*(day_size/window_size), start_day*window_size*(day_size/window_size)+window_size

#begin run:
for r in range(start_day*(day_size/window_size), stop_day*(day_size/window_size)): 
    
    print(f'starting estimation: {r}, going to {stop_day*(day_size/window_size)}.')
    
    #take window; drop any chats/channels for which there is missing data (nan):
    embedding = pivoted.iloc[begin:end].dropna(axis=1, how='any')
    
    #retain local ids for building conversion dictionary:
    local_IDs = dict(zip(embedding.columns.to_list(), range(embedding.shape[1])))
    
    print(f'this embedding starts at: {embedding.first_valid_index()} and ends at {embedding.last_valid_index()}.')
    
    #instantiate data object with window data:
    data = Data(embedding, dim_order='sp')
    
    #pass window to estimator:
    results = network_analysis.analyse_network(settings=settings, data=data)
    
    #update results dict (key = datetime start of target variable):
    results_ts.update({str(embedding.first_valid_index()):results})
     
    #update conversion dict (key = datetime start of target variable):
    convert_ID.update({str(embedding.first_valid_index()): {local_IDs[channel]: global_IDs[channel] for channel in local_IDs.keys()}})
    
    #increment window:
    begin += window_size
    end += window_size    
        
#dump results to pkl file:
with open(f'{datadir}results_day{start_day}_to_day{stop_day}.pkl', 'wb') as f:
    pickle.dump(results_ts, f)
    
#dump conversion IDs to pkl file:
with open(f'{datadir}convert_ID_day{start_day}_to_day{stop_day}.pkl', 'wb') as f:
    pickle.dump(convert_ID, f)