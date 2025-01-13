import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

file_path = '../data/bird/tablenames_dataset.csv'
data = pd.read_csv(file_path)

X = data['question']
y = data['db_id']

unique_db_ids = data['db_id'].unique().tolist()
label_mapping = {db_id: idx for idx, db_id in enumerate(unique_db_ids)}
y = y.map(label_mapping)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

tfidf_vectorizer = TfidfVectorizer(
    max_features=1000, stop_words='english', ngram_range=(1, 2)
)

X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)

X_test_tfidf = tfidf_vectorizer.transform(X_test)

logistic_model = LogisticRegression(max_iter=1000, random_state=42)

logistic_model.fit(X_train_tfidf, y_train)

print("Model training complete!")

joblib.dump(logistic_model, './db_logistic_model.pkl')
joblib.dump(tfidf_vectorizer, './db_tfidf_vectorizer.pkl')
joblib.dump(label_mapping, './db_label_mapping.pkl')

print("Model, vectorizer, and label mapping saved!")

loaded_model = joblib.load('./db_logistic_model.pkl')
loaded_vectorizer = joblib.load('./db_tfidf_vectorizer.pkl')
loaded_label_mapping = joblib.load('./db_label_mapping.pkl')

reverse_label_mapping = {v: k for k, v in loaded_label_mapping.items()}

test_query = "please list the phone numbers of the schools with the top 3 sat excellence rate"
test_vectorized = loaded_vectorizer.transform([test_query])
predicted_label = loaded_model.predict(test_vectorized)[0]
predicted_table = reverse_label_mapping[predicted_label]

print(f"Predicted table for '{test_query}': {predicted_table}")
