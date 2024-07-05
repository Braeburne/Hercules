import json
import datetime
import os
import re
import uuid
import pytz  # Import pytz for time zone support

# List of time zones for user selection
TIME_ZONES = [
    ("Pacific/Midway", "UTC-11:00"),  # Midway Island, Samoa (SST)
    ("Pacific/Honolulu", "UTC-10:00"),  # Hawaii (HST)
    ("Pacific/Marquesas", "UTC-09:30"),  # Marquesas Islands (MART)
    ("America/Anchorage", "UTC-09:00"),  # Alaska (AKST)
    ("America/Los_Angeles", "UTC-08:00"),  # Pacific Time (US & Canada) (PST)
    ("America/Denver", "UTC-07:00"),  # Mountain Time (US & Canada) (MST)
    ("America/Phoenix", "UTC-07:00"),  # Arizona (MST)
    ("America/Chicago", "UTC-06:00"),  # Central Time (US & Canada) (CST)
    ("America/New_York", "UTC-05:00"),  # Eastern Time (US & Canada) (EST)
    ("America/Caracas", "UTC-04:30"),  # Caracas, Venezuela (VET)
    ("America/Halifax", "UTC-04:00"),  # Atlantic Time (Canada) (AST)
    ("America/Santiago", "UTC-04:00"),  # Santiago, Chile (CLST)
    ("America/St_Johns", "UTC-03:30"),  # Newfoundland (NST)
    ("America/Sao_Paulo", "UTC-03:00"),  # São Paulo, Brazil (BRT)
    ("America/Argentina/Buenos_Aires", "UTC-03:00"),  # Buenos Aires, Argentina (ART)
    ("America/Noronha", "UTC-02:00"),  # Fernando de Noronha, Brazil (FNT)
    ("Atlantic/Azores", "UTC-01:00"),  # Azores, Portugal (AZOT)
    ("UTC", "UTC"),  # Coordinated Universal Time (UTC)
    ("Europe/London", "UTC+00:00"),  # London, Dublin, Lisbon (GMT/BST)
    ("Africa/Lagos", "UTC+01:00"),  # Lagos, Nigeria (WAT)
    ("Europe/Paris", "UTC+01:00"),  # Paris, Berlin, Rome (CET/CEST)
    ("Africa/Johannesburg", "UTC+02:00"),  # Johannesburg, South Africa (SAST)
    ("Europe/Moscow", "UTC+03:00"),  # Moscow, St. Petersburg, Volgograd (MSK)
    ("Asia/Dubai", "UTC+04:00"),  # Dubai, Abu Dhabi (GST)
    ("Asia/Tehran", "UTC+04:30"),  # Tehran, Iran (IRST)
    ("Asia/Kolkata", "UTC+05:30"),  # India Standard Time (IST)
    ("Asia/Kathmandu", "UTC+05:45"),  # Kathmandu, Nepal (NPT)
    ("Asia/Dhaka", "UTC+06:00"),  # Dhaka, Bangladesh (BDT)
    ("Asia/Bangkok", "UTC+07:00"),  # Bangkok, Hanoi, Jakarta (ICT)
    ("Asia/Singapore", "UTC+08:00"),  # Singapore, Kuala Lumpur, Perth (SGT)
    ("Asia/Tokyo", "UTC+09:00"),  # Tokyo, Osaka, Sapporo (JST)
    ("Australia/Sydney", "UTC+10:00"),  # Sydney, Melbourne, Brisbane (AEST)
    ("Pacific/Guam", "UTC+10:00"),  # Guam, Port Moresby (ChST)
    ("Pacific/Fiji", "UTC+12:00"),  # Fiji, Marshall Islands (FJT)
    ("Pacific/Auckland", "UTC+12:00"),  # Auckland, Wellington (NZST)
]

