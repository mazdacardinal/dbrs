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
        select_clause = '$select=:id,created_date,complaint_type,incident_zip,borough'
        #create a filter to get only 2017 data
        where_clause = '$where=' + urllib.quote("created_date between '2017-01-01T00:00:00' and '2017-12-31T23:59:59'")
        #create the full url
        url = '%s&%s&%s' % (url_base,select_clause,where_clause)

        #now get the filtered data
        result = requests.get(url)

        #load the data in to a data frame and append it to the full one
        current_df = pd.read_json(result.text, dtype=column_types)
        data_read = current_df.shape[0]

        #remove rows with unspecified boroughs
        current_df = current_df[current_df.borough != 'Unspecified']
        #now add to the full one
        full_df = pd.concat([full_df,current_df])

        #now increase the offset and exit if we read less than the full amount
        offset += chunk_size
        if offset >= 200000 or data_read < chunk_size:
            break

    end = timer()
    print 'Total read', full_df.shape[0]
    print 'Elapsed', (end-start)


    #Problem 1
    #Consider only the 10 most common overall complaint types. For each borough, how many of each of those 10 types were there in 2017?

    #get the top 10 complaints by type in a list
    complaint_counts = full_df.groupby(['complaint_type'])[':id'].agg('count')
    top_complaints = complaint_counts.nlargest(10).to_dict().keys()

    #now use the top 10 complaints to filter the main list
    filtered_top_complaint_df = full_df[full_df['complaint_type'].isin(top_complaints)]
    #now get the top complaints per borough
    borough_top_complaint_df = filtered_top_complaint_df.groupby(['borough','complaint_type'])[':id'].agg('count')
    print 'Show Counts of the Top 10 complaints in each borough'
    print borough_top_complaint_df.head()



    #Problem 2
    #For the 10 most populous zip codes, how many of each of those 10 types were there in 2017?

    #load a data frame with zipcode population information from the census
    zipcode_column_types={'Zip Code ZCTA': np.unicode }
    zipcode_population_df = pd.read_csv('2010_Census_Population_By_Zipcode_ZCTA.csv',dtype=zipcode_column_types).rename(
                         columns={'Zip Code ZCTA': 'incident_zip','2010 Census Population':'Zip Population'})

    #get distinct nyc zipcodes (might want to replace the with a separate imported dataset)
    zipcodes = full_df.incident_zip.unique()

    #filter the population data set by the distinct zipcodes to just get nyc populations
    nyc_zipcode_population_df = zipcode_population_df[zipcode_population_df['incident_zip'].isin(zipcodes)]
    #print nyc_zipcode_population_df.head()

    #now get the top ten most populous zipcodes from nyc (this might need to be improved to be done outset our complaint set)
    ten_largest_zipcodes_df = nyc_zipcode_population_df.nlargest(10, 'Zip Population')#.to_dict().keys()

    #now merge the top ten zipcodes set with the top 10 complaint set we previously calculated for problem 1
    complaints_in_top_zipcodes_df = ten_largest_zipcodes_df.merge(filtered_top_complaint_df[['complaint_type','incident_zip']], on='incident_zip')
    #now get the aggegate count of complaint type for each of the 10 zipcodes
    complaints_in_top_zipcodes_agg_df = complaints_in_top_zipcodes_df.groupby(['incident_zip', 'complaint_type']).count()
    print 'Show Top 10 Complaints in the top 10 zipcodes'
    print complaints_in_top_zipcodes_agg_df.head()


    #Problem 3
    #Considering all complaint types. Which boroughs are the biggest "complainers" relative to the size of the population in 2017?
    #Meaning, calculate a complaint-index that adjusts for population of the borough.

    #get borough population information for 2010 from a previously downloaded file
    borough_pop_df = pd.read_csv('New_York_City_Population_By_Neighborhood_Tabulation_Areas.csv')
    borough_pop_df = borough_pop_df[borough_pop_df['Year'] == 2010]

    #convert the boroughs to uppercase
    borough_pop_df['Borough'] = map(lambda x: x.upper(), borough_pop_df['Borough'])
    #now aggregate across all areas of each borough to get total population per borough
    aggregate_borough_pop_df = borough_pop_df.groupby(['Borough'])['Population'].sum().reset_index()

    #count the complaints per borough from the full list of complaints in to a new dataframe
    aggregate_borough_complaint_df = full_df.groupby(['borough'])[':id'].count().reset_index().rename(columns={'borough': 'Borough', ':id':'Complaints'})
    #now merge the borough complaint set with the population set so we have both at once
    full_borough_df = aggregate_borough_pop_df.merge(aggregate_borough_complaint_df[['Complaints','Borough']], on='Borough')
    #now calculate the complaint index as the number of complaints per person in each borough
    full_borough_df['Complaint_Index'] = full_borough_df['Complaints'] / full_borough_df['Population']
    print 'Show complaints per person for each borough'
    print full_borough_df.head()

if __name__ == "__main__":
    run_exercise()

