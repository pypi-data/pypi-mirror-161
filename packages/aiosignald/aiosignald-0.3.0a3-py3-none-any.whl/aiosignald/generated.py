"""
Generated using https://signald.org/protocol.json
Version: '0.20.0-7-7d9179fd'=
"""
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass, field

from .util import JSONProtocol, locals_to_request, dict_to_nested_dataclass

if TYPE_CHECKING:
    from aiosignald.exc import *


@dataclass
class Stringv1:
    uri: str
    session_id: str


@dataclass
class JsonMessageRequestResponseMessagev1:
    groupId: str
    person: "JsonAddressv1"
    type: str


@dataclass
class JsonMessageRequestResponseMessagev0:
    groupId: str
    person: "JsonAddressv0"
    type: str


@dataclass
class GroupRequestingMemberv1:
    timestamp: int
    uuid: str


@dataclass
class JsonAccountListv0:
    accounts: list["JsonAccountv0"] = field(default_factory=list)


@dataclass
class JsonMessageEnvelopev0:
    username: Optional[str] = None
    uuid: Optional[str] = None
    source: Optional["JsonAddressv0"] = None
    sourceDevice: Optional[int] = None
    type: Optional[str] = None
    relay: Optional[str] = None
    timestamp: Optional[int] = None
    timestampISO: Optional[str] = None
    serverTimestamp: Optional[int] = None
    serverDeliveredTimestamp: Optional[int] = None
    hasLegacyMessage: Optional[bool] = None
    hasContent: Optional[bool] = None
    isUnidentifiedSender: Optional[bool] = None
    dataMessage: Optional["JsonDataMessagev0"] = None
    syncMessage: Optional["JsonSyncMessagev0"] = None
    callMessage: Optional["JsonCallMessagev0"] = None
    receipt: Optional["JsonReceiptMessagev0"] = None
    typing: Optional["JsonTypingMessagev0"] = None


@dataclass
class JsonAccountv0:
    deviceId: Optional[int] = None
    username: Optional[str] = None
    filename: Optional[str] = None
    uuid: Optional[str] = None
    registered: Optional[bool] = None
    has_keys: Optional[bool] = None
    subscribed: Optional[bool] = None


@dataclass
class JsonAddressv0:
    number: Optional[str] = None
    uuid: Optional[str] = None
    relay: Optional[str] = None


@dataclass
class JsonDataMessagev0:
    timestamp: Optional[int] = None
    attachments: list["JsonAttachmentv0"] = field(default_factory=list)
    body: Optional[str] = None
    group: Optional["JsonGroupInfov0"] = None
    groupV2: Optional["JsonGroupV2Infov0"] = None
    endSession: Optional[bool] = None
    expiresInSeconds: Optional[int] = None
    profileKeyUpdate: Optional[bool] = None
    quote: Optional["JsonQuotev0"] = None
    contacts: list["SharedContactv0"] = field(default_factory=list)
    previews: list["JsonPreviewv0"] = field(default_factory=list)
    sticker: Optional["JsonStickerv0"] = None
    viewOnce: Optional[bool] = None
    reaction: Optional["JsonReactionv0"] = None
    remoteDelete: Optional["RemoteDeletev0"] = None
    mentions: list["JsonMentionv0"] = field(default_factory=list)


@dataclass
class JsonSyncMessagev0:
    sent: Optional["JsonSentTranscriptMessagev0"] = None
    contacts: Optional["JsonAttachmentv0"] = None
    contactsComplete: Optional[bool] = None
    groups: Optional["JsonAttachmentv0"] = None
    blockedList: Optional["JsonBlockedListMessagev0"] = None
    request: Optional[str] = None
    readMessages: list["JsonReadMessagev0"] = field(default_factory=list)
    viewOnceOpen: Optional["JsonViewOnceOpenMessagev0"] = None
    verified: Optional["JsonVerifiedMessagev0"] = None
    configuration: Optional["ConfigurationMessagev0"] = None
    stickerPackOperations: list["JsonStickerPackOperationMessagev0"] = field(
        default_factory=list
    )
    fetchType: Optional[str] = None
    messageRequestResponse: Optional["JsonMessageRequestResponseMessagev0"] = None


@dataclass
class JsonCallMessagev0:
    offerMessage: Optional["OfferMessagev0"] = None
    answerMessage: Optional["AnswerMessagev0"] = None
    busyMessage: Optional["BusyMessagev0"] = None
    hangupMessage: Optional["HangupMessagev0"] = None
    iceUpdateMessages: list["IceUpdateMessagev0"] = field(default_factory=list)
    destinationDeviceId: Optional[int] = None
    isMultiRing: Optional[bool] = None


@dataclass
class JsonReceiptMessagev0:
    type: Optional[str] = None
    timestamps: list[int] = field(default_factory=list)
    when: Optional[int] = None


@dataclass
class JsonTypingMessagev0:
    action: Optional[str] = None
    timestamp: Optional[int] = None
    groupId: Optional[str] = None


@dataclass
class JsonAttachmentv0:
    contentType: Optional[str] = None
    id: Optional[str] = None
    size: Optional[int] = None
    storedFilename: Optional[str] = None
    filename: Optional[str] = None
    customFilename: Optional[str] = None
    caption: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    voiceNote: Optional[bool] = None
    key: Optional[str] = None
    digest: Optional[str] = None
    blurhash: Optional[str] = None


@dataclass
class JsonGroupInfov0:
    groupId: Optional[str] = None
    members: list["JsonAddressv0"] = field(default_factory=list)
    name: Optional[str] = None
    type: Optional[str] = None
    avatarId: Optional[int] = None


@dataclass
class JsonGroupV2Infov0:
    id: Optional[str] = None
    revision: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    timer: Optional[int] = None
    members: list["JsonAddressv0"] = field(default_factory=list)
    pendingMembers: list["JsonAddressv0"] = field(default_factory=list)
    requestingMembers: list["JsonAddressv0"] = field(default_factory=list)
    inviteLink: Optional[str] = None
    accessControl: Optional["GroupAccessControlv0"] = None
    memberDetail: list["GroupMemberv0"] = field(default_factory=list)
    pendingMemberDetail: list["GroupMemberv0"] = field(default_factory=list)


@dataclass
class JsonQuotev0:
    """
    A quote is a reply to a previous message. ID is the sent time of the message being replied to
    """

    id: Optional[int] = None
    author: Optional["JsonAddressv0"] = None
    text: Optional[str] = None
    attachments: list["JsonQuotedAttachmentv0"] = field(default_factory=list)
    mentions: list["JsonMentionv0"] = field(default_factory=list)


@dataclass
class SharedContactv0:
    name: Optional["Namev0"] = None
    avatar: Optional["Optionalv0"] = None
    phone: Optional["Optionalv0"] = None
    email: Optional["Optionalv0"] = None
    address: Optional["Optionalv0"] = None
    organization: Optional["Optionalv0"] = None


@dataclass
class JsonPreviewv0:
    url: Optional[str] = None
    title: Optional[str] = None
    attachment: Optional["JsonAttachmentv0"] = None


@dataclass
class JsonStickerv0:
    packID: Optional[str] = None
    packKey: Optional[str] = None
    stickerID: Optional[int] = None
    attachment: Optional["JsonAttachmentv0"] = None
    image: Optional[str] = None


@dataclass
class JsonReactionv0:
    emoji: Optional[str] = None
    remove: Optional[bool] = None
    targetAuthor: Optional["JsonAddressv0"] = None
    targetSentTimestamp: Optional[int] = None


@dataclass
class RemoteDeletev0:
    targetSentTimestamp: Optional[int] = None


