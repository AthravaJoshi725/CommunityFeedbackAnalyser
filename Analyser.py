import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import warnings
import nltk
import pickle

# Load data
twitter_data = pd.read_csv('stemmed_twitterdata.csv')

# Handle missing values by dropping rows with NaN in 'stemmed_content'
twitter_data = twitter_data.dropna(subset=['stemmed_content'])

# Separating data and the labels
X = twitter_data['stemmed_content'].values
y = twitter_data['target'].values

# Splitting the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=2)

# Converting textual data into numerical data
vectorizer = TfidfVectorizer()
X_train = vectorizer.fit_transform(X_train)
X_test = vectorizer.transform(X_test)

# Training the model - logistic regression
logistic_model = LogisticRegression(max_iter=1000)
logistic_model.fit(X_train, y_train)

# Model Evaluation
# Accuracy score on testing data
X_test_pred = logistic_model.predict(X_test)
test_data_accuracy = accuracy_score(X_test_pred, y_test)
print('Accuracy score:', test_data_accuracy)  # Model accuracy on test data

# Save the trained model and vectorizer
model_filename = 'trained_model.sav'
pickle.dump(logistic_model, open(model_filename, 'wb'))

vectorizer_filename = 'tfidf_vectorizer.sav'
pickle.dump(vectorizer, open(vectorizer_filename, 'wb'))
