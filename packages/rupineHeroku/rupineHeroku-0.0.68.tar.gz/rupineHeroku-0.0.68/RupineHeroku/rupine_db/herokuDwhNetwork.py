from psycopg2 import sql
from . import herokuDbAccess

class ObjDmhNetwork:
    gecko_id = ''
    gecko_name = ''
    gecko_symbol = ''
    cmc_id = ''
    chain_id = ''
    twitter_name = ''
    twitter_id = ''
    twitter_hashtag = ''
    github_org = ''
    telegram_link = ''
    created_at = 0 
    modified_at= 0

def ParseDataIntoObj(data):
    retObj = ObjDmhNetwork()
    retObj.gecko_id = data[0]
    retObj.gecko_name = data[1]
    retObj.gecko_symbol = data[2]
    retObj.cmc_id = data[3]
    retObj.chain_id = data[4]
    retObj.twitter_name = data[5]
    retObj.twitter_id = data[6]
    retObj.twitter_hashtag = data[7]
    retObj.github_org = data[8]
    retObj.telegram_link = data[9]
    retObj.created_at = data[10]
    retObj.modified_at= data[11]
    return retObj

def getNetworkList(connection, schema):
    
    # query database    
    query = sql.SQL("SELECT gecko_id, gecko_name, gecko_symbol, cmc_id, chain_id, twitter_name, twitter_id, twitter_hashtag, github_org, telegram_link, created_at, modified_at \
        FROM {}.dwh_network").format(sql.Identifier(schema))
    result = herokuDbAccess.fetchDataInDatabase(query, [], connection)    
    
    # parse into objects
    rows = []
    for tok in result:
        addRow = ParseDataIntoObj(tok)
        rows.append(addRow)

    # return objects
    return rows