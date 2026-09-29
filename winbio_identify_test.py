import ctypes
from ctypes import wintypes


# --------------------------------------------------
# Load Windows Biometric Framework
# --------------------------------------------------

winbio = ctypes.WinDLL("winbio.dll")


# --------------------------------------------------
# Constants
# --------------------------------------------------

WINBIO_TYPE_FINGERPRINT = 0x00000008
WINBIO_POOL_SYSTEM = 0x00000001
WINBIO_FLAG_DEFAULT = 0x00000000

WINBIO_E_UNKNOWN_ID = 0x80098004


# --------------------------------------------------
# WINBIO_IDENTITY structures
# --------------------------------------------------

class WINBIO_IDENTITY_UNION(ctypes.Union):

    _fields_ = [
        ("Null", ctypes.c_ubyte * 32),
        ("TemplateGuid", ctypes.c_ubyte * 16),
        ("AccountSid", ctypes.c_ubyte * 68),
    ]


class WINBIO_IDENTITY(ctypes.Structure):

    _fields_ = [
        ("Type", wintypes.DWORD),
        ("Value", WINBIO_IDENTITY_UNION),
    ]


# --------------------------------------------------
# WinBioOpenSession
# --------------------------------------------------

WinBioOpenSession = winbio.WinBioOpenSession

WinBioOpenSession.argtypes = [
    wintypes.DWORD,       # Factor
    wintypes.DWORD,       # Pool
    wintypes.DWORD,       # Flags
    ctypes.c_void_p,      # Unit IDs
    wintypes.ULONG,       # Unit count
    ctypes.c_void_p,      # Database ID
    ctypes.POINTER(wintypes.HANDLE)
]

WinBioOpenSession.restype = ctypes.c_long


# --------------------------------------------------
# WinBioIdentify
# --------------------------------------------------

WinBioIdentify = winbio.WinBioIdentify

WinBioIdentify.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(WINBIO_IDENTITY),
    ctypes.POINTER(wintypes.BYTE),
    ctypes.POINTER(wintypes.DWORD)
]

WinBioIdentify.restype = ctypes.c_long


# --------------------------------------------------
# WinBioCloseSession
# --------------------------------------------------

WinBioCloseSession = winbio.WinBioCloseSession

WinBioCloseSession.argtypes = [
    wintypes.HANDLE
]

WinBioCloseSession.restype = ctypes.c_long


# --------------------------------------------------
# OPEN BIOMETRIC SESSION
# --------------------------------------------------

session = wintypes.HANDLE()


print()
print("======================================")
print(" Windows Fingerprint Identification")
print("======================================")
print()

print("Opening fingerprint session...")


result = WinBioOpenSession(
    WINBIO_TYPE_FINGERPRINT,
    WINBIO_POOL_SYSTEM,
    WINBIO_FLAG_DEFAULT,
    None,
    0,
    None,
    ctypes.byref(session)
)


print(
    "WinBioOpenSession result:",
    hex(result & 0xFFFFFFFF)
)


if result != 0:

    print()
    print("❌ Could not open biometric session.")
    print()

    input("Press Enter to exit...")

    raise SystemExit


print()
print("✅ Biometric session opened.")
print()

print("👉 PLACE YOUR ENROLLED FINGER ON THE SENSOR.")
print()

print("Waiting for fingerprint...")


# --------------------------------------------------
# IDENTIFY FINGERPRINT
# --------------------------------------------------

unit_id = wintypes.DWORD()

identity = WINBIO_IDENTITY()

subfactor = wintypes.BYTE()

reject_detail = wintypes.DWORD()


result = WinBioIdentify(
    session,
    ctypes.byref(unit_id),
    ctypes.byref(identity),
    ctypes.byref(subfactor),
    ctypes.byref(reject_detail)
)


print()

print(
    "WinBioIdentify result:",
    hex(result & 0xFFFFFFFF)
)


# --------------------------------------------------
# RESULT
# --------------------------------------------------

if result == 0:

    print()
    print("======================================")
    print("✅ FINGERPRINT MATCHED")
    print("======================================")
    print()

    print(
        "Biometric Unit ID:",
        unit_id.value
    )

    print(
        "Identity Type:",
        identity.Type
    )

    print(
        "Subfactor:",
        subfactor.value
    )

    print()
    print(
        "Windows identified an enrolled "
        "fingerprint successfully."
    )


elif (result & 0xFFFFFFFF) == WINBIO_E_UNKNOWN_ID:

    print()
    print("======================================")
    print("❌ FINGERPRINT NOT RECOGNIZED")
    print("======================================")
    print()

    print(
        "The fingerprint does not match "
        "a stored Windows biometric template."
    )


else:

    print()
    print("======================================")
    print("❌ IDENTIFICATION FAILED")
    print("======================================")
    print()

    print(
        "Error code:",
        hex(result & 0xFFFFFFFF)
    )

    print(
        "Reject detail:",
        reject_detail.value
    )


# --------------------------------------------------
# CLOSE SESSION
# --------------------------------------------------

WinBioCloseSession(session)


print()
input("Press Enter to exit...")