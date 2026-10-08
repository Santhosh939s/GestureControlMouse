"""
find_real_cam.py — Opens cameras by device name to find the HP TrueVision HD Camera
"""
import cv2, time, os

out_dir = r's:\gravity projects\mouse control'
print("Trying to find HP TrueVision HD Camera...", flush=True)

# Try indices 0-5 with both backends and save each frame
# The Sharing Camera is a virtual device; HP TrueVision should appear at a different index
# Windows sometimes enumerates virtual devices before physical ones

for i in range(6):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        time.sleep(0.8)   # let camera initialise
        ret, frame = cap.read()
        if ret:
            # Check if it looks like a real camera (not a static instruction image)
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur  = cv2.Laplacian(gray, cv2.CV_64F).var()  # sharpness / motion measure
            mean  = gray.mean()
            path  = os.path.join(out_dir, f"frame_idx{i}.jpg")
            cv2.imwrite(path, frame)
            print(f"  idx={i}  brightness={mean:.1f}  sharpness_var={blur:.1f}  -> {path}", flush=True)
        else:
            print(f"  idx={i}  opened but NO frame read", flush=True)
        cap.release()
    else:
        print(f"  idx={i}  not found", flush=True)

print("\nNow trying with CAP_MSMF backend...", flush=True)
for i in range(6):
    cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
    if cap.isOpened():
        time.sleep(0.8)
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            path = os.path.join(out_dir, f"frame_msmf_idx{i}.jpg")
            cv2.imwrite(path, frame)
            print(f"  MSMF idx={i}  brightness={gray.mean():.1f}  -> {path}", flush=True)
        else:
            print(f"  MSMF idx={i}  opened but NO frame", flush=True)
        cap.release()
    else:
        print(f"  MSMF idx={i}  not found", flush=True)
