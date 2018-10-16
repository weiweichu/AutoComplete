import re
import pandas as pd
import nltk as nltk
from collections import Counter
import json
from textblob import TextBlob



with open('ngram_and_question.json') as f:
    data = json.load(f)
print data.keys()