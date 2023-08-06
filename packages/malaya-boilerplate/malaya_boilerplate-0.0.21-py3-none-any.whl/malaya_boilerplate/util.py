from . import __package__
from shutil import rmtree
from pathlib import Path
import os
import logging

IS_GPU = None


def _delete_folder(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            os.remove(os.path.join(root, file))


def _get_home():
    home = os.environ.get(
        f'{__package__.upper()}_CACHE',
        os.path.join(str(Path.home()), __package__.title()),
    )
    version_path = os.path.join(home, 'version')
    return home, version_path


def _delete_macos():
    home, _ = _get_home()
    macos = os.path.join(home, '__MACOSX')
    if os.path.exists(macos):
        rmtree(macos)


def get_home():
    home, version_path = _get_home()

    try:
        if not os.path.exists(home):
            os.makedirs(home)
    except:
        raise Exception(
            f'Malaya cannot make directory for caching. Please check your {home}'
        )

    _delete_macos()
    if not os.path.isfile(version_path):
        _delete_folder(home)
        with open(version_path, 'w') as fopen:
            fopen.write(version)
    else:
        with open(version_path, 'r') as fopen:
            cached_version = fopen.read()
        try:
            if float(cached_version) < 1:
                _delete_folder(home)
                with open(version_path, 'w') as fopen:
                    fopen.write(version)
        except:
            _delete_folder(home)
            with open(version_path, 'w') as fopen:
                fopen.write(version)

    return home, version_path


def available_gpu():
    """
    Get list of GPUs from `nvidia-smi`.

    Returns
    -------
    result : List[str]
    """
    percent = []
    try:
        ns = os.popen('nvidia-smi')
        lines_ns = ns.readlines()
        for line in lines_ns:
            if line.find('%') != -1:
                percent.append(int(line.split('%')[-2][-3:]))
        percent = [f'/device:GPU:{i}' for i in range(len(percent))]
    except:
        pass
    return percent


def gpu_available():
    """
    Check Malaya is GPU version.

    Returns
    -------
    result : bool
    """

    import pkg_resources

    global IS_GPU

    if IS_GPU is None:
        IS_GPU = f'{__package__}-gpu' in [
            p.project_name for p in pkg_resources.working_set
        ]
        if IS_GPU:
            gpus = available_gpu()
            IS_GPU = len(gpus) > 0
    return IS_GPU


def print_cache(location = None):
    """
    Print cached data, this will print entire cache folder if let location = None.

    Parameters
    ----------
    location : str, (default=None)
        if location is None, will print entire cache directory.

    """

    from .local_file import DisplayablePath

    home, _ = _get_home()
    path = os.path.join(home, location) if location else home
    paths = DisplayablePath.make_tree(Path(path))
    for path in paths:
        print(path.displayable())


def clear_all_cache():
    """
    Remove cached data, this will delete entire cache folder.
    """
    _delete_macos()
    home, _ = _get_home()
    try:
        _delete_folder(home)
        with open(version_path, 'w') as fopen:
            fopen.write(version)
        return True
    except:
        raise Exception(
            f'failed to clear cached models. Please make sure {home} is able to overwrite from Malaya'
        )


def clear_cache(location):
    """
    Remove selected cached data, please run malaya.print_cache() to get path.

    Parameters
    ----------
    location : str

    Returns
    -------
    result : boolean
    """

    home, _ = _get_home()
    if not isinstance(location, str):
        raise ValueError('location must be a string')
    location = os.path.join(home, location)
    if not os.path.exists(location):
        raise Exception(
            'folder not exist, please check path from `malaya.print_cache()`'
        )
    if not os.path.isdir(location):
        raise Exception(
            'Please use parent directory, please check path from `malaya.print_cache()`'
        )
    _delete_folder(location)
    return True


def clear_session(model):
    """
    Clear session from a model to prevent any out-of-memory or segmentation fault issues.

    Parameters
    ----------
    model : malaya object.

    Returns
    -------
    result : boolean
    """

    success = False
    try:
        if hasattr(model, 'sess'):
            model.sess.close()
            success = True
        elif hasattr(model, '_sess'):
            model._sess.close()
            success = True
    except Exception as e:
        logging.warning(e)
    return success
