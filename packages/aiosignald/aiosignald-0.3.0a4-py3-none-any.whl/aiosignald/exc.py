"""
Generated using https://signald.org/protocol.json
Version: '0.20.0-15-f159d1a5'=
"""

from .error import SignaldException
from .generated import *


class UntrustedIdentityError(SignaldException):
    identifier: str
    message: str
    identity_key: "IdentityKeyv1"


class ProtocolNoSessionError(SignaldException):
    sender: str
    timestamp: int
    message: str
    sender_device: int
    content_hint: int
    group_id: str


class DuplicateMessageError(SignaldException):
    timestamp: int
    message: str


class ProtocolInvalidMessageError(SignaldException):
    sender: str
    timestamp: int
    message: str
    sender_device: int
    content_hint: int
    group_id: str


class ProtocolInvalidKeyIdError(SignaldException):
    sender: str
    timestamp: int
    message: str
    sender_device: int
    content_hint: int
    group_id: str


class NoSuchAccountError(SignaldException):
    account: str
    message: str


class ServerNotFoundError(SignaldException):
    uuid: str
    message: str


class InvalidProxyError(SignaldException):
    message: str


class NoSendPermissionError(SignaldException):
    message: str


class InvalidAttachmentError(SignaldException):
    filename: str
    message: str


class InternalError(SignaldException):
    """
    an internal error in signald has occurred. typically these are things that "should never happen" such as issues saving to the local disk, but it is also the default error type and may catch some things that should have their own error type. If you find tht your code is depending on the exception list for any particular behavior, please file an issue so we can pull those errors out to a separate error type: https://gitlab.com/signald/signald/-/issues/new
    """

    exceptions: list[str]
    message: str


class InvalidRequestError(SignaldException):
    message: str


class UnknownGroupError(SignaldException):
    message: str


class RateLimitError(SignaldException):
    message: str


class InvalidRecipientError(SignaldException):
    message: str


class AttachmentTooLargeError(SignaldException):
    filename: str
    message: str


class AuthorizationFailedError(SignaldException):
    """
    Indicates the server rejected our credentials or a failed group update. Typically means the linked device was removed by the primary device, or that the account was re-registered. For group updates, this can indicate that we lack permissions.
    """

    message: str


class SQLError(SignaldException):
    message: str


class UnregisteredUserError(SignaldException):
    message: str
    e164_number: str


class OwnProfileKeyDoesNotExistError(SignaldException):
    message: str


class GroupPatchNotAcceptedError(SignaldException):
    """
    Indicates the server rejected our group update. This can be due to errors such as trying to add a user that's already in the group.
    """

    message: str


class GroupVerificationError(SignaldException):
    message: str


class InvalidGroupStateError(SignaldException):
    message: str


class InvalidInviteURIError(SignaldException):
    message: str


class GroupNotActiveError(SignaldException):
    message: str


class UnsupportedGroupError(SignaldException):
    """
    returned in response to use v1 groups, which are no longer supported
    """

    message: str


class InvalidBase64Error(SignaldException):
    message: str


class ProofRequiredError(SignaldException):
    token: str
    options: list[str]
    message: str
    retry_after: int


class ProfileUnavailableError(SignaldException):
    message: str


class NoKnownUUIDError(SignaldException):
    message: str


class NoSuchSessionError(SignaldException):
    message: str


class UserAlreadyExistsError(SignaldException):
    uuid: str
    message: str


class ScanTimeoutError(SignaldException):
    message: str


class CaptchaRequiredError(SignaldException):
    more: str
    message: str


class AccountHasNoKeysError(SignaldException):
    message: str


class AccountAlreadyVerifiedError(SignaldException):
    message: str


class AccountLockedError(SignaldException):
    more: str
    message: str


class FingerprintVersionMismatchError(SignaldException):
    message: str


class UnknownIdentityKeyError(SignaldException):
    message: str


class InvalidFingerprintError(SignaldException):
    message: str


class InvalidGroupError(SignaldException):
    message: str


class GroupLinkNotActiveError(SignaldException):
    message: str


__all__ = [
    "SignaldException",
    "UntrustedIdentityError",
    "ProtocolNoSessionError",
    "DuplicateMessageError",
    "ProtocolInvalidMessageError",
    "ProtocolInvalidKeyIdError",
    "NoSuchAccountError",
    "ServerNotFoundError",
    "InvalidProxyError",
    "NoSendPermissionError",
    "InvalidAttachmentError",
    "InternalError",
    "InvalidRequestError",
    "UnknownGroupError",
    "RateLimitError",
    "InvalidRecipientError",
    "AttachmentTooLargeError",
    "AuthorizationFailedError",
    "SQLError",
    "UnregisteredUserError",
    "OwnProfileKeyDoesNotExistError",
    "GroupPatchNotAcceptedError",
    "GroupVerificationError",
    "InvalidGroupStateError",
    "InvalidInviteURIError",
    "GroupNotActiveError",
    "UnsupportedGroupError",
    "InvalidBase64Error",
    "ProofRequiredError",
    "ProfileUnavailableError",
    "NoKnownUUIDError",
    "NoSuchSessionError",
    "UserAlreadyExistsError",
    "ScanTimeoutError",
    "CaptchaRequiredError",
    "AccountHasNoKeysError",
    "AccountAlreadyVerifiedError",
    "AccountLockedError",
    "FingerprintVersionMismatchError",
    "UnknownIdentityKeyError",
    "InvalidFingerprintError",
    "InvalidGroupError",
    "GroupLinkNotActiveError",
]
