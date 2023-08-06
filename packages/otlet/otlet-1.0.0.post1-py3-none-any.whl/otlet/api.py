"""
otlet.api
======================
Classes used by otlet for storing data returned from PyPI Web API.
"""
#
# Copyright (c) 2022 Noah Tanner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import re
import time
import datetime
import json
from http.client import HTTPResponse
from urllib.request import urlopen
from urllib.error import HTTPError
from typing import Any, Optional, Dict, List, NamedTuple, Tuple, Union
from types import SimpleNamespace
from .markers import DEPENDENCY_ENVIRONMENT_MARKERS
from .packaging.version import Version, LegacyVersion, parse as parse_version
from .exceptions import (
    OtletError,
    NotPopulatedError,
    PyPIServiceDown,
    PyPIPackageNotFound,
    PyPIPackageVersionNotFound,
)


class _PackageBase:
    """
    Base for :class:`~PackageObject` and :class:`~PackageInfoObject`. Should not be directly instantiated.
    """

    def __init__(self, package_name: str, release: Optional[str] = None) -> None:
        # parse package_name for extras
        _parsed_name = (
            re.compile(r"[\[\]]").sub(",", package_name).strip(",").split(",")
        )
        self.name = _parsed_name[0]
        if len(_parsed_name) == 2:
            self.extras = [_parsed_name[1]]
        else:
            self.extras = []

        self.release = release
        self._http_response = self._attempt_request()
        self.http_response = json.loads(self._http_response.readlines()[0].decode())

    def _attempt_request(self) -> HTTPResponse:
        """Attempt PyPI API request for package. You should not need to call this function directly."""
        _pkexists = False
        try:
            res = urlopen(f"https://pypi.org/pypi/{self.name}/json")
            _pkexists = True
            if self.release:
                res = urlopen(f"https://pypi.org/pypi/{self.name}/{self.release}/json")
        except HTTPError as err:
            if err.code == 404:
                if _pkexists:
                    raise PyPIPackageVersionNotFound(self.name, self.release) from err # type: ignore
                raise PyPIPackageNotFound(self.name) from err
            if err.code == 503:
                raise PyPIServiceDown from err
            else:
                raise err
        return res


