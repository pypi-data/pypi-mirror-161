import dataclasses
import enum
import datetime
from typing import List, Tuple, Dict


class HangarPermissions(enum.Enum):
    CREATE_ORGANISATION = "create_organization"
    CREATE_PROJECT = "create_project"
    CREATE_VERSION = "create_version"
    DELETE_PROJECT = "delete_project"
    DELETE_VERSION = "delete_version"
    EDIT_ALL_USER_SETTINGS = "edit_all_user_settings"
    EDIT_API_KEYS = "edit_api_keys"
    EDIT_OWN_USER_SETTINGS = "edit_own_user_settings"
    EDIT_PAGE = "edit_page"
    EDIT_SUBJECT_SETTINGS = "edit_subject_settings"
    EDIT_TAGS = "edit_tags"
    EDIT_VERSION = "edit_version"
    HARD_DELETE_PROJECT = "hard_delete_project"
    HARD_DELETE_VERSION = "hard_delete_version"
    IS_STAFF = "is_staff"
    IS_SUBJECT_MEMBER = "is_subject_member"
    IS_SUBJECT_OWNER = "is_subject_owner"
    MANAGE_SUBJECT_MEMBERS = "manage_subject_members"
    MANUAL_VALUE_CHANGES = "manual_value_changes"
    MOD_NOTES_AND_FLAGS = "mod_notes_and_flags"
    POST_AS_ORGANIZATION = "post_as_organization"
    REVIEWER = "reviewer"
    SEE_HIDDEN = "see_hidden"
    VIEW_HEALTH = "view_health"
    VIEW_IP = "view_ip"
    VIEW_LOGS = "view_logs"
    VIEW_PUBLIC_INFO = "view_public_info"
    VIEW_STATS = "view_stats"


class HangarPermissionType(enum.Enum):
    GLOBAL = 'global'
    ORGANISATION = 'organisation'
    PROJECT = 'project'


class HangarSearchSort(enum.Enum):
    DOWNLOADS = 'downloads'
    NEWEST = 'newest'
    RECENT_DOWNLOADS = 'recent_downloads'
    RECENT_VIEWS = 'recent_views'
    STARS = 'stars'
    UPDATED = 'updated'
    VIEWS = 'views'


class HangarCompactProjectSort(enum.Enum):
    DOWNLOADS = 'downloads'
    NEWEST = 'newest'
    RECENT_DOWNLOADS = 'recent_downloads'
    RECENT_VIEWS = 'recent_views'
    STARS = 'stars'
    UPDATED = 'updated'
    VIEWS = 'views'
    ONLY_RELEVANCE = 'only_relevance'


class HangarVisibility(enum.Enum):
    NEEDS_APPROVAL = 'needsApproval'
    NEEDS_CHANGES = 'needsChanges'
    NEW = 'new'
    PUBLIC = 'public'
    SOFT_DELETE = 'softDelete'


class HangarStaffSort(enum.Enum):
    JOIN_DATE = 'joinDate'
    PROJECT_COUNT = 'projectCount'


class HangarAuthorSort(enum.Enum):
    JOIN_DATE = 'joinDate'
    PROJECT_COUNT = 'projectCount'
    USERNAME = 'username'


class HangarReviewState(enum.Enum):
    PARTIALLY_REVIEWED = 'partially_reviewed'
    REVIEWED = 'reviewed'
    UNDER_REVIEW = 'under_review'
    UNREVIEWED = 'unreviewed'


@dataclasses.dataclass
class HangarApiKey:
    created_at: datetime.datetime
    name: str
    permissions: List[HangarPermissions]
    token_identifier: str


@dataclasses.dataclass
class HangarApiSession:
    _expires_in: int
    token: str
    expires: datetime.datetime = None

    def __post_init__(self):
        self.expires = datetime.datetime.now() + datetime.timedelta(seconds=self._expires_in)


@dataclasses.dataclass
class HangarUserPermissions:
    permission_binary_string: str
    permissions: List[HangarPermissions]
    type: HangarPermissionType


@dataclasses.dataclass
class HangarNamespace:
    owner: str
    slug: str

    def __str__(self):
        return f"{self.owner}/{self.slug}"


@dataclasses.dataclass
class HangarProjectDonationSettings:
    enabled: bool
    subject: str


@dataclasses.dataclass
class HangarProjectLicense:
    name: str
    type: str
    url: str


@dataclasses.dataclass
class HangarProjectSettings:
    donation: HangarProjectDonationSettings
    forum_sync: bool
    homepage: str
    issues: str
    keywords: List[str]
    license: HangarProjectLicense
    source: str
    sponsors: str
    support: str
    wiki: str


@dataclasses.dataclass
class HangarProjectStatistics:
    downloads: int
    recent_downloads: int
    recent_views: int
    stars: int
    views: int
    watchers: int


@dataclasses.dataclass
class HangarUserActions:
    flagged: bool
    starred: bool
    watching: bool


