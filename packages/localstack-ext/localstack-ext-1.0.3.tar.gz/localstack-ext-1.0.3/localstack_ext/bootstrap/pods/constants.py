NIL_PTR = "NIL"

# well-defined directory names
ASSETS_ROOT_DIR = "assets"
# TODO: consider storing pods metadata in a non-hidden directory
DEFAULT_POD_DIR = "cloudpods"
OBJ_STORE_DIR = "objects"
VERSIONS_DIR = "versions"

# well-defined file names
HEAD_FILE = "HEAD"
VER_LOG_FILE = "VER_LOG"
MAX_VER_FILE = "MAX_VER"
KNOWN_VER_FILE = "KNOWN_VER"
REMOTE_FILE = ".REMOTE"
PODS_CONFIG_FILE = "pods-config.json"
VERSION_SPACE_FILES = [KNOWN_VER_FILE, MAX_VER_FILE, VER_LOG_FILE]
VERSION_SPACE_DIRS = [OBJ_STORE_DIR, VERSIONS_DIR]
VERSION_FILE = "version_{version_no}.yaml"
COMMIT_FILE = "metamodel_commit_{commit_no}.json"

# zip file names
META_ZIP = "version_{version_no}_meta"
STATE_ZIP = "version_{version_no}"
VERSION_SPACE_ARCHIVE = "version_space.zip"
COMPRESSION_FORMAT = "zip"

# misc. constants
VER_LOG_STRUCTURE = "{author};{ver_no};{rev_rid_no}"
