import datetime
import urllib
import urllib.parse
from io import BytesIO
from typing import List, Dict, Any, Tuple

import dateutil
import dateutil.parser
import urllib3

__version__ = '1.0.0'

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
        """
        Create a Hangar v1 SDK instance.

        :param base_url: A base url for the hangar instance, must end with `v1/`
        :param user_agent: A user agent for your application, ideally `yourapp/version`
        """
        self.base_url = base_url
        self.client = urllib3.PoolManager(headers={
            'User-Agent': user_agent,
            'Accept': 'application/json'}
        )

    @property
    def token(self) -> str:
        return str(self.client.headers['Authorization']).removeprefix('HangarAuth ')

    @token.setter
    def token(self, token: str) -> None:
        self.client.headers['Authorization'] = 'HangarAuth ' + token

    @staticmethod
    def _process_parameters(parameters: Dict[str, Any]) -> str:
        return urllib.parse.urlencode({k: v for k, v in parameters.items() if v is not None})

    # Authentication
    def authenticate(self, api_key: str, set_token: bool = True) -> HangarApiSession:
        """
        Log-in with your API key in order to be able to call other endpoints authenticated.

        :param api_key: JWT
        :param set_token: Automatically set the token returned as the token to used to authenticate future requests.
        :return: A <code>HangarApiSession</code> instance
        """
        request = self.client.request('POST',
                                      urllib.parse.urljoin(self.base_url, 'authenticate') + '?apiKey=' + api_key)
        data = orjson.loads(request.data)
        if request.status == 200 or request.status == 201:
            if set_token:
                self.token = data['token']
            return HangarApiSession(data['expiresIn'], data['token'])
        raise HangarAuthenticationException(request.status, data)

    # API Keys
    def get_api_keys(self) -> List[HangarApiKey]:
        """
        Fetches a list of API Keys.
        Requires the `edit_api_keys` permission.

        :return: A list of API keys.
        """
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, 'keys'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return [parse_api_key(key_data) for key_data in data]
        raise HangarApiException(request.status, data)

    def create_api_key(self, name: str, permissions: List[HangarPermissions]) -> str:
        """
        Creates an API key.
        Requires the `edit_api_keys` permission.

        :param name: Name of the API key.
        :param permissions: A list of HangarPermissions for the API key to have.
        :return: An api key, for use with the authenticate endpoint. (Hangar#authenticate(key))
        """
        request = self.client.request('POST', urllib.parse.urljoin(self.base_url, 'keys'),
                                      body=orjson.dumps({'name': name,
                                                         'permissions': [permission.value for permission in
                                                                         permissions]}))
        data = orjson.loads(request.data)
        if request.status == 201:
            return data
        raise HangarApiException(request.status, data)

    def delete_api_key(self, name: str) -> None:
        """
        Deletes an API key.
        Requires the `edit_api_keys` permission.

        :param name: The name of the key to delete
        :return:
        """
        request = self.client.request('DELETE', urllib.parse.urljoin(self.base_url, 'keys' + '?name=' + name))
        data = orjson.loads(request.data)
        if request.status == 204:
            return
        raise HangarApiException(request.status, data)

    # Permissions
    def repository_permissions(self, author: str, slug: str) -> HangarUserPermissions:
        """
        Returns a list of permissions you have in a repository

        :param author: The owner of the project to get the permissions for.
        :param slug: The slug of the project get the permissions for.
        :return: A list of permissions you have in the given repository.
        """
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url,
                                                                  'permissions' + f'?author={author}&slug={slug}'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return parse_user_permissions(data)
        raise HangarApiException(request.status, data)

    def organisation_permissions(self, organisation: str) -> HangarUserPermissions:
        """
        Returns a list of permissions you have in an organisation.

        :param organisation: The organisation to check permissions in
        :return: a list of permissions you have in the given organisation
        """
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url,
                                                                  'permissions' + f'?organisation={organisation}'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return parse_user_permissions(data)
        raise HangarApiException(request.status, data)

    def global_permissions(self) -> HangarUserPermissions:
        """
        Returns a list of permissions you have globally.

        :return: a list of permissions you have globally
        """
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, 'permissions'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return parse_user_permissions(data)
        raise HangarApiException(request.status, data)

    def _run_permission_check(self, check_type: str, permissions: List[HangarPermissions], author: str = None,
                              slug: str = None, organization: str = None) -> Tuple[bool, str]:
        params = {
            "author": author,
            "slug": slug,
            "organization": organization
        }

        string_params = ''
        for permission in permissions:
            string_params += f"permissions={permission.value}&"
        string_params += self._process_parameters(params)

        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, f"has{check_type}?{string_params}"))
        data = orjson.loads(request.data)
        if request.status == 200:
            return data["result"], data['type']
        raise HangarApiException(request.status, data)

    def has_all_permissions_in_project(self, author: str, slug: str,
                                       permissions: List[HangarPermissions]) -> Tuple[bool, str]:
        """
        Checks whether you have all the provided permissions in the given project.

        :param author: The owner of the project to check permissions in
        :param slug: The project slug of the project to check permissions in
        :param permissions: The permissions to check
        :return: result, scope
        """
        return self._run_permission_check('All', permissions, author, slug)

    def has_all_permissions_in_organization(self, organization: str,
                                            permissions: List[HangarPermissions]) -> Tuple[bool, str]:
        """
        Checks whether you have all the provided permissions in the given organization.

        :param organization: The organization to check permissions in
        :param permissions: The permissions to check
        :return: result, scope
        """
        return self._run_permission_check('All', permissions, organization=organization)

    def has_all_permissions_globally(self, permissions: List[HangarPermissions]) -> Tuple[bool, str]:
        """
        Checks whether you have all the provided permissions globally.

        :param permissions: The permissions to check
        :return: result, scope
        """
        return self._run_permission_check('All', permissions)

    def has_any_permissions_in_project(self, author: str, slug: str,
                                       permissions: List[HangarPermissions]) -> Tuple[bool, str]:
        """
        Checks whether you have any of the provided permissions in the given project.

        :param author: The owner of the project to check permissions in
        :param slug: The project slug of the project to check permissions in
        :param permissions: The permissions to check
        :return: result, scope
        """
        return self._run_permission_check('Any', permissions, author, slug)

    def has_any_permissions_in_organization(self, organization: str,
                                            permissions: List[HangarPermissions]) -> Tuple[bool, str]:
        """
        Checks whether you have any of the provided permissions in the given organization.

        :param organization: The organization to check permissions in
        :param permissions: The permissions to check
        :return: result, scope
        """
        return self._run_permission_check('Any', permissions, organization=organization)

    def has_any_permissions_globally(self, permissions: List[HangarPermissions]) -> Tuple[bool, str]:
        """
        Checks whether you have any of the provided permissions globally.

        :param permissions: The permissions to check
        :return: result, scope
        """
        return self._run_permission_check('Any', permissions)

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
        """
        Searches all the projects on Hangar, or for a single user.
        Requires the `view_public_info` permission.

        :param search_query: The query to use when searching
        :param search_limit: The maximum amount of items to return
        :param search_category: A category to filter for
        :param search_license: A license to filter for
        :param search_owner: The author of the project
        :param search_platform: A platform to filter for
        :param search_offset: Where to start searching
        :param search_sort: Used to sort the result
        :param search_version: A Minecraft version to filter for
        :param order_with_relevance: Whether projects should be sorted by the relevance to the given query
        :return: A paginated <code>HangarProject</code> result
        """
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
        """
        Returns info on a specific project.
        Requires the `view_public_info` permission.

        :param author: The author of the project to return
        :param slug: The slug of the project to return
        :return: A <code>HangarProject</code> instance
        """
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, f'projects/{author}/{slug}'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return parse_project(data)
        raise HangarApiException(request.status, data)

    def get_project_members(self, author: str, slug: str,
                            limit: int = DEFAULT_LIMIT,
                            offset: int = DEFAULT_OFFSET) -> HangarPaginatedProjectMemberResult:
        """
        Returns the members of a project.
        Requires the `view_public_info` permission.

        :param author: The author of the project to return members for
        :param slug: The slug of the project to return members for
        :param limit: The maximum amount of items to return
        :param offset: Where to start searching
        :return: A paginated <code>HangarProjectMember</code> result
        """
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
        """
        Returns the stargazers of a project.
        Requires the `view_public_info` permission.

        :param author: The author of the project to return stargazers for
        :param slug: The slug of the project to return stargazers for
        :param limit: The maximum amount of items to return
        :param offset: Where to start searching
        :return: A paginated <code>HangarUser</code> result
        """
        return self._get_project_user_pagination(author, slug, 'stargazers', limit, offset)

    def get_project_stats(self, author: str, slug: str,
                          from_date: datetime.date,
                          to_date: datetime.date) -> Dict[datetime.date, HangarDayProjectStatistics]:
        """
        Returns the stats (downloads and views) for a project per day for a certain date range.
        Requires the `is_subject_member` permission.

        :param author: The author of the project to return statistics for
        :param slug: The slug of the project to return stats for
        :param from_date: The first date to include in the result
        :param to_date: The last date to include in the result
        :return: A dictionary, with <code>datetime.date</code> keys and <code>HangarDayProjectStatistics</code> values.
        """
        params = self._process_parameters({'from': from_date, 'to': to_date})

        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url, f'projects/{author}/{slug}/stats?{params}'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return {dateutil.parser.parse(iso_date_key): parse_day_project_statistics(statistic_data)
                    for iso_date_key, statistic_data in data.items()}
        raise HangarApiException(request.status, data)

    def get_project_watchers(self, author: str, slug: str, limit: int = DEFAULT_LIMIT,
                             offset: int = DEFAULT_OFFSET) -> HangarPaginatedUserResult:
        """
        Returns the watchers of a project.
        Requires the `view_public_info` permission.

        :param author: The author of the project to return watchers for
        :param slug: The slug of the project to return watchers for
        :param limit: The maximum amount of items to return
        :param offset: Where to start searching
        :return: A paginated <code>HangarUser</code> result.
        """
        return self._get_project_user_pagination(author, slug, 'watchers', limit, offset)

    # Projects - Versions
    def get_project_versions(self, author: str, slug: str, channel: str = None, limit: int = DEFAULT_LIMIT,
                             offset: int = DEFAULT_OFFSET, platform: str = None,
                             version_tag: str = None) -> HangarPaginatedVersionResult:
        """
        Returns all versions of a project.
        Requires the `view_public_info` permission in the project or owning organization.

        :param author: The author of the project to return versions for
        :param slug: The slug of the project to return versions for
        :param channel: A name of a version channel to filter for
        :param limit: The maximum amount of items to return
        :param offset: Where to start searching
        :param platform: A platform name to filter for
        :param version_tag: A version tag to filter for
        :return: A paginated <code>HangarVersion</code> result
        """
        params = {'channel': channel, 'limit': limit, 'offset': offset, 'platform': platform, 'vTag': version_tag}

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
        """
        Returns versions of a project with the specified version string.
        Requires the `view_public_info` permission in the project or owning organization.

        :param author: The author of the project to return versions for
        :param slug: The slug of the project to return versions for
        :param name: The name of the versions to return
        :return: A list of <code>HangarVersion</code>s
        """
        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url, f'projects/{author}/{slug}/versions/{name}'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return [parse_version(version_data) for version_data in data['result']]
        raise HangarApiException(request.status, data)

    def get_project_version_for_platform(self, author: str, slug: str, name: str, platform: str) -> HangarVersion:
        """
        Returns a specific version of a project.
        Requires the `view_public_info` permission in the project or owning organization.

        :param author: The author of the project to return the version for
        :param slug: The slug of the version to return
        :param name: The name of the version to return
        :param platform: The platform of the version to return
        :return: A <code>HangarVersion</code> instance
        """
        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url,
                                                           f'projects/{author}/{slug}/versions/{name}/{platform}'))
        data = orjson.loads(request.data)
        if request.status == 200:
            return parse_version(data['result'])
        raise HangarApiException(request.status, data)

    def download_version(self, author: str, slug: str, name: str,
                         platform: str) -> BytesIO:
        # TODO: accept external urls correctly, return custom class instead of binary?
        request = self.client.request('GET',
                                      urllib.parse.urljoin(self.base_url,
                                                           f'projects/{author}/{slug}'
                                                           f'/versions/{name}/{platform}/download'),
                                      preload_content=False,
                                      headers={'Accept': 'application/octet-stream'})

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
        """
        Returns all users that have at least one public project.
        Requires the `view_public_info` permission.

        :param limit: The maximum amount of items to return
        :param offset: Where to start watching
        :param sort: Used to sort the result
        :return: A paginated <code>HangarUser</code> result
        """
        params = {
            'offset': offset,
            'limit': limit,
            'sort': sort.value if sort else None
        }

        return self._get_paginated_user_result('authors', params)

    def get_staff(self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET,
                  sort: HangarStaffSort = None) -> HangarPaginatedUserResult:
        """
        Returns Hangar staff.
        Requires the `view_public_info` permission.

        :param limit: The maximum amount of items to return
        :param offset: Where to start searching
        :param sort: Used to sort the result
        :return: A paginated <code>HangarUser</code> result
        """
        params = {
            'offset': offset,
            'limit': limit,
            'sort': sort.value if sort else None
        }

        return self._get_paginated_user_result('staff', params)

    def get_users(self, query: str, limit: int = DEFAULT_LIMIT,
                  offset: int = DEFAULT_OFFSET) -> HangarPaginatedUserResult:
        """
        Returns a list of users based on a search query

        :param query: The search query
        :param limit: The maximum amount of items to return
        :param offset: Where to start searching
        :return: A paginated <code>HangarUser</code> result
        """
        params = {
            'offset': offset,
            'limit': limit,
            'query': query
        }

        return self._get_paginated_user_result('users', params)

    def get_user(self, user: str) -> HangarUser:
        """
        Returns a specific user.
        Requries the `view_public_info` permission.

        :param user: The name of the user to return
        :return: A <code>HangarUser</code> instance
        """
        request = self.client.request('GET', urllib.parse.urljoin(self.base_url, f'users/{user}'))
        data = orjson.loads(request.data)

        if request.status == 200:
            return parse_user(data)
        raise HangarApiException(request.status, data)

    def get_user_pinned_projects(self, user: str) -> List[HangarCompactProject]:
        """
        Returns the pinned projects for a specific user.
        Requires the `view_public_info` permission

        :param user: The user to return pinned projects for
        :return: A list of <code>HangarCompactProject</code>s
        """
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
        """
        Returns the starred projects for a specific user.
        Requires the `view_public_info` permission.

        :param user: The user to return starred projects for
        :param limit: The maximum amount of items to return
        :param offset: Where to start searching
        :param sort: How to sort the projects
        :return: A paginated <code>HangarCompactProject</code> result
        """
        return self._get_user_compact_project('starred', user, limit, offset, sort)

    def get_user_watching_projects(self, user: str, limit: int = DEFAULT_LIMIT,
                                   offset: int = DEFAULT_OFFSET,
                                   sort: HangarCompactProjectSort = None) -> HangarPaginatedCompactProjectResult:
        """
        Returns the watched projects for a specific user.
        Requires the `view_public_info` permission.
        :param user: The user to return watched projects for
        :param limit: The maximum amount of items to return
        :param offset: Where to start searching
        :param sort: How to sort the projects
        :return: A paginated <code>HangarCompactProject</code> result
        """
        return self._get_user_compact_project('watching', user, limit, offset, sort)
