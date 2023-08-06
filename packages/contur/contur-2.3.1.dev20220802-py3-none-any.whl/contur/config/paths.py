import os
import os.path

def root_path():
    """
    Get the root paths of the contur installation
    """
    croot_user=os.getenv("CONTUR_USER_DIR")
    croot_data=os.getenv("CONTUR_DATA_PATH")
    if croot_user is None:
        croot = get_root_path_from_os()
    return croot_user,croot_data

def get_root_path_from_os():
    """
    Get the root path of the contur installation using the fact that this
    file is in the subdirectory CONTUR_ROOT/contur/config/
    """
    # parent1 = os.path.dirname(__file__)
    # parent2 = os.path.dirname(parent1)
    # parent3 = os.path.dirname(parent2)
    # return parent3
    pass

def user_path(*relpaths):
    """
    Get the complete path to a sub-path in the user's local Contur installation
    """
    return os.path.join(root_path()[0], *relpaths)

def data_path(*relpaths):
    """
    Get the complete path to a sub-path in the user's local Contur installation
    """
    return os.path.join(root_path()[1], *relpaths)
