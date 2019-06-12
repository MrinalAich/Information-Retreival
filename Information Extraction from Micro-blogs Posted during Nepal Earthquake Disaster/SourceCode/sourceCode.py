import re, nltk, numpy, string, math, os, matplotlib.pyplot as plt
import requests, fnmatch, os, glob, time, urllib
from collections import defaultdict
from collections import Counter
from bs4 import BeautifulSoup
from sets import Set
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import svm

# Configurable Parameters
gUnigramWt = 1
gBigramWt = 3
gAlphaFactor = 0.1
gK_FrequentUnwantedWords = 125
gDelta = 1000
gClassNeutralThresholdVal = 0.49
gPercent = 0.5

# Static Parameters
gclassAbowfileName = "bow_classA"
gclassBbowfileName = "bow_classB"
gclassCbowfileName = "bow_classC"
gclassDbowfileName = "bow_classD"
gclassEbowfileName = "bow_classE"
gclassFbowfileName = "bow_classF"
gclassGbowfileName = "bow_classG"

gSetAllFileNames = Set([gclassAbowfileName, gclassBbowfileName, gclassCbowfileName, gclassDbowfileName, gclassEbowfileName, gclassFbowfileName, gclassGbowfileName])

gInputAllTweetsFileName = "rawTweets"
gClassManualFileName = "manualClassifiedFromFIRE"
gStopWordFileName = "stopWordList"
gTrainingDataSetFileName = "trainingDataSet"
gAcronymsFileName = "acronym"

glDeltaSetTweets  = []
glRemainingTweets = []
gStopWordList = []

gTweetCount = 0
gSetCount = 0
gRange = 0

# BOW of all classes
gBowAllClasses = []

# Manually Classified Tweets
gClassMan_Tweets = []

# Output Classified Tweets
gClassifiedTweets = []

# Acronym Dictionaty
gAcronymDict = {}

class tweet_struct(object):
     def __init__(self, id, tweet, scoreA, scoreB, scoreC, scoreD, scoreE, scoreF, scoreG):
        self.id = id
        self.tweet = tweet
        self.scoreA = 0.0
        self.scoreB = 0.0
        self.scoreC = 0.0
        self.scoreD = 0.0
        self.scoreE = 0.0
        self.scoreF = 0.0
        self.scoreG = 0.0
        self.svmProb = []

class bow_struct():
    def __int__(self):
        self.unigramList = []
        self.bigramList = []

# Creates Acronym Dictionary
def createAcronymDict(file_name):
    global gAcronymDict
    with open(file_name + ".txt", 'rt') as file:
        for line in file:
            line = str(line.lower())
            lines = line.split()
            s1 = lines[0]
            s2 = lines[1:]
            s3 = " ".join(str(x) for x in s2)
            gAcronymDict[s1] = s3

# Check for Acronyms
def getAcronyms(term):
    global gAcronymDict
    # Returns whether the acronym is modified
    # and the modified word
    if term in gAcronymDict.keys():
        return 1,gAcronymDict[term]
    else:
        return 0,term

# Reads bagOfWords from a File
def readBagOfWords(fileName):
    bowObj = bow_struct()
    bowObj.bigramList  = []
    bowObj.unigramList = []

    with open(fileName + ".txt", "r") as file:
        for line in file:
            line = str(line.lower())
            words = line.split()
            if len(words) > 1:
                bowObj.bigramList.append(words)
            else:
                bowObj.unigramList.append(words[0])
    file.close()
    return bowObj

def getAboveThreshold(tweetObj):    
    listThreshold = []
    aset = Set()

    maxVal = max(tweetObj.scoreA, tweetObj.scoreB, tweetObj.scoreC, tweetObj.scoreD, tweetObj.scoreE, tweetObj.scoreF, tweetObj.scoreG)
    if maxVal < gClassNeutralThresholdVal:
        return 0,listThreshold
    else:
        aset.add(maxVal)
        if tweetObj.scoreA >= (gPercent*maxVal) and tweetObj.scoreA >= gClassNeutralThresholdVal:
            aset.add(tweetObj.scoreA)
        if tweetObj.scoreB >= (gPercent*maxVal) and tweetObj.scoreB >= gClassNeutralThresholdVal:
            aset.add(tweetObj.scoreB)
        if tweetObj.scoreC >= (gPercent*maxVal) and tweetObj.scoreC >= gClassNeutralThresholdVal:
            aset.add(tweetObj.scoreC)
        if tweetObj.scoreD >= (gPercent*maxVal) and tweetObj.scoreD >= gClassNeutralThresholdVal:
            aset.add(tweetObj.scoreD)        
        if tweetObj.scoreE >= (gPercent*maxVal) and tweetObj.scoreE >= gClassNeutralThresholdVal:
            aset.add(tweetObj.scoreE)
        if tweetObj.scoreF >= (gPercent*maxVal) and tweetObj.scoreF >= gClassNeutralThresholdVal:
            aset.add(tweetObj.scoreF)
        if tweetObj.scoreG >= (gPercent*maxVal) and tweetObj.scoreG >= gClassNeutralThresholdVal:
            aset.add(tweetObj.scoreG)
        listThreshold = list(aset)
        return 1,listThreshold