class PackageInfoObject(_PackageBase):
    """
    Object containing information about a given PyPI package. Data taken from the 'info' API response key.

    :param package_name: Name of PyPI package to query
    :type package_name: str

    :param release: Specific version to query (optional)
    :type release: str

    :param perform_request: Whether or not to perform a fresh API request upon instantiation
    :type perform_request: bool

    :param http_response: JSON-parsed HTTP Response to be used to populate object (optional)
    :type http_response: Dict[str, Any]

    :param disregard_extras: Whether or not the dependency parser should care about extras when parsing (Default: False)
    :type disregard_extras: bool

    :param disregard_markers: Whether or not the dependency parser should care about environment markers (excluding extras) when parsing (Default: False)
    :type disregard_markers: bool

    :var author: Author of the package
    :vartype author: str

    :var author_email: Email of the package author
    :vartype author_email: str

    :var bugtrack_url: Legacy attribute (deprecated) (Use project_urls.Tracker instead)
    :vartype bugtrack_url: Optional[str]

    :var classifiers: PEP 301 package classifiers
    :vartype classifiers: List[str]

    :var description: Package description
    :vartype description: Optional[str]

    :var description_content_type: Type format for package description, if applicable
    :vartype description_content_type: Optional[str]

    :var docs_url: Legacy attribute (deprecated) (Use project_urls.Documentation instead)
    :vartype docs_url: Optional[str]

    :var download_url: Legacy attribute (deprecated)
    :vartype download_url: Optional[str]

    :var downloads: Legacy attribute (deprecated)
    :vartype downloads: Dict[str, int]

    :var home_page: URL for package's home page
    :vartype home_page: Optional[str]

    :var http_response: Dictionary containing information from the PyPI API response object.
    :vartype http_response: Dict[str, Any]

    :var keywords: Keywords used to help searching for package
    :vartype keywords: Optional[str]

    :var license: Package license type
    :vartype license: Optional[str]

    :var maintainer: Maintainer of the package
    :vartype maintainer: Optional[str]

    :var maintainer_email: Email of the package maintainer
    :vartype maintainer_email: Optional[str]

    :var name: Package name
    :vartype name: str

    :var package_url: Main URL for the package
    :vartype package_url: str

    :var platform: Legacy attribute (deprecated)
    :vartype platform: Optional[str]

    :var possible_extras: List of extras that are possible for the package.
    :vartype possible_extras: Tuple[str]

    :var project_url: Main URL for the package
    :vartype project_url: str

    :var project_urls: Additional relevant URLs for the package
    :vartype project_urls: Optional[Dict[str, str]]

    :var release_url: URL for current release version of the package
    :vartype release_url: str

    :var requires_dist: A dictionary containing the packages dependencies and their constraints
    :vartype requires_dist: Optional[List[:class:`~PackageDependencyObject`]]

    :var requires_python: Python version constraints
    :vartype requires_python: Optional[str]

    :var summary: Short summary of the package's function
    :vartype summary: Optional[str]

    :var version: Package version (current stable version, if not specified)
    :vartype version: Union[:class:`packaging.version.Version`, :class:`packaging.version.LegacyVersion`]

    :var yanked: Whether or not this version has been yanked
    :vartype yanked: bool

    :var yanked_reason: If this version has been yanked, reason as to why
    :vartype yanked_reason: Optional[str]

    .. versionchanged:: 1.0.0
        Converted from dataclass into callable object.
    """

    def __init__(
        self,
        package_name,
        package_extras = None,
        release = None,
        perform_request = True,
        http_response = None,
        disregard_extras = False,
        disregard_markers = False,
    ):
        if perform_request:
            super().__init__(package_name, release)
        elif http_response:
            self.http_response = http_response
        else:
            raise OtletError(
                "If not performing a new HTTP request, you must supply a dictionary-parsed HTTPResponse into 'http_response'."
            )

        for k, v in self.http_response["info"].items():
            if v == "":
                self.__dict__[k] = None
            elif k == "version":
                self.__dict__[k] = parse_version(v)
            elif k == "requires_dist":
                _parsed, self.possible_extras = self._parse_dependencies(
                    v, package_extras, disregard_extras, disregard_markers
                )
                self._parsed_deps = _parsed
                if _parsed:
                    _obj = [
                        PackageDependencyObject(
                            k, v["version_constraints"], v["markers"], v["extras"]
                        )
                        for k, v in _parsed.items()
                    ]
                    self.__dict__[k] = _obj
                else:
                    self.__dict__[k] = None
            else:
                self.__dict__[k] = v

    @staticmethod
    def _parse_dependencies(reqs, extras, disregard_extras, disregard_markers):
        # if you're reading this, i'm so sorry
        # i know this is bad, but honestly it works and i'm too scared
        # to touch it, at least for right now. so yeah.

        if not reqs:
            return (None, None)
        if not extras:
            extras = []

        packages: Dict[Any, Any] = {}
        root_extras = set()
        for req in reqs:
            req_split = req.split(";")

            _pkg = req_split[0].split()  # package name
            _p_match = re.match(
                r"(\S+?)([!><=]+)(\S+)", _pkg[0]
            )  # match for non-parenthetical version constraints (i.e. 'coverage[toml]>=5.0.2')
            if not _p_match:
                pkg = _pkg[0]
                pkg_vcon = (
                    _pkg[1] if len(_pkg) > 1 else None
                )  # dependency version constraint(s)
            else:
                pkg = _p_match.group(1)
                pkg_vcon = _p_match.group(2) + _p_match.group(
                    3
                )  # dependency version constraint(s)

            pkgq = (
                req_split[1].split(" and ") if len(req_split) > 1 else None
            )  # installation qualifiers (extras, platform dependencies, etc.)
            if (
                pkg not in packages.keys()
            ):  # check if pkg key has already been initialized, due to some packages stating their dependencies multiple times (i.e. 'argon2-cffi')
                packages[pkg] = {
                    "version_constraints": pkg_vcon,
                    "markers": {},
                    "extras": [],
                }
            if (
                not pkgq
            ):  # if the dependency has no markers, then no additional parsing is needed
                continue
            for constraint in pkgq:
                _c = constraint.strip().split(" or ")
                c = []
                if len(_c) == 1:
                    c = [re.sub(r'[()\s"\']', "", constraint.strip())]
                else:
                    for i in _c:
                        c.append(re.sub(r'[()\s"\']', "", i.strip()))

                _m = []
                for i in c:
                    _m.append(re.match(r"(\w+)([!=<>]+)(\S+)", i))

                for m in _m:
                    if m.group(1) in ["python_version", "python_full_version", "implementation_version"]:  # type: ignore
                        packages[pkg]["markers"][m.group(1)] = m.group(2) + m.group(3)  # type: ignore
                        continue
                    if m.group(1) == "extra":  # type: ignore
                        packages[pkg]["extras"].append(m.group(3))  # type: ignore
                        continue
                    packages[pkg]["markers"][m.group(1)] = m.group(3)  # type: ignore

        # extra checker
        if not disregard_extras:
            for k, v in packages.copy().items():
                hitcount = 0
                if v.get("extras"):
                    for extra in v["extras"]:
                        root_extras.add(extra)
                        if extra not in extras:
                            hitcount += 1
                            if hitcount == len(v["extras"]):
                                try:
                                    packages.pop(k)
                                except KeyError:
                                    continue

        # environment marker checker
        if not disregard_markers:
            # dictionary holding each package, with info on whether or not
            # every marker constraint is met for a given package
            _pkg_wmarks: dict = {}
            for k in packages:
                _pkg_wmarks[k] = []
            for k, v in packages.copy().items():
                for _k, _v in v["markers"].items():
                    # seperate if condition for python_version-like markers
                    # uses Version.fits_constraints() method to confirm constraint(s)
                    if _k in [
                        "python_version",
                        "python_full_version",
                        "implementation_version",
                    ]:
                        if DEPENDENCY_ENVIRONMENT_MARKERS[_k].fits_constraints(
                            re.sub("[)(]", "", _v).split(",")
                        ):
                            _pkg_wmarks[k].append(True)
                        else:
                            _pkg_wmarks[k].append(False)
                    # regular if condition for all other markers
                    elif _v == DEPENDENCY_ENVIRONMENT_MARKERS[_k]:
                        _pkg_wmarks[k].append(True)
                    else:
                        _pkg_wmarks[k].append(False)
            for k, v in _pkg_wmarks.items():
                if not all(v):
                    packages.pop(k)

        return packages, tuple(root_extras)


