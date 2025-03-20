from locust import HttpUser, task, between

class FastAPIUser(HttpUser):
    wait_time = between(1, 5)  # Wait time between tasks

    @task
    def slow_endpoint(self):
        self.client.get("/slow")

    @task
    def error_endpoint(self):
        self.client.get("/error")


    @task
    def compute_endpoint(self):
        self.client.get("/compute?n=10")

    @task
    def server_request_endpoint(self):
        self.client.get("/server_request")
