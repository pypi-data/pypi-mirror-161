import os


def file_list(path, suf=None, list0=None):
    if list0 is None:
        list0 = []
    if os.path.isfile(path):
        list0.append(path)
        return list0
    files = os.listdir(path)
    for f in files:
        p = os.path.join(path, f)
        if os.path.isfile(p) and (suf in [None, os.path.splitext(f)[-1]]):
            list0.append(p)
    return list0


def dir_list(path, list0=None):
    if os.path.isfile(path):
        return []
    files = os.listdir(path)
    if list0 is None:
        list0 = []
    for f in files:
        p = os.path.join(path, f)
        if os.path.isdir(p):
            list0.append(p)
    return list0


def all_in_dir(path, suf=None, list0=None):
    if list0 is None:
        list0 = []
    if os.path.isfile(path):
        list0.append(path)
        return list0
    files = os.listdir(path)
    for f in files:
        p = os.path.join(path, f)
        if os.path.isdir(p) or \
                (os.path.isfile(p) and (suf in [None, os.path.splitext(f)[-1]])):
            list0.append(p)
    return list0


def all_files(path, suf=None, flist=None):
    flist = file_list(path, suf, flist)
    dlist = dir_list(path, None)
    for p in dlist:
        flist = all_files(p, suf, flist)
    return flist




