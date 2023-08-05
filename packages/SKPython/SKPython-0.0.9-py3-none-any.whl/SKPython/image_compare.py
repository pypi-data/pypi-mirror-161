import cv2
from skimage.metrics import structural_similarity as ssim
import os
import shutil

root_dir = "/Users/1004418/temp/image_compare/2022-07-02"
list_dir = os.listdir(root_dir)
list_dir.sort()

list_dir.remove("UNKNOWN")
list_dir.remove(".DS_Store")

dir_num = 0
for i in range(len(list_dir)):
    if i == len(list_dir) - 1:
        break

    compare_file_path1 = f"{root_dir}/{list_dir[i]}/camera1"
    files1 = os.listdir(compare_file_path1)
    files1.sort()

    for j in range(len(list_dir) - (i + 1)):
        compare_file_path2 = f"{root_dir}/{list_dir[i+j+1]}/camera1"
        files2 = os.listdir(compare_file_path2)
        files2.sort()

        if len(files1) != len(files2):
            print(f"not equals size: {len(files1)}, {len(files2)}")
            continue

        for k in range(len(files1)):
            compare_file1 = f"{compare_file_path1}/{files1[k]}"
            compare_file2 = f"{compare_file_path2}/{files2[k]}"

            imageA = cv2.imread(compare_file1)  # 원본
            imageB = cv2.imread(compare_file2)  # 비교
            grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
            grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

            (score, diff) = ssim(grayA, grayB, full=True)
            if score < 0.65:
                print(
                    f"compare_files: {compare_file1.replace(root_dir, '')}, {compare_file2.replace(root_dir, '')}, {score:.5f}"
                )

                save_file_path = (
                    f"/Users/1004418/temp/image_compare/{dir_num}_{int(score*100)}%"
                )
                os.makedirs(save_file_path)

                shutil.copyfile(compare_file1, f"{save_file_path}/1.jpeg")
                shutil.copyfile(compare_file2, f"{save_file_path}/2.jpeg")
                dir_num += 1
