#!/usr/bin/python3
"""
Code for collecting and pre-processing Māori-English tweets.

This script requires access to a Twitter Developer Account, and to the nga-kupu
repository (https://github.com/TeHikuMedia/nga-kupu). By default, only tweets 
from the past week are collected. 

After all tweets have been collected, any words that the RMT system considers 
to be Māori are added to each tweet. These are words that are consistent with 
Māori syllable structure, but which may not actually be Māori. 

The individual tokens in each tweet are extracted, following the removal 
of @user mentions, links, #hashtags and punctuation.
"""

import csv
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import dateutil.parser
import html
import json
import os
import pandas as pa
import re
import requests
import string
from string import printable
from taumahi import kōmiri_kupu, nahanaha
import time
from twokenize import tokenizeRawTweetText
import pickle
from emot.emo_unicode import UNICODE_EMOJI
from utilities import Convert, remove_punc, remove_emoticons, strip_all_entities, save_hashtags

##########################################################################
#COLLECT TWEETS 
#This code is adapted from Twitter's API v2 sample code
#https://github.com/twitterdev/Twitter-API-v2-sample-code
##########################################################################

#To set your environment variables in your terminal run the following line:
#export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")

def create_url(user_id):
    return "https://api.twitter.com/2/users/{}/tweets".format(user_id)

def get_params(start_date, end_date, max_results, next_token):
    #Tweet fields can be edited
    #We remove retweets
    #See https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-tweets     
    fields = {"tweet.fields":"text,conversation_id,in_reply_to_user_id,referenced_tweets,author_id,created_at,lang,source,public_metrics", 
              "start_time":start_date, 
              "end_time":end_date, 
              "exclude":"retweets",
              "max_results":max_results,
              "expansions":"author_id,geo.place_id,in_reply_to_user_id",
              "pagination_token":next_token
              }
    return fields

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserTweetsPython"
    return r

