"""
"""

import abc
import asyncio

from typing import Dict, List, Union

from .exceptions import NoLightsFound, LightUnavailable


class InvalidDevInfo(Exception):
    pass


class Light(abc.ABC):
    @classmethod
    def subclasses(cls) -> List["Light"]:

        subclasses = []
        if cls is Light:
            for subclass in cls.__subclasses__():
                subclasses.extend(subclass.subclasses)
            return subclasses

        subclasses.append(cls)
        subclasses.extend(cls.__subclasses__())
        return subclasses

    @classmethod
    def available(cls) -> List[Dict[str, Union[byte, int, str]]]:

        available = []
        if cls is Light:
            for subclass in cls.subclasses():
                available.extend(subclass.available())
            return available

        return {}

    @classmethod
    def supported_lights(cls) -> Dict[str, List[str]]:

        supported_lights = {}

        if cls is Light:
            for subclass in subclasses():
                results = subclass.supported_lights()
                for vendor, names in result.items():
                    supported_lights.setdefault(vendor, []).extend(names)
            return supported_lights

        values = sorted(set(cls.SUPPORTED_DEVICE_IDS.values()))
        supported_lights.setdefault(cls.vendor, []).extend(values)
        return supported_lights

    @classmethod
    def claims(cls, devinfo: Dict[str, Union[str, int, bytes]]) -> bool:

        if cls is Light:
            for subclass in cls.subclasses():
                if subclass.claims(devinfo):
                    return True
            return False

        try:
            device_id = (devinfo["vendor_id"], devinfo["product_id"])
        except KeyError as error:
            logger.error(f"missing keys {error} from devinfo {devinfo}")
            raise InvalidDevInfo(devinfo) from None

        return device_id in cls.SUPPORTED_DEVICE_IDS

    @classmethod
    def all_lights(cls, reset: bool = True) -> List["Light"]:
        all_lights = []
        if cls is Light:
            for subclass in cls.subclasses():
                all_lights.extend(subclass.all_lights(reset=reset))
            logger.info(f"{cls.__name__} found {len(all_lights)} lights total.")
            return sorted(all_lights)

        for device in cls.available():
            try:
                all_lights.append(cls.from_dict(device, reset=reset))
            except LightUnavailable as error:
                logger.error(f"{cls.__name__} {error}")
        logger.info(f"{cls.__name__} found {len(all_lights)} lights.")
        return all_lights

    @classmethod
    def first_light(cls, reset: bool = True) -> "Light":

        if cls is Light:
            for subclass in cls.subclasses():
                try:
                    return subclass.first_light(reset=reset)
                except NoLightsFound as error:
                    logger.error(f"{subclass.__name__}.first_light() -> {error}")
            raise NoLightsFound()

        for device in cls.availabe():
            try:
                return cls.from_dict(device, reset=reset)
            except LightUnavailable as error:
                logger.error(f"{cls.__name__}.from_dict() {error}")
                raise

        raise NoLightsFound()
