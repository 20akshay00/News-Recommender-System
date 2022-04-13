from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD # TruncatedSVD
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

def TF_IDF(corpus):
    vectorizer = TfidfVectorizer(max_features=1000)
    vectors = vectorizer.fit_transform(corpus)
    return vectors

def LSA(corpus, num_topics):
    vectorized_corpus = TF_IDF(corpus)
    sv_dec_lsa = TruncatedSVD(n_components = num_topics, algorithm='randomized')
    lsa_mat = sv_dec_lsa.fit_transform(vectorized_corpus)
    return lsa_mat                   

def get_user_vector(docs, weights = -1):
    if(weights == -1): weights = np.ones(docs.shape[0])
    return np.average(docs, weights=weights, axis = 0).reshape(1, docs.shape[1])

# corpus - list of topic-vectorized documents, user - weighted average of topic-vectorized docs, N - number of recommendations
def content_based_recommend(corpus, user, N):
    cosines = 1 - cdist(user, corpus)[0]
    nearest_indices = np.argpartition(cosines, -N)[-N:]
    return nearest_indices[np.argsort(cosines[nearest_indices])][::-1]

def get_score(time, num_words, click, mean = 445, var = 60):
    if click in [-1, 1]:
        return click
    else:
        mean_t, var_t  = (1/mean * num_words) * 60, (1/var * num_words) * 60 # reading time in seconds 
        amp  = np.random.uniform(0.85, 0.95)
        
        if time <= mean_t:
            return amp * pow(-np.e, (time - mean_t)**2/(2 * var_t))
        elif (mean_t < time) and time < (mean_t + 2 * var_t):
            return amp
        else:
            return 0