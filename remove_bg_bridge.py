import cv2
import numpy as np
import sys

# Command line args: input_path output_path
input_path, output_path = sys.argv[1], sys.argv[2]

# Load image (with alpha if it exists)
img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)

# If image has no alpha, convert to BGRA
if img.shape[2] == 3:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

# --- Step 1: Remove uniform background using grabCut ---
bgr = img[:, :, :3].copy()
mask = np.zeros(bgr.shape[:2], np.uint8)
bgdModel = np.zeros((1, 65), np.float64)
fgdModel = np.zeros((1, 65), np.float64)

rect = (1, 1, bgr.shape[1] - 2, bgr.shape[0] - 2)
cv2.grabCut(bgr, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
img[:, :, 3] = img[:, :, 3] * mask2

# --- Step 2: Decide if background is closer to white or black ---
# Sample 10px border pixels
border = np.concatenate([
    bgr[0:10, :, :].reshape(-1, 3),
    bgr[-10:, :, :].reshape(-1, 3),
    bgr[:, 0:10, :].reshape(-1, 3),
    bgr[:, -10:, :].reshape(-1, 3)
], axis=0)

mean_color = border.mean(axis=0)
brightness = mean_color.mean()

# --- Step 3: Clean up depending on detected background ---
if brightness > 127:  
    # Likely white background → remove near-white
    white_min = np.array([200, 200, 200, 0], dtype=np.uint8)
    white_max = np.array([255, 255, 255, 255], dtype=np.uint8)
    white_mask = cv2.inRange(img, white_min, white_max)
    img[white_mask > 0, 3] = 0
else:
    # Likely black background → remove near-black
    black_min = np.array([0, 0, 0, 0], dtype=np.uint8)
    black_max = np.array([50, 50, 50, 255], dtype=np.uint8)
    black_mask = cv2.inRange(img, black_min, black_max)
    img[black_mask > 0, 3] = 0

# Save final result
cv2.imwrite(output_path, img)
