#!/usr/bin/env python3
import numpy as np
import pandas as pd

#data directory:
datadir = '/Users/rptkiddle/Desktop/Network-Toxicity/data/'

#load data for resampling:
subset = pd.read_csv('subset.csv')

#reformat date column (str -> datetime): 
subset['date']= pd.to_datetime(subset['date'])

#set datetimeindex (time series data):
subset = subset.set_index('date').sort_index()

#generate new sources dataframe 'presampled' for 5 minute intervals and containing only the counts of existing samples that fall within those windows:
presampled = subset.filter(['source', 'toxicity'])\
                   .groupby('source')\
                   .resample('5T').count()\
                   .rename(columns={'source': 'test'}).drop(columns=['test'])

#add placeholder columns for resampled estimates and window checks:
presampled['retox'] = np.nan

#define function to conditionally calculate resampled toxicity scores:
def re_tox(df):
    channel = df.index.get_level_values(0)[0]
    timestamps = df.index.get_level_values(1)
    print(f"Beginning resampling of channel:'{channel}'; for {len(timestamps)} 5-minute windows...")
    df['retox'] = np.where(
        df['toxicity'] >= 5, #condition to check
            mav_true(channel, timestamps), #return if true (choose: weighted or weighted?)
            mav_false(channel, timestamps), #return if false (choose: weighted or weighted?)
    )
    print(f"Completed resampling for channel:'{channel}'")
    return df

#define sub-function for calculating moving average from 5-minute windows. 
def mav_true(channel, timestamps):
    print('mav_true starting..')
    scores = []
    source = subset[subset['source'] == channel]
    for time in timestamps:
        start, stop = str(time), str(time + pd.Timedelta(5, unit='m'))
        values = source.loc[start:stop]['toxicity'].values
        if len(values) >= 5:
            scores.append(np.average(values))
        elif len(values) < 5:
            scores.append(float('NaN'))
    print('mav_true complete..')
    return np.array(scores)

#define sub-function to calculate average of last 1 to 5 toxicity scores within the last 24hrs relative to each 5-minute window:
def mav_false(channel, timestamps):
    print('mav_false starting..')
    scores = []
    source = subset[subset['source'] == channel]
    for time in timestamps:
        start = str(time + pd.Timedelta(5, unit='m') - pd.Timedelta(1, unit='d'))
        stop = str(time + pd.Timedelta(5, unit='m'))
        values = source.loc[start:stop]['toxicity'].tail(5).values
        if len(values) >= 1:
            scores.append(np.average(values))
        elif len(values) < 1:
            scores.append(float('NaN'))
    print('mav_false complete..')
    return np.array(scores)

#groupby channels and resample:
resampled = presampled.groupby(level=0).apply(re_tox)

#save resampled data:
resampled.to_csv(datadir+'resampled.csv')