from __future__ import print_function, division
import sys, os, json
sys.path.append(os.path.abspath("."))
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer


STOP_WORDS = set(stopwords.words('english'))
SEPARATOR_REGEX = RegexpTokenizer(r'\w+')
PORTER_STEMMER = PorterStemmer()

__author__ = 'panzer'

def tokenizer(sentence, remove_stops = True, stem = True):
  decoded = sentence.encode('ascii', 'ignore').decode('ascii')
  tokens = SEPARATOR_REGEX.tokenize(decoded)
  if remove_stops and stem:
    return [PORTER_STEMMER.stem(token) for token in tokens if token not in STOP_WORDS]
  elif remove_stops:
    return [token for token in tokens if token not in STOP_WORDS]
  elif stem:
    return [PORTER_STEMMER.stem(token) for token in tokens]
  else:
    return tokens

class Token:
  def __init__(self, name):
    self.name = name
    self.word_count = 0
    self.doc_count = 0
    self.tfidf = 0
    self.weight = 0

  def __str__(self):
    return "Word : %s, TFIDF = %0.4f"%(self.name, self.tfidf)

class TFIDF:
  def __init__(self):
    self.words = 0
    self.docs = 0
    self.word_scores = {}

  def update_word(self, name, word_count):
    word_score = self.word_scores.get(name)
    if not word_score:
      word_score = Token(name)
    word_score.doc_count += 1
    word_score.word_count += word_count
    self.word_scores[name]=word_score

  def update_record(self, words_count, words_map):
    self.words += words_count
    self.docs += 1
    for word in words_map:
      self.update_word(word, words_map.get(word))

  def compute_tfidf(self):
    for word in self.word_scores:
      word_stat = self.word_scores.get(word)
      word_stat.tfidf = self.score(word_stat.word_count, word_stat.doc_count)
      self.word_scores[word] = word_stat

  def score(self, word_count, doc_count):
    return word_count/self.words * (self.docs/doc_count)

  def get_words_on_tfidf(self, k=None):
    scores = self.word_scores.values()
    scores = sorted(scores, key=lambda token : token.tfidf, reverse=True)
    if k is None:
      return scores
    else:
      return scores[:k]

  def get_word_info(self, name):
    return self.word_scores.get(name, None)

  def update_word_weight(self, name, weight):
    word_score = self.word_scores.get(name)
    word_score.weight = weight
    self.word_scores[name] = word_score

  @staticmethod
  def count_words(words):
    count_map = {}
    for word in words:
      count_map[word] = count_map.get(word, 0) + 1
    return count_map

def get_docs():
  with open("data/eclipse/consolidated/eclipse_bugs.json", "r") as f:
    data = json.load(f)
  return data

def _main():
  documents = []
  json_data = get_docs()
  tfidf = TFIDF()
  for key, bug in json_data.items():
    document =  tokenizer(" ".join(bug["descriptions"]))
    count_map = TFIDF.count_words(document)
    tfidf.update_record(len(document), count_map)
    documents.append(document)
  tfidf.compute_tfidf()
  top_words = tfidf.get_words_on_tfidf(5)
  for word in top_words:
    print(word)

if __name__ == "__main__":
  _main()


