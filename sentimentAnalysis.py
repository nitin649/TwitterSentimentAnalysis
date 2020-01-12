from tweepy.streaming import StreamListener
from tweepy import API
#from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import re
from textblob import TextBlob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import credential_twitter #in this file we save our keys

# # #  Twitter Client # # #
class  TwitterClient():
    def __init__(self,twitter_user=None):
        self.auth=TwitterAuthenticator().authenticate_twitter_app()
        #print(self.auth)
        self.twitter_client=API(self.auth)
        self.twitter_user=twitter_user

    def get_twitter_client_api(self):
        #return client
        return self.twitter_client
        

    def get_user_timeline_tweets(self,num_tweets):
        tweets=[]
        
        for tweet in tweepy.Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):
           # print('ehhihi')
            print(tweet)
            tweets.append(tweet)
        return tweets
    ### for freinds timeline tweets##########

    def get_friend_timeline_tweets(self,num_tweets):
        friend_list=[]
        for tweet in tweepy.Cursor(self.twitter_client.freinds,id=self.twitter_user).items(num_tweets):
            friend_list.append(tweet)

        return friend_list

    ###for homeline tweets######
    def get_homeline_tweets(self,num_tweets):
        homeline_tweets=[]
        for tweet in tweepy.Cursor(self,twitter_client.homeline_timeline,id=self.twitter_user).items(num_tweets):
            homeline_tweets.append(tweet)
        return homeline_tweets
            





# # #Twitter Authentication # # # 
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth=OAuthHandler(credential_twitter.CONSUMER_KEY,credential_twitter.CONSUMER_SECRET)#doing authentication using our keys
        auth.set_access_token(credential_twitter.ACCESS_TOKEN,credential_twitter.ACCESS_TOKEN_SECRET)
        return auth
        
    
# # # Twitter Streamer # # #    
class TwitterStreamer():
    """this class handles twitter authentication and the connection to the twitter
        streaming api"""
    def __init__(self):
        self.twitter_authenticator=TwitterAuthenticator()#creating Twitter authenticator class object
    def stream_tweets(self,tweets_save,list_cat):
        listener=TwitterListener(tweets_save)#creating object of StdOutlistener class
        #auth=OAuthHandler(credential_twitter.CONSUMER_KEY,credential_twitter.CONSUMER_SECRET)#doing authentication using our keys
        #auth.set_access_token(credential_twitter.ACCESS_TOKEN,credential_twitter.ACCESS_TOKEN_SECRET)
        auth=self.twitter_authenticator.authenticate_twitter_app()
    
        stream=Stream(auth,listener)

        stream.filter(track=list_cat)#this method filter our tweets based on the list of categories we give


# # # twitter Stream Listener # # #

class TwitterListener(StreamListener):#inhert from streamlistener
    """this a basic class that just prints received tweets to stdout"""

    def __init__(self,tweets_save):
        self.tweets_save=tweets_save #creating file where we save our tweets

    def on_data(self,data):#this method is overidden from streamlistener class which is used printing
        try:
            print(data)
            with open(self.tweets_save,'a') as file:
                file.write(data)
            return True
         #if everthing  is good then return True
        except BaseException as e:
            print(str(e))
        return True
    def on_error(self,status):#this method also overiddent from streamlistener class it wiil give error if something is going wrong
        if status==420:
            #returning false on_data method in case rate limit occurs
            return False
        print(status)

#### class for analyzing the data#####
class TweetAnalyze():

    #function for calculate the polarity whether it is positive or negative
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1
    #functionality for analyzing and categorizing content from tweets##
    def tweet_to_dataFrame(self,tweets):
        df=pd.DataFrame(data=[tweet.text for tweet in tweets],columns=['Tweets'])

        df['id']=np.array([tweet.id for tweet in tweets])
        df['len']=np.array([len(tweet.text) for tweet in tweets])
        df['date']=np.array([tweet.created_at for tweet in tweets])
        df['source']=np.array([tweet.source for tweet in tweets])#it gives from where the tweet comes from (android,ios etc)
        df['likes']=np.array([tweet.favorite_count for tweet in tweets])
        df['retweets']=np.array([tweet.retweet_count for tweet in tweets])

        return df
    

if __name__=="__main__":
    twitter_client=TwitterClient()
    tweet_analyzer=TweetAnalyze()
    api=twitter_client.get_twitter_client_api()
    print(api)
    tweets=api.user_timeline(screen_name='narendramodi',count=100)
    #print(tweets[0].id) #this method gives us what all method we can implement on tweets
    #print(tweets)
    df=tweet_analyzer.tweet_to_dataFrame(tweets)

    df['sentiments']=np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['Tweets']])
    #get the  number of likes for the most liked tweet
    print(np.max(df['likes']))

    #get average lenght over all tweets
    print(np.mean(df['len']))

    #get the number of retweets for the most retweeted tweet
    print(np.max(df['retweets']))
    print(df.head(10))

    #Time series for plotting
    """time_likes=pd.Series(data=df['likes'].values,index=df['date'])
    time_likes.plot(figsize=(15,4),label='likes',color='r',legend=True)
    
    time_retweets=pd.Series(data=df['retweets'].values,index=df['date'])
    time_retweets.plot(figsize=(15,4),label='retweets',color='b',legend=True)
    
    plt.show()"""



   
  
