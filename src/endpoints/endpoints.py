import json

def read_json(path:str)->dict:
    with open(path,'r') as file:
        return json.load(file)

class Endpoints:
    def __init__(self):
        self.path='./src/endpoints/data/data.json'
        self.endpoints = read_json(self.path)

    def get_endpoints(self):
        return self.endpoints

    def get_endpoint(self, action:str) -> None:
        for endpoint in self.endpoints:
            if endpoint['action'] == action:
                return endpoint
        raise Exception(f"Endpoint {action} not found")

    def get_action(self, resource):
        endpoint = self.get_endpoint(resource)
        if endpoint:
            return endpoint['action']
        return None

    def get_params(self, resource):
        endpoint = self.get_endpoint(resource)
        if endpoint:
            return endpoint['params']
        return None

    def get_param(self, resource, param):
        params = self.get_params(resource)
        if params:
            return params[param]
        return None

