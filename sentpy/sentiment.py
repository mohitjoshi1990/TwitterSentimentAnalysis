from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
import socket
from pyspark.sql import SQLContext
from pyspark.sql import Row
import sys
import requests
import shutil
import nltk
from nltk.tokenize import word_tokenize
from pyspark.mllib.feature import HashingTF, IDF
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import NaiveBayes, NaiveBayesModel
from pyspark.mllib.classification import LogisticRegressionWithLBFGS, LogisticRegressionModel
from pyspark.mllib.classification import SVMWithSGD, SVMModel
from pyspark.mllib.tree import DecisionTree, DecisionTreeModel
from nltk.classify import ClassifierI
import statistics
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

conf = SparkConf()
conf.setAppName("SentimentAnalysis")
sc = SparkContext(conf=conf)
htf = HashingTF(50000)

all_words = []
documents = []

def wc(data):
  words = word_tokenize(data)
  tag = nltk.pos_tag(words)
  for w in tag:
    all_words.append(w[0].lower())
  return all_words

def trainData():

  positive_words = sc.textFile("/usr/local/spark/pos.txt")
  negative_words = sc.textFile("/usr/local/spark/neg.txt")

  pos_sp = positive_words.flatMap(lambda line: line.split("\n")).collect()
  neg_sp = negative_words.flatMap(lambda line: line.split("\n")).collect()

  for p in pos_sp:
    documents.append({"text": p , "label": 1})

  for p in neg_sp:
    documents.append({"text": p , "label": 0})

  raw_data = sc.parallelize(documents, 4)
  raw_tokenized = raw_data.map(lambda dic : {"text": wc(dic["text"]) , "label" : dic["label"]})

  htf = HashingTF(50000)
  raw_hashed = raw_tokenized.map(lambda dic : LabeledPoint(dic["label"], htf.transform(dic["text"])))
  raw_hashed.persist()

  trained_hashed, test_hashed = raw_hashed.randomSplit([0.65, 0.35])

  LR_model = LogisticRegressionWithLBFGS.train(trained_hashed)
  LR_prediction_and_labels = test_hashed.map(lambda point : (LR_model.predict(point.features), point.label))
  LR_correct = LR_prediction_and_labels.filter(lambda (predicted, actual): predicted == actual)
  LR_accuracy = LR_correct.count() / float(test_hashed.count())
  LR_output_dir = 'usr/local/Spark/LogisticRegression'
  shutil.rmtree("usr/local/Spark/LogisticRegression/metadata", ignore_errors=True)
  shutil.rmtree(LR_output_dir, ignore_errors=True)
  LR_model.save(sc, LR_output_dir)


  NB_model = NaiveBayes.train(trained_hashed)
  NB_prediction_and_labels = test_hashed.map(lambda point : (NB_model.predict(point.features), point.label))
  NB_correct = NB_prediction_and_labels.filter(lambda (predicted, actual): predicted == actual)
  NB_accuracy = NB_correct.count() / float(test_hashed.count())
  NB_output_dir = 'usr/local/Spark/Naive'
  shutil.rmtree("usr/local/Spark/Naive/metadata", ignore_errors=True)
  shutil.rmtree(NB_output_dir, ignore_errors=True)
  NB_model.save(sc, NB_output_dir)


  print "LR training accuracy:" + str(LR_accuracy * 100) + " %"
  print "NB training accuracy:" + str(NB_accuracy * 100) + " %"

trainData()

class Classifier(ClassifierI):

    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def find_max_mode(self,list1):
        list_table = statistics._counts(list1)
        len_table = len(list_table)

        if len_table == 1:
            max_mode = statistics.mode(list1)
        else:
            new_list = []
            for i in range(len_table):
                new_list.append(list_table[i][0])
            max_mode = max(new_list) # use the max value here
        return max_mode

    def classify(self, transformer):
        votes = []
        for c in self._classifiers:
            v = c.predict(transformer)
            votes.append(v)
        return self.find_max_mode(votes)


def sentiment(test_sample):
    test_sample = test_sample.split(" ")
    trans = htf.transform(test_sample)
    return classifier.classify(trans)


NB_output_dir = 'usr/local/Spark/Naive'
NB_load_model= NaiveBayesModel.load(sc, NB_output_dir)
#NB_load_model= NB_model

LR_output_dir = 'usr/local/Spark/LogisticRegression'
LR_load_model= LogisticRegressionModel.load(sc, LR_output_dir)
#LR_load_model= LR_model


classifier = Classifier(NB_load_model, LR_load_model)

spark = SparkSession.builder.getOrCreate();
fetched_tweets = spark.read.json("/usr/local/spark/blacklivesmatter.jsonl")

def get_sql_context_instance(spark_context):
        if ('sqlContextSingletonInstance' not in globals()):
           globals()['sqlContextSingletonInstance'] = SQLContext(spark_context)
        return globals()['sqlContextSingletonInstance']

def process_rdd(rdd):

    sql_context = get_sql_context_instance(rdd.context)

    row_rdd = rdd.map(lambda w: Row(text=w[0], senti=int(w[1])))


    hashtags_df = sql_context.createDataFrame(row_rdd)
    hashtags_df.collect()

    hashtags_df.registerTempTable("hashtags")

    hashtag_totalcounts_df = sql_context.sql("select text, senti from hashtags")
    hashtag_totalcounts_df.show()
    print "total tweets are :"+str(hashtag_totalcounts_df.count())

    htag_positivecounts_df = sql_context.sql("select text, senti from hashtags where senti=1")

    print "positive tweets are :"+str(htag_positivecounts_df.count())
    htag_negcounts_df = sql_context.sql("select text, senti from hashtags where senti=0")

    print "negative tweets are :"+str(htag_negcounts_df.count())



ascii_encoded_tweets = fetched_tweets.rdd.map(lambda x :(x.full_text.encode('ascii', 'ignore'))).collect()
sentiment_tweet = map(lambda x :(x,sentiment(x)), ascii_encoded_tweets)
parallelized_rdd = sc.parallelize(sentiment_tweet,4)
process_rdd(parallelized_rdd)
