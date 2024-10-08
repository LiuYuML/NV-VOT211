import cv2
import numpy as np
import os

# need a txt path
# need a specifc name default to be 

def is_deformation_check(current, template, threshold):
    """
    Determine if deformation has occurred by calculating the correlation between the
    current frame and a template image.

    Args:
    - current: The current frame image (as a NumPy array).
    - template: The template image (as a NumPy array) to compare with.
    - threshold: The threshold for the correlation score. If the score is below
      this threshold, deformation is considered to have occurred.

    Returns:
    - True if deformation is detected, False otherwise.
    """
    #print(template.shape,current.shape[1], current.shape[0])
    template = cv2.resize(template, (current.shape[1], current.shape[0]))
    result = cv2.matchTemplate(current, template, cv2.TM_CCOEFF_NORMED)
    #print(result.shape)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    #print(threshold)
    return max_val < threshold,max_val*0.2

def get_axis_aligned_bbox(region):
    """ convert region to (cx, cy, w, h) that represent by axis aligned box
    """
    region = np.array(region)
    nv = region.size
    if nv == 8:
        cx = np.mean(region[0::2])
        cy = np.mean(region[1::2])
        x1 = min(region[0::2])
        x2 = max(region[0::2])
        y1 = min(region[1::2])
        y2 = max(region[1::2])
        A1 = np.linalg.norm(region[0:2] - region[2:4]) * \
            np.linalg.norm(region[2:4] - region[4:6])
        A2 = (x2 - x1) * (y2 - y1)
        s = np.sqrt(A1 / A2)
        w = s * (x2 - x1) + 1
        h = s * (y2 - y1) + 1
        x = cx-w/2
        y = cy-h/2
    else:
        x = region[0]
        y = region[1]
        w = region[2]
        h = region[3]
        cx = x+w/2
        cy = y+h/2
    return x, y, w, h


def process_ground_truth(ground_truth_file,isVOT=False):
    if not isVOT:
        #print(ground_truth_file)
        gt_ = []
        with open(ground_truth_file, 'r') as file:
            for line in file:
                # Parse the ground truth information for each frame
                values = line.strip().split()
                if len(values) ==1:
                    #print("hi")
                    values = line.strip().split(",")
                if "NaN" in values:
                    gt_.append(["NaN","NaN","NaN","NaN"])
                    continue
                #print(ground_truth_file,values,len(gt_))
                values = map(float, values)
                x, y, w, h = map(int, values)
                gt_.append((x, y, w, h))
        return gt_
    else:
        gt_ = []
        with open(ground_truth_file, 'r') as file:
            for line in file:
                # Parse the ground truth information for each frame
                values = line.strip().split()
                #print(values)
                if len(values) ==1:
                    #print("hi")
                    values = line.strip().split(",")
                    #print(values)
                #print(ground_truth_file,values)
                values = [float(i) for i in values]
                #print(values)
                values = get_axis_aligned_bbox(values)
                x, y, w, h = map(int, values)
                gt_.append((x, y, w, h))
        return gt_
    
