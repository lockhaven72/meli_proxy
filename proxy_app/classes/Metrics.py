from prometheus_client import Counter, Gauge, Histogram, Summary

class Metrics:
    concurrent_requests_gauge = Gauge('concurrent_requests', 'Concurrent requests using the proxy.')
    exceptions_counter = Counter('exceptions_counter', 'Number of exceptions hitted during a request.')