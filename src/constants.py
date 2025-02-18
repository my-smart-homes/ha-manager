from enum import Enum

DB_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

# DATE
DATE_FORMAT = "%Y-%m-%d"
PLACEHOLDER_END_DATE = "2050-01-01"
PLACEHOLDER_START_DATE = "1900-01-01"
FULL_DATE_FORMAT = f"{DATE_FORMAT} %H:%M:%S"

# LOGGING FORMAT
LOG_WITHOUT_TIMESTAMP = "[%(levelname)s] %(name)s > %(funcName)s | %(message)s"
LOG_WITH_TIMESTAMP = "[%(log_color)s%(levelname)s%(reset)s] %(asctime)s | %(yellow)s%(name)s > %(funcName)s%(reset)s | Line %(lineno)d | %(cyan)s%(message)s"
LOG_FORMAT = LOG_WITH_TIMESTAMP

class Environment(str, Enum):
    LOCAL = "LOCAL"
    STAGING = "STAGING"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_debug(self):
        return self in (self.LOCAL, self.STAGING, self.TESTING)

    @property
    def is_testing(self):
        return self == self.TESTING

    @property
    def is_deployed(self) -> bool:
        return self in (self.STAGING, self.PRODUCTION)
