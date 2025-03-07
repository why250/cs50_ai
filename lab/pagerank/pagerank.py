import os
import random
import re
import sys
import numpy as np

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    N = len(corpus.keys())
    if len(corpus[page]) == 0:
        prob_dist = dict.fromkeys(corpus.keys(),1/N) # dict.fromkeys generate a dictionary with all keys in corpus and value is 1/len(corpus)
    else:
        prob_dist = dict.fromkeys(corpus.keys(),(1-damping_factor)/N)
    for p in corpus.keys():
        if p in corpus[page]:
            prob_dist[p] += damping_factor/len(corpus[page])

    return prob_dist




def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict.fromkeys(corpus.keys(),0)
    next_page = random.choice(list(corpus.keys())) # random.choice() accepts a list
    pagerank[next_page] += 1
    for i in range(n-1):
        prob_dist = transition_model(corpus,next_page,damping_factor)
        x = random.random()
        prob_sum = 0
        for page,prob in prob_dist.items(): # prob_dist.items() returns a list of tuples
            prob_sum += prob
            if prob_sum > x:
                break
        next_page = page
        pagerank[next_page] += 1
    pagerank = {p:pagerank[p]/n for p in pagerank.keys()}
    print(f"Sum of sample_pagerank = {sum(pagerank.values())}")

    return pagerank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Ctrl + / 注释
    # Ctrl + ] 缩进
    N = len(corpus.keys())
    numlinks = {p:len(corpus[p]) for p in corpus.keys()}
    pagerank = dict.fromkeys(corpus.keys(),1/N)
    flag = True
    new_pagerank = {}
    while flag:
        flag =  False
        for p in corpus.keys():
            x = sum(pagerank[i]/numlinks[i] for i in corpus.keys() if p in corpus[i] and numlinks[i] != 0)
            x += sum(pagerank[i]/N for i in corpus.keys() if numlinks[i] == 0) 
            #  page that has no links at all should be interpreted as having one link for every page in the corpus (including itself).
            new_pagerank[p] = (1-damping_factor)/N + damping_factor*x
        for p in corpus.keys():
            if abs(new_pagerank[p]-pagerank[p])>0.001:
                flag = True
            pagerank[p] = new_pagerank[p]
    print(f"Sum of iterate_pagerank = {sum(pagerank.values()):.3f}") # :.3f keep 3 digits after .
    
    return pagerank


if __name__ == "__main__":
    main()