def main(image_folder, base_output_path, dataset_name, gt_path,gt_name,index,threshold=2.0):
    isVOT = False
    for root, _, files in os.walk(image_folder):
        image_files = sorted([os.path.join(root, f) for f in files if f.endswith('.jpg')])
        if len(image_files) !=0:
            root_elements = image_files[0].split(os.path.sep)
            #print(root_elements)
            output_file_path = os.path.join(base_output_path, dataset_name, f'{root_elements[index]}.txt')
            if dataset_name == "otb":
                final_gt_path = os.path.join(gt_path,str(root_elements[index]),gt_name)
            if dataset_name == 'avist':
                final_gt_path = os.path.join(gt_path,str(root_elements[index])+".txt")
            if dataset_name == 'got10k_test':
                final_gt_path = os.path.join(gt_path,str(root_elements[index]),str(root_elements[index])+gt_name)
                #print("gt_path:",final_gt_path)
            if dataset_name == "XJU211":
                final_gt_path = os.path.join(gt_path,str(root_elements[index])+".txt")
            if dataset_name == "VOT":
                final_gt_path = os.path.join(gt_path,str(root_elements[index]),gt_name)
                isVOT = True
                #print(final_gt_path)
            if dataset_name == "UAVDark135":
                final_gt_path = os.path.join(gt_path,str(root_elements[index])+".txt")
                isVOT = False
            if dataset_name == "NAT2021":
                final_gt_path = os.path.join(gt_path,str(root_elements[index])+".txt")
                isVOT = False
            if dataset_name == "DarkTrack2021":
                final_gt_path = os.path.join(gt_path,str(root_elements[index])+".txt")
                isVOT = False
            gt = process_ground_truth(final_gt_path,isVOT)
            os.makedirs(os.path.join(base_output_path, dataset_name), exist_ok=True)    
            if os.path.exists(output_file_path):
                print(output_file_path," Already Done!")
                continue
            x,y,w,h = gt[0]
            image1 = cv2.imread(os.path.join(image_folder, image_files[0]))[y:y+h,x:x+w]
            with open(output_file_path, 'w') as output_file:
                threshold = 0
                for idx, image_path in enumerate(image_files):
                    #print(len(gt),len(image_files))
                    if (idx+1)<len(gt):
                        #threshold = 0
                        if idx == 0:
                            #x,y,w,h = gt[0]
                            image2 = image1
                            _,threshold = is_deformation_check(image2, image1, threshold)
                            output_file.write('0,')
                        elif idx == len(image_files) - 1:
                            img_h,img_w,_ = cv2.imread(os.path.join(image_folder, image_files[idx])).shape
                            x,y,w,h = gt[idx]
                            if x=="NaN":
                                output_file.write('0,')
                                continue
                            x = max(x,0)
                            y = max(y,0)
                            tmp_h = min(y+h,img_h)
                            h = tmp_h-y
                            tmp_w = min(x+w,img_w)
                            w = tmp_w-x
                            if h!=0 and w!=0:
                                image2 = cv2.imread(os.path.join(image_folder, image_files[idx]))[y:y+h,x:x+w]
                                is_deformation,_ = is_deformation_check(image2, image1, threshold)
                                output_file.write('1\n' if is_deformation else '0\n')
                            else:
                                output_file.write('0\n')
                        else:
                            # Compare with the previous frame
                            img_h,img_w,_ = cv2.imread(os.path.join(image_folder, image_files[idx])).shape
                            x,y,w,h = gt[idx]
                            if x=="NaN":
                                output_file.write('0,')
                                continue
                            x = max(x,0)
                            y = max(y,0)
                            tmp_h = min(y+h,img_h)
                            h = tmp_h-y
                            tmp_w = min(x+w,img_w)
                            w = tmp_w-x
                            if h!=0 and w!=0:
                                image2 = cv2.imread(os.path.join(image_folder, image_files[idx]))[y:y+h,x:x+w]
                                is_deformation,_ = is_deformation_check(image2, image1, threshold)
                                output_file.write('1,' if is_deformation else '0,')
                            else:
                                output_file.write('0,')

                        # Write "1\n" or "0\n" for the last frame in each directory
                    elif (idx+1)==len(gt):
                        output_file.write('0\n')
            print(output_file_path," Already Done!")
