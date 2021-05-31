"""
"""

from pathlib import Path
from typing import List, Tuple, Union

import numpy as np

from loguru import logger
from PIL import Image, ImageDraw, ImageFont


MIN_FRAME_DURATION = 0.02


def add_pulsar(
    filename: Union[str, Path],
    period: float,
    origins: List[Tuple[int, int]],
    size: Tuple[int, int] = None,
) -> None:

    try:
        src = Image.open(filename)
    except Exception as error:
        logger.error(f"{error} Unable to add pulsar animation to {filename}")
        raise

    size = size or (15, 15)

    w = size[0] // 2
    h = size[1] // 2

    # remap Y from matplotlib coords to PIL coords and offset
    # by half the width and height of the drawn object (ellipse)
    origins = [(x - w, (src.height - y) - h) for x, y in origins]

    logger.debug(f"Origins: {origins}")

    nframes = int((period / MIN_FRAME_DURATION) / 4)
    duration = MIN_FRAME_DURATION

    if nframes <= 1:
        nframes = 2

    logger.debug(f"period {period} nframes {nframes} duration={duration}")

    if nframes == 2:
        alphas = [0, 255]
    else:
        alphas = np.linspace(0, 255, int(nframes / 2) + 1, dtype=int).tolist()
        alphas.extend(reversed(alphas[:-1]))

    pulsar = Image.new("RGBA", size, (0, 0, 0, 0))

    draw = ImageDraw.Draw(pulsar)
    bbox = [2, 2, size[0] - 2, size[1] - 2]
    frames = []
    for fnum, alpha in enumerate(alphas):
        frames.append(Image.new("RGBA", src.size, (0, 0, 0, 255)))
        frames[-1].alpha_composite(src)
        c = (alpha, 255 - alpha, 255 - alpha, alpha)
        draw.ellipse(bbox, fill=c)
        for origin in origins:
            frames[-1].alpha_composite(pulsar, dest=origin)

    frames[0].save(
        filename,
        append_images=frames[1:],
        save_all=True,
        duration=duration,
        loop=0,
    )
