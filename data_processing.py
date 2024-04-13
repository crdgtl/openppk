import os
from datetime import datetime, timedelta

def read_mrk_file(mrk_file):
    """
    Read the .MRK file and parse its contents.

    Args:
        mrk_file (str): The path to the .MRK file.

    Returns:
        list: A list of parsed data from the .MRK file, where each element is a list of values from a line.
    """
    with open(mrk_file, "r") as file:
        lines = file.readlines()

    data = []
    prev_utc_time = None
    for line in lines:
        fields = line.strip().split("\t")
        try:
            gps_week = int(fields[2].strip("[]"))
            gps_seconds = float(fields[1])
            utc_time = gps_to_utc(gps_week, gps_seconds)

            if prev_utc_time is not None and utc_time <= prev_utc_time:
                print(f"Warning: UTC times are not increasing for row {len(data) + 1}. Continuing with processing...")
            prev_utc_time = utc_time

            row_data = fields[:3] + [utc_time] + fields[3:]
            data.append(row_data)
        except (ValueError, IndexError) as e:
            print(f"Error parsing line {len(data) + 1}: {str(e)}. Skipping line.")

    return data

def gps_to_utc(gps_week, gps_seconds):
    """
    Convert GPS time to UTC time.

    Args:
        gps_week (int): GPS week number.
        gps_seconds (float): GPS seconds of the week.

    Returns:
        datetime: UTC time corresponding to the GPS time.
    """
    gps_epoch = datetime(1980, 1, 6)
    elapsed_time = timedelta(weeks=gps_week, seconds=gps_seconds)
    utc_time = gps_epoch + elapsed_time
    return utc_time

def process_mrk_file(mrk_data, pos_data, mrk_utc_format, pos_utc_format):
    """
    Process the .MRK file data and interpolate positions.

    Args:
        mrk_data (list): Parsed data from the .MRK file.
        pos_data (list): Position data from the .pos file.
        mrk_utc_format (str): UTC time format used in the .MRK file.
        pos_utc_format (str): UTC time format used in the .pos file.

    Returns:
        list: A list of processed output data, where each element is a list of values.
    """
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

def find_closest_times(mrk_time_str, pos_data, mrk_utc_format, pos_utc_format):
    """
    Find the closest UTC times in the .pos file data for a given UTC time from the .MRK file.

    Args:
        mrk_time_str (str): UTC time from the .MRK file.
        pos_data (list): Position data from the .pos file.
        mrk_utc_format (str): UTC time format used in the .MRK file.
        pos_utc_format (str): UTC time format used in the .pos file.

    Returns:
        list: A list of the two closest position data entries.

    Raises:
        ValueError: If no matching UTC timestamps are found in the .pos file.
    """
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

def parse_utc_time(utc_time_str, utc_format):
    """
    Parse a UTC time string into a datetime object.

    Args:
        utc_time_str (str): UTC time string.
        utc_format (str): UTC time format.

    Returns:
        datetime: Parsed UTC time as a datetime object.

    Raises:
        ValueError: If the UTC timestamp format is invalid.
    """
    try:
        return datetime.strptime(utc_time_str, utc_format)
    except ValueError:
        if '.' in utc_time_str:
            utc_time_parts = utc_time_str.split('.')
            fractional_part = utc_time_parts[1].ljust(6, '0')
            utc_time_str = '.'.join([utc_time_parts[0], fractional_part])
            return datetime.strptime(utc_time_str, utc_format)
        raise ValueError(f"Invalid UTC timestamp format: {utc_time_str}")

def interpolate_positions(mrk_time_str, closest_pos_data, mrk_utc_format, pos_utc_format):
    """
    Interpolate positions based on the closest UTC times.

    Args:
        mrk_time_str (str): UTC time from the .MRK file.
        closest_pos_data (list): List of the two closest position data entries.
        mrk_utc_format (str): UTC time format used in the .MRK file.
        pos_utc_format (str): UTC time format used in the .pos file.

    Returns:
        tuple: Interpolated latitude, longitude, and height.
    """
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

def write_output_mrk_file(output_data, original_mrk_file):
    """
    Write the processed output data to a new .MRK file.

    Args:
        output_data (list): List of processed output data.
        original_mrk_file (str): Path to the original .MRK file.
    """
    output_file = os.path.join(os.path.dirname(original_mrk_file), f"POS-{os.path.basename(original_mrk_file)}")
    with open(output_file, "w") as file:
        file.write("\n".join(output_data))
    print(f"Output file written: {output_file}")