# Classification based functions
def assignClassToTweet(tweetObj, listReq, recentlyClassifiedTweets):
    global gClassNeutralThresholdVal
    
    flag,aboveThresholdList = getAboveThreshold(tweetObj)

    # Classify to multiple Classes
    if not flag: # Below Threshold value
        gClassifiedTweets[7].append(tweetObj) # Neutral Class
        if listReq:
            recentlyClassifiedTweets[7].append(tweetObj)
        return recentlyClassifiedTweets

    if tweetObj.scoreA in aboveThresholdList:
        gClassifiedTweets[0].append(tweetObj) # Resource Available
        if listReq:
            recentlyClassifiedTweets[0].append(tweetObj)
    if tweetObj.scoreB in aboveThresholdList:
        gClassifiedTweets[1].append(tweetObj) # Resources Required
        if listReq:
            recentlyClassifiedTweets[1].append(tweetObj)
    if tweetObj.scoreC in aboveThresholdList:
        gClassifiedTweets[2].append(tweetObj) # Medical Resources Available
        if listReq:
            recentlyClassifiedTweets[2].append(tweetObj)
    if tweetObj.scoreD in aboveThresholdList:
        gClassifiedTweets[3].append(tweetObj) # Medical Resources Required
        if listReq:
            recentlyClassifiedTweets[3].append(tweetObj)
    if tweetObj.scoreE in aboveThresholdList:
        gClassifiedTweets[4].append(tweetObj) # Available/Requirement of rsc at specific Locations
        if listReq:
            recentlyClassifiedTweets[4].append(tweetObj)
    if tweetObj.scoreF in aboveThresholdList:
        gClassifiedTweets[5].append(tweetObj) # Activites of various NGOs
        if listReq:
            recentlyClassifiedTweets[5].append(tweetObj)
    if tweetObj.scoreG in aboveThresholdList:
        gClassifiedTweets[6].append(tweetObj) # Infrastructure damage and restoration report
        if listReq:
            recentlyClassifiedTweets[6].append(tweetObj)

    return recentlyClassifiedTweets

# Text Classification based on Uni-grams
def textClassify_Unigram(content, bowList):
    score = 0
    for word in content.split():
        if word in bowList:
            score = score + gUnigramWt
    return score

# Text Classification based on Bi-grams
def textClassify_Bigram(content, bowList):
    score = 0
    biwords = content.split()
    content_len = len(biwords)
    for i in range(0,content_len-2):
        temp = [biwords[i], biwords[i+1]]
        if temp in bowList:
            score = score + gBigramWt
    return score

# Text Classification of Tweet
def textClassify(content, bowObj):
    score = 0.0
    score = score + textClassify_Unigram(content, bowObj.unigramList)
    score = score + textClassify_Bigram(content, bowObj.bigramList)

    return score

