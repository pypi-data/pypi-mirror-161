import os


def get_ext_files(path, ext, deep=False):
    if deep:
        files = []
        for dir_path, subdir, files in os.walk(path):
            for f in files:
                full_path = os.path.join(dir_path, f)
                if os.path.splitext(f)[-1] == ext:
                    files.append(full_path)
        return files
    else:
        files = [os.path.join(path, i) for i in os.listdir(
            path) if os.path.splitext(i)[-1] == ext]
        return files
