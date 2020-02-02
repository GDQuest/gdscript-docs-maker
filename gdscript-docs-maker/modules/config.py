import logging

LOGGER = logging.getLogger("GDScript docs maker")
LOG_LEVEL = [logging.INFO, logging.DEBUG]
LOG_LEVEL = [None] + sorted(LOG_LEVEL, reverse=True)
