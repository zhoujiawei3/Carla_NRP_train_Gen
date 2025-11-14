
import os
import cv2
import numpy as np
import argparse


def train_to_label(folder_path, output_folder_path):
    os.makedirs(output_folder_path, exist_ok=True)
    count = 0
    for filename in sorted(os.listdir(folder_path)):
        if not (filename.lower().endswith('.png') or filename.lower().endswith('.jpg')):
            continue

        input_path = os.path.join(folder_path, filename)
        output_file = os.path.join(output_folder_path, os.path.splitext(filename)[0] + '.txt')

        # 如果已经存在标签文件则跳过
        if os.path.exists(output_file):
            count += 1
            continue

        mask = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            print(f"Warning: failed to read mask {input_path}, skipping")
            continue

        # 二值化（车身像素 > 0）
        _, binary = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            # 没有目标，写一个空文件或跳过（这里写空文件）
            open(output_file, 'w').close()
            count += 1
            continue

        # 合并所有 contour 点再取凸包来稳定 bbox
        try:
            all_points = np.vstack(contours)
        except Exception:
            # 若合并失败，使用第一个轮廓
            all_points = contours[0]

        hull = cv2.convexHull(all_points)
        x, y, w, h = cv2.boundingRect(hull)

        img_h, img_w = mask.shape[:2]

        # YOLO 格式: class x_center_norm y_center_norm width_norm height_norm
        x_center = x + w / 2.0
        y_center = y + h / 2.0

        x_center_n = x_center / img_w
        y_center_n = y_center / img_h
        w_n = w / img_w
        h_n = h / img_h

        # class id 2 as in original script
        with open(output_file, 'w') as f:
            f.write(f"2 {x_center_n:.6f} {y_center_n:.6f} {w_n:.6f} {h_n:.6f}\n")

        count += 1
        if count % 100 == 0:
            print(f"Processed {count} images")

    print(f"Done processing {count} images")


def main():
    parser = argparse.ArgumentParser(description='Generate label txt files from mask images')
    parser.add_argument('--input_dir', '-i', required=True, help='input folder containing mask images')
    parser.add_argument('--output_dir', '-o', required=True, help='output folder for label txt files')
    args = parser.parse_args()

    train_to_label(args.input_dir, args.output_dir)


if __name__ == '__main__':
    main()