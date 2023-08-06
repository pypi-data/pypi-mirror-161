# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name="auth-get-sso-cookie",
    version="2.2.0",
    description="Utility for aquiring CERN Single Sign-On cookie using Kerberos credentials.",
    long_description="auth-get-sso-cookie acquires CERN Single Sign-On cookie using Kerberos credentials allowing for automated access to CERN SSO protected pages using tools alike wget, curl or similar.",
    url="https://gitlab.cern.ch/authzsvc/docs/auth-get-sso-cookie",
    # Author details
    author="Asier Aguado",
    author_email="asier.aguado@cern.ch",
    # Choose your license
    license="MIT",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
    ],
    # What does your project relate to?
    keywords="authentication sso cern",
    py_modules=["cern_sso", "command_line_tools", "old_cern_sso"],
    packages=find_packages(),
    package_data={'auth_get_sso_cookie': ['auth_get_sso_cookie/*']},
    install_requires=["requests", "requests-gssapi", "beautifulsoup4"],
    # only compatible with linux, we prefer the multi-platform entry_points
    # scripts=["auth-get-sso-cookie", "auth-get-sso-token"],
    entry_points={
        "console_scripts": [
            "auth-get-sso-cookie=command_line_tools:auth_get_sso_cookie",
            "auth-get-sso-token=command_line_tools:auth_get_sso_token",
            "auth-get-user-token=command_line_tools:auth_get_user_token"
        ],
    },
)