@dataclass
class JsonMentionv0:
    uuid: Optional[str] = None
    start: Optional[int] = None
    length: Optional[int] = None


@dataclass
class JsonSentTranscriptMessagev0:
    destination: Optional["JsonAddressv0"] = None
    timestamp: Optional[int] = None
    expirationStartTimestamp: Optional[int] = None
    message: Optional["JsonDataMessagev0"] = None
    unidentifiedStatus: Optional[dict] = None
    isRecipientUpdate: Optional[bool] = None


@dataclass
class JsonBlockedListMessagev0:
    addresses: list["JsonAddressv0"] = field(default_factory=list)
    groupIds: list[str] = field(default_factory=list)


@dataclass
class JsonReadMessagev0:
    sender: Optional["JsonAddressv0"] = None
    timestamp: Optional[int] = None


@dataclass
class JsonViewOnceOpenMessagev0:
    sender: Optional["JsonAddressv0"] = None
    timestamp: Optional[int] = None


@dataclass
class JsonVerifiedMessagev0:
    destination: Optional["JsonAddressv0"] = None
    identityKey: Optional[str] = None
    verified: Optional[str] = None
    timestamp: Optional[int] = None


@dataclass
class ConfigurationMessagev0:
    readReceipts: Optional["Optionalv0"] = None
    unidentifiedDeliveryIndicators: Optional["Optionalv0"] = None
    typingIndicators: Optional["Optionalv0"] = None
    linkPreviews: Optional["Optionalv0"] = None


@dataclass
class JsonStickerPackOperationMessagev0:
    packID: Optional[str] = None
    packKey: Optional[str] = None
    type: Optional[str] = None


@dataclass
class OfferMessagev0:
    id: Optional[int] = None
    sdp: Optional[str] = None
    type: Optional["Typev0"] = None
    opaque: Optional[str] = None


@dataclass
class AnswerMessagev0:
    id: Optional[int] = None
    sdp: Optional[str] = None
    opaque: Optional[str] = None


@dataclass
class BusyMessagev0:
    id: Optional[int] = None


@dataclass
class HangupMessagev0:
    id: Optional[int] = None
    type: Optional["Typev0"] = None
    deviceId: Optional[int] = None
    legacy: Optional[bool] = None


@dataclass
class IceUpdateMessagev0:
    id: Optional[int] = None
    opaque: Optional[str] = None
    sdp: Optional[str] = None


@dataclass
class JsonQuotedAttachmentv0:
    contentType: Optional[str] = None
    fileName: Optional[str] = None
    thumbnail: Optional["JsonAttachmentv0"] = None


@dataclass
class GroupAccessControlv0:
    """
    group access control settings. Options for each controlled action are: UNKNOWN, ANY, MEMBER, ADMINISTRATOR, UNSATISFIABLE and UNRECOGNIZED
    """

    link: Optional[str] = None
    attributes: Optional[str] = None
    members: Optional[str] = None


@dataclass
class GroupMemberv0:
    uuid: Optional[str] = None
    role: Optional[str] = None
    joined_revision: Optional[int] = None


@dataclass
class Namev0:
    display: Optional["Optionalv0"] = None
    given: Optional["Optionalv0"] = None
    family: Optional["Optionalv0"] = None
    prefix: Optional["Optionalv0"] = None
    suffix: Optional["Optionalv0"] = None
    middle: Optional["Optionalv0"] = None


@dataclass
class Optionalv0:
    empty: Optional[bool] = None
    present: Optional[bool] = None


@dataclass
class Typev0:
    pass


@dataclass
class ClientMessageWrapperv1:
    """
    Wraps all incoming messages sent to the client after a v1 subscribe request is issued
    """

    type: Optional[str] = None
    version: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[bool] = None
    account: Optional[str] = None


@dataclass
class IncomingMessagev1:
    account: Optional[str] = None
    source: Optional["JsonAddressv1"] = None
    type: Optional[str] = None
    timestamp: Optional[int] = None
    source_device: Optional[int] = None
    server_receiver_timestamp: Optional[int] = None
    server_deliver_timestamp: Optional[int] = None
    has_legacy_message: Optional[bool] = None
    has_content: Optional[bool] = None
    unidentified_sender: Optional[bool] = None
    data_message: Optional["JsonDataMessagev1"] = None
    sync_message: Optional["JsonSyncMessagev1"] = None
    call_message: Optional["CallMessagev1"] = None
    receipt_message: Optional["ReceiptMessagev1"] = None
    typing_message: Optional["TypingMessagev1"] = None
    story_message: Optional["StoryMessagev1"] = None
    server_guid: Optional[str] = None


@dataclass
class ListenerStatev1:
    """
    prior attempt to indicate signald connectivity state. WebSocketConnectionState messages will be delivered at the  same time as well as in other parts of the websocket lifecycle.
    """

    connected: Optional[bool] = None


@dataclass
class WebSocketConnectionStatev1:
    """
    indicates when the websocket connection state to the signal server has changed
    """

    state: Optional[str] = None
    socket: Optional[str] = None


@dataclass
class StorageChangev1:
    """
    Broadcast to subscribed clients when there is a state change from the storage service
    """

    version: Optional[int] = None


@dataclass
class SendResponsev1:
    results: list["JsonSendMessageResultv1"] = field(default_factory=list)
    timestamp: Optional[int] = None


@dataclass
class JsonVersionMessagev1:
    name: Optional[str] = None
    version: Optional[str] = None
    branch: Optional[str] = None
    commit: Optional[str] = None


@dataclass
class JsonGroupV2Infov1:
    """
    Information about a Signal group
    """

    id: Optional[str] = None
    revision: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    timer: Optional[int] = None
    members: list["JsonAddressv1"] = field(default_factory=list)
    pendingMembers: list["JsonAddressv1"] = field(default_factory=list)
    requestingMembers: list["JsonAddressv1"] = field(default_factory=list)
    inviteLink: Optional[str] = None
    accessControl: Optional["GroupAccessControlv1"] = None
    memberDetail: list["GroupMemberv1"] = field(default_factory=list)
    pendingMemberDetail: list["GroupMemberv1"] = field(default_factory=list)
    announcements: Optional[str] = None
    removed: Optional[bool] = None
    banned_members: list["BannedGroupMemberv1"] = field(default_factory=list)
    group_change: Optional["GroupChangev1"] = None


@dataclass
class LinkedDevicesv1:
    devices: list["DeviceInfov1"] = field(default_factory=list)


@dataclass
class JsonGroupJoinInfov1:
    groupID: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    memberCount: Optional[int] = None
    addFromInviteLink: Optional[int] = None
    revision: Optional[int] = None
    pendingAdminApproval: Optional[bool] = None


@dataclass
class GroupInfov1:
    """
    A generic type that is used when the group version is not known
    """

    v1: Optional["JsonGroupInfov1"] = None
    v2: Optional["JsonGroupV2Infov1"] = None


@dataclass
class SetProfilev1:
    account: Optional[str] = None
    name: Optional[str] = None
    avatarFile: Optional[str] = None
    about: Optional[str] = None
    emoji: Optional[str] = None
    mobilecoin_address: Optional[str] = None
    visible_badge_ids: list[str] = field(default_factory=list)


@dataclass
class JsonAddressv1:
    number: Optional[str] = None
    uuid: Optional[str] = None
    relay: Optional[str] = None


@dataclass
class Profilev1:
    """
    Information about a Signal user
    """

    name: Optional[str] = None
    avatar: Optional[str] = None
    address: Optional["JsonAddressv1"] = None
    capabilities: Optional["Capabilitiesv1"] = None
    color: Optional[str] = None
    about: Optional[str] = None
    emoji: Optional[str] = None
    contact_name: Optional[str] = None
    profile_name: Optional[str] = None
    inbox_position: Optional[int] = None
    expiration_time: Optional[int] = None
    mobilecoin_address: Optional[str] = None
    visible_badge_ids: list[str] = field(default_factory=list)