class URLReleaseObject(NamedTuple):
    """
    Object containing information about a specific release of a PyPI package. Data taken from either the 'urls' or 'releases' API response keys. Should not be directly called.

    :param comment_text: Legacy attribute (deprecated)
    :type comment_text: str

    :param digests: Checksum digests for package release
    :type digests: :class:`types.SimpleNamespace`

    :param downloads: Legacy attribute (deprecated)
    :type downloads: int

    :param filename: Name of the release file
    :type filename: str

    :param has_sig: Presence of PGP signature with release
    :type has_sig: bool

    :param md5_digest: MD5 checksum digest for package release
    :type md5_digest: str

    :param packagetype: Type of package release
    :type packagetype: str

    :param python_version: PEP 425-compliant compatibility tag ('source' if source dist)
    :type python_version: str

    :param requires_python: Version constraints for the given release
    :type requires_python: Optional[str]

    :param size: File size, in bytes
    :type size: int

    :param upload_time: Datetime object for when release was uploaded to PyPI
    :type upload_time: :class:`datetime.datetime`

    :param upload_time_iso_8601: ISO 8601 compliant representation of when release was uploaded to PyPI
    :type upload_time_iso_8601: str

    :param url: Package release's download URL
    :type url: str

    :param yanked: Whether or not this version has been yanked
    :type yanked: bool

    :param yanked_reason: If this version has been yanked, reason as to why
    :type yanked_reason: Optional[str]
    """

    comment_text: str
    digests: SimpleNamespace
    downloads: int
    filename: str
    has_sig: bool
    md5_digest: str
    packagetype: str
    python_version: str
    requires_python: Optional[str]
    size: int
    upload_time: datetime.datetime
    upload_time_iso_8601: str
    url: str
    yanked: bool
    yanked_reason: Optional[str]

    @classmethod
    def construct(cls, url_release_item):
        return cls(
            url_release_item["comment_text"],
            SimpleNamespace(**url_release_item["digests"]),
            url_release_item["downloads"],
            url_release_item["filename"],
            url_release_item["has_sig"],
            url_release_item["md5_digest"],
            url_release_item["packagetype"],
            url_release_item["python_version"],
            url_release_item["requires_python"],
            url_release_item["size"],
            datetime.datetime(
                *time.strptime(
                    url_release_item.get(
                        "upload_time"
                    ),
                    "%Y-%m-%dT%H:%M:%S",
                )[:6]
            ),
            url_release_item["upload_time_iso_8601"],
            url_release_item["url"],
            url_release_item["yanked"],
            url_release_item["yanked_reason"] or None,
        )


