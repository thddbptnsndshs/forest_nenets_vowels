import os
import warnings

import yaml

warnings.filterwarnings("ignore")

from fastapi import FastAPI, Response, Request
from src.plot import FNPlots
from src.parser import FNProcessor
import matplotlib.pyplot as plt
import io
from pydantic import BaseModel
import uvicorn
from typing import List

app = FastAPI()
parser = FNProcessor()
data = parser.preprocess_data('output_20240820.csv')
plotter = FNPlots(data)


class TableRequest(BaseModel):
    word: str
    round_factor: int = 5
    columns_to_add: List[str] = None


@app.post("/plot", response_class=Response)
async def plot(request: Request):
    """
    Draw a .png plot from .yaml config
    :param request: user request with a .yaml config
    :return: Response with either a .png file or an error message
    """
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
    """
    Create a LaTeX duration mean+std table in plain text from user request
    :param request: TableRequest with fields word, round_factor and columns_to_add
    :return: Response in plain text
    """
    return Response(content=plotter.get_word_duration_table(
        request.word,
        request.round_factor,
        request.columns_to_add,
    ), media_type="text/plain")


@app.get("/health", response_class=Response)
async def health():
    """
    :return: Response in plain text
    """
    health_response = f"""Data root directory: {os.getenv('ROOT_PATH')}
Audio dir: {os.getenv('AUDIO_TEXTGRID_DIR')}
Formant dir: {os.getenv('FORMANT_DIR')}
Got processed data of shape {data.shape}"""
    return Response(content=health_response, media_type="text/plain", status_code=200)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