@dataclass
class GroupListv1:
    groups: list["JsonGroupV2Infov1"] = field(default_factory=list)
    legacyGroups: list["JsonGroupInfov1"] = field(default_factory=list)


@dataclass
class ProfileListv1:
    profiles: list["Profilev1"] = field(default_factory=list)


@dataclass
class LinkingURIv1:
    uri: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class Accountv1:
    """
    A local account in signald
    """

    address: Optional["JsonAddressv1"] = None
    pending: Optional[bool] = None
    pni: Optional[str] = None
    device_id: Optional[int] = None
    account_id: Optional[str] = None


@dataclass
class IdentityKeyListv1:
    """
    a list of identity keys associated with a particular address
    """

    address: Optional["JsonAddressv1"] = None
    identities: list["IdentityKeyv1"] = field(default_factory=list)


@dataclass
class AccountListv1:
    accounts: list["Accountv1"] = field(default_factory=list)


@dataclass
class GetAllIdentitiesv1:
    """
    get all known identity keys
    """

    account: Optional[str] = None


@dataclass
class AllIdentityKeyListv1:
    identity_keys: list["IdentityKeyListv1"] = field(default_factory=list)


@dataclass
class ServerListv1:
    servers: list["Serverv1"] = field(default_factory=list)


@dataclass
class RemoteConfigListv1:
    config: list["RemoteConfigv1"] = field(default_factory=list)


@dataclass
class BooleanMessagev1:
    """
    A message containing a single boolean, usually as a response
    """

    value: Optional[bool] = None


@dataclass
class GroupHistoryPagev1:
    """
    The result of fetching a group's history along with paging data.
    """

    results: list["GroupHistoryEntryv1"] = field(default_factory=list)
    paging_data: Optional["PagingDatav1"] = None


@dataclass
class JsonSendMessageResultv1:
    address: Optional["JsonAddressv1"] = None
    success: Optional["SendSuccessv1"] = None
    networkFailure: Optional[bool] = None
    unregisteredFailure: Optional[bool] = None
    identityFailure: Optional[str] = None
    proof_required_failure: Optional["ProofRequiredError"] = None


@dataclass
class IdentityKeyv1:
    added: Optional[int] = None
    safety_number: Optional[str] = None
    qr_code_data: Optional[str] = None
    trust_level: Optional[str] = None


@dataclass
class JsonDataMessagev1:
    timestamp: Optional[int] = None
    attachments: list["JsonAttachmentv1"] = field(default_factory=list)
    body: Optional[str] = None
    group: Optional["JsonGroupInfov1"] = None
    groupV2: Optional["JsonGroupV2Infov1"] = None
    endSession: Optional[bool] = None
    expiresInSeconds: Optional[int] = None
    profileKeyUpdate: Optional[bool] = None
    quote: Optional["JsonQuotev1"] = None
    contacts: list["SharedContactv1"] = field(default_factory=list)
    previews: list["JsonPreviewv1"] = field(default_factory=list)
    sticker: Optional["JsonStickerv0"] = None
    viewOnce: Optional[bool] = None
    reaction: Optional["JsonReactionv1"] = None
    remoteDelete: Optional["RemoteDeletev1"] = None
    mentions: list["JsonMentionv1"] = field(default_factory=list)
    payment: Optional["Paymentv1"] = None
    is_expiration_update: Optional[bool] = None
    group_call_update: Optional[str] = None
    story_context: Optional["StoryContextv1"] = None


@dataclass
class JsonSyncMessagev1:
    sent: Optional["JsonSentTranscriptMessagev1"] = None
    contacts: Optional["JsonAttachmentv1"] = None
    contactsComplete: Optional[bool] = None
    groups: Optional["JsonAttachmentv1"] = None
    blockedList: Optional["JsonBlockedListMessagev1"] = None
    request: Optional[str] = None
    readMessages: list["JsonReadMessagev1"] = field(default_factory=list)
    viewOnceOpen: Optional["JsonViewOnceOpenMessagev1"] = None
    verified: Optional["JsonVerifiedMessagev1"] = None
    configuration: Optional["ConfigurationMessagev0"] = None
    stickerPackOperations: list["JsonStickerPackOperationMessagev0"] = field(
        default_factory=list
    )
    fetchType: Optional[str] = None
    messageRequestResponse: Optional["JsonMessageRequestResponseMessagev1"] = None


@dataclass
class CallMessagev1:
    offer_message: Optional["OfferMessagev1"] = None
    answer_message: Optional["AnswerMessagev1"] = None
    busy_message: Optional["BusyMessagev1"] = None
    hangup_message: Optional["HangupMessagev1"] = None
    ice_update_message: list["IceUpdateMessagev1"] = field(default_factory=list)
    destination_device_id: Optional[int] = None
    multi_ring: Optional[bool] = None


@dataclass
class ReceiptMessagev1:
    type: Optional[str] = None
    timestamps: list[int] = field(default_factory=list)
    when: Optional[int] = None


@dataclass
class TypingMessagev1:
    action: Optional[str] = None
    timestamp: Optional[int] = None
    group_id: Optional[str] = None


@dataclass
class StoryMessagev1:
    group: Optional["JsonGroupV2Infov1"] = None
    file: Optional["JsonAttachmentv1"] = None
    text: Optional["TextAttachmentv1"] = None
    allow_replies: Optional[bool] = None


@dataclass
class JsonAttachmentv1:
    """
    represents a file attached to a message. When sending, only `filename` is required.
    """

    contentType: Optional[str] = None
    id: Optional[str] = None
    size: Optional[int] = None
    storedFilename: Optional[str] = None
    filename: Optional[str] = None
    customFilename: Optional[str] = None
    caption: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    voiceNote: Optional[bool] = None
    key: Optional[str] = None
    digest: Optional[str] = None
    blurhash: Optional[str] = None


@dataclass
class JsonQuotev1:
    """
    A quote is a reply to a previous message. ID is the sent time of the message being replied to
    """

    id: Optional[int] = None
    author: Optional["JsonAddressv1"] = None
    text: Optional[str] = None
    attachments: list["JsonQuotedAttachmentv0"] = field(default_factory=list)
    mentions: list["JsonMentionv1"] = field(default_factory=list)


@dataclass
class JsonMentionv1:
    uuid: Optional[str] = None
    start: Optional[int] = None
    length: Optional[int] = None


@dataclass
class JsonPreviewv1:
    """
    metadata about one of the links in a message
    """

    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[int] = None
    attachment: Optional["JsonAttachmentv1"] = None


@dataclass
class JsonReactionv1:
    emoji: Optional[str] = None
    remove: Optional[bool] = None
    targetAuthor: Optional["JsonAddressv1"] = None
    targetSentTimestamp: Optional[int] = None


@dataclass
class GroupAccessControlv1:
    """
    group access control settings. Options for each controlled action are: UNKNOWN, ANY, MEMBER, ADMINISTRATOR, UNSATISFIABLE and UNRECOGNIZED
    """

    link: Optional[str] = None
    attributes: Optional[str] = None
    members: Optional[str] = None


@dataclass
class GroupMemberv1:
    uuid: Optional[str] = None
    role: Optional[str] = None
    joined_revision: Optional[int] = None


@dataclass
class BannedGroupMemberv1:
    uuid: Optional[str] = None
    timestamp: Optional[int] = None


