import sys
import simple_sentiment_analyzer as ssa

def main():
    sent_file = sys.argv[1]
    tweet_file = sys.argv[2]
    analyzer = ssa.SentimentAnalyzer(True)
    analyzer.build_dictionary(sent_file)
    analyzer.analyze_tweets(tweet_file)
    analyzer.append_unknown()

if __name__ == '__main__':
    main()
