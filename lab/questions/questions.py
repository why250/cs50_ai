import nltk
import sys
import os
import string
import math 

nltk.download('stopwords')

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    while True:
        query = set(tokenize(input("Query: ")))
        if query == "exit":
            break
        # Determine top file matches according to TF-IDF
        filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

        # Extract sentences from top files
        sentences = dict()
        for filename in filenames:
            for passage in files[filename].split("\n"):
                for sentence in nltk.sent_tokenize(passage):
                    tokens = tokenize(sentence)
                    if tokens:
                        sentences[sentence] = tokens

        # Compute IDF values across sentences
        idfs = compute_idfs(sentences)

        # Determine top sentence matches
        matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
        for match in matches:
            print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = os.listdir(directory)
    dict = {}
    for file in files:
        with open(os.path.join(directory,file)) as f:
            contents = f.read()
            dict[file] = contents
    return dict

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    stopwords = nltk.corpus.stopwords.words("english")
    words = [word.lower() for word in nltk.word_tokenize(document) 
            if word not in stopwords and word not in string.punctuation]
    return words

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    num_docs = len(documents.keys())
    num_word_appear_docs = {}
    for doc in documents.keys():
        flag = False
        words = documents[doc]
        for word in words:
            if word not in num_word_appear_docs.keys():
                num_word_appear_docs[word] = 1
                flag = True
            elif flag == False:
                num_word_appear_docs[word] += 1
                flag = True
    words_idfs = {}
    for word in num_word_appear_docs.keys():
        words_idfs[word] = math.log(num_docs/num_word_appear_docs[word])
    return words_idfs
# Inverse document frequency (IDF) represents specialbity of each words

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    file_idfs = dict.fromkeys(files.keys())

    for file in files.keys():
        file_idfs[file] = 0
        for word in query:
            if word in files[file]:
                file_idfs[file] += files[file].count(word)*idfs[word]
    
    return sorted(files.keys(),key = lambda file: file_idfs[file],reverse = True)[:n]


# lambda function
# lambda var1,var2,... : expression(var1,var2,...)
# equals to 
# def function(var1,var2,...):
#   return expression(var1,var2,...)

# sorted(iterable,*,key=None,reverse=False)


def query_term_density(query,sentence):
    return sum([word in query for word in sentence])/len(sentence)

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_idfs = dict.fromkeys(sentences.keys())
    for sentence in sentences.keys():
        sentence_idfs[sentence] = 0
        for word in query:
            if word not in sentences[sentence]:
                continue
            sentence_idfs[sentence] += idfs[word]

    top_sentences = sorted(sentences.keys(),key = lambda sentence: 
    (sentence_idfs[sentence],query_term_density(query,sentence)),reverse = True)[:n]
    return top_sentences

if __name__ == "__main__":
    main()
