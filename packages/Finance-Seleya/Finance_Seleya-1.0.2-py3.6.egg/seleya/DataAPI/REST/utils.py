import dateutil.parser as dt_parser
import pandas as pd
import json

def convert_date(date, format='%Y-%m-%d'):
    try:
        if isinstance(date, (str, unicode)):
            date = dt_parser.parse(date)
    except Exception as e:
        raise Exception('date:{}格式不能识别。'%date)

    return date.strftime(format)

def to_pandas(result):
    res = json.loads(result)
    columns = res['columns']
    items = res['items']
    data = pd.DataFrame.from_dict(items, orient='columns')
    if data.empty:
        return pd.DataFrame(columns=columns)
    data.columns=columns
    return data