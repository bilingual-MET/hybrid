# Hybrid Architecture for Labelling Bilingual Māori-English Tweets

This repository contains code used to develop a hybrid architecture for labelling bilingual Māori-English tweets. A small sample file is provided for demonstration purposes, along with a script for downloading additional tweets.

## Architecture

![hybrid_updated](https://user-images.githubusercontent.com/107286789/173212143-ef287a66-2f30-4b31-9ee7-1fc53409925b.png)

### Collect and Pre-process Tweets
  
- Step 0: Apply for a [Twitter developer account](https://developer.twitter.com/en/apply-for-access) if you do not have one already.
- Step 1: Download or clone the [nga-kupu repository](https://github.com/TeHikuMedia/nga-kupu), which is bound by the [Kaitiakitanga Licence](https://tehiku.nz/te-hiku-tech/te-hiku-dev-korero/25141/data-sovereignty-and-the-kaitiakitanga-license).
- Step 2: Ensure that Python 3 is installed on your machine, then run the following commands in the terminal:
```
pip install requests
pip install requests-oauthlib
pip install yelp_uri
pip install beautifulsoup4
pip install emot
```
- Step 3:.Copy all files in the `preprocessing` folder to the `scripts` folder in the `nga-kupu` repository. Also update the four word lists in `__init.py__` in the `taumahi` folder as per `update_word_lists.txt` (i.e. modify the first word list and clear the other three). Run `python3 setup.py install` from the main `nga-kupu` folder.
- Step 4: Configure your API bearer token by running the following command in the terminal:
```
export 'BEARER_TOKEN'='<your_bearer_token>'
```
- Step 5: Run the `collect_and_clean.py` script that you moved to the `scripts` folder. This script gathers tweets from the past week from a predefined list of users (`users.csv`), then cleans the tweets and generates the RMT labels that are needed as input to the hybrid architecture. Run the following command from the working directory: 
```
python3 collect_and_clean_tweets.py
``` 

## Sample Data for Architecture Experiments
|tweet_id	|user_id	|modified_text|maori_words_rmt|
| :------ | :-------- | :-------- | :----- |
|1001|	x10|	Living by the Moon: Te Maramataka a Te Whānau-ā-Apanui, Wiremu Tāwhai Te Whānau-ā-Apanui, Te Whakatōhea, Ngāti Awa <link>	| 'te', 'maramataka', 'te', 'wiremu', 'tāwhai', 'te', 'te', 'whakatōhea', 'ngāti', 'awa'|		
|1016|	x25|	<user> oh man, take me, take me!!|	'take', 'me', 'take', 'me'|

### Token-level Labels
[Step 1](Step1-Token-level.ipynb)
  
[Step 2](Step2-Token-level.ipynb)

### Tweet-level Labels
[Steps](Tweet-labels.ipynb)
