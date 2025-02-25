
from sqlalchemy import create_engine,text
from src.config import Settings
import pandas as pd
class Database:
    def __init__(self):
        self.settings=Settings()
        self.engine=self.get_engine()
        self.connection= self.engine.connect()
        
        
    def get_engine(self):
        engine=create_engine(f"postgresql://{self.settings.DB_USERNAME}:{self.settings.DB_PASSWORD}@{self.settings.DB_HOST}:{self.settings.DB_PORT}/{self.settings.DB_NAME}")
        return engine
    def alter_table_schema(self,table_name:str,df:pd.DataFrame):
        
        exist_columns=self.get_columns_db(table_name)
        new_columns=[column for column in df.columns if column not in exist_columns]
        
        # self.connection.begin()
        for column in new_columns:
            query=text(f"""ALTER TABLE {table_name} ADD COLUMN "{column}" TEXT""")
            self.connection.execute(query)
            print(f"Column {column} added to table {table_name}")
        self.connection.commit()
        # self.connection.close()

    def get_columns_db(self,table_name:str):
        
        query=text(f"""SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'""")
        result=self.connection.execute(query)
        columns=[column[0] for column in result]
        return columns

    def save_into_db(self,resource:str,content:dict,page:int):
        table_name=resource.split("/")[-2]
        df=pd.json_normalize(content,sep="_")
        
        
        
        if page==1:
            df.to_sql(table_name,self.engine,if_exists="replace",index=False)
        else:
            self.alter_table_schema(table_name,df)
            df.to_sql(table_name,self.engine,if_exists="append",index=False)