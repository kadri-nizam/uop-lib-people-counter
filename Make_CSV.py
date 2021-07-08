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

filename = dt.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
filename = filename + '_uop_entrance_data.csv'
data.to_csv(filename)