class PackageVulnerabilitiesObject(NamedTuple):
    """
    Contains information about applicable package vulnerabilities, mainly sourced from 'https://osv.dev/'. Data taken from the 'vulnerabilities' API response key. Should not be directly called.

    :param aliases: Alias name(s) for this vulnerability, usually a 'CVE-ID'
    :type aliases: List[str]

    :param details: Details about the vulnerability
    :type details: str

    :param fixed_in: Version(s) that the vulnerability was patched in
    :type fixed_in: List[Union[:class:`packaging.version.Version`, :class:`packaging.version.LegacyVersion`]]

    :param id: 'PYSEC-ID' for this vulnerability
    :type id: str

    :param link: Link to web page where this information was sourced from, usually an 'https://osv.dev/' link
    :type link: str

    :param source: Where this vulnerability information was sourced from, usually 'osv'
    :type source: str

    .. versionadded:: 0.4.0
    """

    aliases: List[str]
    details: str
    fixed_in: List[str]
    id: str
    link: str
    source: str

    @classmethod
    def construct(cls, vuln_dict):
        return cls(
            vuln_dict["aliases"],
            vuln_dict["details"],
            [parse_version(v) for v in vuln_dict["fixed_in"]],
            vuln_dict["id"],
            vuln_dict["link"],
            vuln_dict["source"],
        )


class PackageObject(_PackageBase):
    """
    Object containing all relevant information for a given PyPI package.

    :param package_name: Name of PyPI package to query
    :type package_name: str

    :param release: Specific version to query (optional)
    :type release: str

    :param disregard_extras: Whether or not the dependency parser should care about extras when parsing (Default: False)
    :type disregard_extras: bool

    :param disregard_markers: Whether or not the dependency parser should care about environment markers (excluding extras) when parsing (Default: False)
    :type disregard_markers: bool

    :var info: Info about a given package version
    :vartype info: :class:`~PackageInfoObject`

    :var last_serial: The most recent serial ID number for the package.
    :vartype last_serial: int

    :var releases: Dictionary containing all release objects for a given package
    :vartype releases: Optional[Dict[str, List[:class:`~URLReleaseObject`]]]

    :var urls: List of package releases for the given version
    :vartype urls: List[:class:`~URLReleaseObject`]

    :var vulnerabilities: List of objects containing vulnerability details for the given version, if applicable.
    :vartype vulnerabilities: Optional[List[:class:`~PackageVulnerabilitiesObject`]]

    .. versionchanged:: 1.0.0
        Converted from dataclass into callable object.
    """

    def __init__(self, package_name, release = None, **kwargs):
        super().__init__(package_name, release)
        self.info = PackageInfoObject(
            package_name, self.extras, release, False, self.http_response, **kwargs
        )
        self.last_serial = self.http_response["last_serial"]
        self.releases = None
        self.urls = [URLReleaseObject.construct(_) for _ in self.http_response["urls"]]
        self.vulnerabilities = [
            PackageVulnerabilitiesObject.construct(_)
            for _ in self.http_response["vulnerabilities"]
        ] or None

        if not release:
            self.releases = {}
            for k, v in self.http_response["releases"].items():
                if not v:
                    self.releases[k] = None
                self.releases[k] = [URLReleaseObject.construct(_) for _ in v]

    def populate_dependencies(self, depth=0):
        """Populate all dependencies for the package."""
        for dep in self.dependencies:
            dep.populate(depth)

    @property
    def canonicalized_name(self) -> str:
        return (
            re.compile(r"[-_.]+").sub("-", self.info.name).lower()
        )  # stolen from packaging module

    @property
    def version(self) -> str:
        return str(self.info.version)

    @property
    def release_name(self) -> str:
        return f"{self.name} v{self.version}"

    @property
    def upload_time(self) -> Optional[datetime.datetime]:
        try:
            return self.urls[0].upload_time 
        except IndexError:
            return None

    @property
    def dependencies(self) -> list:
        return self.info.requires_dist

    @property
    def dependency_count(self) -> int:
        if not self.info.requires_dist:
            return 0
        return len(self.info.requires_dist)


