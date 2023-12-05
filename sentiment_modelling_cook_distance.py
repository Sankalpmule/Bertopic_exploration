# -*- coding: utf-8 -*-
"""Sentiment_modelling_cook_distance.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Cdrp47GuY788aEZB9KY25bfK0pnIf0X1
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from google.colab import drive
drive.mount('/content/gdrive')

!pip install umap-learn
!pip install hdbscan
!pip install bertopic



# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_circles
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
from string import punctuation
import nltk
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
nltk.download('punkt')
import re
from nltk.stem.porter import *
import warnings
warnings.filterwarnings("ignore")

# %matplotlib inline

file_name_1 = "gdrive/My Drive/SBERT/complaints.csv"
data = pd.read_csv(file_name_1)
data.drop('Unnamed: 0',axis=1,inplace=True)
data

!pip install -U sentence-transformers

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

embeddings = model.encode(data['Consumer complaint narrative'].tolist())

data1 = pd.DataFrame(embeddings,columns=["col{}".format(i) for i in range(1,385)])
data1['Consumer complaint narrative'] = data['Consumer complaint narrative'].tolist()
data1['label'] = data['label'].tolist()
data1['Product'] = data['Product'].tolist()

data1.to_csv('gdrive/My Drive/SBERT/complaints_dataset_embeddings.csv')









file_name_1 = "gdrive/My Drive/SBERT/complaints_dataset_embeddings.csv"
data = pd.read_csv(file_name_1)
data.drop('Unnamed: 0',axis=1,inplace=True)
data

import umap
X,y = data.drop(columns=['Consumer complaint narrative','label','Product'],axis=1),data['label']
umap_embeddings = umap.UMAP(n_neighbors=15,
                            n_components=10,
                            metric='cosine').fit_transform(X)

import hdbscan
cluster = hdbscan.HDBSCAN(min_cluster_size=200, min_samples=4,
                          metric='euclidean',
                          cluster_selection_method='eom').fit(umap_embeddings)

unique_labels = np.unique(cluster.labels_,axis=0)
len(unique_labels)

count = pd.Series(cluster.labels_).value_counts()
count

# Prepare data
umap_data = umap.UMAP(n_neighbors=15, n_components=2, min_dist=0.0, metric='cosine').fit_transform(X)
result = pd.DataFrame(umap_data, columns=['x', 'y'])
result['labels'] = cluster.labels_

# Visualize clusters
fig, ax = plt.subplots(figsize=(20, 10))
outliers = result.loc[result.labels == -1, :]
clustered = result.loc[result.labels != -1, :]
plt.scatter(outliers.x, outliers.y, color='#BDBDBD', s=0.05)
plt.scatter(clustered.x, clustered.y, c=clustered.labels, s=0.05, cmap='hsv_r')
plt.colorbar()



from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
# Prepare data, extract embeddings, and prepare sub-models
docs = data['Consumer complaint narrative'].tolist()
cluster = hdbscan.HDBSCAN(min_cluster_size=200, min_samples=4,
                          metric='euclidean',
                          cluster_selection_method='eom',prediction_data=True)
umap_model = umap.UMAP(n_neighbors=15, n_components=10, min_dist=0.0, metric='cosine', random_state=42)
vectorizer_model = CountVectorizer(ngram_range=(1, 3),stop_words="english")
sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = np.array(X)
ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
# We reduce our embeddings to 2D as it will allows us to quickly iterate later on

# Train our topic model
topic_model = BERTopic(hdbscan_model=cluster,embedding_model=sentence_model, umap_model=umap_model,
                       vectorizer_model=vectorizer_model,calculate_probabilities=True,ctfidf_model=ctfidf_model, nr_topics='auto',verbose=True)
topics, probs = topic_model.fit_transform(docs, embeddings)

"""### c-TF-IDF representation of the topics in 2D using Umap and then visualize the two dimensions using plotly such that we can create an interactive view."""

topic_model.visualize_topics()

"""### Using the previous method, we can visualize the topics and get insight into their relationships. However, you might want a more fine-grained approach where we can visualize the documents inside the topics to see if they were assigned correctly or whether they make sense. To do so, we can use the topic_model.visualize_documents() function. This function recalculates the document embeddings and reduces them to 2-dimensional space for easier visualization purposes"""

reduced_embeddings = umap.UMAP(n_neighbors=15, n_components=2,
                          min_dist=0.0, metric='cosine').fit_transform(embeddings)

topic_model.visualize_documents(docs, reduced_embeddings=reduced_embeddings,
                                hide_document_hover=True, hide_annotations=True)

topic_model.visualize_barchart()

