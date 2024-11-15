from transformers import pipeline

def test_pipeline_loads():
    classifier = pipeline("sentiment-analysis")
    result = classifier("Crypto rocks.")
    print("Pipeline result:", result)
    assert result[0]["label"] in ["POSITIVE", "NEGATIVE"]

test_pipeline_loads()