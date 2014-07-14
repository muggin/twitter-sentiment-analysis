__author__ = 'WojteK'
import re
import json
import codecs

# Debug Twitter structs FORFUCKSSAKE!
TWEET_TEXT_FIELD = 'text'
TWEET_STATUSES_FIELD = 'statuses'
USERNAME_REGEX = '^\@\S+$'
HASHTAG_REGEX = '^\#\S+$'
URL_REGEX = '^(?:https?:\/\/)?(?:[w]{3}\.)?(?:[^\.\s\d]{2,12})\.(?:[a-z]{2,4})(?:\/[a-z\.]{1,12})*'


class SentimentAnalyzer:
    '''
    Simple Tweet Sentiment Analyzer, based on ngram token sentiment.
    Handles tri/bi/unigram sentiment dictionaries.
    Performs basic tweet cleaning (removing urls, usernames, hashtags).
    Allows evaluation of unknown words and appending them to the unigram dictionary.
    '''

    def __init__(self, deduce_sentiment=False):
        '''
        Class initializer.
        :type deduce_sentiment: object
        :param deduce_sentiment: if program should deduce sentiment for unknown words
        '''
        self.deduce_sentiment = deduce_sentiment
        self.unigram_dict = {}
        self.bigram_dict = {}
        self.trigram_dict = {}
        self.hashtag_dict = {}
        self.unknown_dict = {}

    def __score_trigrams(self, tweet_split):
        '''
        Find and score trigrams in tweet. Replace used words with empty strings.
        :param tweet_split: tokenized tweet text
        :return: total score based on trigrams found in tweet
        '''
        assert isinstance(tweet_split, list)
        score = 0
        if (len(self.trigram_dict) > 0) and (len(tweet_split) > 2):
            for index in xrange(0, len(tweet_split) - 2):
                dict_key = tweet_split[index], tweet_split[index + 1], tweet_split[index + 2]
                if dict_key in self.trigram_dict:
                    score += self.trigram_dict[dict_key]
                    tweet_split[index] = tweet_split[index + 1] = tweet_split[index + 2] = ''
        return score

    def __score_bigrams(self, tweet_split):
        '''
        Find and score bigrams in tweet. Replace used words with empty strings.
        :param tweet_split: tokenized tweet text
        :return: total score based on bigrams found in tweet
        '''
        assert isinstance(tweet_split, list)
        score = 0
        if (len(self.bigram_dict) > 0) and (len(tweet_split) > 1):
            for index in xrange(0, len(tweet_split) - 1):
                dict_key = tweet_split[index], tweet_split[index + 1]
                if dict_key in self.bigram_dict:
                    score += self.bigram_dict[dict_key]
                    tweet_split[index] = tweet_split[index + 1] = ''
        return score

    def __score_unigrams(self, tweet_split):
        '''
        Find and score unigrams in tweet. Replace used words with empty strings.
        :param tweet_split: tokenized tweet text
        :return: total score based on unigrams found in tweet
        '''
        assert isinstance(tweet_split, list)
        score = 0
        if (len(self.unigram_dict) > 0) and (len(tweet_split) > 0):
            for index in xrange(0, len(tweet_split)):
                dict_key = tweet_split[index]
                if dict_key in self.unigram_dict:
                    score += self.unigram_dict[dict_key]
                    tweet_split[index] = ''
        return score

    def __score_hashtags(self, hashtags):
        '''
        Score all hashtags found in tweet.
        :param hashtags: list of hasthags found in tweet
        :return: total score based on hashtags found in tweet
        '''
        assert isinstance(hashtags, list)
        score = 0
        if (len(self.hashtag_dict) > 0) and (len(hashtags) > 0):
            for tag in hashtags:
                if tag in self.hashtag_dict:
                    score += self.hashtag_dict[tag]
        return score

    def __find_unknown(self, tweet_split):
        '''
        Find unknown words in tweet.
        :param tweet_split: tokenized tweet text
        :return: list of unknown words used in tweet (unknown as in not in unigram dictionary)
        '''
        assert isinstance(tweet_split, list)
        unknown_list = []
        for word in tweet_split:
            if word not in self.unigram_dict and word != '':
                unknown_list.append(word)
        return unknown_list

    def __append_to_unknown(self, unknown_words, sentiment):
        '''
        Append a list of unknown words to the unknown_dict, with given sentiment.
        unknown_dict structure: <key>:<(sentiment, occurrence_count)>
        :param unknown_words: list of unknown words from one tweet
        :param sentiment: sentiment value associated with these words
        :return: None
        '''
        assert isinstance(unknown_words, list)
        for word in unknown_words:
            if word in self.unknown_dict:
                entry = self.unknown_dict[word]
                self.unknown_dict[word] = entry[0] + sentiment, entry[1] + 1
            else:
                self.unknown_dict[word] = sentiment, 1

    def __clean_tweet(self, tweet_split):
        '''
        Clean tweet from urls, usernames, hashtags, etc.
        :param tweet_split: tokenized tweet text
        :return: tuple containing list of found hashtags, urls, usernames
        '''
        assert isinstance(tweet_split, list)
        hashtags = [word for word in tweet_split if re.match(HASHTAG_REGEX, word)]
        urls = [word for word in tweet_split if re.match(URL_REGEX, word)]
        usernames = [word for word in tweet_split if re.match(USERNAME_REGEX, word)]
        cleaning_list = hashtags + urls + usernames
        for word in cleaning_list:
            tweet_split.remove(word)
        return urls, usernames, hashtags

    def append_unknown(self):
        '''
        Append unknown_dict to unigram_dict.
        :return: None
        '''
        for word in self.unknown_dict:
            entry = self.unknown_dict[word]
            self.unigram_dict[word] = entry[0] / entry[1]

    def build_dictionary(self, sentiment_file_path):
        '''
        Build uni/bi/trigram_dict based on sentiment file passed as argument.
        :param sentiment_file_path: sentiment file path
        :return: None
        '''
        with codecs.open(sentiment_file_path, 'r', 'utf-8') as sentiment_file:
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

    def build_hashtag_dictionary(self, hashtag_file_path):
        '''
        Build hashtag_dict based on sentiment file passed as argument.
        :param hashtag_file_path: hashtag file path
        :return: None
        '''
        with codecs.open(hashtag_file_path, 'r', 'utf-8') as sentiment_file:
            for line in sentiment_file:
                term, sentiment = line.strip('\n').split('\t')
                key_split = term.split(' ')
                if len(key_split) == 1:
                    self.hashtag_dict[term] = int(sentiment)
                else:
                    print key_split, ' - invalid dictionary key format!'

    def evaluate_tweet(self, tweet):
        '''
        Evaluate single tweet.
        :param tweet: tweet text
        :return: tweets total sentiment score
        '''
        score = 0
        tweet_split = tweet.split(' ')
        tags, urls, usernames = self.__clean_tweet(tweet_split)
        score += self.__score_trigrams(tweet_split)
        score += self.__score_bigrams(tweet_split)
        score += self.__score_unigrams(tweet_split)
        score += self.__score_hashtags(tags)
        if self.deduce_sentiment:
            unknown_list = self.__find_unknown(tweet_split)
            self.__append_to_unknown(unknown_list, score)
        return score

    def analyze_tweets(self, tweet_file_path, print_output=True):
        '''
        Analyze and evaluate all tweets from file passed as argument.
        :param tweet_file_path: tweet file path
        :param print_output: if program should print work effects
        :return: None
        '''
        with codecs.open(tweet_file_path, 'r', 'utf-8') as tweet_file:
            for line in tweet_file:
                tweets_struct = json.loads(line)
                for tweet in tweets_struct[TWEET_STATUSES_FIELD]:
                    if TWEET_TEXT_FIELD in tweet:
                        tweet_score = self.evaluate_tweet(tweet[TWEET_TEXT_FIELD])
                        if print_output:
                            print '* ', tweet[TWEET_TEXT_FIELD], '\n'
                            print 'Tweet score: ', tweet_score, '\n'
