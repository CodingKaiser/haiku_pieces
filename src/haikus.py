import pathlib
from typing import Tuple

import numpy as np
import pandas as pd
from pydantic import BaseModel

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import red, blue, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class HaikuTagConfig(BaseModel):
    page_paddingX: float = 1 * cm
    page_paddingY: float = 0.8 * cm

    # Width of object itself
    obj_width: float = 6 * cm
    obj_height: float = 6 * cm

    # Width between two objects
    obj_paddingX: float = 0.5 * cm
    obj_paddingY: float = 0.2 * cm

    page_dim: Tuple[float, float] = landscape(A4)

    font_path: str = './QuicksandBold700.ttf'
    font_name: str = 'Quicksand Bold'
    font_size: int = 20


def draw_puzzle_piece(c, x, y, size):
    corner_radius = size * 0.1  # Adjust this for the desired roundness of the corners

    # Coordinates for the puzzle piece
    path = c.beginPath()
    path.moveTo(x + corner_radius, y)  # Starting point
    path.lineTo(x + size - corner_radius, y)
    path.arc(x + size - 2 * corner_radius, y - 2 * corner_radius, x + size, y, startAng=90, extent=-90)
    path.lineTo(x + size,
                y - size + corner_radius)
    path.arc(x + size,
             y - size + 2 * corner_radius,
             x + size - 2 * corner_radius,
             y - size, startAng=0, extent=-90)
    path.lineTo(x + corner_radius, y - size)
    path.arc(x,
             y - size,
             x + 2 * corner_radius,
             y - size + 2 * corner_radius,
             startAng=-90,
             extent=-90)
    path.lineTo(x, y - corner_radius)
    path.arc(x,
             y,
             x + 2 * corner_radius,
             y - 2 * corner_radius,
             startAng=180,
             extent=-90)
    # now we move to draw the inside of the puzzle, so we move to the middle the top side of the piece
    path.moveTo(x + 0.5 * size, y)
    path.lineTo(x + 0.5 * size, y - size * 0.25)
    # now draw a jigsaw type connection using path.arc
    path.arc(x + size * 0.474, y - size * 0.242, x + size * 0.58, y - size * 0.36, startAng=120, extent=-240)
    # now move to the middle of the inside of the piece
    path.lineTo(x + 0.5 * size, y - size * 0.5)
    # now move to the middle right half of the piece
    path.moveTo(x + size, y - size * 0.5)
    path.lineTo(x + size * 0.8, y - size * 0.5)
    path.arc(x + size * 0.81, y - size * 0.474, x + size * 0.69, y - size * 0.58, startAng=30, extent=-240)
    path.lineTo(x + 0.5 * size, y - size * 0.5)
    path.moveTo(x + 0.5 * size, y - size)
    path.lineTo(x + 0.5 * size, y - size * 0.8)
    path.arc(x + size * 0.529, y - size * 0.81, x + size * 0.42, y - size * 0.69, startAng=300, extent=-240)
    path.lineTo(x + 0.5 * size, y - size * 0.5)
    path.moveTo(x, y - 0.5 * size)
    path.lineTo(x + size * 0.18, y - 0.5 * size)
    path.arc(x + size * 0.17, y - size * 0.529, x + size * 0.30, y - size * 0.42, startAng=210, extent=-240)
    path.lineTo(x + 0.5 * size, y - size * 0.5)

    c.drawPath(path, stroke=1, fill=0)


def grid_on_page(width: float, height: float, page_dim: Tuple[float, float]):
    """ Calculate maximal number of rows and columns on a given page """
    page_width, page_height = page_dim

    rows = int(page_height / height)
    cols = int(page_width / width)

    return rows, cols


def generate_haiku_tags(df: pd.DataFrame, output_file: pathlib.Path, conf: HaikuTagConfig):

    # Calculate number of rows and cols per page
    rows, cols = grid_on_page(width=(conf.obj_width + conf.obj_paddingX),
                              height=(conf.obj_height + conf.obj_paddingY),
                              page_dim=conf.page_dim)

    can = canvas.Canvas(str(output_file.absolute()), pagesize=conf.page_dim)
    can.setStrokeColor(black)

    for index, row in df.iterrows():
        haiku_line1, haiku_line2, haiku_line3 = row

        # Calculate grid position on page
        col = index % cols
        row_num = (index % (rows * cols)) // cols

        print(f'Index: {index}, row: {row_num}, col: {col}')

        pdfmetrics.registerFont(TTFont(conf.font_name, conf.font_path))

        offsetX = conf.page_paddingX + (conf.obj_width + conf.obj_paddingX) * col
        offsetY = conf.page_paddingY + (conf.obj_height + conf.obj_paddingY) * row_num

        # Draw jigsaw puzzle piece
        draw_puzzle_piece(can, offsetX, offsetY + conf.obj_height, min(conf.obj_width, conf.obj_height))

        # Configure font
        can.setFont(conf.font_name, conf.font_size)

        # Calculate width of text
        text_width1 = pdfmetrics.stringWidth(haiku_line1, conf.font_name, conf.font_size)
        text_width2 = pdfmetrics.stringWidth(haiku_line2, conf.font_name, conf.font_size)
        text_width3 = pdfmetrics.stringWidth(haiku_line3, conf.font_name, conf.font_size)

        # Add text horizontally centered
        can.drawString((offsetX + conf.obj_width / 2) - text_width1 / 2, (offsetY + 2.5 * cm),
                       haiku_line1)
        can.drawString((offsetX + conf.obj_width / 2) - text_width2 / 2, (offsetY + 2.0 * cm),
                       haiku_line2)
        can.drawString((offsetX + conf.obj_width / 2) - text_width3 / 2, (offsetY + 1.5 * cm),
                       haiku_line3)

        if index > 0 and (index + 1) % (cols * rows) == 0:
            print('Next page')
            can.showPage()
            can.setStrokeColor(black)

    can.save()
    print(f'Processed {index} elements')
    return index + 1


if __name__ == '__main__':
    c = HaikuTagConfig()

    df = pd.read_csv('haikus_input.csv', delimiter=';')
    output_file = pathlib.Path('./haiku_tags').with_suffix('.pdf')

    generate_haiku_tags(df, output_file=output_file, conf=c)
