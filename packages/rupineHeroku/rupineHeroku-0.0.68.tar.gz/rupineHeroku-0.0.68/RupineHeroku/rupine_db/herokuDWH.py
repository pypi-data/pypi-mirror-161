from RupineHeroku.rupine_db import herokuDbAccess
from psycopg2 import sql
from datetime import datetime
import pytz

def postAccountAddress(connection, schema, data):
    query = sql.SQL("INSERT INTO {}.dwh_address_account (chain_id,chain,account,public_address,context) VALUES (%s,%s,%s,%s,%s)").format(sql.Identifier(schema))
    params = (
        data['chain_id'],
        data['chain'],
        data['account'],
        data['public_address'],
        data['context'])
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def getAccountAddress(connection, schema, account=None, public_address=None, chain=None, chain_id=None):
    conditions = ""
    params = []
    if chain is None and chain_id is None:
        return []
    elif chain is not None:
        conditions = conditions + " AND t.chain = %s"
        params.append(chain)
    elif chain_id is not None:
        conditions = conditions + " AND t.chain_id = %s"
        params.append(chain_id)
    if account is not None:
        query = sql.SQL("SELECT account,public_address,context from {0}.dwh_address_account t WHERE 1=1 %s  AND account = %%s " % (conditions)).format(sql.Identifier(schema))
        params.append(account)
    elif public_address is not None:
        query = sql.SQL("SELECT account,public_address,context from {0}.dwh_address_account t WHERE 1=1 %s AND public_address = %%s" % (conditions)).format(sql.Identifier(schema))
        params.append(public_address)
    else:
        return []

    result = herokuDbAccess.fetchDataInDatabase(query, [*params], connection)  
    return result


# import os
# from dotenv import load_dotenv
# import herokuDbAccess as db
# from datetime import datetime
# load_dotenv()

# if __name__ == '__main__':
#     connection = db.connect(
#         os.environ.get("HEROKU_DB_USER"),
#         os.environ.get("HEROKU_DB_PW"),
#         os.environ.get("HEROKU_DB_HOST"),
#         os.environ.get("HEROKU_DB_PORT"),
#         os.environ.get("HEROKU_DB_DATABASE")
#     )
#     data = {
#         'chain_id':None,
#         'chain':'DeFiChain',
#         'account':'Benni',
#         'public_address':'df1qgssyvcqld7cwxzvnajyt3xlqae67muxrqh06ct',
#         'context':'private'
        
#     }
#     postAccountAddress(connection,'stage',data)
#     print(getAccountAddress(connection,'stage','Benni',chain='DeFiChain'))
    # data = {
    #     'chain_id':1,
    #     'chain':'ETH',
    #     'account':'MYACC',
    #     'address':'dfi1',
    #     'token':'BLUE1',
    #     'buy_timestamp':127897934,
    #     'buy_price':12.4,
    #     'buy_transaction_hashes':'sjdlfjskljdfklsj,jhghjhghj',
    #     'sell_timestamp':893434,
    #     'sell_price':34.35,
    #     'sell_transaction_hashes':'shdsdfjkhsdjkf2,sdjfklj',
    #     'amount':12.2
    # }
    #res = getTaxTransactionRewards(connection,'stage',['dfi1','df1qgssyvcqld7cwxzvnajyt3xlqae67muxrqh06ct'],'DeFiChain',None,'DFI',0)
    #res = getTaxTokens(connection,'stage',['dfi1','df1qgssyvcqld7cwxzvnajyt3xlqae67muxrqh06ct'],'DeFiChain',None)
    # res = getLatestWarehouseDate(connection,'stage','BLUE12','MYACC','Defi',None)
    # print(res)