@dataclasses.dataclass
class HangarCompactProject:
    name: str
    namespace: HangarNamespace
    visibility: HangarVisibility
    created: datetime.datetime
    updated: datetime.datetime
    category: str
    statistics: HangarProjectStatistics


@dataclasses.dataclass
class HangarProject(HangarCompactProject):
    description: str
    post_id: int
    settings: HangarProjectSettings
    topic_id: int
    user_actions: HangarUserActions


@dataclasses.dataclass
class HangarPagination:
    count: int
    limit: int
    offset: int


@dataclasses.dataclass
class HangarPaginatedResult:
    pagination: HangarPagination
    result: object


@dataclasses.dataclass
class HangarPaginatedProjectResult(HangarPaginatedResult):
    result: List[HangarProject]


@dataclasses.dataclass
class HangarPaginatedCompactProjectResult(HangarPaginatedResult):
    result: List[HangarCompactProject]


class HangarColor(enum.Enum):
    class ColorConversionException(Exception):
        pass

    BLUE = 0x0000FF
    DARK_LIME_GREEN = 0x009600
    PURE_BLUE = 0x0096FF
    PURE_GREEN = 0x00DC00
    PURE_CYAN = 0x00E1E1
    PURE_GREEN_2 = 0x7FFF00
    GRAY = 0xA9A9A9
    PURE_VIOLET = 0xB400FF
    PALE_CYAN = 0xB9F2FF
    LIGHT_GRAY = 0xC0C0C0
    VERY_LIGHT_VIOLET = 0xC87DFF
    MODERATE_YELLOW = 0xCFB53B
    PURE_RED = 0xDC0000
    PURE_MAGENTA = 0xE100E1
    VERY_PALE_CYAN = 0xE7FEFF
    PURE_ORANGE = 0xFF8200
    PURE_YELLOW = 0xFFC800
    TRANSPARENT = None

    @property
    def hex_string(self) -> str:
        if self.value == HangarColor.TRANSPARENT:
            raise HangarColor.ColorConversionException("Cannot convert TRANSPARENT to hex string")
        return "#{:06x}".format(self.value).upper()

    @property
    def rgb(self) -> Tuple[int, int, int]:
        if self.value == HangarColor.TRANSPARENT:
            raise HangarColor.ColorConversionException("Cannot convert TRANSPARENT to RGB")
        return self.value >> 16, (self.value >> 8) & 0xFF, self.value & 0xFF

    @property
    def display_name(self) -> str:
        return self.name.replace('_', ' ').capitalize()


@dataclasses.dataclass
class HangarRole:
    title: str
    value: str
    role_id: int
    assignable: bool
    color: HangarColor
    permissions: int
    rank: int
    role_category: str


@dataclasses.dataclass
class HangarProjectMember:
    user: str
    permissions: List[HangarRole]


@dataclasses.dataclass
class HangarPaginatedProjectMemberResult(HangarPaginatedResult):
    result: List[HangarProjectMember]


@dataclasses.dataclass
class HangarUser:
    name: str
    created_at: datetime.datetime
    join_date: datetime.datetime
    is_organisation: datetime.datetime
    locked: bool
    roles: List[HangarRole]
    tagline: str
    project_count: int


@dataclasses.dataclass
class HangarPaginatedUserResult(HangarPaginatedResult):
    result: List[HangarUser]


@dataclasses.dataclass
class HangarDayProjectStatistics:
    downloads: int
    views: int


class HangarProjectChannelFlag(enum.Enum):
    FROZEN = 'FROZEN'
    PINNED = 'PINNED'
    SKIP_REVIEW_QUEUE = 'SKIP_REVIEW_QUEUE'
    UNSTABLE = 'UNSTABLE'


class HangarPinnedStatus(enum.Enum):
    CHANNEL = 'CHANNEL'
    VERSION = 'VERSION'
    NONE = 'NONE'


@dataclasses.dataclass
class HangarProjectChannel:
    name: str
    color: HangarColor
    created: datetime.datetime
    flags: List[HangarProjectChannelFlag]


@dataclasses.dataclass
class HangarPluginDependency:
    name: str
    namespace: HangarNamespace
    required: bool
    external_url: str


@dataclasses.dataclass
class HangarVersionStatistics:
    downloads: int


@dataclasses.dataclass
class HangarFileInfo:
    name: str
    size_bytes: int
    md_5: str


@dataclasses.dataclass
class HangarVersion:
    author: str
    channel: HangarProjectChannel
    created: datetime.datetime
    description: str
    external_url: str
    file_info: HangarFileInfo
    name: str
    pinned_status: HangarPinnedStatus
    platform_dependencies: Dict[str, List[str]]
    platform_dependencies_formatted: Dict[str, str]
    plugin_dependencies: Dict[str, HangarPluginDependency]
    post_id: int
    review_state: HangarReviewState
    statistics: HangarVersionStatistics
    visibility: HangarVisibility


@dataclasses.dataclass
class HangarPaginatedVersionResult(HangarPaginatedResult):
    result: List[HangarVersion]
