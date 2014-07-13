__author__ = 'WojteK'
import re
import json

TWEET_TEXT_FIELD = 'text'
USERNAME_REGEX = '^\@\S+$'
HASHTAG_REGEX = '^\#\S+$'
URL_REGEX = '^(?:https?:\/\/)?(?:[w]{3}\.)?(?:[^\.\s\d]{2,12})\.(?:[a-z]{2,4})(?:\/[a-z\.]{1,12})*'



class SentimentAnalyzer:
'''
Simple Tweet Sentiment Analyzer.
Handles tri/bi/unigram sentiment dictionaries.
Performs basic tweet cleaning (removing urls, usernames, hashtags).
Allows evaluation of unknown words and appending them to the unigram dictionary.
'''

    def __init__(self, deduce_sentiment = False):
        '''
        Class initializer.
        '''
        self.deduce_sentiment = deduce_sentiment
        self.unigram_dict = {}
        self.bigram_dict = {}
        self.trigram_dict = {}
        self.unknown_dict = {}


    def __score_trigrams(self, tweet_split):
        '''
        Find and score trigrams in tweet. Replace used words with empty strings.
        '''
        score = 0
        if len(tweet_split) > 2:
            for index in xrange(0, len(tweet_split) - 2):
                dict_key = tweet_split[index], tweet_split[index + 1], tweet_split[index + 2]
                if dict_key in self.trigram_dict:
                    score += self.trigram_dict[dict_key]
                    tweet_split[index] = tweet_split[index + 1] = tweet_split[index + 2] = ''
        return score


    def __score_bigrams(self, tweet_split):
        '''
        Find and score bigrams in tweet. Replace used words with empty strings.
        '''
        score = 0
        if len(tweet_split) > 1:
            for index in xrange(0, len(tweet_split) - 1):
                dict_key = tweet_split[index], tweet_split[index + 1]
                if dict_key in self.bigram_dict:
                    score += self.bigram_dict[dict_key]
                    tweet_split[index] = tweet_split[index + 1] = ''
        return score


    def __score_unigrams(self, tweet_split):
        '''
        Find and score unigrams in tweet. Replace used words with empty strings.
        '''
        score = 0
        if len(tweet_split) > 0:
            for index in xrange(0, len(tweet_split)):
                dict_key = tweet_split[index]
                if dict_key in self.unigram_dict:
                    score += self.unigram_dict[dict_key]
                    tweet_split[index] = ''
        return score


    def __find_unknown(self, tweet_split):
        '''
        Find unknown words in tweet.
        '''
        unknown_list = []
        for word in tweet_split:
            if word not in self.unigram_dict and word != '':
                unknown_list.append(word)
        return unknown_list


    def __append_to_unknown(self, unknown_words, sentiment):
        '''
        Append a list of unknown words to the unknown_dict, with given sentiment.
        unknown_dict structure: <key>:<(sentiment, occurrence_count)>
        '''
        for word in unknown_words:
            if word in self.unknown_dict:
                entry = self.unknown_dict[word]
                self.unknown_dict[word] = entry[0] + sentiment, entry[1] + 1
            else:
                self.unknown_dict[word] = sentiment, 1


    def __clean_tweet(self, tweet_split):
        '''
        Clean tweet from urls, usernames, hashtags, etc.
        '''
        cleaning_list = []
        cleaning_list += [word for word in tweet_split if re.match(URL_REGEX, word)]
        cleaning_list += [word for word in tweet_split if re.match(USERNAME_REGEX, word)]
        cleaning_list += [word for word in tweet_split if re.match(HASHTAG_REGEX, word)]
        for word in cleaning_list:
            tweet_split.remove(word)


    def append_unknown(self):
        '''
        Append unknown_dict to unigram_dict.
        '''
        for word in self.unknown_dict:
            entry = self.unknown_dict[word]
            value = self.unigram_dict[word] = entry[0]/float(entry[1])
            print word, ' ', value


    def build_dictionary(self, sentiment_file_path):
        '''
        Build unigram_dict and bigram_dict based on sentiment file passed as argument.
        '''
        with open(sentiment_file_path, 'r') as sentiment_file:
            for line in sentiment_file:
                term, sentiment = line.strip('\n').split('\t')
                key_split = term.split(' ')
                if len(key_split) == 1:
                    self.unigram_dict[term] = int(sentiment)
                elif len(key_split) == 2:
                    dict_key = key_split[0], key_split[1]
                    self.bigram_dict[dict_key] = int(sentiment)
                elif len(key_split) == 3:
                    dict_key = key_split[0], key_split[1], key_split[2]
                    self.trigram_dict[dict_key] = int(sentiment)
                else:
                    print key_split, ' - invalid dictionary key format!'


    def evaluate_tweet(self, tweet):
        '''
        Evaluate single tweet.
        '''
        score = 0
        tweet_split = tweet.split(' ')
        self.__clean_tweet(tweet_split)
        score += self.__score_trigrams(tweet_split)
        score += self.__score_bigrams(tweet_split)
        score += self.__score_unigrams(tweet_split)
        if self.deduce_sentiment:
            unknown_list = self.__find_unknown(tweet_split)
            self.__append_to_unknown(unknown_list, score)
        return score


    def analyze_tweets(self, tweet_file_path):
        '''
        Analyze and evaluate all tweets from file passed as argument.
        '''
        with open(tweet_file_path, 'r') as tweet_file:
            for tweet in tweet_file:
                tweet_struct = json.loads(tweet)
                if TWEET_TEXT_FIELD in tweet_struct:
                    self.evaluate_tweet(tweet_struct[TWEET_TEXT_FIELD])