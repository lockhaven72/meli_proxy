# Meli-Proxy challenge

## Description
A proxy is required to forward the internal requests into MercadoLibre's API, with autoscaling, metrics and monitoring features.  

## Architecture diagram
![Architecture diagram](./documentation/architecture-diagram.jpg?raw=true)

## Design considerations

- I decided to go with Python's Django web framework as it can be used to handle the amount of requests that will hit the proxy (circa 50000 requests per second). Flask web framework may also be used to achieve the proxy functionality, but due to the previous reason it was left out.

- A Postgresql dabatase is used as Django offers an ORM to facilitate the database management.  
  The database is used to count the number of requests that hit the proxy, and based on the maximum allowed requests number, the following ones get rejected (this number can be set with environment variables). This is performed through a middleware that is set in the Django's settings. However, this could be replaced by a Redis database acting as a cache, or even by an ingress controller acting as a API gateway, which can limit the amount of requests (such as Kong / Ambassador). Other alternative is managing this information in memory.

- Prometheus and Grafana are used to collect metrics and visualize the information in dashboards.

- K8s is required to achieve the autoscaling requirement, although the solution can also be tested with docker-compose, this enabled me to test the whole solution.

- In order to autoscale, metrics-server is deployed in order to collect pod's metrics (CPU and memory usage) - see references below.

- In order to access the main application and the monitoring tools, an ingress controller is deployed (Nginx) which acts as a reverse proxy - see references below.

- The application's image has been pushed into DockerHub: https://hub.docker.com/repository/docker/lockhaven72/meli-proxy

## Running the application

### Running the application with k8s

Taking into consideration that Docker and k8s are already installed in the Linux host machine, simply run:
```
kubectl apply -f deployment/.
```

Ingress files may fail to get applied, since the ingress controller takes a few minutes to get deployed. You can check ingress controller status by running:
```
kubectl get pods -n ingress-nginx   -l app.kubernetes.io/name=ingress-nginx --watch
```

Once the ingress controller it's running, reapply the failing ingress files (metrics_ingress.yml and monitoring_ingress.yml). Also, in case 'metrics-proxy' pod doesn't come up, reapply 'app_deployment.yml' file once the db is operational (see possible enhancements below).

Since routing against localhost may still fail (error 502 Bad Gateway), execute a port-forwarding against the service.
```
kubectl port-forward svc/meli-proxy-service 8080:80
```

Bear in mind that the 'migrations' file is required by the database to create the 'userSession' table, for which you'll need to log into the main application's container and execute
```
./manage.py migrate
```
In case you run into known error: ProgrammingError('relation "proxy_app_usersession" does not exist\nLINE 1: ...ed_endpoint", "proxy_app_usersession"."date" FROM "proxy_app...\n ^\n').

**Access information**  
Main application - http://localhost/<API endpoints>   - http://localhost:8080/<API endpoints> via port-forward.
Endpoints /metrics and /health are reserved and bypassed.

Grafana - http://www.meli-proxy-grafana.com
Add Prometheus as a metrics source - meli-proxy-metrics-service.default 

Prometheus - http://www.meli-proxy-metrics.com
User and password by default.  


### Running the application with docker-compose.

Commands required to run whole application:
```
docker-compose build
docker-compose run -d db
docker-compose run web python manage.py makemigrations proxy_app
docker-compose run web python manage.py migrate
docker-compose run
```

**Access information**  
Main application - http://localhost:8080/<API endpoints>  
Endpoints /metrics and /health are reserved and bypassed.

Grafana - http://localhost:3000/
Add Prometheus as a metrics source - http://prometheus:9090  

Prometheus - http://localhost:9090/
User and password by default.  

## Detected bugs and possible future enhancements

1 - No access from client's network into ingress hosts (Grafana & Prometheus)  
Although 'localhost' can be assigned to access the 'meli-proxy' application, Grafana and Prometheus' access is failing since they cannot reuse the loopback address. I encountered issues while assigning 'host' and 'path' fields in each ingress files as I couldn't access each hostname. Possibly, this was a networking issue in my local setup.

2 - Main application's healthprobe and readiness probe failing with 'connection refused' error messages.  
It was possible to create these checks in both Grafana and Prometheus deployments. I haven't figured out yet the reason behind this issue in the Django application. Also, the Postgresql deployment lacks of these checks. Perhaps, a connection into the db could be applied to check its operability. These features were commented to avoid the application from launching.

3 - Postgresql database initializes without models.  
As explained before, this can be enhanced by adding an Ansible playbook that performs the whole solution implementation. A volume is attached in order to share between them the 'migrations' and 'manage.py' script files. Also, a new Postgresql image with the tables already created could be pulled in order to avoid this manual operation.

4 - Add code testing.  
Unittests can be added to improve code reliability.  
Furthermore, Python linters could be applied to achieve PEP8 compliance, code coverage tests, code complexity evaluations and security checks through pipelines (GitHub workflows / GitLab pipelines).  

5 - Add load tests.  
Even though HPA (Horizontal Pod Autoscaling) has been applied based perform autoscaling operations, load tests were left out due lack of time.  
These can be performed using JMeter and check how the solutions scales.

6 - Add custom metrics to make 'meli-proxy' pods autoscale.  
Autoscaling can be performed by applying custom metrics, such as the amount of requests received per container in order to increase the amount of running pods.  
In the challenge, only pod's CPU is monitored.  

7 - Enhance bearer token generator script.  
Although a token generator script 'token_generator.py' has been designed to obtain the bearer token, the authorization code can only be obtained manually by now, since I couldn't find a way to obtain this code in the header fields from the redirected URL.  

8 - Enhance deployment order.  
Since each resource may depend on others, launching them in order and waiting until the ingress controller is deployed can be enhanced.  

9 - Further customization of Grafana dashboards.  
Only the total number of exceptions and handled requests metrics were taken into consideration, a lot more information could be viewed.

## Local test setup

Docker Desktop assigned resources:
- CPUs: 3
- Memory: 2 GB

## References
- Metrics-server: https://github.com/kubernetes-sigs/metrics-server
- Nginx ingress controller: https://kubernetes.github.io/ingress-nginx/deploy/