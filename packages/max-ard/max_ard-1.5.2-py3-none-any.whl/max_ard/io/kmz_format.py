"""Convert ARD Selects to a KMZ File"""

from os import mkdir, rename
from os.path import join, split, splitext
from shutil import make_archive, rmtree

from max_ard.io import KmlDoc

__all__ = ("KmzDoc",)


def KmzDoc(select, path):
    """Convert a Select to a KMZ file and save

    Parameters
    ----------
    select: Select
    path: path at which to save the KMZ

    Returns
    -------
    none"""

    # get the kml doc as a string
    kml_str = KmlDoc(select)

    splitext_path = splitext(path)
    path_minus_extension = splitext_path[0]

    split_path = split(path)
    basepath = split_path[0]
    kmz_fullname = split_path[1]

    kmz_basename = splitext(kmz_fullname)[0]
    folder_path = join(basepath, kmz_basename)

    mkdir(folder_path)

    kml_path = join(folder_path, kmz_basename + ".kml")
    with open(kml_path, "w") as out:
        out.write(kml_str)

    make_archive(path_minus_extension, "zip", folder_path)
    folder_zipped_path = folder_path + ".zip"

    rename(folder_zipped_path, folder_path + ".kmz")
    rmtree(folder_path)
