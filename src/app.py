import os
import warnings

import yaml

warnings.filterwarnings("ignore")

from fastapi import FastAPI, Response, Request
from argparse import ArgumentParser
from src.plot import FNPlots
from src.parser import FNProcessor
import matplotlib.pyplot as plt
import io
from pydantic import BaseModel
import uvicorn
from typing import List

app = FastAPI()
parser = FNProcessor()
# argparser = ArgumentParser()
#
# argparser.add_argument('-f', '--filename', type=str, default='output_20240820.csv')
# args = argparser.parse_args()
data = parser.preprocess_data('output_20240820.csv')
plotter = FNPlots(data)


class TableRequest(BaseModel):
    word: str
    round_factor: int = 5
    columns_to_add: List[str] = None


@app.post("/plot", response_class=Response)
async def plot(request: Request):
    raw_body = await request.body()
    try:
        config = yaml.safe_load(raw_body)
    except yaml.YAMLError:
        return Response(content="Invalid YAML", media_type="text/plain", status_code=422)

    if config['kind'] == 'duration':
        plotter.duration_plot(**config)
    elif config['kind'] == 'formant':
        plotter.formant_plot(**config)
    else:
        return Response(content="Unknown plot kind", media_type="text/plain", status_code=422)

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Return the image
    return Response(content=buf.read(), media_type="image/png")


@app.post("/table", response_class=Response)
async def table(request: TableRequest):
    return Response(content=plotter.get_word_duration_table(
        request.word,
        request.round_factor,
        request.columns_to_add,
    ), media_type="text/plain")


@app.get("/health", response_class=Response)
async def health():
    health_response = f"""Data root directory: {os.getenv('ROOT_PATH')}
Audio dir: {os.getenv('AUDIO_TEXTGRID_DIR')}
Formant dir: {os.getenv('FORMANT_DIR')}
Got processed data of shape {data.shape}"""
    return Response(content=health_response, media_type="text/plain", status_code=200)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
