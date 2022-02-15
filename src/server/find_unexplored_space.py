from random import randrange
from scipy import spatial
import pandas as pd
import numpy as np

def find_unexplored_space(df):
    
    df = df[['gps_lat','gps_long']].copy()
    center = np.around(df.mean().values, decimals=4)
    dist = abs(df - center).max().values
    dlat = round(dist[0]/0.0001)
    dlon = round(dist[1]/0.0001)

    mb = []
    for i in range((dlat*2)+1):
        for j in range((dlon*2)+1):
            mb.append([center[0]+ (i-dlat)*0.0001, center[1]+ (j-dlon)*0.0001])

    d = []
    t = []
    for i in range(len(mb)):
        a,b = spatial.KDTree(df.values).query(mb[i])
        d.append(a)
        t.append(b)

    max = np.max(d)
    id = d.index(max)
    return mb[id]