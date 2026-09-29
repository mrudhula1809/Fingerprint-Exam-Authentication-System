import ctypes
from ctypes import wintypes

# Load Windows Biometric Framework
winbio = ctypes.WinDLL("winbio.dll")

# Constants
WINBIO_TYPE_FINGERPRINT = 0x00000008
WINBIO_POOL_SYSTEM = 1

# Open the Windows biometric session
session_handle = ctypes.c_void_p()

result = winbio.WinBioOpenSession(
    WINBIO_TYPE_FINGERPRINT,
    WINBIO_POOL_SYSTEM,
    0,
    None,
    0,
    None,
    ctypes.byref(session_handle),
    0
)

if result == 0:
    print("SUCCESS: Windows Biometric Framework is available.")
    print("Your fingerprint sensor can potentially be accessed through Windows.")
else:
    print("FAILED.")
    print("WinBio error code:", result)