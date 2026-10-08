"""
enum_cameras.py — Enumerate DirectShow video capture devices using Windows COM
This shows the EXACT order OpenCV uses to assign camera indices.
"""
import ctypes
import ctypes.wintypes
import comtypes
import comtypes.client

# Load required COM libraries
comtypes.client.GetModule("C:\\Windows\\System32\\quartz.dll")

CLSID_SystemDeviceEnum = comtypes.GUID("{62BE5D10-60EB-11d0-BD3B-00A0C911CE86}")
CLSID_VideoInputDeviceCategory = comtypes.GUID("{860BB310-5D01-11d0-BD3B-00A0C911CE86}")

IID_ICreateDevEnum = comtypes.GUID("{29840822-5B84-11D0-BD3B-00A0C911CE86}")
IID_IEnumMoniker   = comtypes.GUID("{00000102-0000-0000-C000-000000000046}")
IID_IMoniker       = comtypes.GUID("{0000000F-0000-0000-C000-000000000046}")
IID_IPropertyBag   = comtypes.GUID("{55272A00-42CB-11CE-8135-00AA004BB851}")

try:
    from comtypes.gen import quartz as q
    dev_enum = comtypes.client.CreateObject(CLSID_SystemDeviceEnum)
    print("COM device enumeration:")

    import ctypes.wintypes as wt

    # Use ICreateDevEnum via raw COM
    # Simpler: use Windows Script Host / WMI via subprocess
    raise NotImplementedError("Fallback to subprocess method")

except Exception as e:
    import subprocess, json

    print(f"COM method failed ({e}), using PowerShell WMI...")
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-PnpDevice | Where-Object {$_.Class -in 'Camera','Image'} | Select-Object FriendlyName,Status,InstanceId | ConvertTo-Json"],
        capture_output=True, text=True, timeout=10
    )
    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr)
