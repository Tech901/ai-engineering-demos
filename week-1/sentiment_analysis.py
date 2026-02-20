"""
Week 1 - Azure Sentiment Analysis
Connects to Azure AI Language service and performs sentiment analysis
on user-provided text input.
"""

import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


def authenticate_client():
    """Create and return an authenticated TextAnalyticsClient."""
    endpoint = os.environ.get("AZURE_LANGUAGE_ENDPOINT")
    key = os.environ.get("AZURE_LANGUAGE_KEY")

    if not endpoint or not key:
        raise ValueError(
            "Missing Azure credentials. Please set the following environment variables:\n"
            "  AZURE_LANGUAGE_ENDPOINT - Your Azure AI Language service endpoint\n"
            "  AZURE_LANGUAGE_KEY      - Your Azure AI Language service key"
        )

    credential = AzureKeyCredential(key)
    client = TextAnalyticsClient(endpoint=endpoint, credential=credential)
    return client


def analyze_sentiment(client, text):
    """Analyze the sentiment of the given text and return the result."""
    documents = [text]
    response = client.analyze_sentiment(documents=documents)
    result = response[0]

    if result.is_error:
        raise RuntimeError(
            f"Sentiment analysis error: [{result.error.code}] {result.error.message}"
        )

    return result


def display_result(result):
    """Print a formatted sentiment analysis result."""
    print("\n--- Sentiment Analysis Result ---")
    print(f"Overall Sentiment : {result.sentiment.capitalize()}")
    print(f"Confidence Scores :")
    print(f"  Positive : {result.confidence_scores.positive:.2%}")
    print(f"  Neutral  : {result.confidence_scores.neutral:.2%}")
    print(f"  Negative : {result.confidence_scores.negative:.2%}")

    if result.sentences:
        print("\nSentence-level breakdown:")
        for i, sentence in enumerate(result.sentences, start=1):
            print(
                f"  [{i}] \"{sentence.text}\""
                f" → {sentence.sentiment.capitalize()}"
                f" (pos={sentence.confidence_scores.positive:.2%},"
                f" neu={sentence.confidence_scores.neutral:.2%},"
                f" neg={sentence.confidence_scores.negative:.2%})"
            )
    print("---------------------------------\n")


def main():
    print("=== Azure Sentiment Analysis ===")
    print("Type 'quit' or 'exit' to stop.\n")

    try:
        client = authenticate_client()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return

    while True:
        user_input = input("Enter text to analyze: ").strip()

        if not user_input:
            print("Please enter some text.\n")
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        try:
            result = analyze_sentiment(client, user_input)
            display_result(result)
        except RuntimeError as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
