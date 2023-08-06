from psycopg2 import sql
from ..rupine_db import herokuDbAccess

#################################################################################################################
# Object ########################################################################################################
#################################################################################################################
    
class ObjEvmToken:
    token_address = None
    abi = None
    chain_id = None 
    symbol = None
    name = None
    decimals = None
    token_class = None
    totalsupply = None
    keywords = None
    telegram_link = None
    creator_address = None
    creation_timestamp = None 
    creation_block_number = None 
    creation_tx_hash = None
    created_at = 0
    modified_at = 0


    def __init__(self):
        pass

    def __eq__(self, other): 
        if not isinstance(other, ObjEvmToken):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.token_address == other.token_address and 
                self.abi == other.abi and
                self.chain_id == other.chain_id and
                self.symbol == other.symbol and
                self.name == other.name and
                self.decimals == other.decimals and
                self.token_class == other.token_class and
                self.totalsupply == other.totalsupply and
                self.keywords == other.keywords and
                self.telegram_link == other.telegram_link and
                self.creator_address == other.creator_address and
                self.creation_timestamp == other.creation_timestamp and
                self.creation_block_number == other.creation_block_number and
                self.creation_tx_hash == other.creation_tx_hash and
                self.created_at == other.created_at and
                self.modified_at == other.modified_at)

    def clone(self):
        retTok = ObjEvmToken()
        retTok.token_address = self.token_address
        retTok.abi = self.abi
        retTok.chain_id = self.chain_id
        retTok.symbol = self.symbol
        retTok.name = self.name
        retTok.decimals = self.decimals
        retTok.token_class = self.token_class
        retTok.totalsupply = self.totalsupply
        retTok.keywords = self.keywords
        retTok.telegram_link = self.telegram_link
        retTok.creator_address = self.creator_address
        retTok.creation_timestamp = self.creation_timestamp
        retTok.creation_block_number = self.creation_block_number
        retTok.creation_tx_hash = self.creation_tx_hash
        retTok.created_at = self.created_at
        retTok.modified_at = self.modified_at
        return retTok

#################################################################################################################
# DB ACCESS #####################################################################################################
#################################################################################################################

def postEvmToken(connection, schema:str, token:ObjEvmToken):

    query = sql.SQL("INSERT INTO {}.evm_token (token_address, abi, chain_id, symbol, name, decimals, token_class, totalsupply, keywords, telegram_link, creator_address, creation_timestamp, creation_block_number, creation_tx_hash) \
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)").format(sql.Identifier(schema))
    params = (
        token.token_address,
        token.abi,
        token.chain_id,
        token.symbol,
        token.name,
        token.decimals,
        token.token_class,
        token.totalsupply,
        token.keywords,
        token.telegram_link,
        token.creator_address,
        token.creation_timestamp,
        token.creation_block_number,
        token.creation_tx_hash)
    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def UpdateEvmTokenAbi(connection, schema, token_address, abi):
    
    query = sql.SQL("UPDATE {}.evm_token \
           SET abi=%s \
           WHERE token_address=%s").format(sql.Identifier(schema))
    params = (
        abi,
        token_address
    )

    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def getEvmToken(connection, schema, chain_id, token_address):
    
    # query database    
    query = sql.SQL("SELECT token_address, abi, chain_id, symbol, name, decimals, token_class, totalsupply, keywords, telegram_link, creator_address, creation_timestamp, creation_block_number, creation_tx_hash, created_at, modified_at \
        FROM {}.evm_token WHERE chain_id = %s AND token_address = %s").format(sql.Identifier(schema))
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id,token_address], connection)    
    
    # parse into objects
    rows = []
    for tok in result:
        addRow = ParseObjEvmToken(tok)
        rows.append(addRow)

    # return objects
    return rows

def getEvmTokenList(connection, schema, chain_id, gteCreatedAt):
    
    # query database    
    query = sql.SQL("SELECT token_address, abi, chain_id, symbol, name, decimals, token_class, totalsupply, keywords, telegram_link, creator_address, creation_timestamp, creation_block_number, creation_tx_hash, created_at, modified_at \
        FROM {}.evm_token WHERE chain_id = %s AND created_at >= %s").format(sql.Identifier(schema))
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id,gteCreatedAt], connection)    
    
    # parse into objects
    rows = []
    for tok in result:
        addRow = ParseObjEvmToken(tok)
        rows.append(addRow)

    # return objects
    return rows

def getEvmTokenWithoutName(connection, schema, chain_id, gteCreatedAt):
    
    # query database    
    query = sql.SQL("SELECT token_address, abi, chain_id, symbol, name, decimals, token_class, totalsupply, keywords, telegram_link, creator_address, creation_timestamp, creation_block_number, creation_tx_hash, created_at, modified_at \
        FROM {}.evm_token WHERE chain_id = %s AND name is NULL AND created_at >= %s").format(sql.Identifier(schema))
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id,gteCreatedAt], connection)    
    
    # parse into objects
    rows = []
    for tok in result:
        addRow = ParseObjEvmToken(tok)
        rows.append(addRow)

    # return objects
    return rows

#################################################################################################################
# Reply to Object ###############################################################################################
#################################################################################################################

def ParseObjEvmToken(data):
    retObj = ObjEvmToken()
    retObj.token_address = data[0]
    retObj.abi = data[1]
    retObj.chain_id = data[2] 
    retObj.symbol = data[3]
    retObj.name = data[4]
    retObj.decimals = data[5]
    retObj.token_class = data[6]
    retObj.totalsupply = data[7]
    retObj.keywords = data[8]
    retObj.telegram_link = data[9] 
    retObj.creator_address = data[10] 
    retObj.creation_timestamp = data[11] 
    retObj.creation_timestamp = data[12] 
    retObj.creation_tx_hash = data[13] 
    retObj.created_at = data[14] 
    retObj.modified_at = data[15] 
    return retObj

