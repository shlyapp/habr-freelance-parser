from typing import List
import requests
import re
from bs4 import BeautifulSoup

from models.task import Task

class HabrFreelanceParser:
    def __init__(self) -> None:
        self.url = "https://freelance.habr.com"
        self.session = requests.session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
        })

    def _get_count_page(self, soup) -> int:
        return int(soup.find("div", {"class": "pagination"}).find_all("a")[len(soup.find("div", {"class": "pagination"}).find_all("a")) - 2].text)
    
    def _make_request(self, method: str, endpoint: str) -> str:
        url = f"{self.url}{endpoint}"
        response = requests.request(method, url)
        response.raise_for_status()
        return response.text
    
    def _parse_title(self, li) -> str:
        title = li.find("div", {"class": "task__title"}).text.strip()
        return title

    def _parse_id(self, li) -> int:
        id = int(re.findall(r"\d+", li.find("a")["href"])[0])
        return id

    def _parse_link(self, li) -> str:
        task_link = li.find("a")["href"]
        link = f"{self.url}{task_link}" 
        return link

    def _parse_views(self, li) -> int:
        views = 0
        if li.find('span', class_='params__views'):
            views = li.find('span', class_='params__views').find('i').text
        return views

    def _parse_responses(self, li) -> int:
        responses = 0
        if li.find('span', class_='params__responses'):
            responses = li.find('span', class_='params__responses').find('i').text
        return responses
    
    def _parse_price(self, li) -> int:
        price = li.find('span', class_='count')
        if price:
            price = price.get_text(strip=True)
            numbers = re.findall(r'\b\d+\b', price)
            extracted_number = "".join(numbers)
            return int(extracted_number)
        return 0

    def _parse_tags(self, li):
        tag_elements = li.find('ul', class_='tags tags_short').find_all('a', class_='tags__item_link')
        tags = [tag.get_text().replace("\u200b", "") for tag in tag_elements]
        return tags    

    def get_tasks(self, page: int = 0) -> List[Task]:
        endpoint = f"/tasks?page={page}"
        data = self._make_request("GET", endpoint)
        soup = BeautifulSoup(data, "html.parser")
        tasks = []
        for li in soup.find_all("li", {"class": "content-list__item"}):
            task = Task(
                title=self._parse_title(li),
                id=self._parse_id(li),
                link=self._parse_link(li),
                views=self._parse_views(li),
                responses=self._parse_responses(li),
                price=self._parse_price(li),
                tags=self._parse_tags(li)
            )
            tasks.append(task)
        return tasks