class PackageDependencyObject(PackageObject):
    """Object containing information about a specific dependency of a PyPI package. Should not be directly called.

    :var name: Name of PyPI package
    :vartype name: str

    :var version_constraints: Version constraints that the given dependency must fulfill (i.e. '[">=3.1.2", "<4.0"]')
    :vartype version_constraints: List[str]

    :var markers: A dictionary containing all relevent environment markers pursuant to PEP 508 (excluding extras)
    :vartype markers: Dict[str, str]

    :var requires_extras: A list of extras that are required for the dependency to be installed with the package
    :vartype requires_extras: List[str]

    :var is_populated: Boolean value stating whether or not the object has been populated with info from PyPI
    :vartype is_populated: bool

    .. versionadded:: 1.0.0
    """

    def __init__(
        self,
        package_name,
        version_constraints = None,
        markers = None,
        extras = None,
    ):
        self.name = package_name
        self.version_constraints = (
            re.sub(r"[)(\s]", "", version_constraints).split(",")
            if version_constraints
            else None
        )
        self.markers = markers
        self.requires_extras = extras
        self.is_populated = False

    def __repr__(self):
        return f"PackageDependencyObject({self.name})"

    def populate(self, recursion_depth=0):
        """Populate the object with package information from PyPI."""
        if not self.is_populated:
            super().__init__(self.name, self.get_latest_possible_version())
            self.is_populated = True
        if recursion_depth:
            if self.dependencies:
                for j in self.dependencies:
                    j.populate(recursion_depth - 1)

    def get_latest_possible_version(self, allow_pre=False):
        """Fetches the maximum allowable version that fits within self.version_constraints, or None if no possible version is available."""
        _j = PackageObject(self.name)
        for i in reversed(list(_j.releases.keys())):
            _i = parse_version(i)
            if not self.version_constraints:
                return _i
            if _i.fits_constraints(self.version_constraints) and not (
                not allow_pre and _i.is_prerelease
            ):
                return _i
        return None

    @property
    def canonicalized_name(self) -> str:
        if not self.is_populated:
            raise NotPopulatedError("canonicalized_name")
        return super().canonicalized_name

    @property
    def version(self) -> str:
        if not self.is_populated:
            raise NotPopulatedError("version")
        return super().version

    @property
    def release_name(self) -> str:
        if not self.is_populated:
            raise NotPopulatedError("release_name")
        return super().release_name

    @property
    def upload_time(self) -> Optional[datetime.datetime]:
        if not self.is_populated:
            raise NotPopulatedError("upload_time")
        return super().upload_time

    @property
    def dependencies(self) -> list:
        if not self.is_populated:
            raise NotPopulatedError("dependencies")
        return super().dependencies

    @property
    def dependency_count(self) -> int:
        if not self.is_populated:
            raise NotPopulatedError("dependency_count")
        return super().dependency_count


__all__ = [
    "PackageInfoObject",
    "URLReleaseObject",
    "PackageObject",
    "PackageDependencyObject",
    "PackageVulnerabilitiesObject",
]
