"""Activate, get and deactivate translations."""
from __future__ import annotations

import gettext as gettext_module
import os.path
from threading import local

__all__ = ["activate", "deactivate", "decimal_separator", "thousands_separator"]

_TRANSLATIONS: dict[str | None, gettext_module.NullTranslations] = {
    None: gettext_module.NullTranslations()
}
_CURRENT = local()


# Mapping of locale to thousands separator
_THOUSANDS_SEPARATOR = {
    "de_DE": ".",
    "fr_FR": " ",
    "pt_BR": ".",
}

# Mapping of locale to decimal separator
_DECIMAL_SEPARATOR = {
    "de_DE": ",",
    "pt_BR": ",",
}


def _get_default_locale_path() -> str | None:
    try:
        if __file__ is None:
            return None
        return os.path.join(os.path.dirname(__file__), "locale")
    except NameError:
        return None


def get_translation() -> gettext_module.NullTranslations:
    try:
        return _TRANSLATIONS[_CURRENT.locale]
    except (AttributeError, KeyError):
        return _TRANSLATIONS[None]


def activate(locale: str, path: str | None = None) -> gettext_module.NullTranslations:
    """Activate internationalisation.

    Set `locale` as current locale. Search for locale in directory `path`.

    Args:
        locale (str): Language name, e.g. `en_GB`.
        path (str): Path to search for locales.

    Returns:
        dict: Translations.

    Raises:
        Exception: If humanize cannot find the locale folder.
    """
    if path is None:
        path = _get_default_locale_path()

    if path is None:
        raise Exception(
            "Humanize cannot determinate the default location of the 'locale' folder. "
            "You need to pass the path explicitly."
        )
    if locale not in _TRANSLATIONS:
        translation = gettext_module.translation("humanize", path, [locale])
        _TRANSLATIONS[locale] = translation
    _CURRENT.locale = locale
    return _TRANSLATIONS[locale]


def deactivate() -> None:
    """Deactivate internationalisation."""
    _CURRENT.locale = None


def _gettext(message: str) -> str:
    """Get translation.

    Args:
        message (str): Text to translate.

    Returns:
        str: Translated text.
    """
    return get_translation().gettext(message)


def _pgettext(msgctxt: str, message: str) -> str:
    """Fetches a particular translation.

    It works with `msgctxt` .po modifiers and allows duplicate keys with different
    translations.

    Args:
        msgctxt (str): Context of the translation.
        message (str): Text to translate.

    Returns:
        str: Translated text.
    """
    # This GNU gettext function was added in Python 3.8, so for older versions we
    # reimplement it. It works by joining `msgctx` and `message` by '4' byte.
    try:
        # Python 3.8+
        return get_translation().pgettext(msgctxt, message)
    except AttributeError:
        # Python 3.7 and older
        key = msgctxt + "\x04" + message
        translation = get_translation().gettext(key)
        return message if translation == key else translation


def _ngettext(message: str, plural: str, num: int) -> str:
    """Plural version of _gettext.

    Args:
        message (str): Singular text to translate.
        plural (str): Plural text to translate.
        num (int): The number (e.g. item count) to determine translation for the
            respective grammatical number.

    Returns:
        str: Translated text.
    """
    return get_translation().ngettext(message, plural, num)


def _gettext_noop(message: str) -> str:
    """Mark a string as a translation string without translating it.

    Example usage:
    ```python
    CONSTANTS = [_gettext_noop('first'), _gettext_noop('second')]
    def num_name(n):
        return _gettext(CONSTANTS[n])
    ```

    Args:
        message (str): Text to translate in the future.

    Returns:
        str: Original text, unchanged.
    """
    return message


def _ngettext_noop(singular: str, plural: str) -> tuple[str, str]:
    """Mark two strings as pluralized translations without translating them.

    Example usage:
    ```python
    CONSTANTS = [ngettext_noop('first', 'firsts'), ngettext_noop('second', 'seconds')]
    def num_name(n):
        return _ngettext(*CONSTANTS[n])
    ```

    Args:
        singular (str): Singular text to translate in the future.
        plural (str): Plural text to translate in the future.

    Returns:
        tuple: Original text, unchanged.
    """
    return singular, plural


def thousands_separator() -> str:
    """Return the thousands separator for a locale, default to comma.

    Returns:
         str: Thousands separator.
    """
    try:
        sep = _THOUSANDS_SEPARATOR[_CURRENT.locale]
    except (AttributeError, KeyError):
        sep = ","
    return sep


def decimal_separator() -> str:
    """Return the decimal separator for a locale, default to dot.

    Returns:
         str: Decimal separator.
    """
    try:
        sep = _DECIMAL_SEPARATOR[_CURRENT.locale]
    except (AttributeError, KeyError):
        sep = "."
    return sep
