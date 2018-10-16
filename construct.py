import re
import pandas as pd
import nltk as nltk
from collections import Counter
import json
from textblob import TextBlob


# Class to for trie node
class TrieNode(object):
    def __init__(self, char):
        self.char = char
        self.children = []
        # Is it the last character of the word.`
        self.word_finished = False
        # How many times this character appeared in the addition process
        self.counter = 1


# Class to clean sample conversation, building trie and auto completion
class AutoComplete():
    def __init__(self):
        """
        Initializer
        fname: the path for training data
        ngram_n: ngram used for process text
        num_completion: number of completed question returned
        root: root of trie
        """
        self.fname = "sample_conversations.json"
        self.ngram_n = 5
        self.num_completion = 5
        self.ngram_dict = {}
        self.root = TrieNode("*")

    def add(self, question):
        """
        Add questions to trie
        :param question: question to be inserted
        :return:
        """
        node = self.root
        for char in question:
            found_in_child = False
            # Search for the character in the children of the present `node`
            for child in node.children:
                if child.char == char:
                    # We found it, increase the counter by 1 to keep track that another
                    # word has it as well
                    child.counter += 1
                    # And point the node to the child that contains this char
                    node = child
                    found_in_child = True
                    break
            # We did not find it so add a new child
            if not found_in_child:
                new_node = TrieNode(char)
                node.children.append(new_node)
                # And then point node to the new child
                node = new_node
            # Sort the children for their occur frequency
            node.children.sort(key=lambda x: x.counter, reverse=True)
            # End of the question, stop here
            if char == '?':
                break
        # Everything finished. Mark it as the end of a question.
        node.word_finished = True

    def find_prefix(self, prefix):
        """
        Return the top N frequent questions asked from history
        :param prefix: prefix to be completed
        :return: top N frequently asked questions start with prefix
        """
        node = self.root
        if not node.children:
            return
        for char in prefix:
            char_not_found = True
            # Search through all the children of the present `node`
            for child in node.children:
                if child.char.lower() == char.lower():
                    # We found the char existing in the child.
                    char_not_found = False
                    # Assign node as the child containing the char and break
                    node = child
                    break
            # Return False anyway when we did not find a char.
            if char_not_found:
                return
        rst = []
        self.find_topN_children(rst, node, prefix)
        return rst

    def find_topN_children(self, rst, node, pre):
        """
        Find the top N frequency asked questions
        :param rst: list to store result
        :param node: current node of the trie
        :param pre: prefix
        :return: top N frequently asked questions
        """
        # Find a complete question, add to the results
        if node.word_finished:
            rst.append(pre);
            return
        # Do dfs to a node to find a complete question
        for child in node.children:
            # Already got enough questions, stop
            if len(rst) >= self.num_completion:
                break
            self.find_topN_children(rst, child, pre + child.char)
        return

    def get_questions(self, text):
        """
        Extract the question sentence from a message
        :param text: conversations containing questions
        :return: question sentence
        """
        re.sub('\s+', ' ', text).encode('utf-8').strip()
        m = re.findall("[,\.:!;].+\?", text)
        if len(m) > 0:
            return m[0][1:].strip()
        else:
            return text

    def clean_conversations(self):
        """
        1. Extract questions from sample conversation
        2. Use ngram to remove similar questions.
        :return: all questions
        """

        print("Reading sample conversations...")
        # Read agent's messages from sample_conversations
        conversations = pd.read_json(self.fname)
        messages = [i['Messages'] for i in [j for j in conversations['Issues']]]
        agent_messages_all = [[j['Text'] for j in i if not j['IsFromCustomer']] for i in messages]
        agent_messages_list = [item for sublist in [a for a in agent_messages_all if len(a) > 0] for item in sublist]
        agent_messages = [item for sublist in [nltk.sent_tokenize(a) for a in agent_messages_list] for item in sublist]

        print("Extracting frequently asked problems...")
        # Get agent's questions from sample conversations
        # get messages which contain questions
        agent_questions_uncleaned = [text for text in agent_messages if "?" in text]
        # get the question sentense
        agent_questions_cleaned = [self.get_questions(text) for text in agent_questions_uncleaned]
        # correct spelling error
        print("Checking spelling...This will take for a while...")
        agent_questions_corrected = agent_questions_cleaned
        # agent_questions_corrected = [str(TextBlob(i).correct()) for i in agent_questions_cleaned]
        # remove repeated questions
        questions = list(set(agent_questions_corrected))

        print("Done correcting, now analyzing the questions...")
        # get ngrams from the questions
        frequencies = Counter()
        for question in questions:
            ngram = nltk.ngrams(question.split(), self.ngram_n)
            frequencies += Counter(ngram)
        # Map ngram to questions from low frequency to high frequency gram
        temp = []
        ngrams = []
        sorted_questions_all = []
        visited = set()
        for row, freq in frequencies.most_common()[::-1]:
            gram = ' '.join(row)
            for question in questions:
                if question not in visited:
                    if gram in question:
                        temp.append(question)
                        visited.add(question)
            if (len(temp) > 0):
                sorted_questions_all.append(temp[:])
                ngrams.append(gram)
                temp = []
        # Get one question to represent a ngram
        sorted_questions = [s[0] for s in sorted_questions_all]
        self.ngram_dict = dict(zip(ngrams, sorted_questions))
        with open("ngram_dict.json", 'w') as w:
            json.dump(self.ngram_dict, w)

    def read_ngram_dict(self):
        """
        Read ngram dictionary
        :return:
        """
        with open(self.fname) as f:
            self.ngram_dict = json.load(f)

    def construct_trie(self, sorted_questions):
        """
        Construct trie
        :param sorted_questions:
        :return:
        """
        print("Almost there! Preparing to make completions...")
        for question in self.ngram_dict.values():
            self.add(question)

    def run_from_ngram_dict(self):
        """
        Read existing ngram json file and construct trie
        :return:
        """
        self.read_ngram_dict()
        self.construct_trie(self.ngram_dict.values())
        print("Ready to go!")

    def run_from_sample_conversation(self):
        """
        Analyze sample conversation, extract questions and construct trie
        :return:
        """
        self.clean_conversations()
        self.construct_trie(self.ngram_dict.values())
        print("Ready to go!")

    def auto_completion(self, prefix):
        """
        get auto completion
        :param prefix:
        :return:
        """
        return self.find_prefix(prefix.strip().lower())
