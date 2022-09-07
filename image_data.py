"""
Read a variety of image file formats as input for tiled.
"""

from PIL import Image
from tiled.adapters.array import ArrayAdapter
from tiled.adapters.mapping import MapAdapter
import numpy
import pathlib
import yaml

ROOT = pathlib.Path(__file__).parent

EXTENSIONS = []
# https://mimetype.io/all-types#image
MIMETYPES = """
    image/avif
    image/bmp
    image/gif
    image/jpeg
    image/png
    image/tiff
    image/vnd.microsoft.icon
    image/webp
""".split()
# TODO:     image/svg+xml  not handled by PIL

EMPTY_ARRAY = numpy.array([0,0])


def interpret_exif(image):
    from PIL.ExifTags import TAGS
    from PIL.TiffImagePlugin import IFDRational

    exif = image.getexif()
    md = {}
    for tag_id in exif:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exif.get(tag_id)
        # decode bytes 
        if isinstance(data, bytes):
            data = data.decode()
        if isinstance(data, IFDRational):
            attrs = "numerator denominator imag".split()
            data = {k: getattr(data, k) for k in attrs}
        md[tag] = data
    return md


def image_metadata(image):
    attrs = """
        bits
        filename
        format
        format_description
        is_animated
        layer
        layers
        mode
        n_frames
        size
        text
    """.split()
    md = {k: getattr(image, k) for k in attrs if hasattr(image, k)}

    # TODO: "image.info" will need special handling
    if "info" in md:
        for k in "exif icc_profile xmp".split():
            if k in md["info"]:
                md["info"].pop(k)

    exif = interpret_exif(image)
    if len(exif) > 0:
        md["exif"] = exif

    md["extrema"] = image.getextrema()

    return md


def read_image(filename):
    try:
        image = Image.open(filename)
        md = image_metadata(image)

        # special cases
        if image.format == "GIF":
            pass
        elif image.format == "SVG":
            pass

        im = image.getdata()
        if im.bands == 1:
            dimensions = im.size
        else:
            dimensions = (im.bands, *im.size)
        pixels = numpy.array(list(im)).reshape(dimensions)
        print(yaml.dump(md))
        return ArrayAdapter.from_array(pixels, metadata=md)

    except Exception as exc:
        arrays = dict(
            ignore=ArrayAdapter.from_array(
                numpy.array([0,0]), metadata=dict(ignore="placeholder, ignore")
            )
        )
        return MapAdapter(
            arrays, metadata=dict(
                filename=str(filename),
                exception=exc,
                purpose="some problem reading this file as an image"
            )
        )


def main():
    testdir = ROOT / "data" / "usaxs" / "2021"
    for filepath in testdir.iterdir():
        read_image(filepath)

    testdir = ROOT / "data" / "images"
    for filepath in testdir.iterdir():
        read_image(filepath)


if __name__ == "__main__":
    main()
