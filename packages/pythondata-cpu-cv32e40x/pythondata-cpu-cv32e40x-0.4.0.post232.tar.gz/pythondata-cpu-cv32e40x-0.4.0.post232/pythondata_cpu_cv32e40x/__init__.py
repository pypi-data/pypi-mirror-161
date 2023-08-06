import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.4.0.post232"
version_tuple = (0, 4, 0, 232)
try:
    from packaging.version import Version as V
    pversion = V("0.4.0.post232")
except ImportError:
    pass

# Data version info
data_version_str = "0.4.0.post90"
data_version_tuple = (0, 4, 0, 90)
try:
    from packaging.version import Version as V
    pdata_version = V("0.4.0.post90")
except ImportError:
    pass
data_git_hash = "4349cdc69b4f3cf45ddb12a092e76fa074ce8504"
data_git_describe = "0.4.0-90-g4349cdc6"
data_git_msg = """\
commit 4349cdc69b4f3cf45ddb12a092e76fa074ce8504
Merge: 4f7a8d91 5c32cd85
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Fri Jul 29 12:27:11 2022 +0200

    Merge pull request #632 from Silabs-ArjanB/ArjanB_obi15
    
    Updated OBI to version 1.5.0

"""

# Tool version info
tool_version_str = "0.0.post142"
tool_version_tuple = (0, 0, 142)
try:
    from packaging.version import Version as V
    ptool_version = V("0.0.post142")
except ImportError:
    pass


def data_file(f):
    """Get absolute path for file inside pythondata_cpu_cv32e40x."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_cv32e40x".format(f))
    return fn
