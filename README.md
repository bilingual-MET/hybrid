# Hybrid Architecture for Labelling Bilingual Māori-English Tweets

This repository contains code used to develop a hybrid architecture for labelling bilingual Māori-English tweets. A small sample file is provided for demonstration purposes, along with a script for downloading additional tweets.

## Architecture

![hybrid_updated](https://user-images.githubusercontent.com/107286789/173212143-ef287a66-2f30-4b31-9ee7-1fc53409925b.png)

## Sample Data
|tweet_id	|user_id	|modified_text|maori_words_rmt|
| :------ | :-------- | :-------- | :----- |
|1001|	x10|	Living by the Moon: Te Maramataka a Te Whānau-ā-Apanui, Wiremu Tāwhai Te Whānau-ā-Apanui, Te Whakatōhea, Ngāti Awa <link>	| 'te', 'maramataka', 'te', 'wiremu', 'tāwhai', 'te', 'te', 'whakatōhea', 'ngāti', 'awa'|		
|1016|	x25|	<user> oh man, take me, take me!!|	'take', 'me', 'take', 'me'|

### Pre-processing
  
#### Filtering out non-English and non-Maori tweets
  A series of manual checks and a simple [Python script](Filter_nonEnglish_nonMaori_tweets.py) were used to filter out tweets that contain languages other than English and Māori. A series of small subsets of the data (first 100, last 100, middle 100, etc.) were extracted and manually investigated. Any user who posted a tweet in a language other than English or Māori was marked and their user ID was recorded. These user IDs were passed into the Python script, which removed tweets by these users from the dataset. Finally, a search was conducted to identify tweets that contained apostrophies mid-word (e.g. "Lota nu'u ua ou fanau ai"). The user ID for these tweets was also recorded and passed into the Python script. 
  
[Additional pre-processing](Additional-preprocessing.ipynb)
  
### Token-level Labels
[Step 1](Step1-Token-level.ipynb)
  
[Step 2](Step2-Token-level.ipynb)

### Tweet-level Labels
[Steps](Tweet-labels.ipynb)
