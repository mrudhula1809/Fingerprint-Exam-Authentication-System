import ctypes
from ctypes import wintypes

# Load Windows Biometric Framework
winbio = ctypes.WinDLL("winbio.dll")

# Constants
WINBIO_TYPE_FINGERPRINT = 0x00000008

# ---------------------------------------------------------
# Define WINBIO_UNIT_SCHEMA
# ---------------------------------------------------------

class WINBIO_VERSION(ctypes.Structure):
    _fields_ = [
        ("MajorVersion", wintypes.ULONG),
        ("MinorVersion", wintypes.ULONG)
    ]


class WINBIO_UNIT_SCHEMA(ctypes.Structure):
    _fields_ = [
        ("UnitId", wintypes.ULONG),
        ("PoolType", wintypes.ULONG),
        ("BiometricFactor", wintypes.ULONG),
        ("SensorSubType", wintypes.ULONG),
        ("Capabilities", wintypes.ULONG),

        ("DeviceInstanceId", wintypes.LPWSTR),
        ("Description", wintypes.LPWSTR),
        ("Manufacturer", wintypes.LPWSTR),
        ("Model", wintypes.LPWSTR),
        ("SerialNumber", wintypes.LPWSTR),

        ("FirmwareVersion", WINBIO_VERSION)
    ]


# ---------------------------------------------------------
# Function definitions
# ---------------------------------------------------------

winbio.WinBioEnumBiometricUnits.argtypes = [
    wintypes.ULONG,
    ctypes.POINTER(
        ctypes.POINTER(WINBIO_UNIT_SCHEMA)
    ),
    ctypes.POINTER(wintypes.ULONG)
]

winbio.WinBioEnumBiometricUnits.restype = wintypes.LONG


winbio.WinBioFree.argtypes = [
    ctypes.c_void_p
]

winbio.WinBioFree.restype = wintypes.LONG


# ---------------------------------------------------------
# Start test
# ---------------------------------------------------------

print()
print("==============================================")
print("   WINDOWS FINGERPRINT SENSOR CHECK")
print("==============================================")
print()

print("Checking Windows Biometric Framework...")
print()

unit_array = ctypes.POINTER(WINBIO_UNIT_SCHEMA)()
unit_count = wintypes.ULONG()

result = winbio.WinBioEnumBiometricUnits(
    WINBIO_TYPE_FINGERPRINT,
    ctypes.byref(unit_array),
    ctypes.byref(unit_count)
)

print("Result:", hex(result & 0xFFFFFFFF))
print("Number of fingerprint sensors:", unit_count.value)
print()

if result != 0:
    print("❌ Windows could not enumerate the fingerprint sensor.")
    print("Error code:", hex(result & 0xFFFFFFFF))

elif unit_count.value == 0:
    print("❌ Windows Biometric Framework sees no fingerprint sensor.")

else:
    print("✅ Windows Biometric Framework sees the fingerprint sensor!")
    print()

    for i in range(unit_count.value):

        sensor = unit_array[i]

        print("----------------------------------------------")
        print("Sensor", i + 1)
        print("----------------------------------------------")
        print("Unit ID:", sensor.UnitId)
        print("Description:", sensor.Description)
        print("Manufacturer:", sensor.Manufacturer)
        print("Model:", sensor.Model)
        print("Serial Number:", sensor.SerialNumber)
        print()

    # Free memory allocated by Windows
    winbio.WinBioFree(unit_array)

print()
print("==============================================")
print("TEST FINISHED")
print("==============================================")