import os
from datetime import datetime, timedelta

import os

def find_mrk_file(directory):
    # Find the .MRK file in the subdirectories of the specified directory
    mrk_file = None
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".MRK"):
                mrk_file = os.path.join(root, file)
                break
        if mrk_file is not None:
            break
    if mrk_file is None:
        raise FileNotFoundError(f"No .MRK file found in {directory} or its subdirectories.")
    return mrk_file

def read_mrk_file(mrk_file):
    # Read the .MRK file
    with open(mrk_file, "r") as file:
        lines = file.readlines()

    # Parse the .MRK file and calculate UTC times
    data = []
    prev_utc_time = None
    for line in lines:
        fields = line.strip().split("\t")
        try:
            gps_week = int(fields[2].strip("[]"))
            gps_seconds = float(fields[1])

            # Calculate UTC time from GPS time
            gps_epoch = datetime(1980, 1, 6)
            elapsed_time = timedelta(weeks=gps_week, seconds=gps_seconds)
            utc_time = gps_epoch + elapsed_time

            # Validate that UTC times are different for each new row
            if prev_utc_time is not None and utc_time <= prev_utc_time:
                print(f"Warning: UTC times are not increasing for row {len(data) + 1}. Continuing with processing...")
            prev_utc_time = utc_time

            # Extract all data from the .MRK file
            row_data = fields[:3] + [utc_time] + fields[3:]
            data.append(row_data)
        except (ValueError, IndexError) as e:
            print(f"Error parsing line {len(data) + 1}: {str(e)}. Skipping line.")

    return data

def parse_utc_time(utc_time_str, utc_format):
    try:
        return datetime.strptime(utc_time_str, utc_format)
    except ValueError:
        # Try adding missing decimal places to the fractional part of seconds
        if '.' in utc_time_str:
            utc_time_parts = utc_time_str.split('.')
            fractional_part = utc_time_parts[1].ljust(6, '0')
            utc_time_str = '.'.join([utc_time_parts[0], fractional_part])
            return datetime.strptime(utc_time_str, utc_format)
        raise ValueError(f"Invalid UTC timestamp format: {utc_time_str}")

def find_closest_times(mrk_time_str, pos_data, mrk_utc_format, pos_utc_format):
    pos_times = []
    for data in pos_data:
        if len(data) > 1:
            try:
                pos_time = parse_utc_time(" ".join(data[:2]), pos_utc_format)
                pos_times.append((pos_time, data))
            except ValueError:
                continue
    try:
        mrk_datetime = parse_utc_time(mrk_time_str, mrk_utc_format)
        mrk_datetime = mrk_datetime.replace(microsecond=int(mrk_datetime.microsecond / 1000) * 1000)
    except ValueError as e:
        raise ValueError(f"Invalid UTC timestamp format in .MRK file: {mrk_time_str}")
    closest_times = sorted(pos_times, key=lambda x: abs(x[0] - mrk_datetime))[:2]
    if len(closest_times) < 2:
        raise ValueError(f"No matching UTC timestamps found in .pos file for {mrk_time_str}")
    return [time[1] for time in closest_times]

def interpolate_positions(mrk_time_str, closest_pos_data, mrk_utc_format, pos_utc_format):
    mrk_datetime = parse_utc_time(mrk_time_str, mrk_utc_format)
    pos_datetimes = [parse_utc_time(" ".join(data[:2]), pos_utc_format) for data in closest_pos_data]
    time_diff = (pos_datetimes[1] - pos_datetimes[0]).total_seconds()
    interpolation_factor = (mrk_datetime - pos_datetimes[0]).total_seconds() / time_diff
    lat1, lon1, height1 = map(float, closest_pos_data[0][2:5])
    lat2, lon2, height2 = map(float, closest_pos_data[1][2:5])
    interpolated_lat = lat1 + (lat2 - lat1) * interpolation_factor
    interpolated_lon = lon1 + (lon2 - lon1) * interpolation_factor
    interpolated_height = height1 + (height2 - height1) * interpolation_factor
    return interpolated_lat, interpolated_lon, interpolated_height

def process_mrk_file(mrk_data, pos_data, mrk_utc_format, pos_utc_format):
    print(f"Processing {len(mrk_data)} lines from .MRK file")
    output_data = []
    for mrk_line in mrk_data:
        mrk_time_str = str(mrk_line[3])  # Convert UTC time to string
        try:
            closest_pos_data = find_closest_times(mrk_time_str, pos_data, mrk_utc_format, pos_utc_format)
            interpolated_lat, interpolated_lon, interpolated_height = interpolate_positions(mrk_time_str, closest_pos_data, mrk_utc_format, pos_utc_format)
            output_line = mrk_line[:4] + [f"{interpolated_lat:.8f}", f"{interpolated_lon:.8f}", f"{interpolated_height:.3f}"] + mrk_line[4:]
            output_data.append("\t".join(str(field) for field in output_line))
        except ValueError as e:
            print(f"Error: {str(e)}")
            return
    print(f"Generated {len(output_data)} lines of output data")
    return output_data

def write_output_mrk_file(output_data, original_mrk_file):
    output_file = os.path.join(os.path.dirname(original_mrk_file), f"POS-{os.path.basename(original_mrk_file)}")
    with open(output_file, "w") as file:
        file.write("\n".join(output_data))
    print(f"Output file written: {output_file}")

def main():
    # Get the current working directory
    current_dir = os.getcwd()

    try:
        mrk_file = find_mrk_file(current_dir)
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        return
    pos_files = [file for file in os.listdir(current_dir) if file.endswith(".pos")]
    if not pos_files:
        raise FileNotFoundError("No .pos file found in the current directory.")
    if len(pos_files) > 1:
        print("Multiple .pos files found in the current directory. Using the first one.")
    pos_file = os.path.join(current_dir, pos_files[0])
    try:
        with open(pos_file, "r") as file:
            pos_data = [line.strip().split() for line in file if not line.startswith("%")]
    except IOError as e:
        raise IOError(f"Error reading .pos file: {str(e)}")
    mrk_utc_format = "%Y-%m-%d %H:%M:%S.%f"  # Update this with the correct format for the MRK file
    pos_utc_format = "%Y/%m/%d %H:%M:%S.%f"  # Update this with the correct format for the POS file
    mrk_data = read_mrk_file(mrk_file)
    output_data = process_mrk_file(mrk_data, pos_data, mrk_utc_format, pos_utc_format)
    if output_data:
        write_output_mrk_file(output_data, mrk_file)
        print(f"Processed {mrk_file} and created POS-{os.path.basename(mrk_file)} in the current directory.")

if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, IOError, ValueError) as e:
        print(f"Error: {str(e)}")
