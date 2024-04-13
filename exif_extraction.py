import subprocess
import re

def extract_exif_data(file_path):
    """
    Extract EXIF data from an image file using ExifTool.

    Args:
        file_path (str): Path to the image file.

    Returns:
        dict: Extracted EXIF data as a dictionary, or None if extraction fails.
    """
    try:
        # Construct the ExifTool command
        exiftool_path = r"C:\Program Files\exiftool.exe"  # Replace with the actual path to exiftool.exe
        exiftool_cmd = [
            exiftool_path,
            '-s',
            '-s',
            '-GimbalRollDegree',
            '-GimbalPitchDegree',
            '-GimbalYawDegree',
            '-FileName',
            file_path
        ]

        # Run the ExifTool command and capture the output
        output = subprocess.check_output(exiftool_cmd, universal_newlines=True)

        # Parse the output to extract the desired values
        gimbal_roll = re.search(r'GimbalRollDegree:\s*([-+]?\d+\.\d+)', output)
        gimbal_pitch = re.search(r'GimbalPitchDegree:\s*([-+]?\d+\.\d+)', output)
        gimbal_yaw = re.search(r'GimbalYawDegree:\s*([-+]?\d+\.\d+)', output)
        image_name = re.search(r'FileName:\s*(.+)', output)

        if gimbal_roll and gimbal_pitch and gimbal_yaw and image_name:
            gimbal_roll = float(gimbal_roll.group(1))
            gimbal_pitch = float(gimbal_pitch.group(1))
            gimbal_yaw = float(gimbal_yaw.group(1))
            image_name = image_name.group(1)

            return {
                'Gimbal Roll': gimbal_roll,
                'Gimbal Pitch': gimbal_pitch,
                'Gimbal Yaw': gimbal_yaw,
                'Image Name': image_name
            }
        else:
            print("Gimbal Roll, Pitch, and Yaw degrees or Image Name not found in the ExifTool output.")

    except subprocess.CalledProcessError as e:
        print(f"Error running ExifTool: {e}")
    except Exception as e:
        print(f"Error processing file '{file_path}': {e}")

    return None
