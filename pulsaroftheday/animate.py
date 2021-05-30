"""
"""

from pathlib import Path
from typing import List, Tuple, Union

import numpy as np

from loguru import logger
from PIL import Image, ImageDraw, ImageFont


def add_pulsar(
    filename: Union[str, Path],
    period: float,
    origins: List[Tuple[int, int]] = None,
    color: Tuple[int, int, int] = None,
    size: Tuple[int, int] = None,
    nframes: int = 9,
) -> None:

    try:
        src = Image.open(filename)
    except Exception as error:
        logger.error(f"{error} Unable to add pulsar animation to {filename}")
        raise

    size = size or (20, 20)

    w = size[0] // 2
    h = size[1] // 2

    origins = origins or [
        [src.width // 4 - w, src.height // 2 - w],
        [int(src.width * 0.75) - w, src.height // 2 - w],
    ]

    origins = [[x - w, src.height - y - h] for x, y in origins]

    logger.debug(f"Origins: {origins}")

    color = color or (255, 0, 0)

    duration = period / nframes

    logger.debug(f"period {period} nframes {nframes} duration={duration}")

    # XXX the longer the duration the more frames needed for a smooth
    #     transition

    alphas = np.linspace(0, 255, int(nframes / 2) + 1, dtype=int).tolist()

    alphas.extend(reversed(alphas[:-1]))

    try:
        font = ImageFont.truetype("Courier New.ttf", 72)
    except OSError as error:
        logger.debug(f"{error}")
        font = ImageFont.load_default()

    pulsar = Image.new("RGBA", size, (0, 0, 0, 0))

    draw = ImageDraw.Draw(pulsar)
    bbox = [2, 2, size[0] - 2, size[1] - 2]
    frames = []
    for fnum, alpha in enumerate(alphas):
        frames.append(Image.new("RGBA", src.size, (0, 0, 0, 255)))
        frames[-1].alpha_composite(src)
        c = (alpha, 0, 0, alpha)
        draw.ellipse(bbox, fill=c)  # , width=1, outline=(0, 0, 0, 255))
        for origin in origins:
            frames[-1].alpha_composite(pulsar, dest=tuple(origin))

    logger.debug(f"Number of frames: {len(frames)}")

    frames[0].save(
        filename,
        append_images=frames[1:],
        save_all=True,
        duration=duration,
        loop=0,
    )
