from .Connections import db_connection
from configparser import ConfigParser
import os
import logging

log_conf = logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def createDB():

    logging.info('Starting creating databases')

    config = ConfigParser()
    config.read('ETL/Connections/credencials.ini')

    HOST=config['MySql']['host']
    USER=config['MySql']['user']
    PASSWORD=config['MySql']['pass']
    PORT=3306

    try:
        dbconn = db_connection.mysqlconnection(HOST,USER,PASSWORD,PORT)
        cursor = dbconn.cursor()

        for file in os.listdir(os.path.join('ETL','SQL')):
            
            logging.info(f'Reading file {file}')

            with open(os.path.join('ETL','SQL',file),'r') as script:
                
                for command in script.read().split(';'):
                    if len(command) > 0:
                        cursor.execute(command)
                    
            dbconn.commit()
            
        cursor.close()
        dbconn.close()

    except Exception as e:
        cursor.close()
        dbconn.close()
        logging.error(f'Error on create databases: {e}')
        raise TypeError(e)
    finally:
        logging.info('Complete creation of databases')
    