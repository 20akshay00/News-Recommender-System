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
    user = (weights @ docs)
    return (user / np.linalg.norm(user)).reshape(1, docs.shape[1])

# corpus - list of topic-vectorized documents, user - weighted average of topic-vectorized docs, N - number of recommendations
def content_based_recommend(corpus, user, N):
    cosines = 1 - cdist(user, corpus)[0]
    nearest_indices = np.argpartition(cosines, -N)[-N:]
    return nearest_indices[np.argsort(cosines[nearest_indices])][::-1]

def get_engagement(time, num_words, click, mean = 445, var = 60):
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

def get_ratings_mat(corpus, user_doc_dict, user_rating_dict):
    user_vectors = np.array([get_user_vector(corpus[user_doc_dict[i]], user_rating_dict[i]) for i in user_doc_dict.keys()])
    
    ratings = np.empty((user_vectors.shape[0], corpus.shape[0]))
    ratings.fill(np.nan)

    for (user_ind, doc_inds) in zip(user_doc_dict.keys(), user_doc_dict.values()):
        ratings[user_ind - 1][doc_inds] = np.array(user_rating_dict[user_ind])
    
    return ratings

# N is the number of recommendations, corpus is vectorized LSA
def get_collab_recommendations(corpus, user_doc_dict, user_rating_dict, N): 
    av_ratings = np.nansum(get_ratings_mat(corpus, user_doc_dict, user_rating_dict), axis = 0)
    recommend_indices = np.argpartition(av_ratings, -N)[-N:]
    return recommend_indices