from src.config import Settings
import requests
import json
from src.db.database import Database
import pandas as pd
from src.endpoints.endpoints import Endpoints
from src.utils.tools import get_total_pages,get_body_params_pagination,HEADERS
from src.api.api_instance import Api

settings=Settings()
endpoints=Endpoints().get_endpoints()
# endpoints=endpoints.get_endpoint(action="ListarContasCorrentes")




for endpoint in endpoints:
    
    resource=endpoint.get("resource")
    action=endpoint.get("action")
    chave=endpoint.get("chave")
    params=endpoint.get("params")
    data_source=endpoint.get("data_source")
    page_label=endpoint.get("page_label")
    total_of_pages_label=endpoint.get("total_of_pages_label")
    records_label=endpoint.get("records_label")


    total_of_pages=get_total_pages(resource,action,params,page_label,total_of_pages_label,records_label)
    
    records_fetched=0
    # for page in range(1,total_of_pages+1):
    for page in range(1,4):
        params[page_label]=page
     
       
        body=get_body_params_pagination(action,params,page,page_label)     
        api=Api(url=f"{settings.BASE_URL}{resource}",headers=HEADERS,json=body,params=params)
        
        response=api.request(api.post)        
        records_fetched+=response.get(records_label,0)
        contents=response.get(data_source,[])
        
        # black_list=["tags","recomendacoes","homepage","fax_ddd","bloquear_exclusao","produtor_rural","enderecoEntrega"]
        black_list=["tags"]
        # # lista=[key for key in content.keys() if key not in black_list]
        lista = [{key: value for key, value in content.items() if key not in black_list} for content in contents]
               
        print(f"Page {page} fetched {records_fetched} records from {resource}")
        db=Database()
        db.save_into_db(resource,lista,page)
        





