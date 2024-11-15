from transformers import pipeline

classifier = pipeline("sentiment-analysis")
result = classifier("Crypto rocks!")
print(result)