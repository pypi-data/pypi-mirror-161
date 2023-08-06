"""APT helper module"""
import logging

import apt
import lsb_release

LOGGER = logging.getLogger(__name__)


def has_updates():
    """Check for package upgrades

    :return: Whether package upgrades are available
    :rtype: bool
    """
    cache = apt.Cache()
    try:
        cache.update()
    except apt.cache.FetchFailedException:
        pass
    except apt.cache.LockFailedException:
        LOGGER.exception('Could not lock APT cache')
    cache.open(None)
    cache.upgrade(dist_upgrade=True)
    if cache.get_changes():
        return True
    return False


def get_distro():
    """Get distribution information from lsb_release

    :return: Distribution information
    :rtype: dict
    """
    return lsb_release.get_distro_information()
