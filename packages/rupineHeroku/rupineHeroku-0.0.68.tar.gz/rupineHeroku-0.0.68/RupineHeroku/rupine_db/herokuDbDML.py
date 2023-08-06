from RupineHeroku.rupine_db import herokuDbAccess
from psycopg2 import sql
import json

def POST(connection, schema, tableName:str, data:dict, onConflict:bool=False):
    columns = data.keys()
    onConflictString = ''
    if onConflict:
        onConflictString = 'ON CONFLICT (id) DO NOTHING'
    queryString = "INSERT INTO {{}}.{} ({}) VALUES ({}) {};".format(tableName,', '.join(columns),','.join(['%s']*len(columns)),onConflictString)

    params = []
    for key in data:
        if type(data[key]) == dict:
            params.append(json.dumps(data[key]))
        else:
            params.append(data[key])

    query = sql.SQL(queryString).format(sql.Identifier(schema))
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

# import os
# from dotenv import load_dotenv
# import herokuDbAccess as db
# load_dotenv()

# def convertToType(data,type):
#     if data is None:
#         return None
#     else:
#         return type(data)
# def assignDBResponse(res:tuple):
#     return {
#         'id':res[0],
#         'address':res[1],
#         'block_number':res[2],
#         'future_settlement_block':res[3],
#         'loan':convertToType(res[4],float),
#         'loan_token':res[5],
#         'loan_oracle_price':convertToType(res[6],float),
#         'loan_dex_price':convertToType(res[7],float),
#         'invest_type':res[8],
#         'sentiment':res[9],
#         'risk':convertToType(res[10],float),
#         'invest':convertToType(res[11],float),
#         'invest_token':res[12],
#         'invest_oracle_price':convertToType(res[13],float),
#         'invest_dex_price':convertToType(res[14],float),
#         'lp_pool_tokens':convertToType(res[15],float),
#     }

# if __name__ == '__main__':
#     connection = db.connect(
#         os.environ.get("HEROKU_DB_USER"),
#         os.environ.get("HEROKU_DB_PW"),
#         os.environ.get("HEROKU_DB_HOST"),
#         os.environ.get("HEROKU_DB_PORT"),
#         os.environ.get("HEROKU_DB_DATABASE")
#     )
#     data = {
#         'id': '1',
#         'txid':'sdg',
#         'public_address':'sdjkl',
#         'transaction_type':'skjlfd',
#         'block_number':1,
#         'block_timestamp':2,
#         'tx_order':1,
#         'vin':1,
#         'vout':0,
#         'data':{'some':'data','and':1}
#     }

    #    id varchar(255) not null
    # ,  varchar(255) not null
    # ,  varchar(255) not null 
    # ,  varchar(255) not null
    # ,  integer not null
    # ,  integer not null
    # ,  integer not null
    # ,  integer
    # ,  integer
    # ,  json
    print(POST(connection,'dbdev','dfi_transaction',data,True))
#     data = {
#         'id':"bla",
#         'key':"TSLA-DUSD",
#         'block_number':123,
#         'block_timestamp':456,
#         'pool_reserve':390.1,
#         'reserve_a':4.5,
#         'reserve_b':6.5,
#         'dex_price':0.12
#     }
#     postDFIDEX(connection,'dbdev',data)
#     print(getlatestDEXBlock(connection,'dbdev','TSLA-DUSD'))
#     res = getOracleRecordForTimestamp(connection,'prod','PYPL',1652344775)
#     print(res)
#     print(len(res))
#     res = putDFIBotcontrol(connection,'stage','dfi1','N')
#     print(res)
    # data = {
    #     'id':'1003718-tf1q6qj52ykxlf6halmx0g32gaumuuptactwgrqh23-MSFT',
    #     'address':'tf1q6qj52ykxlf6halmx0g32gaumuuptactwgrqh23',
    #     'expected_roi':13,
    #     'is_active':'N',
    #     'waiting_for_loan_payback':'Y'
    # } 
#     putDFIBotEventROI(connection,os.environ.get("ENVIRONMENT"),data)
#     changeDFIBotEventStatus(connection,os.environ.get("ENVIRONMENT"),data)
    # print(getTokenRisk(connection,'prod',1,1,1,True))
    # data = {
    #     'id':'dfi1-123-TSLA',
    #     'address':'dfi1',
    #     'is_active':'Y' 
    # }
    # changeDFIBotEventStatus(connection,'stage',data)

    # trades = getDFIBotEvents(connection,'stage','dfi1',True)
    # for t in trades:
    #     print(assignDBResponse(t))
