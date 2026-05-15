"""
SAYLOR ENGAGEMENT RESUME - Continue from 2022-2025
Skip 2021 (already collected with engagement)
Complete the remaining 15 quarters!
"""

import asyncio
from playwright.async_api import async_playwright
import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import os

# CONFIG
TARGET_USER = "saylor"
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2025, 8, 31)

QUARTERLY_DIR = "./saylor_quarterly_ENGAGEMENT"

# DUAL OUTPUT (raw + filtered)
RAW_OUTPUT = "03_STAGE1_Data_Raw_Saylor.csv"              # Unfiltered (like 04_STAGE1_Data_Raw_Elon.csv)
RAW_JSON = "saylor_ALL_tweets_RAW.json"

FINAL_OUTPUT = "07_STAGE2_Valid_Saylor.csv"  # Crypto filtered
FINAL_JSON = "saylor_crypto_WITH_ENGAGEMENT_FINAL.json"

TWITTER_EMAIL = "kilokode11@gmail.com"
TWITTER_PASSWORD = "manusiabiasa."
BROWSER_DATA_DIR = "./browser_data_saylor"

# KEYWORDS
CRYPTO_KEYWORDS = [
    'bitcoin', 'btc', '$btc',
    'ethereum', 'eth', '$eth',
    'xrp', '$xrp', 'ripple',
    'solana', 'sol', '$sol',
    'binance', 'bnb', '$bnb',
    'cardano', 'ada', '$ada',
    'tron', 'trx', '$trx',
    'dogecoin', 'doge', '$doge',
    'chainlink', 'link', '$link',
    'polygon', 'matic', '$matic',
    'crypto', 'cryptocurrency', 'blockchain',
    'defi', 'web3', 'nft', 'hodl',
    'digital gold', 'digital asset',
    'store of value', 'inflation hedge',
]

def is_crypto_related(text):
    """Simple keyword check"""
    text_lower = text.lower()
    for keyword in CRYPTO_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

def parse_engagement_count(text):
    """Parse 1.2K, 3.5M, etc"""
    if not text:
        return 0
    
    text = text.strip().replace(',', '')
    
    if 'K' in text.upper():
        try:
            num = float(text.upper().replace('K', ''))
            return int(num * 1000)
        except:
            return 0
    
    if 'M' in text.upper():
        try:
            num = float(text.upper().replace('M', ''))
            return int(num * 1000000)
        except:
            return 0
    
    try:
        return int(text)
    except:
        return 0

async def extract_engagement(element):
    """Extract likes, retweets, replies, views"""
    metrics = {
        'likes': 0,
        'retweets': 0,
        'replies': 0,
        'views': 0,
        'quotes': 0,
    }
    
    try:
        engagement_group = await element.query_selector('[role="group"]')
        if not engagement_group:
            return metrics
        
        buttons = await engagement_group.query_selector_all('button, [role="button"], div[data-testid]')
        
        for button in buttons:
            try:
                aria_label = await button.get_attribute('aria-label')
                if aria_label:
                    aria_lower = aria_label.lower()
                    
                    if 'repl' in aria_lower:
                        match = re.search(r'(\d+[\d,KkMm]*)', aria_label)
                        if match:
                            metrics['replies'] = parse_engagement_count(match.group(1))
                    
                    elif 'retweet' in aria_lower or 'repost' in aria_lower:
                        match = re.search(r'(\d+[\d,KkMm]*)', aria_label)
                        if match:
                            metrics['retweets'] = parse_engagement_count(match.group(1))
                    
                    elif 'like' in aria_lower:
                        match = re.search(r'(\d+[\d,KkMm]*)', aria_label)
                        if match:
                            metrics['likes'] = parse_engagement_count(match.group(1))
                    
                    elif 'view' in aria_lower:
                        match = re.search(r'(\d+[\d,KkMm]*)', aria_label)
                        if match:
                            metrics['views'] = parse_engagement_count(match.group(1))
                
                testid = await button.get_attribute('data-testid')
                if testid:
                    text = await button.inner_text()
                    
                    if 'reply' in testid.lower():
                        metrics['replies'] = parse_engagement_count(text)
                    elif 'retweet' in testid.lower():
                        metrics['retweets'] = parse_engagement_count(text)
                    elif 'like' in testid.lower():
                        metrics['likes'] = parse_engagement_count(text)
                    elif 'view' in testid.lower():
                        metrics['views'] = parse_engagement_count(text)
                        
            except:
                continue
                
    except:
        pass
    
    return metrics

def generate_quarters(start_date, end_date):
    """Generate quarterly periods"""
    quarters = []
    current = start_date
    
    while current <= end_date:
        if current.month + 3 > 12:
            quarter_end = datetime(current.year + 1, (current.month + 3) - 12, 1) - timedelta(days=1)
        else:
            quarter_end = datetime(current.year, current.month + 3, 1) - timedelta(days=1)
        
        if quarter_end > end_date:
            quarter_end = end_date
        
        quarters.append({
            'start': current,
            'end': quarter_end,
            'label': f"{current.strftime('%Y-%m')}_to_{quarter_end.strftime('%Y-%m')}"
        })
        
        if current.month + 3 > 12:
            current = datetime(current.year + 1, (current.month + 3) - 12, 1)
        else:
            current = datetime(current.year, current.month + 3, 1)
        
        if current > end_date:
            break
    
    return quarters