# Classify Tweet based on Text and SVM (if required)
def classifyTweet(tweetObj, considerSvmClassify, recentlyClassifiedTweets):
    global gClassNeutralThresholdVal

    # Classification based on SVM Probabilty and Text Classification
    if considerSvmClassify:
        gClassNeutralThresholdVal = 0.49
        # Normalizing the Text classified Score
        sumTextValue = 0.001
        classTextValue = []
        for index in range(0,7):
            classTextValue.append(textClassify(tweetObj.tweet, gBowAllClasses[index]))
            sumTextValue = sumTextValue + classTextValue[index]
        normalizedTextValue =  [float(i) / sumTextValue for i in classTextValue]

        tweetObj.scoreA = ((1 - gAlphaFactor) * normalizedTextValue[0]) + (gAlphaFactor * tweetObj.svmProb[0])
        tweetObj.scoreB = ((1 - gAlphaFactor) * normalizedTextValue[1]) + (gAlphaFactor * tweetObj.svmProb[1])
        tweetObj.scoreC = ((1 - gAlphaFactor) * normalizedTextValue[2]) + (gAlphaFactor * tweetObj.svmProb[2])
        tweetObj.scoreD = ((1 - gAlphaFactor) * normalizedTextValue[3]) + (gAlphaFactor * tweetObj.svmProb[3])
        tweetObj.scoreE = ((1 - gAlphaFactor) * normalizedTextValue[4]) + (gAlphaFactor * tweetObj.svmProb[4])
        tweetObj.scoreF = ((1 - gAlphaFactor) * normalizedTextValue[5]) + (gAlphaFactor * tweetObj.svmProb[5])
        tweetObj.scoreG = ((1 - gAlphaFactor) * normalizedTextValue[6]) + (gAlphaFactor * tweetObj.svmProb[6])
    else:
        gClassNeutralThresholdVal = 1.25
        tweetObj.scoreA = textClassify(tweetObj.tweet, gBowAllClasses[0])
        tweetObj.scoreB = textClassify(tweetObj.tweet, gBowAllClasses[1])
        tweetObj.scoreC = textClassify(tweetObj.tweet, gBowAllClasses[2])
        tweetObj.scoreD = textClassify(tweetObj.tweet, gBowAllClasses[3])
        tweetObj.scoreE = textClassify(tweetObj.tweet, gBowAllClasses[4])
        tweetObj.scoreF = textClassify(tweetObj.tweet, gBowAllClasses[5])
        tweetObj.scoreG = textClassify(tweetObj.tweet, gBowAllClasses[6])

    # Assigning class to the Tweet
    return assignClassToTweet(tweetObj, considerSvmClassify, recentlyClassifiedTweets)

# Writes Classified tweets in file
def writeTweetClass(fileName, class_Tweets):
    with open(fileName + ".txt", "w") as file:
        for tweetObj in class_Tweets:
            file.write( str("%.3f" % tweetObj.scoreA) + "\t" + str("%.3f" % tweetObj.scoreB) + "\t" + str("%.3f" % tweetObj.scoreC) + "\t" + str("%.3f" % tweetObj.scoreD) + "\t" + str("%.3f" % tweetObj.scoreE) + "\t" + str("%.3f" % tweetObj.scoreF) + "\t" + str("%.3f" % tweetObj.scoreG) + "\t" + (tweetObj.id) + "\n")
    file.close()

# Outputs System's classified tweets
def writeAllTweetClasses():
    writeTweetClass("Classified_A", gClassifiedTweets[0])
    writeTweetClass("Classified_B", gClassifiedTweets[1])
    writeTweetClass("Classified_C", gClassifiedTweets[2])
    writeTweetClass("Classified_D", gClassifiedTweets[3])
    writeTweetClass("Classified_E", gClassifiedTweets[4])
    writeTweetClass("Classified_F", gClassifiedTweets[5])
    writeTweetClass("Classified_G", gClassifiedTweets[6])
    writeTweetClass("Classified_Neutral", gClassifiedTweets[7])
 
# Accuracy related functions
def readManualClassification(fileName):
    global gClassMan_Tweets
    with open(fileName + ".txt", "r") as file:
        for line in file:
            words = line.split()
            tweetId = words[2]
            ch = words[0][3]
            for iter in range(1,8):
                if ch == str(iter):
                    gClassMan_Tweets[iter-1].append(tweetId)
                    break

def plotEvaluationGraph(precision_N, recall_N, fMeasure_N, plotName, multiplePlots):
    incr_serial = []
    for iter in range(1, len(precision_N)+1):
        incr_serial.append(iter)

    plt.xlabel("Number of tweets")
    plt.ylabel("Percentage %")
    plt.ylim([0,100])
    plt.xlim([0,len(precision_N)])

    # Plot figures
    if multiplePlots:
        legene_p, = plt.plot(incr_serial, precision_N, 'r', label='precision')
        legene_r, = plt.plot(incr_serial, recall_N, 'g', label='recall')
        legene_f, = plt.plot(incr_serial, fMeasure_N, 'b', label='fMeasure')
        plt.legend(handles=[legene_p, legene_r, legene_f], loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3)
    else:
        legene_p, = plt.plot(incr_serial, precision_N, 'r', label='accuracy')
        plt.legend(handles=[legene_p], loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=1)

    try: # Remove file, if already exists
        os.remove(plotName + ".png")
    except:
        pass
    plt.savefig(plotName + ".png")
    plt.close()

