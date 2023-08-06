from . import herokuDbAccess
from psycopg2 import sql

def getEvmLatestTokenLiquidityPools(connection, schema, chain_id):
    
    # query database    
    query = sql.SQL("SELECT token_address, chain_id, abi, symbol, name, decimals, token_class, totalsupply, keywords, telegram_link, creator_address, creation_timestamp, creation_block_number, creation_tx_hash, max_tx_amount_percent, max_wallet_size_percent, is_verified, is_honeypot, buy_tax, sell_tax, latest_timestamp_token_history, liquidity_pool_address, exchange_name, latest_timestamp_lp, created_at_lp, modified_at_lp, token_side, reserve_a, reserve_b, is_sellable, holder_count, volume_daily \
        FROM {}.v_evm_latest_token_liquidity_pools WHERE chain_id = %s").format(sql.Identifier(schema))

    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id], connection)  

    # parse into objects
    rows = []
    for tok in result:
        addRow = ParseObjViewEvmTokenLiqPool(tok)
        rows.append(addRow)

    # return objects
    return rows

def getEvmLatestTokenLiquidityPoolsWithoutName(connection, schema, chain_id, gteCreatedAt):

    # query database    
    query = sql.SQL("SELECT token_address, chain_id, abi, symbol, name, decimals, token_class, totalsupply, keywords, telegram_link, creator_address, creation_timestamp, creation_block_number, creation_tx_hash, max_tx_amount_percent, max_wallet_size_percent, is_verified, is_honeypot, buy_tax, sell_tax, latest_timestamp_token_history, liquidity_pool_address, exchange_name, latest_timestamp_lp, created_at_lp, modified_at_lp, token_side, reserve_a, reserve_b, is_sellable, holder_count, volume_daily \
        FROM {}.v_evm_latest_token_liquidity_pools WHERE chain_id = %s AND name = 'n/a' AND creation_timestamp >= %s").format(sql.Identifier(schema))
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id,gteCreatedAt], connection)    
    
    # parse into objects
    rows = []
    for tok in result:
        addRow = ParseObjViewEvmTokenLiqPool(tok)
        rows.append(addRow)
    
    # return objects
    return rows

def getEvmLatestTokenLiquidityPoolsNotLaunched(connection, schema, chain_id, gteCreatedAt):
    
    # query database    
    query = sql.SQL("SELECT token_address, chain_id, abi, symbol, name, decimals, token_class, totalsupply, keywords, telegram_link, creator_address, creation_timestamp, creation_block_number, creation_tx_hash, max_tx_amount_percent, max_wallet_size_percent, is_verified, is_honeypot, buy_tax, sell_tax, latest_timestamp_token_history, liquidity_pool_address, exchange_name, latest_timestamp_lp, created_at_lp, modified_at_lp, token_side, reserve_a, reserve_b, is_sellable, holder_count, volume_daily \
         FROM {}.v_evm_latest_token_liquidity_pools WHERE chain_id = %s AND liquidity_pool_address is NULL AND creation_timestamp >= %s").format(sql.Identifier(schema))
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id,gteCreatedAt], connection) 

    # parse into objects
    rows = []
    for tok in result:
        addRow = ParseObjViewEvmTokenLiqPool(tok)
        rows.append(addRow)

    # return objects
    return rows

#################################################################################################################
# Reply to Object ###############################################################################################
#################################################################################################################

