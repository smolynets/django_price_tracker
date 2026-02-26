# Test Task: Category and Product Management System

## Description:
Price tracking system built with Django/DRF. Implement a Celery Beat periodic task (daily) to fetch price data from external APIs and persist it in a PostgreSQL database.

####  Database Structure:
- Shop & Product: Core entities where each product is linked to a specific shop and identified by a unique external_id to prevent duplicates during API synchronization.
- ProductPriceRecord: A historical log that tracks price changes over time, constrained by a unique_together rule to ensure only one price point is stored per product per day.
- CurrencyRate: Stores daily exchange rates with high precision (decimal_places=4) to facilitate multi-currency price analysis.
- ProductPriceAlert: A notification layer that maps user emails to specific products, triggering alerts when the threshold_price is met or exceeded.

#### Celery and Redis
The project utilizes Celery, Redis and Celery Beat to automate the data lifecycle:
- Scheduled Scraping: Triggers a daily periodic task to fetch the latest product data and currency rates from external APIs.
- Asynchronous Processing: Offloads heavy database operations (like bulk_create for ProductPriceRecord) and email notifications (for ProductPriceAlert) to background workers, ensuring the API remains fast and responsive.
But for test here are two manual endpoiunts to populate DB.

#### Python Web Framework:
Django/DRF


### Setup:

##### Create .env file:
	cp sample_env .env

#### Docker setup:

##### Run in project root directory:
	docker-compose up -d

##### Rebuild:
	docker-compose up --build -d

##### For db migrate:
	docker exec -it web poetry run python manage.py migrate

##### For admin user creation:
	docker exec -it web poetry run python manage.py createsuperuser


#### Local setup:

##### Update .env for local setup (see sample_env commented lines):
	cp sample_env .env

##### Install dependencies:
	poetry init
    poetry install

##### For db migrate:
	poetry run python manage.py migrate

##### For admin user creation:
	poetry run python manage.py createsuperuser

##### Celery worker (in new terminal):
	poetry run celery -A core worker -l info

##### Beat worker (in new terminal):
    poetry run celery -A core beat -l info

##### For admin user runserver:
	poetry run python manage.py runserver

#### General (docker and local):

##### Fow access to admin part:
	http://127.0.0.1:8000/admin

##### Fow access to swagger documentation:
	http://127.0.0.1:8000/api/docs/