def connect_to_endpoint(url, params, f):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    print("Code {}".format(response.status_code), file=f)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def append_to_csv(json_response, filename):
    csvFile = open(filename, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    #Loop through each tweet
    for tweet in json_response['data']:
        #Create a variable for each field
        tweet_id = tweet['id'] + "'"
        url = "https://twitter.com/X/status/" + tweet_id.replace("'","")
        user_id = tweet['author_id'] + "'"
        date = dateutil.parser.parse(tweet['created_at'])
        tweet['text'] = tweet['text'].replace("\n"," ")
        tweet['text'] = tweet['text'].replace("\r"," ")
        content = tweet['text']    
        conversation_id = tweet['conversation_id'] + "'"
        if('in_reply_to_user_id' in tweet):
            in_reply_to_user_id = tweet['in_reply_to_user_id'] + "'"  
        else:
            in_reply_to_user_id = "N/A"
        if('referenced_tweets' in tweet):
            ref_tweet_id = tweet['referenced_tweets'][0]['id'] + "'"
            ref_tweet_type = tweet['referenced_tweets'][0]['type']
        else:
            ref_tweet_id = "N/A"
            ref_tweet_type = "N/A"
        if ('geo' in tweet):   
            geo = tweet['geo']['place_id']
        else:
            geo = "N/A"
        lang = tweet['lang']
        source = tweet['source']                        
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']                          
        reply_count = tweet['public_metrics']['reply_count']
        retweet_count = tweet['public_metrics']['retweet_count']
        #Assemble all data in a list
        res = [tweet_id, url, user_id, date, content, conversation_id, 
               in_reply_to_user_id, ref_tweet_id, ref_tweet_type, geo, lang, 
               source, like_count, quote_count, reply_count, retweet_count]
        #Append the result to the CSV file
        csvWriter.writerow(res)
    #When done, close the CSV file
    csvFile.close()

def query_user(user_id, batch_number, f, start_date, end_date, filename):
    RATE_LIMIT = 300
    #Total number of tweets we collected from the loop
    total_tweets = 0    
    #Count tweets in batch    
    count = 0 
    flag = True
    next_token = None    
    max_count = 100
    # Check if flag is true
    while flag:
        url = create_url(user_id)
        params = get_params(start_date, end_date, max_count, next_token)
        json_response = connect_to_endpoint(url, params, f)
        #If user doesn't exist
        if 'meta' not in json_response:
            batch_number += 1
            print("B{}: 0 tweets".format(batch_number))
            break
        result_count = json_response['meta']['result_count']
        if 'next_token' in json_response['meta']:
            batch_number += 1
            #Save the token to use for next call
            next_token = json_response['meta']['next_token']
            if result_count is not None and result_count > 0 and next_token is not None:
                print(json.dumps(json_response, indent=4, sort_keys=True),file=f)
                append_to_csv(json_response, filename + ".csv")
                count += result_count
                total_tweets += result_count
                print("Batch {}: {} tweets".format(batch_number, result_count))
        #If no next token exists
        else:
            if result_count is not None and result_count > 0:
                batch_number += 1
                print(json.dumps(json_response, indent=4, sort_keys=True),file=f)
                append_to_csv(json_response, filename + ".csv")
                count += result_count
                total_tweets += result_count
                print("B{}: {} tweets".format(batch_number, result_count))
            #Since this is the final request, turn flag to false to move to the next time period.
            flag = False
            next_token = None
        if(batch_number != 0 and batch_number % RATE_LIMIT == 0):
            print("Sleeping for 15 minutes...")
            time.sleep(900)
        if(total_tweets == 0):
            batch_number += 1
    print("User total: {} tweets".format(total_tweets))
    return batch_number

"""
Calculate dates for the past week.
"""
def calc_dates(DURATION):
    #https://thispointer.com/python-how-to-get-current-date-and-time-or-timestamp/
    #https://thispointer.com/how-to-subtract-days-from-a-date-in-python/    
    #First, get the current date and time (UTC)
    dateTimeObj = datetime.now(tz=timezone.utc)    
    #Calculate the date one week prior
    start_date = dateTimeObj - timedelta(days=DURATION)    
    start_date2 = start_date.strftime("%Y-%m-%dT00:00:01Z")
    filename = start_date.strftime("%Y-%m-%d")
    end_date = dateTimeObj.strftime("%Y-%m-%dT00:00:00Z")
    #Example date: 2017-07-10T16:00:00Z
    return start_date2, end_date, filename

##########################################################################
#CLEAN TWEETS
##########################################################################
    
def format_data(input_file):
    output_file = input_file.replace(".csv", "-new.csv")
        
    tweets = remove_special_chars(input_file)
    tweets.to_csv(output_file, sep=",", header = True, index = False)
    
    tweets = remove_short_tweets(output_file)
    tweets.to_csv(output_file, sep=",", header = True, index = False)
    
    tweets = decode_html_links(output_file)
    tweets.to_csv(output_file, sep=",", header = True, index = False)
        
    tweets = standardise_user_mentions(output_file)
    tweets.to_csv(output_file, sep=",", header = True, index = False)
    
    content = tweets.pop("modified_text")
    tweets.insert(4, content.name, content) 
    tweets.to_csv(output_file, sep="\t", header = True, index = False)

#Strips emojis and other special characters from tweets.
#Removes tweets containing accented characters.
def remove_special_chars(input_file):
    tweets = pa.read_csv(input_file, sep=",")
    good_tweets = []
    original_length = len(tweets)
    #Remove tweets containing accents as these are likely to be foreign tweets
    tweets = tweets[tweets["content"].str.contains(r"[áÁàÀâÂäÄãÃåÅæÆçÇéÉèÈêÊëËíÍìÌîÎïÏñÑóÓòÒôÔöÖõÕøØœŒßúÚùÙûÛüÜẼẽĨĩũŨ]") == False]
    new_length = len(tweets)
    accent_tweets = original_length - new_length
    print(str(accent_tweets) + " accented tweets removed")
    tweets['modified_text'] = tweets['content']
    for tweet in tweets['modified_text']:
        tweet = tweet.replace("\\'","'")
        macrons = "ĀāĒēĪīŌōŪ"
        permitted_chars = printable + macrons
        tweet = "".join(c for c in tweet if c in permitted_chars) 
        spaces = re.compile(r" {2,}")
        tweet = spaces.sub(r" ", tweet)
        speechmarks = re.compile(r'"{1,}')
        tweet = speechmarks.sub(r"'", tweet)
        good_tweets.append(tweet)
    #Insert new column with decoded text
    tweets['modified_text'] = good_tweets
    return tweets

#Removes tweets comprising fewer than four tokens (words).
def remove_short_tweets(input_file):
    #Read the CSV file passed in
    tweets = pa.read_csv(input_file, sep=",", lineterminator='\n')
    #Index of the tweet
    pos = 0
    #Num short tweets removed
    num_removed = 0
    #To avoid type error
    tweets['modified_text'] = tweets['modified_text'].apply(str)
    #For each tweet
    for tweet in tweets['modified_text']:
        #Count number of tokens in tweet after removing @user mentions, 
        #hashtags, URLs and punctuation. 
        #Emojis are still counted as words at this point, which is not ideal
        user_mentions = re.compile(r"@\S*")
        tweet2 = user_mentions.sub(r"", tweet)
        urls = re.compile(r"http\S*:\S*")
        tweet2 = urls.sub(r"", tweet2)
        #hashtags = re.compile(r"#\w+")
        #tweet2 = hashtags.sub(r"", tweet2)
        tweet2 = tweet2.translate(str.maketrans('','',string.punctuation))
        excess_space = re.compile(r" {2,}")
        tweet2 = excess_space.sub(r" ", tweet2)
        #print(tweet)
        #print(tweet2)
        tokens = tokenizeRawTweetText(str(tweet2).lower())
        #print(len(tokens))
        #If there are three words or less
        if(len(tokens)<4):
            #print(tweet)
            #Increment count
            num_removed+=1
            #Remove tweet
            tweets = tweets.drop(tweets.index[pos])
        else:
            pos+=1
    print(str(num_removed) + " short tweets removed")
    return tweets
    
#Decodes all HTML entities in tweet text (e.g. '&lt;' becomes '<')
def decode_html_links(input_file):
    #Run twice to fix tweets like &amp;amp;
    good_tweets = []
    #tweets = pa.read_csv(input_file, sep="\t", skiprows=range(1,114240), nrows=3)    
    tweets = pa.read_csv(input_file, sep=",")         
    for tweet in tweets['modified_text']:
        #print(tweet)
        decoded = html.unescape(tweet)
        decoded = decoded.replace('"',"'")    
        #Standardise URLs (NB: removes any punctuation immediately after link - if no space)
        urls = re.compile(r"http\S*")
        decoded = urls.sub(r"<link>", decoded)
        good_tweets.append(decoded)
    #Remove (original) text column
    del tweets['modified_text']
    #Insert new column with decoded text
    tweets['modified_text'] = good_tweets
    return tweets

#Replaces @user mentions with <user>
def standardise_user_mentions(input_file):
    good_tweets = []
    tweets = pa.read_csv(input_file, sep=",")         
    for tweet in tweets['modified_text']:
        usernames = re.compile(r"@\S+")
        tweet = usernames.sub(r"<user>", tweet)
        #Correct formula error
        formula_error = re.compile(r"^=")
        tweet = formula_error.sub("", tweet)
        good_tweets.append(tweet)
    del tweets['modified_text']
    tweets['modified_text'] = good_tweets
    return tweets
    
##########################################################################
#GET RMT LABELS
#Code adapted with permission from Te Hiku Media's nga-kupu repository
#https://github.com/TeHikuMedia/nga-kupu/blob/master/scripts/kupu_tūtira
#This work is bound by the Kaitiakitanga Licence
#https://tehiku.nz/te-hiku-tech/te-hiku-dev-korero/25141/data-sovereignty-and-the-kaitiakitanga-license
##########################################################################
    
#Returns the plain tweet text from the input file in a single string.
def tangohia_kupu_tōkau(tweets):
    text = ' '.join(tweets['modified_text']).lower()
    return text

#Writes the list of Māori words to the given file, one word per line.
def tuhi_puta_tuhinga(output_file, kupu_hou):
    #Write to output file
    kupu_tūtira_hou = open(output_file, "w")
    kupu_tūtira_hou.write("\n".join(kupu_hou))
    kupu_tūtira_hou.close()

#Adds to the tweet any words that the RMT system considers to be Māori
def get_rmt_labels(input_file, output_file):  
    #Gather text from input files    
    #Reads in a dataframe with multiple columns, but only analyses the tweet text
    tweets = pa.read_csv(input_file, sep="\t")
    kupu_tōkau = tangohia_kupu_tōkau(tweets)

    #Writes these words that are considered to be Māori in the text (the keys
    # of the first object returned by the kōmiri_kupu function) to their output
    # files or prints them to the console depending on user input, in Māori
    # alphabetical order
    tuhi_puta_tuhinga(output_file, nahanaha(kōmiri_kupu(kupu_tōkau)[0].keys()))
    
    #Store the Maori words in a list
    maori_words = ['a','i','he','me','to','no','ā','ae','ana','au','e','ia','ka','ki','kia','ko','ma','moe','o','ora','ra','u']
    with open(output_file, 'r') as f:
        for line in f:
            maori_words.append(line.strip("\n").lower())
    f.close()
        
    maori_percentages = []    
    #2D array to keep track of Maori words in each tweet
    matches2 = []
    total_words_list = []
    num_maori_words_list = []
    for tweet in tweets['modified_text']:
        #Remove <link>, <user>, punctuation and unnecessary spaces
        tweet2 = tweet.lower()
        tweet2 = re.sub("<link>", "", tweet2)
        tweet2 = re.sub("<user>", "", tweet2)
        tweet2 = re.sub('['+string.punctuation+']', '', tweet2)
        #tweet = re.sub('\d','',tweet)
        tweet2 = re.sub(r'^ ','',tweet2)
        tweet2 = re.sub(r' $','',tweet2)
        tweet2 = re.sub(r" {2,}", " ", tweet2)
        #Extract the tokens from the tweet
        tokens = tokenizeRawTweetText(str(tweet2).lower())
        #Store the length of the tweet
        total_words = len(tokens)
        #Counter variable
        num_maori_words = 0
        #List to store all words that are detected as Maori in the tweet
        matches = []
        #For each word in the tweet
        for token in tokens:
            #If the word is also in the list of Maori words
            if token in maori_words:
                #Increment the count
                matches.append(token)
                num_maori_words += 1
        if(total_words == 0):
            percentage_maori = 0
        else:
            percentage_maori = float(num_maori_words/total_words)
            percentage_maori = round(percentage_maori, 2)
        matches2.append(matches)        
        maori_percentages.append(percentage_maori)
        num_maori_words_list.append(num_maori_words)
        total_words_list.append(total_words)
    #Insert new columns
    tweets['maori_words_rmt'] = matches2
    tweets['rmt_num_maori_words'] = num_maori_words_list
    tweets['rmt_total_words'] = total_words_list
    tweets['rmt_percent_maori'] = maori_percentages
    #Calculate number of favourites
    tweets['favourites'] = tweets['like_count'] + tweets['retweet_count'] + tweets['quote_count']
    return tweets
        
##########################################################################
#MORE PROCESSING
##########################################################################
    
#Sorts tweets chronologically
def sort_by_date(tweets):
    tweets = tweets.sort_values(by='date')
    return tweets

#Removes any duplicate tweets (there shouldn't be any unless collection dates overlap)
def remove_duplicates(tweets):
    unique_tweets = tweets.drop_duplicates(subset='tweet_id', keep="first")
    duplicates = len(tweets) - len(unique_tweets)
    return unique_tweets, duplicates

#Removes similar/identical tweets posted by the same user, but only if they 
#contain more than six words.
def remove_similar_tweets(tweets):
    #Create copy of dataframe to preserve original formatting
    original = tweets.copy(deep=True)
    num_tweets = len(tweets)
    df2 = pa.DataFrame()
    #Loop through all users in the dataframe
    for user in tweets['user_id'].unique():
        #Select all tweets by the current user that contain more than six words
        user_tweets = tweets[(tweets['user_id'] == user) & (tweets['rmt_total_words']>6)]
        current_user = user_tweets.copy(deep=True)
        #Lower-case all text
        current_user['modified_text'] = current_user['modified_text'].str.lower()
        #Remove <user> and <link> references
        current_user['modified_text'] = current_user['modified_text'].str.replace("<user>","")
        current_user['modified_text'] = current_user['modified_text'].str.replace("<link>", "")
        #Remove numbers
        current_user['modified_text'] = current_user['modified_text'].str.replace("\d","")
        #Remove spaces and punctuation
        current_user['modified_text'] = current_user['modified_text'].str.replace('[^\w\s]','')
        current_user['modified_text'] = current_user['modified_text'].str.replace('\s+','')
        #Remove successive instances of duplicate tweets       
        current_user.drop_duplicates(subset = 'modified_text', keep = "first", inplace = True)         
        #Select all tweets containing fewer than seven words
        short_tweets = tweets[(tweets['user_id'] == user) & (tweets['rmt_total_words']<=6)]
        #Merge the two dataframes (for tweets with diff. lengths) with the original                 
        merged = original[original.index.isin(current_user.index)]
        merged2 = original[original.index.isin(short_tweets.index)]        
        df1 = merged.combine_first(merged2)
        df2 = df2.append(df1)
    sim_tweets = num_tweets - len(df2)
    return df2, sim_tweets

#Isolates hashtags and extracts all tokens in tweets. 
def extract_tokens(tweets):
    new_token = []
    hasht = []
    #Expand common English contractions
    with open('contraction_dic.txt', 'rb') as handle:
        data = handle.read()
    dic_contractions = pickle.loads(data)
    handle.close()
    for ind, row in tweets.iterrows():
        new_text = row['modified_text'].replace("<link>", "")
        #Lower-casing is mainly so that it matches the RMT system labels
        new_text = new_text.lower()
        #Remove user references
        new_text1 = new_text.replace("<user>", "")
        #Expand contractions
        dd = dic_contractions
        res = ' '.join([dd.get(i, i) for i in new_text1.split()])
        res1 = strip_all_entities(res)
        #Extract hashtags
        hashtags = save_hashtags(res)
        #Remove emoticons
        tweet = remove_emoticons(res1)
        #tweet = res1.replace("...",' ')
        tweet = tweet.replace("...",' ')
        tweet = tweet.replace("<3",' ')
        tweet = tweet.replace(":-X",' ')
        tweet = tweet.replace(":-(|)",' ')
        #Remove punctuation
        tweet1 = remove_punc(tweet)
        twt1 = ' '.join([dd.get(i, i) for i in tweet1.split()])
        twt1 = ''.join([c for c in twt1 if not c.isdigit()])
        twt1 = twt1.strip().replace('\d+','').split()
        new_token.append(twt1)
        hasht.append(hashtags)
    tweets['tokens'] = new_token
    tweets['hashtags'] = hasht
    return tweets

#Double-checks that tweets containing less than four words are removed
def remove_short_tweets2(tweets):
    short_tweets = len(tweets[tweets['rmt_total_words'] <= 3])    
    tweets = tweets[tweets['rmt_total_words'] > 3]
    return tweets, short_tweets   

#Removes temporary files that were created when scraping and cleaning tweets
def remove_tmp_files(filename):
    tmp_files = [filename + ".json", filename + ".csv", filename + "-new.csv"]
    for file in tmp_files:    
        try:
            os.remove(file)
        except OSError as e:
            print("Error: %s : %s" % (file, e.strerror))

##########################################################################
#CALL FUNCTIONS
##########################################################################
    
def main():
    batch = 0
    user_count = 0
    #Read in list of user IDs
    all_users = pa.read_csv("users.csv", sep=",")
    
    #Remove suspected bots and foreign-language tweeters
    #Foreign-language tweeters were identified through manual checks and by 
    #looking for users who used apostrophes (or similar) in the middle of words
    USERS_TO_REMOVE = ["3906144072", "15146988", "16581893", "778337", 
                       "3115912512", "607946466", "3161644651",
                       "577480986", "2263983222", "382360962", "103691430", 
                       "1250197063", "136851410", "1478661074", "161179087", 
                       "16121076", "16581893", "18204149", "18541658", 
                       "188228410", "19156803", "228205154", "244016140", 
                       "2468588772", "24860196", "272596297", "292135904", 
                       "3191955342", "35175100", "3667199000", "46342291", 
                       "46540286", "55052867", "842581424", "942573468"]
    ids = all_users['user_id'].astype(str).apply(lambda x: re.sub("'","", x))
    ids = [x for x in ids if x not in USERS_TO_REMOVE]
    
    #Get start and end dates for the past week
    start_date, end_date, filename = calc_dates(7)
    #Can override start and end dates by commenting out previous line, and 
    #uncommenting the following:
    #start_date = "2022-03-07T00:00:01Z"
    #end_date = "2022-04-11T00:00:00Z"
    #filename = "2022-03-07"
           
    print("")
    print("Start:", start_date)
    print("End:", end_date)
    print("")
    
    # Create CSV file
    csvFile = open(filename + ".csv", "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    #Create headers for the data we want to save
    csvWriter.writerow(['tweet_id', 'url', 'user_id', 'date', 'content', 'conversation_id', 'in_reply_to_user_id', 'ref_tweet_id', 'ref_tweet_type', 'geo', 'lang', 'source', 'like_count', 'quote_count', 'reply_count', 'retweet_count'])
    csvFile.close()
    
    with open(filename + ".json", 'a', encoding="utf8") as f:
        #For each user in list
        for user in ids:
            user_count += 1
            print("User:",user_count)
            batch = query_user(user, batch, f, start_date, end_date, filename)
            print("")
            print("Cumulative requests:",batch)
            print("")
    f.close()
    
    format_data(filename + ".csv")
    all_tweets = get_rmt_labels(filename + "-new.csv", filename + "-lexicon.csv")
    all_tweets, duplicates = remove_duplicates(all_tweets)
    print("{} duplicate tweets removed".format(duplicates))
    all_tweets, sim_tweets = remove_similar_tweets(all_tweets)
    print("{} similar tweets removed".format(sim_tweets))
    all_tweets, short_tweets2 = remove_short_tweets2(all_tweets)
    print("{} additional short tweets removed".format(short_tweets2))    
    all_tweets = extract_tokens(all_tweets)
    all_tweets = sort_by_date(all_tweets)
    #Append all tweets to file, regardless of percentage
    all_tweets.to_csv(filename + "-all.csv", sep="\t", header = True, index = False)
    #We only considered 'bilingual tweets', i.e. tweets that the RMT system
    #deemed to contain 30-80% Māori text
    bilingual_tweets = all_tweets.loc[(all_tweets['rmt_percent_maori'] >= 0.3) & (all_tweets['rmt_percent_maori'] <= 0.8)]   
    bilingual_tweets.to_csv(filename + "-bilingual.csv",sep = "\t", header = True, index = False)      
    remove_tmp_files(filename)
    
if __name__ == "__main__":
    main()