"""The topics that were created can be hierarchically reduced. In order to understand the potential hierarchical structure of the topics, we can use scipy.cluster.hierarchy to create clusters and visualize how they relate to one another. This might help to select an appropriate nr_topics when reducing the number of topics that you have created.

When tweaking your topic model, the number of topics that are generated has a large effect on the quality of the topic representations. Some topics could be merged and having an understanding of the effect will help you understand which topics should and which should not be merged.

That is where hierarchical topic modeling comes in. It tries to model the possible hierarchical nature of the topics you have created to understand which topics are similar to each other. Moreover, you will have more insight into sub-topics that might exist in your data.
"""

hierarchical_topics = topic_model.hierarchical_topics(docs)
topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)

tree = topic_model.get_topic_tree(hierarchical_topics)
print(tree)

topic_model.visualize_heatmap()

classes = np.array(data['Product'])
topics_per_class = topic_model.topics_per_class(docs, classes=classes)
topic_model.visualize_topics_per_class(topics_per_class)

# To visualize the probabilities of topic assignment
topic_model.visualize_distribution(probs[1])

# Calculate the topic distributions on a token-level
topic_distr, topic_token_distr = topic_model.approximate_distribution(docs, calculate_tokens=True)

# Visualize the token-level distributions
df = topic_model.visualize_approximate_distribution(docs[0], topic_token_distr[0])
df



"""# Modelling"""

labels = cluster.labels_
print(labels)

unique_labels = np.unique(cluster.labels_,axis=0)

print("no of clusters:",len(unique_labels))

# test_x,test_y = data_test.drop(columns=['tweet','sentiment'],axis=1),data_test['sentiment']
# test_x = np.array(test_x)
# test_embeddings = umap.UMAP(n_neighbors=15,
#                             n_components=5,
#                             metric='cosine').fit_transform(test_x)
# test_labels, strengths = hdbscan.approximate_predict(cluster, test_embeddings)
# test_labels

from collections import defaultdict
clusturing_models = defaultdict(list)
clustering_x = defaultdict(list)
clustering_y = defaultdict(list)
clustering_samples = defaultdict(list)
complaints = data['Consumer complaint narrative'].tolist()

for i in range(len(data)):
  l,u = labels[i],umap_embeddings[i]
  clustering_x[l].append(u)
  clustering_y[l].append(data.label.tolist()[i])
  clustering_samples[l].append(complaints[i])

cluster_info = []
for i in clustering_x.keys():
  cluster_info.append([i,len(clustering_x[i])])
cluster_info = pd.DataFrame(cluster_info,columns=['cluster_name','sample_size'])
cluster_info

data['label'].unique()

data['Product'].unique()

#original_model downsample
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.metrics import f1_score
X,y = data.drop(columns=['Consumer complaint narrative','label','Product'],axis=1),data['label']
# umap_embeddings = umap.UMAP(n_neighbors=100,
#                             n_components=20,
#                             metric='cosine').fit_transform(X)
train_x,test_x,train_y,test_y = train_test_split(umap_embeddings, y, test_size=0.2, random_state=42)
original_clf = RandomForestClassifier(n_estimators = 10, criterion = 'entropy', random_state = 42).fit(train_x,train_y)
y_train = original_clf.predict(train_x)
target_names = ['Checking or savings account', 'Credit card or prepaid card','Credit reporting, credit repair services, or other personal consumer reports','Debt collection','Mortgage','Student loan']
# print('training report for cluster {}'.format(n_cluster))
# print(classification_report(train_y, y_train, target_names=target_names))
target_names = ['Checking or savings account', 'Credit card or prepaid card','Credit reporting, credit repair services, or other personal consumer reports','Debt collection','Mortgage','Student loan']
y_pred = original_clf.predict(test_x)
print('f1 score',f1_score(test_y, original_clf.predict(test_x),average='weighted'))
print(classification_report(test_y, y_pred, target_names=target_names))

import statsmodels.api as sm
results = []

