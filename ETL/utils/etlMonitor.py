
from ..connections.dbConnection import stringConnections
from .utilsFunctions import utils
from configparser import ConfigParser
from datetime import datetime
import pandas as pd

class control:

    def __init__(self) -> None:
        
        config = ConfigParser()
        config.read('./credencials.ini')

        self.host=config['MySQL']['host']
        self.user=config['MySQL']['user']
        self.password=config['MySQL']['password']
        self.port=int(config['MySQL']['port'])
        self.database = 'monitoring'
        
        self.connString = stringConnections()
        self.utils = utils()

        self.dbconn = self.connString.engineSqlAlchemy(self.host,self.user,self.password,self.port,self.database)
        self.mysqlconn = self.connString.mysqlConnection(self.host,self.user,self.password,self.port,self.database)

    def InsertLog(self,process_id, table, status, row_count = 0, error=None):
        
        try:
            log_table = 'etl_logging'
            record = {  
                    "process_id": process_id,
                    "table_name": table,
                    "start_date": datetime.now(),
                    "complete_date": None,
                    "row_count": row_count,
                    "status": status,
                    "error_message": error
                }

            if status == 'InProgress':

                df_log_insert = pd.DataFrame(record, index=[0])
                df_log_insert.to_sql(log_table,self.dbconn,if_exists='append',index=False)
            
            elif status == 'Complete':

                df_log = pd.read_sql(log_table,self.dbconn)
                df_log = df_log[df_log['table_name'] == table].sort_values(by=['log_id'], ascending=False).head(1)
                df_log['complete_date'] = datetime.now()
                df_log['row_count'] = row_count
                df_log['status'] = status

                self.utils.InsertToMySQL(df_log,self.mysqlconn,log_table)

            else:

                df_log = pd.read_sql(log_table,self.dbconn)
                df_log = df_log[df_log['table_name'] == table].sort_values(by=['log_id'], ascending=False).head(1)
                df_log['complete_date'] = datetime.now()
                df_log['row_count'] = row_count
                df_log['status'] = status
                df_log['error_message'] = error

                self.utils.InsertToMySQL(df_log,self.mysqlconn,log_table)
            
        except Exception as e:
            raise e


