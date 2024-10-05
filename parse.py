import requests
from bs4 import BeautifulSoup
import json
from deep_translator import GoogleTranslator

import logging
logging.basicConfig(level=logging.INFO)

handle = "parse"
logger = logging.getLogger(handle)

class GetData:
    folder_path = "data/"
    translator = GoogleTranslator(source='ru', target='en')

    @classmethod
    def get_data(cls, url: str, file_name: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        data = []
        data.extend(cls.extract_data(soup))
        last_page_number = cls.get_last_page_number(soup)
        
        for i in range(2, last_page_number+1):
            logger.info(f"page №{i}")

            new_url = f"{url}&page={i}"
            response = requests.get(new_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            data.extend(cls.extract_data(soup))
        
        cls.save_to_file(data, file_name)


    @staticmethod
    def get_last_page_number(soup: BeautifulSoup):
        return int(soup.find("div", {"class": "letterlist"}).find_all("a")[-1].text.strip())
        

    @classmethod
    def extract_data(cls, soup: BeautifulSoup, translate_flag: bool=True):
        blocks = soup.find_all("li", {"class": "vkr-card vkr-list__item"})
        lst = []

        for i, block in enumerate(blocks):
            logger.info(i)

            topic = block.find("h3").text.strip()
            if translate_flag:
                topic = cls.translator.translate(topic)
            
            tutor = block.find_all("p")[3].find("span").text.strip().split()[0]
            if translate_flag:
                tutor = cls.translator.translate(tutor)
            
            lst.append([topic, tutor]) 
        
        return lst

    @classmethod
    def save_to_file(cls, data: dict, file_name: str):
        with open(f"{cls.folder_path}{file_name}.txt", "w") as outfile:
            for i, (topic, _) in enumerate(data):
                print(f"{i+1}. {topic}", file=outfile)
        
        dct = {"data": {i+1: {"topic": topic, "tutor": tutor} for i, (topic, tutor) in enumerate(data)}}
        outfile = open(f"{cls.folder_path}{file_name}_raw.json", "w")

        json.dump(dct, outfile, indent=4)
    
    @classmethod
    def unite_raw_ollama_jsons(cls, file_name: str):
        infile_raw = open(f"{cls.folder_path}{file_name}_raw.json")
        dct_raw = json.load(infile_raw)

        infile_ollama = open(f"{cls.folder_path}{file_name}_ollama.json")
        dct_ollama = json.load(infile_ollama)

        for k, v in dct_ollama.items():
            dct_raw["data"][k]["topics"] = v
        
        outfile = open(f"{cls.folder_path}{file_name}_united.json", "w")
        json.dump(dct_raw, outfile, indent=4)


# url = "https://www.hse.ru/edu/vkr/?year=2024&program=p135181773%3Bg122468442"
# GetData.get_data(url, "2024")

GetData.unite_raw_ollama_jsons("2024")