import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer
import sqlite3 as sql
from sklearn.metrics import accuracy_score, precision_score, recall_score

src = '..\\jobs.db'

conn, cur = None, None
try:
    conn = sql.connect(src)
except sql.Error as e:
    print(e)
    sys.exit(1)

df = pd.read_sql_query("select distinct(title, yes_no) from jobs", conn)
keys = ['title', 'yes_no']

X_train, X_test, y_train, y_test = train_test_split(df['title'], df['yes_no'], random_state=1)
cv = CountVectorizer(strip_accents='ascii', token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b', lowercase=True, stop_words='english')

X_train_cv = cv.fit_transform(X_train)
X_test_cv  = cv.transform(X_test)
word_freq_df = pd.DataFrame(X_train_cv.toarray(), columns=cv.get_feature_names())

#top_words_df = pd.DataFrame(word_freq_df[''].sum()).sortValues(0, ascending=False)
naive_bayes = MultinomialNB()
naive_bayes.fit(X_train_cv, y_train)
predictions = naive_bayes.predict(X_test_cv)

print('Accuracy score:', accuracy_score(y_test, predictions))
print('Precision score:', precision_score(y_test, predictions))
print('Recall score:', recall_score(y_test, predictions))
