from datetime import datetime
from types import SimpleNamespace
from typing import Any, Optional, Dict, List, NamedTuple, Tuple, Union, Callable
from http.client import HTTPResponse
from .packaging.version import Version, LegacyVersion

class _PackageBase:
    def __init__(self, package_name: str, release: Optional[str] = ...) -> None: ...
    def _attempt_request(self) -> HTTPResponse: ...
class PackageInfoObject(_PackageBase):
    def __init__(
        self,
        package_name: str,
        package_extras: Optional[list] = ...,
        release: Optional[str] = ...,
        perform_request: bool = ...,
        http_response: Dict[str, Any] = ...,
        disregard_extras= ...,
        disregard_markers= ...,
    ) -> None:
        self.author: str
        self.author_email: str
        self.bugtrack_url: Optional[str]
        self.classifiers: List[str]
        self.description: Optional[str]
        self.description_content_type: Optional[str]
        self.docs_url: Optional[str]
        self.download_url: Optional[str]
        self.downloads: Dict[str, int]
        self.home_page: Optional[str]
        self.http_response: Dict[str, Any]
        self.keywords: Optional[str]
        self.license: Optional[str]
        self.maintainer: Optional[str]
        self.maintainer_email: Optional[str]
        self.name: str
        self.package_url: str
        self.platform: Optional[str]
        self.possible_extras: Tuple[str]
        self.project_url: str
        self.project_urls: Optional[Dict[str,str]]
        self.release_url: str
        self.requires_dist: Optional[List[PackageDependencyObject]]
        self.requires_python: Optional[str]
        self.summary: Optional[str]
        self.version: Union[Version, LegacyVersion]
        self.yanked: bool
        self.yanked_reason: Optional[str]
    @staticmethod
    def _parse_dependencies(
        reqs: list, extras: Optional[list], disregard_extras: bool, disregard_markers: bool
    ) -> Tuple[Optional[dict], Optional[tuple]]: ...
class URLReleaseObject(NamedTuple):
    comment_text: str
    digests: SimpleNamespace
    downloads: int
    filename: str
    has_sig: bool
    md5_digest: str
    packagetype: str
    python_version: str
    size: int
    upload_time: datetime
    url: str
    yanked: bool
    yanked_reason: Optional[str]
    @classmethod
    def construct(cls: Callable, url_release_item: Dict[str, Any]) -> URLReleaseObject: ...
class PackageVulnerabilitiesObject(NamedTuple):
    aliases: List[str]
    details: str
    fixed_in: List[str]
    id: str
    link: str
    source: str
    @classmethod
    def construct(cls: Callable, vuln_dict: Dict[str, Any]) -> PackageVulnerabilitiesObject: ...
class PackageObject(_PackageBase):
    def __init__(
        self, package_name: str, release: Optional[str] = ..., **kwargs
    ) -> None:
        self.info: PackageInfoObject
        self.last_serial: int
        self.releases: Optional[Dict[str, List[URLReleaseObject]]]
        self.urls: List[URLReleaseObject]
        self.vulnerabilities: Optional[List[PackageVulnerabilitiesObject]]
        self.canonicalized_name: str
        self.version: str
        self.release_name: str
        self.upload_time: Optional[datetime]
        self.dependencies: list
        self.dependency_count: int
        def populate_dependencies(self, depth: int = ...) -> None: ...
class PackageDependencyObject(PackageObject):
    def __init__(
        self,
        package_name: str,
        version_constraints: Optional[str] = ...,
        markers: Optional[dict] = ...,
        extras: Optional[list] = ...,
    ) -> None: 
        self.canonicalized_name: str
        self.version: str
        self.release_name: str
        self.upload_time: Optional[datetime]
        self.dependencies: list
        self.dependency_count: int
    def populate(self, recursion_depth: int = ...) -> None: ...
    def get_latest_possible_version(self, allow_pre: bool = ...) -> Optional[Version]: ...
    