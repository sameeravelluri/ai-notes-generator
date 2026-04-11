from transformers import pipeline
summarizer = pipeline("text-generation", model="facebook/bart-large-cnn")
def summarize_text(text):
    if not text or text.strip() == "":
        return "No text found"
    text = text[:800]
    result = summarizer(
        text,
        max_new_tokens=120,
        do_sample=False
    )
    return result[0]["generated_text"]