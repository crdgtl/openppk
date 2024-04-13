import os
import logging
from file_operations import find_mrk_file
from data_processing import read_mrk_file, process_mrk_file, write_output_mrk_file
from geo_processing import process_geo_txt

def main():
    """
    Main function that coordinates the execution of the script.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Get the current working directory
    current_directory = os.getcwd()

    try:
        # Find the .MRK file in the current directory
        mrk_file = find_mrk_file(current_directory)
        logging.info(f"Found .MRK file: {mrk_file}")

        # Find the .pos file in the current directory
        pos_files = [file for file in os.listdir(current_directory) if file.endswith(".pos")]
        if not pos_files:
            raise FileNotFoundError("No .pos file found in the current directory.")
        if len(pos_files) > 1:
            logging.warning("Multiple .pos files found in the current directory. Using the first one.")
        pos_file = os.path.join(current_directory, pos_files[0])
        logging.info(f"Using .pos file: {pos_file}")

        # Read the .pos file
        with open(pos_file, "r") as file:
            pos_data = [line.strip().split() for line in file if not line.startswith("%")]

        # Define the UTC formats for .MRK and .pos files
        mrk_utc_format = "%Y-%m-%d %H:%M:%S.%f"
        pos_utc_format = "%Y/%m/%d %H:%M:%S.%f"

        # Read and process the .MRK file
        mrk_data = read_mrk_file(mrk_file)
        output_data = process_mrk_file(mrk_data, pos_data, mrk_utc_format, pos_utc_format)

        if output_data:
            # Write the output .MRK file
            write_output_mrk_file(output_data, mrk_file)
            logging.info(f"Processed {mrk_file} and created POS-{os.path.basename(mrk_file)} in the current directory.")

            # Prompt the user for the proj.4 string
            proj4_string = input("Please enter the proj.4 string for your coordinate system: ")

            # Process the geo.txt file
            process_geo_txt("\n".join(output_data), current_directory, proj4_string)

    except (FileNotFoundError, IOError, ValueError) as e:
        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
