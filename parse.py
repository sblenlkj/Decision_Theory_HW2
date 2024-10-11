import requests
from bs4 import BeautifulSoup
import json
from deep_translator import GoogleTranslator

import logging
logging.basicConfig(level=logging.INFO)

import hashlib
from collections import defaultdict, Counter
from itertools import combinations

class Connection:
    def __init__(self, a, b):
        self.a, self.b = sorted([a, b])
    
    def __repr__(self) -> str:
        return f"Connection({self.a}, {self.b})"
    
    def __eq__(self, value: object) -> bool:
        return self.a == value.a and self.b == value.b
    
    def __hash__(self) -> int:
        return self.hash_function(self.b + self.a)
    
    def to_list(self) -> list:
        return [self.a, self.b]
    
    def hash_function(self, s):
        return int(hashlib.sha1(s.encode("utf-8")).hexdigest(), 16) % (10 ** 8)

class GetData:
    folder_path = "data/"
    translator = GoogleTranslator(source='ru', target='en')
    logger = logging.getLogger("parse")

    
    def get_data(self, url: str, file_name: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        data = []
        data.extend(self.extract_data(soup))
        last_page_number = self.get_last_page_number(soup)
        
        for i in range(2, last_page_number+1):
            self.logger.info(f"page №{i}")

            new_url = f"{url}&page={i}"
            response = requests.get(new_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            data.extend(self.extract_data(soup))
        
        self.save_to_file(data, file_name)


    @staticmethod
    def get_last_page_number(soup: BeautifulSoup):
        return int(soup.find("div", {"class": "letterlist"}).find_all("a")[-1].text.strip())
        

    def extract_data(self, soup: BeautifulSoup, translate_flag: bool=True):
        blocks = soup.find_all("li", {"class": "vkr-card vkr-list__item"})
        lst = []

        for i, block in enumerate(blocks):
            self.logger.info(i)

            topic = block.find("h3").text.strip()
            if translate_flag:
                topic = self.translator.translate(topic)
            
            tutor = block.find_all("p")[3].find("span").text.strip().split()[0]
            if translate_flag:
                tutor = self.translator.translate(tutor)
            
            lst.append([topic, tutor]) 
        
        return lst

    def save_to_file(self, data: dict, file_name: str):
        with open(f"{self.folder_path}for_ollama.txt", "w") as outfile:
            for i, (topic, _) in enumerate(data):
                print(f"{i+1}. {topic}", file=outfile)
        
        dct = {"data": {i+1: {"topic": topic, "tutor": tutor} for i, (topic, tutor) in enumerate(data)}}
        outfile = open(f"{self.folder_path}{file_name}", "w")

        json.dump(dct, outfile, indent=4)
    

    def unite_raw_ollama_jsons(self, parse_file_name: str, ollama_file_name: str, united_file_name: str):
        infile_raw = open(f"{self.folder_path}{parse_file_name}")
        dct_raw = json.load(infile_raw)

        infile_ollama = open(f"{self.folder_path}{ollama_file_name}")
        dct_ollama = json.load(infile_ollama)

        for k, v in dct_ollama.items():
            dct_raw["data"][k].update(v)
        
        outfile = open(f"{self.folder_path}{united_file_name}", "w")
        json.dump(dct_raw, outfile, indent=4)
    
    def process_json(self, file_name: str) -> None:
        infile = open(f"{self.folder_path}{file_name}")
        dct = json.load(infile)
        
        nodes_dct = defaultdict(list)
        connections_lst = []
        
        
        for v in dct["data"].values():
            nodes = []
            nodes_dct["tutors"].append(v["tutor"])
            nodes.append(v["tutor"])

            nodes_dct["countries"].extend(v["countries"])
            nodes.extend(v["countries"])

            nodes_dct["topics"].extend(v["topics"])
            nodes.extend(v["topics"])

            connections_lst.extend([Connection(t[0], t[1]) for t in combinations(nodes, 2)])
        
        for k, v in nodes_dct.items():
            nodes_dct[k] = list(map(lambda x: [x[0], x[1]], sorted(Counter(v).items())))
        
        dct["nodes"] = nodes_dct
        dct["connections"] = [{"times": v, "nodes": c.to_list()} for c, v in Counter(connections_lst).items()]


        outfile = open(f"{self.folder_path}{file_name.strip(".json")}_processed.json", "w")
        json.dump(dct, outfile, indent=4)

def main():
    url, file_name = "https://www.hse.ru/edu/vkr/?year=2024&program=p135181773%3Bg122468442", "2024"
    g = GetData(file_name)
    
    # g.get_data(url)
    # g.unite_raw_ollama_jsons()
    g.process_final_json()


if __name__ == "__main__":
    main()

