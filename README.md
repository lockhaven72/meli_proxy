# meli_proxy

Commands required to run whole application:
- docker-compose build
- docker-compose run -d db
- docker-compose run web python manage.py makemigrations proxy_app
- docker-compose run web python manage.py migrate
- docker-compose run

Grafana
http://localhost:3000/
Para la config - http://prometheus:9090

Prometheus
http://localhost:9090/

