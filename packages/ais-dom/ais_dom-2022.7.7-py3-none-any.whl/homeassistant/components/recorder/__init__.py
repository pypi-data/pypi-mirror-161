"""Support for recording details."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.const import CONF_EXCLUDE, CONF_INCLUDE, EVENT_STATE_CHANGED
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entityfilter import (
    INCLUDE_EXCLUDE_BASE_FILTER_SCHEMA,
    INCLUDE_EXCLUDE_FILTER_SCHEMA_INNER,
    convert_include_exclude_filter,
)
from homeassistant.helpers.integration_platform import (
    async_process_integration_platforms,
)
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import bind_hass

from . import statistics, websocket_api
from .const import (
    CONF_DB_INTEGRITY_CHECK,
    DATA_INSTANCE,
    DOMAIN,
    EXCLUDE_ATTRIBUTES,
    SQLITE_URL_PREFIX,
)
from .core import Recorder
from .services import async_register_services
from .tasks import AddRecorderPlatformTask

_LOGGER = logging.getLogger(__name__)


DEFAULT_URL = "sqlite:///{hass_config_path}"
DEFAULT_DB_FILE = "home-assistant_v2.db"
DEFAULT_DB_INTEGRITY_CHECK = True
DEFAULT_DB_MAX_RETRIES = 10
DEFAULT_DB_RETRY_WAIT = 3
DEFAULT_COMMIT_INTERVAL = 1

CONF_AUTO_PURGE = "auto_purge"
CONF_AUTO_REPACK = "auto_repack"
CONF_DB_URL = "db_url"
CONF_DB_MAX_RETRIES = "db_max_retries"
CONF_DB_RETRY_WAIT = "db_retry_wait"
CONF_PURGE_KEEP_DAYS = "purge_keep_days"
CONF_PURGE_INTERVAL = "purge_interval"
CONF_EVENT_TYPES = "event_types"
CONF_COMMIT_INTERVAL = "commit_interval"


EXCLUDE_SCHEMA = INCLUDE_EXCLUDE_FILTER_SCHEMA_INNER.extend(
    {vol.Optional(CONF_EVENT_TYPES): vol.All(cv.ensure_list, [cv.string])}
)

FILTER_SCHEMA = INCLUDE_EXCLUDE_BASE_FILTER_SCHEMA.extend(
    {vol.Optional(CONF_EXCLUDE, default=EXCLUDE_SCHEMA({})): EXCLUDE_SCHEMA}
)


ALLOW_IN_MEMORY_DB = False


def validate_db_url(db_url: str) -> Any:
    """Validate database URL."""
    # Don't allow on-memory sqlite databases
    if (db_url == SQLITE_URL_PREFIX or ":memory:" in db_url) and not ALLOW_IN_MEMORY_DB:
        raise vol.Invalid("In-memory SQLite database is not supported")

    return db_url


CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(DOMAIN, default=dict): vol.All(
            cv.deprecated(CONF_PURGE_INTERVAL),
            cv.deprecated(CONF_DB_INTEGRITY_CHECK),
            FILTER_SCHEMA.extend(
                {
                    vol.Optional(CONF_AUTO_PURGE, default=True): cv.boolean,
                    vol.Optional(CONF_AUTO_REPACK, default=True): cv.boolean,
                    vol.Optional(CONF_PURGE_KEEP_DAYS, default=10): vol.All(
                        vol.Coerce(int), vol.Range(min=1)
                    ),
                    vol.Optional(CONF_PURGE_INTERVAL, default=1): cv.positive_int,
                    vol.Optional(CONF_DB_URL): vol.All(cv.string, validate_db_url),
                    vol.Optional(
                        CONF_COMMIT_INTERVAL, default=DEFAULT_COMMIT_INTERVAL
                    ): cv.positive_int,
                    vol.Optional(
                        CONF_DB_MAX_RETRIES, default=DEFAULT_DB_MAX_RETRIES
                    ): cv.positive_int,
                    vol.Optional(
                        CONF_DB_RETRY_WAIT, default=DEFAULT_DB_RETRY_WAIT
                    ): cv.positive_int,
                    vol.Optional(
                        CONF_DB_INTEGRITY_CHECK, default=DEFAULT_DB_INTEGRITY_CHECK
                    ): cv.boolean,
                }
            ),
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def get_instance(hass: HomeAssistant) -> Recorder:
    """Get the recorder instance."""
    instance: Recorder = hass.data[DATA_INSTANCE]
    return instance


@bind_hass
def is_entity_recorded(hass: HomeAssistant, entity_id: str) -> bool:
    """Check if an entity is being recorded.

    Async friendly.
    """
    if DATA_INSTANCE not in hass.data:
        return False
    instance: Recorder = hass.data[DATA_INSTANCE]
    return instance.entity_filter(entity_id)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the recorder."""
    hass.data[DOMAIN] = {}
    exclude_attributes_by_domain: dict[str, set[str]] = {}
    hass.data[EXCLUDE_ATTRIBUTES] = exclude_attributes_by_domain
    conf = config[DOMAIN]
    # entity_filter = convert_include_exclude_filter(conf)
    auto_purge = conf[CONF_AUTO_PURGE]
    auto_repack = conf[CONF_AUTO_REPACK]
    keep_days = conf[CONF_PURGE_KEEP_DAYS]
    # commit_interval = conf[CONF_COMMIT_INTERVAL]
    # db_max_retries = conf[CONF_DB_MAX_RETRIES]
    # db_retry_wait = conf[CONF_DB_RETRY_WAIT]
    # db_url = conf.get(CONF_DB_URL) or DEFAULT_URL.format(
    #     hass_config_path=hass.config.path(DEFAULT_DB_FILE)
    # )
    # AIS dom fix - get recorder config from file
    commit_interval = 60
    db_max_retries = 10
    db_retry_wait = 3
    db_integrity_check = conf[CONF_DB_INTEGRITY_CHECK]
    try:
        import json

        import homeassistant.components.ais_dom.ais_global as ais_global

        if ais_global.G_DB_SETTINGS_INFO is None:
            with open(
                hass.config.config_dir + ais_global.G_DB_SETTINGS_INFO_FILE
            ) as json_file:
                ais_global.G_DB_SETTINGS_INFO = json.load(json_file)
        db_url = ais_global.G_DB_SETTINGS_INFO["dbUrl"]
        if db_url == "":
            return
        if db_url == "sqlite:///:memory:":
            keep_days = 5
        else:
            if db_url.startswith("sqlite://///"):
                # DB in file
                from homeassistant.components import ais_usb

                if ais_usb.is_usb_url_valid_external_drive(db_url) is not True:
                    _LOGGER.error(
                        "Invalid external drive: %s selected for recording! ", db_url
                    )
                    # enable recorder in memory
                    db_url = "sqlite:///:memory:"
                    keep_days = 5
                else:
                    keep_days = 10
                    if "dbKeepDays" in ais_global.G_DB_SETTINGS_INFO:
                        keep_days = int(ais_global.G_DB_SETTINGS_INFO["dbKeepDays"])
        db_include = ais_global.G_DB_SETTINGS_INFO.get("dbInclude", {})
        db_exclude = ais_global.G_DB_SETTINGS_INFO.get("dbExclude", {})

    except Exception as e:
        # enable recorder in memory
        _LOGGER.error(
            "Get recorder config from file error, enable recorder in memory " + str(e)
        )
        db_url = "sqlite:///:memory:"
        keep_days = 5
        db_include = ais_global.G_AIS_INCLUDE_DB_DEFAULT
        db_exclude = ais_global.G_AIS_EXCLUDE_DB_DEFAULT

    # ais exclude
    exclude = ais_global.G_AIS_EXCLUDE_DB_DEFAULT
    include = {"domains": [], "entity_globs": [], "entities": []}
    if db_include != {}:
        include["domains"].extend(db_include.get("domains", {}))
        include["entity_globs"].extend(db_include.get("entity_globs", {}))
        include["entities"].extend(db_include.get("entities", {}))
    if db_exclude != {}:
        exclude["domains"].extend(db_exclude.get("domains", {}))
        exclude["entity_globs"].extend(db_exclude.get("entity_globs", {}))
        exclude["entities"].extend(db_exclude.get("entities", {}))

    conf[CONF_EXCLUDE] = exclude
    conf[CONF_INCLUDE] = include
    entity_filter = convert_include_exclude_filter(conf)

    exclude = conf[CONF_EXCLUDE]

    exclude_t = exclude.get(CONF_EVENT_TYPES, [])
    if EVENT_STATE_CHANGED in exclude_t:
        _LOGGER.warning(
            "State change events are excluded, recorder will not record state changes."
            "This will become an error in Home Assistant Core 2022.2"
        )
    instance = hass.data[DATA_INSTANCE] = Recorder(
        hass=hass,
        auto_purge=auto_purge,
        auto_repack=auto_repack,
        keep_days=keep_days,
        commit_interval=commit_interval,
        uri=db_url,
        db_max_retries=db_max_retries,
        db_retry_wait=db_retry_wait,
        entity_filter=entity_filter,
        exclude_t=exclude_t,
        exclude_attributes_by_domain=exclude_attributes_by_domain,
    )
    instance.async_initialize()
    instance.async_register()
    instance.start()
    async_register_services(hass, instance)
    statistics.async_setup(hass)
    websocket_api.async_setup(hass)
    await async_process_integration_platforms(hass, DOMAIN, _process_recorder_platform)

    return await instance.async_db_ready


async def _process_recorder_platform(
    hass: HomeAssistant, domain: str, platform: Any
) -> None:
    """Process a recorder platform."""
    instance: Recorder = hass.data[DATA_INSTANCE]
    instance.queue_task(AddRecorderPlatformTask(domain, platform))
