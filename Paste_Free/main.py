import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging

def logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    return logging.getLogger()

class PasteFree:
    def __init__(self):
        self.url_base = 'https://pastefree.net'
        self.logger = logger()
        
    def get_recent_posts(self):
        res = requests.get(f'{self.url_base}/posts')
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.content, 'html.parser')
        
        posts = soup.find_all('a', class_='block py-4 sm:py-5 sm:grid sm:grid-cols-6 sm:gap-4 sm:px-6 hover:bg-gray-50')
        return posts
    
    def get_page(self, id: str):
        page = requests.get(f'{self.url_base}/{id}')
        
        if page.status_code == 200:
            return BeautifulSoup(page.content, 'html.parser')
        
    def get_date(self,date):
        time = date.replace('ago', '').strip().split(' ')
        time_num = int(time[0])
        time_prefix = time[1].replace('s', '')
        
        date_now = datetime.now()
        
        times = {
            'minute': timedelta(minutes=time_num),
            'hour': timedelta(hours=time_num),
            'day': timedelta(days=time_num),
            'week': timedelta(weeks=time_num),
            'month': timedelta(days=time_num*30)
        }
        
        for time, time_delta in times.items():
            if time == time_prefix:
                return date_now - time_delta
            
        return date_now
        
    def start(self):
        all_posts = []
        
        posts = self.get_recent_posts()
        
        if not posts:
            self.logger.debug(f"Não foi possível coletar página")
            return None
        
        for post in posts:
            post_id = post['href'].split('/')[-1]
            
            self.logger.info(f"Analisando post com o ID {post_id}")
            post_infos = {
                "url": f"{self.url_base}/{post_id}",
                "infos": {
                    "post_id": post_id
                }
            }
            
            post_soup = self.get_page(post_id)
            if not post_soup:
                continue
            
            extra_infos = post_soup.find_all('span', class_='mr-2 mb-1')
            c_class = 'relative z-10 text-xl font-light mx-auto leading-8 lg:mx-0 w-full mb-10 md:mb-0 post-content break-words min-h-96'
            
            post_infos['infos']['post_name'] = post_soup.find('span', class_='block xl:inline').text
            post_infos['infos']['content'] = post_soup.find('div', class_=c_class).get_text(separator=' ')
            post_infos['infos']['views'] = extra_infos[0].text
            post_infos['infos']['post_date'] = self.get_date(extra_infos[2].text)
            
            all_posts.append(post_infos)
            
            print(post_infos)       
    
if __name__ == "__main__":
    PasteFree().start()