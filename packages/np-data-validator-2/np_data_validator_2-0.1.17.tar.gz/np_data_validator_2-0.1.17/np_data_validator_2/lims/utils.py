def fix_lims_path(path):
    if path.startswith("/allen"):
        return "/" + path
    return path
