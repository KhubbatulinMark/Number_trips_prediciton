########################################################################
# import python-library
########################################################################
# default
import sys
import os
import glob
from datetime import datetime, date
# additional
import tqdm
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
# original lib
import common
########################################################################

path = common.yaml_load()['taxi_data']
extension = 'csv'