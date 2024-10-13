import requests
from bs4 import BeautifulSoup
import json
from deep_translator import GoogleTranslator

import logging
logging.basicConfig(level=logging.INFO)

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


def main():
    url = "https://www.hse.ru/edu/vkr/?year=2024&program=p135181773%3Bg122468442"
    g = GetData()
    
    # g.get_data(url, "1_raw.json")
    # g.unite_raw_ollama_jsons("1_raw.json", "1_ollama.json", "122.json")


if __name__ == "__main__":
    main()

