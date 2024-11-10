import os
import warnings

import numpy as np
import pandas as pd

from src.utils import correct_spelling

warnings.filterwarnings("ignore")


class FNProcessor:

    def __init__(self):
        self.vowels = 'aeoiuæăĕŏĭŭ°æy'
        self.vowels_long = 'aeoiuæ'
        self.vowels_short = 'ăĕŏĭŭ°æ̆'
        self.consonants = 'mḿnńŋŋ́pṕtčkʔʰsšxx́λlwẃjdbcfghqrv'
        self.orig2pal = {
            'ḿ': 'M',
            'ŋ́': 'G',
            'ṕ': 'P',
            'kˊ': 'K',
            'dʹ': 'D',
            'lˊ': 'L',
            'λ´': 'F',
            'x́': 'X',
            'ẃ': 'W',
        }
        self.pal2orig = dict(zip(self.orig2pal.values(), self.orig2pal.keys()))

    def parse_syllables(
            self,
            word: str
    ):
        """
        Parses a word into syllables; supposes that all syllables are of shape CV, CVV, CVC, CVVC
        :param word: str, word spelled with FN practical transcription
        :return: list of (syllable, structure) tuples
        """
        if word[0] in self.vowels:
            word = 'ʔ' + word  # no vowel-initial words
        cv_mask = ''
        one2one_parse = ''

        for rep in self.orig2pal:
            word = word.replace(rep, self.orig2pal[rep])

        # create a CV-mask
        for seg in word:
            if seg in self.orig2pal.values() or seg in ['š', 'č', 'ń', 'j']:
                cv_mask += 'c'
            elif seg in self.consonants:
                cv_mask += 'C'
            elif seg in self.vowels_short:
                cv_mask += 'v'
            elif seg in self.vowels_long:
                cv_mask += 'V'
            one2one_parse += seg

        # split into syllables
        nucleus = False
        syllables = list()
        syll, seg_syll = '', ''
        for slot, seg in zip(cv_mask[::-1], one2one_parse[::-1]):
            syll += slot.replace('V', 'VV').replace('v', 'V')

            if seg in self.pal2orig:
                seg = self.pal2orig[seg]

            seg_syll += seg
            if slot in ['c', 'C']:
                if nucleus:
                    syllables.append((syll[::-1], seg_syll[::-1]))
                    syll, seg_syll = '', ''
                    nucleus = False
            else:
                nucleus = True
        return syllables[::-1]

    @staticmethod
    def get_context(
            syllables,
            idx,
            vowel,
            target_syll,
            target_idx,
    ):
        """
        Computes several context characteristics for each vowel in the word parsed into syllables beforehand.

        :param syllables: List[str], list of (structure, syllable) pairs
        :param idx: int, index of the word in the dataframe
        :param vowel: str, vowel
        :param target_syll: str, syllable structure
        :param target_idx: int, index of syllable in the `syllables` list
        :return: tuple of context characteristics

        syllable_structure: syllable structure (CV, CVV, CVC, or CVVC)
        syllable_count: monosyllable/polysyllabic
        position: initial, medial, final
        stress: stressed/unstressed according to the rule --- stress falls on odd-numbered non-final syllables
        vowel: high (/i ĭ u ŭ/), mid (/e o ĕ ŏ æ æ̆/), low (/a ă/)
        pre_schwa: yes/no
        palatalization: left for CjVC, right for CVCj, double for CjVCj, none for CVC (Cj = palatalized C)
        """
        if target_syll is None:
            return '', '', '', '', '', '', ''

        if target_syll.startswith('c'):
            if target_syll.endswith('c'):
                palatalization = 'double'
            else:
                palatalization = 'left'
        else:
            if target_syll.endswith('c'):
                palatalization = 'right'
            else:
                palatalization = 'none'

        syllable_structure = target_syll.replace('c', 'C')
        syllable_count = 'monosyllable' if len(syllables) == 1 else 'polysyllabic'

        if syllable_count == 'monosyllable':
            position = 'final'
        else:
            if target_idx == 0:
                position = 'initial'
            elif target_idx == len(syllables) - 1:
                position = 'final'
            else:
                position = 'medial'

        stress = 'stressed' if idx % 2 == 0 and (
                    position != 'final' or syllable_count == 'monosyllable') else 'unstressed'
        if vowel in 'aă':
            vowel = 'low'
        elif vowel in 'uŭiĭ':
            vowel = 'high'
        elif vowel in 'eĕoŏææ̆':
            vowel = 'mid'

        if position != 'final':
            if '°' in syllables[target_idx + 1][1]:
                pre_schwa = 'yes'
            else:
                pre_schwa = 'no'
        else:
            pre_schwa = 'no'

        return syllable_structure, syllable_count, position, stress, vowel, pre_schwa, palatalization

    def determine_contexts(self, syllables, vowels, indices):
        """
        Get the first occurrence of vowel and return the context characteristics
        :param syllables: List[List[str, str]], list of (structure, syllable) pairs
        :param vowels: List[str], list of vowels
        :param indices: List[int], indeces of words
        :return: list of [vowel, index, tuples of context characteristics]
        syllable_structure: syllable structure (CV, CVV, CVC, or CVVC)
        syllable_count: monosyllable/polysyllabic
        position: initial, medial, final
        stress: stressed/unstressed according to the rule --- stress falls on odd-numbered non-final syllables
        vowel: high (/i ĭ u ŭ/), mid (/e o ĕ ŏ æ æ̆/), low (/a ă/)
        pre_schwa: yes/no
        palatalization: left for CjVC, right for CVCj, double for CjVCj, none for CVC (Cj = palatalized C)
        """
        out = list()

        while len(vowels) > 0:
            for idx, (syll, seg_syll) in enumerate(syllables):
                for i, vowel in enumerate(vowels):
                    if vowel not in ''.join([s[1] for s in syllables]):
                        vowels.pop(i)
                        indices.pop(i)
                    if vowel in seg_syll:
                        target_syll, target_seg_syll = syll, seg_syll
                        target_idx = idx
                        out.append(
                            [vowel,
                             indices[i],
                             self.get_context(syllables, idx, vowel, target_syll, target_idx)]
                        )
                        vowels.pop(i)
                        indices.pop(i)
                        break
        return out

    def preprocess_data(self, filename: str):
        """
        Load .csv dataset, extract and preprocess the data
        :param filename: str, path to input file
        :return: pd.DataFrame with preprocessed data
        """
        df = pd.read_csv(
                os.path.join(
                    os.getenv('ROOT_PATH', '../misc'),
                    os.getenv('FORMANT_PATH', 'formants'),
                    filename,
                ), delimiter='\t')
        # average the formant measures
        for col in ['f0', 'f1', 'f2', 'f3']:
            df[col.upper()] = df[col].apply(lambda x: np.array([float(val) for val in x[2:-1].split(',')]).mean())
        # leave out unneeded columns
        df = df[['filename', 'word', 'segment', 'vowelIntervalNum', 'wordIntervalNum',
                 'duration', 'f0max', 'f0min', 'intensity', 'intensity_max', 'F0', 'F1', 'F2', 'F3']]
        # drop lines with no words
        df = df.dropna(subset='word')
        # some intervals on word level have multiple orthographic words in one --- split them and explode
        df['word'] = df['word'].apply(lambda x: x.split())
        df = df.explode('word').reset_index(drop=True)
        # correct graphically vowel-initial words so that they all have an onset
        df['word'] = df['word'].apply(lambda x: 'ʔ' + x if x[0] in self.vowels else x)
        # get consultant IDs from filenames
        df['consultant'] = df['filename'].apply(lambda x: x.split('_')[-1])

        # group segments by words in each filename
        mrg_df_grouped = pd.DataFrame(
            df.groupby(['filename', 'word',])['segment'].apply(lambda x: list(x))).reset_index()
        # assign indeces to all words in each filename
        mrg_df_grouped['indeces'] = df.reset_index().groupby(['filename', 'word'])['index'] \
            .apply(lambda x: list(x)).values
        # apply parsing functions to the dataframe
        res = []
        for idx, row in mrg_df_grouped.iterrows():
            res.append(
                self.determine_contexts(
                    self.parse_syllables(
                        row.word
                    ), row.segment, row.indeces
                )
            )
        # dump the result into a column in the dataframe
        mrg_df_grouped['out'] = res
        mrg_df_grouped_expl = mrg_df_grouped.explode(['out'])
        mrg_df_grouped_expl[['segment', 'indeces', 'context',]] = mrg_df_grouped_expl['out'].apply(pd.Series).values
        mrg_df_grouped_expl[[
             'syllable_structure',
             'syllable_count',
             'position',
             'stress',
             'vowel',
             'pre_schwa',
             'palatalization',
        ]] = mrg_df_grouped_expl['context'].apply(pd.Series).values
        mrg_df_grouped_expl = mrg_df_grouped_expl.drop(columns=['out', 'context'])
        df = mrg_df_grouped_expl.merge(df, left_on='indeces', right_index=True, suffixes=('', '_DROP'))
        df = df.drop(columns=list(filter(lambda x: '_DROP' in x, df.columns)))
        # remove parsing errors
        df = df.loc[~df['syllable_structure'].isin(['CVCC', 'CVCC', 'CVVCCC'])]
        return correct_spelling(df)
