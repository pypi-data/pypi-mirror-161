import os

# path to directory: rettij (the project's root dir, 3 directories up from this file)
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".."))

# path to directory: rettij
SRC_DIR = os.path.join(PROJECT_ROOT_DIR, "rettij")

# path to directory: rettij/components
COMPONENTS_DIR = os.path.join(SRC_DIR, "components")

# path to directory: user
USER_DIR = os.path.join(SRC_DIR, "user")

# path to directory: test
TESTS_DIR = os.path.join(PROJECT_ROOT_DIR, "tests")

# Path to directory rettij/resources
RESOURCES_DIR = os.path.join(SRC_DIR, "resources")
