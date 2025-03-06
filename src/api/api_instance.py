import requests
from typing import Union,Callable
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry
from loguru import logger

class Session:
    def __init__(self):
        self.session = requests.Session()
        self.retry = Retry(connect=1,total=5, backoff_factor=1,status_forcelist=[429, 502, 503, 504 ],allowed_methods=["GET","POST","PUT","DELETE"])
        self.adapter = HTTPAdapter(max_retries=self.retry)
        self.session.mount('http://', self.adapter)
        self.session.mount('https://', self.adapter)

    def get(self)->Union[requests.Session,None]:
        return self.session
    

class Api:
    def __init__(self,url:str,headers:dict=None,params:dict=None,json:dict=None,proxies:dict=None)->None:
        self.url=url
        self.headers=headers
        self.params=params
        self.json=json
        self.verify=True
        self.proxies=proxies
        self.session=Session().get()
        self.timeout=30

    def get(self)->Union[requests.Response,None]:
        return self.session.get(url=self.url,
                                headers=self.headers,
                                params=self.params,
                                proxies=self.proxies,
                                verify=self.verify,
                                timeout=self.timeout)

    def post(self)->Union[requests.Response,None]:
        return self.session.post(url=self.url,
                                 headers=self.headers,
                                 params=self.params,
                                 json=self.json,
                                 verify=self.verify,
                                 proxies=self.proxies,
                                 timeout=self.timeout)
    def put(self)->Union[requests.Response,None]:
        return self.session.put(url=self.url,
                                headers=self.headers,
                                params=self.params,
                                json=self.json,
                                verify=self.verify,
                                proxies=self.proxies,
                                timeout=self.timeout)
    
    def delete(self)->Union[requests.Response,None]:
        return self.session.delete(url=self.url,
                                   headers=self.headers,
                                   params=self.params,
                                   json=self.json,
                                   verify=self.verify,
                                   proxies=self.proxies,
                                   timeout=self.timeout)
    
    def request(self,method:Callable)->Union[requests.Response,None]:
        try:
            response=method()
            if 200 <= response.status_code < 300:
                try:
                    return response.json()
                except ValueError:
                    logger.warning(f"Status code {response.status_code}\n - {response.reason} - {response.url} - {response.text}") 
                    return response.text
            else:
                logger.error(f"Error:Received status code: {response.status_code}\n - {response.reason} - {response.url} - {response.text}")
                return response.content      
        except RequestException as error:
            return logger.error(f"Request failed: {error}")
            
                
        


    