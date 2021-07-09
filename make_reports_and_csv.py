#!/usr/bin/env python
# coding: utf-8

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import re


def import_data(report_files_path):
    data = {'MAIN':[], 'SOUTH':[], 'STARBUCKS':[]}

    for file in report_files_path:

        with file.open() as f:
            report_date = dt.datetime.strptime(re.search('\d{8}', f.name)[0], '%Y%m%d').date()

            # Parse the file and remake the first column to be in an ISO dateformat for easy access later
            file_data = [','.join(x.split()) for x in f.read().split('\n')][1:-1]
            file_data = [
                report_date.strftime('%Y-%m-%d') + ' ' 
                + str.replace(x, re.search('-\d{2}:\d{2}', x)[0], '') 
                for x in file_data
            ]

            camera = str.upper(file.parent.stem)
            data[camera] += file_data
    
    return data


def sanitize_data(data):
    for camera in data:
        # Expand the series, currently delimited by commas, into a dataframe
        # then sort it so it is chronologically ascending
        data[camera] = pd.Series(data[camera]).str.split(',', expand = True)

        # Data is originally string type. Convert to int type to do math later
        data[camera][1] = data[camera][1].astype(int)
        data[camera][2] = data[camera][2].astype(int)

        # Rename columns
        data[camera].columns = ['DATE', f'{camera}_IN', f'{camera}_OUT']
        data[camera] = data[camera].set_index('DATE')

    # Combine all tables into a single one, filling NaN as 0
    data = pd.concat([data[camera] for camera in data], axis = 1).fillna(0)

    # Change index from string to datetime object so we can use pivot tables later
    data.index = pd.to_datetime(data.index)
    return data.sort_index()


# Start data extraction
current_dir = Path('./')
report_files = sorted(list(current_dir.glob('**/Daily_Report_*.txt')))

raw_data = import_data(report_files)
data = sanitize_data(raw_data)

for tt in ['MONTHLY', 'DAILY']:    
    total_entry = data.resample(tt[0]).sum().sum(1)
    opening_to_noon = data.between_time('08:00:00', '12:00:00', include_end = False).resample(tt[0]).sum().sum(1)
    noon_to_nine = data.between_time('12:00:00', '21:00:00', include_end = False).resample(tt[0]).sum().sum(1)
    nine_to_midnight = data.between_time('21:00:00', '23:00:00', include_end = False).resample(tt[0]).sum().sum(1)
    midnight_to_closing = data.between_time('00:00:00', '02:00:00').resample(tt[0]).sum().sum(1)

    report = pd.DataFrame()
    report['TOTAL' + '_' + tt] = total_entry
    report[tt + '_OPENING_TO_NOON'] = opening_to_noon
    report[tt + '_NOON_TO_NINE'] = noon_to_nine
    report[tt + '_NINE_TO_MIDNIGHT'] = nine_to_midnight
    report[tt + '_MIDNIGHT_TO_CLOSING'] = midnight_to_closing

    # Write to file
    filetime = dt.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    data.to_csv(filetime + '_' + str.lower(tt) + '_uop_entrance_data.csv')
    report.to_csv(filetime + '_' + str.lower(tt) + '_report_info.csv')
    report.describe().to_csv(filetime + '_' + str.lower(tt) + '_report_stats.csv')