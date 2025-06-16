from newsapi import NewsApiClient
from datetime import datetime, timedelta


def get_news():
    newsapi = NewsApiClient(api_key='e394f02413fc4ae38162a497f836fc55')

    today = datetime.today().strftime('%Y-%m-%d')
    thirty_days_ago = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')

    bitcoin_headlines = newsapi.get_everything(q='bitcoin',
                                               from_param=thirty_days_ago,
                                               to=today,
                                               language='es',
                                               sort_by='publishedAt')

    tech_news = newsapi.get_everything(q='technology',
                                       from_param=thirty_days_ago,
                                       to=today,
                                       language='es',
                                       sort_by='publishedAt')

    return bitcoin_headlines['articles'], tech_news['articles']