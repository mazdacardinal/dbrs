import json
import urllib
import requests
import numpy as np
import pandas as pd
from timeit import default_timer as timer

def run_exercise():
    """
    Gather data from freely available sets to compute NYC complaint data per borough and per zipcode
    """

    #we want to get data from a url source in chunks to hopefully make it faster
    #create an empty data frame to start that will hold the full set
    full_df = pd.DataFrame()

    #set the column types for the data frames we are going to load
    column_types={'complaint_type': np.unicode,
       'incident_zip': np.unicode,
      }

    offset = 0
    chunk_size = 100000
    start = timer()

    while True:
        #retrieve data in chunks using json api as it lets us filter out years and select only certain columms
        url_base = 'https://data.cityofnewyork.us/resource/fhrw-4uyv.json?$limit=%s&$offset=%s' % (chunk_size,offset)
        select_clause = '$select=created_date,complaint_type,incident_zip,borough'
        #create a filter to get only 2017 data
        where_clause = '$where=' + urllib.quote("created_date between '2017-01-01T00:00:00' and '2017-12-31T23:59:59'")
        #create the full url
        url = '%s&%s&%s' % (url_base,select_clause,where_clause)

        #now get the filtered data
        result = requests.get(url)

        #load the data in to a data frame and append it to the full one
        current_df = pd.read_json(result.text, dtype=column_types)
        full_df = pd.concat([full_df,current_df])

        data_read = current_df.shape[0]
        offset += chunk_size

        if data_read < chunk_size:
            break

    end = timer()
    print 'Total read', full_df.shape[0]
    print 'Elapsed', (end-start)

if __name__ == "__main__":
    run_exercise()

