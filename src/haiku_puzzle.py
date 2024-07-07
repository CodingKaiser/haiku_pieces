from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def draw_puzzle_piece(c, x, y, size):
    """
    Draws a single puzzle piece at a specified location.

    Parameters:
    c (Canvas): The ReportLab canvas object.
    x (int): The x-coordinate of the top-left corner of the piece.
    y (int): The y-coordinate of the top-left corner of the piece.
    size (int): The size of the piece (width and height).
    """
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
    # Take the following line of code and flip it 90 degrees to the right making sure to adjust the x and y coordinates accord to the last lineTo
    # path.arc(x + size * 0.474, y - size * 0.242, x + size * 0.58, y - size * 0.36, startAng=120, extent=-240)
    path.arc(x + size * 0.81, y - size * 0.474, x + size * 0.69, y - size * 0.58, startAng=30, extent=-240)
    path.lineTo(x + 0.5 * size, y - size * 0.5)
    path.moveTo(x + 0.5 * size, y - size)
    path.lineTo(x + 0.5 * size, y - size * 0.8)
    # Take the following line of code and flip it 90 degrees clockwise making sure to adjust the x and y coordinates accord to the last lineTo
    # path.arc(x + size * 0.81, y - size * 0.474, x + size * 0.69, y - size * 0.58, startAng=30, extent=-240)
    path.arc(x + size * 0.529, y - size * 0.81, x + size * 0.42, y - size * 0.69, startAng=300, extent=-240)
    path.lineTo(x + 0.5 * size, y - size * 0.5)

    path.moveTo(x, y - 0.5 * size)
    path.lineTo(x + size * 0.18, y - 0.5 * size)
    # Take the following line of code and flip it 90 degrees clockwise making sure to adjust the x and y coordinates accord to the last lineTo
    # path.arc(x + size * 0.529, y - size * 0.81, x + size * 0.42, y - size * 0.69, startAng=300, extent=-240)
    path.arc(x + size * 0.17, y - size * 0.529, x + size * 0.30, y - size * 0.42, startAng=210, extent=-240)
    path.lineTo(x + 0.5 * size, y - size * 0.5)

    c.drawPath(path, stroke=1, fill=0)


def draw_jigsaw_puzzle(c, rows, cols, piece_size):
    """
    Draws a complete jigsaw puzzle with the specified number of rows and columns.

    Parameters:
    c (Canvas): The ReportLab canvas object.
    rows (int): The number of rows of puzzle pieces.
    cols (int): The number of columns of puzzle pieces.
    piece_size (int): The size of each puzzle piece (width and height).
    """
    for row in range(rows):
        for col in range(cols):
            x = col * piece_size * 1.1 + 50  # Adding some spacing
            y = 800 - row * piece_size * 1.1 - 50  # Adjust starting point and spacing
            draw_puzzle_piece(c, x, y, piece_size)


# Create a canvas
c = canvas.Canvas("jigsaw_puzzle.pdf", pagesize=letter)
# Draw the jigsaw puzzle
draw_jigsaw_puzzle(c, 2, 2, 200)  # Adjust the number of rows, columns, and size as needed
c.showPage()
c.save()
