import cv2
import subprocess
import tempfile
import os
import time
import json
import csv

# ------------------ USER CONFIG ------------------
VIDEO_PATH = r"C:\Users\Sejal\Downloads\3148319-hd_1920_1080_30fps.mp4"
ALPR_PATH = r"C:\Users\Sejal\Downloads\openalpr-2.3.0-win-64bit\openalpr_64\alpr.exe"
PROCESS_EVERY_N_FRAMES = 15      # sample every N frames
CONFIDENCE_THRESHOLD = 20.0      # lowered for testing
SHOW_WINDOW = True               # show video feed
# --------------------------------------------------

# Repo root
repo_dir = os.path.dirname(os.path.abspath(__file__))

# Authorized plates file inside repo
AUTHORIZED_CSV = os.path.join(repo_dir, "authorized_plates.csv")
if not os.path.exists(AUTHORIZED_CSV):
    # Create sample authorized plates if missing
    with open(AUTHORIZED_CSV, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["BJJ 8840"])
        writer.writerow(["DL3CAF9999"])
        writer.writerow(["MH12AB1234"])
    print(f"Sample {AUTHORIZED_CSV} created. Edit with your plates if needed.")

# Plates folder inside repo
PLATES_FOLDER = os.path.join(repo_dir, "plates_captured")
os.makedirs(PLATES_FOLDER, exist_ok=True)

# Log CSV inside repo
OUTPUT_LOG = os.path.join(repo_dir, "alpr_video_log.csv")
if not os.path.exists(OUTPUT_LOG):
    with open(OUTPUT_LOG, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp","frame_no","time_sec","plate","confidence","allowed"])

# Load authorized plates
authorized = set()
with open(AUTHORIZED_CSV, newline='', encoding='utf-8') as f:
    for row in csv.reader(f):
        if row: authorized.add(row[0].strip().upper())

# Video capture
cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS) or 25
frame_no = 0

# ALPR function (default country)
def run_alpr(image_path):
    try:
        result = subprocess.run([ALPR_PATH, "-j", image_path],
                                capture_output=True, text=True, timeout=10)
        if result.stdout:
            return json.loads(result.stdout)
    except Exception as e:
        print("ALPR Error:", e)
    return None

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    if frame_no % PROCESS_EVERY_N_FRAMES == 0:
        # Temp image
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmpname = tmp.name
            cv2.imwrite(tmpname, frame)

        results = run_alpr(tmpname)
        os.remove(tmpname)

        if results and "results" in results:
            for r in results["results"]:
                plate = r.get("plate","").upper()
                conf = float(r.get("confidence",0))
                allowed = plate in authorized and conf >= CONFIDENCE_THRESHOLD

                if conf >= CONFIDENCE_THRESHOLD and plate:
                    coords = r.get("coordinates")
                    if coords:
                        xs = [c["x"] for c in coords]
                        ys = [c["y"] for c in coords]
                        x1, y1 = min(xs), min(ys)
                        x2, y2 = max(xs), max(ys)

                        # Save cropped plate
                        plate_filename = os.path.join(PLATES_FOLDER, f"{plate}_{frame_no}.jpg")
                        cv2.imwrite(plate_filename, frame[y1:y2, x1:x2])

                        # Print result
                        print(f"{plate} - {'ACCESS GRANTED' if allowed else 'ACCESS DENIED'}")

                        # Log
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        t_sec = frame_no / fps
                        with open(OUTPUT_LOG, "a", newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow([timestamp, frame_no, round(t_sec,2), plate, conf, allowed])

                        # Draw rectangle on video
                        if SHOW_WINDOW:
                            cv2.rectangle(frame, (x1, y1), (x2, y2),
                                          (0,255,0) if allowed else (0,0,255), 2)
                            cv2.putText(frame, f"{plate} {'GRANTED' if allowed else 'DENIED'}",
                                        (x1, max(20, y1-10)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),2)

    # Show video
    if SHOW_WINDOW:
        cv2.imshow("Video Access Monitor", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    frame_no += 1

cap.release()
cv2.destroyAllWindows()
print(f"Video processing done. Check '{PLATES_FOLDER}' for plate images and '{OUTPUT_LOG}' for logs.")