def check_existing_quarters():
    """Check which quarters already have engagement data"""
    Path(QUARTERLY_DIR).mkdir(exist_ok=True)
    
    existing = []
    for file in os.listdir(QUARTERLY_DIR):
        if file.endswith('.json'):
            quarter_label = file.replace('.json', '')
            existing.append(quarter_label)
    
    return existing

async def check_if_logged_in(page):
    """Check login"""
    try:
        await page.goto("https://twitter.com/home", timeout=10000)
        await page.wait_for_timeout(2000)
        try:
            await page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=5000)
            return True
        except:
            return False
    except:
        return False

async def login_twitter(page):
    """Auto-login"""
    print("\n🔐 Logging in...")
    
    try:
        await page.goto("https://twitter.com/login", timeout=30000)
        await page.wait_for_timeout(3000)
        
        print("   Entering Email...")
        selectors = [
            'input[autocomplete="username"]',
            'input[name="text"]',
            'input[type="text"]',
        ]
        
        email_input = None
        for selector in selectors:
            try:
                email_input = page.locator(selector).first
                await email_input.wait_for(timeout=5000)
                break
            except:
                continue
        
        if email_input:
            await email_input.fill(TWITTER_EMAIL)
            await email_input.press("Enter")
            await page.wait_for_timeout(3000)
        else:
            return False
        
        print("   Entering Password...")
        password_input = page.locator('input[type="password"]').first
        await password_input.wait_for(timeout=5000)
        await password_input.fill(TWITTER_PASSWORD)
        await password_input.press("Enter")
        await page.wait_for_timeout(5000)
        
        if "home" in page.url:
            print("   ✅ Login OK!")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def scrape_quarter(page, username, start_date, end_date, quarter_label):
    """Scrape with engagement"""
    print(f"\n[QUARTER] {quarter_label}")
    print(f"   {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    query = f"from:{username} since:{start_date.strftime('%Y-%m-%d')} until:{end_date.strftime('%Y-%m-%d')}"
    url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
    
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(5000)
    
    tweets = []
    seen_ids = set()
    scroll_attempts = 0
    max_scrolls = 100
    no_new_content = 0
    
    while scroll_attempts < max_scrolls:
        tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')
        
        new_tweets = 0
        for element in tweet_elements:
            try:
                link_element = await element.query_selector('a[href*="/status/"]')
                if not link_element:
                    continue
                
                href = await link_element.get_attribute('href')
                if not href or '/status/' not in href:
                    continue
                
                tweet_id = href.split('/status/')[-1].split('?')[0]
                
                if tweet_id in seen_ids:
                    continue
                seen_ids.add(tweet_id)
                
                text_element = await element.query_selector('[data-testid="tweetText"]')
                text = await text_element.inner_text() if text_element else ""
                
                time_element = await element.query_selector('time')
                timestamp = await time_element.get_attribute('datetime') if time_element else ""
                
                engagement = await extract_engagement(element)
                
                total_engagement = (
                    engagement['likes'] + 
                    engagement['retweets'] + 
                    engagement['replies']
                )
                
                tweet = {
                    'id': tweet_id,
                    'username': username,
                    'timestamp': timestamp,
                    'content': text,
                    'likes': engagement['likes'],
                    'retweets': engagement['retweets'],
                    'replies': engagement['replies'],
                    'quotes': engagement['quotes'],
                    'views': engagement['views'],
                    'total_engagement': total_engagement,
                    'url': f'https://twitter.com/{username}/status/{tweet_id}',
                    'quarter': quarter_label,
                }
                
                tweets.append(tweet)
                new_tweets += 1
                
            except:
                continue
        
        if new_tweets > 0:
            no_new_content = 0
            if len(tweets) % 50 == 0:
                print(f"   {len(tweets)} tweets (scroll {scroll_attempts+1})")
        else:
            no_new_content += 1
            if no_new_content >= 10:
                break
        
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(2000)
        scroll_attempts += 1
    
    print(f"   [DONE] {len(tweets)} tweets with engagement")
    return tweets

async def main():
    print("="*80)
    print("RESUME ENGAGEMENT SCRAPING")
    print("="*80)
    
    # Check existing
    existing_quarters = check_existing_quarters()
    print(f"\n[OK] Already collected: {len(existing_quarters)} quarters")
    for q in sorted(existing_quarters):
        print(f"   [DONE] {q}")
    
    # Generate all quarters
    all_quarters = generate_quarters(START_DATE, END_DATE)
    
    # Find remaining
    remaining_quarters = [q for q in all_quarters if q['label'] not in existing_quarters]
    
    print(f"\n[PENDING] Remaining: {len(remaining_quarters)} quarters")
    for i, q in enumerate(remaining_quarters, 1):
        print(f"   {i}. {q['label']}")
    
    if not remaining_quarters:
        print("\n[COMPLETE] ALL QUARTERS ALREADY COLLECTED!")
        print("   Proceeding to combine data...")
    else:
        print(f"\n[START] Starting {len(remaining_quarters)} remaining quarters...")
    
    # Launch browser
    async with async_playwright() as p:
        print("\n[LAUNCH] Launching browser...")
        
        context = await p.chromium.launch_persistent_context(
            BROWSER_DATA_DIR,
            headless=False,
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Login
        if remaining_quarters:
            print("\n[CHECK] Checking login...")
            is_logged_in = await check_if_logged_in(page)
            
            if not is_logged_in:
                login_success = await login_twitter(page)
                if not login_success:
                    print("\n⚠️  Login failed! Do manually.")
                    input("   Press ENTER...")
            else:
                print("   [OK] Logged in!")
            
            # Scrape remaining
            for i, quarter in enumerate(remaining_quarters, 1):
                print("\n" + "="*80)
                print(f"QUARTER {i}/{len(remaining_quarters)} (Overall: {len(existing_quarters)+i}/{len(all_quarters)})")
                print("="*80)
                
                quarter_tweets = await scrape_quarter(
                    page, 
                    TARGET_USER, 
                    quarter['start'], 
                    quarter['end'],
                    quarter['label']
                )
                
                if quarter_tweets:
                    quarter_file = f"{QUARTERLY_DIR}/{quarter['label']}.json"
                    with open(quarter_file, 'w', encoding='utf-8') as f:
                        json.dump(quarter_tweets, f, ensure_ascii=False, indent=2)
                    print(f"   💾 {quarter_file}")
                    existing_quarters.append(quarter['label'])
                
                print(f"   📊 Progress: {len(existing_quarters)}/{len(all_quarters)}")
                
                if i < len(remaining_quarters):
                    await page.wait_for_timeout(5000)
        
        await context.close()
    
    # Combine all
    print("\n" + "="*80)
    print("📦 COMBINING ALL QUARTERLY DATA")
    print("="*80)
    
    all_tweets = []
    for quarter_file in sorted(os.listdir(QUARTERLY_DIR)):
        if quarter_file.endswith('.json'):
            filepath = os.path.join(QUARTERLY_DIR, quarter_file)
            with open(filepath, 'r', encoding='utf-8') as f:
                quarter_tweets = json.load(f)
                all_tweets.extend(quarter_tweets)
                print(f"   ✅ {quarter_file}: {len(quarter_tweets)} tweets")
    
    print(f"\n   📊 Total: {len(all_tweets)} tweets")
    
    # Save RAW (unfiltered) first
    if all_tweets:
        print(f"\n💾 Saving RAW data (unfiltered)...")
        
        with open(RAW_OUTPUT, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'id', 'username', 'timestamp', 'content', 
                'likes', 'retweets', 'replies', 'quotes', 'views',
                'total_engagement', 'url', 'quarter'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_tweets)
        
        print(f"   ✅ {RAW_OUTPUT} ({len(all_tweets)} tweets - ALL unfiltered)")
        
        with open(RAW_JSON, 'w', encoding='utf-8') as f:
            json.dump(all_tweets, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ {RAW_JSON}")
    
    # Filter crypto
    print("\n🔍 Filtering crypto...")
    crypto_tweets = [t for t in all_tweets if is_crypto_related(t['content'])]
    
    print(f"   ✅ {len(crypto_tweets)} crypto / {len(all_tweets)} total")
    print(f"   Crypto rate: {len(crypto_tweets)/len(all_tweets)*100:.1f}%")
    
    # Save FILTERED (crypto only)
    if crypto_tweets:
        print(f"\n💾 Saving FILTERED data (crypto only)...")
        
        with open(FINAL_OUTPUT, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'id', 'username', 'timestamp', 'content', 
                'likes', 'retweets', 'replies', 'quotes', 'views',
                'total_engagement', 'url', 'quarter'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(crypto_tweets)
        
        print(f"   ✅ {FINAL_OUTPUT} ({len(crypto_tweets)} tweets - crypto filtered)")
        
        with open(FINAL_JSON, 'w', encoding='utf-8') as f:
            json.dump(crypto_tweets, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ {FINAL_JSON}")
    
    # Summary
    print("\n" + "="*80)
    print("🎉 COMPLETE - DUAL OUTPUT!")
    print("="*80)
    print(f"Total tweets: {len(all_tweets)}")
    print(f"Crypto tweets: {len(crypto_tweets)}")
    print(f"Quarters: {len(existing_quarters)}/{len(all_quarters)}")
    print(f"\nOutput files:")
    print(f"  📦 RAW (unfiltered): {RAW_OUTPUT}")
    print(f"  🎯 CRYPTO (filtered): {FINAL_OUTPUT}")
    print("="*80)

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("\nRESUME MODE - Continue engagement scraping!")
    print("   Skip 2021 (already done)")
    print("   Scrape 2022-2025 remaining quarters\n")
    
    # Auto-resume, no input needed
    print("Auto-starting in 3 seconds...")
    import time
    time.sleep(3)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped")
        print(f"   Saved in: {QUARTERLY_DIR}/")



