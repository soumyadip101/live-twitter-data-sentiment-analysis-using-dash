import twitterApiSetup
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import json
import sqlite3
from textblob import TextBlob
from unidecode import unidecode
from threading import Lock, Timer


# isolation lever disables automatic transactions,
# we are disabling thread check as we are creating connection here, but we'll be inserting from a separate thread (no need for serialization)
conn = sqlite3.connect('twitter.db', isolation_level=None, check_same_thread=False)
c = conn.cursor()

def create_table():
	try:
		# it allows concurrent write and reads
		c.execute("PRAGMA journal_mode=wal")
		c.execute("PRAGMA wal_checkpoint=TRUNCATE")
		c.execute("CREATE TABLE IF NOT EXISTS sentiment(id INTEGER PRIMARY KEY AUTOINCREMENT, unix INTEGER, tweet TEXT, sentiment REAL)")
		# id on index, both as DESC (as we are sorting in DESC order)
		c.execute("CREATE INDEX id_unix ON sentiment (id DESC, unix DESC)")
		
	except Exception as e:
		print(str(e))
create_table()
		# conn.commit()
lock = Lock()

create_table()

ckey = twitterApiSetup.CONSUMER_KEY
csecret = twitterApiSetup.CONSUMER_SECRET
atoken = twitterApiSetup.TWITTER_APP_KEY
asecret = twitterApiSetup.TWITTER_APP_SECRET

class Listener(StreamListener):

	data = []
	lock = None

	def __init__(self, lock):

        # create lock
		self.lock = lock
        # init timer for database save
		self.save_in_database()
        # call __inint__ of super class
		super().__init__()

	def save_in_database(self):
		# set a timer (1 second)
		Timer(1, self.save_in_database).start()
        # with lock, if there's data, save in transaction using one bulk query
		with self.lock:
			if len(self.data):
				c.execute('BEGIN TRANSACTION')
				try:
					c.executemany("INSERT INTO sentiment (unix, tweet, sentiment) VALUES (?, ?, ?)", self.data)
				except:
					pass
				c.execute('COMMIT')
				self.data = []

	def on_data(self, text):
		try:
			data = json.loads(text)
            # there are records which need to be ignored like:
            # {'limit': {'track': 14667, 'timestamp_ms': '1520216832822'}}
			if 'truncated' not in data:
				return True
			if data['truncated']:
				tweet = unidecode(data['extended_tweet']['full_text'])
			else:
				tweet = unidecode(data['text'])
			time_ms = data['timestamp_ms']
			analysis = TextBlob(tweet)
			sentiment = analysis.sentiment.polarity
			# print(time_ms, tweet, sentiment)

			# append to data list (to be saved every 1 second)
			with self.lock:
				self.data.append((time_ms, tweet, sentiment))

		except KeyError as e:
            #print(data)
			print(str(e))
		return True

	def on_error(self, status):
		print(status)

# Authentication for connecting to twitter api
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
# Extract live tweet feed from twitter
twitterStream = Stream(auth, Listener(lock))
twitterStream.filter(track=["a","e","i","o","u"])


