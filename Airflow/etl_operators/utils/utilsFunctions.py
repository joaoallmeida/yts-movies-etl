import logging
import pandas as pd
import json

class utils:

    def __init__(self) -> None:
        pass
        
    def truncateTable(self,table,dbconn):

        logging.info(f'Truncate table {table}')
        
        try:
            
            cursor = dbconn.cursor()
            query_cmd = f'TRUNCATE TABLE {table}' 
            cursor.execute(query_cmd)
            
            dbconn.commit()
            dbconn.close()
            
        except Exception as e:
            logging.error(f'Error to truncate table: {e}')
            dbconn.close()
            raise TypeError(e)
        finally:
            logging.info('Complete Truncate table')

    def getTorrentValue(self,df):
        torrent_list = list()

        try:
            data = df[~df['torrents'].isna()]

            for a,b in data.iterrows():
                for t in json.loads(b.torrents):
                    t['id'] = b.id
                    t['url_torrent'] = f"magnet:?xt=urn:btih:{t['hash']}&dn={b.title}-{t['quality']}-{t['type']}&tr=http://track.one:1234/announce&tr=udp://open.demonii.com:1337/announce&tr=udp://tracker.openbittorrent.com:80&tr=udp://tracker.coppersurfer.tk:6969&tr=udp://glotorrents.pw:6969/announce&tr=udp://tracker.opentrackr.org:1337/announce&tr=udp://torrent.gresille.org:80/announce&tr=udp://p4p.arenabg.com:1337&tr=udp://tracker.leechers-paradise.org:6969"
                    torrent_list.append(t)

            df_aux = pd.DataFrame(torrent_list)
            df_merge = df.merge(df_aux, on='id',how='inner',suffixes=(None, '_tt'))
            df_merge = df_merge.drop(['torrents'],axis=1)
        
        except Exception as e:
            logging.error(e)
            raise TypeError(e)
        
        return df_merge

    def convertToJson(self,df,cols):

        try:
            for col in cols:
                df[col] = df[col].apply(lambda x: json.dumps(x))

        except Exception as e:
            logging.error(e)
            raise TypeError(e)

        return df

    def InsertToMySQL(self,df,dbconn,table):
        
        try:
            
            sql01 = ",".join(f'{c}' for c in df.columns)
            sql02 = ",".join(f'{s} = VALUES({s})' for s in df.columns) 
            sql03 = ",".join(f'%s' for s in df.columns) 
            sql04 = f"INSERT INTO {table} ({sql01}) VALUES({sql03})"
            sql05 = f"ON DUPLICATE KEY UPDATE {sql02}"
            sql06 = f"{sql04} {sql05};"
            
            data = list(df.fillna(method="ffill").itertuples(index=False,name=None))
            cursor = dbconn.cursor()
            cursor.executemany(sql06,data)

            dbconn.commit()
            
            lines_number = cursor.rowcount
            
        except Exception as e:
            logging.error(e)
            raise TypeError(e)
        
        return lines_number
        
    def getChanges(self,df,table,dbconn):

        try:
            
            df_target = pd.read_sql_table(table, dbconn)
            changes = df[~df.apply(tuple,axis=1).isin(df_target.apply(tuple,axis=1))]
            insert = changes[~changes['id'].isin(df_target['id'])]
            # modified = changes[changes['id'].isin(df_target['id'])]
            
        except Exception as e:
            logging.error(e)
            raise TypeError(e)
        
        return insert

    def splitGenreColumn(self,df):
        
        df['genres'] = df['genres'].apply(lambda x: json.loads(x))
        data = df[df['genres'].notna()][['id','genres']].to_dict()
        
        df_aux = pd.DataFrame(data['genres'].values(),index=data['id'].values()).add_prefix('genre_').reset_index()
        df = df.merge(df_aux, left_on='id', right_on='index',how='left')
        df = df.drop(['genres','index'],axis=1)

        return df

    def upperString(self,df,columns):

        for col in columns:
            df[col] = df[col].str.upper()
            
        return df