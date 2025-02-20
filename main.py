from src.config import Settings
import requests
import json
from sqlalchemy import create_engine,text
import pandas as pd
import logging
from requests.adapters import HTTPAdapter,Retry
from src.endpoints.endpoints import Endpoints

settings=Settings()
endpoints=Endpoints().get_endpoints()


app_key=settings.APP_KEY
app_secret=settings.APP_SECRET
base_url=settings.BASE_URL



HEADERS = {
    'Content-Type': 'application/json',
}



def request (resource:str,body:dict)->dict:
    requests_session=custom_session()
    response=requests_session.post(
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
    total_of_pages=response.get("total_de_paginas",response.get("nTotPaginas"))
    return total_of_pages

def save_file(resource:str,content:dict):
    file_name=resource.split("/")[-2]
    content=json.dumps(content)
    with open(f"{file_name}.json","w") as file:
        file.write(content)
def get_engine():
    engine=create_engine(f"postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    return engine
def alter_table_schema(table_name:str,df:pd.DataFrame):
    engine=get_engine()
    exist_columns=get_columns_db(table_name)
    new_columns=[column for column in df.columns if column not in exist_columns]
    connection=engine.connect()
    connection.begin()
    for column in new_columns:
        query=text(f"""ALTER TABLE {table_name} ADD COLUMN "{column}" TEXT""")
        connection.execute(query)
        print(f"Column {column} added to table {table_name}")
    connection.commit()
    connection.close()

def get_columns_db(table_name:str):
    engine=get_engine()
    connection=engine.connect()
    query=text(f"""SELECT column_name
    FROM information_schema.columns
    WHERE table_name = '{table_name}'""")
    result=connection.execute(query)
    columns=[column[0] for column in result]
    return columns

def save_into_db(resource:str,content:dict,page:int):
    table_name=resource.split("/")[-2]
    df=pd.json_normalize(content,sep="_")
    engine=get_engine()
    
    
    if page==1:
        df.to_sql(table_name,engine,if_exists="replace",index=False)
    else:
        alter_table_schema(table_name,df)
        df.to_sql(table_name,engine,if_exists="append",index=False)
    
def custom_session():    
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5,status_forcelist=[ 502, 503, 504 ])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

for endpoint in endpoints:
    resource=endpoint.get("resource")
    action=endpoint.get("action")
    chave=endpoint.get("chave")
    params=endpoint.get("params")


    total_of_pages=get_total_pages(resource,action,params)
    print(total_of_pages)
    records_fetched=0
    # for page in range(1,total_of_pages+1):
    for page in range(1,4):
        if params.get("pagina") is not None:
            params["pagina"]=page
        if params.get("nPagina") is not None:
            params["nPagina"]=page
        body={
            "call":action,
            "app_key": app_key,
            "app_secret": app_secret,
            "param":[params]}

        
        response=request(resource,body)
        print(response)
        records_fetched+=response.get("registros",response.get("nRegistros"))

        contents=response.get(chave,[])
        print(contents)
        # black_list=["tags","recomendacoes","homepage","fax_ddd","bloquear_exclusao","produtor_rural","enderecoEntrega"]
        black_list=["tags"]
        # # lista=[key for key in content.keys() if key not in black_list]
        lista = [{key: value for key, value in content.items() if key not in black_list} for content in contents]
        # lista=[content for content in contents if content.keys() not in black_list]
        # for content in contents:
        #     for key in black_list:
        #         content.pop(key,None)
        
        print(f"Page {page} fetched {records_fetched} records from {resource}")
        save_into_db(resource,lista,page)





