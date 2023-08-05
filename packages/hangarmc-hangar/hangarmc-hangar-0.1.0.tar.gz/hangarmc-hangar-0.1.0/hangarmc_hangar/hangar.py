import datetime
import urllib
import urllib.parse
from io import BytesIO
from typing import List, Dict, Any

import dateutil
import dateutil.parser
import urllib3

__version__ = '0.1.0'

from orjson import orjson

from hangarmc_hangar.exception.hangar_exceptions import HangarAuthenticationException, HangarApiException, \
    HangarDownloadException
from hangarmc_hangar.model.hangar_models import HangarApiSession, HangarApiKey, HangarPermissions, \
    HangarUserPermissions, HangarSearchSort, HangarPaginatedProjectResult, HangarProject, \
    HangarPaginatedProjectMemberResult, HangarPaginatedUserResult, HangarDayProjectStatistics, HangarAuthorSort, \
    HangarStaffSort, HangarUser, HangarCompactProject, HangarPaginatedCompactProjectResult, HangarCompactProjectSort, \
    HangarPaginatedVersionResult, HangarVersion
from hangarmc_hangar.parser.hangar_parsers import parse_api_key, parse_user_permissions, parse_pagination, \
    parse_project, parse_project_member, parse_user, parse_day_project_statistics, parse_compact_project, parse_version

USER_AGENT = f"hangarmc-hangar/{__version__}"

# Common Instances
MINIDIGGER_INSTANCE = "https://hangar.benndorf.dev/api/v1/"
PAPER_INSTANCE = None  # to be continued...
SPONGE_INSTANCE = None  # to be continued...

DEFAULT_LIMIT = 50
DEFAULT_OFFSET = 0


