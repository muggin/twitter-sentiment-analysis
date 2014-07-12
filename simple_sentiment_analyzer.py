__author__ = 'Wojtek'
import sys
import json

_tweet_text_field = 'text'
# Check if unknown word is not @reference, #hashtag, http://url
# Find trigrams
# Find bigrams
# Find unigrams


'''

'''
class SentimentAnalyzer:
    def __init__(self, deduce_sentiment = False):
        self.deduce_sentiment = deduce_sentiment
        self.unigram_dict = {}
        self.bigram_dict = {}
        self.trigram_dict = {}
        self.unknown_dict = {}

    '''
    Append a list of unknown words to the unknown_dict, with given sentiment.
    unknown_dict structure: <key>:<(sentiment, occurrence_count)>
    '''
    def __append_to_unknown(self, unknown_words, sentiment):
        for word in unknown_words:
            if word in self.unknown_dict:
                entry = self.unknown_dict[word]
                self.unknown_dict[word] = entry[0] + sentiment, entry[1] + 1
            else:
                self.unknown_dict[word] = sentiment, 1

    '''
    Append unknown_dict to unigram_dict.
    '''
    def append_unknown(self):
        for word in self.unknown_dict:
            entry = self.unknown_dict[word]
            self.unigram_dict[word] = entry[0]/entry[1]

    '''
    Build unigram_dict and bigram_dict based on sentiment file passed as argument.
    '''
    def build_dictionary(self, sentiment_file_path):
        with open(sentiment_file_path, 'r') as sentiment_file:
            for line in sentiment_file:
                term, sentiment = line.strip('\n').split('\t')
                key_split = term.split(' ')
                if len(key_split) == 1:
                    self.unigram_dict[term] = sentiment
                elif len(key_split) == 2:
                    dict_key = key_split[0], key_split[1]
                    self.bigram_dict[dict_key] = sentiment
                elif len(key_split) == 3:
                    dict_key = key_split[0], key_split[1], key_split[2]
                    self.trigram_dict[dict_key] = sentiment
                else:
                    print key_split, ' - invalid dictionary key format!'

    '''
    Evaluate single tweet.
    '''
    def evaluate_tweet(self, tweet):
        score = 0
        unknown_list = []
        words = tweet.split(' ')
        for word in words:
            if word in self.unigram_dict:
                score += int(self.unigram_dict[word])
            elif self.deduce_sentiment:
                unknown_list.append(word)
        if self.deduce_sentiment:
            self.__append_to_unknown(unknown_list, score)
        return score

    '''
    Analyze and evaluate all tweets from file passed as argument.
    '''
    def analyze_tweets(self, tweet_file_path):
        with open(tweet_file_path, 'r') as tweet_file:
            for tweet in tweet_file:
                tweet_struct = json.loads(tweet)
                if _tweet_text_field in tweet_struct:
                    print self.evaluate_tweet(tweet_struct[_tweet_text_field])