from pymongo import InsertOne
from pymongo.errors import BulkWriteError
from seleya.DataAPI.db.mongodb import MongoDBManager
from seleya.config.default_config import MONGO_DB
from seleya import *
import pdb


class FetchEngine(object):
    def __init__(self):
        self._MONGO_DB = MONGO_DB
        self._mongo_client = MongoDBManager(self._MONGO_DB)
        self._sly_engine = DBFetchEngine.create_engine('sly')
        
    def max_cid(self, uid):
        query = {'uid': uid}
        cid = self._mongo_client[self._MONGO_DB['db']].esg_combine.distinct('cid')
        cid = max(cid) if len(cid) > 0 else 10000
        return cid + 1
    
        
    def write_combine(self, combine, name='user_combine'):
        requests = [InsertOne(d) for d in combine.to_dict(orient='records')]
        self._mongo_client[self._MONGO_DB['db']][name].bulk_write(
                        requests, bypass_document_validation=True)
        
    def remove_combine(self, uid, name, create_date, create_name):
        query = {'uid':uid, 'name':{'$in':name},
                'create_date': {'$in':create_date},
                'create_name':{'$in':create_name}}
        self._mongo_client[self._MONGO_DB['db']]['esg_portfolio'].remove(
            query)
        
    def fetch_combine(self, uid, columns):
        query = {'uid': uid}
        results = self._mongo_client[self._MONGO_DB['db']].user_combine.find(
            query, dict(zip(columns, [1 for i in range(0,len(columns))])))
        results = pd.DataFrame(results)
        results = results.drop(['_id'],axis=1) if not results.empty else pd.DataFrame(
            columns=columns)
        return results
    
    def fetch_metrics(self, table_name, codes, columns):
        query = {'code':{'$in':codes}}
        results = self._mongo_client[self._MONGO_DB['db']][table_name].find(
            query, dict(zip(columns, [1 for i in range(0,len(columns))])))
        results = pd.DataFrame(results)
        results = results.drop(['_id'],axis=1) if not results.empty else pd.DataFrame(
            columns=columns)
        return results
    
    def fetch_indicator_detail(self, key, indicator):
        return ESGMetricsDetailFactory(self._sly_engine).result(
            key=key, codes=indicator, columns=['category','column_name'])
    
    def fetch_esg_combine(self, uid, columns, name=None, date=None):
        query = {'uid': uid} if (name is None or date is None) else {'uid':uid, 'name':name, 'date':date}
        results = self._mongo_client[self._MONGO_DB['db']].user_esg_portfolio.find(
            query, dict(zip(columns, [1 for i in range(0,len(columns))])))
        results = pd.DataFrame(results)
        results = results.drop(['_id'],axis=1) if not results.empty else pd.DataFrame(
            columns=columns)
        return results
    
        
        
        
fetch_engine = FetchEngine()

def custom_combine(uid, data):
    if 'RIC Code' not in data.columns or 'Portfolio Weight' not in data.columns:
        return False
    current_id = fetch_engine.max_cid(uid=uid)
    data = data[['RIC Code', 'ISIN', 'Portfolio Weight']].rename(
                columns={'RIC Code':'code','ISIN':'isin','Portfolio Weight':'weight'})
    data['cid'] = current_id
    data['uid'] = uid
    fetch_engine.write_combine(data)
    return True
    
    
def esg_portfolio(uid, indicator, key, name=None, date=None):
    def _weighted(data):
        weighted = data[['weight']] / data[['weight']].sum()
        weighted['code'] = data['code']
        return weighted
    
    def to_combine(data):
        cdata = pd.DataFrame(data['rows'])
        cdata['create_date'] = data['date']
        cdata['create_name'] = data['name']
        return cdata[['code','weight','create_date','create_name']]
    ##提取指标信息
    indicator_info = fetch_engine.fetch_indicator_detail(key=key, 
                                                  indicator=indicator)
    if indicator_info.empty:
        return
    
    ##提取组合信息
    #combine_info = fetch_engine.fetch_combine(
    #    uid=uid,columns=['code', 'cid', 'isin', 'weight'])
    
    combine_info = fetch_engine.fetch_esg_combine(
        uid=uid, name=name, date=date, columns=['date','name','rows'])
    
    combine_info = combine_info.apply(lambda x: to_combine(x), axis=1)
    combine_info = pd.concat(combine_info.values,axis=0)
    codes = combine_info.code.unique().tolist()
    ##按类别提取
    grouped = indicator_info.groupby('category')
    res = []
    for name,group in grouped:
        columns = ['date','code'] + group['column_name'].unique().tolist()
        print('esg_metrics_' + name.lower())
        data = fetch_engine.fetch_metrics('esg_metrics_' + name.lower(), 
                                          codes, columns)
        columns = [col for col in data.columns.tolist() if col not in ['code','date']]
        for col in columns:
            for cid, combine in combine_info.groupby(['create_date','create_name']):
                df = combine.merge(data[['date','code',col]],on=['code'])
                df = df.dropna(subset=[col])
                if df.empty:
                    continue
                new_weight = df.set_index('date').groupby(level=['date']).apply(lambda x: _weighted(x))
                new_df = new_weight.reset_index().merge(df[['date','code','create_date','create_name', col]], on=['date','code'])
                result = new_df.set_index(['date']).groupby(level=['date']).apply(lambda x: (x[col] * x['weight']).sum())
                result.name = 'portfolio'
                result = result.reset_index()
                result['name'] = col
                result['uid'] = uid
                result['create_date'] = cid[0]
                result['create_name'] = cid[1]
                res.append(result)
    portfolio_data = pd.concat(res,axis=0)
    fetch_engine.remove_combine(uid=uid, name=indicator, 
                                create_date=portfolio_data['create_date'].tolist(), 
                                create_name=portfolio_data['create_name'].tolist())
    fetch_engine.write_combine(combine=portfolio_data, name='esg_portfolio')
    return portfolio_data