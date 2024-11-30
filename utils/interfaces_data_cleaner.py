import os
import re


def load_irrelevant_phrases(file_path: str) -> list[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def remove_irrelevant_phrases(polish_source_file_path: str, kashubian_source_file_path: str,
                              polish_destination_file_path: str, kashubian_destination_file_pathsearch_phrases: str,
                              search_phrases: list[str], search_in: str) -> None:
    if search_in not in ['polish', 'kashubian', 'both']:
        raise ValueError("search_in parameter must be 'polish', 'kashubian', or 'both'")

    with open(polish_source_file_path, 'r', encoding='utf-8') as polish_source_file, \
            open(kashubian_source_file_path, 'r', encoding='utf-8') as kashubian_source_file:

        polish_lines = polish_source_file.readlines()
        kashubian_lines = kashubian_source_file.readlines()

    with open(polish_destination_file_path, 'w', encoding='utf-8') as polish_destination_file, \
            open(kashubian_destination_file_pathsearch_phrases, 'w', encoding='utf-8') as kashubian_destination_file:

        for polish_line, kashubian_line in zip(polish_lines, kashubian_lines):
            modified_polish_line = polish_line.strip()
            modified_kashubian_line = kashubian_line.strip()

            if search_in in ['polish', 'both']:
                for phrase in search_phrases:
                    modified_polish_line = modified_polish_line.replace(phrase, '').strip()

            if search_in in ['kashubian', 'both']:
                for phrase in search_phrases:
                    modified_kashubian_line = modified_kashubian_line.replace(phrase, '').strip().rstrip('-')

            modified_polish_line = re.sub(r'\s+', ' ', modified_polish_line)
            modified_polish_line = re.sub('\ss\s|^s\s|\ss$', '', modified_polish_line)
            modified_kashubian_line = re.sub(r'\s+', ' ', modified_kashubian_line)
            modified_kashubian_line = re.sub('\ss\s|^s\s|\ss$', '', modified_kashubian_line)

            if not modified_polish_line or not modified_kashubian_line or len(modified_polish_line) < 2 or len(modified_kashubian_line) < 2:
                continue  # Skip empty or one symbol lines

            polish_destination_file.write(modified_polish_line + '\n')
            kashubian_destination_file.write(modified_kashubian_line + '\n')


def remove_duplicated_phrases(polish_file_path: str, kashubian_file_path: str) -> None:
    seen_phrases = set()
    polish_content = []
    kashubian_content = []

    with open(polish_file_path, 'r', encoding='utf-8') as polish_file, \
            open(kashubian_file_path, 'r', encoding='utf-8') as kashubian_file:

        for polish_line, kashubian_line in zip(polish_file, kashubian_file):
            polish_line = polish_line.strip()
            kashubian_line = kashubian_line.strip()

            line_pair = (polish_line, kashubian_line)

            if line_pair not in seen_phrases:
                seen_phrases.add(line_pair)
                polish_content.append(polish_line)
                kashubian_content.append(kashubian_line)

    with open(polish_file_path, 'w', encoding='utf-8') as polish_file, \
            open(kashubian_file_path, 'w', encoding='utf-8') as kashubian_file:
        polish_file.write('\n'.join(polish_content) + '\n')
        kashubian_file.write('\n'.join(kashubian_content) + '\n')


def clean_data() -> None:
    phrases_file = 'phrases_to_remove.txt'
    phrases_to_remove = load_irrelevant_phrases(phrases_file)

    file_names = ['GNOME', 'KDE4', 'Ubuntu']
    for file_name in file_names:
        source_dir = '../data/0_raw/bilingual'
        destination_dir = '../data/1_cleaned'
        polish_file_source_path = f'{source_dir}/{file_name}.pol.txt'
        polish_file_destination_path = f'{destination_dir}/{file_name}.pol.txt'
        kashubian_file_source_path = f'{source_dir}/{file_name}.csb.txt'
        kashubian_file_destination_path = f'{destination_dir}/{file_name}.csb.txt'
        remove_irrelevant_phrases(polish_file_source_path, kashubian_file_source_path, polish_file_destination_path,
                                  kashubian_file_destination_path, phrases_to_remove, 'both')
        remove_duplicated_phrases(polish_file_destination_path, kashubian_file_destination_path)


clean_data()
