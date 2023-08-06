import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
import plotly.express as px
from datetime import datetime
import warnings
import matplotlib.pyplot as plt
from dataextractor import RaceDataExtractor

class RaceData(RaceDataExtractor):
  def __init__(self, year):
    self.year = year
    super().__init__(year)
    self.raw_data = super().getAllraces()
    self.wdcPlot_df = None

  def getWDC(self):
    race_df = self.raw_data
    wdc_df = pd.pivot_table(race_df, index=['Car', 'Driver'], columns=['race_num', 'Location']).fillna('0')['PTS'].astype(int)
    pts_ls = []
    for column in wdc_df.columns:
      pts = wdc_df.loc[:,:column].sum(axis=1)
      pts_ls.append(pts)
    k = 1
    i = 0
    for column in wdc_df.columns:
      wdc_df.insert(loc=k, column=(column[0], 'Total PTS'), value=pts_ls[i])
      i = i + 1
      k = k + 2
    return wdc_df

  def plotWDC(self):
    wdc_df = self.getWDC()
    wdc_df = (
        wdc_df
        .reset_index()
        .drop(columns='Car')
        .set_index('Driver')
        .transpose()
        .reset_index()
        .drop(columns='race_num')
        .set_index('Location')
        .transpose()
    )
    # points = wdc_df['Total PTS']
    races = wdc_df.drop(columns='Total PTS').columns
    wdc_df = wdc_df.drop(columns=races)
    wdc_df.columns = races
    wdc_df = wdc_df.transpose()
    for col in wdc_df.columns:
      if pd.DataFrame(wdc_df[col]).shape[1] > 1:
        new_vals = wdc_df[col].sum(axis=1)
        wdc_df.drop(columns=col, inplace=True)
        wdc_df[col] = new_vals
    fig = px.line(
        (
            wdc_df.transpose()
            .sort_values(by=wdc_df.index[-1], ascending=False)
            .transpose()
        ),
        markers=True
    )
    self.wdcPlot_df = wdc_df
    return fig
  
  def plot_quali(self, race_loc):
    race_data = self.raw_data[self.raw_data['Location'] == race_loc]
    quali_data = race_data[['Driver', 'Car', 'Q1', 'Q2', 'Q3']]
    quali_data['Q1'] = str_to_time(quali_data['Q1'])
    quali_data['Q2'] = str_to_time(quali_data['Q2'])
    quali_data['Q3'] = str_to_time(quali_data['Q3'])
    quali_data['Q1 int'] = time_to_int(quali_data['Q1'])
    quali_data['Q2 int'] = time_to_int(quali_data['Q2'])
    quali_data['Q3 int'] = time_to_int(quali_data['Q3'])
    temp_series = quali_data[quali_data['Q1 int'] != 0]
    quali_data['Q1 scale'] = (
        (temp_series['Q1 int'] - temp_series['Q1 int'].min())/
        (temp_series['Q1 int'].max() - temp_series['Q1 int'].min())
    )
    temp_series = quali_data[quali_data['Q2 int'] != 0]
    quali_data['Q2 scale'] = (
        (temp_series['Q2 int'] - temp_series['Q2 int'].min())/
        (temp_series['Q2 int'].max() - temp_series['Q2 int'].min())
    )
    temp_series = quali_data[quali_data['Q3 int'] != 0]
    quali_data['Q3 scale'] = (
        (temp_series['Q3 int'] - temp_series['Q3 int'].min())/
        (temp_series['Q3 int'].max() - temp_series['Q3 int'].min())
    )
    quali_construct = quali_data.groupby('Car').min().reset_index()
    figures = []

    #Plot Q1
    fig, ax = plt.subplots(figsize=(16, 9))
    ax2 = ax.twinx()
    pd.concat(
        [
            quali_data[['Driver', 'Q1 scale']][quali_data['Q1 scale'].isna()],
            quali_data[['Driver', 'Q1 scale']].dropna().sort_values(by='Q1 scale', ascending=False)            
        ]
    ).plot(kind='barh', x='Driver', ax=ax, label='Q1')
    quali_data['Q1 scale neg'] = - quali_data['Q1 scale']
    # quali_construct['Q1 scale neg'] = - quali_construct['Q1 scale']
    pd.concat(
        [
            quali_data[['Car', 'Q1 scale neg']][quali_data['Q1 scale neg'].isna()],
            quali_data[['Car', 'Q1 scale neg']].dropna().sort_values(by='Q1 scale neg')            
        ]
    ).plot(kind='barh', x='Car', ax=ax2, label='Q1')
    plt.plot([0, 0],[-220, 220], color='red')
    plt.plot([0.25, 0.25],[-220, 220], color='green', linestyle='dashed', label='<25% slower')
    plt.plot([-0.25, -0.25],[-220, 220], color='green', linestyle='dashed')
    plt.plot([0.5, 0.5],[-220, 220], color='blue', linestyle='dashed', label='<50% slower')
    plt.plot([-0.5, -0.5],[-220, 220], color='blue', linestyle='dashed')
    ax.legend()
    figures.append(fig)

    #Plot Q2
    fig2, ax = plt.subplots(figsize=(16, 9))
    ax2 = ax.twinx()
    pd.concat(
        [
            # quali_data[['Driver', 'Q2 scale']][quali_data['Q2 scale'].isna()],
            quali_data[['Driver', 'Q2 scale']].dropna().sort_values(by='Q2 scale', ascending=False)            
        ]
    ).plot(kind='barh', x='Driver', ax=ax, label='Q2')
    quali_data['Q2 scale neg'] = - quali_data['Q2 scale']
    # quali_construct['Q1 scale neg'] = - quali_construct['Q1 scale']
    pd.concat(
        [
            # quali_data[['Car', 'Q2 scale neg']][quali_data['Q2 scale neg'].isna()],
            quali_data[['Car', 'Q2 scale neg']].dropna().sort_values(by='Q2 scale neg')            
        ]
    ).plot(kind='barh', x='Car', ax=ax2, label='Q2')
    plt.plot([0, 0],[-220, 220], color='red')
    plt.plot([0.25, 0.25],[-220, 220], color='green', linestyle='dashed', label='<25% slower')
    plt.plot([-0.25, -0.25],[-220, 220], color='green', linestyle='dashed')
    plt.plot([0.5, 0.5],[-220, 220], color='blue', linestyle='dashed', label='<50% slower')
    plt.plot([-0.5, -0.5],[-220, 220], color='blue', linestyle='dashed')
    ax.legend()
    figures.append(fig2)

    #Plot Q3
    fig3, ax = plt.subplots(figsize=(16, 9))
    ax2 = ax.twinx()
    pd.concat(
        [
            # quali_data[['Driver', 'Q3 scale']][quali_data['Q3 scale'].isna()],
            quali_data[['Driver', 'Q3 scale']].dropna().sort_values(by='Q3 scale', ascending=False)            
        ]
    ).plot(kind='barh', x='Driver', ax=ax, label='Q3')
    quali_data['Q3 scale neg'] = - quali_data['Q3 scale']
    # quali_construct['Q1 scale neg'] = - quali_construct['Q1 scale']
    pd.concat(
        [
            # quali_data[['Car', 'Q3 scale neg']][quali_data['Q3 scale neg'].isna()],
            quali_data[['Car', 'Q3 scale neg']].dropna().sort_values(by='Q3 scale neg')            
        ]
    ).plot(kind='barh', x='Car', ax=ax2, label='Q3')
    plt.plot([0, 0],[-220, 220], color='red')
    plt.plot([0.25, 0.25],[-220, 220], color='green', linestyle='dashed', label='<25% slower')
    plt.plot([-0.25, -0.25],[-220, 220], color='green', linestyle='dashed')
    plt.plot([0.5, 0.5],[-220, 220], color='blue', linestyle='dashed', label='<50% slower')
    plt.plot([-0.5, -0.5],[-220, 220], color='blue', linestyle='dashed')
    ax.legend()
    figures.append(fig3)

    # pd.concat(
    #     [
    #         quali_data[['Driver', 'Q2 scale']].dropna().sort_values(by='Q2 scale'),
    #         quali_data[['Driver', 'Q2 scale']][quali_data['Q2 scale'].isna()]
    #     ]
    # ).plot.barh(stacked=True, ax=ax, x='Driver', color='red')#(kind='barh', x='Driver', ax=ax)
    return figures
    
  def compare_speed(self, race_loc):
      race_data = self.raw_data[self.raw_data['Location'] == race_loc]
      quali_data = race_data[['Driver', 'Car', 'Q1', 'Q2', 'Q3']]
      quali_data['Q1'] = str_to_time(quali_data['Q1'])
      quali_data['Q2'] = str_to_time(quali_data['Q2'])
      quali_data['Q3'] = str_to_time(quali_data['Q3'])
      quali_data['Q1 int'] = time_to_int(quali_data['Q1'])
      quali_data['Q2 int'] = time_to_int(quali_data['Q2'])
      quali_data['Q3 int'] = time_to_int(quali_data['Q3'])
      temp_series = quali_data[quali_data['Q1 int'] != 0]
      quali_data['Q1 scale'] = (
          (temp_series['Q1 int'] - temp_series['Q1 int'].min())
      )
      temp_series = quali_data[quali_data['Q2 int'] != 0]
      quali_data['Q2 scale'] = (
          (temp_series['Q2 int'] - temp_series['Q2 int'].min())
      )
      temp_series = quali_data[quali_data['Q3 int'] != 0]
      quali_data['Q3 scale'] = (
          (temp_series['Q3 int'] - temp_series['Q3 int'].min())
      )
      quali_construct = quali_data.groupby('Car').min().reset_index()
      figures = []

      #Plot Q1
      fig, ax = plt.subplots(figsize=(16, 9))
      ax2 = ax.twinx()
      pd.concat(
          [
              quali_data[['Driver', 'Q1 scale']][quali_data['Q1 scale'].isna()],
              quali_data[['Driver', 'Q1 scale']].dropna().sort_values(by='Q1 scale', ascending=False)            
          ]
      ).plot(kind='barh', x='Driver', ax=ax, label='Q1')
      quali_data['Q1 scale neg'] = - quali_data['Q1 scale']
      # quali_construct['Q1 scale neg'] = - quali_construct['Q1 scale']
      pd.concat(
          [
              quali_data[['Car', 'Q1 scale neg']][quali_data['Q1 scale neg'].isna()],
              quali_data[['Car', 'Q1 scale neg']].dropna().sort_values(by='Q1 scale neg')            
          ]
      ).plot(kind='barh', x='Car', ax=ax2, label='Q1')
      plt.plot([0, 0],[-220, 220], color='red')
      ax.legend()
      figures.append(fig)

      #Plot Q2
      fig2, ax = plt.subplots(figsize=(16, 9))
      ax2 = ax.twinx()
      pd.concat(
         [
              # quali_data[['Driver', 'Q2 scale']][quali_data['Q2 scale'].isna()],
              quali_data[['Driver', 'Q2 scale']].dropna().sort_values(by='Q2 scale', ascending=False)            
          ]
      ).plot(kind='barh', x='Driver', ax=ax, label='Q2')
      quali_data['Q2 scale neg'] = - quali_data['Q2 scale']
      # quali_construct['Q1 scale neg'] = - quali_construct['Q1 scale']
      pd.concat(
          [
              # quali_data[['Car', 'Q2 scale neg']][quali_data['Q2 scale neg'].isna()],
              quali_data[['Car', 'Q2 scale neg']].dropna().sort_values(by='Q2 scale neg')            
          ]
      ).plot(kind='barh', x='Car', ax=ax2, label='Q2')
      plt.plot([0, 0],[-220, 220], color='red')
      ax.legend()
      figures.append(fig2)

      #Plot Q3  
      fig3, ax = plt.subplots(figsize=(16, 9))
      ax2 = ax.twinx()
      pd.concat(
          [
              # quali_data[['Driver', 'Q3 scale']][quali_data['Q3 scale'].isna()],
              quali_data[['Driver', 'Q3 scale']].dropna().sort_values(by='Q3 scale', ascending=False)            
          ]
      ).plot(kind='barh', x='Driver', ax=ax, label='Q3')
      quali_data['Q3 scale neg'] = - quali_data['Q3 scale']
      # quali_construct['Q1 scale neg'] = - quali_construct['Q1 scale']
      pd.concat(
          [
              # quali_data[['Car', 'Q3 scale neg']][quali_data['Q3 scale neg'].isna()],
              quali_data[['Car', 'Q3 scale neg']].dropna().sort_values(by='Q3 scale neg')            
          ]
      ).plot(kind='barh', x='Car', ax=ax2, label='Q3')
      plt.plot([0, 0],[-220, 220], color='red')
      ax.legend()
      figures.append(fig3)

      # pd.concat(
      #     [
      #         quali_data[['Driver', 'Q2 scale']].dropna().sort_values(by='Q2 scale'),
      #         quali_data[['Driver', 'Q2 scale']][quali_data['Q2 scale'].isna()]
      #     ]
      # ).plot.barh(stacked=True, ax=ax, x='Driver', color='red')#(kind='barh', x='Driver', ax=ax)
      return figures
