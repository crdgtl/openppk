import os
from tqdm import tqdm
from exif_extraction import extract_exif_data
from multiprocessing import Pool

def process_geo_txt(script_output, image_dir, proj4_string):
    """
    Process the script output and generate the geo.txt file.

    Args:
        script_output (str): Output data from the script.
        image_dir (str): Directory containing the image files.
        proj4_string (str): Proj.4 string for the coordinate system.
    """
    # Find the subdirectory containing .JPG images
    image_subdir = find_image_subdir(image_dir)
    if image_subdir is None:
        print("Error: No subdirectory containing .JPG images found.")
        return

    # Read the script output and extract the interpolated positions
    positions = extract_positions(script_output)

    # Check if the number of positions matches the number of .JPG images
    image_files = [f for f in os.listdir(image_subdir) if f.endswith(".JPG")]
    if len(positions) != len(image_files):
        print(f"Error: Number of positions ({len(positions)}) does not match the number of .JPG images ({len(image_files)}).")
        return

    # Create a pool of worker processes
    pool = Pool()

    # Process each image in parallel using multiprocessing
    results = []
    for i, image_file in enumerate(sorted(image_files)):
        image_path = os.path.join(image_subdir, image_file)
        result = pool.apply_async(extract_exif_data, (image_path,))
        results.append((i, result))

    # Open the geo.txt file for writing
    with open("geo.txt", "w") as geo_file:
        # Write the proj.4 string in the first row
        geo_file.write(f"{proj4_string}\n")

        # Retrieve the results and write the corresponding rows to geo.txt
        for i, result in tqdm(results, desc="Processing images"):
            exif_data = result.get()

            if exif_data:
                image_name = exif_data.get('Image Name', '')
                yaw = str(exif_data.get('Gimbal Yaw', ''))
                pitch = str(exif_data.get('Gimbal Pitch', ''))
                roll = str(exif_data.get('Gimbal Roll', ''))
            else:
                image_name = image_files[i]
                yaw = ''
                pitch = ''
                roll = ''

            _, lat, lon, height = positions[i]  # Corrected order of values
            row = f"{image_name} {lon} {lat} {height} {yaw} {pitch} {roll}\n"
            geo_file.write(row)

    # Close the pool of worker processes
    pool.close()
    pool.join()

    print("geo.txt file created successfully.")

def find_image_subdir(image_dir):
    """
    Find the subdirectory containing .JPG images.

    Args:
        image_dir (str): Directory to search for the image subdirectory.

    Returns:
        str: Path to the subdirectory containing .JPG images, or None if not found.
    """
    for root, dirs, files in os.walk(image_dir):
        for d in dirs:
            if any(file.endswith(".JPG") for file in os.listdir(os.path.join(root, d))):
                return os.path.join(root, d)
    return None

def extract_positions(script_output):
    """
    Extract the interpolated positions from the script output.

    Args:
        script_output (str): Output data from the script.

    Returns:
        list: List of interpolated positions, where each position is a tuple of (utc_time, lat, lon, height).
    """
    positions = []
    for line in script_output.split("\n"):
        fields = line.strip().split("\t")
        if len(fields) >= 7:
            positions.append((fields[3], fields[4], fields[5], fields[6]))
    return positions
