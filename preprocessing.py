import pandas as pd
import re
from spellchecker import SpellChecker

spell = SpellChecker()

df = pd.read_csv("FinalTweetList.csv")
allTags = {}


def tagTesting(splitSentence, sentiment):
    # now we need to filter out the top banks now
    # lets use a regex
    regex = "^@[a-zA-Z0-9_]*"
    # we need to iterate through all the tweets and find the @whatever and then filter banks with it
    matchedStrings = []
    for i in splitSentence:
        teststring = i
        result = re.match(regex, teststring)
        if result:
            matchedStrings.append(teststring)
            if teststring in allTags.keys():
                allTags[teststring] = allTags[teststring] + 1
            else:
                allTags[teststring] = 1

    return (matchedStrings, sentiment)


# now we need to iterate through every tweet and tokenize it and then filter them
df.columns = ['Tweets', 'Sentiments', 'Ignore']
allTweets = df["Tweets"].values
allSentiments = df["Sentiments"].values

allSentences = [i.split(" ") for i in allTweets]

tweetSentimentPair = []
for i in range(0, len(allSentences)):
    tweetSentimentPair.append(tagTesting(allSentences[i], allSentiments[i]))


allTagsSorted = sorted(allTags.items(), key=lambda kv: kv[1], reverse=True)

# now we need to filter out and have only a single @tag in the tweet sentiment pair
# we need to keep the tag with the highest number of occurances in allTags dictionary


tagSentimantPair = []
i = -1
for pair in tweetSentimentPair:
    i = i+1
    tags = pair[0]
    sentiment = pair[1]
    # we need to filter out the tags
    tempPairs = [(i, allTags[i]) for i in tags]
    # now we need to sort it out in descending order based on the count value of the ags
    tempPairs = sorted(tempPairs, key=lambda x: x[1], reverse=True)
    try:
        # last parameter is the row number of that specific tweet
        tagSentimantPair.append((tempPairs[0][0], sentiment, i))
    except:
        pass

# now tagSentimentPair contains (bankName,sentiment,line number)
# now lets get all the line numbers for that specific bank name, it will help us create a sub 500 tweet dataset
bankLineDict = {}
for i in tagSentimantPair:
    if i[0] in bankLineDict.keys():
        bankLineDict[i[0]].append(i[2])
    else:
        bankLineDict[i[0]] = []


#lets even make a lineSentiment dict {lineno: sentiment}
lineSentimentDict = {}
for i in tagSentimantPair:
    lineSentimentDict[i[2]] = i[1]

print(lineSentimentDict)

# now using the dictionary of bank names and lines , we can create a dataset

# command to get a number of rows for each bank , use it only to check
# for i in bankLineDict.keys():
#     print(i,len(bankLineDict[i]))
# on running the above , we get the top 5 banks as:
"""
@AxisBankSupport 507
@TheOfficialSBI 2270
@HDFCBank_Cares 863
@KotakBankLtd 604
@ICICIBank_Care 801
"""

# we now need to create a new sample dataset
# let's take 500 tweets now
banks = ["@AxisBankSupport", "@TheOfficialSBI",
         "@HDFCBank_Cares", "@KotakBankLtd", "@ICICIBank_Care"]

df = pd.read_csv("FinalTweetList.csv")
df.columns = ['Tweets', 'Sentiments', 'Ignore']


#spell checking and correction
#removing numbers
def filterTweet(tweet):
    newtweet = ""
    for word in tweet.split():
        if "@" not in word:
            if word.isalpha():
                # word = spell.correction(word)
                newtweet = newtweet + " " + word

    return newtweet


masterDf =  pd.DataFrame(columns=['Tweet','Sentiment'])

for bankName in banks:
    lines = bankLineDict[bankName]
    bankdf = pd.DataFrame(columns=['Tweet'])
    count = 0
    for lineNumber in lines:
        tweet = df["Tweets"].iloc[lineNumber]
        tweet = filterTweet(tweet)
        #we now need to store this tweet in a dataframe  - MASTER DF AND BANK DF
        masterDf = masterDf.append({'Tweet': tweet,'Sentiment':lineSentimentDict[lineNumber]}, ignore_index=True)

        
        count = count + 1
        if(count<501):
            bankdf = bankdf.append({'Tweet': tweet}, ignore_index=True)
    
    bankdf.to_csv("./TweetDataset/" +bankName[1:]+".csv")


masterDf.to_csv("MasterDataframe.csv")
