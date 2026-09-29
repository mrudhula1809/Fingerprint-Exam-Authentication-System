import ctypes
from ctypes import wintypes

winbio = ctypes.WinDLL("winbio.dll")

WINBIO_TYPE_FINGERPRINT = 0x00000008
WINBIO_POOL_SYSTEM = 1
WINBIO_FLAG_DEFAULT = 0

session = ctypes.c_void_p()

result = winbio.WinBioOpenSession(
    WINBIO_TYPE_FINGERPRINT,
    WINBIO_POOL_SYSTEM,
    WINBIO_FLAG_DEFAULT,
    None,
    0,
    None,
    ctypes.byref(session)
)

if result != 0:
    print("Could not open biometric session.")
    print("Error:", hex(result))
    exit()

print("Biometric session opened successfully.")

# Prepare sensor location
unit_id = wintypes.ULONG()

print("Checking for fingerprint sensor...")

result = winbio.WinBioLocateSensor(
    session,
    ctypes.byref(unit_id)
)

if result == 0:
    print("Fingerprint sensor found! ✅")
    print("Sensor Unit ID:", unit_id.value)
else:
    print("Could not locate fingerprint sensor.")
    print("Error:", hex(result))

winbio.WinBioCloseSession(session)

print("Test finished.")