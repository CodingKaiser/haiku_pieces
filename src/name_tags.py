import pathlib
from typing import Tuple

import numpy as np
import pandas as pd
from pydantic import BaseModel

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import red
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class NameTagConfig(BaseModel):
    page_paddingX: float = 1 * cm
    page_paddingY: float = 0.8 * cm

    # Width of object itself
    obj_width: float = 4.8 * cm
    obj_height: float = 4.3 * cm

    # Width between two objects
    obj_paddingX: float = 0.5 * cm
    obj_paddingY: float = 0.2 * cm

    page_dim: Tuple[float, float] = landscape(A4)

    font_path: str = './QuicksandBold700.ttf'
    font_name: str = 'Quicksand Bold'
    font_size: int = 20


def get_heart_coords():
    t = np.linspace(0, 2 * np.pi, 1000)
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)

    # Move origin to lower left corner
    x -= min(x)
    y -= min(y)

    # Scale to width of 1
    x *= 1 / max(x)
    y *= 1 / max(y)

    return x, y


def grid_on_page(width: float, height: float, page_dim: Tuple[float, float]):
    """ Calculate maximal number of rows and columns on a given page """

    page_width, page_height = page_dim

    rows = int(page_height / height)
    cols = int(page_width / width)

    return rows, cols


def generte_name_tags(df: pd.DataFrame, output_file: pathlib.Path, conf: NameTagConfig):

    # Calculate number of rows and cols per page
    rows, cols = grid_on_page(width=(conf.obj_width + conf.obj_paddingX),
                              height=(conf.obj_height + conf.obj_paddingY),
                              page_dim=conf.page_dim)

    # Get base format of heart
    x, y = get_heart_coords()

    can = canvas.Canvas(str(output_file.absolute()), pagesize=conf.page_dim)
    can.setStrokeColor(red)

    for index, (lastname, firstname) in df.iterrows():

        # Calculate grid position on page
        col = index % cols
        row = (index % (rows * cols)) // cols

        print(f'Index: {index}, row: {row}, col: {col}')

        pdfmetrics.registerFont(TTFont(conf.font_name, conf.font_path))

        offsetX = conf.page_paddingX + (conf.obj_width + conf.obj_paddingX) * col
        offsetY = conf.page_paddingY + (conf.obj_height + conf.obj_paddingY) * row

        # Calculate current offset
        current_x = x * conf.obj_width + offsetX
        current_y = y * conf.obj_height + offsetY

        # Convert coordinates into a tuples with (x1, y1, x2, y2), ...
        linelist = [(current_x[i], current_y[i], current_x[i + 1],
                     current_y[i + 1]) for i in range(len(x) - 1)]

        # Draw heart shape
        can.lines(linelist)

        # Configure font
        font_size = 18 if len(firstname) > 11 else 22
        can.setFont(conf.font_name, font_size)

        # Calculate width of text
        text_width = pdfmetrics.stringWidth(firstname, conf.font_name, font_size)

        # Add text horizontally centered
        can.drawString((offsetX + conf.obj_width / 2) - text_width / 2, (offsetY + 2.5 * cm),
                       firstname)

        if index > 0 and (index + 1) % (cols * rows) == 0:
            print('Next page')
            can.showPage()
            can.setStrokeColor(red)

    can.save()
    print(f'Processed {index} elements')
    return index + 1


if __name__ == '__main__':

    c = NameTagConfig()

    df = pd.read_csv('guestlist.csv', delimiter=';')
    df = df.loc[:, ['Nachname', 'Vorname']]

    output_file = pathlib.Path('./test').with_suffix('.pdf')

    generte_name_tags(df, output_file=output_file, conf=c)
