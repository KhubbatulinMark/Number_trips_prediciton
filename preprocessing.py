########################################################################
# import python-library
########################################################################
# default
import sys
import os
import glob
from datetime import datetime, date
import logging
# additional
from tqdm import tqdm
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
# original lib
import common
########################################################################

########################################################################
# configuration and logs
########################################################################
logging.basicConfig(
                    level=logging.DEBUG, 
                    filename='logs.log', 
                    format='%(asctime)s %(levelname)s:%(message)s'
                    )

path = common.yaml_load()['taxi_data']
########################################################################

def round_min(minute):
    return round(minute, 2)

def get_grid_params(grid_input:dict, grid_cells: int):
    d_latitude = (grid_input['latitude'][1] - grid_input['latitude'][0]) / grid_cells
    d_longitude = (grid_input['longitude'][1] - grid_input['longitude'][0]) / grid_cells

    return d_latitude, d_longitude

def get_region_5(row, d_latitude: float , d_longitude: float, ny_grid: float, grid_cells: int):

    # calc indexes assuming matrix longitude/latitude
    # coordinates tuple should fit an interval on the intersection
    # of latitude and longitude indexes
    # region is calculated as a function of two indexes
    # so that it fits provided 'regions.csv' table

    longitude_index = (row['pickup_longitude'] - ny_grid['longitude'][0]) // d_longitude
    latitude_index = (row['pickup_latitude'] - ny_grid['latitude'][0]) // d_latitude + 1
    region = longitude_index * grid_cells + latitude_index
    return int(region)

def get_region_individual(pickup_longitude: float, pickup_latitude: float,d_latitude: float , d_longitude: float, ny_grid: dict, grid_cells: int):

    # calc indexes assuming matrix longitude/latitude
    # coordinates tuple should fit an interval on the intersection
    # of latitude and longitude indexes
    # region is calculated as a function of two indexes
    # so that it fits provided 'regions.csv' table

    longitude_index = (pickup_longitude - ny_grid['longitude'][0]) // d_longitude
    latitude_index = (pickup_latitude - ny_grid['latitude'][0]) // d_latitude + 1
    region = longitude_index * grid_cells + latitude_index
    return int(region)
       
def filter_data(df):
    """
    Filtering data from errors and outliers
    """

    df['tpep_pickup_datetime'] = df['tpep_pickup_datetime'].astype('datetime64')
    df['tpep_dropoff_datetime'] =  df['tpep_dropoff_datetime'].astype('datetime64')

    row_len = len(df)

    # Create duration column
    df['trip_duration_min'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']) / \
                                                                            np.timedelta64(1, 'm')
    # Arround minute 
    df['trip_duration_min'] = df['trip_duration_min'].apply(round_min)
    # Zero duration cleaning. Threshold < 1 minute
    df.drop(df[df['trip_duration_min'] < 1].index, inplace=True, axis=0) 
    # Zero passenger cleaning. Threshold = 0 passenger
    df.drop(df[df['passenger_count'] == 0].index, inplace=True)
    # Zero distance cleaning. Threshold < 1 mile distance
    df.drop(df[df['trip_distance'] < 1].index, inplace=True)

    # only town region
    town_square = common.yaml_load()['ny_square']

    d_latitude, d_longitude = get_grid_params(grid_input = town_square, grid_cells = 50)

    df['region'] = df.apply(get_region_5, d_latitude = d_latitude , d_longitude = d_longitude , ny_grid = town_square, grid_cells = 50,  axis=1)

    df.drop(df[df['region'] > 2500].index, inplace=True)

    logging.debug(f"Has been filtered {row_len - len(df)} rows")

    return df

def aggregation(path):
        
    path_files = common.get_path(path)

    print('Start filtering and aggregation:')
    for path in tqdm(path_files):
        df = pd.read_csv(path)
        filename = common.get_filename(path)
        logging.debug(f"File {filename} start fitering and aggreagation")
        df = filter_data(df)

        # Create date-hour colomn
        df['date_hour'] = [datetime(item.year, item.month, item.day, item.hour) 
                             for item in  df.tpep_pickup_datetime]

        # Group by on date_hour and region
        data_group = df.groupby(['date_hour', 'region']).size().reset_index(name='count')

        data_group.to_csv('data_aggregation/' + filename + '.csv')

        logging.debug(f"File {filename} is ready \n")

if __name__ == "__main__":

    path = common.yaml_load()['taxi_data']

    aggregation(path)


