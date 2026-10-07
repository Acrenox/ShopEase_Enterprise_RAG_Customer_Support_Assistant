import json

from app.rag.pipeline import RAGPipeline


def main():
    with open('data/evaluation/questions.json', encoding='utf-8') as handle:
        questions = json.load(handle)

    pipeline = RAGPipeline()
    for item in questions:
        result = pipeline.ask(item['question'])
        print('=' * 60)
        print(f"Question: {item['question']}")
        print(f"Expected category: {item['category']}")
        print(f"Predicted category: {result['category']}")
        print(f"Answer: {result['answer']}")


if __name__ == '__main__':
    main()
