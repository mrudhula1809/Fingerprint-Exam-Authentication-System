import ctypes
from ctypes import wintypes

winbio = ctypes.WinDLL("winbio.dll")

# Constants
WINBIO_TYPE_FINGERPRINT = 0x00000008
WINBIO_POOL_SYSTEM = 1

session_handle = ctypes.c_void_p()

# Open biometric session
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

if result != 0:
    print("Could not open biometric session.")
    print("Error code:", result)
    exit()

print("Biometric session opened.")
print("Now place your enrolled finger on the fingerprint sensor...")

# Close session for this first test
winbio.WinBioCloseSession(session_handle)

print("Biometric session test completed.")