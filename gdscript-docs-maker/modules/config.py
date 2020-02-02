import logging

LOGGER = logging.getLogger("GDScript docs maker")
LOG_LEVELS = [logging.INFO, logging.DEBUG]
LOG_LEVELS = [0] + sorted(LOG_LEVELS, reverse=True)
