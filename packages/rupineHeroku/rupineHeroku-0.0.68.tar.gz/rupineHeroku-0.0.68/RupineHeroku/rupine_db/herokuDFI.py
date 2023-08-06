from xmlrpc.client import boolean
from RupineHeroku.rupine_db import herokuDbAccess
from psycopg2 import sql
from datetime import datetime, timedelta
import pytz
from RupineHeroku.rupine_db.herokuDbDML import POST

# def postDFI(connection, schema, tableName:str, data:dict, onConflict:bool=False):
#     columns = data.keys()
#     onConflictString = ''
#     if onConflict:
#         onConflictString = 'ON CONFLICT (id) DO NOTHING'
#     queryString = "INSERT INTO {}.{} ({}) VALUES ({}) {};".format(sql.Identifier(schema),tableName,', '.join(columns),','.join(['%s']*len(columns)),onConflictString)

#     params = []
#     for key in data:
#         params.append(data[key])

#     query = sql.SQL(queryString)
#     result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
#     return result

# def postDFIDEX(connection, schema, data):
#     query = sql.SQL("INSERT INTO {}.dfi_dex (id, key, key_id, block_number, block_timestamp, pool_reserve, reserve_a, reserve_b, dex_price, last_handled_block_number) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING;").format(sql.Identifier(schema))
#     params = (
#         data['id'],
#         data['key'],
#         data['key_id'],
#         data['block_number'],
#         data['block_timestamp'],
#         data['pool_reserve'],
#         data['reserve_a'],
#         data['reserve_b'],
#         data['dex_price'],
#         data['last_handled_block_number']
#     )
#     result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
#     return result

# def postDFIFee(connection, schema, data):

#     query = sql.SQL("INSERT INTO {}.dfi_fee (key, key_id, block_number, block_timestamp, dex_fee_pct_token_a, dex_fee_pct_token_b, dex_fee_in_pct_token_a, dex_fee_in_pct_token_b, dex_fee_out_pct_token_a, dex_fee_out_pct_token_b, commission, last_handled_block_number) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);").format(sql.Identifier(schema))
#     params = (
#         data['key'],
#         data['key_id'],
#         data['block_number'],
#         data['block_timestamp'],
#         data['dex_fee_pct_token_a'],
#         data['dex_fee_pct_token_b'],
#         data['dex_fee_in_pct_token_a'],
#         data['dex_fee_in_pct_token_b'],
#         data['dex_fee_out_pct_token_a'],
#         data['dex_fee_out_pct_token_b'],
#         data['commission'],
#         data['last_handled_block_number']
#     )
#     result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
#     return result

# def postDFIOracle(connection, schema, data):

#     query = sql.SQL("INSERT INTO {}.dfi_oracle (id,key,is_live,block_number,block_median_timestamp,block_timestamp,active_price,next_price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING;").format(sql.Identifier(schema))
#     params = (
#         data['id'],
#         data['key'],
#         data['is_live'],
#         data['block_number'],
#         data['block_median_timestamp'],
#         data['block_timestamp'],
#         data['active_price'],
#         data['next_price']
#     )
#     result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
#     return result

# TODO
# getDEXPrice for timestamp: exact (nearest timestamp) OR hourly, daily, monthly-  -> group and return min, max, open, close, avg, median
# for blockNumber its trivial

