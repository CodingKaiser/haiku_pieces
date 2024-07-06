import pathlib
from typing import List, Tuple, Hashable, Iterable

import numpy as np
import pandas as pd
from pandas import Series
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import red, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class HaikuPuzzleConfig(BaseModel):
    page_paddingX: float = 1 * cm
    page_paddingY: float = 0.8 * cm

    # Width of object itself
    obj_width: float = 7.0 * cm  # Increased width to fit the text
    obj_height: float = 2.5 * cm  # Reduced height

    # Width between two objects
    obj_paddingX: float = 0.5 * cm
    obj_paddingY: float = 0.2 * cm

    page_dim: Tuple[float, float] = landscape(A4)

    font_path: str = './QuicksandBold700.ttf'
    font_name: str = 'Quicksand Bold'
    font_size: int = 16  # Reduced font size


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


def generate_haiku_puzzles(haikus: Iterable[Tuple[Hashable, Series]], output_file: pathlib.Path, conf: HaikuPuzzleConfig):
    # Calculate number of rows and cols per page
    rows, cols = grid_on_page(width=(conf.obj_width * 3 + conf.obj_paddingX * 2),
                              height=(conf.obj_height + conf.obj_paddingY),
                              page_dim=conf.page_dim)

    can = canvas.Canvas(str(output_file.absolute()), pagesize=conf.page_dim)
    can.setStrokeColor(black)

    # Get base format of heart
    heart_x, heart_y = get_heart_coords()

    for index, haiku in haikus:

        # Calculate grid position on page
        col = (index * 3) % cols
        row = ((index * 3) % (rows * cols)) // cols

        if col + 3 > cols:
            col = 0
            row += 1

        offsetX = conf.page_paddingX + (conf.obj_width * 3 + conf.obj_paddingX * 2) * col
        offsetY = conf.page_paddingY + (conf.obj_height + conf.obj_paddingY) * row

        # Draw three rectangles with connecting hearts
        for i in range(3):
            x0 = offsetX + (conf.obj_width + conf.obj_paddingX) * i
            y0 = offsetY
            x1 = x0 + conf.obj_width
            y1 = y0 + conf.obj_height
            can.rect(x0, y0, conf.obj_width, conf.obj_height)

            if i < 2:
                # Draw heart
                heart_center_x = x1 - conf.obj_paddingX / 2
                heart_center_y = y0 + conf.obj_height / 2
                heart_scale_x = conf.obj_paddingX / 2
                heart_scale_y = conf.obj_height / 2

                heart_coords = [(heart_center_x + heart_scale_x * hx, heart_center_y + heart_scale_y * hy) for hx, hy in zip(heart_x, heart_y)]
                linelist = [(heart_coords[j][0], heart_coords[j][1], heart_coords[j + 1][0], heart_coords[j + 1][1]) for j in range(len(heart_coords) - 1)]

                can.lines(linelist)

        pdfmetrics.registerFont(TTFont(conf.font_name, conf.font_path))
        can.setFont(conf.font_name, conf.font_size)

        # Draw haiku lines
        for i, line in enumerate(haiku):
            x = offsetX + (conf.obj_width + conf.obj_paddingX) * i + conf.obj_width / 2
            y = offsetY + conf.obj_height / 2
            text_width = pdfmetrics.stringWidth(line, conf.font_name, conf.font_size)
            can.drawString(x - text_width / 2, y - conf.font_size / 2, line)

        if (index + 1) % (rows * cols // 3) == 0:
            can.showPage()
            can.setStrokeColor(black)

    can.save()
    print(f'Processed {index + 1} haikus')
    return index + 1


if __name__ == '__main__':
    c = HaikuPuzzleConfig()

    df = pd.read_csv('haikus_input.csv', delimiter=';')
    haikus = df.iterrows()

    output_file = pathlib.Path('./haiku_puzzles').with_suffix('.pdf')

    generate_haiku_puzzles(haikus, output_file=output_file, conf=c)
