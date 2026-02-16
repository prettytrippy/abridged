from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import nltk
from nltk.tokenize import sent_tokenize
import numpy as np
import scipy
import scipy.sparse as sp
import scipy.sparse.linalg as spla

nltk.download('punkt_tab')

def sentence_split(text):
    return list(sent_tokenize(text))

def matricize(sentences, max_df, min_df):
    vectorizer = TfidfVectorizer(
        strip_accents='unicode', analyzer='char_wb', 
        max_df=max_df, min_df=min_df,
        norm=None)
    vectors = vectorizer.fit_transform(sentences)
    return cosine_similarity(vectors)

def pagerank(A, alpha=0.85):
    n = A.shape[0]

    # Degree matrix
    deg = np.array(A.sum(axis=1)).ravel()
    deg[deg == 0] = 1e-8  # avoid division by zero

    Dinv = sp.diags(1.0 / deg)
    M = sp.eye(n) - alpha * Dinv @ A

    # RHS: uniform teleportation
    rhs = np.full(n, (1 - alpha) / n)

    pr, info = spla.cg(M, rhs, maxiter=4)
    if info != 0:
        raise RuntimeError(f"CG did not converge (info={info})")

    pr /= pr.sum()
    return pr

def score(M, alpha):
    return pagerank(M, alpha)

def rank(scores, sentences):
    return sorted(((scores[i], s, i) for i, s in enumerate(sentences)), reverse=True)
    
def summarize(text, slider_value, max_df, min_df, alpha):   
    sentences = sentence_split(text)
    M = matricize(sentences, max_df, min_df)
    scores = score(M, alpha)
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
