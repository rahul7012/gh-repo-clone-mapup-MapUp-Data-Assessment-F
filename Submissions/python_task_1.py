
import pandas as pd


def generate_car_matrix(dataset_path)->pd.DataFrame:


    # Load the CSV into a DataFrame
    df = pd.read_csv(dataset_path)

    # Create a pivot table with id_1 as index, id_2 as columns, and car as values
    car_matrix = df.pivot(index='id_1', columns='id_2', values='car').fillna(0)

    # Set diagonal values to 0
    for col in car_matrix.columns:
        car_matrix.at[col, col] = 0

    return car_matrix


def get_type_count(df)->dict:


    # Create a new categorical column 'car_type'
    df['car_type'] = pd.cut(df['car'], bins=[-float('inf'), 15, 25, float('inf')],
                            labels=['low', 'medium', 'high'], right=False)

    # Count occurrences for each car_type category
    type_count = df['car_type'].value_counts().to_dict()

    # Sort the dictionary alphabetically based on keys
    sorted_type_count = dict(sorted(type_count.items()))

    return sorted_type_count


def get_bus_indexes(df)->list:
    # Calculate the mean value of the 'bus' column
    bus_mean = df['bus'].mean()

    # Identify indices where the 'bus' values are greater than twice the mean
    bus_indexes = df[df['bus'] > 2 * bus_mean].index.tolist()

    # Sort the indices in ascending order
    bus_indexes.sort()

    return bus_indexes


def filter_routes(df)->list:
    # Group by 'route' and calculate the average of 'truck' column for each route
    route_avg_truck = df.groupby('route')['truck'].mean()

    # Filter routes where the average of 'truck' column is greater than 7
    selected_routes = route_avg_truck[route_avg_truck > 7].index.tolist()

    # Sort the list of selected routes
    selected_routes.sort()

    return selected_routes


def multiply_matrix(input_matrix)->pd.DataFrame:
    # Copy the input matrix to avoid modifying the original DataFrame
    modified_matrix = input_matrix.copy()

    # Apply the specified logic to each value in the DataFrame
    modified_matrix[modified_matrix > 20] *= 0.75
    modified_matrix[modified_matrix <= 20] *= 1.25

    # Round the values to 1 decimal place
    modified_matrix = modified_matrix.round(1)

    return modified_matrix


def verify_timestamps(df)->pd.Series:
    # Combine 'startDay' and 'startTime' columns to create a 'start_timestamp' column
    df['start_timestamp'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'])

    # Combine 'endDay' and 'endTime' columns to create an 'end_timestamp' column
    df['end_timestamp'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'])

    # Check if each (id, id_2) pair covers a full 24-hour period and spans all 7 days
    incomplete_timestamps = df.groupby(['id', 'id_2']).apply(lambda group: not (
        (group['end_timestamp'].max() - group['start_timestamp'].min()) == pd.Timedelta(days=6, hours=23, minutes=59, seconds=59)
        and group['start_timestamp'].min().time() == pd.Timestamp('00:00:00').time()
        and group['end_timestamp'].max().time() == pd.Timestamp('23:59:59').time()
    ))

    return incomplete_timestamps
