from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import nltk
from nltk.tokenize import sent_tokenize
import numpy as np
import scipy
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from file_io import file_search

nltk.download('punkt_tab')

def sentence_split(text):
    return list(sent_tokenize(text))

def matricize(sentences, max_df, min_df):
    vectorizer = TfidfVectorizer(
        strip_accents='unicode', analyzer='char_wb', 
        max_df=max_df, min_df=min_df,
        norm=None)
    vectors = vectorizer.fit_transform(sentences)
    return vectors

def rank(scores, sentences):
    return sorted(((scores[i], s, i) for i, s in enumerate(sentences)), reverse=True)
    
def summarize(text, slider_value, max_df, min_df, k):   
    sentences = sentence_split(text)

    M = matricize(sentences, max_df, min_df)

    U, S, V = np.linalg.svd(M.toarray().T, full_matrices=False)

    V = V.T
    Vmu = np.mean(V, axis=0)
    Vstd = np.std(V, axis=0)

    V[V < Vmu + k * Vstd] = 0
    V = V.T

    scores = np.sum((np.diag(S) @ V), axis=0)

    ranked = rank(scores, sentences)

    n = int(len(sentences) * slider_value/100)

    if n <= 0:
        n = 1
    if n > len(sentences):
        n = len(sentences)

    possibilities = ranked[:n]
    sorted_possibilities = list(sorted(((i, s) for score, s, i in possibilities), reverse=False))
    summary = "\n".join([s for (i, s) in sorted_possibilities])

    return summary

