"""
Read a variety of image file formats as input for tiled.
"""

from PIL import Image
from PIL import UnidentifiedImageError
from tiled.adapters.array import ArrayAdapter
import numpy
import pathlib

ROOT = pathlib.Path(__file__).parent

EXTENSIONS = []
# https://mimetype.io/all-types#image
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
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


def read_image(filename):
    if filename.name.endswith(".svg"):
        pass
    try:
        image = Image.open(filename)
        attrs = """
            bits
            filename
            format
            format_description
            info
            is_animated
            layer
            layers
            mode
            n_frames
            size
            text
        """.split()
        md = {k: getattr(image, k) for k in attrs if hasattr(image, k)}

        # special cases
        if image.format == "GIF":
            pass
        elif image.format == "JPEG":
            exif = image.getexif()
            if len(exif) > 0:
                md["exif"] = {k: v for k, v in exif.items()}
        elif image.format == "SVG":
            pass
        elif image.format == "WEBP":
            if "info" in md:
                for k in "exif icc_profile xmp".split():
                    if k in md["info"]:
                        md["info"].pop(k)
                exif = image.getexif()
                if len(exif) > 0:
                    md["exif"] = {k: v for k, v in exif.items()}

        im = image.getdata()
        md["extrema"] = image.getextrema()
        if im.bands == 1:
            dimensions = im.size
        else:
            dimensions = (im.bands, *im.size)
        pixels = numpy.array(list(im)).reshape(dimensions)
        print(md)
        return ArrayAdapter.from_array(pixels, metadata=md)
    except UnidentifiedImageError:
        return  ArrayAdapter.from_array(numpy.array([]), metadata={})


def main():
    testdir = ROOT / "data" / "usaxs" / "2021"
    for filepath in testdir.iterdir():
        read_image(filepath)

    testdir = ROOT / "data" / "images"
    for filepath in testdir.iterdir():
        read_image(filepath)


if __name__ == "__main__":
    main()
