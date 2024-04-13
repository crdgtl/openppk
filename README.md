# openppk

openppk is an open-source Python script that interpolates position data from a .MRK file using a corresponding .pos file. It is designed to assist in post-processing kinematic (PPK) data for applications such as surveying, mapping, and geospatial analysis.

The benefit of this tool is being able to PPK process images, in state plane coordinate zones, from command line, with orientation data captured. Being available as a command line tool gives a lot of opportunity for creating web apps or simple to use versions, and automation.

**BETA:** We are currently testing locally on Windows. There are hard paths for things like exiftool that need to be fixed to run universally.

**NEW FEATURE:** The script now exports a geo.txt in the directory where run with relevant latitude, longitude, and height values to a geo.txt file for ODM or WebODM processing.

We're currently only testing with a DJI Mavic 3E RTK, but this should work with other DJI Enterprise drones or Autel drones that export a .MRK file. 

## Installation

1. Install Python 3.x on your computer if you haven't already. You can download it from the official Python website: https://www.python.org/downloads/

2. Open a terminal or command prompt and install the required Python dependencies by running the following command:
```
pip install tqdm
```

## Usage

1. Copy the entire mission folder from your DJI drone to your computer. This folder should contain the .MRK file and the captured images.

2. Process your raw GNSS data from the drone mission using RTKPOST or RNX2RTKP with a local RINEX base station to obtain a high-precision kinematic correction. Save the output as a .pos file.

3. Place the openppk.py script in the same directory as your .pos file, along with the copied mission folder containing the .MRK file and images.

4. Open a terminal or command prompt, navigate to the directory containing the openppk.py script, and run the following command:
```
python openppk.py
```

5. The script will prompt you to enter the proj.4 string for your coordinate system. Provide the appropriate string and press Enter.

6. The script will process the .MRK file, interpolate the position data using the .pos file, and generate the following output files:
- `POS-<original_mrk_file_name>.MRK`: Contains the UTC time values and interpolated position data. Written to the subdirectory with images.
- `geo.txt`: Contains the image names, longitude, latitude, height, yaw, pitch, and roll values for each image, formatted for ODM or WebODM processing. Written to the directory where run.

7. You can now use the generated `geo.txt` file along with your images in OpenDroneMap or WebODM for further processing and analysis.

## Notes

- The tool is currently in beta, and we have only tested the output images on a limited dataset. We welcome feedback, reviews, and contributions from the community to improve the tool.

- If you encounter any issues or have suggestions for improvements, please open an issue on the project's GitHub repository.

## License

openppk is released under the MIT License

Copyright (c) 2024 Core Digital

For commercial services, please contact Core Digital at:
info at our domain, find us! 

For more details, please refer to the [LICENSE](LICENSE) file.
