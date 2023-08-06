from psycopg2 import sql
from ..rupine_db import herokuDbAccess

class ObjDmhNetworkStatisticHistory:
    gecko_id = ''
    gecko_market_cap_rank = 0
    gecko_market_cap = 0
    gecko_current_price = 0
    gecko_total_volume = 0
    twitter_follower = 0
    twitter_hashtag_count = 0
    github_total_commits = 0
    github_contributer_gte_100 = 0
    github_contributer_lt_100_gte_10 = 0
    github_contributer_lt_10 = 0
    github_contributer_monthly_gte_100 = 0
    github_contributer_monthly_lt_100 = 0
    defilama_tvl = 0
    created_at = 0 
    modified_at= 0
    reddit_subscribers = 0
    reddit_average_posts_48h = 0
    reddit_average_comments_48h = 0
    reddit_accounts_active_48h = 0
    github_forks = 0
    github_stars = 0
    github_subscribers = 0
    github_pull_requests_merged = 0
    github_pull_request_contributors = 0
    github_commit_count_4_weeks = 0
    timestamp = 0

def ParseDataIntoObj(data):
    retObj = ObjDmhNetworkStatisticHistory()
    retObj.gecko_id = data[0]
    retObj.gecko_market_cap_rank = data[1]
    retObj.gecko_market_cap = data[2]
    retObj.gecko_current_price = data[3]
    retObj.gecko_total_volume = data[4]
    retObj.twitter_follower = data[5]
    retObj.twitter_hashtag_count = data[6]
    retObj.github_total_commits = data[7]
    retObj.github_contributer_gte_100 = data[8]
    retObj.github_contributer_lt_100_gte_10 = data[9]
    retObj.github_contributer_lt_10 = data[10]
    retObj.github_contributer_monthly_gte_100 = data[10]
    retObj.github_contributer_monthly_lt_100 = data[11]
    retObj.defilama_tvl = data[12]
    retObj.created_at = data[13]
    retObj.modified_at= data[14]
    retObj.reddit_subscribers = data[15]
    retObj.reddit_average_posts_48h = data[16]
    retObj.reddit_average_comments_48h = data[17]
    retObj.reddit_accounts_active_48h = data[18]
    retObj.github_forks = data[19]
    retObj.github_stars = data[20]
    retObj.github_subscribers = data[21]
    retObj.github_pull_requests_merged = data[22]
    retObj.github_pull_request_contributors = data[23]
    retObj.github_commit_count_4_weeks = data[24]
    retObj.timestamp = data[25]
    return retObj

def postHistoryEntry(connection, schema:str, entry:ObjDmhNetworkStatisticHistory):

    query = sql.SQL("INSERT INTO {}.dwh_network_statistics_history (gecko_id, gecko_market_cap_rank, gecko_market_cap, gecko_current_price, gecko_total_volume, twitter_follower, twitter_hashtag_count, github_total_commits, github_contributer_gte_100, github_contributer_lt_100_gte_10, github_contributer_lt_10, github_contributer_monthly_gte_100, github_contributer_monthly_lt_100, defilama_tvl, reddit_subscribers, reddit_average_posts_48h, reddit_average_comments_48h, reddit_accounts_active_48h, github_forks, github_stars, github_subscribers, github_pull_requests_merged, github_pull_request_contributors, github_commit_count_4_weeks, timestamp) \
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)").format(sql.Identifier(schema))
    params = (
        entry.gecko_id,
        entry.gecko_market_cap_rank,
        entry.gecko_market_cap,
        entry.gecko_current_price,
        entry.gecko_total_volume,
        entry.twitter_follower,
        entry.twitter_hashtag_count,
        entry.github_total_commits,
        entry.github_contributer_gte_100,
        entry.github_contributer_lt_100_gte_10,
        entry.github_contributer_lt_10,
        entry.github_contributer_monthly_gte_100,
        entry.github_contributer_monthly_lt_100,
        entry.defilama_tvl,
        entry.reddit_subscribers,
        entry.reddit_average_posts_48h,
        entry.reddit_average_comments_48h,
        entry.reddit_accounts_active_48h,
        entry.github_forks,
        entry.github_stars,
        entry.github_subscribers,
        entry.github_pull_requests_merged,
        entry.github_pull_request_contributors,
        entry.github_commit_count_4_weeks,
        entry.timestamp)

    result = herokuDbAccess.insertDataIntoDatabase(query, params, connection)    
    return result

def getNetworkHistory(connection, schema, gecko_id):
    
    # query database    
    query = sql.SQL("SELECT gecko_id, gecko_market_cap_rank, gecko_market_cap, gecko_current_price, gecko_total_volume, \
            twitter_follower, twitter_hashtag_count, github_total_commits, github_contributer_gte_100, \
            github_contributer_lt_100_gte_10, github_contributer_lt_10, github_contributer_monthly_gte_100, \
            github_contributer_monthly_lt_100, defilama_tvl, created_at, modified_at, reddit_subscribers, \
            reddit_average_posts_48h, reddit_average_comments_48h, reddit_accounts_active_48h, github_forks, \
            github_stars, github_subscribers, github_pull_requests_merged, github_pull_request_contributors, \
            github_commit_count_4_weeks, timestamp \
        FROM {}.dwh_network_statistics_history WHERE gecko_id=%s").format(sql.Identifier(schema))
    result = herokuDbAccess.fetchDataInDatabase(query, [gecko_id], connection)    
    
    # parse into objects
    rows = []
    for tok in result:
        addRow = ParseDataIntoObj(tok)
        rows.append(addRow)

    # return objects
    return rows

def getNetworkHistory(connection, schema, gecko_id, time_start, time_end):
    
    # query database    
    query = sql.SQL("SELECT gecko_id, gecko_market_cap_rank, gecko_market_cap, gecko_current_price, gecko_total_volume, \
            twitter_follower, twitter_hashtag_count, github_total_commits, github_contributer_gte_100, \
            github_contributer_lt_100_gte_10, github_contributer_lt_10, github_contributer_monthly_gte_100, \
            github_contributer_monthly_lt_100, defilama_tvl, created_at, modified_at, reddit_subscribers, \
            reddit_average_posts_48h, reddit_average_comments_48h, reddit_accounts_active_48h, github_forks, \
            github_stars, github_subscribers, github_pull_requests_merged, github_pull_request_contributors, \
            github_commit_count_4_weeks, timestamp \
        FROM {}.dwh_network_statistics_history \
        WHERE gecko_id=%s AND timestamp>%s AND timestamp<%s").format(sql.Identifier(schema))
    result = herokuDbAccess.fetchDataInDatabase(query, [gecko_id, time_start, time_end], connection)    
    
    # parse into objects
    rows = []
    for tok in result:
        addRow = ParseDataIntoObj(tok)
        rows.append(addRow)

    # return objects
    return rows