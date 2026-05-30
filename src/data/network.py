"""HTTP session helpers and SSL setup for Windows/macOS certificate stores."""

from __future__ import annotations

import os
import ssl
import warnings

import requests
import urllib3

_ssl_configured = False


def configure_ssl(*, insecure: bool = False) -> None:
    """
    Configure HTTPS certificate verification before any market-data requests.

    On Windows, Python often ships with certifi only, which misses certificates
    from the system store (common on corporate networks). truststore fixes that
    by using the OS trust store while keeping verification enabled.
    """
    global _ssl_configured
    if _ssl_configured:
        return
    _ssl_configured = True

    # yfinance 1.4+ defaults to curl_cffi, which does not use truststore on Windows.
    # Use requests so OS certificate store integration works. Must be set before
    # yfinance is imported.
    os.environ.setdefault("YF_DISABLE_CURL_CFFI", "1")

    if insecure:
        warnings.warn(
            "SSL verification disabled (--insecure-ssl). Use only on trusted networks.",
            stacklevel=2,
        )
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        ssl._create_default_https_context = ssl._create_unverified_context  # noqa: SLF001
        return

    try:
        import truststore

        truststore.inject_into_ssl()
    except ImportError:
        pass
    else:
        return

    try:
        import certifi

        bundle = certifi.where()
        defaults = ssl.get_default_verify_paths()
        if defaults.cafile != bundle:
            ssl_context = ssl.create_default_context(cafile=bundle)
            ssl._create_default_https_context = lambda: ssl_context  # noqa: SLF001
    except ImportError:
        pass


def build_session(*, insecure: bool = False) -> requests.Session:
    configure_ssl(insecure=insecure)
    session = requests.Session()
    if insecure:
        session.verify = False
    return session
