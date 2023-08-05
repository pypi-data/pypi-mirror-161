from FairResources.Sources import Sources
import os
import re
import pandas
import feedparser
import random
from FList import LIST

TRENDING_URL = 'http://www.google.com/trends/hottrends/atom/feed?pn=p1'

def google_trends():
    """Returns a list of hit terms via google trends
    """
    try:
        listing = feedparser.parse(TRENDING_URL)['entries']
        trends = [item['title'] for item in listing]
        return trends
    except Exception as e:
        print('ERR hot terms failed!', str(e))
        return None

CWD = os.path.dirname(__file__)
PUNKT_ONE = "/tokenizers/punkt/english.pickle"
PUNKT_TWO = "/tokenizers/punkt/PY3/english.pickle"
NLTK_PUNKT_ONE = f"{str(CWD)}{PUNKT_ONE}"
NLTK_PUNKT_TWO = f"{str(CWD)}{PUNKT_TWO}"

STOCKTICKERS = os.path.join(os.path.dirname(__file__), 'stocks.csv')
SOURCES = Sources
REDDIT_COMMUNITIES = Sources.reddit_communities
TWITTER_USERS = Sources.twitter_users

ALL = [a for a in os.scandir(os.path.dirname(__file__))]

def get_all_files():
    raw_items = os.scandir(os.path.dirname(__file__))
    files = []
    for item in raw_items:
        item: os.DirEntry = item
        if item.is_dir() or item.is_file():
            files.append(item.name)
    return files

def get_source(sourceTerm):
    sources = get_all_files()
    for src in sources:
        srcSmall = str(src).lower()
        sourceTermSmall = str(sourceTerm).lower()
        if srcSmall.__contains__(sourceTermSmall):
            mainSource = os.path.join(os.path.dirname(__file__), src)
            if src.endswith("_sources.txt"):
                source_list = get_resource(mainSource)
            else:
                source_list = get_resource_not_url(mainSource)
            return source_list

def get_resource(resource):
    """Uses generator to return next useragent in saved file
    """
    with open(resource, 'r') as f:
        urls = ['http://' + u.strip() for u in f.readlines()]
        return LIST.scramble(urls)

def get_resource_not_url(resource):
    """Uses generator to return next useragent in saved file
    """
    with open(resource, 'r') as f:
        urls = [u.strip() for u in f.readlines()]
        return LIST.scramble(urls)

def get_random(items):
    selection = random.randint(0, len(items) - 1)
    return items[selection]

def get_google_sources():
    return get_source("google")

def get_popular_sources():
    return get_source("popular")

def get_rss_sources():
    return get_source("rss")

def get_metaverse_sources():
    return get_source("metaverse")

def get_search_terms():
    return get_source("google")

def get_random_user_agent():
    all = get_source("useragents")
    return LIST.get_random(all, False)

def get_stopwords():
    return get_source("stopwords")

def get_random_metaverse_source():
    m_urls = get_metaverse_sources()
    m_count = len(m_urls)
    ran_dom = random.randint(0, m_count)
    url = m_urls[ran_dom]
    return url

# Load Stock Ticker List from CSV File
def read_stock_csv():
    df = pandas.read_csv(STOCKTICKERS)
    return df

def read_stock_csv_to_dict():
    df = pandas.read_csv(STOCKTICKERS)
    df_dict = df.to_dict()
    return df_dict

def build_list_of_companies(dic):
    companies_list = []
    # keys = Symbol, Name...
    tickers = dic['Symbol']
    names = dic['Name']
    ipo_years = dic['IPO Year']
    sectors = dic['Sector']
    industries = dic['Industry']
    countries = dic['Country']
    market_caps = dic['Market Cap']

    # 'IPO Year' 'Sector' 'Industry' 'Country' 'Market Cap'
    index_count = 0
    while index_count <= len(tickers):
        ticker = LIST.get(index_count, tickers)
        name = LIST.get(index_count, names)
        ipo_year = LIST.get(index_count, ipo_years)
        sector = LIST.get(index_count, sectors)
        industry = LIST.get(index_count, industries)
        country = LIST.get(index_count, countries)
        market_cap = LIST.get(index_count, market_caps)

        single_company = {
            "ticker": ticker,
            "name": name,
            "ipo_year": ipo_year,
            "sector": sector,
            "industry": industry,
            "country": country,
            "market_cap": market_cap,
        }
        companies_list.append(single_company)
        index_count += 1
    return companies_list


# Parse Stock Ticker List from CSV File
def get_stock_tickers():
    df = read_stock_csv()
    list_of_tickers = []
    for ticker in df['Symbol']:
        list_of_tickers.append(ticker)
    return list_of_tickers

def get_company_names_from_csv():
    df = read_stock_csv()
    list_of_companies = []
    for name in df['Name']:
        name = to_tokens(name)
        one = name[0] if len(name) > 0 else ""
        two = name[1] if len(name) > 1 else ""
        new_name = one + " " + two
        list_of_companies.append((one, new_name))
    return list(set(list_of_companies))

def to_tokens(text):
    """ ALTERNATIVE: Split a string into array of words. """
    try:
        text = re.sub(r'[^\w ]', '', text)  # strip special chars
        return [x.strip('.').lower() for x in text.split()]
    except TypeError:
        return None
