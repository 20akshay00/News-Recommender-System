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

# calculate user vector as a linear combination of the documents they have read
def get_user_vector(docs, weights = None):
    if(weights is None): weights = np.ones(docs.shape[0])
    user = (weights @ docs)
    return (user / np.linalg.norm(user)).reshape(1, docs.shape[1])

# corpus - list of topic-vectorized documents, user - weighted average of topic-vectorized docs, N - number of recommendations
def content_based_recommend(corpus, user, N):
    cosines = 1 - cdist(user, corpus)[0]
    nearest_indices = np.argpartition(cosines, -N)[-N:]
    return nearest_indices[np.argsort(cosines[nearest_indices])][::-1]

# calculate engagement score implicitly using time spent on the page by the user
def get_engagement(time, num_words, click, mean = 445, var = 60):
    if click in [-1, 1]:
        return click
    else:
        mean_t, std_t  = (1/mean * num_words) * 60, np.sqrt((1/var * num_words) * 60) # reading time in seconds 
        amp  = np.random.uniform(0.85, 0.95)
        
        if time <= mean_t: return amp * pow(np.e, -(time - mean_t)**2/(2 * std_t**2))
        elif (mean_t < time) and time < (mean_t + 4 * std_t): return amp
        else: return 0

# calculate ratings using explicit rating and time spent on page
def get_ratings_mat(corpus, user_doc_dict, user_rating_dict, user_vec_dim):    
    ratings = np.empty((user_vec_dim, corpus.shape[0]))
    ratings.fill(np.nan)

    for (user_ind, doc_inds) in zip(user_doc_dict.keys(), user_doc_dict.values()):
        ratings[user_ind - 1][doc_inds] = np.array(user_rating_dict[user_ind])
    
    return ratings

# N is the number of recommendations, corpus is vectorized LSA
def collab_based_recommend(user, corpus, user_doc_dict, user_rating_dict, N): 
    # find N nearest users
    user_vectors = np.array([get_user_vector(corpus[user_doc_dict[i]], user_rating_dict[i]) for i in user_doc_dict.keys()])
    nearest_user_inds = content_based_recommend(user_vectors, user.reshape(1, -1), 10)

    # calculate average document rating for these users over the corpus, and pick top N
    av_ratings = np.nanmean(get_ratings_mat(corpus, user_doc_dict, user_rating_dict, user_vectors.shape[0])[nearest_user_inds], axis = 0)
    recommend_indices = np.argpartition(av_ratings, -N)[-N:]
    return recommend_indices