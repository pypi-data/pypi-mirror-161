import pandas as pd
import numpy as np

#data cleaning

#combine dataframes, take a range of years, and drop unnecessary columns
def comb_drop(*dataframes, start_date='0', end_date='9999', date_col=-1, drop_col):
    frame = pd.concat(dataframes)
    if (date_col != -1):
        frame = frame[(frame[date_col].astype(str) >= start_date) & (frame[date_col].astype(str) <= end_date)]
    frame = frame.drop(columns=drop_col).reset_index(drop=True)
    return frame

#create a new column which calculates the change in an existing column
#'id_col' allows change to be calculated only between adjacent rows with the same id
def calc_change(*dataframes, old_col, new_col, id_col=-1):
    for frame in dataframes:
        frame[new_col] = 0
        for i in range(1, len(frame)):
            if (id_col != -1):
                if (frame.loc[i, id_col] == frame.loc[(i-1), id_col]):
                    frame.loc[i, new_col] = frame.loc[i, old_col] - frame.loc[(i-1), old_col]
            else:
                frame.loc[i, new_col] = frame.loc[i, old_col] - frame.loc[(i-1), old_col]
    if (len(dataframes) == 1):
        return dataframes[0]
    else:
        return dataframes

#granularity regulation

#annual to quarterly interpolation using a (positively or negatively) correlated, quarterly dataset
#adds new column to dataframe with quarterly projection
def atq_cor_interp(df, year_col, data_col, quar_col, new_col_loc=-1, new_col_name='proj_data', cor_type=0):
    a = df.groupby(year_col).mean()[quar_col]
    if (new_col_loc != -1):
        df.insert(new_col_loc, new_col_name, 0)
    else:
        df[new_col_name] = 0
    for i in range(len(df)):
        b = int(np.floor(i/4))
        c = (df.loc[i, quar_col]/a.iloc[b])*(df.loc[i, data_col])
        if (cor_type == 0):
            df.loc[i, new_col_name] = c
        else:
            df.loc[i, new_col_name] = df.loc[i, data_col] + (df.loc[i, data_col] - c)
    return df

#quarterly to monthly linear interpolation
#'add_month' will add a column with the month of each row, labeled 'month'
def qtm_lin_interp(dataframe, col_name, add_month=False, add_month_index=0):
    df = pd.concat([dataframe, dataframe, dataframe]).sort_index().reset_index(drop=True)
    if add_month:
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        month_list = (months*(len(df) + 1))[:len(df)]
        df.insert(add_month_index, 'month', month_list)
    c = 0
    d = df.columns.get_loc(col_name)
    for i in range((len(df) - 3)):
        if ((i % 3) == 0):
            if df.iloc[i, d] > df.iloc[i+3, d]:
                a = (df.iloc[i, d] - df.iloc[i+3, d])/3
                df.iloc[i+1, d] = df.iloc[i+1, d] - a
                df.iloc[i+2, d] = df.iloc[i+2, d] - (2*a)
                c = -a
            else:
                b = (df.iloc[i+3, d] - df.iloc[i, d])/3
                df.iloc[i+1, d] = df.iloc[i+1, d] + b
                df.iloc[i+2, d] = df.iloc[i+2, d] + (2*b)
                c = b
    #need to make a special case for the last two entries
    df.iloc[(len(df) - 2), d] = df.iloc[(len(df) - 2), d] + c
    df.iloc[(len(df) - 1), d] = df.iloc[(len(df) - 1), d] + (2*c)
    return df



