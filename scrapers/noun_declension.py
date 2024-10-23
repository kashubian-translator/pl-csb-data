import re
from typing import TextIO, List, Dict

import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from bs4.element import Tag

from scrapers.utils import send_request_with_retries


API_URL = "https://sloworz.org/api/graphql"
POLISH_NOUN_API_URL = "https://odmiana.net/odmiana-przez-przypadki-rzeczownika-"


class PolishNounDeclensionFetcher:
    def __init__(self, noun: str):
        self.noun = noun.strip()
        self.url = f"{POLISH_NOUN_API_URL}{quote(self.noun)}"

    def fetch_declensions(self) -> Dict:
        response = requests.get(self.url)
        if response.status_code != 200:
            print(f"ERROR: Received status code {response.status_code}")
            return {}

        html_content = response.content
        parsed_html = BeautifulSoup(html_content, 'html.parser')
        declension_table = parsed_html.find('table')
        if not declension_table:
            print("ERROR: Failed to find declension table in parsed HTML")
            return {}

        return self._parse_declension_table(declension_table)

    def _parse_declension_table(self, table: Tag) -> Dict:
        declension_dict = {
            "nounVariation": {
                "nominative": "", "genitive": "", "dative": "", "accusative": "",
                "instrumental": "", "locative": "", "vocative": "",
                "nominativePlural": "", "genitivePlural": "", "dativePlural": "",
                "accusativePlural": "", "instrumentalPlural": "", "locativePlural": "",
                "vocativePlural": ""
            }
        }

        case_mapping = {
            "Mianownik": "nominative", "Dopełniacz": "genitive", "Celownik": "dative",
            "Biernik": "accusative", "Narzędnik": "instrumental", "Miejscownik": "locative",
            "Wołacz": "vocative"
        }

        rows = self._get_table_rows_excluding_header(table)
        for row in rows:
            cols = row.find_all('td')
            case_name = cols[0].get_text().split('(')[0].strip()
            singular = cols[1].get_text().strip()
            plural = cols[2].get_text().strip()

            if case_name in case_mapping:
                declension_dict["nounVariation"][case_mapping[case_name]] = singular
                declension_dict["nounVariation"][case_mapping[case_name] + "Plural"] = plural

        return declension_dict

    @staticmethod
    def _get_table_rows_excluding_header(table: Tag) -> Tag:
        return table.find_all("tr")[1:]


class TextNormalizer:
    @staticmethod
    def remove_numbered_parentheses(s: str) -> str:
        return re.sub(r'\s*\(\d+\)\s*', '', s)

    @staticmethod
    def remove_parentheses_content(s: str) -> str:
        return re.sub(r'\(([^)]+)\)', r'\1', s)

    @staticmethod
    def remove_square_brackets_content(s: str) -> str:
        return re.sub(r'\[([^]]+)]', r'\1', s)

    @staticmethod
    def normalize_word(s: str) -> str:
        s = TextNormalizer.remove_numbered_parentheses(s)
        s = TextNormalizer.remove_parentheses_content(s)
        s = TextNormalizer.remove_square_brackets_content(s)
        return s.strip() + '\n'


class KashubianWordProcessor:
    def __init__(self, pl_file: TextIO, csb_file: TextIO, entry: Dict):
        self.pl_file = pl_file
        self.csb_file = csb_file
        self.entry = entry

    def save_words_and_translations(self) -> None:
        if self.entry['partOfSpeech'] != "NOUN":
            return

        word_meanings = self.entry['meanings']
        for word_meaning in word_meanings:
            polish_translations = self._fetch_polish_translations(word_meaning)
            self._process_polish_translations(polish_translations, word_meaning)

    def _fetch_polish_translations(self, word: str) -> List[str]:
        return [part.strip() for part in word['translation']['polish'].split(',')]

    def _process_polish_translations(self, polish_translations: List[str], word_meaning: str) -> None:
        for polish_translation in polish_translations:
            declensions = PolishNounDeclensionFetcher(TextNormalizer.normalize_word(polish_translation)).fetch_declensions()
            self._process_declensions(declensions, word_meaning)

    def _process_declensions(self, declensions: Dict, word_meaning: str) -> None:
        if not declensions:
            return

        noun_variations = self.entry['variation']['nounVariation'].items()
        for declension, word in noun_variations:
            if declension not in ('nominative', 'nominativePlural') and word:
                self._save_translations(declensions, word_meaning, declension)

    def _save_translations(self, declensions: Dict, word_meaning: str, declension: str) -> None:
        for word_variation in self._fetch_variations(word_meaning['translation']['polish']):
            for variation in self._fetch_variation_variations(word_variation):
                self.csb_file.write(TextNormalizer.normalize_word(variation))
                self.pl_file.write(TextNormalizer.normalize_word(declensions['nounVariation'][declension]))

    @staticmethod
    def _fetch_variations(word: str) -> List[str]:
        return [part.strip() for part in word.split('//')]

    @staticmethod
    def _fetch_variation_variations(word: str) -> List[str]:
        return [part.strip() for part in word.split('/')]


class KashubianEntryFetcher:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def fetch_entry(self, entry_id: int) -> Dict:
        query = f"""
        query KashubianEntry {{
            findKashubianEntry(id: {entry_id}) {{
                word
                variation
                meanings {{
                    id(orderBy: ASC)
                    translation {{ polish }}
                }}
                partOfSpeech
            }}
        }}
        """
        response = send_request_with_retries(self.api_url, 'post', json={'query': query})
        return response.json()['data']['findKashubianEntry']

    def fetch_all_entries(self, start: int, limit: int) -> List[Dict]:
        query = f"""
        query AllKashubianEntries {{
            findAllKashubianEntries(page: {{start: {start}, limit: {limit}}}, where: {{normalizedWord: {{BY_NORMALIZED: ""}}}}) {{
                select {{ id normalizedWord(orderBy: ASC) }}
            }}
        }}
        """
        response = send_request_with_retries(self.api_url, 'post', json={'query': query})
        return response.json()['data']['findAllKashubianEntries']['select']


class PhraseFetcher:
    def __init__(self, pl_file: TextIO, csb_file: TextIO):
        self.pl_file = pl_file
        self.csb_file = csb_file
        self.entry_fetcher = KashubianEntryFetcher(API_URL)

    def fetch_and_save_phrases(self, start: int = 0, limit: int = 500) -> None:
        entries = self.entry_fetcher.fetch_all_entries(start, limit)
        while entries:
            for entry in entries:
                word_entry = self.entry_fetcher.fetch_entry(entry['id'])
                processor = KashubianWordProcessor(self.pl_file, self.csb_file, word_entry)
                processor.save_words_and_translations()
            start += 1
            entries = self.entry_fetcher.fetch_all_entries(start, limit)


def main():
    with open("../data/raw/bilingual/declension.pl.txt", "w", encoding="utf-8") as pl_file, \
            open("../data/raw/bilingual/declension.csb.txt", "w", encoding="utf-8") as csb_file:
        fetcher = PhraseFetcher(pl_file, csb_file)
        fetcher.fetch_and_save_phrases()


if __name__ == "__main__":
    main()