for n_cluster in clustering_x.keys():
  new_X= np.array(clustering_x[n_cluster])

  new_y = np.array(clustering_y[n_cluster]).reshape(-1,1)

  #cook distance
  #add constant to predictor variables
  x = sm.add_constant(new_X)

  #fit linear regression model
  model = sm.OLS(new_y, x).fit()
  np.set_printoptions(suppress=True)

  #create instance of influence
  influence = model.get_influence()

  #obtain Cook's distance for each observation
  cooks = influence.cooks_distance
  mean_cooks = np.mean(cooks[0])
  mean_cooks_list = [5*mean_cooks for i in range(len(cooks[0]))]
  # Draw plot
  x_axis = list(range(len(cooks[0])))
  fig, graph = plt.subplots()
  #plt.figure(figsize = (12, 8))
  graph.scatter(x_axis, cooks[0])
  graph.plot(x_axis, cooks[0], color='black')
  graph.plot(x_axis, mean_cooks_list, color="red")
  plt.xlabel('Row Number', fontsize = 12)
  plt.ylabel('Cooks Distance', fontsize = 12)
  plt.title('Influencial Points for Cluster {}'.format(n_cluster), fontsize = 22)

  cooks_samples = []
  for i, txt in enumerate(clustering_samples[n_cluster]):
    if cooks[0][i]>4*mean_cooks:
      # graph.annotate(txt, (x_axis[i], cooks[0][i]))
      cooks_samples.append([cooks[0][i],txt])

  plt.show()

  train_x,test_x,train_y,test_y = train_test_split(new_X, new_y, test_size=0.2, random_state=42)
  # print(train_x.shape)
  # print(train_y.shape)
  clf = RandomForestClassifier(n_estimators = 10, criterion = 'entropy', random_state = 42).fit(train_x,train_y)
  y_train = clf.predict(train_x)
  target_names = ['Checking or savings account', 'Credit card or prepaid card','Credit reporting, credit repair services, or other personal consumer reports','Debt collection','Mortgage','Student loan']
  # print('training report for cluster {}'.format(n_cluster))
  # print(classification_report(train_y, y_train, target_names=target_names))

  y_pred = clf.predict(test_x)
  test_score = f1_score(test_y, clf.predict(test_x),average='weighted')
  test_score_original = f1_score(test_y, original_clf.predict(test_x),average='weighted')
  results.append([test_score_original,test_score,test_score>test_score_original])
  # print('testing report for cluster {}'.format(n_cluster))
  # print(classification_report(test_y, y_pred, target_names=target_names))
  print(pd.DataFrame(cooks_samples,columns=['cook distance','discription']))
results = pd.DataFrame(results,columns=['old_model_score','clustering_model_score','improvement'])
results

"""### Keep same sample size"""

from collections import defaultdict
clusturing_models = defaultdict(list)
clustering_x = defaultdict(list)
clustering_y = defaultdict(list)
X = np.array(X)
for i in range(len(data)):
  l,u = labels[i],X[i]
  clustering_x[l].append(u)
  clustering_y[l].append(data.label.tolist()[i])

#original_model downsample
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.metrics import f1_score
X,y = data.drop(columns=['Consumer complaint narrative','label','Product'],axis=1),data['label']
# umap_embeddings = umap.UMAP(n_neighbors=100,
#                             n_components=20,
#                             metric='cosine').fit_transform(X)
train_x,test_x,train_y,test_y = train_test_split(umap_embeddings, y, test_size=0.2, random_state=42)
original_clf = RandomForestClassifier(n_estimators = 10, criterion = 'entropy', random_state = 42).fit(train_x,train_y)
y_train = original_clf.predict(train_x)
target_names = ['Checking or savings account', 'Credit card or prepaid card','Credit reporting, credit repair services, or other personal consumer reports','Debt collection','Mortgage','Student loan']
# print('training report for cluster {}'.format(n_cluster))
# print(classification_report(train_y, y_train, target_names=target_names))
target_names = ['Checking or savings account', 'Credit card or prepaid card','Credit reporting, credit repair services, or other personal consumer reports','Debt collection','Mortgage','Student loan']
y_pred = original_clf.predict(test_x)
print('f1 score',f1_score(test_y, original_clf.predict(test_x),average='weighted'))
print(classification_report(test_y, y_pred, target_names=target_names))

results = []

for n_cluster in clustering_x.keys():
  new_X= np.array(clustering_x[n_cluster])

  new_y = np.array(clustering_y[n_cluster]).reshape(-1,1)

  train_x,test_x,train_y,test_y = train_test_split(new_X, new_y, test_size=0.2, random_state=42)
  clf = LogisticRegression(random_state=0,max_iter=500).fit(train_x,train_y)
  y_train = clf.predict(train_x)
  target_names = ['negative', 'positive']
  # print('training report for cluster {}'.format(n_cluster))
  # print(classification_report(train_y, y_train, target_names=target_names))

  y_pred = clf.predict(test_x)
  test_score = roc_auc_score(test_y, clf.predict_proba(test_x)[:, 1])
  test_score_original = roc_auc_score(test_y, original_clf.predict_proba(test_x)[:, 1])
  results.append([test_score_original,test_score,test_score>test_score_original])
  # print('testing report for cluster {}'.format(n_cluster))
  # print(classification_report(test_y, y_pred, target_names=target_names))
results = pd.DataFrame(results,columns=['old_model_score','clustering_model_score','improvement'])
results

