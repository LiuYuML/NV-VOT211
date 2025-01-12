import cv2
import numpy as np
import os

def is_camera_moving(image1, image2, threshold=2.0):
    # Convert images to grayscale
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Calculate optical flow between the two frames
    flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    # Calculate the magnitude of the optical flow vectors
    magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)

    # Calculate the mean magnitude
    mean_magnitude = np.mean(magnitude)

    # Determine camera motion based on the mean magnitude
    return mean_magnitude > threshold

def main(image_folder, base_output_path, dataset_name, index, threshold=2.0):
    for root, _, files in os.walk(image_folder):
        image_files = sorted([os.path.join(root, f) for f in files if f.endswith('.jpg')])
        if len(image_files) !=0:
            root_elements = image_files[0].split(os.path.sep)
            output_file_path = os.path.join(base_output_path, dataset_name, f'{root_elements[index]}.txt')
            os.makedirs(os.path.join(base_output_path, dataset_name), exist_ok=True)    
            if os.path.exists(output_file_path):
                print(output_file_path," Already Done!")
                continue
            with open(output_file_path, 'w') as output_file:
                for idx, image_path in enumerate(image_files):
                    image1 = cv2.imread(os.path.join(image_folder, image_path))
                    
                    if idx == 0:
                        # Write "0," for the first frame in each directory
                        output_file.write('0,')
                    elif idx == len(image_files) - 1:
                        image2 = cv2.imread(os.path.join(image_folder, image_files[idx-1]))
                        is_moving = is_camera_moving(image2, image1, threshold)
                        output_file.write('1\n' if is_moving else '0\n')
                    else:
                        # Compare with the previous frame
                        image2 = cv2.imread(os.path.join(image_folder, image_files[idx-1]))
                        is_moving = is_camera_moving(image2, image1, threshold)
                        output_file.write('1,' if is_moving else '0,')

                    # Write "1\n" or "0\n" for the last frame in each directory
            print(output_file_path," Already Done!")
# Example usage:
if __name__ == "__main__":
    #image_folder = r'<path-to-dataset>\OTB100'
    #base_output_path = r'<output_path>\camera_motion'
    #dataset_name = 'otb'
    #index = -3  
    #main(image_folder, base_output_path, dataset_name, index)

    
    
