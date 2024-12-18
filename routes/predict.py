from flask import Blueprint, request, jsonify
from utils.preprocessing import preprocess_content, remove_urls
from utils.classification import load_classification_models, predict_benefit
from utils.extraction import extract_urls, extract_dates, generate_title, generate_summary, extract_tickers
from utils.postprocessing import clean_urls, filter_dates

predict_bp = Blueprint("predict", __name__)

# Load SVM model and vectorizer
svm, vectorizer = load_classification_models()

def process_request(input_text, input_timestamp):
    """
    Main processing function to handle input text and timestamp.
    """
    # Preprocessing
    cleaned_text_url = preprocess_content(input_text)
    cleaned_text = remove_urls(cleaned_text_url)

    # Classification
    benefit = predict_benefit(svm, vectorizer, [cleaned_text])[0]

    # If not beneficial, return only benefit prediction
    if benefit == 0:
        return {
            "benefit": int(benefit),  # Ensure it's a Python int
            "filtered_dates": [],
            "title": "",
            "urls": [],
            "ticker": "",
            "description": "",
        }

    # Extraction
    urls = extract_urls(cleaned_text_url)
    dates = extract_dates(cleaned_text, input_timestamp)
    title = generate_title(cleaned_text)
    description = generate_summary(cleaned_text)
    ticker = extract_tickers(cleaned_text)

    # Post-processing: Clean URLs and filter dates
    cleaned_urls = clean_urls(urls)
    filtered_dates = filter_dates(dates, input_timestamp)

    # Final response
    return {
        "benefit": int(benefit),  # Ensure it's a Python int
        "filtered_dates": [str(date) for date in filtered_dates],  # Convert to string
        "title": str(title),
        "urls": cleaned_urls,
        "ticker": str(ticker),
        "description": str(description),
    }

@predict_bp.route("/predict", methods=["POST"])
def predict():
    """
    Flask route to handle POST requests for predictions.
    """
    try:
        # Get JSON payload
        data = request.get_json()
        input_text = data.get("text", "")
        input_timestamp = data.get("timestamp", "")

        # Validate inputs
        if not input_text or not input_timestamp:
            return jsonify({"error": "Both 'text' and 'timestamp' are required"}), 400

        # Process the request
        result = process_request(input_text, input_timestamp)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
