from enum import Enum

USER_COLUMN = 'sarus_protected_entity'
WEIGHTS = 'sarus_weights'
PUBLIC = 'sarus_is_public'
LIST_VALUES = 'sarus_list_values'
ARRAY_VALUES = 'sarus_array_values'
OPTIONAL_VALUE = 'sarus_optional_value'
TEXT_MIN_LENGTH = 'min_length'
TEXT_MAX_LENGTH = 'max_length'
TEXT_CHARSET = 'text_char_set'
TEXT_EXACT_CHARSET = 'FullUserInput'
TEXT_ALPHABET_NAME = 'text_alphabet_name'
SQL_MAPPING = 'sql_mapping'
NON_EMPTY_PROTECTED_PATHS = 'non_zero_protected_values'
STRUCT_KIND = 'merge_paths'
TO_MERGE = 'fks_for_merging'
FLOAT_DISTRIBUTION = 'distribution_model'
FLOAT_DIST_PARAMS = 'parameters'
MAX_MAX_MULT = 'max_max_multiplicity'
DATASET_SLUGNAME = 'slugname'


class StructKind(Enum):
    HAS_PE = '0'
    NO_PE = '1'
    TO_MERGE = '2'


DATETIME_YEAR = 'year'
DATETIME_MONTH = 'month'
DATETIME_DAY = 'day'
DATETIME_HOUR = 'hour'
DATETIME_MINUTES = 'minutes'
DATETIME_SECONDS = 'seconds'


# Statuses constants
TO_SQL_TASK = "sql_preparation"

# Big Data Status
BIG_DATA_TASK = 'big_data_dataset'
BIG_DATA_THRESHOLD = 'threshold'
IS_BIG_DATA = 'is_big_data'
DATASET_N_LINES = 'dataset_n_lines'
DATASET_N_BYTES = 'dataset_n_bytes'
THRESHOLD_TYPE = "threshold_type"

# Caching Status
TO_PARQUET = 'to_parquet'
CACHE = TO_PARQUET
CACHE_PATH = 'path'
COMPUTATION_QUEUED = 'computation_queued'

# Attributes Status
SCHEMA_TASK = 'schema'
SIZE_TASK = 'size'
BOUNDS_TASK = 'bounds'
MARGINALS_TASK = 'marginals'
