import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

global lista

url = 'https://paste.fo/recent/'
class Paste_fo():
    def __init__(self,href):
        #dict objects
        global lista
        lista['creator'] = {}
        lista['infos'] = {}
        lista['creator']['contacts'] = []
        
        #content request
        res = requests.get(f'https://paste.fo{href}').text
        self.soup = BeautifulSoup(res, 'html.parser')
        
        #Add info to dictonary
        lista['name'] = self.soup.find('h2').text
        lista['content'] = requests.get(f'https://paste.fo/raw{href}').text
        Paste_fo.content_info(self)
        lista['creator']['name'] = Paste_fo.name_taker(self)
        Paste_fo.creator_info(self)
        
        print(f'https://paste.fo{href} concluida')
        
        
    def name_taker(self):
        #User Soup
        name_html = self.soup.find('h3', class_="paste-info larger")
        
        name = name_html.text
        if name != 'Anonymous':
            #User Href
            self.user_href = name_html.find('a')['href']
            
        return name
    
    
    def content_info(self):
        soup = self.soup
        
        #Find info list
        infos = soup.find('div', class_='paste-about').find_all('h4')
        for info in infos[:3]:
            splited = info.text.strip().split(' ')
            
            name = splited[0]
            
            value = ' '.join(splited[1:])
            lista['infos'][name] = value
        
        #Find Date
        date_info = infos[3].text.strip().split(' ')
        time = date_info[2]
        if time != 'now':
            num = int(date_info[1])
        
        date = datetime.now()
        
        if time == 'minutes':
            date = date - timedelta(minutes=num)
        elif time == 'hours':
            date = date - timedelta(hours=num)
        
        lista['infos']['date'] = date
        
     
    def creator_info(self):
        #Creator Name
        name = lista['creator']['name']
        
        if name == 'Anonymous':
            return None
        
        #Creater Account requests
        res = requests.get(f'https://paste.fo/user/{name}')
        soup = BeautifulSoup(res.content, 'html.parser')
        
        #Take infos
        infos = soup.find_all('h4', class_='paste-info')
        for info in infos:
            info_name, num = info.text.strip().split(' ')
            lista['creator'][info_name] = num
        
        #Contacts soup
        contacts_soup = soup.find('div', class_='profilecontact')
        
        #Contacts list
        if contacts_soup:
            contacts_soup = contacts_soup.find_all('h4', class_='profileattribute')
            for contact in contacts_soup:
                if contact.text:
                    lista['creator']['contacts'].append(contact.text.strip())
            
        
scrap = []   
for i in range(1,4):  
    #GET
    response = requests.get(f'{url}{i}')
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find('table', class_='pastelist').find_all('tr')
    
    #Send creator post to class
    for post in posts:
        lista = {}
        if post.get('class'):
            continue
        
        href = post.find('a')['href']
        Paste_fo(href)
        scrap.append(lista)

print('Dados Coletados')
print(scrap)
