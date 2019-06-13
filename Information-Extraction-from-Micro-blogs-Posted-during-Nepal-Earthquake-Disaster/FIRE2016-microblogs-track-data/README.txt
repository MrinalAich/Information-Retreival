
This folder contains, apart from this readme.txt file, one text file named "fire16-microblog-track-topics.txt", and one folder named "microblogs-crawl-directory".

The file "fire16-microblog-track-topics.txt" contains 7 (seven) topics in TREC format, each describing a generic information need during a disaster situation. Each topic contains an identifier number, a title, a description, and a more detailed narrative which describes what types of microblogs would be considered relevant to the topic.

The folder "microblogs-crawl-directory" contains:

- a text file "Nepal-earthquake-tweetids.txt" containing 50,068 tweetids, i.e., identifiers of tweets / microblogs posted in Twitter during the Nepal earthquake in April 2015.

- a Python script "crawl_tweets.py" along with the libraries that are required by this script.

The script should be executable on any standard Linux machine having Python 2.x installed and having Internet connection. On running the script, the tweets corresponding to the tweetids in the above text file will be downloaded using the Twitter API. This crawling process should require around 3--4 hours. However, the download may need more time if multiple groups are attempting to download the tweets in parallel. 


The downloaded tweets will be written into a file named "Nepal-earthquake-tweets.jsonl" which will be created in the same directory where the script is located. Each line in this file will be a json-encoded tweet, where json (JavaScript Object Notation) is an open standard format that uses human-readable text to transmit data objects consisting of attribute–value pairs. 

The attributes for a tweet, as returned by the Twitter API, are described at https://dev.twitter.com/overview/api/tweets. Specifically, the value corresponding to the "text" attribute gives the textual content of the tweet, and the value corresponding to the "id" attribute gives the integer tweetid of the tweet.

Json parsers are available in all popular programming languages, and such a parser can be used to decode each line of this file individually, to get the attribute-value pairs for a tweet.

You can refer to http://www.json.org/ for more details on json, and for knowing about json parsers in various programming languages.

=====

Note that multiple people often post the same text in Twitter, e.g., by retweeting or copying someone else's tweet. We have attempted to remove such duplicate tweets as far as possible, still there might be some duplicates (i.e., multiple tweets containing the same or nearly same text, but different tweetids) in the tweet file. For such cases, if a certain tweet is relevant to a particular topic, all duplicates of that tweet will be considered relevant to that topic as well.

===== 

You are free to use any data contained within the tweets, or any external resource, for identifying the tweets relevant to a given topic.
While submitting the results, you will need to submit the tweetids of the tweets that you judged relevant to each topic. The exact format for submitting the results will be declared in due time.

=====

For any further queries, please contact the track organizers:
Saptarshi Ghosh, Department of CST, IIEST Shibpur, India (saptarshi.ghosh@gmail.com)
Kripabandhu Ghosh, ISI Kolkata, India (kripa.ghosh@gmail.com)


