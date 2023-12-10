import pandas as pd


def calculate_distance_matrix(csv_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file, index_col='ID')

    # Initialize an empty DataFrame for the distance matrix
    distance_matrix = pd.DataFrame(index=df.index, columns=df.index)

    # Iterate through each pair of toll locations
    for toll_A in df.index:
        for toll_B in df.index:
            # Skip diagonal entries
            if toll_A == toll_B:
                distance_matrix.loc[toll_A, toll_B] = 0
            else:
                # Check if distances are known for both A to B and B to A
                if (f'{toll_A}-{toll_B}' in df.columns) and (f'{toll_B}-{toll_A}' in df.columns):
                    distance_A_B = df.at[toll_A, f'{toll_A}-{toll_B}']
                    distance_B_A = df.at[toll_B, f'{toll_B}-{toll_A}']
                    # Calculate the cumulative distance
                    cumulative_distance = distance_A_B + distance_B_A
                    distance_matrix.loc[toll_A, toll_B] = cumulative_distance
                    distance_matrix.loc[toll_B, toll_A] = cumulative_distance

    return distance_matrix


def unroll_distance_matrix(distance_matrix):
    # Initialize an empty DataFrame for unrolled distances
    unrolled_distances = pd.DataFrame(columns=['id_start', 'id_end', 'distance'])

    # Iterate through each pair of toll locations
    for toll_A in distance_matrix.index:
        for toll_B in distance_matrix.columns:
            # Skip diagonal entries
            if toll_A != toll_B:
                distance = distance_matrix.at[toll_A, toll_B]
                # Append the data to the unrolled_distances DataFrame
                unrolled_distances = unrolled_distances.append({'id_start': toll_A, 'id_end': toll_B, 'distance': distance}, ignore_index=True)

    return unrolled_distances



def find_ids_within_ten_percentage_threshold(unrolled_distances, reference_value):
    # Filter rows based on the reference_value
    reference_data = unrolled_distances[unrolled_distances['id_start'] == reference_value]

    if reference_data.empty:
        return "Reference value not found in the DataFrame."

    # Calculate the average distance for the reference value
    average_distance = reference_data['distance'].mean()

    # Calculate the threshold range
    lower_threshold = average_distance * 0.9
    upper_threshold = average_distance * 1.1

    # Filter rows within the 10% threshold
    within_threshold = unrolled_distances[(unrolled_distances['distance'] >= lower_threshold) & (unrolled_distances['distance'] <= upper_threshold)]

    # Get unique values from the 'id_start' column and sort them
    result_ids = sorted(within_threshold['id_start'].unique())

    return result_ids


def calculate_toll_rate(unrolled_distances):
    # Create new columns for each vehicle type with their respective rate coefficients
    vehicle_types = ['moto', 'car', 'rv', 'bus', 'truck']
    rate_coefficients = [0.8, 1.2, 1.5, 2.2, 3.6]

    for vehicle_type, rate_coefficient in zip(vehicle_types, rate_coefficients):
        # Calculate toll rates by multiplying distance with the rate coefficient
        unrolled_distances[vehicle_type] = unrolled_distances['distance'] * rate_coefficient

    return unrolled_distances


def calculate_time_based_toll_rates(unrolled_distances):
    # Define time ranges and discount factors
    weekday_time_ranges = [(time(0, 0, 0), time(10, 0, 0)),
                           (time(10, 0, 0), time(18, 0, 0)),
                           (time(18, 0, 0), time(23, 59, 59))]
    weekend_time_ranges = [(time(0, 0, 0), time(23, 59, 59))]
    weekday_discount_factors = [0.8, 1.2, 0.8]
    weekend_discount_factor = 0.7

    # Create new columns for time-based toll rates
    for time_range in weekday_time_ranges + weekend_time_ranges:
        start_time, end_time = time_range
        day_range = pd.date_range(datetime.min, datetime.min + timedelta(days=6), freq='D')
        
        for day in day_range:
            start_datetime = datetime.combine(day.date(), start_time)
            end_datetime = datetime.combine(day.date(), end_time)

            mask = (unrolled_distances['start_time'] >= start_datetime) & (unrolled_distances['end_time'] <= end_datetime)
            if not mask.any():
                continue
            
            # Apply discount factors based on weekdays and weekends
            discount_factor = weekday_discount_factors if day.weekday() < 5 else weekend_discount_factor
            for vehicle_type in ['moto', 'car', 'rv', 'bus', 'truck']:
                unrolled_distances.loc[mask, vehicle_type] *= discount_factor

    return unrolled_distances
