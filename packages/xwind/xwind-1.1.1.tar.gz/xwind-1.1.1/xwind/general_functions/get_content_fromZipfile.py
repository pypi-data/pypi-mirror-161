import zipfile as zp

from .get_encoding import from_string


def get_string_from_zip(zip_file_path):
    azip = zp.ZipFile(zip_file_path)
    file_name = azip.namelist()[0]
    content = azip.read(file_name)
    encoding = from_string(content)
    return content.decode(encoding)
