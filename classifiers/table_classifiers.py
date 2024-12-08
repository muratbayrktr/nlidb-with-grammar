import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
from scipy.sparse import hstack  # For combining sparse matrices

# Load the dataset
df = pd.read_csv('data/bird/tablenames_dataset.csv')

# Preprocess the dataset
df['input_text'] = df['db_id'] + " " + df['question'] + " " + df['evidence']
df['primary_table'] = df['table_names'].apply(lambda x: eval(x)[0] if eval(x) else None)

# Drop rows with missing input_text or primary_table values
df_cleaned = df.dropna(subset=['input_text', 'primary_table'])

# Prepare features and target
X_text = df_cleaned['input_text']
X_db = pd.get_dummies(df_cleaned['db_id'], sparse=True)  # One-hot encode db_id
y = df_cleaned['primary_table']

# Train-test split
X_text_train, X_text_test, X_db_train, X_db_test, y_train, y_test = train_test_split(
    X_text, X_db, y, test_size=0.2, random_state=42
)

# Vectorize text input
vectorizer = TfidfVectorizer(max_features=5000)
X_text_train_vec = vectorizer.fit_transform(X_text_train)
X_text_test_vec = vectorizer.transform(X_text_test)

# Combine TF-IDF features with db_id encoding
X_train_combined = hstack([X_text_train_vec, X_db_train])
X_test_combined = hstack([X_text_test_vec, X_db_test])

# Define baseline models
models = {
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
    "NaiveBayes": MultinomialNB()
}

# Evaluate each model
baseline_results = {}
for name, model in models.items():
    # Train the model
    model.fit(X_train_combined, y_train)
    # Predict on test set
    y_pred = model.predict(X_test_combined)
    # Generate classification report
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    baseline_results[name] = {
        "Overall Accuracy": accuracy_score(y_test, y_pred),
        "Precision (Macro Avg)": report["macro avg"]["precision"],
        "Recall (Macro Avg)": report["macro avg"]["recall"],
        "F1 Score (Macro Avg)": report["macro avg"]["f1-score"]
    }

# Display results
results_df = pd.DataFrame(baseline_results).T
print(results_df)