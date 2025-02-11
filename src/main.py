from config import Settings
import requests
import json


settings=Settings()


app_key=settings.APP_KEY
app_secret=settings.APP_SECRET
base_url=settings.BASE_URL

endpoints=[{
    'resource':'geral/clientes/',    
    'action':'ListarClientes',
    'params':{
        "pagina": 1,
        "registros_por_pagina": 100,
        "apenas_importado_api": "N"}
   
}]

HEADERS = {
    'Content-Type': 'application/json',
}



def request (resource:str,body:dict)->dict:
    response=requests.post(
        url=f'{base_url}{resource}',
        headers=HEADERS,
        json=body        
        )
    
    if response.status_code==200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}")


def get_total_pages(resource:str,action:str,params:dict)->int:
    body={"call":action,
      "app_key": app_key,
      "app_secret": app_secret,
      "param":[params]
        
    }
    response=request(resource,body)
    total_of_pages=response.get("total_de_paginas",0)
    return total_of_pages

def save_file(resource:str,content:dict):
    file_name=resource.split("/")[-2]
    content=json.dumps(content)
    with open(f"{file_name}.json","w") as file:
        file.write(content)


for endpoint in endpoints:
    resource=endpoint.get("resource")
    action=endpoint.get("action")
    params=endpoint.get("params")


    total_of_pages=get_total_pages(resource,action,params)
    print(total_of_pages)
    records_fetched=0
    for page in range(1,total_of_pages+1):
        params["pagina"]=page
        body={
            "call":action,
            "app_key": app_key,
            "app_secret": app_secret,
            "param":[params]}

        print(resource)
        response=request(resource,body)
        print(response)
        records_fetched+=response.get("registros",0)
        print(f"Page {page} fetched {records_fetched} records")
        save_file(resource,response)





