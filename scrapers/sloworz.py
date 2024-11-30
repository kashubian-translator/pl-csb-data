import re
from scrapers.utils import send_request_with_retries

api_url = "https://sloworz.org/api/graphql"


def process_word(s):
    # Remove any integer within parentheses, including the parentheses
    s = re.sub(r'\s*\(\d+\)\s*', '', s)

    # Remove parentheses but keep the content inside
    s = re.sub(r'\(([^)]+)\)', r'\1', s)

    # Remove square brackets but keep the content inside
    s = re.sub(r'\[([^]]+)]', r'\1', s)

    return s.strip() + '\n'


def find_kashubian_entry(pl_file, csb_file, csb_sentences_file, entry_id):
    find_kashubian_entry_query = \
        f"""
        query KashubianEntry {{
          findKashubianEntry(id: {entry_id})
          {{
            word
            meanings
            {{
              id(orderBy: ASC)
              translation {{
                polish
              }}
              examples {{
                example
              }}
            }}
          }}
        }}
        """
    response = send_request_with_retries(api_url, 'post', json={'query': find_kashubian_entry_query})
    entry = response.json()['data']['findKashubianEntry']
    kashubian_words = [part.strip() for part in entry['word'].split('/')]
    meanings = entry['meanings']
    for meaning in meanings:
        polish_translations = [part.strip() for part in meaning['translation']['polish'].split(',')]
        for word in kashubian_words:
            for translation in polish_translations:
                csb_file.write(process_word(word))
                pl_file.write(process_word(translation))
        examples = meaning['examples']
        for example_json in examples:
            csb_sentences_file.write(f"{example_json['example']}\n")


def find_all_kashubian_entries(pl_file, csb_file, csb_sentences_file, start, limit):
    find_all_kashubian_entries_query = \
        f"""
        query AllKashubianEntries {{
          findAllKashubianEntries(
            page: {{start: {start}, limit: {limit}}}
            where: {{normalizedWord: {{BY_NORMALIZED: ""}}}}
          ) {{
            select {{
              id
              normalizedWord(orderBy: ASC)
            }}
          }}
        }}
        """
    response = send_request_with_retries(api_url, 'post', json={'query': find_all_kashubian_entries_query})
    entries = response.json()['data']['findAllKashubianEntries']['select']
    for entry in entries:
        find_kashubian_entry(pl_file, csb_file, csb_sentences_file, entry['id'])
    return len(entries)


def fetch_and_save_phrases_with_translations(pl_file, csb_file, csb_sentences_file, start=0, limit=500):
    entries_num = find_all_kashubian_entries(pl_file, csb_file, csb_sentences_file, start, limit)
    while entries_num > 0:
        start += 1
        entries_num = find_all_kashubian_entries(pl_file, csb_file, csb_sentences_file, start, limit)


def main():
    pl_file = open("../data/2_cleaned/sloworz.pol.txt", "a")
    csb_file = open("../data/2_cleaned/sloworz.csb.txt", "a")
    csb_sentences_file = open("../data/1_raw/kashubian_only/sloworz.sentences.csb.txt", "a")

    fetch_and_save_phrases_with_translations(pl_file, csb_file, csb_sentences_file)

    pl_file.close()
    csb_file.close()
    csb_sentences_file.close()


main()