def matchManual_ClassifiedClasses(sys_accuracy, sys_score, sys_N, baseClass, outputClass, plotName):
    score = 0
    precision = 0.0
    recall = 0.0
    precision_N = []
    recall_N = []
    fMeasure_N = []
    classCount = 0

    for baseId in baseClass:
        classCount = classCount + 1
        sys_N = sys_N + 1
        objIndex = 0
        found = 0
        while not found and objIndex < len(outputClass):
            outputObj = outputClass[objIndex]
            objIndex = objIndex + 1
            if outputObj.id == baseId:
                score = score + 1
                sys_score = sys_score + 1
                found = 1
        precision = float(score)/float(classCount)
        recall = float(score)/float(len(outputClass))
        precision_N.append(precision * 100.0)
        recall_N.append(recall * 100.0)
        sys_accuracy.append((float(sys_score)/float(sys_N)) * 100.0)
        if precision and recall:
            fMeasure_N.append((float(2.0*precision*recall)/float(precision+recall)) * 100.0)
        else:
            fMeasure_N.append(0.0)

    plotEvaluationGraph(precision_N, recall_N, fMeasure_N, plotName, 1)
    return sys_accuracy,sys_score,sys_N

# Checks accuracy of the System (all Tweets considered)
def checkAccuracy():
    global gClassMan_Tweets, gClassifiedTweets

    readManualClassification(gClassManualFileName)
    # Precision & Recall
    sys_accuracy = []
    sys_score = 0
    sys_N = 0

    sum = 0
    iter = 0
    for iter in range(0,8):
        sum = sum + len(gClassifiedTweets[iter])
        iter = iter + 1

    sys_accuracy,sys_score,sys_N = matchManual_ClassifiedClasses(sys_accuracy, sys_score, sys_N, gClassMan_Tweets[0], gClassifiedTweets[0], "Class_Resources_Available")
    sys_accuracy,sys_score,sys_N = matchManual_ClassifiedClasses(sys_accuracy, sys_score, sys_N, gClassMan_Tweets[1], gClassifiedTweets[1], "Class_Resources_Required")
    sys_accuracy,sys_score,sys_N = matchManual_ClassifiedClasses(sys_accuracy, sys_score, sys_N, gClassMan_Tweets[2], gClassifiedTweets[2], "Class_Medical_Rsc_Available")
    sys_accuracy,sys_score,sys_N = matchManual_ClassifiedClasses(sys_accuracy, sys_score, sys_N, gClassMan_Tweets[3], gClassifiedTweets[3], "Class_Medical_Rsc_Required")
    sys_accuracy,sys_score,sys_N = matchManual_ClassifiedClasses(sys_accuracy, sys_score, sys_N, gClassMan_Tweets[4], gClassifiedTweets[4], "Class_Rsc_at_Locations")
    sys_accuracy,sys_score,sys_N = matchManual_ClassifiedClasses(sys_accuracy, sys_score, sys_N, gClassMan_Tweets[5], gClassifiedTweets[5], "Class_NGO_Activites")
    sys_accuracy,sys_score,sys_N = matchManual_ClassifiedClasses(sys_accuracy, sys_score, sys_N, gClassMan_Tweets[6], gClassifiedTweets[6], "Class_Infr_Damage_Restoration")
    sys_accuracy,sys_score,sys_N = matchManual_ClassifiedClasses(sys_accuracy, sys_score, sys_N, gClassMan_Tweets[7], gClassifiedTweets[7], "Class_Neutral")

    plotEvaluationGraph(sys_accuracy, [], [], "System_Accuracy", 0)

    print "IR System's Evalutaion (" + str(gTweetCount) + " tweets): "
    print "Precision: " + str(float(sys_accuracy[-1]))

