import ctypes
from ctypes import wintypes
import sys

# ============================================================
# Windows Biometric Framework
# ============================================================

winbio = ctypes.WinDLL("winbio.dll")

# ============================================================
# Constants
# ============================================================

WINBIO_TYPE_FINGERPRINT = 0x00000008
WINBIO_POOL_SYSTEM = 1
WINBIO_FLAG_DEFAULT = 0

# Identity types
WINBIO_ID_TYPE_NULL = 1
WINBIO_ID_TYPE_WILDCARD = 2
WINBIO_ID_TYPE_GUID = 3
WINBIO_ID_TYPE_SID = 4


# ============================================================
# WINBIO_IDENTITY
# ============================================================

class ACCOUNT_SID(ctypes.Structure):
    _fields_ = [
        ("Size", wintypes.ULONG),
        ("Data", ctypes.c_ubyte * 68)
    ]


class IDENTITY_VALUE(ctypes.Union):
    _fields_ = [
        ("Null", wintypes.ULONG),
        ("Wildcard", wintypes.ULONG),
        ("AccountSid", ACCOUNT_SID)
    ]


class WINBIO_IDENTITY(ctypes.Structure):
    _fields_ = [
        ("Type", wintypes.ULONG),
        ("Value", IDENTITY_VALUE)
    ]


# ============================================================
# Function definitions
# ============================================================

winbio.WinBioOpenSession.argtypes = [
    wintypes.ULONG,
    wintypes.ULONG,
    wintypes.ULONG,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_void_p)
]

winbio.WinBioOpenSession.restype = wintypes.LONG


winbio.WinBioIdentify.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(wintypes.ULONG),
    ctypes.POINTER(WINBIO_IDENTITY),
    ctypes.POINTER(wintypes.ULONG),
    ctypes.POINTER(wintypes.ULONG)
]

winbio.WinBioIdentify.restype = wintypes.LONG


winbio.WinBioCloseSession.argtypes = [
    ctypes.c_void_p
]

winbio.WinBioCloseSession.restype = wintypes.LONG


# ============================================================
# Open biometric session
# ============================================================

session_handle = ctypes.c_void_p()

print()
print("==============================================")
print("     FINGERPRINT AUTHENTICATION TEST")
print("==============================================")
print()

print("Opening Windows Biometric Framework...")

result = winbio.WinBioOpenSession(
    WINBIO_TYPE_FINGERPRINT,
    WINBIO_POOL_SYSTEM,
    WINBIO_FLAG_DEFAULT,
    None,
    0,
    None,
    ctypes.byref(session_handle)
)

if result != 0:
    print()
    print("❌ Could not open biometric session.")
    print("Error:", hex(result & 0xFFFFFFFF))
    sys.exit(1)

print("✅ Biometric session opened.")
print()

# ============================================================
# Ask for fingerprint
# ============================================================

print("==============================================")
print("       PLACE YOUR ENROLLED FINGER")
print("          ON THE FINGERPRINT SENSOR")
print("==============================================")
print()
print("Waiting for fingerprint...")
print()

# ============================================================
# Variables for identification
# ============================================================

unit_id = wintypes.ULONG()
identity = WINBIO_IDENTITY()
sub_factor = wintypes.ULONG()
reject_detail = wintypes.ULONG()

# ============================================================
# Identify fingerprint
# ============================================================

result = winbio.WinBioIdentify(
    session_handle,
    ctypes.byref(unit_id),
    ctypes.byref(identity),
    ctypes.byref(sub_factor),
    ctypes.byref(reject_detail)
)

# ============================================================
# Process result
# ============================================================

print()

if result == 0:

    print("==============================================")
    print("       ✅ FINGERPRINT IDENTIFIED")
    print("==============================================")
    print()

    print("Authentication successful!")
    print("Biometric Unit ID:", unit_id.value)
    print("Identity Type:", identity.Type)
    print("Sub-factor:", sub_factor.value)
    print("Reject Detail:", reject_detail.value)

else:

    print("==============================================")
    print("       ❌ FINGERPRINT NOT IDENTIFIED")
    print("==============================================")
    print()

    print("Error code:", hex(result & 0xFFFFFFFF))
    print("Reject detail:", reject_detail.value)

# ============================================================
# Close session
# ============================================================

winbio.WinBioCloseSession(session_handle)

print()
print("Biometric session closed.")
print()
print("Test completed.")