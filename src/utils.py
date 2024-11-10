import json
import os
import re
import warnings

import pandas as pd
from tqdm import tqdm

warnings.filterwarnings("ignore")


def rename_files_with_underscores():
    """
    Renames audio files replacing spaces with underscores so that they coincide with .TextGrid files, which Praat
    automatically renames in the same way
    """
    for path, subdirs, files in os.walk(
            os.path.join(
                os.getenv('ROOT_PATH', '../misc'),
                os.getenv('AUDIO_TEXTGRID_DIR', 'audio'),
            )
    ):
        for name in files:
            fn = os.path.join(path, name)
            new_fn = re.sub(' ', '_', fn)
            os.rename(fn, new_fn)


def correct_character(
        word: str,
        segment: str,
        target_word: str,
        target_char: str,
        correct_to: str,
        index: int = None,
        verbose: bool = False
):
    """
    Implement spelling corrections
    :param word: str, word to correct
    :param segment: str, segment to correct
    :param target_word: str, target word of correction
    :param target_char: str, target character of correction
    :param correct_to: str, character(s) to replace the target character with
    :param index: str, index of `target_char` in `target_word`, if None, taken to be the index of the first occurrence
    :param verbose: bool
    :return: results of correction
    word: str
    correct_to: str
    """
    if word != target_word or segment not in word:
        return word, segment
    else:
        if index is None:
            if target_word.count(target_char) > 1 and verbose:
                print(f'Warning: word {word} contains more than one instances of char {target_char}.')
                print(f'Defaulting to index == {target_word.index(target_char)}.')
            index = target_word.index(target_char)
        word = list(word)
        word[index] = correct_to
        word = ''.join(word)
        return word, correct_to

# def correct_character(word, segment, target_word, target_char, correct_to, index=None):
#     if word != target_word:
#         return word, segment
#     else:
#         if index is None:
#             if target_word.count(target_char) > 1:
#                 print(f'Warning: word {word} contains more than one instances of char {target_char}.')
#                 print(f'Defaulting to index == {target_word.index(target_char)}.')
#             index = target_word.index(target_char)
#         word = list(word)
#         word[index] = correct_to
#         word = ''.join(word)
#         return word, correct_to


def correct_spelling(data):
    """
    Fix spelling in dataframe
    :param data: pd.DataFrame, has columns ['word', 'segment',]
    :return: pd.DataFrame with corrected data
    """
    with open('assets/replace_rules.json', 'r') as f:
        replace_rules = json.load(f)
    with open('assets/rewrite_rules.json', 'r') as f:
        rewrite_rules = json.load(f)
    with open('assets/replace_char.json', 'r') as f:
        replace_char = json.load(f)

    print('replacing characters')
    for char in tqdm(replace_char):
        data['word'] = data['word'].apply(lambda x: re.sub(
            char['target_char'],
            char['correct_to'],
            x
        ))

    print('applying word replace rules')
    for rule in tqdm(replace_rules):
        data['word'] = data['word'].apply(lambda x: rule['correct_to'] if x == rule['target_word'] else x)

    print('applying vowel rewrite rules')
    for rule in tqdm(rewrite_rules):
        data['word_segment'] = data.apply(lambda x: correct_character(x.word, x.segment, **rule), axis=1)
        data[['word', 'segment']] = data['word_segment'].apply(pd.Series)

    data = data.drop(columns=['word_segment'])
    return data
