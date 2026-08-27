from Retrieval.intent_classifier_llm import IntentClassifier


classifier = IntentClassifier()


questions = [
    "What is Webenza?",
    "What SEO services do you provide?",
    "I am interested in SEO for my company",
    "Can someone from Webenza contact me?",
    "My email is test@example.com",
    "Tell me about your ZoloStays case study",
]


for question in questions:

    result = classifier.classify(question)

    print("\nQuestion:")
    print(question)

    print("Intent:")
    print(result)