def getOraclePrice(connection, schema, tokenSymbol:str,timestamp=None,blockNumber=None):
    tokenSymbolQuery = tokenSymbol.upper() + '-USD'
    if timestamp is None and blockNumber is None:
        return None
    elif timestamp is not None:
        query = sql.SQL("SELECT d.id, d.key, d.is_live, d.block_number, d.block_median_timestamp, d.block_timestamp, d.active_price, d.next_price, d.created_at, d.modified_at FROM {0}.dfi_oracle d \
            RIGHT JOIN (SELECT key,MIN(block_timestamp) AS min_block_timestamp FROM {0}.dfi_oracle \
            WHERE 1=1 AND block_timestamp >= %s AND key = %s GROUP BY key) cond \
            ON d.key = cond.key AND d.block_timestamp = cond.min_block_timestamp").format(sql.Identifier(schema))
        params = [timestamp,tokenSymbolQuery]
    else:
        query = sql.SQL("SELECT d.id, d.key, d.is_live, d.block_number, d.block_median_timestamp, d.block_timestamp, d.active_price, d.next_price, d.created_at, d.modified_at FROM {0}.dfi_oracle d \
            RIGHT JOIN (SELECT key,MIN(block_timestamp) AS min_block_timestamp FROM {0}.dfi_oracle \
            WHERE 1=1 AND block_number >= %s AND key = %s GROUP BY key) cond \
            ON d.key = cond.key AND d.block_timestamp = cond.min_block_timestamp").format(sql.Identifier(schema))
        params = [blockNumber,tokenSymbolQuery]
    
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def getlatestOracleBlock(connection, schema, tokenSymbol:str):
    tokenSymbolQuery = tokenSymbol + '-USD'
    query = sql.SQL("SELECT MAX(d.block_number) AS max_block_number FROM {0}.dfi_oracle d \
        WHERE 1=1 AND key = %s ").format(sql.Identifier(schema))
    params = [tokenSymbolQuery]
   
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def getlatestDEXBlock(connection, schema, poolSymbol:str=None):
    if poolSymbol is None:
        query = sql.SQL("SELECT d.key,d.key_id,MAX(d.last_handled_block_number) AS max_block_number, FIRST_VALUE(d.id) OVER (PARTITION d.key,d.key_id BY ORDER BY d.last_handled_block_number DESC) AS max_id FROM {0}.dfi_dex d GROUP BY d.key,d.key_id").format(sql.Identifier(schema))
        params = []
    else:
        query = sql.SQL("SELECT d.key,d.key_id,MAX(d.last_handled_block_number) AS max_block_number, FIRST_VALUE(d.id) OVER (PARTITION d.key,d.key_id BY ORDER BY d.last_handled_block_number DESC) AS max_id FROM {0}.dfi_dex d WHERE 1=1 AND key = %s GROUP BY d.key,d.key_id").format(sql.Identifier(schema))
        params = [poolSymbol]
   
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def getlatestDEXFeeBlock(connection, schema, poolSymbol:str=None):
    if poolSymbol is None:
        query = sql.SQL("SELECT d.key,d.key_id,MAX(d.last_handled_block_number) AS max_block_number, FIRST_VALUE(d.id) OVER (PARTITION d.key,d.key_id BY ORDER BY d.last_handled_block_number DESC) AS max_id FROM {0}.dfi_fee d GROUP BY d.key,d.key_id").format(sql.Identifier(schema))
        params = []
    else:
        query = sql.SQL("SELECT d.key,d.key_id,MAX(d.last_handled_block_number) AS max_block_number, FIRST_VALUE(d.id) OVER (PARTITION d.key,d.key_id BY ORDER BY d.last_handled_block_number DESC) AS max_id FROM {0}.dfi_fee d WHERE 1=1 AND key = %s GROUP BY d.key,d.key_id").format(sql.Identifier(schema))
        params = [poolSymbol]
   
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def getOracleRecordForTimestamp(connection, schema, tokenSymbol:str, timestamp:int):
    tokenSymbolQuery = tokenSymbol + '-USD'
    query = sql.SQL("SELECT * FROM {0}.dfi_oracle o RIGHT JOIN ( \
        SELECT DISTINCT key,FIRST_VALUE(block_timestamp) OVER (ORDER BY ABS(block_timestamp - %s) ASC,block_timestamp DESC) as res \
        FROM {0}.dfi_oracle WHERE 1=1 AND key = %s ) sel \
        ON sel.key = o.key AND sel.res = o.block_timestamp").format(sql.Identifier(schema))
    params = [timestamp,tokenSymbolQuery]
   
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def getTokenRisk(connection, schema, cnt_trading_periods, cnt_part_trading_periods, cnt_non_trading_periods, downside:bool=True, firstWeeks:int=6, percentRnk:float=0.25):
    query = sql.SQL("SELECT a.key, (4*b.risk_after + risk)/5 AS risk FROM {0}.dfi_oracle_risk_calculation(%s,%s,%s,%s,%s,%s,%s,%s) a \
                LEFT JOIN (SELECT key, risk as risk_after FROM {0}.dfi_oracle_risk_calculation(%s,%s,%s,%s,%s,%s,%s,%s)) b ON a.key = b.key").format(
                    sql.Identifier(schema))

    hour_of_day = datetime.now(tz=pytz.timezone('EST')).hour + datetime.now(tz=pytz.timezone('EST')).minute/60
    split_timestamp = int((datetime.now() - timedelta(weeks=firstWeeks)).timestamp())
    params = [hour_of_day,split_timestamp,False,downside,percentRnk,cnt_trading_periods,cnt_part_trading_periods,cnt_non_trading_periods,hour_of_day,split_timestamp,True,downside,percentRnk,cnt_trading_periods,cnt_part_trading_periods,cnt_non_trading_periods]
    
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def postDFIBotEvent(connection, schema, data):
    if 'risk' not in data:
        data['risk'] = None
    
    data['is_active'] = 'Y'
    data['waiting_for_loan_payback'] = 'N'
    
    return POST(connection,schema,'dfi_bot',data)
    # query = sql.SQL("INSERT INTO {}.dfi_bot (id,address,block_number,future_settlement_block,loan,loan_token,loan_oracle_price,loan_dex_price,invest_type,sentiment,risk,is_active,waiting_for_loan_payback) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);").format(sql.Identifier(schema))
    # params = (
    #     data['id'],
    #     data['address'],
    #     data['block_number'],
    #     data['future_settlement_block'],
    #     data['loan'],
    #     data['loan_token'],
    #     data['loan_oracle_price'],
    #     data['loan_dex_price'],
    #     data['invest_type'],
    #     data['sentiment'],
    #     data['risk'],
    #     'Y',
    #     'N'
    # )
    # result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    # return result

