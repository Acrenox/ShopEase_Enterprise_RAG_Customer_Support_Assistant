install:
	python -m pip install -r requirements.txt

index:
	python -m ingestion.build_index

api:
	uvicorn app.main:app --reload

test:
	pytest -q

evaluate:
	python scripts/evaluate.py

docker-build:
	docker build -t shopease-rag .

docker-run:
	docker run -p 8000:8000 --env-file .env shopease-rag
