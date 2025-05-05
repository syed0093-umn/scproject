import json
import re
from urllib.parse import urlparse, urlunparse
from fuzzywuzzy import fuzz
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def load_data(fname):
    with open(fname) as f:
        return json.load(f)

def extract_original(url):
    """If this is a web.archive.org URL, pull out the original URL embedded in the path."""
    p = urlparse(url)
    if 'web.archive.org' in p.netloc:
        # path like /web/<timestamp>/<original_url>
        m = re.match(r'/web/\d+/(https?://.+)', p.path)
        if m:
            return m.group(1)
    return url

def clean(url):
    """Lowercase domain + strip query/fragments."""
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc.lower(), p.path, '', '', ''))

news = load_data('news_posts.json')
click = load_data('clickbait_posts.json')

for L in (news, click):
    for post in L:
        orig = extract_original(post['url'])
        post['clean_url'] = clean(orig)
        post['domain'] = urlparse(post['clean_url']).netloc

# exact
cb_lookup = {p['clean_url']: p for p in click}
exact = [(n, cb_lookup[n['clean_url']]) for n in news if n['clean_url'] in cb_lookup]
logging.info(f"Exact matches: {len(exact)}")

# domain
from collections import defaultdict
by_dom = defaultdict(list)
for p in click:
    by_dom[p['domain']].append(p)
domain = []
for n in news:
    if n['clean_url'] not in cb_lookup:
        for cb in by_dom.get(n['domain'], []):
            domain.append((n, cb))
logging.info(f"Domain matches: {len(domain)}")

# fuzzy on title
# fuzzy = []
# TH = 80
# for n in news:
#     if n['clean_url'] not in cb_lookup:
#         for cb in click:
#             if fuzz.token_set_ratio(n['title'], cb['title']) >= TH:
#                 fuzzy.append((n, cb))
# logging.info(f"Fuzzy matches (≥{TH}): {len(fuzzy)}")

# save
json.dump(exact, open('exact_matches.json','w'), indent=2)
json.dump(domain, open('domain_matches.json','w'), indent=2)
# json.dump(fuzzy, open('fuzzy_matches.json','w'), indent=2)

import pandas as pd

# flatten all three match-lists into one list of dicts
rows = []
for src, dst in exact + domain: # + fuzzy:
    rows.append({
        'news_id':       src['id'],
        'news_title':    src['title'],
        'news_url':      src['clean_url'],
        'click_id':      dst['id'],
        'click_title':   dst['title'],
        'click_url':     dst['clean_url'],
        'publisher_sub': dst['subreddit'],
        'click_score':   dst.get('score', 0),
        'click_comments':dst.get('num_comments', 0)
    })

# build the DataFrame
df_matches = pd.DataFrame(rows)

# optionally save
df_matches.to_csv('matched_pairs.csv', index=False)
# or as JSON:
df_matches.to_json('matched_pairs.json', orient='records', indent=2)

logging.info(f"Matched pairs DataFrame created with {len(df_matches)} rows")
