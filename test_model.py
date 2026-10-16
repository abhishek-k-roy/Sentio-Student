
from sentio.emotion_model import load_classifier

classifier = load_classifier()

samples = [
    "I have two exams tomorrow and I cannot manage my study time.",
    "I need to finish my assignment before the deadline.",
    "I enjoyed spending time with my friends today.",
]

for text in samples:
    print(f"\nText: {text}")

    predictions = classifier(text)

    for item in sorted(
        predictions,
        key=lambda x: x["score"],
        reverse=True,
    ):
        print(f"  {item['label']}: {item['score']:.4f}")
