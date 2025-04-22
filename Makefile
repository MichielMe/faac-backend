build:
	docker build -t faac-backend .

run-dev:
	docker run -v ./app/assets:/app/app/assets -p 8000:8000 faac-backend