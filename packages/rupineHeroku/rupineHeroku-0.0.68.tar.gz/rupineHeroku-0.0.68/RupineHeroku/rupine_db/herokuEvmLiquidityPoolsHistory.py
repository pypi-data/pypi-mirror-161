from psycopg2 import sql
from ..DataStructures import ObjEvmToken
from . import herokuDbAccess

def postEvmLiquidityPoolHistory(connection, schema:str, timestamp, chain_id, liquidity_pool_address, reserve_a, reserve_b, is_sellable, holder_count, volume_daily):

    query = sql.SQL("INSERT INTO {}.evm_token_liquidity_pools_history (timestamp, chain_id, liquidity_pool_address, reserve_a, reserve_b, is_sellable, holder_count, volume_daily) \
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)").format(sql.Identifier(schema))
    params = (
        timestamp, chain_id, liquidity_pool_address, reserve_a, reserve_b, is_sellable, holder_count, volume_daily)

    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def getEvmLiquidityPoolHistory(connection, schema, chain_id, liquidity_pool_address):
    
    query = sql.SQL("SELECT timestamp, chain_id, liquidity_pool_address, reserve_a, reserve_b, is_sellable, holder_count, volume_daily, created_at, modified_at \
                        FROM {}.evm_token_liquidity_pools_history \
                        WHERE liquidity_pool_address = %s").format(sql.Identifier(schema))
    
    result = herokuDbAccess.fetchDataInDatabase(query, [chain_id,liquidity_pool_address], connection)    
    return result