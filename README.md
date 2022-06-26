# Hybrid Architecture for Labelling Bilingual Māori-English Tweets

This repository contains code used to develop a hybrid architecture for labelling bilingual Māori-English tweets. A small sample file is provided for demonstration purposes, along with a script for downloading additional tweets.

## Architecture

![hybrid_updated](https://user-images.githubusercontent.com/107286789/173212143-ef287a66-2f30-4b31-9ee7-1fc53409925b.png)

## Collect and Pre-process Tweets
  
0. Apply for a [Twitter developer account](https://developer.twitter.com/en/apply-for-access) if you do not have one already.
1. Download or clone the [nga-kupu](https://github.com/TeHikuMedia/nga-kupu) repository, which is bound by the [Kaitiakitanga Licence](https://tehiku.nz/te-hiku-tech/te-hiku-dev-korero/25141/data-sovereignty-and-the-kaitiakitanga-license).
2. Ensure that Python 3 is installed on your machine, then run the following commands in the terminal:
```
pip install requests
pip install requests-oauthlib
pip install yelp_uri
pip install beautifulsoup4
pip install emot
```
3. Copy all files in the [`preprocessing`](https://github.com/bilingual-MET/hybrid/tree/main/preprocessing) folder of this repository to `nga-kupu-master/scripts`. 
4. Update the four word lists in `nga-kupu-master/taumahi/__init.py__` according to the instructions in `update_word_lists.txt`.
5. Run `python3 setup.py install` from `nga-kupu-master`.
6. Configure your API bearer token by running the following command in the terminal: `export 'BEARER_TOKEN'='<your_bearer_token>'`
7. Run the `collect_and_clean_tweets.py` script that you moved to the `nga-kupu-master/scripts` folder. This script gathers tweets from the past week from a predefined list of users (`users.csv`), then cleans the tweets and generates the RMT labels that are needed as input to the hybrid architecture (below).

## Run Experiments

### Sample Data
|tweet_id	|user_id	|modified_text|maori_words_rmt|
| :------ | :-------- | :-------- | :----- |
|1001|	x10|	Living by the Moon: Te Maramataka a Te Whānau-ā-Apanui, Wiremu Tāwhai Te Whānau-ā-Apanui, Te Whakatōhea, Ngāti Awa <link>	| 'te', 'maramataka', 'te', 'wiremu', 'tāwhai', 'te', 'te', 'whakatōhea', 'ngāti', 'awa'|		
|1016|	x25|	<user> oh man, take me, take me!!|	'take', 'me', 'take', 'me'|

### Token-level Labels
[Step 1](Step1-Token-level.ipynb)
  
[Step 2](Step2-Token-level.ipynb)

### Tweet-level Labels
[Steps](Tweet-labels.ipynb)