class Hangar:
    def __init__(self, base_url: str = MINIDIGGER_INSTANCE,
                 user_agent: str = USER_AGENT):  # TODO: add paper and sponge instances
        self.base_url = base_url
        self.client = urllib3.PoolManager(headers={
            'User-Agent': user_agent,
            'Accept': 'application/json'}
        )

    @property
    def jwt(self) -> str:
        return str(self.client.headers['Authorization']).removeprefix('HangarAuth ')

    @jwt.setter
    def jwt(self, jwt: str) -> None:
        self.client.headers['Authorization'] = 'HangarAuth ' + jwt

    @staticmethod
    def _process_parameters(parameters: Dict[str, Any]) -> str:
        return urllib.parse.urlencode({k: v for k, v in parameters.items() if v is not None})

    # Authentication
    def authenticate(self, api_key: str, set_jwt: bool = True) -> HangarApiSession:
        request = self.client.request('POST',
                                      urllib.parse.urljoin(self.base_url, 'authenticate') + '?apiKey=' + api_key)
        data = orjson.loads(request.data)
        if request.status == 200 or request.status == 201:
            if set_jwt:
                self.jwt = data['token']
            return HangarApiSession(data['expiresIn'], data['token'])
        raise HangarAuthenticationException(request.status, data)

    # API Keys
    def get_api_keys(self) -> List[HangarApiKey]:
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, 'keys'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return [parse_api_key(key_data) for key_data in data]
        raise HangarApiException(request.status, data)

    def create_api_key(self, name: str, permissions: List[HangarPermissions]) -> str:
        request = self.client.request('POST', urllib.parse.urljoin(self.base_url, 'keys'),
                                      body={'name': name,
                                            'permissions': [permission.value for permission in permissions]})
        data = orjson.loads(request.data)
        if request.status == 201:
            return data
        raise HangarApiException(request.status, data)

    def delete_api_key(self, name: str) -> None:
        request = self.client.request('DELETE', urllib.parse.urljoin(self.base_url, 'keys' + '?name=' + name))
        data = orjson.loads(request.data)
        if request.status == 204:
            return
        raise HangarApiException(request.status, data)

    # Permissions
    def repository_permissions(self, author: str, slug: str) -> HangarUserPermissions:
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url,
                                                                  'permissions' + f'?author={author}&slug={slug}'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return parse_user_permissions(data)
        raise HangarApiException(request.status, data)

    def organisation_permissions(self, organisation: str) -> HangarUserPermissions:
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url,
                                                                  'permissions' + f'?organisation={organisation}'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return parse_user_permissions(data)
        raise HangarApiException(request.status, data)

    # TODO: hasAny & hasAll, see https://discord.com/channels/855123416889163777/859516358281396234/997605343012077629

    # Projects - Projects
    def search_projects(self, search_query: str = None,
                        search_limit: int = DEFAULT_LIMIT,
                        search_category: str = None,
                        search_license: str = None,
                        search_owner: str = None,
                        search_platform: str = None,
                        search_offset: int = DEFAULT_OFFSET,
                        search_sort: HangarSearchSort = None,
                        search_version: str = None,
                        order_with_relevance: bool = True) -> HangarPaginatedProjectResult:
        params = {
            "q": search_query,
            "category": search_category,
            "license": search_license,
            "limit": search_limit,
            "offset": search_offset,
            "orderWithRelevance": order_with_relevance,
            "owner": search_owner,
            "platform": search_platform,
            "sort": search_sort.value if search_sort else None,
            "version": search_version
        }

        params = self._process_parameters(params)

        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, f'projects?{params}'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return HangarPaginatedProjectResult(
                parse_pagination(data['pagination']),
                [parse_project(project_data) for project_data in data['result']]
            )
        raise HangarApiException(request.status, data)

    def get_project(self, author: str, slug: str) -> HangarProject:
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, f'projects/{author}/{slug}'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return parse_project(data)
        raise HangarApiException(request.status, data)

    def get_project_members(self, author: str, slug: str,
                            limit: int = DEFAULT_LIMIT,
                            offset: int = DEFAULT_OFFSET) -> HangarPaginatedProjectMemberResult:
        params = self._process_parameters({'offset': offset, 'limit': limit})
        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url, f'projects/{author}/{slug}/members?{params}'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return HangarPaginatedProjectMemberResult(
                parse_pagination(data['pagination']),
                [parse_project_member(project_member_data) for project_member_data in data['result']]
            )
        raise HangarApiException(request.status, data)

    def _get_project_user_pagination(self, author: str, slug: str, pagination: str, limit: int = DEFAULT_LIMIT,
                                     offset: int = DEFAULT_OFFSET) -> HangarPaginatedUserResult:
        params = self._process_parameters({'offset': offset, 'limit': limit})

        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url,
                                                           f'projects/{author}/{slug}/{pagination}?{params}'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return HangarPaginatedUserResult(
                parse_pagination(data['pagination']),
                [parse_user(user_data) for user_data in data['result']]
            )
        raise HangarApiException(request.status, data)

    def get_project_stargazers(self, author: str, slug: str, limit: int = DEFAULT_LIMIT,
                               offset: int = DEFAULT_OFFSET) -> HangarPaginatedUserResult:
        return self._get_project_user_pagination(author, slug, 'stargazers', limit, offset)

    def get_project_stats(self, author: str, slug: str,
                          from_date: datetime.date,
                          to_date: datetime.date) -> Dict[datetime.date, HangarDayProjectStatistics]:
        params = self._process_parameters({'from': from_date.isoformat(), 'to': to_date.isoformat()})

        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url, f'projects/{author}/{slug}/stats?{params}'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return {dateutil.parser.parse(iso_date_key): parse_day_project_statistics(statistic_data)
                    for iso_date_key, statistic_data in data.items()}
        raise HangarApiException(request.status, data)

    def get_project_watchers(self, author: str, slug: str, limit: int = DEFAULT_LIMIT,
                             offset: int = DEFAULT_OFFSET) -> HangarPaginatedUserResult:
        return self._get_project_user_pagination(author, slug, 'watchers', limit, offset)

    # Projects - Versions
    def get_project_versions(self, author: str, slug: str, channel: str = None, limit: int = DEFAULT_LIMIT,
                             offset: int = DEFAULT_OFFSET, platform: str = None,
                             version_tag: str = None) -> HangarPaginatedVersionResult:
        params = {'channel': channel, 'limit': limit, 'offset': offset, 'platform': platform, 'versionTag': version_tag}

        params = self._process_parameters(params)

        request = self.client.request('GET', urllib.parse.urljoin(self.base_url,
                                                                  f'projects/{author}/{slug}/versions?{params}'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return HangarPaginatedVersionResult(
                parse_pagination(data['pagination']),
                [parse_version(version_data) for version_data in data['result']]
            )
        raise HangarApiException(request.status, data)

    def get_project_version(self, author: str, slug: str, name: str) -> List[HangarVersion]:
        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url, f'projects/{author}/{slug}/versions/{name}'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return [parse_version(version_data) for version_data in data['result']]
        raise HangarApiException(request.status, data)

    def get_project_version_for_platform(self, author: str, slug: str, name: str, platform: str) -> HangarVersion:
        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url,
                                                           f'projects/{author}/{slug}/versions/{name}/{platform}'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return parse_version(data['result'])
        raise HangarApiException(request.status, data)

    def download_version(self, author: str, slug: str, name: str, platform: str) -> BytesIO:
        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url,
                                                           f'projects/{author}/{slug}'
                                                           f'/versions/{name}/{platform}/download'),
                                      preload_content=False)

        download_bytesio = BytesIO()
        while True:
            data = request.read(2 ** 16)  # 64kb
            if not data:
                break
            download_bytesio.write(data)
        request.release_conn()

        if request.status == 200:
            return download_bytesio
        raise HangarDownloadException(request.status)

    # Users
    def _get_paginated_user_result(self, pagination: str, parameters: Dict[str, Any]) -> HangarPaginatedUserResult:
        params = self._process_parameters(parameters)

        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url, f'{pagination}?{params}'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return HangarPaginatedUserResult(
                parse_pagination(data['pagination']),
                [parse_user(user_data) for user_data in data['result']]
            )
        raise HangarApiException(request.status, data)

    def get_authors(self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET,
                    sort: HangarAuthorSort = None) -> HangarPaginatedUserResult:
        params = {
            'offset': offset,
            'limit': limit,
            'sort': sort.value if sort else None
        }

        return self._get_paginated_user_result('authors', params)

    def get_staff(self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET,
                  sort: HangarStaffSort = None) -> HangarPaginatedUserResult:
        params = {
            'offset': offset,
            'limit': limit,
            'sort': sort.value if sort else None
        }

        return self._get_paginated_user_result('staff', params)

    def get_users(self, query: str, limit: int = DEFAULT_LIMIT,
                  offset: int = DEFAULT_OFFSET) -> HangarPaginatedUserResult:
        params = {
            'offset': offset,
            'limit': limit,
            'query': query
        }

        return self._get_paginated_user_result('users', params)

    def get_user(self, user: str) -> HangarUser:
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, f'users/{user}'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return parse_user(data)
        raise HangarApiException(request.status, data)

    def get_user_pinned_projects(self, user: str) -> List[HangarCompactProject]:
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, f'users/{user}/pinned'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return [parse_compact_project(project_data) for project_data in data['result']]
        raise HangarApiException(request.status, data)

    def _get_user_compact_project(self, pagination: str, user: str, limit: int = DEFAULT_LIMIT,
                                  offset: int = DEFAULT_OFFSET,
                                  sort: HangarCompactProjectSort = None) -> HangarPaginatedCompactProjectResult:
        params = {
            'offset': offset,
            'limit': limit,
            'sort': sort.value if sort else None
        }

        params = self._process_parameters(params)

        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, f'users/{user}/{pagination}?{params}'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return HangarPaginatedCompactProjectResult(
                parse_pagination(data['pagination']),
                [parse_compact_project(project_data) for project_data in data['result']]
            )
        raise HangarApiException(request.status, data)

    def get_user_starred_projects(self, user: str, limit: int = DEFAULT_LIMIT,
                                  offset: int = DEFAULT_OFFSET,
                                  sort: HangarCompactProjectSort = None) -> HangarPaginatedCompactProjectResult:
        return self._get_user_compact_project('starred', user, limit, offset, sort)

    def get_user_watching_projects(self, user: str, limit: int = DEFAULT_LIMIT,
                                   offset: int = DEFAULT_OFFSET,
                                   sort: HangarCompactProjectSort = None) -> HangarPaginatedCompactProjectResult:
        return self._get_user_compact_project('watching', user, limit, offset, sort)