# Gets Labelled data for Training
def getTrainingTweetLists(filename):
    global gClassifiedTweets
    rFile = open(filename + ".txt", 'r')
    spaceJoin = " "
    for line in rFile:
        line = str(line.lower())
        data = line.split()
        obj = tweet_struct(data[1], str(spaceJoin.join(data[2:])), 0, 0, 0, 0, 0, 0, 0)
        obj.svmProb = []
        gClassifiedTweets[int(data[0])].append(obj)        

# Train SVM and do classification
def trainSVM_Classify(tweetSet):
    global gClassifiedTweets

    listAllTweets = []
    listLabel = []

    # Merging all classified Tweets - Train Set
    totalTrainData = 0
    for iter in range(0, len(gClassifiedTweets)):
        for obj in gClassifiedTweets[iter]:
            listAllTweets.append(obj.tweet)
            listLabel.append(iter)
            totalTrainData = totalTrainData + 1

    # Merging all Test Set
    for obj in tweetSet:
        listAllTweets.append(obj.tweet)

    # Vectorize all the tweets : Train + Test Set
    vectorizer = CountVectorizer(min_df=1)
    totalSet = vectorizer.fit_transform(listAllTweets)

    # Fit Train data to SVM
    trainSet = totalSet[0:totalTrainData]
    trainArray = trainSet.toarray()
    testSet = totalSet[totalTrainData:]
    testArray = testSet.toarray()
    clf = svm.SVC(kernel='linear',decision_function_shape='ovr')
    #clf = svm.SVC()
    clf.fit(trainArray, listLabel)

    # Predict the Test data
    index = 0
    for testVector in testArray:
        output = clf.decision_function([testVector])
        tweetSet[index].svmProb = [float(i) / sum(output[0]) for i in output[0]]
        index = index + 1

    return tweetSet

# Stop word checker
def isStopWord(word):
    word=word.lower()
    if word.isdigit() or len(word)<=3 or word in gStopWordList:
        return True
    else:
        return False

# Most frequent k-words from Neutral Tweets
def getKFreqWords(tweetSet):
    global gCounter
    wordCntr = Counter()

    # Count occurences of each word in Neutral Tweets
    for tweetObj in tweetSet:
        tweetContent = tweetObj.tweet
        data = tweetContent.split()
        for word in data:
            if not isStopWord(word):
                wordCntr[word] = wordCntr[word] + 1

    # Get the k-frequent words
    kFreqWordsTuples = wordCntr.most_common(gK_FrequentUnwantedWords)

    kFreqWords = []
    for tuple in kFreqWordsTuples:
        kFreqWords.append(tuple[0])

    return kFreqWords,wordCntr

# Calculates Term frequencies of the list of Classified Tweets
def getTermFrequency(classifiedTweets):
    listOfTermFreq = []
    for iter in range(0,8):
        wordCntr = Counter()
        listOfTermFreq.append(wordCntr)

    for classNum in range(0, len(classifiedTweets)):
        for tweetObj in classifiedTweets[classNum]:
            tweetContent = tweetObj.tweet
            data = tweetContent.split()
            for word in data:
                if not isStopWord(word):
                    listOfTermFreq[classNum][word] = listOfTermFreq[classNum][word] + 1
    return listOfTermFreq

# SVM Classification and updating BOW's
gCounter = 0
def classifyDeltaTweets(tweetList1000):
    global gCounter, gAlphaFactor, gClassNeutralThresholdVal

    gCounter = gCounter + 1
    print "Iteration: " + str(gCounter)
	
    # Train SVM and get SVM Classified Tweets
    tweetList1000 = trainSVM_Classify(tweetList1000)

    # Recently classified Tweets, will be used to update global BOW
    recentlyClassifiedTweets = []
    for iter in range(0,8):
        recentlyClassifiedTweets.append([])
    # Update alpha-factor to give more weightage to SVM classification
    if (gCounter - 1) != 0:
        gAlphaFactor = gAlphaFactor +  (gAlphaFactor / ((gCounter-1) * 1.0))

    # Classify these 'delta' tweets
    for tweetObj in tweetList1000:
        recentlyClassifiedTweets = classifyTweet(tweetObj, 1, recentlyClassifiedTweets)

    # Removing unwanted words using Neutral Classified Tweets
    freqUnwantedWords,termCounter = getKFreqWords(recentlyClassifiedTweets[7])

    # Get Term frequencies of the Recently Classified Tweets
    termFreqEachClass = getTermFrequency(recentlyClassifiedTweets)

    # Update BOW
    for classIndex in range(0,7):
        # Considering each Class
        for tweetObj in recentlyClassifiedTweets[classIndex]:
            # Append each word of the tweet as unigram in its class's BOW List
            data = (tweetObj.tweet).split()
            for word in data:
                # Do not consider Stop Words and remove Frequent Neutral words
                if not isStopWord(word) and word not in freqUnwantedWords and word not in gBowAllClasses[classIndex].unigramList and termFreqEachClass[classIndex][word] > 2 and termCounter[word] > 1:
                    gBowAllClasses[classIndex].unigramList.append(word)

