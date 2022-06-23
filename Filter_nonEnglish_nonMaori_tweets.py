import csv

INDEX_TWEET_ID 				= 0			
INDEX_URL					= 1
INDEX_USER_ID				= 2
INDEX_DATE					= 3
INDEX_MODIFIED_TEXT			= 4
INDEX_CONVERSATION_ID		= 5
INDEX_IN_REPLY_TO_USER_ID	= 6
INDEX_REF_TWEET_ID			= 7
INDEX_REF_TWEET_TYPE		= 8
INDEX_GEO					= 9
INDEX_LANG					= 10
INDEX_SOURCE				= 11
# --
INDEX_LIKE_COUNT			= 12
INDEX_QUOTE_COUNT			= 13
INDEX_REPLY_COUNT			= 14
INDEX_RETWEET_COUNT			= 15
INDEX_MAORI_WORDS			= 16
INDEX_NUM_MAORI_WORDS		= 17
INDEX_TOTAL_WORDS			= 18
INDEX_PERCENT_MAORI			= 19
INDEX_FAVOURITES			= 20
INDEX_YEAR					= 21
INDEX_ERROR					= 22
INDEX_MEDIA					= 23
INDEX_OUTLINKS				= 24

ACCENTS = ['á','Á','à','À','â','Â','ä','Ä','ã','Ã','å','Å','æ','Æ','ç','Ç','é','É','è','È','ê','Ê','ë','Ë','í','Í','ì','Ì','î','Î','ï','Ï','ñ','Ñ','ó','Ó','ò','Ò','ô','Ô','ö','Ö','õ','Õ','ø','Ø','œ','Œ','ß','ú','Ú','ù','Ù','û','Û','ü','Ü']


USERS_FIRST_100  = [
	'123456789',
	'123456789',
	'123456789'
]

USERS_LAST_100  = [
	'123456789',
	'123456789',
	'123456789'
]

USERS_MIDDLE_100 = [
	'123456789'
]

USERS_BOTTOM_MIDDLE_100 = [
	'123456789',
	'123456789'
]

USERS_TOP_MIDDLE_100 = [
]

USERS_APOSTROPHE = [
	'123456789',
	'123456789',
	'123456789',
	'123456789',
	'123456789',
	'123456789',
	'123456789'
]

USERS  = USERS_FIRST_100 + USERS_LAST_100 + USERS_MIDDLE_100 + USERS_BOTTOM_MIDDLE_100 + USERS_TOP_MIDDLE_100 + USERS_APOSTROPHE

COUNTS = [0 for user in USERS]
FILES  = [open("output_"+user+".csv", "w", encoding='utf-8') for user in USERS]

tweets = [];

tweets_cleaned = [];

file_in = 'dataset_dd_mm_prev.csv'
file_out_cleaned_formatted = "dataset_dd_mm_new.csv"

with open(file_in, encoding='utf-8') as csvfile:
	csvreader = csv.reader(csvfile)
	for row in csvreader:
		tweets.append(row)

header = tweets[0]
tweets = tweets[1:]

file_out_cleaned = open("output_cleaned.csv", "w", encoding='utf-8')
file_out_original = open("output_original.csv", "w", encoding='utf-8')
for tweet in tweets:

	if len(tweet) != 26:
		print(tweet)
		pass

	content = tweet[INDEX_MODIFIED_TEXT] 

	# for accent in ACCENTS:
	# 	if accent in content:
	# 		print("ACCENTS")
	# 		break;

	exclude = False
	for i in range(0,len(USERS)):
		if tweet[INDEX_USER_ID] == (USERS[i]+'\''):
			COUNTS[i] += 1
			print(tweet[INDEX_TWEET_ID], tweet[INDEX_USER_ID], tweet[INDEX_MODIFIED_TEXT], sep=',', file=FILES[i])
			exclude = True
	
	if not exclude:
		tweets_cleaned.append(tweet)
		print(tweet[INDEX_TWEET_ID], tweet[INDEX_USER_ID], tweet[INDEX_MODIFIED_TEXT], sep=',', file=file_out_cleaned)

	print(tweet[INDEX_TWEET_ID], tweet[INDEX_USER_ID], tweet[INDEX_MODIFIED_TEXT], sep=',', file=file_out_original)


for i in range(0,len(USERS)):
	print("count_user_"+USERS[i], COUNTS[i])

print("tweets removed: ", (len(tweets)-len(tweets_cleaned)))
print("old dataset size: ", len(tweets))
print("new dataset size: ", len(tweets_cleaned))

tweets_cleaned = [header] + tweets_cleaned
with open(file_out_cleaned_formatted, 'w', encoding='utf-8',newline='') as csvfile:
		csvwriter = csv.writer(csvfile)
		for tweet in tweets_cleaned:
			csvwriter.writerow(tweet)


	
