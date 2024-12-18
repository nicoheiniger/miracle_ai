import joblib


def load_classification_models():
    """
    Load trained SVM model and vectorizer.
    """
    svm = joblib.load("models/svm_model.joblib")
    vectorizer = joblib.load("models/vectorizer.joblib")
    return svm, vectorizer


def predict_benefit(svm, vectorizer, cleaned_texts):
    """
    Use SVM and vectorizer to predict benefit.
    """
    features = vectorizer.transform(cleaned_texts)
    predictions = svm.predict(features)
    return predictions
