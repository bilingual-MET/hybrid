# Hybrid Architecture for Labelling Bilingual Māori-English Tweets

This repository contains code used for developing a hybrid architecture. This depositary provide only a sample data for demo.

## Architecture

![hybrid_updated](https://user-images.githubusercontent.com/107286789/173212143-ef287a66-2f30-4b31-9ee7-1fc53409925b.png)

## Sample Data
|tweet_id	|user_id	|modified_text|maori_words_rmt|
| :------ | :-------- | :-------- | :----- |
|1001|	x10|	Living by the Moon: Te Maramataka a Te Whānau-ā-Apanui, Wiremu Tāwhai Te Whānau-ā-Apanui, Te Whakatōhea, Ngāti Awa <link>	| 'te', 'maramataka', 'te', 'wiremu', 'tāwhai', 'te', 'te', 'whakatōhea', 'ngāti', 'awa'|		
|1016|	x25|	<user> oh man, take me, take me!!|	'take', 'me', 'take', 'me'|

### Pre-processing
[Additional pre-processing](Additional-preprocessing.ipynb)
  
### Token-level Labels
[Step 1](Step1-Token-level.ipynb)
[Step 2](Step2-Token-level.ipynb)

### Tweet-level Labels
[Step](Tweet-labels.ipynb)
