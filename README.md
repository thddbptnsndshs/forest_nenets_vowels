# Forest Nenets Vowels, Stress and Monosyllables

Formant and duration data have been processed with [this Praat script](https://github.com/jonorthwash/praat-scripts/blob/master/collect_durations_f0_formants_intensity_and_fields_throughout_vowels.praat).

## Installation

1. Install requirements in a Python venv

`python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

2. Set environment variables

| Variable           | Usage                                                            | type | Default value                                            |
|--------------------|------------------------------------------------------------------|------|----------------------------------------------------------|
| ROOT_PATH          | Root path of the project where inputs and outputs are stored     | str  | `'../misc'`                                              |
| AUDIO_TEXTGRID_DIR | Directory containing audio files                                 | str  | `audio'`                                                 |
| FORMANT_DIR        | Directory containing Praat-extracted formant data in .csv format | str  | `formants'`                                              |
| FONT_PATH          | Path to font to be used in plots                                 | str  | `/System/Library/Fonts/Supplemental/Times New Roman.ttf` |

3. Run FastAPI app on localhost (to run the app on a remote server, change `src/app.py`)

`uvicorn src.app:app`

4. You can request plots and tables. For examples of plot configs, see `plot_configs/`)

Draw a plot:

`curl -X POST --data-binary @plot_configs/stressed_syll.yml -H "Content-Type: text/x-yaml; charset=utf-8" http://0.0.0.0:8000/plot --output images/duration_plot.png`

`curl -X POST --data-binary @plot_configs/OKT_formant_plot.yml -H "Content-Type: text/x-yaml; charset=utf-8" http://0.0.0.0:8000/plot --output images/formant_plot.png`

Draw a LaTeX table: 

`curl -X POST --url http://0.0.0.0:8000/table --header 'Content-Type: application/json; charset=utf-8' --data '{"word": "tŭta", "columns_to_add": ["position"]}'`
