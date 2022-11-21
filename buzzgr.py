import requests
from bs4 import BeautifulSoup
import dotenv
import datetime
import json
import time
from requests.models import Response
import urllib3
import os

CONFIG = dotenv.dotenv_values()


INSTOCK = []


def scrape_main_site(url, headers):
    items = []
    s = requests.Session()
    response = s.get(url=url, headers=headers)
    print(response)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div',  {'class': 'product-item'})
    for product in products:
        item = [product['data-productname'],
                product['data-productprice'],
                product['data-productcode'],
                product.find('a')['href'],
                product.find('img')['src']]
        items.append(item)
        
    return items


def discord_webhook(product_item):
  
  data = {}
  data["username"] = CONFIG['USERNAME']
  data["avatar_url"] = CONFIG['AVATAR_URL']
  data["embeds"] = []
  embed = {}
  if product_item == 'initial':
      embed["title"] = "Cache Cleared."
      embed["author"] = {'name': 'asos.com', 'icon_url': 'https://i.imgur.com/Fg3nF2K.png', 'url':'https://www.asos.com'}
      embed["color"] = int(16777215)
      embed["footer"] = {'text': 'Buzz | Celestial Scripts', 'icon_url': ''}
      embed["timestamp"] = str(datetime.datetime.utcnow())
      data["embeds"].append(embed)
      result = requests.post("https://discord.com/api/webhooks/861700007476592670/W_e-iZd_1TMqkjJzF4SF2tNKdvfFFdkB88nQF0YXvaXXb-xn1UHOh05mfGQ7jRmg4CFE", data=json.dumps(data), headers={"Content-Type": "application/json"})
  else:
      product_name = product_item[0].split(';')
      embed["title"] = f'[NEW] **{product_name[0].upper()}**'
      print(product_item[0])
      embed["fields"] = [{'name': 'PRICE:' , 'value': f'{product_item[1]} RSD', 'inline': True},
      {'name': 'SKU:' , 'value': f'{product_item[2]}', 'inline': True}]
      embed['url'] = f'{product_item[3]}'  # Item link
      embed['thumbnail'] = {'url': f'https://www.buzzsneakers.com{product_item[4]}'} #Item Image
      embed["author"] = {'name': 'buzzsneakers.com', 'icon_url': 'https://bucurestimall.ro/wp-content/uploads/2017/08/BUZZ-LOGO-White-on-Black.jpg', 'url':'https://www.buzzsneakers.com'}
      embed["color"] = int(16777215)
      embed["footer"] = {'text': 'buzzsneakers.com for axel940#4947', 'icon_url': ''}
      embed["timestamp"] = str(datetime.datetime.utcnow())
      data["embeds"].append(embed)

      result = requests.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

  try:
      result.raise_for_status()
  except requests.exceptions.HTTPError as err:
      print(err)
  else:
      print("Payload delivered successfully, code {}.".format(result.status_code))


def checker(item):
    for product in INSTOCK:
        if product == item:
            return True
    return False


def remove_duplicates(mylist):
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(item, start):
    if not checker(item):
        INSTOCK.append(item)
        if start == 0:
            discord_webhook(item)


def monitor():
    print('STARTING MONITOR')
    discord_webhook('initial')
    start = 1
    headers = {
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'exitslidermodal=1; zps-tgr-dts=sc%3D2-expAppOnNewSession%3D%5B%5D-pc%3D5-sesst%3D1667784933649; zsccae066dca638488ca7ce61689552a062=1667784933648zsc0.5609731289530194; mobile_cookie_baner=1; order_limit=24; zft-sdc=isef%3Dtrue-isfr%3Dtrue-src%3Ddirect; NBIDSN=c91a4a2d86bdbb040b277f87e2498c35M3OA4vb4nNKuMhoPGpLhWNILOE53ods8ezk57bBRgsnRxQsjaLrxhWQ9MCFw1nh3ol50; _bamls_usid=7e81e6cc-032a-4aa4-879f-724645094bb7; site_cookie_info=1; zabUserId=1667648041570zabu0.35575858271690186; NBPHPSESSIONSECURE=f9e4d2fa9f4814a0c09144126c6f8643',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Host': 'www.buzzsneakers.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Accept-Language': 'en-IN,en-GB;q=0.9,en;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    keywords = CONFIG['KEYWORDS'].split('%')
    i = 0
    print('Initial Listing Load Complete, checking for changes in future cycles.')
    while True:
        i = i + 1
        print(f'[{datetime.datetime.utcnow()}] [LOG] - Cycle #{i} Complete')
        #urls = json.loads(os.environ['CATEGORY_URLS'])
        urls = ["https://www.buzzsneakers.com/SRB_rs/proizvodi?search=Jordan+1","https://www.buzzsneakers.com/SRB_rs/proizvodi?search=dunk"]
        j = 0
        for url in urls:
            j = j + 1
            print(f'    [{datetime.datetime.utcnow()}] [EVENT] - Checking Link #{j}') 
            try:
                items = remove_duplicates(scrape_main_site(url, headers))
                for item in items:
                    check = False
                    if keywords == '':
                        comparitor(item, start)
                    else:
                        for key in keywords:
                            if key.lower() in item[0].lower():
                                check = True
                                break
                        if check:
                            comparitor(item, start)
                time.sleep(float(CONFIG['DELAY']))
                
            except Exception as e:
                print(f"Exception found '{e}' - Rotating headers and retrying")
                headers = {
                    # Requests sorts cookies= alphabetically
                    # 'Cookie': 'exitslidermodal=1; zps-tgr-dts=sc%3D2-expAppOnNewSession%3D%5B%5D-pc%3D5-sesst%3D1667784933649; zsccae066dca638488ca7ce61689552a062=1667784933648zsc0.5609731289530194; mobile_cookie_baner=1; order_limit=24; zft-sdc=isef%3Dtrue-isfr%3Dtrue-src%3Ddirect; NBIDSN=c91a4a2d86bdbb040b277f87e2498c35M3OA4vb4nNKuMhoPGpLhWNILOE53ods8ezk57bBRgsnRxQsjaLrxhWQ9MCFw1nh3ol50; _bamls_usid=7e81e6cc-032a-4aa4-879f-724645094bb7; site_cookie_info=1; zabUserId=1667648041570zabu0.35575858271690186; NBPHPSESSIONSECURE=f9e4d2fa9f4814a0c09144126c6f8643',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Host': 'www.buzzsneakers.com',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                    'Accept-Language': 'en-IN,en-GB;q=0.9,en;q=0.8',
                    # 'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                }
        start = 0

if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