def putDFIBotEventInvest(connection, schema, data):
    query = sql.SQL("UPDATE {}.dfi_bot SET invest = %s, invest_token = %s, invest_oracle_price =%s, invest_dex_price = %s WHERE id = %s AND address = %s").format(sql.Identifier(schema))
    params = (
        data['invest'],
        data['invest_token'],
        data['invest_oracle_price'],
        data['invest_dex_price'],
        data['id'],
        data['address'],
    )
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def putDFIBotEventAddLiquidity(connection, schema, data):
    query = sql.SQL("UPDATE {}.dfi_bot SET lp_pool_tokens = %s WHERE id = %s AND address = %s").format(sql.Identifier(schema))
    params = (
        data['lp_pool_tokens'],
        data['id'],
        data['address'],
    )
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def putDFIBotEventROI(connection, schema, data):
    query = sql.SQL("UPDATE {}.dfi_bot SET expected_roi = %s WHERE id = %s AND address = %s").format(sql.Identifier(schema))
    params = (
        data['expected_roi'],
        data['id'],
        data['address'],
    )
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def changeDFIBotEventStatus(connection, schema, data):
    status = None
    params = []
    if 'is_active' in data:
        status = ' is_active = %s'
        params.append(data['is_active'])
    if 'waiting_for_loan_payback' in data:
        if status is None:
            status = ' waiting_for_loan_payback = %s'
        else:
            status = status + ', waiting_for_loan_payback = %s'
        params.append(data['waiting_for_loan_payback'])

    if status is not None:
        query = sql.SQL("UPDATE {}.dfi_bot SET %s WHERE id = %%s AND address = %%s" % status).format(sql.Identifier(schema))
        params.append(data['id'])
        params.append(data['address'])
        params = tuple(params)

        result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
        return result
    else:
        return None

def getDFIBotEvents(connection, schema, address:str,is_active:bool=True,waiting_for_loan_payback:bool=None):
    if is_active == True:
        condition = " AND d.is_active = 'Y'"
    elif is_active == False:
        condition = " AND d.is_active = 'N'"
    else:
        condition = ''

    if waiting_for_loan_payback == True:
        condition = condition + " AND d.waiting_for_loan_payback = 'Y'"
    elif waiting_for_loan_payback == False:
        condition = condition + " AND d.waiting_for_loan_payback = 'N'"
    else:
        condition = condition

    query = sql.SQL("SELECT * FROM {0}.dfi_bot d \
        WHERE 1=1 AND d.address = %%s %s" % (condition)).format(sql.Identifier(schema))
    params = [address]
    
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def getDFIBotControl(connection, schema, address:str=None):
    if address is None:
        query = sql.SQL("SELECT address,is_active FROM {0}.dfi_bot_control").format(sql.Identifier(schema))
        params = []
    else:
        query = sql.SQL("SELECT address,is_active FROM {0}.dfi_bot_control WHERE 1=1 AND address = %s").format(sql.Identifier(schema))
        params = [address]
    
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
    return result

def putDFIBotControl(connection, schema, address:str,flag:str):
    if len(getDFIBotControl(connection,schema,address)) == 0:
        query = sql.SQL("INSERT INTO {}.dfi_bot_control (address,is_active) VALUES (%s,%s);").format(sql.Identifier(schema))
        params = (
        address,
        flag
    )
    else:
        query = sql.SQL("UPDATE {}.dfi_bot_control SET is_active = %s WHERE address = %s").format(sql.Identifier(schema))
        params = (
            flag,
            address
        )
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def getLatestBlockOfBotEvent(connection, schema, address:str):
    query = sql.SQL("SELECT MAX(block_number) AS max_block_number from {0}.dfi_bot WHERE 1=1 AND address = %s").format(sql.Identifier(schema))
    params = [address]
   
    result = herokuDbAccess.fetchDataInDatabase(query, params, connection)    
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
#     print(POST(connection,'dbdev','my_table',{'id':1,'col':'pubs'},True))
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