# Example usage:
if __name__ == "__main__":
    #image_folder = r'C:\Users\leoyu\Desktop\OTBSpace\SOTDrawRect\OTB100'
    #base_output_path = r'C:\Users\leoyu\Desktop\LeoSOTSpace\NTB\utils\deformation'
    #dataset_name = 'otb'
    #index = -3  # You can specify the desired index here
    #gt_path = r"C:\Users\leoyu\Desktop\OTBSpace\SOTDrawRect\OTB100"
    #gt_name = r"groundtruth_rect.txt"
    #main(image_folder, base_output_path, dataset_name,gt_path,gt_name,index)

    #image_folder = r'C:\Users\leoyu\Desktop\LeoSOTSpace\avist\avist\sequences'
    #base_output_path = r'C:\Users\leoyu\Desktop\LeoSOTSpace\NTB\utils\deformation'
    #dataset_name = 'avist'
    #index = -2  # You can specify the desired index here
    #gt_path = r"C:\Users\leoyu\Desktop\LeoSOTSpace\avist\avist\anno"
    #gt_name = r"groundtruth_rect.txt"
    #main(image_folder, base_output_path, dataset_name,gt_path,gt_name,index)
    
    #image_folder = r'C:\Users\leoyu\Desktop\LeoSOTSpace\GOT-10k\GOT-10k\test'
    #base_output_path = r'C:\Users\leoyu\Desktop\LeoSOTSpace\NTB\utils\deformation'
    #dataset_name = 'got10k_test'
    #index = -2  # You can specify the desired index here
    #gt_path = r"C:\Users\leoyu\Desktop\LeoSOTSpace\GOT-10k\best_got_results\garbage_submission_2023_05_21_13_11_04"
    #gt_name = r"_001.txt"
    #main(image_folder, base_output_path, dataset_name,gt_path,gt_name,index)
    
    #image_folder = r'C:\Users\leoyu\Desktop\LeoSOTSpace\NTB\test\sequences'
    #base_output_path = r'C:\Users\leoyu\Desktop\LeoSOTSpace\NTB\utils\deformation'
    #dataset_name = 'XJU211'
    #index = -2  # You can specify the desired index here
    #gt_path = r"C:\Users\leoyu\Desktop\LeoSOTSpace\NTB\test\anno"
    #gt_name = r"groundtruth_rect.txt"
    #main(image_folder, base_output_path, dataset_name,gt_path,gt_name,index)
    
    
    
    #image_folder = r'D:\Documents\Desktop\ly\MBZUAI\Dataset CVPR\VOT2018'
    #base_output_path = r'D:\Documents\Desktop\ly\MBZUAI\Dataset CVPR\deformation'
    #dataset_name = 'VOT'
    #index = -2  # You can specify the desired index here
    #gt_path = r"D:\Documents\Desktop\ly\MBZUAI\Dataset CVPR\VOT2018"
    #gt_name = r"groundtruth.txt"
    #main(image_folder, base_output_path, dataset_name,gt_path, gt_name,index)
    
    
    #image_folder = r'D:\Documents\Desktop\ly\MBZUAI\Dataset CVPR\VOT2018'
    #base_output_path = r'D:\Documents\Desktop\ly\MBZUAI\Dataset CVPR\camera_motion'
    #dataset_name = 'VOT'
    #index = -2  # You can specify the desired index here
    #gt_path = r"D:\Documents\Desktop\ly\MBZUAI\Dataset CVPR\VOT2018"
    #gt_name = r"groundtruth.txt"
    #main(image_folder, base_output_path, dataset_name, index)
    
    
    #image_folder = r'E:\ly\ACCV\dataset\Other night benchmark\UAVDark135\UAVDark135_TSP_out\Sequences'
    #base_output_path = r'D:\Documents\Desktop\ly\MBZUAI\Dataset CVPR\codes\tmp\deformation'
    #dataset_name = 'UAVDark135'
    #index = -2  # You can specify the desired index here
    #gt_path = r"E:\ly\ACCV\dataset\Other night benchmark\UAVDark135\UAVDark135_TSP_out\anno_revise"
    #gt_name = r"groundtruth.txt"
    #main(image_folder, base_output_path, dataset_name,gt_path, gt_name,index)
    
    
    #image_folder = r'E:\ly\ACCV\dataset\Other night benchmark\NAT2021\NAT2021_test\NAT2021L\data_seq'
    #base_output_path = r'D:\Documents\Desktop\ly\MBZUAI\Dataset CVPR\codes\tmp\deformation'
    #dataset_name = 'NAT2021'
    #index = -2  # You can specify the desired index here
    #gt_path = r"E:\ly\ACCV\dataset\Other night benchmark\NAT2021\NAT2021_test\NAT2021L\anno"
    #gt_name = r"groundtruth.txt"
    #main(image_folder, base_output_path, dataset_name,gt_path, gt_name,index)
    
    image_folder = r'E:\ly\ACCV\dataset\Other night benchmark\DarkTrack\DarkTrack2021\data_seq'
    base_output_path = r'D:\Documents\Desktop\ly\MBZUAI\Dataset CVPR\codes\tmp\deformation'
    dataset_name = 'DarkTrack2021'
    index = -2  # You can specify the desired index here
    gt_path = r"E:\ly\ACCV\dataset\Other night benchmark\DarkTrack\DarkTrack2021\anno"
    gt_name = r"groundtruth.txt"
    main(image_folder, base_output_path, dataset_name,gt_path, gt_name,index)