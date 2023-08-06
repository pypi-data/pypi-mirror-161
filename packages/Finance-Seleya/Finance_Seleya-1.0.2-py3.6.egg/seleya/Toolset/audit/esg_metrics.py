from seleya.DataAPI.db.mongodb import MongoDBManager
from seleya.config.default_config import MONGO_DB
from seleya import *
import pdb,itertools


class FetchEngine(object):
    def __init__(self):
        self._MONGO_DB = MONGO_DB
        self._mongo_client = MongoDBManager(self._MONGO_DB)
    def fetch_audit(self, codes, begin_date, end_date, indicators, tag):
        query = {'code': {'$in':codes}, 
                 'indicator':{'$in':indicators},
                 'tag':{'$in':tag},
                 'date':{'$gte':begin_date.strftime('%Y-%m-%d'),
                         '$lte':end_date.strftime('%Y-%m-%d')}
                }
        results = self._mongo_client[self._MONGO_DB['db']].esg_audit.find(
            query)
        
        results = pd.DataFrame(results)
        results = results.drop(['_id'],axis=1) if not results.empty else pd.DataFrame()
        return results
    
fetch_engine = FetchEngine()

def check_audit(codes, indicators, begin_date, end_date):
    tag = ['Title']
    results = fetch_engine.fetch_audit(codes=codes, indicators=indicators,
                            begin_date=begin_date, end_date=end_date, 
                                       tag=tag)
    return results.drop(['tag'],axis=1) if not results.empty else None

def esg_audit(codes, indicators, begin_date, end_date, tags=None,
              is_value=False):
    
    tag = ['Title','URL','Page','Note','FiscalDate'] if tags is None else tags
    tag = tag + ['value'] if is_value else tag
    results = fetch_engine.fetch_audit(codes=codes, indicators=indicators,
                            begin_date=begin_date, end_date=end_date, 
                                       tag=tag)
    return results if results is not None else None