def get_time_zone():
    # Prompt user to select a time zone and return both IANA and UTC formats.
    print("\nSelect your time zone:")
    for idx, (iana, utc) in enumerate(TIME_ZONES, start=1):
        print(f"[{idx}] {iana} ({utc})")

    while True:
        choice = input(f"\nEnter your choice (1-{len(TIME_ZONES)}): ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(TIME_ZONES):
                return TIME_ZONES[index]
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def print_logo():
    print("""
  ___ ___                             .__                 
 /   |   \   ___________   ____  __ __|  |   ____   ______
/    ~    \_/ __ \_  __ \_/ ___\|  |  \  | _/ __ \ /  ___/
\    Y    /\  ___/|  | \/\  \___|  |  /  |_\  ___/ \___ \ 
 \___|_  /  \___  >__|    \___  >____/|____/\___  >____  >
       \/       \/            \/                \/     \/ 
    """)

# Generates sessions ID using UUID version 4
def generate_session_id():
    return str(uuid.uuid4())

# Function to load data from JSON file
def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Function to save data to JSON file
def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def validate_input(prompt, regex_pattern):
    while True:
        user_input = input(prompt)
        if re.fullmatch(regex_pattern, user_input):
            return user_input
        else:
            print("Invalid input format. Please enter the input in the correct format.")

# Print options in a numbered list.
def print_numbered_options(options):
    for idx, option in enumerate(options, start=1):
        print(f"[{idx}] {option}")

# Select an option from a list and return the index.
def select_option(options, message):
    print(message)
    print_numbered_options(options)
    choice = input(f"\nEnter your choice (1-{len(options)}): ")
    try:
        index = int(choice) - 1
        if 0 <= index < len(options):
            return index
        else:
            print("Invalid choice. Please select a valid option.")
            return select_option(options, message)
    except ValueError:
        print("Invalid input. Please enter a number.")
        return select_option(options, message)

# Function to calculate time elapsed
def calculate_time_elapsed(start_time, end_time):
    # Define input and output formats
    input_format = "%I:%M %p"  # HH:MM AM/PM format
    output_format = "%Y-%m-%d %H:%M:%S"  # ISO 8601 format for datetime
    
    # Parse start and end times
    start = datetime.datetime.strptime(start_time, input_format)
    end = datetime.datetime.strptime(end_time, input_format)
    
    # Convert to ISO 8601 format
    # start_iso = start.strftime(output_format)
    # end_iso = end.strftime(output_format)
    
    # Calculate elapsed time
    elapsed = end - start

    # Format elapsed time string to HH:MM:SS format
    elapsed_str = "{:02}:{:02}:{:02}".format(elapsed.seconds // 3600, (elapsed.seconds // 60) % 60, elapsed.seconds % 60)
    
    return elapsed_str

def calculate_average_time_per_workout(time_elapsed, exercise_amount):
    try:
        # Splitting time_elapsed into hours, minutes, and seconds
        times = time_elapsed.split(':')
        hours = int(times[0])
        minutes = int(times[1])
        seconds = int(times[2])

        # Convert hours, minutes, seconds to total seconds
        total_seconds = hours * 3600 + minutes * 60 + seconds

        # Calculate average time per workout in seconds
        average_time_per_workout_seconds = total_seconds / int(exercise_amount)

        # Convert average time per workout to timedelta object
        average_time_per_workout_timedelta = datetime.timedelta(seconds=average_time_per_workout_seconds)

        # Format average time per workout as string
        average_time_per_workout_str = str(average_time_per_workout_timedelta)

        return average_time_per_workout_str

    except ValueError:
        # Handle if the string format does not match expected format
        raise ValueError("Invalid time duration format for time_elapsed")

def generate_exercise_logs(exercise_count):
    # Initialize an empty list to store exercise logs
    exercise_logs = []

    # Loop to prompt for each exercise
    for exercise_index in range(int(exercise_count)):
        print(f"\nExercise {exercise_index + 1}")
        exercise_name = input("Exercise Name: ")
        weightage = input("Weightage (Lbs.) (Note: Input 'Bodyweight' for Calisthenics): ")
        sets = input("Sets: ")
        reps = input("Reps: ")
        start_time = input("Start Time (HH:MM {AM/PM}): ")
        end_time = input("End Time (HH:MM {AM/PM}): ")
        time_elapsed = calculate_time_elapsed(start_time, end_time)
        average_time_between_sets = calculate_average_time_per_workout(time_elapsed, sets)
        sets_completed = input("Sets Completed (True/False): ").lower() == 'true'
        machine_used = input("Machine Used (True/False): ").lower() == 'true'

        # Create exercise log object
        exercise_log = {
            "Exercise_Name": exercise_name,
            "Weightage": weightage,
            "Sets": sets,
            "Reps": reps,
            "Time_Elapsed": time_elapsed,
            "Average_Time_Between_Sets": average_time_between_sets,
            "Sets_Completed": sets_completed,
            "Machine_Used": machine_used
        }

        # Append exercise log to exercise_logs list
        exercise_logs.append(exercise_log)

    return exercise_logs

def get_current_month_log_file():
    today = datetime.datetime.today()
    month_year = today.strftime('%m-%Y')
    log_filename = f"{month_year}_gym_logs.json"

    if not os.path.exists(log_filename):
        with open(log_filename, 'w') as file:
            json.dump({"Gym_Logs": []}, file)  # Initialize with empty array
        print(f"Created new gym log file: {log_filename}")

    return log_filename

# Function to start a review session
def program_loop(selected_iana, selected_utc, session_id):
    gym_logs_filename = get_current_month_log_file()

    # Load existing logs or initialize if not exists
    if os.path.exists(gym_logs_filename):
        with open(gym_logs_filename, 'r') as file:
            gym_logs = json.load(file)
    else:
        gym_logs = {"Gym_Logs": []}
    
    # Determine the numerical indicator for the new log entry
    log_position = len(gym_logs["Gym_Logs"]) + 1
    log_entry_number = f"{log_position:02}"  # Zero-padded to two digits

    # Gather information about the entry time of the gym log
    start_time = datetime.datetime.now().isoformat()

    # Get UTC time of gym log creation
    utc_start_time = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat() + 'Z'

    # Get HTTP Date timestamp (RFC 1123 format)
    http_date_time = datetime.datetime.now(pytz.timezone(selected_iana)).strftime('%a, %d %b %Y %H:%M:%S %Z')

    # Format the Data Log ID for the log_entry
    data_log_id = (f"{log_entry_number} | {http_date_time}")

    print("Commencing gym log creation...")

    venues = ["Home Gym", "Apartment Gym", "Commercial Gym"]
    venue_category = select_option(venues, "\nWhat kind of venue did you work out at today?")

    if venue_category == 1:
        venue_category = "Home Gym"
    elif venue_category == 2:
        venue_category = "Apartment Gym"
    elif venue_category == 3:
        venue_category = "Commercial Gym"
    else:
        venue_category = "Venue Category Assignment Error"

    print("\nWhen did you begin your workout? (Format as HH:MM {AM/PM} in your designated IANA time zone)")
    start_time = input("Enter Answer: ")

    print("\nWhen did you finish your workout? (Format as HH:MM {AM/PM} in your designated IANA time zone)")
    end_time = input("Enter Answer: ")

    time_elapsed = calculate_time_elapsed(start_time, end_time)

    print("\nHow many exercises did you do this gym session?")
    exercise_count = input("Enter Answer: ")

    average_time_per_workout = calculate_average_time_per_workout(time_elapsed, exercise_count)

    exercise_logs = generate_exercise_logs(exercise_count)

    # Initializing data log with all known information thus far
    log_entry = {
            "Review_Instance_Data_Log_ID": data_log_id,
            "IANA_Time_Zone": selected_iana,
            "UTC_Time_Zone": selected_utc,
            "Date": datetime.date.today().strftime("%m-%d-%Y"),
            "Venue_Category": venue_category,
            "Time_Elapsed": time_elapsed,
            "Average_Time_Per_Workout": average_time_per_workout,
            "ISO_8601_Local_Timestamp": start_time,
            "ISO_8601_UTC_Timestamp": utc_start_time,
            "HTTP_Date_Timestamp": http_date_time,
            "Exercise_Logs": exercise_logs,
            "UUID4_Session_ID": session_id
        }
    
    gym_logs["Gym_Logs"].append(log_entry)

    # Save updated logs back to file
    save_json(gym_logs_filename, gym_logs)

    print("Gym session logged successfully.")

    return

def main():
    print_logo()

    # Ask user to select time zone
    selected_iana, selected_utc = get_time_zone()
    print(f"\nSelected time zone (IANA format): {selected_iana}")
    print(f"Selected time zone (UTC format): {selected_utc}")
    # Generate Session ID, which we be designated on all data logs created during this session.
    # This Session ID is re-generated every time the user opens a new session - which happens
    # whenever the program is run.
    session_id = generate_session_id()

    while True:
        # Begin Program Loop
        program_loop(selected_iana, selected_utc, session_id)

        # Prompt for next action
        print("\nWhat would you like to do next?")
        print("[1] View Gym Data Analytics")
        print("[2] View Gym Logs")
        print("[3] Exit")

        choice = input("\nEnter your choice (1-3): ")

        while True:
            if choice == '1':
                return
            elif choice == '2':
                return  # Go back to select a different section
            elif choice == '3':
                print("\nThank you for using Hercules!")
                return  # Exit the program
            else:
                print("\nInvalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()  