import numpy as np

import PIL.Image
import PIL.ImageColor
import PIL.ImageDraw
import PIL.ImageFont

from . import func


def wrap_text(text, font: PIL.ImageFont.ImageFont, width):
    w, _ = font.getsize(text)
    max_char = int((width / w) * len(text))
    n_lines = len(text) // max_char + (len(text) % max_char != 0)
    wrapped_text = '\n'.join([text[i * max_char:(i + 1) * max_char] for i in range(n_lines)])
    return wrapped_text


def draw_text(image, text, pos=(0, 0), font=None, text_color='white', background_color='black', wrap=False):
    # get font
    if font is None:
        font = PIL.ImageFont.load_default()
    # context
    draw = PIL.ImageDraw.Draw(image)

    # draw background
    if background_color is not None:
        # get text size
        w, h = font.getsize(text)
        # draw rect
        draw.rectangle((pos[0], pos[1], pos[0] + w, pos[1] + h), fill=background_color)
    # texxt wrapping
    if wrap:
        if isinstance / (wrap, int):
            width = wrap
        else:
            width = image.size[0] - pos[0]
        text = wrap_text(text, font, width)

    # draw text
    draw.text(pos, text, fill=text_color, font=font)


def draw_receptive_field(image, size=224, outline=(255, 0, 0)):
    # context
    draw = PIL.ImageDraw.Draw(image)
    # retangle
    image_size = image.size
    left_top = (np.array(image_size) - size) // 2
    right_bottom = left_top + size
    draw.rectangle([*left_top, *right_bottom], outline=outline, width=3)


def draw_rect(image, box=[0, 0, 224, 224], outline=(255, 0, 0), width=2):
    # context
    draw = PIL.ImageDraw.Draw(image)
    # retangle
    draw.rectangle(box, outline=outline, width=width)


__default_colors__ = [PIL.ImageColor.getrgb(c) for c in ['#B22222', '#FF69B4', '#FF6347', '#FFD700', '#ADFF2F', '#40E0D0']]


def draw_bboxes(image, bboxes, classes, scores=None, id2name=None, colors=__default_colors__, copy=True):
    """ draw bounding boxes with their class names on images
    Input:
        image: PIL.Image
        bboxes: [n_boxes, (x1, y1, x2, y2)]
        classes, scores: [n_boxes]
        id2name: dict
    """
    if copy:
        image = image.copy()

    if id2name is not None:
        labels = [id2name.get(cid, 'unknown') for cid in classes]
    else:
        labels = [str(cid) for cid in classes]

    font = PIL.ImageFont.truetype('./fonts/Roboto-Regular.ttf', size=14)

    for idx in range(bboxes.shape[0]):
        color = colors[idx % len(colors)]
        x1, y1, x2, y2 = bboxes[idx]

        draw_rect(image, [x1, y1, x2, y2], outline=color)
        text = str(labels[idx])
        if scores is not None:
            text += f' {scores[idx]:.3}'

        _, h = font.getsize(text)
        draw_text(image, text, [x1, y1 - h], font=font, text_color='black', background_color=color)

    return image


def make_grid(images, grid=None, max_size=224, bg_color=(255, 255, 255)):
    """ make a image grid
    Parameters:
        images: array of PIL.Image
            list of image
        grid: 2-tuple of int or int
            (n_col, n_row) or n_col
        max_size: int
            the max dimension of image
        bg_color: 3-tuple, 4-tuple, or str
            background color
    Returns:
        PIL.Image
            grided image
    """
    if grid is None:
        grid = (len(images), 1)
    if isinstance(grid, int):
        grid = (grid, len(images) // grid + (len(images) % grid > 0))

    assert len(grid) == 2
    bg_size = (max_size * grid[0], max_size * grid[1])
    background = PIL.Image.new('RGB', bg_size, bg_color)

    pasted_images = 0
    for row in range(grid[1]):
        for col in range(grid[0]):
            if pasted_images == len(images):
                return background

            left = max_size * col
            top = max_size * row

            nImage = np.array(images[pasted_images])
            nResized = func.resize_keep_ratio(nImage, max_size)
            background.paste(PIL.Image.fromarray(nResized), (left, top))

            pasted_images += 1

    return background


def draw_palette(colors, size=64):
    palette = np.empty((size, len(colors) * size, 3), dtype=np.uint8)
    for i in range(len(colors)):
        palette[:, i * size:(i + 1) * size, :] = colors[i]
    return PIL.Image.fromarray(palette)


EDGE_TOP = 0
EDGE_LEFT = 1
EDGE_RIGHT = 2
EDGE_BOTTOM = 3


def draw_text_at_edge(image, text, pos=EDGE_BOTTOM,
                      font_size=14, text_width=100, background_color=0, text_color='white'):
    font = PIL.ImageFont.truetype('./fonts/Roboto-Regular.ttf', size=font_size)
    if pos in [EDGE_TOP, EDGE_BOTTOM]:
        text_width = image.size[0]

    wrapped_text = wrap_text(text, font, text_width)
    _, text_height = font.getsize_multiline(wrapped_text)
    if pos in [EDGE_TOP, EDGE_BOTTOM]:
        image_width = image.size[0]
        image_height = image.size[1] + text_height
    else:
        image_width = image.size[0] + text_width
        image_height = max(image.size[1], text_height)

    image_x = 0
    image_y = 0
    text_x = 0
    text_y = 0
    if pos == EDGE_BOTTOM:
        text_y = image.size[1]
    elif pos == EDGE_LEFT:
        image_x = text_width
    elif pos == EDGE_RIGHT:
        text_x = image.size[0]
    elif pos == EDGE_TOP:
        image_y = text_height

    new_image = PIL.Image.new(image.mode, (image_width, image_height), color=background_color)
    new_image.paste(image, (image_x, image_y))
    # draw text
    draw = PIL.ImageDraw.Draw(new_image)
    draw.text((text_x, text_y), wrapped_text, fill=text_color, font=font)

    return new_image
