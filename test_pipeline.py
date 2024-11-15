from transformers import pipeline

def test_pipeline_loads():
    classifier = pipeline("sentiment-analysis")
    result = classifier("Crypto rocks.")
    assert result[0]["label"] in ["POSITIVE", "NEGATIVE"]