@dataclass
class GroupChangev1:
    """
    Represents a group change made by a user. This can also represent request link invites. Only the fields relevant to the group change performed will be set. Note that in signald, group changes are currently only received from incoming messages from a message subscription.
    """

    editor: Optional["JsonAddressv1"] = None
    revision: Optional[int] = None
    new_members: list["GroupMemberv1"] = field(default_factory=list)
    delete_members: list["JsonAddressv1"] = field(default_factory=list)
    modify_member_roles: list["GroupMemberv1"] = field(default_factory=list)
    modified_profile_keys: list["GroupMemberv1"] = field(default_factory=list)
    new_pending_members: list["GroupPendingMemberv1"] = field(default_factory=list)
    delete_pending_members: list["JsonAddressv1"] = field(default_factory=list)
    promote_pending_members: list["GroupMemberv1"] = field(default_factory=list)
    new_banned_members: list["BannedGroupMemberv1"] = field(default_factory=list)
    new_unbanned_members: list["BannedGroupMemberv1"] = field(default_factory=list)
    new_title: Optional[str] = None
    new_avatar: Optional[bool] = None
    new_timer: Optional[int] = None
    new_access_control: Optional["GroupAccessControlv1"] = None
    new_requesting_members: list["GroupRequestingMemberv1"] = field(
        default_factory=list
    )
    delete_requesting_members: list["JsonAddressv1"] = field(default_factory=list)
    promote_requesting_members: list["GroupMemberv1"] = field(default_factory=list)
    new_invite_link_password: Optional[bool] = None
    new_description: Optional[str] = None
    new_is_announcement_group: Optional[str] = None


@dataclass
class DeviceInfov1:
    id: Optional[int] = None
    name: Optional[str] = None
    created: Optional[int] = None
    lastSeen: Optional[int] = None


@dataclass
class JsonGroupInfov1:
    """
    information about a legacy group
    """

    groupId: Optional[str] = None
    members: list["JsonAddressv1"] = field(default_factory=list)
    name: Optional[str] = None
    type: Optional[str] = None
    avatarId: Optional[int] = None


@dataclass
class Capabilitiesv1:
    gv2: Optional[bool] = None
    storage: Optional[bool] = None
    stories: Optional[bool] = None
    gv1_migration: Optional[bool] = None
    sender_key: Optional[bool] = None
    announcement_group: Optional[bool] = None
    change_number: Optional[bool] = None


@dataclass
class Serverv1:
    """
    a Signal server
    """

    uuid: Optional[str] = None
    proxy: Optional[str] = None
    ca: Optional[str] = None
    service_url: Optional[str] = None
    cdn_urls: list["ServerCDNv1"] = field(default_factory=list)
    contact_discovery_url: Optional[str] = None
    key_backup_url: Optional[str] = None
    storage_url: Optional[str] = None
    zk_param: Optional[str] = None
    unidentified_sender_root: Optional[str] = None
    key_backup_service_name: Optional[str] = None
    key_backup_service_id: Optional[str] = None
    key_backup_mrenclave: Optional[str] = None
    cds_mrenclave: Optional[str] = None
    ias_ca: Optional[str] = None


@dataclass
class Paymentv1:
    """
    details about a MobileCoin payment
    """

    receipt: Optional[str] = None
    note: Optional[str] = None


@dataclass
class RemoteConfigv1:
    """
    A remote config (feature flag) entry.
    """

    name: Optional[str] = None
    value: Optional[str] = None


@dataclass
class GroupHistoryEntryv1:
    group: Optional["JsonGroupV2Infov1"] = None
    change: Optional["GroupChangev1"] = None


@dataclass
class PagingDatav1:
    has_more_pages: Optional[bool] = None
    next_page_revision: Optional[int] = None


@dataclass
class JsonViewOnceOpenMessagev1:
    sender: Optional["JsonAddressv1"] = None
    timestamp: Optional[int] = None


@dataclass
class SendSuccessv1:
    unidentified: Optional[bool] = None
    needsSync: Optional[bool] = None
    duration: Optional[int] = None
    devices: list[int] = field(default_factory=list)


@dataclass
class SharedContactv1:
    name: Optional["SharedContactNamev1"] = None
    email: list["SharedContactEmailv1"] = field(default_factory=list)
    phone: list["SharedContactPhonev1"] = field(default_factory=list)
    address: list["SharedContactAddressv1"] = field(default_factory=list)
    avatar: Optional["SharedContactAvatarv1"] = None
    organization: Optional[str] = None


@dataclass
class RemoteDeletev1:
    target_sent_timestamp: Optional[int] = None


@dataclass
class StoryContextv1:
    author: Optional[str] = None
    sent_timestamp: Optional[int] = None


@dataclass
class JsonSentTranscriptMessagev1:
    destination: Optional["JsonAddressv1"] = None
    timestamp: Optional[int] = None
    expirationStartTimestamp: Optional[int] = None
    message: Optional["JsonDataMessagev1"] = None
    story: Optional["StoryMessagev1"] = None
    unidentifiedStatus: Optional[dict] = None
    isRecipientUpdate: Optional[bool] = None


@dataclass
class JsonBlockedListMessagev1:
    addresses: list["JsonAddressv1"] = field(default_factory=list)
    groupIds: list[str] = field(default_factory=list)


@dataclass
class JsonReadMessagev1:
    sender: Optional["JsonAddressv1"] = None
    timestamp: Optional[int] = None


@dataclass
class JsonVerifiedMessagev1:
    destination: Optional["JsonAddressv1"] = None
    identityKey: Optional[str] = None
    verified: Optional[str] = None
    timestamp: Optional[int] = None


@dataclass
class OfferMessagev1:
    id: Optional[int] = None
    sdp: Optional[str] = None
    type: Optional[str] = None
    opaque: Optional[str] = None


@dataclass
class AnswerMessagev1:
    id: Optional[int] = None
    sdp: Optional[str] = None
    opaque: Optional[str] = None


@dataclass
class BusyMessagev1:
    id: Optional[int] = None


@dataclass
class HangupMessagev1:
    id: Optional[int] = None
    type: Optional[str] = None
    legacy: Optional[bool] = None
    device_id: Optional[int] = None


@dataclass
class IceUpdateMessagev1:
    id: Optional[int] = None
    opaque: Optional[str] = None
    sdp: Optional[str] = None


@dataclass
class TextAttachmentv1:
    text: Optional[str] = None
    style: Optional[str] = None
    preview: Optional["JsonPreviewv1"] = None
    text_foreground_color: Optional[str] = None
    text_background_color: Optional[str] = None
    background_gradient: Optional["Gradientv1"] = None
    background_color: Optional[str] = None


@dataclass
class GroupPendingMemberv1:
    uuid: Optional[str] = None
    role: Optional[str] = None
    timestamp: Optional[int] = None
    added_by_uuid: Optional[str] = None


@dataclass
class ServerCDNv1:
    number: Optional[int] = None
    url: Optional[str] = None


@dataclass
class SharedContactNamev1:
    display: Optional[str] = None
    given: Optional[str] = None
    middle: Optional[str] = None
    family: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None


@dataclass
class SharedContactEmailv1:
    type: Optional[str] = None
    value: Optional[str] = None
    label: Optional[str] = None


@dataclass
class SharedContactPhonev1:
    type: Optional[str] = None
    value: Optional[str] = None
    label: Optional[str] = None


@dataclass
class SharedContactAddressv1:
    type: Optional[str] = None
    label: Optional[str] = None
    street: Optional[str] = None
    pobox: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None


@dataclass
class SharedContactAvatarv1:
    attachment: Optional["JsonAttachmentv1"] = None
    is_profile: Optional[bool] = None


