import joblib
import importlib.resources as pkg_resources

class ClassificationEngine:
    def __init__(self):
        self.models = {
            "db": {
                "model_path": pkg_resources.files("app.models").joinpath("db_logistic_model.pkl"),
                "vectorizer_path": pkg_resources.files("app.models").joinpath("db_tfidf_vectorizer.pkl"),
                "label_mapping_path": pkg_resources.files("app.models").joinpath("db_label_mapping.pkl"),
            },
            # "table": {
            #     "model_path": pkg_resources.files("app.models").joinpath("table_logistic_model.pkl"),
            #     "vectorizer_path": pkg_resources.files("app.models").joinpath("table_tfidf_vectorizer.pkl"),
            #     "label_mapping_path": pkg_resources.files("app.models").joinpath("table_label_mapping.pkl"),
            # },
            # "column": {
            #     "model_path": pkg_resources.files("app.models").joinpath("column_logistic_model.pkl"),
            #     "vectorizer_path": pkg_resources.files("app.models").joinpath("column_tfidf_vectorizer.pkl"),
            #     "label_mapping_path": pkg_resources.files("app.models").joinpath("column_label_mapping.pkl"),
            # },
        }       
         
        self.engines = {}
        for classification_type, paths in self.models.items():
            model = joblib.load(paths["model_path"])
            vectorizer = joblib.load(paths["vectorizer_path"])
            label_mapping = joblib.load(paths["label_mapping_path"])
            reverse_label_mapping = {v: k for k, v in label_mapping.items()}
            
            self.engines[classification_type] = {
                "model": model,
                "vectorizer": vectorizer,
                "reverse_label_mapping": reverse_label_mapping,
            }

    def classify(self, nlq: str, classification_type: str):
        """
        Predicts the label based on the classification type.
        :param nlq: The natural language query string.
        :param classification_type: Type of classification ('db', 'table', or 'column').
        :return: Predicted label.
        """
        if classification_type not in self.engines:
            raise ValueError(f"Unsupported classification type: {classification_type}")

        engine = self.engines[classification_type]
        query_vectorized = engine["vectorizer"].transform([nlq]) 
        prediction_idx = engine["model"].predict(query_vectorized)[0]
        predicted_label = engine["reverse_label_mapping"][prediction_idx] 
        return predicted_label
