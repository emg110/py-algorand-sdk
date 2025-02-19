from . import constants
from . import encoding
import decimal
import base64
import base58
import binascii
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError
from typing import Dict, Any


def microalgos_to_algos(microalgos):
    """
    Convert microalgos to algos.

    Args:
        microalgos (int): how many microalgos

    Returns:
        int or decimal: how many algos
    """
    return decimal.Decimal(microalgos) / constants.microalgos_to_algos_ratio


def algos_to_microalgos(algos):
    """
    Convert algos to microalgos.

    Args:
        algos (int or decimal): how many algos

    Returns:
        int: how many microalgos
    """
    return round(algos * constants.microalgos_to_algos_ratio)

def ipfscidv0_to_byte32(cid):
    """
    Convert ipfscidv0 to 32 bytes hex string.

    Args:
        cid (string): IPFS CID Version 0

    Returns:
        str: 32 Bytes long string
    """
    """bytes32 is converted back into Ipfs hash format."""

    decoded = base58.b58decode(cid)
    sliced_decoded = decoded[2:]
    return binascii.b2a_hex(sliced_decoded).decode("utf-8")


def byte32_to_ipfscidv0(hexstr):
    """
    Convert 32 bytes hex string to ipfscidv0.

    Args:
        hexstr (string): 32 Bytes long string

    Returns:
        str: IPFS CID Version 0
    """

    binary_str = binascii.a2b_hex(hexstr)
    completed_binary_str = b'\x12 ' + binary_str
    return base58.b58encode(completed_binary_str).decode("utf-8")



def sign_bytes(to_sign, private_key):
    """
    Sign arbitrary bytes after prepending with "MX" for domain separation.

    Args:
        to_sign (bytes): bytes to sign

    Returns:
        str: base64 signature
    """
    to_sign = constants.bytes_prefix + to_sign
    private_key = base64.b64decode(private_key)
    signing_key = SigningKey(private_key[: constants.key_len_bytes])
    signed = signing_key.sign(to_sign)
    signature = base64.b64encode(signed.signature).decode()
    return signature


def verify_bytes(message, signature, public_key):
    """
    Verify the signature of a message that was prepended with "MX" for domain
    separation.

    Args:
        message (bytes): message that was signed, without prefix
        signature (str): base64 signature
        public_key (str): base32 address

    Returns:
        bool: whether or not the signature is valid
    """
    verify_key = VerifyKey(encoding.decode_address(public_key))
    prefixed_message = constants.bytes_prefix + message
    try:
        verify_key.verify(prefixed_message, base64.b64decode(signature))
        return True
    except BadSignatureError:
        return False


def build_headers_from(
    kwarg_headers: Dict[str, Any], additional_headers: Dict[str, Any]
):
    """
    Build correct headers for `AlgodClient.algod_request`.

    Args:
        kwarg_headers (Dict[str, Any]): headers passed through kwargs.
        additional_headers (Dict[str, Any]): additional headers to pass to `AlgodClient.algod_request`

    Returns:
        Dict[str, any]: final version of headers dictionary to be used for `AlgodClient.algod_request`
    """
    if kwarg_headers:
        kwarg_headers.update(additional_headers)
    else:
        kwarg_headers = additional_headers

    return kwarg_headers
