# Forest Nenets Vowels, Stress and Monosyllables

Formant and duration data have been processed with [this Praat script](https://github.com/jonorthwash/praat-scripts/blob/master/collect_durations_f0_formants_intensity_and_fields_throughout_vowels.praat).

## Environment variables

| Variable           | Usage                                                            | type | Default value                                            |
|--------------------|------------------------------------------------------------------|------|----------------------------------------------------------|
| ROOT_PATH          | Root path of the project where inputs and outputs are stored     | str  | `'../misc'`                                              |
| AUDIO_TEXTGRID_DIR | Directory containing audio files                                 | str  | `audio'`                                                 |
| FORMANT_DIR        | Directory containing Praat-extracted formant data in .csv format | str  | `formants'`                                              |
| FONT_PATH          | Path to font to be used in plots                                 | str  | `/System/Library/Fonts/Supplemental/Times New Roman.ttf` |

curl -X POST --data-binary @plot_configs/stressed_syll.yml -H "Content-Type: text/x-yaml" http://0.0.0.0:8000/plot 

curl -X POST --url http://0.0.0.0:8000/table --header 'Content-Type: application/json' --data '{"word": "kata", "columns_to_add": ["position"]}'