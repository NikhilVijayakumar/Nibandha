from pathlib import Path

# Project Roots
# Project Roots
PROJECT_ROOT_MARKER = "src/"
DEFAULT_TARGET_PACKAGE = "src/nikhil/nibandha"
DEFAULT_UNIT_TESTS_DIR = "tests/unit"
DEFAULT_E2E_TESTS_DIR = "tests/e2e"
DEFAULT_SOURCE_ROOT = "src"


# Report Directores
REPORT_DIR = ".Nibandha/Report"
GENERATED_DOCS_ROOT = "docs"

# Documentation Paths
DOC_FEATURES_DIR = "docs/features"
DOC_TECHNICAL_DIR = "docs/technical"
DOC_TEST_DIR = "docs/test"
DOC_MODULES_LEGACY_DIR = "docs/modules" # Kept for fallback/migration checks

# Asset Paths
ASSETS_IMAGES_DIR_REL = "../assets/images"
ASSETS_DATA_DIR_REL = "../assets/data"

UNKNOWN_VALUE = "unknown"
NOT_APPLICABLE = "N/A"

# Colors
COLOR_PASS = "green"
COLOR_FAIL = "red"
COLOR_WARNING = "yellow"
COLOR_NEUTRAL = "blue"

# Hygiene Constants
HYGIENE_IGNORED_NUMBERS = (-1, 0, 1)
HYGIENE_MIN_PATH_LENGTH = 3
HYGIENE_FORBIDDEN_NAMES = {"print", "pdb", "set_trace"}

# Report Ordering
REPORT_ORDER_UNIT = 3
REPORT_ORDER_E2E = 4
REPORT_ORDER_ARCHITECTURE = 5
REPORT_ORDER_TYPE_SAFETY = 6
REPORT_ORDER_COMPLEXITY = 7
REPORT_ORDER_CODE_HYGIENE = 8
REPORT_ORDER_DUPLICATION = 9
REPORT_ORDER_SECURITY = 10
REPORT_ORDER_DEPENDENCY = 11
REPORT_ORDER_PACKAGE = 12
REPORT_ORDER_DOCUMENTATION = 13
REPORT_ORDER_ENCODING = 14
REPORT_ORDER_CONCLUSION = 15

# Table/Figure Limits
TOP_N_ERRORS_DISPLAY = 30
TOP_N_CATEGORIES_DISPLAY = 10



# Coupling Thresholds
COUPLING_HIGH_THRESHOLD = 12
COUPLING_MODERATE_THRESHOLD = 7
COUPLING_LOW_THRESHOLD = 3

# Package Scoring
PACKAGE_INITIAL_SCORE = 100
PACKAGE_PENALTY_MAJOR = 20
PACKAGE_PENALTY_MINOR = 5
PACKAGE_HEALTHY_THRESHOLD = 80
PACKAGE_ATTENTION_THRESHOLD = 50

# Scanner Constants
SCANNER_EXCLUSIONS = {
    "__pycache__", ".venv", "venv", "env", "test", "tests",
    "build", "dist", ".git", ".idea", ".vscode", "node_modules", 
    "site-packages", ".tox"
}
PIP_TIMEOUT_SECONDS = 10
VERSION_REGEX_PATTERN = r'\d+\.\d+(?:\.\d+)?(?:\.\w+)?'
DEPENDENCY_GROUP_REGEX = r'\[(.*)\]'
DEFAULT_TOP_N_MODULES = 5

# Update Types
UPDATE_TYPE_MAJOR = "MAJOR"
UPDATE_TYPE_MINOR = "MINOR"
UPDATE_TYPE_PATCH = "PATCH"

# Image Paths (Relative to report output)
IMG_PATH_DEPENDENCY_MATRIX = "../assets/images/dependencies/dependency_matrix.png"
IMG_PATH_MODULE_DEPENDENCIES = "../assets/images/dependencies/module_dependencies.png"
IMG_PATH_UNIT_OUTCOMES = "/unit_outcomes.png"
IMG_PATH_UNIT_COVERAGE = "/unit_coverage.png"
IMG_PATH_UNIT_DURATIONS = "/unit_durations.png"
IMG_PATH_UNIT_SLOWEST = "/unit_slowest_tests.png"
IMG_PATH_UNIT_MODULE_DURATIONS = "/unit_module_durations.png"
IMG_PATH_ARCH_STATUS = "/quality/architecture_status.png"
IMG_PATH_ERROR_CATEGORIES = "/quality/error_categories.png"
IMG_PATH_TYPE_ERRORS = "/quality/type_errors_by_module.png"
IMG_PATH_COMPLEXITY_DIST = "/quality/complexity_distribution.png"
IMG_PATH_COMPLEXITY_BOX = "/quality/complexity_boxplot.png"
IMG_PATH_E2E_STATUS = "/e2e_status.png"
IMG_PATH_E2E_DURATIONS = "/e2e_durations.png"
IMG_PATH_DOC_COVERAGE = "/documentation/doc_coverage.png"
IMG_PATH_DOC_DRIFT = "/documentation/doc_drift.png"

# Additional Regex Patterns
REGEX_DUPLICATION_PATTERN = r"==(.+):\["
REGEX_MYPY_ERROR = r"([^:]+):.*error:.*\[([^\]]+)\]"
REGEX_COMPLEXITY_SCORE = r"complex \((\d+)\)"

# Additional Thresholds
THRESHOLD_COMPLEXITY_MAX = 10
THRESHOLD_TOP_N_MODULES = 5
UPDATE_TYPE_UNKNOWN = "UNKNOWN"

# Report Filenames
REPORT_FILENAME_COVER = "00_cover_page.md"
REPORT_FILENAME_INTRO = "01_introduction.md"
REPORT_FILENAME_REFERENCES = "02_global_references.md"
REPORT_FILENAME_UNIT = "03_unit_report.md"
REPORT_FILENAME_E2E = "04_e2e_report.md"
REPORT_FILENAME_ARCHITECTURE = "05_architecture_report.md"
REPORT_FILENAME_TYPE_SAFETY = "06_type_safety_report.md"
REPORT_FILENAME_COMPLEXITY = "07_complexity_report.md"
REPORT_FILENAME_HYGIENE = "08_code_hygiene_report.md"
REPORT_FILENAME_DUPLICATION = "09_duplication_report.md"
REPORT_FILENAME_SECURITY = "10_security_report.md"
REPORT_FILENAME_DEPENDENCY_MODULE = "11_module_dependency_report.md"
REPORT_FILENAME_DEPENDENCY_PACKAGE = "12_package_dependency_report.md"
REPORT_FILENAME_DOCUMENTATION = "13_documentation_report.md"
REPORT_FILENAME_ENCODING = "14_encoding_report.md"
REPORT_FILENAME_CONCLUSION = "15_conclusion.md"
