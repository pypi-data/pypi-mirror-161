from typing import Dict, List

import dateutil
import dateutil.parser

from hangarmc_hangar.model.hangar_models import HangarApiKey, HangarPermissions, HangarUserPermissions, \
    HangarPermissionType, HangarPagination, HangarNamespace, HangarProjectDonationSettings, HangarProjectLicense, \
    HangarProjectSettings, HangarProjectStatistics, HangarUserActions, HangarProject, HangarProjectMember, \
    HangarRole, HangarUser, HangarDayProjectStatistics, HangarVisibility, HangarColor, HangarCompactProject, \
    HangarVersion, HangarProjectChannel, HangarProjectChannelFlag, HangarPinnedStatus, HangarPluginDependency, \
    HangarReviewState, HangarVersionStatistics, HangarFileInfo


def parse_hangar_color(color_string: str) -> HangarColor:
    if color_string == 'transparent':
        return HangarColor.TRANSPARENT
    return HangarColor(int(color_string.removeprefix('#'), 16))


def parse_api_key(data: Dict) -> HangarApiKey:
    return HangarApiKey(
        dateutil.parser.parse(data['createdAt']),
        data['name'],
        [HangarPermissions(permission_string) for permission_string in data['permissions']],
        data['tokenIdentifier']
    )


def parse_user_permissions(data: Dict) -> HangarUserPermissions:
    return HangarUserPermissions(
        data['permissionBinString'],
        [HangarPermissions(permission_string) for permission_string in data['permissions']],
        HangarPermissionType(data['type'])
    )


def parse_pagination(data: Dict) -> HangarPagination:
    return HangarPagination(
        data['count'],
        data['limit'],
        data['offset']
    )


def _parse_namespace(data: Dict) -> HangarNamespace:
    return HangarNamespace(
        data['owner'],
        data['slug']
    )


def _parse_project_donation_settings(data: Dict) -> HangarProjectDonationSettings:
    return HangarProjectDonationSettings(
        data['enable'],
        data['subject']
    )


def _parse_project_license(data: Dict) -> HangarProjectLicense:
    return HangarProjectLicense(
        data['name'],
        data['type'],
        data['url']
    )


def _parse_project_settings(data: Dict) -> HangarProjectSettings:
    return HangarProjectSettings(
        _parse_project_donation_settings(data['donation']),
        data['forumSync'],
        data['homepage'],
        data['issues'],
        data['keywords'],
        _parse_project_license(data['license']),
        data['source'],
        data['sponsors'],
        data['support'],
        data['wiki']
    )


def _parse_project_statistics(data: Dict) -> HangarProjectStatistics:
    return HangarProjectStatistics(
        data['downloads'],
        data['recentDownloads'],
        data['recentViews'],
        data['stars'],
        data['views'],
        data['watchers']
    )


def _parse_user_actions(data: Dict) -> HangarUserActions:
    return HangarUserActions(
        data['flagged'],
        data['starred'],
        data['watching']
    )


def parse_compact_project(data: Dict) -> HangarCompactProject:
    return HangarCompactProject(
        data['name'],
        _parse_namespace(data['namespace']),
        HangarVisibility(data['visibility']),
        dateutil.parser.parse(data['createdAt']),
        dateutil.parser.parse(data['lastUpdated']),
        data['category'],
        _parse_project_statistics(data['statistics'])
    )


def parse_project(data: Dict) -> HangarProject:
    return HangarProject(
        data['name'],
        _parse_namespace(data['namespace']),
        HangarVisibility(data['visibility']),
        dateutil.parser.parse(data['createdAt']),
        dateutil.parser.parse(data['lastUpdated']),
        data['category'],
        _parse_project_statistics(data['stats']),
        data['description'],
        data['postId'],
        _parse_project_settings(data['settings']),
        data['topicId'],
        _parse_user_actions(data['userActions']),
    )


def parse_project_member(data: Dict) -> HangarProjectMember:
    return HangarProjectMember(
        data['user'],
        _parse_roles(data['roles'])
    )


def _parse_role(data: Dict) -> HangarRole:
    return HangarRole(
        data['title'],
        data['value'],
        data['roleId'],
        data['assignable'],
        parse_hangar_color(data['color']),
        int(data['permissions']),
        data['rank'],
        data['roleCategory']
    )


def _parse_roles(data: List[Dict]) -> List[HangarRole]:
    return [_parse_role(role) for role in data]


def parse_user(data: Dict) -> HangarUser:
    return HangarUser(
        data['name'],
        dateutil.parser.parse(data['createdAt']),
        dateutil.parser.parse(data['joinDate']),
        data['isOrganization'],
        data['locked'],
        _parse_roles(data['roles']),
        data['tagline'],
        data['projectCount']
    )


def parse_day_project_statistics(data: Dict) -> HangarDayProjectStatistics:
    return HangarDayProjectStatistics(
        data['downloads'],
        data['views']
    )


def parse_channel(data: Dict) -> HangarProjectChannel:
    return HangarProjectChannel(
        data['name'],
        parse_hangar_color(data['color']),
        dateutil.parser.parse(data['createdAt']),
        [HangarProjectChannelFlag(data_flag) for data_flag in data['flags']]
    )


def parse_dependency(data: Dict) -> HangarPluginDependency:
    return HangarPluginDependency(
        data['name'],
        _parse_namespace(data['namespace']),
        data['required'],
        data['externalUrl']
    )


def parse_version_statistics(data: Dict) -> HangarVersionStatistics:
    return HangarVersionStatistics(
        data['downloads']
    )


def parse_file_info(data: Dict) -> HangarFileInfo | None:
    if data is None:
        return None
    return HangarFileInfo(
        data['name'],
        data['sizeBytes'],
        data['md5Hash'],
    )


def parse_version(data: Dict) -> HangarVersion:
    return HangarVersion(
        data['author'],
        parse_channel(data['channel']),
        dateutil.parser.parse(data['createdAt']),
        data['description'],
        data['externalUrl'],
        parse_file_info(data['fileInfo']),
        data['name'],
        HangarPinnedStatus(data['pinnedStatus']),
        data['platformDependencies'],
        data['platformDependenciesFormatted'],
        {dependency_key: parse_dependency(dependency) for dependency_key, dependency in
         data['pluginDependencies'].items()},
        data['postId'],
        HangarReviewState(data['reviewState']),
        parse_version_statistics(data['stats']),
        HangarVisibility(data['visibility'])
    )