@dataclass
class Gradientv1:
    start_color: Optional[str] = None
    end_color: Optional[str] = None


class SignaldGeneratedAPI(JSONProtocol):
    async def send(
        self,
        username: Optional[str] = None,
        account: Optional[str] = None,
        recipientAddress: Optional["JsonAddressv1"] = None,
        recipientGroupId: Optional[str] = None,
        messageBody: Optional[str] = None,
        attachments: Optional[list["JsonAttachmentv1"]] = None,
        quote: Optional["JsonQuotev1"] = None,
        timestamp: Optional[int] = None,
        mentions: Optional[list["JsonMentionv1"]] = None,
        previews: Optional[list["JsonPreviewv1"]] = None,
        members: Optional[list["JsonAddressv1"]] = None,
    ) -> SendResponsev1:
        """


        :param username: Example: "+12024561414"
        :param account: Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param recipientAddress:
        :param recipientGroupId: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param messageBody: Example: "hello"
        :param attachments:
        :param quote:
        :param timestamp:
        :param mentions:
        :param previews:
        :param members: Optionally set to a sub-set of group members. Ignored if recipientGroupId isn't specified
        """

        return dict_to_nested_dataclass(
            SendResponsev1,
            await self.get_response(
                {"type": "send", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def react(
        self,
        username: Optional[str] = None,
        recipientAddress: Optional["JsonAddressv1"] = None,
        recipientGroupId: Optional[str] = None,
        reaction: Optional["JsonReactionv1"] = None,
        timestamp: Optional[int] = None,
        members: Optional[list["JsonAddressv1"]] = None,
    ) -> SendResponsev1:
        """
        react to a previous message

        :param username: Example: "+12024561414"
        :param recipientAddress:
        :param recipientGroupId: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param reaction:
        :param timestamp:
        :param members: Optionally set to a sub-set of group members. Ignored if recipientGroupId isn't specified
        """

        return dict_to_nested_dataclass(
            SendResponsev1,
            await self.get_response(
                {"type": "react", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def version(
        self,
    ) -> JsonVersionMessagev1:
        """ """

        return dict_to_nested_dataclass(
            JsonVersionMessagev1,
            await self.get_response(
                {"type": "version", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def accept_invitation(
        self,
        account: Optional[str] = None,
        groupID: Optional[str] = None,
    ) -> JsonGroupV2Infov1:
        """
        Accept a v2 group invitation. Note that you must have a profile name set to join groups.

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param groupID: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        """

        return dict_to_nested_dataclass(
            JsonGroupV2Infov1,
            await self.get_response(
                {
                    "type": "accept_invitation",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def approve_membership(
        self,
        account: Optional[str] = None,
        groupID: Optional[str] = None,
        members: Optional[list["JsonAddressv1"]] = None,
    ) -> JsonGroupV2Infov1:
        """
        approve a request to join a group

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param groupID: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param members: list of requesting members to approve
        """

        return dict_to_nested_dataclass(
            JsonGroupV2Infov1,
            await self.get_response(
                {
                    "type": "approve_membership",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def get_group(
        self,
        account: Optional[str] = None,
        groupID: Optional[str] = None,
        revision: Optional[int] = None,
    ) -> JsonGroupV2Infov1:
        """
        Query the server for the latest state of a known group. If the account is not a member of the group, an UnknownGroupError is returned.

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param groupID: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param revision: the latest known revision, default value (-1) forces fetch from server
        """

        return dict_to_nested_dataclass(
            JsonGroupV2Infov1,
            await self.get_response(
                {"type": "get_group", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def get_linked_devices(
        self,
        account: Optional[str] = None,
    ) -> LinkedDevicesv1:
        """
        list all linked devices on a Signal account

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        """

        return dict_to_nested_dataclass(
            LinkedDevicesv1,
            await self.get_response(
                {
                    "type": "get_linked_devices",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def join_group(
        self,
        account: Optional[str] = None,
        uri: Optional[str] = None,
    ) -> JsonGroupJoinInfov1:
        """
        Join a group using the a signal.group URL. Note that you must have a profile name set to join groups.

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param uri: The signal.group URL Example: "https://signal.group/#CjQKINH_GZhXhfifTcnBkaKTNRxW-hHKnGSq-cJNyPVqHRp8EhDUB7zjKNEl0NaULhsqJCX3"
        """

        return dict_to_nested_dataclass(
            JsonGroupJoinInfov1,
            await self.get_response(
                {"type": "join_group", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def remove_linked_device(
        self,
        account: Optional[str] = None,
        deviceId: Optional[int] = None,
    ):
        """
        Remove a linked device from the Signal account. Only allowed when the local device id is 1

        :param account: The account to interact with Example: "+12024561414"
        :param deviceId: the ID of the device to unlink Example: 3
        """

        await self.get_response(
            {
                "type": "remove_linked_device",
                "version": "v1",
                **locals_to_request(locals()),
            }
        )

    async def update_group(
        self,
        account: Optional[str] = None,
        groupID: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        avatar: Optional[str] = None,
        updateTimer: Optional[int] = None,
        addMembers: Optional[list["JsonAddressv1"]] = None,
        removeMembers: Optional[list["JsonAddressv1"]] = None,
        updateRole: Optional["GroupMemberv1"] = None,
        updateAccessControl: Optional["GroupAccessControlv1"] = None,
        resetLink: Optional[bool] = None,
        announcements: Optional[str] = None,
    ) -> GroupInfov1:
        """
        modify a group. Note that only one modification action may be performed at once

        :param account: The identifier of the account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param groupID: the ID of the group to update Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param title: Example: "Parkdale Run Club"
        :param description: A new group description. Set to empty string to remove an existing description. Example: "A club for running in Parkdale"
        :param avatar: Example: "/tmp/image.jpg"
        :param updateTimer: update the group timer.
        :param addMembers:
        :param removeMembers:
        :param updateRole:
        :param updateAccessControl: note that only one of the access controls may be updated per request
        :param resetLink: regenerate the group link password, invalidating the old one
        :param announcements: ENABLED to only allow admins to post messages, DISABLED to allow anyone to post
        """

        return dict_to_nested_dataclass(
            GroupInfov1,
            await self.get_response(
                {"type": "update_group", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def set_profile(
        self,
        account: Optional[str] = None,
        name: Optional[str] = None,
        avatarFile: Optional[str] = None,
        about: Optional[str] = None,
        emoji: Optional[str] = None,
        mobilecoin_address: Optional[str] = None,
        visible_badge_ids: Optional[list[str]] = None,
    ):
        """


        :param account: The phone number of the account to use Example: "+12024561414"
        :param name: Change the profile name Example: "signald user"
        :param avatarFile: Path to new profile avatar file. If unset or null, unset the profile avatar Example: "/tmp/image.jpg"
        :param about: Change the 'about' profile field
        :param emoji: Change the profile emoji
        :param mobilecoin_address: Change the profile payment address. Payment address must be a *base64-encoded* MobileCoin address. Note that this is not the traditional MobileCoin address encoding, which is custom. Clients are responsible for converting between MobileCoin's custom base58 on the user-facing side and base64 encoding on the signald side.
        :param visible_badge_ids: configure visible badge IDs
        """

        await self.get_response(
            {"type": "set_profile", "version": "v1", **locals_to_request(locals())}
        )

    async def resolve_address(
        self,
        account: Optional[str] = None,
        partial: Optional["JsonAddressv1"] = None,
    ) -> JsonAddressv1:
        """
        Resolve a partial JsonAddress with only a number or UUID to one with both. Anywhere that signald accepts a JsonAddress will except a partial, this is a convenience function for client authors, mostly because signald doesn't resolve all the partials it returns.

        :param account: The signal account to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param partial: The partial address, missing fields
        """

        return dict_to_nested_dataclass(
            JsonAddressv1,
            await self.get_response(
                {
                    "type": "resolve_address",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def mark_read(
        self,
        account: Optional[str] = None,
        to: Optional["JsonAddressv1"] = None,
        timestamps: Optional[list[int]] = None,
        when: Optional[int] = None,
    ):
        """


        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param to: The address that sent the message being marked as read
        :param timestamps: List of messages to mark as read Example: 1615576442475
        :param when:
        """

        await self.get_response(
            {"type": "mark_read", "version": "v1", **locals_to_request(locals())}
        )

    async def get_profile(
        self,
        account: Optional[str] = None,
        async_: Optional[bool] = None,
        address: Optional["JsonAddressv1"] = None,
    ) -> Profilev1:
        """
        Get all information available about a user

        :param account: the signald account to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param async_: if true, return results from local store immediately, refreshing from server in the background if needed. if false (default), block until profile can be retrieved from server
        :param address: the address to look up
        """

        return dict_to_nested_dataclass(
            Profilev1,
            await self.get_response(
                {"type": "get_profile", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def list_groups(
        self,
        account: Optional[str] = None,
    ) -> GroupListv1:
        """


        :param account: Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        """

        return dict_to_nested_dataclass(
            GroupListv1,
            await self.get_response(
                {"type": "list_groups", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def list_contacts(
        self,
        account: Optional[str] = None,
        async_: Optional[bool] = None,
    ) -> ProfileListv1:
        """


        :param account: Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param async_: return results from local store immediately, refreshing from server afterward if needed. If false (default), block until all pending profiles have been retrieved.
        """

        return dict_to_nested_dataclass(
            ProfileListv1,
            await self.get_response(
                {
                    "type": "list_contacts",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def create_group(
        self,
        account: Optional[str] = None,
        title: Optional[str] = None,
        avatar: Optional[str] = None,
        members: Optional[list["JsonAddressv1"]] = None,
        timer: Optional[int] = None,
        member_role: Optional[str] = None,
    ) -> JsonGroupV2Infov1:
        """


        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param title: Example: "Parkdale Run Club"
        :param avatar: Example: "/tmp/image.jpg"
        :param members:
        :param timer: the message expiration timer
        :param member_role: The role of all members other than the group creator. Options are ADMINISTRATOR or DEFAULT (case insensitive) Example: "ADMINISTRATOR"
        """

        return dict_to_nested_dataclass(
            JsonGroupV2Infov1,
            await self.get_response(
                {"type": "create_group", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def leave_group(
        self,
        account: Optional[str] = None,
        groupID: Optional[str] = None,
    ) -> GroupInfov1:
        """


        :param account: The account to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param groupID: The group to leave Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        """

        return dict_to_nested_dataclass(
            GroupInfov1,
            await self.get_response(
                {"type": "leave_group", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def generate_linking_uri(
        self,
        server: Optional[str] = None,
    ) -> LinkingURIv1:
        """
        Generate a linking URI. Typically this is QR encoded and scanned by the primary device. Submit the returned session_id with a finish_link request.

        :param server: The identifier of the server to use. Leave blank for default (usually Signal production servers but configurable at build time)
        """

        return dict_to_nested_dataclass(
            LinkingURIv1,
            await self.get_response(
                {
                    "type": "generate_linking_uri",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def finish_link(
        self,
        overwrite: Optional[bool] = None,
        device_name: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Accountv1:
        """
        After a linking URI has been requested, finish_link must be called with the session_id provided with the URI. it will return information about the new account once the linking process is completed by the other device and the new account is setup. Note that the account setup process can sometimes take some time, if rapid userfeedback is required after scanning, use wait_for_scan first, then finish setup with finish_link.

        :param overwrite: overwrite existing account data if the phone number conflicts. false by default
        :param device_name:
        :param session_id:
        """

        return dict_to_nested_dataclass(
            Accountv1,
            await self.get_response(
                {"type": "finish_link", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def add_device(
        self,
        account: Optional[str] = None,
        uri: Optional[str] = None,
    ):
        """
        Link a new device to a local Signal account

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param uri: the sgnl://linkdevice uri provided (typically in qr code form) by the new device Example: "sgnl://linkdevice?uuid=jAaZ5lxLfh7zVw5WELd6-Q&pub_key=BfFbjSwmAgpVJBXUdfmSgf61eX3a%2Bq9AoxAVpl1HUap9"
        """

        await self.get_response(
            {"type": "add_device", "version": "v1", **locals_to_request(locals())}
        )

    async def register(
        self,
        account: Optional[str] = None,
        voice: Optional[bool] = None,
        captcha: Optional[str] = None,
        server: Optional[str] = None,
    ) -> Accountv1:
        """
        begin the account registration process by requesting a phone number verification code. when the code is received, submit it with a verify request

        :param account: the e164 phone number to register with Example: "+12024561414"
        :param voice: set to true to request a voice call instead of an SMS for verification
        :param captcha: See https://signald.org/articles/captcha/
        :param server: The identifier of the server to use. Leave blank for default (usually Signal production servers but configurable at build time)
        """

        return dict_to_nested_dataclass(
            Accountv1,
            await self.get_response(
                {"type": "register", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def verify(
        self,
        account: Optional[str] = None,
        code: Optional[str] = None,
    ) -> Accountv1:
        """
        verify an account's phone number with a code after registering, completing the account creation process

        :param account: the e164 phone number being verified Example: "+12024561414"
        :param code: the verification code, dash (-) optional Example: "555555"
        """

        return dict_to_nested_dataclass(
            Accountv1,
            await self.get_response(
                {"type": "verify", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def get_identities(
        self,
        account: Optional[str] = None,
        address: Optional["JsonAddressv1"] = None,
    ) -> IdentityKeyListv1:
        """
        Get information about a known keys for a particular address

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param address: address to get keys for
        """

        return dict_to_nested_dataclass(
            IdentityKeyListv1,
            await self.get_response(
                {
                    "type": "get_identities",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def trust(
        self,
        account: Optional[str] = None,
        address: Optional["JsonAddressv1"] = None,
        safety_number: Optional[str] = None,
        qr_code_data: Optional[str] = None,
        trust_level: Optional[str] = None,
    ):
        """
        Trust another user's safety number using either the QR code data or the safety number text

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param address: The user to query identity keys for
        :param safety_number: required if qr_code_data is absent Example: "373453558586758076680580548714989751943247272727416091564451"
        :param qr_code_data: base64-encoded QR code data. required if safety_number is absent
        :param trust_level: One of TRUSTED_UNVERIFIED, TRUSTED_VERIFIED or UNTRUSTED. Default is TRUSTED_VERIFIED Example: "TRUSTED_VERIFIED"
        """

        await self.get_response(
            {"type": "trust", "version": "v1", **locals_to_request(locals())}
        )

    async def delete_account(
        self,
        account: Optional[str] = None,
        server: Optional[bool] = None,
    ):
        """
        delete all account data signald has on disk, and optionally delete the account from the server as well. Note that this is not "unlink" and will delete the entire account, even from a linked device.

        :param account: The account to delete Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param server: delete account information from the server as well (default false)
        """

        await self.get_response(
            {"type": "delete_account", "version": "v1", **locals_to_request(locals())}
        )

    async def typing(
        self,
        account: Optional[str] = None,
        address: Optional["JsonAddressv1"] = None,
        group: Optional[str] = None,
        typing: Optional[bool] = None,
        when: Optional[int] = None,
    ):
        """
        send a typing started or stopped message

        :param account: The account to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param address:
        :param group: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param typing: Example: true
        :param when:
        """

        await self.get_response(
            {"type": "typing", "version": "v1", **locals_to_request(locals())}
        )

    async def reset_session(
        self,
        account: Optional[str] = None,
        address: Optional["JsonAddressv1"] = None,
        timestamp: Optional[int] = None,
    ) -> SendResponsev1:
        """
        reset a session with a particular user

        :param account: The account to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param address: the user to reset session with
        :param timestamp:
        """

        return dict_to_nested_dataclass(
            SendResponsev1,
            await self.get_response(
                {
                    "type": "reset_session",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def request_sync(
        self,
        groups: Optional[bool] = None,
        configuration: Optional[bool] = None,
        contacts: Optional[bool] = None,
        blocked: Optional[bool] = None,
        keys: Optional[bool] = None,
        account: Optional[str] = None,
    ):
        """
        Request other devices on the account send us their group list, syncable config and contact list.

        :param groups: request group sync (default true)
        :param configuration: request configuration sync (default true)
        :param contacts: request contact sync (default true)
        :param blocked: request block list sync (default true)
        :param keys: request storage service keys
        :param account: The account to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        """

        await self.get_response(
            {"type": "request_sync", "version": "v1", **locals_to_request(locals())}
        )

    async def list_accounts(
        self,
    ) -> AccountListv1:
        """
        return all local accounts

        """

        return dict_to_nested_dataclass(
            AccountListv1,
            await self.get_response(
                {
                    "type": "list_accounts",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def group_link_info(
        self,
        account: Optional[str] = None,
        uri: Optional[str] = None,
    ) -> JsonGroupJoinInfov1:
        """
        Get information about a group from a signal.group link

        :param account: The account to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param uri: the signald.group link Example: "https://signal.group/#CjQKINH_GZhXhfifTcnBkaKTNRxW-hHKnGSq-cJNyPVqHRp8EhDUB7zjKNEl0NaULhsqJCX3"
        """

        return dict_to_nested_dataclass(
            JsonGroupJoinInfov1,
            await self.get_response(
                {
                    "type": "group_link_info",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def update_contact(
        self,
        account: Optional[str] = None,
        address: Optional["JsonAddressv1"] = None,
        name: Optional[str] = None,
        color: Optional[str] = None,
        inbox_position: Optional[int] = None,
    ) -> Profilev1:
        """
        update information about a local contact

        :param account: Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param address:
        :param name:
        :param color:
        :param inbox_position:
        """

        return dict_to_nested_dataclass(
            Profilev1,
            await self.get_response(
                {
                    "type": "update_contact",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def set_expiration(
        self,
        account: Optional[str] = None,
        address: Optional["JsonAddressv1"] = None,
        group: Optional[str] = None,
        expiration: Optional[int] = None,
    ) -> SendResponsev1:
        """
        Set the message expiration timer for a thread. Expiration must be specified in seconds, set to 0 to disable timer

        :param account: The account to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param address:
        :param group: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param expiration: Example: 604800
        """

        return dict_to_nested_dataclass(
            SendResponsev1,
            await self.get_response(
                {
                    "type": "set_expiration",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def set_device_name(
        self,
        account: Optional[str] = None,
        device_name: Optional[str] = None,
    ):
        """
        set this device's name. This will show up on the mobile device on the same account under settings -> linked devices

        :param account: The account to set the device name of Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param device_name: The device name
        """

        await self.get_response(
            {"type": "set_device_name", "version": "v1", **locals_to_request(locals())}
        )

    async def get_all_identities(
        self,
        account: Optional[str] = None,
    ) -> AllIdentityKeyListv1:
        """
        get all known identity keys

        :param account: The account to interact with Example: "+12024561414"
        """

        return dict_to_nested_dataclass(
            AllIdentityKeyListv1,
            await self.get_response(
                {
                    "type": "get_all_identities",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def subscribe(
        self,
        account: Optional[str] = None,
    ):
        """
        receive incoming messages. After making a subscribe request, incoming messages will be sent to the client encoded as ClientMessageWrapper. Send an unsubscribe request or disconnect from the socket to stop receiving messages.

        :param account: The account to subscribe to incoming message for Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        """

        await self.get_response(
            {"type": "subscribe", "version": "v1", **locals_to_request(locals())}
        )

    async def unsubscribe(
        self,
        account: Optional[str] = None,
    ):
        """
        See subscribe for more info

        :param account: The account to unsubscribe from Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        """

        await self.get_response(
            {"type": "unsubscribe", "version": "v1", **locals_to_request(locals())}
        )

    async def remote_delete(
        self,
        account: Optional[str] = None,
        address: Optional["JsonAddressv1"] = None,
        group: Optional[str] = None,
        timestamp: Optional[int] = None,
        members: Optional[list["JsonAddressv1"]] = None,
    ) -> SendResponsev1:
        """
        delete a message previously sent

        :param account: the account to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param address: the address to send the delete message to. should match address the message to be deleted was sent to. required if group is not set.
        :param group: the group to send the delete message to. should match group the message to be deleted was sent to. required if address is not set. Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param timestamp:
        :param members: Optionally set to a sub-set of group members. Ignored if group isn't specified
        """

        return dict_to_nested_dataclass(
            SendResponsev1,
            await self.get_response(
                {
                    "type": "remote_delete",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def add_server(
        self,
        server: Optional["Serverv1"] = None,
    ) -> Stringv1:
        """
        add a new server to connect to. Returns the new server's UUID.

        :param server:
        """

        return dict_to_nested_dataclass(
            Stringv1,
            await self.get_response(
                {"type": "add_server", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def get_servers(
        self,
    ) -> ServerListv1:
        """ """

        return dict_to_nested_dataclass(
            ServerListv1,
            await self.get_response(
                {"type": "get_servers", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def delete_server(
        self,
        uuid: Optional[str] = None,
    ):
        """


        :param uuid:
        """

        await self.get_response(
            {"type": "delete_server", "version": "v1", **locals_to_request(locals())}
        )

    async def send_payment(
        self,
        account: Optional[str] = None,
        address: Optional["JsonAddressv1"] = None,
        payment: Optional["Paymentv1"] = None,
        when: Optional[int] = None,
    ) -> SendResponsev1:
        """
        send a mobilecoin payment

        :param account: the account to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param address: the address to send the payment message to
        :param payment:
        :param when:
        """

        return dict_to_nested_dataclass(
            SendResponsev1,
            await self.get_response(
                {"type": "send_payment", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def get_remote_config(
        self,
        account: Optional[str] = None,
    ) -> RemoteConfigListv1:
        """
        Retrieves the remote config (feature flags) from the server.

        :param account: The account to use to retrieve the remote config Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        """

        return dict_to_nested_dataclass(
            RemoteConfigListv1,
            await self.get_response(
                {
                    "type": "get_remote_config",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def refuse_membership(
        self,
        account: Optional[str] = None,
        members: Optional[list["JsonAddressv1"]] = None,
        group_id: Optional[str] = None,
        also_ban: Optional[bool] = None,
    ) -> JsonGroupV2Infov1:
        """
        deny a request to join a group

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param members: list of requesting members to refuse
        :param group_id: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param also_ban:
        """

        return dict_to_nested_dataclass(
            JsonGroupV2Infov1,
            await self.get_response(
                {
                    "type": "refuse_membership",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def submit_challenge(
        self,
        account: Optional[str] = None,
        challenge: Optional[str] = None,
        captcha_token: Optional[str] = None,
    ):
        """


        :param account: Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param challenge:
        :param captcha_token:
        """

        await self.get_response(
            {"type": "submit_challenge", "version": "v1", **locals_to_request(locals())}
        )

    async def is_identifier_registered(
        self,
        account: Optional[str] = None,
        identifier: Optional[str] = None,
    ) -> BooleanMessagev1:
        """
        Determine whether an account identifier is registered on the Signal service.

        :param account: The account to use to use Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param identifier: The UUID of an identifier to check if it is registered on Signal. This UUID is either a Phone Number Identity (PNI) or an Account Identity (ACI). Example: "aeed01f0-a234-478e-8cf7-261c283151e7"
        """

        return dict_to_nested_dataclass(
            BooleanMessagev1,
            await self.get_response(
                {
                    "type": "is_identifier_registered",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def wait_for_scan(
        self,
        session_id: Optional[str] = None,
    ):
        """
        An optional part of the linking process. Intended to be called after displaying the QR code, will return quickly after the user scans the QR code. finish_link must be called after wait_for_scan returns a non-error

        :param session_id:
        """

        await self.get_response(
            {"type": "wait_for_scan", "version": "v1", **locals_to_request(locals())}
        )

    async def get_group_revision_pages(
        self,
        account: Optional[str] = None,
        group_id: Optional[str] = None,
        from_revision: Optional[int] = None,
        include_first_revision: Optional[bool] = None,
    ) -> GroupHistoryPagev1:
        """
        Query the server for group revision history. The history contains information about the changes between each revision and the user that made the change.

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param group_id: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param from_revision: The revision to start the pages from. Note that if this is lower than the revision you joined the group, an AuthorizationFailedError is returned.
        :param include_first_revision: Whether to include the first state in the returned pages (default false)
        """

        return dict_to_nested_dataclass(
            GroupHistoryPagev1,
            await self.get_response(
                {
                    "type": "get_group_revision_pages",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def send_sync_message(
        self,
        account: Optional[str] = None,
        view_once_open_message: Optional["JsonViewOnceOpenMessagev1"] = None,
        message_request_response: Optional[
            "JsonMessageRequestResponseMessagev1"
        ] = None,
    ) -> JsonSendMessageResultv1:
        """
        Sends a sync message to the account's devices

        :param account: Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param view_once_open_message: This can be set to indicate to other devices about having viewed a view-once message.
        :param message_request_response: This can be set to indicate to other devices about a response to an incoming message request from an unknown user or group. Warning: Using the BLOCK and BLOCK_AND_DELETE options relies on other devices to do the blocking, and it does not make you leave the group!
        """

        return dict_to_nested_dataclass(
            JsonSendMessageResultv1,
            await self.get_response(
                {
                    "type": "send_sync_message",
                    "version": "v1",
                    **locals_to_request(locals()),
                }
            ),
        )

    async def ban_user(
        self,
        account: Optional[str] = None,
        group_id: Optional[str] = None,
        users: Optional[list["JsonAddressv1"]] = None,
    ) -> JsonGroupV2Infov1:
        """
        Bans users from a group. This works even if the users aren't in the group. If they are currently in the group, they will also be removed.

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param group_id: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param users: List of users to ban
        """

        return dict_to_nested_dataclass(
            JsonGroupV2Infov1,
            await self.get_response(
                {"type": "ban_user", "version": "v1", **locals_to_request(locals())}
            ),
        )

    async def unban_user(
        self,
        account: Optional[str] = None,
        group_id: Optional[str] = None,
        users: Optional[list["JsonAddressv1"]] = None,
    ) -> JsonGroupV2Infov1:
        """
        Unbans users from a group.

        :param account: The account to interact with Example: "0cc10e61-d64c-4dbc-b51c-334f7dd45a4a"
        :param group_id: Example: "EdSqI90cS0UomDpgUXOlCoObWvQOXlH5G3Z2d3f4ayE="
        :param users: List of users to unban
        """

        return dict_to_nested_dataclass(
            JsonGroupV2Infov1,
            await self.get_response(
                {"type": "unban_user", "version": "v1", **locals_to_request(locals())}
            ),
        )


__all__ = [
    "SignaldGeneratedAPI",
    "JsonAccountListv0",
    "JsonMessageEnvelopev0",
    "JsonAccountv0",
    "JsonAddressv0",
    "JsonDataMessagev0",
    "JsonSyncMessagev0",
    "JsonCallMessagev0",
    "JsonReceiptMessagev0",
    "JsonTypingMessagev0",
    "JsonAttachmentv0",
    "JsonGroupInfov0",
    "JsonGroupV2Infov0",
    "JsonQuotev0",
    "SharedContactv0",
    "JsonPreviewv0",
    "JsonStickerv0",
    "JsonReactionv0",
    "RemoteDeletev0",
    "JsonMentionv0",
    "JsonSentTranscriptMessagev0",
    "JsonBlockedListMessagev0",
    "JsonReadMessagev0",
    "JsonViewOnceOpenMessagev0",
    "JsonVerifiedMessagev0",
    "ConfigurationMessagev0",
    "JsonStickerPackOperationMessagev0",
    "OfferMessagev0",
    "AnswerMessagev0",
    "BusyMessagev0",
    "HangupMessagev0",
    "IceUpdateMessagev0",
    "JsonQuotedAttachmentv0",
    "GroupAccessControlv0",
    "GroupMemberv0",
    "Namev0",
    "Optionalv0",
    "Typev0",
    "ClientMessageWrapperv1",
    "IncomingMessagev1",
    "ListenerStatev1",
    "WebSocketConnectionStatev1",
    "StorageChangev1",
    "SendResponsev1",
    "JsonVersionMessagev1",
    "JsonGroupV2Infov1",
    "LinkedDevicesv1",
    "JsonGroupJoinInfov1",
    "GroupInfov1",
    "SetProfilev1",
    "JsonAddressv1",
    "Profilev1",
    "GroupListv1",
    "ProfileListv1",
    "LinkingURIv1",
    "Accountv1",
    "IdentityKeyListv1",
    "AccountListv1",
    "GetAllIdentitiesv1",
    "AllIdentityKeyListv1",
    "ServerListv1",
    "RemoteConfigListv1",
    "BooleanMessagev1",
    "GroupHistoryPagev1",
    "JsonSendMessageResultv1",
    "IdentityKeyv1",
    "JsonDataMessagev1",
    "JsonSyncMessagev1",
    "CallMessagev1",
    "ReceiptMessagev1",
    "TypingMessagev1",
    "StoryMessagev1",
    "JsonAttachmentv1",
    "JsonQuotev1",
    "JsonMentionv1",
    "JsonPreviewv1",
    "JsonReactionv1",
    "GroupAccessControlv1",
    "GroupMemberv1",
    "BannedGroupMemberv1",
    "GroupChangev1",
    "DeviceInfov1",
    "JsonGroupInfov1",
    "Capabilitiesv1",
    "Serverv1",
    "Paymentv1",
    "RemoteConfigv1",
    "GroupHistoryEntryv1",
    "PagingDatav1",
    "JsonViewOnceOpenMessagev1",
    "SendSuccessv1",
    "SharedContactv1",
    "RemoteDeletev1",
    "StoryContextv1",
    "JsonSentTranscriptMessagev1",
    "JsonBlockedListMessagev1",
    "JsonReadMessagev1",
    "JsonVerifiedMessagev1",
    "OfferMessagev1",
    "AnswerMessagev1",
    "BusyMessagev1",
    "HangupMessagev1",
    "IceUpdateMessagev1",
    "TextAttachmentv1",
    "GroupPendingMemberv1",
    "ServerCDNv1",
    "SharedContactNamev1",
    "SharedContactEmailv1",
    "SharedContactPhonev1",
    "SharedContactAddressv1",
    "SharedContactAvatarv1",
    "Gradientv1",
]
