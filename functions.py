# -*- coding: utf-8 -*-
"""all_functions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11nDcxSA2Rilh5diGn7jho8IEnvvhDDkW
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import re as re
import nltk
from nltk.tokenize import TweetTokenizer
import string
nltk.download('stopwords')
from nltk.corpus import stopwords
nltk.download('vader_lexicon')
from scipy import sparse
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from tqdm import tqdm

def scraper(since, until, hashtag):
  #import libraries
  # !pip install snscrape
  import pandas as pd
  import snscrape.modules.twitter as sntwitter
  # Creating list to append tweet data to

  #since='2021-09-21'
  #until='2021-09-22'
  #hashtag='AAPL'

  tweets_list2 = []
  data=pd.DataFrame()
  # Using TwitterSearchScraper to scrape data and append tweets to list
  for i,tweet in enumerate(sntwitter.TwitterSearchScraper('#'+str(hashtag)+' since:'+str(since)+'until:'+str(until)+'lang:en').get_items()):        # if i>5000:
        #     break
    tweets_list2.append([tweet.date, tweet.content])
        
    # Creating a dataframe from the tweets list above
  data = pd.DataFrame(tweets_list2, columns=['Datetime', 'Text'])
  data["Stockname"] = str(hashtag)
  date = until
  return [data, date, hashtag]




def data_cleaner(data, date, hashtag):
  

  df = data
  def split_date_time(series):
    L1=[]
    L2=[]
    for i in range(len(series)):
      date, time = str(df["Datetime"][i]).split(' ')
      L1.append(date)
      L2.append(time)
    df_1 = pd.DataFrame()
    df_1["Date"] = L1
    df_1["Time"] = L2
    return df_1
  df_1=split_date_time(df["Datetime"])
  df = df.merge(df_1, right_index=True, left_index=True)
  df.drop('Datetime', axis=1, inplace=True)
  df.drop('Time', axis=1, inplace=True)

  def pre_process(df):
    column=df["Text"]
    

    column = column.str.lower()                                                       # Lower Case
    column = column.apply(lambda x: re.sub(r'https?:\/\/\S+', '', x))                 # URL links
    column = column.apply(lambda x: re.sub(r"www\.[a-z]?\.?(com)+|[a-z]+\.(com)", '', x))       # URL Links
    column = column.apply(lambda x: re.sub(r'{link}', '', x))                         # Placeholders
    column = column.apply(lambda x: re.sub(r"\[video\]", '', x))                      # Placeholders
    column = column.apply(lambda x: re.sub(r'&[a-z]+;', '', x))                       # HTML Functions
    column = column.apply(lambda x: re.sub(r"[^a-z\s\(\-:\)\\\/\];='#]", '', x))      # Non Letters
    column = column.apply(lambda x: re.sub(r'@mention', '', x))                       # Mentions
    column = column.apply(lambda x: re.sub(r'\n', '', x))                             # \n
    column = column.apply(lambda x: re.sub(r'-', '', x))                              # -
    column = column.apply(lambda x: re.sub(r'(\s)#\w+', '', x))      # remove word starting from hashtag
    return column
  
  column=pre_process(df)
  df["clean_text"] = column

  def tokenizer(df):                    
  

    column = df["clean_text"]
    tknzr = TweetTokenizer()
    column = column.apply(tknzr.tokenize)

    PUNCUATION_LIST = list(string.punctuation)
    def remove_punctuation(word_list):
      """Remove punctuation tokens from a list of tokens"""
      return [w for w in word_list if w not in PUNCUATION_LIST]
    df['tokens'] = column.apply(remove_punctuation)
    return df

  df = tokenizer(df)

  
  import nltk
  nltk.download('stopwords')  
  from nltk.corpus import stopwords
  def remove_stopwords(x):
      return [y for y in x if y not in stopwords.words('english')]

  df['temp_list1'] = df['tokens'].apply(lambda x : remove_stopwords(x))
  

  from nltk.corpus import stopwords
  stopwords = set('rt')
  stopwords.update(['retweet', 'RT', 'Retweet', 'RETWEET', 'rt', 'plz', 'tsla','tesla','stock','#tsla','elonmusk','apple','#wallstreetbets','reddit','wsbchairman','aapl','#aapl','microsoft'])
  l=[]
  for i in df.temp_list1:
    t = " ".join(review for review in i)
    l.append(t)
  df["temp_list2"] = l
  textt = " ".join(review for review in df.temp_list2)

  sid = SentimentIntensityAnalyzer()
  ss=[]
  for k in tqdm(df.temp_list2):
    # print(k)
    ss.append(sid.polarity_scores(k))
  neg=[]
  pos=[]
  neu=[]
  compound=[]
  for i in tqdm(range(df.temp_list2.shape[0])):
    neg.append(ss[i]["neg"])
    pos.append(ss[i]["pos"])
    neu.append(ss[i]["neu"])
    compound.append(ss[i]["compound"])
  sia_table = pd.DataFrame()
  sia_table["sia_pos"] = pos
  sia_table["sia_neu"] = neu
  sia_table["sia_neg"] = neg
  sia_table["sia_compound"] = compound

  sentiment=[]
  for i in ss:
    if i['compound'] >= 0.05 :
      sentiment.append("Positive")

    elif i['compound'] <= - 0.05 :
      sentiment.append("Negative")

    else :
      sentiment.append("Neutral")
  df["Sentiment"] = sentiment

  neg=0
  pos=0
  neu=0
  pos_count=[]
  neg_count=[]
  neu_count=[]
  if df.Sentiment[0] == 'Positive':
    pos+=1
    pos_count.append(pos)
    neg_count.append(neg) 
    neu_count.append(neu)
  elif df.Sentiment[0] == 'Negative':
    neg+=1
    pos_count.append(pos)
    neg_count.append(neg) 
    neu_count.append(neu)
  elif df.Sentiment[0] == 'Neutral':
    neu+=1
    pos_count.append(pos)
    neg_count.append(neg) 
    neu_count.append(neu)
  for i in range(1,len(df.Date)):   
    if df.Date[i] == df.Date[i-1]:
      if df.Sentiment[i] == 'Positive':
        pos = pos + 1 
        pos_count.append(pos)
        neg_count.append(neg) 
        neu_count.append(neu)
      elif df.Sentiment[i] == 'Negative':
        neg = neg + 1
        neg_count.append(neg)
        pos_count.append(pos)
        neu_count.append(neu)
      elif df.Sentiment[i] == 'Neutral':
        neu = neu + 1
        neu_count.append(neu)
        neg_count.append(neg)
        pos_count.append(pos)
    elif df.Date[i] != df.Date[i-1]:
      neg=0
      pos=0
      neu=0
      if df.Sentiment[i] == 'Positive':
        pos+=1
        pos_count.append(pos)
        neg_count.append(neg) 
        neu_count.append(neu)
      elif df.Sentiment[i] == 'Negative':
        neg+=1
        pos_count.append(pos)
        neg_count.append(neg) 
        neu_count.append(neu)
      elif df.Sentiment[i] == 'Neutral':
        neu+=1
        pos_count.append(pos)
        neg_count.append(neg) 
        neu_count.append(neu)
    
  df.pos_count = pos_count
  df.neg_count = neg_count
  df.neu_count = neu_count


  new_df = pd.DataFrame()
  new_df["Date"] = 0
  new_df["pos_count"]=0
  new_df["neu_count"]=0
  new_df["neg_count"]=0
  stockname=[]
  Date=[]
  pos_count=[]
  neg_count=[]
  neu_count=[]
  total_count=[]

  for i in range(len(df.Date)-1):
    # i = k -  len(df.Date)
    if df.Date[i] != df.Date[i+1]:
      a = df.Date[i]
      Date.append(a)
      z= df.Stockname[i]
      stockname.append(z)
      b = df.pos_count[i]
      pos_count.append(b)
      c = df.neg_count[i]
      neg_count.append(c)
      d = df.neu_count[i]
      neu_count.append(d)
      e=b+c+d
      total_count.append(e)
  new_df["Date"] = Date
  new_df["Stockname"] = stockname
  new_df["pos_count"]=pos_count
  new_df["neu_count"]=neu_count
  new_df["neg_count"]=neg_count
  new_df["total_count"]=total_count

  year=[]
  month=[]
  day=[]
  for i in range(new_df.shape[0]):
    A,B,C = new_df.Date[i].split('-')
    # print(str(df1.iloc[i,0]).split(' ')[0].split('-')[1],'   ', i)
    year.append(A)
    month.append(B)
    day.append(C)
  new_df["Year"] = year
  new_df["Month"] = month
  new_df["Day"] = day
  # new_df.drop('Date',axis=1, inplace=True)
  new_df = new_df.sort_values(by='Date')
  new_df.head()

  
  import yfinance as yf
    
  df1 = yf.download(tickers=hashtag, period='30d', interval='1d', rounding ="True",   )
  year=[]
  month=[]
  day=[];
  for i in range(len(df1.index)):
    year.append((str(df1.index[i])).split(' ')[0].split('-')[0])
    month.append((str(df1.index[i])).split(' ')[0].split('-')[1])
    day.append((str(df1.index[i])).split(' ')[0].split('-')[2])
  #   year.append(a)
  #   month.append(b)
  #   day.append(c)
  df1["Stockname"] = hashtag
  df1["Year"] = year
  df1["Month"] = month
  df1["Day"] = day
  
  df_all = new_df.merge(df1, how='left', on=['Day', 'Month', 'Year','Stockname'])
  df_all = df_all[['Day','Month','Year','Stockname','pos_count','neu_count','neg_count','total_count','Close','Volume','Open','High','Low']]
  df_all = df_all.sort_values(['Year','Month','Day'])

  A = df_all.groupby(by='Stockname')
  l1 = ["NVDA","AAPL","MSFT","TSLA","PYPL"]
  l2=[ [] for i in range(len(l1)) ]
  for i in range(len(l1)):
    try:
      l2[i] = A.get_group(l1[i]).interpolate(method='linear', limit_direction='backward')
    except:
      continue
  df_merge = pd.DataFrame()
  for i in l2:
    df_merge = df_merge.append(i, ignore_index=True)
  
  #df_merge['Date_x']=pd.to_datetime(df_merge['Date_x'])
  df_merge = df_merge.sort_values(by=['Year','Month','Day'])
  df_merge.dropna(axis=0, how='any', thresh=None, subset=None, inplace=True)
  
  return df_merge


