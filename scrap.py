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

class PasteFo:
    def __init__(self):
        self.url_base = "https://paste.fo"
        self.logger = logger()

    def get_recent_page_posts(self, page_number: int | str) -> list[BeautifulSoup]:
        page = requests.get(f"{self.url_base}/recent/{page_number}")

        if page.status_code != 200:
            return None

        soup = BeautifulSoup(page.text, 'html.parser')

        posts = soup.find('table', {"class": "pastelist"}).find_all('tr')
        return posts

    def get_page(self, page_id: str) -> BeautifulSoup | None:
        page = requests.get(f"{self.url_base}/{page_id}")

        if page.status_code == 200:
            return BeautifulSoup(page.content, 'html.parser')

    def get_aditional_infos(self, page_soup: BeautifulSoup) -> dict[str, str | int]:
        infos = [x.text.strip().split(' ') for x in page_soup.find('div', class_='paste-about').find_all('h4')]

        aditional_infos = {}
        for info in infos[:3]:
            aditional_infos[info[0]] = ' '.join(info[1:])

        return aditional_infos

    def get_post_date(self, page_soup: BeautifulSoup) -> datetime:
        time_infos = page_soup.find('div', class_='paste-about').find_all('h4')[3].text.strip().split(' ')

        _time = time_infos[1]
        time_prefix = time_infos[2]

        date_now  = datetime.now()

        if time_prefix == 'now':
            return date_now

        time_ago = int(_time)

        time_units =  {
            "minute": timedelta(minutes=time_ago),
            "hour": timedelta(hours=time_ago),
            "day": timedelta(days=time_ago)
        }

        for time_unit, _timedelta in time_units.items():
            if time_unit in time_prefix.lower():
                return date_now - _timedelta

    def get_creator_infos(self, page_soup: BeautifulSoup) -> dict[str, str | int]:
        creator_name = page_soup.find('h3', {"class": "paste-info larger"})

        if creator_name.text == 'Anonymous':
            return {
                "name": "Anonymous"
            }

        creator_id = creator_name.find('a')['href']
        creator_profile = requests.get(f'https://paste.fo/{creator_id}')
        creator_soup = BeautifulSoup(creator_profile.content, 'html.parser')

        creator_infos = {
            "name": creator_id.split("/")[-1],
            "profile": f"https://paste.fo/{creator_id}",
            "contacts": []
        }

        infos = creator_soup.find_all('h4', class_='paste-info')
        for info in infos:
            info_name, num = info.text.strip().split(' ')
            creator_infos[info_name] = num

        contacts_soup = creator_soup.find('div', class_='profilecontact')

        if contacts_soup:
            for contact in contacts_soup.find_all('h4', class_='profileattribute'):
                if contact.text:
                    creator_infos['contacts'].append(contact.text.strip())

        return creator_infos

    def start(self):
        all_posts = []

        self.logger.info("Inciando coleta...")

        for page_number in range(1,4):
            self.logger.info(f"Coletando página {page_number}")

            posts = self.get_recent_page_posts(page_number)

            if not posts:
                self.logger.debug(f"Não foi possível coletar página {1}")
                continue

            for post in posts:
                if post.get("class"):
                    continue

                post_id = post.find('a')['href'].replace("/", "")
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

                post_infos["infos"]["post_name"] = post_soup.find("h2").text.strip().rstrip()
                post_infos["infos"]["raw_code"] = post_soup.find("textarea", {"name": "content"}).text
                post_infos["infos"]["aditional_infos"] = self.get_aditional_infos(post_soup)
                post_infos["infos"]["post_date"] = self.get_post_date(post_soup)
                post_infos["infos"]["creator"] = self.get_creator_infos(post_soup)
                all_posts.append(post_infos)
                print(post_infos)

if __name__ == "__main__":
    PasteFo().start()
