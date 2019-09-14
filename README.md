# live-twitter-data-sentiment-analysis-using-dash

This application analyzes the sentiments of live tweets from twitter by classifying them as positive and negative tweets using VaderSentiment and then visualizes the live sentiment trend of the search words using a dashboard build using Python's Dash.

- `tweepy` library is used for tweet extraction using a Twitter API
- `textblob` library is used for sentiment analysis using the tweets
- `dash` package is used to generate a real-time graphing dashboard of the live tweets

# Quick start
## Installation
- Clone repo
- install `requirements.txt` using pip install -r requirements.txt

## Setup
> Fill in your Twitter App credentials to twitter_stream.py. Go to [this](apps.twitter.com) link to set that up if you need to. A detailed explanation is given below
- Sign up for a Twitter [developer account](https://developer.twitter.com/). 
- Create an application [here](https://developer.twitter.com/en/apps).
- Set the following keys in `twitterApiSetup.py`. You can get these values from the app you created:
- `CONSUMER_KEY`
- `CONSUMER_SECRET`
- `TWITTER_APP_KEY`
- `TWITTER_APP_SECRET`

> Run `twitter_stream.py` to build database

> If you're using this locally, you can run the application with the `dev_server.py` script

> You might need the latest version of sqlite.