def ParseObjViewEvmTokenLiqPool(data):
    retObj = ObjViewEvmTokenLiqPool()
    retObj.token_address = data[0]
    retObj.chain_id = data[1] 
    retObj.abi = data[2]
    retObj.symbol = data[3]
    retObj.name = data[4]
    retObj.decimals = data[5]
    retObj.token_class = data[6]
    retObj.totalsupply = data[7]
    retObj.keywords = data[8]
    retObj.telegram_link = data[9] 
    retObj.creator_address = data[10] 
    retObj.creation_timestamp = data[11] 
    retObj.creation_block_number = data[12] 
    retObj.creation_tx_hash = data[13] 
    retObj.max_tx_amount_percent = data[14]
    retObj.max_wallet_size_percent = data[15]
    retObj.is_verified = data[16]
    retObj.is_honeypot = data[17]
    retObj.buy_tax = data[18]
    retObj.sell_tax = data[19]
    retObj.latest_timestamp_token_history = data[20]
    retObj.liquidity_pool_address = data[21] 
    retObj.exchange_name = data[22] 
    retObj.latest_timestamp_lp = data[23] 
    retObj.created_at_lp = data[24] 
    retObj.modified_at_lp = data[25] 
    retObj.token_side = data[26] 
    retObj.reserve_a = data[27] 
    retObj.reserve_b = data[28] 
    retObj.is_sellable = data[29] 
    retObj.holder_count = data[30] 
    retObj.volume_daily = data[31] 
    return retObj

#################################################################################################################
# Object ########################################################################################################
#################################################################################################################

class ObjViewEvmTokenLiqPool:
    token_address = None
    chain_id = None 
    abi = None
    symbol = None
    name = None
    decimals = 0
    token_class = ''
    totalsupply = 0
    keywords = ''
    telegram_link = ''
    creator_address = ''
    creation_timestamp = 0 
    creation_block_number = 0 
    creation_tx_hash = '' 
    max_tx_amount_percent = 0 
    max_wallet_size_percent = 0 
    is_verified = False 
    is_honeypot = False 
    buy_tax = 0 
    sell_tax = 0  
    latest_timestamp_token_history = 0 
    liquidity_pool_address = ''
    exchange_name = ''
    latest_timestamp_lp = 0
    created_at_lp = 0
    modified_at_lp = 0
    token_side = ''
    reserve_a = 0
    reserve_b = 0
    is_sellable = ''
    holder_count = 0
    volume_daily = 0

    def __init__(self):
        pass

    def __eq__(self, other): 
        if not isinstance(other, ObjViewEvmTokenLiqPool):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.token_address == other.token_address and
                self.chain_id == other.chain_id and
                self.abi == other.abi and
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
                self.max_tx_amount_percent == other.max_tx_amount_percent and
                self.max_wallet_size_percent == other.max_wallet_size_percent and
                self.is_verified == other.is_verified and
                self.is_honeypot == other.is_honeypot and
                self.buy_tax == other.buy_tax and
                self.sell_tax == other.sell_tax and
                self.latest_timestamp_token_history == other.latest_timestamp_token_history and
                self.liquidity_pool_address == other.liquidity_pool_address and
                self.exchange_name == other.exchange_name and
                self.latest_timestamp_lp == other.latest_timestamp_lp and
                self.created_at_lp == other.created_at_lp and
                self.modified_at_lp == other.modified_at_lp and
                self.token_side == other.token_side and
                self.reserve_a == other.reserve_a and
                self.reserve_b == other.reserve_b and
                self.is_sellable == other.is_sellable and
                self.holder_count == other.holder_count and
                self.volume_daily == other.volume_daily)

    def clone(self):
        retTok = ObjViewEvmTokenLiqPool()
        retTok.token_address = self.token_address
        retTok.chain_id = self.chain_id
        retTok.abi = self.abi
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
        retTok.max_tx_amount_percent = self.max_tx_amount_percent
        retTok.max_wallet_size_percent = self.max_wallet_size_percent
        retTok.is_verified = self.is_verified
        retTok.is_honeypot = self.is_honeypot
        retTok.buy_tax = self.buy_tax
        retTok.sell_tax = self.sell_tax
        retTok.latest_timestamp_token_history = self.latest_timestamp_token_history
        retTok.liquidity_pool_address = self.liquidity_pool_address
        retTok.exchange_name = self.exchange_name
        retTok.latest_timestamp_lp = self.latest_timestamp_lp
        retTok.created_at_lp = self.created_at_lp
        retTok.modified_at_lp = self.modified_at_lp
        retTok.token_side = self.token_side
        retTok.reserve_a = self.reserve_a
        retTok.reserve_b = self.reserve_b
        retTok.is_sellable = self.is_sellable
        retTok.holder_count = self.holder_count
        retTok.volume_daily = self.volume_daily
        return retTok