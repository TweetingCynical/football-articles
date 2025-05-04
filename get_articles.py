# %%
# Imports
import httpx
from selectolax.parser import HTMLParser
import json
import time
import random
import os
import subprocess
from datetime import datetime
from urllib.parse import urlparse, urljoin

# %%
# Configurations
with open('assets/config/headers.json') as f:
    headers = json.load(f)

with open('assets/config/excluded_phrases.json') as f:
    excluded_phrases = json.load(f)

with open('assets/config/tags_to_check.json') as f:
    tags_to_check = json.load(f)

with open('assets/config/site_configs.json') as f:
    site_configs = json.load(f)

# %%
# Function for scraping articles
def scrape_site(config):
    print(f"Scraping: {config['name']}")
    try:
        resp = httpx.get(config["url"], headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch: {e}")
        return []

    html = HTMLParser(resp.text)
    articles = html.css(config["article_selector"])
    results = []

    for article in articles:
        if len(results) >= 20:
            break
        
        try:
            link = article.css_first(config["link_selector"]).attributes.get("href", "")
            full_link = urljoin(config.get("prepend_domain") or '', link)

            headline_node = article.css_first(config["headline_selector"])
            headline = headline_node.text().strip() if headline_node else None

            tags = [t if t != "Manchester United" else "Man Utd" for t in tags_to_check if headline and t.lower() in headline.lower()]

            image_node = article.css_first(config["image_selector"])
            image = image_node.attributes.get("src") if image_node else None

            # Get full article page
            article_resp = httpx.get(full_link, headers=headers, timeout=10)
            item_html = HTMLParser(article_resp.text)
            content_nodes = item_html.css(config["content_selector"])
            body = [n.text().strip() for n in content_nodes if n.text() and not any(p in n.text() for p in excluded_phrases)]

            date = None
            if config.get("timestamp"):
                time_node = item_html.css_first(config["date_selector"])
                if time_node and "data-ps-datetime" in time_node.attributes:
                    try:
                        ts = int(time_node.attributes["data-ps-datetime"])
                        date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    except: pass
            else:
                date_node = item_html.css_first(config["date_selector"])
                if date_node:
                    raw = date_node.text().strip()
                    try:
                        cleaned = ' '.join(part for part in raw.split() if part not in ['UK', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
                        dt = datetime.strptime(cleaned, config["date_format"])
                        date = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except: pass

            domain = urlparse(full_link).netloc.replace("www.", "").replace(config["domain_trim"], "")

            results.append({
                "headline": headline,
                "tags": tags,
                "link": full_link,
                "image": image,
                "date": date,
                "source": domain,
                "body": body
            })

            time.sleep(random.uniform(0.4, 1.0))
            print(f"Scraping Success - {config['name']}: {headline}")
        except Exception as e:
            print(f"Error in article loop: {e}")

    return results

# %%
# UNCOMMENT FOR TESTING ONLY
# all_results = scrape_site(site_configs[1])

# %%
# Run scraper across all configs
all_results = []
for config in site_configs:
    all_results += scrape_site(config)


# %%
# De-duplicate by headline
unique = {}
for item in all_results:
    if item['headline'] and item['headline'] not in unique:
        unique[item['headline']] = item

# %%
# Write JSON
with open('assets/js/articles.json', 'w', encoding='utf-8') as f:
    json.dump(list(unique.values()), f, indent=2, ensure_ascii=False)

print(f"Saved {len(unique)} unique articles.")

# %%
# Git commands
git_add_command = "git add ."
git_commit_command = 'git commit -m "Automated update of articles"'
git_push_command = "git push"

os.environ["GIT_AUTHOR_NAME"] = "TweetingCynical"
os.environ["GIT_AUTHOR_EMAIL"] = "jon@exce-ed.com"

# Get the current working directory
current_directory = os.getcwd()
script_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_directory)

# Print the current working directory for debugging
print("Current Directory:", current_directory)
print("Script Directory:", script_directory)

# Run Git commands
subprocess.run(git_add_command, shell=True)
subprocess.run(git_commit_command, shell=True)
subprocess.run(git_push_command, shell=True)