# Classify tweet as manually Neutral Tweet
def classifyManAsNeutralTweets(id):
    global gClassMan_Tweets
    bFlag = 0
    for classList in gClassMan_Tweets:
        if id in classList:
            bFlag = 1
            break

    if bFlag == 0:
        # Neutral Tweet
        gClassMan_Tweets[7].append(id)
        
# Creats set of 1000 tweets
def createSetOf1000(tweetId, content):
    global gTweetCount, gDelta, gSetCount, gRange, glDeltaSetTweets, glRemainingTweets

    tweetObj = tweet_struct(tweetId, content, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    for iter in range(0,8):
        tweetObj.svmProb.append([])
    classifyManAsNeutralTweets(tweetId)   

    gTweetCount = gTweetCount + 1
    # Select tweets for SVM classification
    if gRange  < gTweetCount:
        glDeltaSetTweets.append(tweetObj)
        if gSetCount == gDelta:
            # Classify Set of 'delta' Tweets 
            classifyDeltaTweets(glDeltaSetTweets)
            gRange = gRange + 9900
            glDeltaSetTweets = []
            gSetCount = 0
        else:
            gSetCount = gSetCount + 1
    else:
        glRemainingTweets.append(tweetObj)

# Creates stop word List
def createStopWord():
    global gStopWordList

    rfile = open(gStopWordFileName + ".txt", "r")
    for line in rfile:
        line = str(line.lower())
        data = line.split()
        for word in data:
            gStopWordList.append(word)
    rfile.close()

# Initializations
def doInitialization():
    global gClassifiedTweets, gClassMan_Tweets

    for iter in range(0,8):
        gClassifiedTweets.append([])

    for iter in range(0,8):
        gClassMan_Tweets.append([])

    # Read manually classified Bag of words
    for bowClassFileName in gSetAllFileNames:
        gBowAllClasses.append(readBagOfWords(bowClassFileName))

    # Create Stop words List
    createStopWord()

    # Get Training Data
    getTrainingTweetLists(gTrainingDataSetFileName)

    # Create Acronym Dictionary
    createAcronymDict(gAcronymsFileName)

# Main-function
def main():

    doInitialization()

    with open(gInputAllTweetsFileName + ".txt", "r") as r_file:
        mod_tweet = ""
        tweet_id  = ""
        total_read = 0
        # Preprocessing Steps
        for line in r_file:
            line = re.sub(r'@([A-Za-z0-9_]+):*', r'', line)                    # Remove all @*
            line = line.translate(string.maketrans("",""), string.punctuation) # Remove all punctuations
            line = str(line.lower())
            tweet_line = line.split()
            if tweet_id == "": # Tweet Id Init
                tweet_id = tweet_line[0]
            for word in tweet_line:
                if fnmatch.fnmatch(word, "http*") or fnmatch.fnmatch(word, "*-*-*"):
                    pass
                else:
                    word = re.sub(r'[^\w]', '', word)
                if re.match(r'^\d{18}', str(word), 0) and mod_tweet != "":  # To handle multiple line tweet
                    createSetOf1000(tweet_id, mod_tweet[19:])                    # Write Previous Tweet contents & Tweet Classification
                    tweet_id = word                                         # Store current tweet id
                    mod_tweet = str(word)
                    total_read = total_read + 1
                else:
                    change,mod_word = getAcronyms(word) 
                    if change:
                        word = word.replace(word, mod_word)
                    mod_tweet = mod_tweet + " " + str(word)

    # Write Last Tweet contents & Tweet Classification
    createSetOf1000(tweet_id, mod_tweet)

    # Classify Remaining Tweets
    for tweetObj in glRemainingTweets:
        classifyTweet(tweetObj, 0, [])

    # Results
    writeAllTweetClasses()
    checkAccuracy()
    r_file.close()

if __name__ == "__main__": main()
