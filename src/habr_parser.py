from typing import List
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from models.task import Task
from utils import ru_month_num
from config import HOUR_ADD


class HabrFreelanceParser:
    def __init__(self) -> None:
        self.url = "https://freelance.habr.com"
        self.session = requests.session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
        })

    def get_count_page(self) -> int:
        endpoint = "/tasks"
        page = self._make_request("GET", endpoint)
        soup = BeautifulSoup(page, "html.parser")
        return int(soup.find("div", {"class": "pagination"}).find_all("a")[len(soup.find("div", {"class": "pagination"}).find_all("a")) - 2].text)
    
    def _make_request(self, method: str, endpoint: str) -> str:
        url = f"{self.url}{endpoint}"
        response = requests.request(method, url)
        response.raise_for_status()
        return response.text
    
    def _parse_id(self, li) -> int:
        id = int(re.findall(r"\d+", li.find("a")["href"])[0])
        return id
    
    def _parse_price(self, text) -> int:
        numbers = re.findall(r'\b\d+\b', text)
        if len(numbers) == 0:
            return 0
        extracted_number = "".join(numbers)
        return int(extracted_number)

    def get_task(self, id: int) -> Task:
        endpoint = f"/tasks/{id}"
        page = self._make_request("GET", endpoint)
        soup = BeautifulSoup(page, "html.parser")
        title = soup.find("h2", {"class": "task__title"}).text.strip().replace("\n", " ")
        description = soup.find("div", {"class": "task__description"}).text.strip()
        price = self._parse_price(soup.find("div", {"class": "task__finance"}).text.strip())
        metadata = soup.find("div", {"class": "task__meta"}).text.strip().replace("\n", "").replace("•", "").split()
        day, month, year = int(metadata[0]), ru_month_num[metadata[1]], int(metadata[2][:-1])
        hour, minute = [int(i) for i in metadata[3].split(":")]
        data = datetime(day=day, month=month, year=year, hour=hour, minute=minute) + timedelta(hours=HOUR_ADD)
        responses, views = int(metadata[4]), int(metadata[6])
        link = f"{self.url}{endpoint}"
        task = Task(title=title, description=description, id=id, link=link, views=views, responses=responses, price=price, data=data)
        return task
        
    def get_tasks_ids(self, page: int = 0) -> List[int]:
        endpoint = f"/tasks?page={page}"
        data = self._make_request("GET", endpoint)
        soup = BeautifulSoup(data, "html.parser")
        tasks_ids = []
        for li in soup.find_all("li", {"class": "content-list__item"}):
            id = self._parse_id(li)
            tasks_ids.append(id)
        return tasks_ids
