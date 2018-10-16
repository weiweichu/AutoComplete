# AutoComplete
This is to learn from sample conversation and auto complete questions.

How to run?

1. python server.py. To see options: python server.py -h

2. curl http://localhost:8000/autocomplete?prefix=What+is+y

What will be returned?

1. A json file containing the ngram dictionary. 

2. The autocomplete questions.
