import sys
import simple_sentiment_analyzer as ssa

default_word_sentiment_file = "/Users/Wojtek/Documents/Projekty/Twitter_Sentiment_Analysis/AFINN-111.txt"
default_tweet_file = "/Users/Wojtek/Documents/Projekty/Twitter_Sentiment_Analysis/tweets.txt"

def main():
    sent_file = sys.argv[1]
    tweet_file = sys.argv[2]
    analyzer = ssa.SentimentAnalyzer(True)
    analyzer.build_dictionary(default_word_sentiment_file)
    analyzer.analyze_tweets(default_tweet_file)
    analyzer.append_unknown()

if __name__ == '__main__':
    main()
