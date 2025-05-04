# %%
# Imports
import httpx
from selectolax.parser import HTMLParser
import json
import time
import os
import random

from datetime import datetime
from urllib.parse import urlparse

# Set the timer
start_time = time.time()


# %%
# Set URL for Mirror Football
url = 'https://www.mirror.co.uk/all-about/manchester-united-fc'

headers = {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

try:
    resp = httpx.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
except httpx.RequestError as e:
    print(f"Request failed: {e}")


if resp.status_code == 200:
    print("Request successful.")
else:
    print(f"Request failed: {resp.status_code}")


# %%
# Get HTML from Mirror Football
html = HTMLParser(resp.text)

# Get articles
articles = html.css("article.story")
print(articles)

# %%
# Exclude body contents containing these phrases
excluded_phrases = [
    'Manchester Evening News',
    'Our community members are treated to',
    'Sky Sports',
    'Mirror Football',
    'Get involved!',
    'Let us know in the comments below',
    'Have your say in the comments section',
    'HAVE YOUR SAY',
    'Share your thoughts in the comments below',
    'Join the debate!',
    'Join our new WhatsApp',
    'Sky has slashed',
    'At Reach and across our'
    'TNT Sports',
    'Get our FREE daily Manchester United email newsletter',
    'Get the FREE Mirror Football newsletter',
    'Join our new WhatsApp community!',
    'Vote in our poll HERE to have your say',
    'READ MORE: ',
    'Sign up for our daily newsletter',
    'We have more newsletters',
    'READ NEXT: ',
    'LUCKHURST: ',
    'TEAM NEWS: ',
    'TEN HAG: ',
    'Our team of Manchester United experts are',
    '--',
    'We also treat our community members',
    'Hello and welcome to our press conference coverage',
    'We will bring you the latest',
    'delivered straight to your inbox',
    'ALSO READ: ',
    "United's Adidas home shirt is made up",
    "United's Adidas away shirt is made up",
    'Prices start from',
    'with our dedicated Man Utd updates',
    'Keep tabs on the latest ',
    'Man Utd fixtures',
    'Report and free match highlights',
    'Transfer Centre',
    'Sorry, this blog is currently unavailable. Please try again later.',
    'Premier League table',
    'Watch Premier League highlights',
    'Stream Sky Sports',
    'Get Sky Sports',
    'Stream Sky Sports on NOW!',
    'Download the Sky Sports App',
    'Premier League fixtures',
    'Papers - latest headlines',
    'Latest Man Utd news',
    'Get NOW to stream Sky Sports',
    'Please use Chrome browser for a more accessible video player',
    '© 2024 Sky UK',
    'Watch free Premier League highlights',
    '\n                                    \n                                        \n                                            \n                                        Football\n                                    \n                                ',
    'Comment and Analysis',
    '@ghostgoal',
    'Download the Sky Sports',
    'Get NOW to stream big moments',
    'Live football on Sky Sports',
    'Correctly predict six scorelines',
    'Football Expert',
    'How the teams lined up',
    'Match stats',
    'Stream the biggest moments on NOW',
    '        ',
    'Football Journalist',
    'Listen and subscribe on',
    'Subscribe to',
    'Try MUFC Pro',
    'Free trial',
    'Luckhurst',
    'Sign up here',
    'PLAYER RATINGS',
    'MATCH REACTION',
    'latest news and updates',
    'Read the full feature',
    'Find out more here',
    'Here at the Manchester Evening News, we’re',
    'Make sure you don’t miss out on the latest',
    'You can also subscribe to our free newsletter service',
    'Our team of Manchester United experts',
    'You can get all the breaking news and best analysi',
    'Our shows are available on all podcast platforms',
    '© 2025 Sky UK',
    '@skysports',
    'Play for free!',
    '© Planet Sport Limited 2025',
    'MORE MAN UTD COVERAGE ON F365',
    'MUST READ FROM F365',
    'TRY THIS NEXT',
    'MORE ON MAN UTD',
    
    ]

# Tags for article headlines
tags_to_check = [
    'Exclusive',
    'Manchester United',
    'Man Utd', 
    'Premier League',
    'Champions League',
    'Europa League'
    'Transfer News',
    'Ferguson',
    'Rooney',
    'Ronaldo',
    'Ratcliffe',
    'INEOS',
    'Amorim',
    'Fernandes',
    'Maguire',
    'De Ligt',
    'Amad',
    'Yoro',
    'Onana',
    'Mainoo',
    'Rashford',
    'Hojlund',
    'Martinez',
    'Mason Mount',
    'Antony',
    'Solksjaer',
    'Casemiro',
    'Garnacho',
    'Eriksen',
    'Beckham',
    'Roy Keane',
    'Gary Neville',
    'Mourinho',
    'LIVE',
    'Glazer',
    ]



# %%
# Mirror Football results
results = []

for article in articles:

    try:
        image_value = article.css_first("a div amp-img").attributes.get('src')
    except AttributeError:
        # Handle the case where "amp-img" is not found
        image_value = None
    
    articleLink = article.css_first("a").attributes.get('href', '')

    itemResp = httpx.get(articleLink, headers=headers)
    itemHtml = HTMLParser(itemResp.text)
    story = []
    contents = itemHtml.css('p')
    infoContents = itemHtml.css('div.article-information')
    
    date_value = None
    headline_value = article.css_first("a").text()
    
    # Check if any tag is present in the headline_value
    matching_tags = [tag for tag in tags_to_check if tag.lower() in headline_value.lower()]
    
    corrected_tags = []
    
    for tag in matching_tags:
        if tag == "Manchester United":
            tag = "Man Utd"
        corrected_tags.append(tag)
    
    for dates in infoContents:
        try:
            date_value = dates.css_first("ul li span.time-container").text()
        except AttributeError:
        # Handle the case where "time-container" is not found
            date_value = None
        break
    
    for content in contents:
        content_text = content.css_first('p').text()
            
        # Check if any excluded phrase is present in the content
        if not any(phrase in content_text for phrase in excluded_phrases):
            trimmed_content_text = content_text.strip()
            story.append(trimmed_content_text)
            
    # Convert the date string to a datetime object
    try:
        date_object = datetime.strptime(date_value, '%H:%M, %d %b %Y')
        formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
    except (TypeError, ValueError):
        formatted_date = None

    # Extract the domain from the link
    parsed_url = urlparse(articleLink)
    domain = parsed_url.netloc.replace('www.', '').replace('.co.uk', '')

    item = {
        "headline": headline_value,
        "tags": corrected_tags,
        "link": article.css_first("a").attributes.get('href', ''),
        "image": image_value,
        "date": formatted_date,
        "source": domain,  # Add the 'source' key-value pair
        "body": story
    }
    results.append(item)
    
    # Add a delay to avoid IP banning
    delay = random.uniform(0, 1)
    time.sleep(delay)


# %%
# Set URL for Manchester Evening News
url = 'https://www.manchestereveningnews.co.uk/all-about/manchester-united-fc'

headers = {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

try:
    resp = httpx.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
except httpx.RequestError as e:
    print(f"Request failed: {e}")


if resp.status_code == 200:
    print("Request successful.")
else:
    print(f"Request failed: {resp.status_code}")

# %%
# Get HTML Manchester Evening News
html = HTMLParser(resp.text)

# Get articles
articles = html.css("div.teaser")
print(articles)

# %%
# MEN results
for article in articles:
    
    articleLink = article.css_first("a").attributes.get('href', '')

    itemResp = httpx.get(articleLink, headers=headers)
    itemHtml = HTMLParser(itemResp.text)
    story = []
    contents = itemHtml.css('p')
    headlineContents = itemHtml.css('div.headline-with-subtype')
    imgContents = itemHtml.css('div.img-container')
    infoContents = itemHtml.css('div.article-information')
    
    headline_value = None
    image_value = None
    date_value = None
    
    for headline in headlineContents:
        try:
            headline_value = headline.css_first("h1").text()
            # Check if any tag is present in the headline_value
            matching_tags = [tag for tag in tags_to_check if tag.lower() in headline_value.lower()]
        except AttributeError:
        # Handle the case where a headline is not found
            headline_value = None
            matching_tags = None
        break
    
    corrected_tags = []
    
    for tag in matching_tags:
        if tag == "Manchester United":
            tag = "Man Utd"
        corrected_tags.append(tag)
    
    for image in imgContents:
        try:
            image_value = image.css_first("img").attributes.get('src')
        except AttributeError:
        # Handle the case where "amp-img" is not found
            image_value = None
        break
    
    for dates in infoContents:
        try:
            date_value = dates.css_first("ul li span.time-container").text()
        except AttributeError:
        # Handle the case where "time-container" is not found
            date_value = None
        break
    
    for content in contents:
        content_text = content.css_first('p').text()
            
        # Check if any excluded phrase is present in the content
        if not any(phrase in content_text for phrase in excluded_phrases):
            trimmed_content_text = content_text.strip()
            story.append(trimmed_content_text)
            
    
    # Convert the date string to a datetime object
    try:
        date_object = datetime.strptime(date_value, '%H:%M, %d %b %Y')
        formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
    except (TypeError, ValueError):
        formatted_date = None

    # Extract the domain from the link
    parsed_url = urlparse(articleLink)
    domain = parsed_url.netloc.replace('www.', '').replace('.co.uk', '')

    item = {
        "headline": headline_value,
        "tags": corrected_tags,
        "link": articleLink,
        "image": image_value,
        "date": formatted_date,
        "source": domain,  # Add the 'source' key-value pair
        "body": story
    }
    results.append(item)
    
    # Add a delay to avoid IP banning
    delay = random.uniform(0, 1)
    time.sleep(delay)


# %% [markdown]
# ALL WORKING UP TO THIS POINT. NOW TEST FOR SKY SPORTS, THEN MOVE JSON DUMP TO THE END WHEN WORKING

# %%
# Set URL for Football 365
url = 'https://www.football365.com/manchester-united'

headers = {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

try:
    resp = httpx.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
except httpx.RequestError as e:
    print(f"Request failed: {e}")


if resp.status_code == 200:
    print("Request successful.")
else:
    print(f"Request failed: {resp.status_code}")

# %%
# Get HTML from Football 365
html = HTMLParser(resp.text)

# Get articles
articles = html.css("div.news-card")
print(articles)

# %%
headers["referer"] = url

for article in articles:
    try:
        articleLink = article.css_first("a").attributes.get('href', '')
        headline_value = None
        headline_value = article.css_first("h2").text().strip()

        itemResp = httpx.get(articleLink, headers=headers)
        itemHtml = HTMLParser(itemResp.text)
        story = []
        contents = itemHtml.css('p')
        imgContents = itemHtml.css('img.object-cover')
        infoContents = itemHtml.css('div.article-information')
        
        image_value = None
        
        try:
            # Check if any tag is present in the headline_value
            matching_tags = [tag for tag in tags_to_check if tag.lower() in headline_value.lower()]
        except AttributeError:
            # Handle the case where a headline is not found
            headline_value = None
            matching_tags = None
            break
        
        corrected_tags = []
        
        for tag in matching_tags:
            if tag == "Manchester United":
                tag = "Man Utd"
            corrected_tags.append(tag)
        
        for image in imgContents:
            try:
                image_value = image.css_first("img").attributes.get('src')
            except AttributeError:
            # Handle the case where "amp-img" is not found
                image_value = None
            break
        
        for content in contents:
            content_text = content.css_first('p').text()
                
            # Check if any excluded phrase is present in the content
            if not any(phrase in content_text for phrase in excluded_phrases):
                trimmed_content_text = content_text.strip()
                story.append(trimmed_content_text)
                
        
        formatted_date = None
        try:
            date_node = itemHtml.css_first("header time")
            if date_node and "data-ps-datetime" in date_node.attributes:
                timestamp_str = date_node.attributes["data-ps-datetime"]
                if timestamp_str.isdigit():
                    timestamp_sec = int(timestamp_str)
                    date_object = datetime.fromtimestamp(timestamp_sec)
                    formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    print(f"Non-numeric timestamp: {timestamp_str}")
            else:
                print("No data-ps-datetime attribute found in <time> element")
        except Exception as e:
            print(f"Failed to parse Football365 date: {e}")


        # Format it as needed
        formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')

        # Extract the domain from the link
        parsed_url = urlparse(articleLink)
        domain = parsed_url.netloc.replace('www.', '').replace('.com', '')

        item = {
            "headline": headline_value,
            "tags": corrected_tags,
            "link": articleLink,
            "image": image_value,
            "date": formatted_date,
            "source": domain,  # Add the 'source' key-value pair
            "body": story
        }
        results.append(item)
        
        # Add a delay to avoid IP banning
        delay = random.uniform(0, 1)
        time.sleep(delay)
        print(item)

    except Exception as e:
        print(f"Failed to process article: {e}")


# %%
# Get articles
articles = html.css("article.ps-more-articles-card")
print(articles)

# %%
headers["referer"] = url

for article in articles:
    try:
        articleLink = article.css_first("a").attributes.get('href', '')
        headline_value = None
        headline_value = article.css_first("h3").text().strip()

        itemResp = httpx.get(articleLink, headers=headers)
        itemHtml = HTMLParser(itemResp.text)
        story = []
        contents = itemHtml.css('p')
        imgContents = itemHtml.css('img.object-cover')
        infoContents = itemHtml.css('div.article-information')
        
        image_value = None
        
        try:
            # Check if any tag is present in the headline_value
            matching_tags = [tag for tag in tags_to_check if tag.lower() in headline_value.lower()]
        except AttributeError:
            # Handle the case where a headline is not found
            headline_value = None
            matching_tags = None
            break
        
        corrected_tags = []
        
        for tag in matching_tags:
            if tag == "Manchester United":
                tag = "Man Utd"
            corrected_tags.append(tag)
        
        for image in imgContents:
            try:
                image_value = image.css_first("img").attributes.get('src')
            except AttributeError:
            # Handle the case where "amp-img" is not found
                image_value = None
            break
        
        for content in contents:
            content_text = content.css_first('p').text()
                
            # Check if any excluded phrase is present in the content
            if not any(phrase in content_text for phrase in excluded_phrases):
                trimmed_content_text = content_text.strip()
                story.append(trimmed_content_text)
                
        
        formatted_date = None
        try:
            date_node = itemHtml.css_first("header time")
            if date_node and "data-ps-datetime" in date_node.attributes:
                timestamp_str = date_node.attributes["data-ps-datetime"]
                if timestamp_str.isdigit():
                    timestamp_sec = int(timestamp_str)
                    date_object = datetime.fromtimestamp(timestamp_sec)
                    formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    print(f"Non-numeric timestamp: {timestamp_str}")
            else:
                print("No data-ps-datetime attribute found in <time> element")
        except Exception as e:
            print(f"Failed to parse Football365 date: {e}")


        # Format it as needed
        formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')

        # Extract the domain from the link
        parsed_url = urlparse(articleLink)
        domain = parsed_url.netloc.replace('www.', '').replace('.com', '')

        item = {
            "headline": headline_value,
            "tags": corrected_tags,
            "link": articleLink,
            "image": image_value,
            "date": formatted_date,
            "source": domain,  # Add the 'source' key-value pair
            "body": story
        }
        results.append(item)
        
        # Add a delay to avoid IP banning
        delay = random.uniform(0, 1)
        time.sleep(delay)
        print(item)

    except Exception as e:
        print(f"Failed to process article: {e}")


# %%
# Set URL for Sky Sports
url = 'https://www.skysports.com/manchester-united-news'

headers = {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

try:
    resp = httpx.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
except httpx.RequestError as e:
    print(f"Request failed: {e}")


if resp.status_code == 200:
    print("Request successful.")
else:
    print(f"Request failed: {resp.status_code}")

# %%
# Get HTML from Sky Sports
html = HTMLParser(resp.text)

# Get articles
articles = html.css("div.sdc-site-tiles__item")
print(articles)

# WORKING

# %%
# Pretty print article node for verification
print(articles[0].html) # Shows raw HTML of the first article

# %%
headers["referer"] = url

for article in articles:
    try:
        articleLink = article.css_first("a").attributes.get('href', '')
        full_article_url = f"https://www.skysports.com{articleLink}"
        headline_value = article.css_first("span.sdc-site-tile__headline-text").text().strip()

        matching_tags = [tag for tag in tags_to_check if tag.lower() in headline_value.lower()]
        corrected_tags = ["Man Utd" if tag == "Manchester United" else tag for tag in matching_tags]

        img_node = article.css_first("picture img")
        image_value = img_node.attributes.get('src') if img_node else None

        itemResp = httpx.get(full_article_url, headers=headers, timeout=10)
        itemHtml = HTMLParser(itemResp.text)

        # Get date from full article page
        try:
            date_node = itemHtml.css_first("p.sdc-article-date__date-time")
            if date_node:
                raw_date = date_node.text().strip()
                cleaned_date = ' '.join(part for part in raw_date.replace(',', '').split() if part not in ['UK', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
                date_object = datetime.strptime(cleaned_date, "%d %B %Y %H:%M")
                formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
            else:
                formatted_date = None
        except Exception as e:
            print(f"Failed to parse date: {e}")
            formatted_date = None

        story = []
        contents = itemHtml.css('p')
        for content in contents:
            content_text = content.text().strip()
            if content_text and not any(phrase in content_text for phrase in excluded_phrases):
                story.append(content_text)

        domain = urlparse(full_article_url).netloc.replace('www.', '').replace('.com', '')

        item = {
            "headline": headline_value,
            "tags": corrected_tags,
            "link": full_article_url,
            "image": image_value,
            "date": formatted_date,
            "source": domain,
            "body": story
        }
        results.append(item)

        time.sleep(random.uniform(0.5, 1.2))  # Slightly longer to avoid detection
        print(item)

    except Exception as e:
        print(f"Failed to process article: {e}")


# %%
# Create a set to store unique headlines
unique_headlines = set()

# Create a new list to store articles with unique headlines
unique_articles = []

# Iterate through the articles
for article in results:
    headline = article['headline']

    # Check if the headline is unique
    if headline not in unique_headlines:
        unique_headlines.add(headline)
        unique_articles.append(article)

# Save the new list of articles with unique headlines
with open('assets/js/articles.json', 'w', encoding='utf-8') as json_file:
    json.dump(unique_articles, json_file, ensure_ascii=False, indent=2)

# with open('Outputs/articles.json', 'w', encoding='utf-8') as json_file:
#     json.dump(results, json_file, ensure_ascii=False, indent=2)

# %%
# End the timer
end_time = time.time()

elapsed = end_time - start_time

# Print a message with the elapsed time
print(f"Script took {elapsed:.2f} seconds to run.")

# %%
import subprocess

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


