"""Contains the collections framework, legacy collection classes, event
model, date and time facilities, internationalization, and miscellaneous
utility classes (a string tokenizer, a random-number generator, and a
bit array).
"""

from __future__ import print_function

__all__ = ["Date", "EventObject", "Locale"]

from typing import Optional

from java.lang import Object


class Date(Object):
    """The class Date represents a specific instant in time, with
    millisecond precision.
    """

    def __init__(self, date=None):
        # type: (Optional[long]) -> None
        print(self, date)

    def __cmp__(self, other):
        # type: (Date) -> bool
        pass

    def __ge__(self, other):
        # type: (Date) -> bool
        pass

    def __gt__(self, other):
        # type: (Date) -> bool
        pass

    def __lt__(self, other):
        # type: (Date) -> bool
        pass

    def after(self, when):
        # type: (Date) -> bool
        pass

    def before(self, when):
        # type: (Date) -> bool
        pass

    def compareTo(self, anotherDate):
        # type: (Date) -> int
        pass

    def getTime(self):
        # type: () -> long
        pass

    def setTime(self, time):
        # type: (long) -> None
        pass


class EventObject(Object):
    """The root class from which all event state objects shall be
    derived.

    All Events are constructed with a reference to the object, the
    "source", that is logically deemed to be the object upon which the
    Event in question initially occurred upon.
    """

    source = None  # type: Object

    def __init__(self, source):
        # type: (Object) -> None
        self.source = source

    def getSource(self):
        return self.source


class classproperty(property):  # pylint: disable=invalid-name
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class Locale(Object):
    """A Locale object represents a specific geographical, political, or
    cultural region. An operation that requires a Locale to perform its
    task is called locale-sensitive and uses the Locale to tailor
    information for the user. For example, displaying a number is a
    locale-sensitive operation; the number should be formatted according
    to the customs and conventions of the user's native country, region,
    or culture.
    """

    country = None  # type: Optional[str]
    language = None  # type: str
    variant = None  # type: Optional[str]

    def __init__(self, language, country=None, variant=None):
        # type: (str, Optional[str], Optional[str]) -> None
        self.language = language
        self.country = country
        self.variant = variant

    def __repr__(self):
        return "{!r}".format(self.__str__())

    def __str__(self):
        ret = self.language
        if self.country:
            ret += "_{}".format(self.country)
        if self.variant:
            ret += "_{}".format(self.variant)
        return unicode(ret)

    @classproperty
    def CANADA(self):
        return Locale("en", "CA")

    @classproperty
    def CANADA_FRENCH(self):
        return Locale("fr", "CA")

    @classproperty
    def CHINA(self):
        return Locale("zh", "CN")

    @classproperty
    def CHINESE(self):
        return Locale("zh")

    @classproperty
    def ENGLISH(self):
        return Locale("en")

    @classproperty
    def FRANCE(self):
        return Locale("fr", "FR")

    @classproperty
    def FRENCH(self):
        return Locale("fr")

    @classproperty
    def GERMAN(self):
        return Locale("de")

    @classproperty
    def GERMANY(self):
        return Locale("de", "DE")

    @classproperty
    def ITALIAN(self):
        return Locale("it")

    @classproperty
    def ITALY(self):
        return Locale("it", "IT")

    @classproperty
    def JAPAN(self):
        return Locale("ja", "JP")

    @classproperty
    def JAPANESE(self):
        return Locale("ja")

    @classproperty
    def KOREA(self):
        return Locale("ko", "KR")

    @classproperty
    def KOREAN(self):
        return Locale("ko")

    @classproperty
    def PRC(self):
        return self.CHINA

    @classproperty
    def SIMPLIFIED_CHINESE(self):
        return self.CHINA

    @classproperty
    def TAIWAN(self):
        return Locale("zh", "TW")

    @classproperty
    def TRADITIONAL_CHINESE(self):
        return Locale("zh", "TW")

    @classproperty
    def UK(self):
        return Locale("en", "GB")

    @classproperty
    def US(self):
        return Locale("en", "US")
