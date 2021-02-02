#!/usr/bin/env python
# coding: utf-8

# In[77]:


from datetime import datetime, date
from pathlib import Path

import numpy as np
import pandas as pd
import re

import matplotlib.pyplot as plt


# In[72]:


current_dir = Path('./')
report_files = list(current_dir.glob('**/Daily_Report_*.txt'))


# In[83]:


data = {'MAIN':[], 'SOUTH':[], 'STARBUCKS':[]}

for file in report_files:
    
    with file.open() as f:
        report_date = datetime.strptime(re.search('\d{8}', f.name)[0], '%Y%m%d').date()
    
        # Parse the file and remake the first column to be in an ISO dateformat for easy access later
        file_data = [','.join(x.split()) for x in f.read().split('\n')][1:-1]
        file_data = [
            report_date.strftime('%Y-%m-%d') + ' ' 
            + str.replace(x, re.search('-\d{2}:\d{2}', x)[0], '') 
            for x in file_data
        ]
        
        camera = str.upper(file.parent.stem)
        
        data[camera] += file_data


# In[84]:


for key in data:
    data[key] = pd.Series(data[key]).str.split(',', expand = True)
    data[key].columns = ['TIME', f'{key}_IN', f'{key}_OUT']
    data[key] = data[key].set_index('TIME')
    
data = pd.concat([data[key] for key in data], axis = 1)


# In[85]:


data

