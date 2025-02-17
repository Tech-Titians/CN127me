import tkinter as tk
# DATASET IMPORTING

#!pip install chardet
#!pip install scikit-learn

import chardet

with open('CN127\spam.csv', 'rb') as f:
    encoding = chardet.detect(f.read())['encoding']

import pandas as pd

raw_data_set = pd.read_csv('CN127\spam.csv', encoding=encoding)

data_set = raw_data_set.where((pd.notnull(raw_data_set)),'')


import nltk
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


nltk.download('punkt')
nltk.download('stopwords')


def process_text(text):

    tokens = word_tokenize(text)

    tokens = [word.lower() for word in tokens]

    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]

    stop_words = set(stopwords.words('english'))
    words = [word for word in stripped if word not in stop_words]
    return words


data_set['processed_text'] = data_set['v2'].apply(process_text)


data_set.head()

data_set.loc[data_set['v1'] == 'spam', 'v1',] = 0
data_set.loc[data_set['v1'] == 'ham', 'v1',] = 1

X = data_set['v2']
Y = data_set['v1']

from sklearn.model_selection import train_test_split, GridSearchCV

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=3)

# Feature Extraction

from sklearn.feature_extraction.text import TfidfVectorizer


feature_extraction = TfidfVectorizer(min_df=1)

X_train_features = feature_extraction.fit_transform(X_train)
X_test_features = feature_extraction.transform(X_test)

Y_train = Y_train.astype('int')
Y_test = Y_test.astype('int')

print(X_train)

print(X_train_features)


from sklearn.feature_extraction.text import CountVectorizer
count_vectorizer = CountVectorizer()

X_train_word_freq = count_vectorizer.fit_transform(X_train)
X_test_word_freq = count_vectorizer.transform(X_test)

spam_keywords = ['free', 'buy now', 'limited time offer', 'click','warning','alert','suspicious']

def presence_of_keywords(text):
    return [1 if keyword in text else 0 for keyword in spam_keywords]

additional_features_train = X_train.apply(presence_of_keywords).apply(pd.Series)
additional_features_test = X_test.apply(presence_of_keywords).apply(pd.Series)

def email_length(text):
    return len(text)

X_train_email_length = X_train.apply(email_length)
X_test_email_length = X_test.apply(email_length)

from scipy.sparse import hstack
X_train_combined = hstack([X_train_features, X_train_word_freq, additional_features_train, X_train_email_length.values.reshape(-1, 1)])
X_test_combined = hstack([X_test_features, X_test_word_freq, additional_features_test, X_test_email_length.values.reshape(-1, 1)])



# MODEL TRAINING


from sklearn.linear_model import LogisticRegression
model = LogisticRegression()

model.fit(X_train_features, Y_train)

lr_predict=model.predict(X_test_features)

from sklearn.metrics import f1_score

lr_f1 = f1_score(Y_test, lr_predict)
print(lr_f1)

# SVM

from sklearn.svm import SVC

svm_model = SVC()

svm_model.fit(X_train_features, Y_train)


from sklearn.metrics import f1_score
svm_predictions = svm_model.predict(X_test_features)

#F1 SCORE
svm_f1 = f1_score(Y_test, svm_predictions)
print(svm_f1)


def predict_and_display():
    new_email = text_input.get("1.0", tk.END).strip()  # Get input

    # Apply your existing preprocessing and feature extraction steps:
    processed_email = process_text(new_email)  # ... (adapt as needed)

    input_data_features = feature_extraction.transform([new_email])

    # Model prediction
    prediction = svm_model.predict(input_data_features)[0]  # Use best model

    # Update result label
    if prediction == 1:
        result_label.config(text="Ham mail")
    else:
        result_label.config(text="Spam mail")

# updating ===========

window = tk.Tk()
window.title("Spam Email Detector")

# Input area
tk.Label(window, text="Enter Email Text:",).grid(row=0, column=0)
text_input = tk.Text(window)
text_input.grid(row=0, column=1)

# Button
tk.Button(window, text="Predict", command=predict_and_display).grid(row=1, column=1)

# Result label
result_label = tk.Label(window, text="")
result_label.grid(row=2, column=0, columnspan=2)

window.mainloop()