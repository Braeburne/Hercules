import configparser
import datetime
import json
import os
import re
import uuid
import pytz  # Import pytz for time zone support

# Frequently Used Regex Patterns
middle_endian_date_regex = r'^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])-\d{4}$' # MM-DD-YYYY
clock_time_regex = r'^(0[1-9]|1[0-2]):[0-5][0-9] [APap][mM]$' # HH:MM AM/PM, not the 24-hour clock
stopwatch_regex = r'[0-5][0-9]:[0-5][0-9]$' # MM:SS
english_regex = r'^[A-Za-z\s]+$' # Alphabetic strings only
numeric_regex = r'^\d+$' # Numeric strings only
alphanumeric_regex = r'^[A-Za-z0-9\s]+$' # Letters, digits and spaces only
kleene_star_regex = r'.*?' # All characters allowed

# Create lists for use in several functions (e.g. select_option() function)
failure_list = ["Exhaustion", "Strain", "Environment", "Other"]
venues = ["Home Gym", "Apartment Gym", "Commercial Gym", "Improvised Gym", "Other"]
binary_choice = ["Yes", "No"]
booleans = ["True", "False"]
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
] # List of time zones for user selection

# Default settings.ini values
default_config = {
    'timezone': {
        'iana': 'UTC',
        'utc': 'UTC'
    },
    'profile': {
        'name': 'default'
    }
}

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

def get_current_month_log_file():
    today = datetime.datetime.today()
    month_year = today.strftime('%m-%Y')
    log_filename = f"{month_year}_fitness_session_logs.json"

    if not os.path.exists(log_filename):
        with open(log_filename, 'w') as file:
            json.dump({"Fitness_Session_Logs": []}, file)  # Initialize with empty array
        print(f"Created new fitness session log file: {log_filename}")

    return log_filename

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

        # Extract hours, minutes, and seconds from timedelta object
        avg_hours, remainder = divmod(average_time_per_workout_timedelta.seconds, 3600)
        avg_minutes, avg_seconds = divmod(remainder, 60)

        # Format average time per workout as string HH:MM:SS
        average_time_per_workout_str = f"{int(avg_hours):02}:{int(avg_minutes):02}:{int(avg_seconds):02}"

        return average_time_per_workout_str

    except ValueError:
        # Handle if the string format does not match expected format
        raise ValueError("Invalid time duration format for time_elapsed")

def generate_exercise_logs(exercise_count):
    # Initialize an empty list to store exercise logs
    exercise_logs = []

    # Loop to prompt for each exercise
    for exercise_index in range(int(exercise_count)):
        weightage = []
        weight_type = ""
        sets = 0
        reps = []

        print(f"\nExercise {exercise_index + 1}")
        exercise_name = validate_input("Exercise Name: ", kleene_star_regex)

        exercise_type = select_option(["Timed Exercise", "Set-based Exercise"], "Exercise Type:")
        if exercise_type == 0:
            exercise_type = "Timed Exercise"
        else:
            exercise_type = "Set-based Exercise"

        exercise_class = select_option(["Weightlifting", "Calisthenics", "Plyometrics", "Cardio"], "\nExercise Class:")
        if exercise_class == 0:
            exercise_class = "Weightlifting"
        elif exercise_class == 1:
            exercise_class = "Calisthenics"
        elif exercise_class == 2:
            exercise_class = "Plyometrics"
        else:
            exercise_class = "Cardio"

        weight_setup = select_option(["Freeweight", "Machine"], "\nWhat type of weight was used in the exercise?")
        if weight_setup == 0:
            weight_setup = "Freeweight"
        else:
            weight_setup = "Machine"
            weight_type = "Plates"

        if weight_setup == "Freeweight":
            weight_type = select_option(["Barbell", "Dumbell", "Bodyweight"], "\nWhat type of freeweights did you use?")
            if weight_type == 0:
                weight_type = "Barbell"
            elif weight_type == 1:
                weight_type = "Dumbell"
            elif weight_type == 2:
                weight_type = "Bodyweight"

        if weight_setup == "Freeweight" and weight_type != "Bodyweight":
            print("\nHow many weights did you use in the exercise?")
            weight_count = int(validate_input("Enter Answer: ", numeric_regex))
        else:
            weight_count = "N/A"

        consistent_weightage = select_option(binary_choice, "\nDid you use the same weightage for all sets?")
        # print(consistent_weightage)
        if consistent_weightage == 0:
            consistent_weightage = True
        elif consistent_weightage == 1:
            consistent_weightage = False
        else:
            consistent_weightage = "Boolean Assignment Error"
        
        if consistent_weightage:
            weightage = validate_input("Weightage (lbs.) ('Bodyweight' or 'Clean Bar'): ", r'^\d+$|^Bodyweight$|^Clean Bar$')
            if weightage != "Clean Bar" and weightage != "Bodyweight":
                weightage = int(weightage)
            sets = int(validate_input("Sets: ", numeric_regex))
        else:
            sets = int(validate_input("How many sets did you perform? ", numeric_regex))
            for set_index in range(sets):
                weight = validate_input(f"Weightage for set {set_index + 1} (lbs.) ('Bodyweight' or 'Clean Bar'): ", r'^\d+$|^Bodyweight$|^Clean Bar$')
                if weight != "Clean Bar" and weight != "Bodyweight":
                    weight = int(weight)
                weightage.append(weight)

        if exercise_type == "Timed Exercise":
            reps = validate_input("Time(s): ", stopwatch_regex)
        else:
            consistent_reps = select_option(binary_choice, "\nDid you do the same number of reps for all sets?")
            # print(consistent_reps)
            if consistent_reps == 0:
                consistent_reps = True
            elif consistent_reps == 1:
                consistent_reps = False
            else:
                consistent_reps = "Boolean Assignment Error"

            if consistent_reps:
                reps = int(validate_input("Reps: ", numeric_regex))
            else:
                # print(f"Sets: {sets}")
                for set_index in range(sets):
                    reps_count = int(validate_input(f"Reps for set {set_index + 1}: ", numeric_regex))
                    reps.append(reps_count)

        # weightage = validate_input("Weightage (lbs.) ('Bodyweight' or 'Clean Bar'): ", r'^\d+$|^Bodyweight$|^Clean Bar$')
        start_time = validate_input("\nStart Time: ", clock_time_regex)
        end_time = validate_input("End Time: ", clock_time_regex)
        time_elapsed = calculate_time_elapsed(start_time, end_time)
        average_set_length = calculate_average_time_per_workout(time_elapsed, sets)
        
        machine_used = select_option(booleans, "\nMachine Used (True/False): ")
        if machine_used == 0:
            machine_used = True
        elif machine_used == 1:
            machine_used = False
        else:
            machine_used = "Boolean Assignment Error"

        if machine_used:
            machine_name = validate_input("Machine Name: ", kleene_star_regex)
            machine_brand = validate_input("Machine Brand: ", kleene_star_regex)
        else:
            machine_name = None
            machine_brand = None

        sets_failed = select_option(booleans, "\nSets Failed (True/False): ")
        if sets_failed == 0:
            sets_failed = True
        elif sets_failed == 1:
            sets_failed = False
        else:
            sets_failed = "Boolean Assignment Error"

        if sets_failed:
            reason = select_option(failure_list, "\nSelect your reason for failing to take the sets to completion:")
            if reason == 0:
                reason = failure_list[0]
            if reason == 1:
                reason = failure_list[1]
            if reason == 2:
                reason = failure_list[2]
            if reason == 3:
                reason = failure_list[3]
            
            if reason == "Other":
                reason = validate_input("Other: ", kleene_star_regex)
        else:
            reason = "N/A"

        boolean = select_option(binary_choice, "\nWould you like to write notes regarding the exercise?")
        if boolean == 0:
            boolean = True
        elif boolean == 1:
            boolean = False
        else:
            boolean = "Boolean Assignment Error"

        if boolean:
            notes = input("Notes: ")
        else:
            notes = "N/A"

        # Create exercise log object
        exercise_log = {
            "Exercise_Name": exercise_name,
            "Exercise_Type": exercise_type,
            "Exercise_Class": exercise_class,
            "Machine_Used": machine_used,
            "Machine_Name": machine_name,
            "Machine_Brand": machine_brand,
            "Weightage": weightage,
            "Weight_Setup": weight_setup,
            "Weight_Type": weight_type,
            "Weight_Count": weight_count,
            "Sets": sets,
            "Reps_or_Times": reps,
            "Time_Elapsed": time_elapsed,
            "Average_Set_Length": average_set_length,
            "Sets_Failed": sets_failed,
            "Cause_Of_Failure": reason,
            "Notes": notes
        }

        # Append exercise log to exercise_logs list
        exercise_logs.append(exercise_log)

    return exercise_logs

# Function to start a gym logging session
def program_loop():
    # Generate Session ID, which will be designated on all data logs created during this session.
    # This Session ID is re-generated every time the user opens a new session - which happens
    # whenever the program is run.
    session_id = generate_session_id()

    # Load settings from the config file
    config = load_config()

    # Fetch timezone settings from the config file
    selected_iana = config.get('timezone', 'iana')
    selected_utc = config.get('timezone', 'utc')
    username = config.get('profile', 'name')

    fitness_session_logs_filename = get_current_month_log_file()

    # Load existing logs or initialize if not exists
    if os.path.exists(fitness_session_logs_filename):
        with open(fitness_session_logs_filename, 'r') as file:
            fitness_session_logs = json.load(file)
    else:
        fitness_session_logs = {"Fitness_Session_Logs": []}
    
    # Determine the numerical indicator for the new log entry
    log_position = len(fitness_session_logs["Fitness_Session_Logs"]) + 1
    log_entry_number = f"{log_position:02}"  # Zero-padded to two digits

    # Gather information about the entry time of the gym log
    local_start_time = datetime.datetime.now().isoformat()

    # Get UTC time of gym log creation
    utc_start_time = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat() + 'Z'

    # Get HTTP Date timestamp (RFC 1123 format)
    http_date_time = datetime.datetime.now(pytz.timezone(selected_iana)).strftime('%a, %d %b %Y %H:%M:%S %Z')

    # Format the Data Log ID for the log_entry
    data_log_id = (f"{log_entry_number} | {http_date_time}")

    print("\nCommencing gym log creation...")

    print("\nWhat date did you complete this fitness session on? (Format as MM-DD-YYYY)")
    date = validate_input("Enter Answer: ", middle_endian_date_regex)

    venue_category = select_option(venues, "\nWhat kind of venue did you work out at on the session date?")

    if venue_category == 0:
        venue_category = "Home Gym"
    elif venue_category == 1:
        venue_category = "Apartment Gym"
    elif venue_category == 2:
        venue_category = "Commercial Gym"
    elif venue_category == 3:
        venue_category = "Improvised Gym"
    elif venue_category == 4:
        venue_category = "Other"
        venue_category = validate_input("Other: ", kleene_star_regex)
    else:
        venue_category = "Venue Category Assignment Error"

    boolean = select_option(binary_choice, "\nWould you like to write notes regarding the fitness session generally?")
    if boolean == 0:
        boolean = True
    elif boolean == 1:
        boolean = False
    else:
        boolean = "Boolean Assignment Error"    

    if boolean:
        notes = input("Notes: ")
    else:
        notes = "N/A"

    print("\nHow much did you weigh on the session date (lbs.)? Round to the nearest integer.")
    weight = validate_input("Enter Answer: ", numeric_regex)

    print("\nWhat time did you begin your workout? (Format as HH:MM {AM/PM} in your designated IANA time zone)")
    start_time = validate_input("Enter Answer: ", clock_time_regex)

    print("\nWhat time did you finish your workout? (Format as HH:MM {AM/PM} in your designated IANA time zone)")
    end_time = validate_input("Enter Answer: ", clock_time_regex)

    time_elapsed = calculate_time_elapsed(start_time, end_time)

    print("\nHow many exercises did you do in this fitness session?")
    exercise_count = validate_input("Enter Answer: ", numeric_regex)

    average_time_per_workout = calculate_average_time_per_workout(time_elapsed, exercise_count)

    exercise_logs = generate_exercise_logs(exercise_count)

    # Initializing data log with all known information thus far
    log_entry = {
            "Fitness_Session_Log_ID": data_log_id,
            "Username": username,
            "Weight": int(weight),
            "Venue_Category": venue_category,
            "IANA_Time_Zone": selected_iana,
            "UTC_Time_Zone": selected_utc,
            "Fitness_Session_Date": date,
            "Fitness_Session_Start_Time": start_time,
            "Fitness_Session_End_Time": end_time,
            "Time_Elapsed": time_elapsed,
            "Average_Time_Per_Workout": average_time_per_workout,
            "Record_ISO_8601_Local_Timestamp": local_start_time,
            "Record_ISO_8601_UTC_Timestamp": utc_start_time,
            "Record_HTTP_Date_Timestamp": http_date_time,
            "Record_Middle_Endian_Date": datetime.date.today().strftime("%m-%d-%Y"),
            "Record_UUID4_Session_ID": session_id,
            "Exercise_Logs": exercise_logs,
            "Fitness_Session_Notes": notes
        }
    
    fitness_session_logs["Fitness_Session_Logs"].append(log_entry)

    # Save updated logs back to file
    save_json(fitness_session_logs_filename, fitness_session_logs)

    print("\nFitness session logged successfully.")

    # Prompt for next action
    print("\nWhat would you like to do next?")
    print("[1] View Gym Data Analytics")
    print("[2] View Gym Logs")
    print("[3] Back to Main Menu")

    choice = input("\nEnter your choice (1-3): ")

    while True:
        if choice == '1':
            return # Unimplemented currently
        elif choice == '2':
            return  # Unimplemented currently
        elif choice == '3':
            return # Exit to main menu
        else:
            print("\nInvalid choice. Please select a valid option.")

def create_default_config():
    config = configparser.ConfigParser()
    config.read_dict(default_config)
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)
    print("\nDefault settings.ini file created with default values.\n")

def load_config():
    # Initialize the ConfigParser
    config = configparser.ConfigParser()
    config_file = 'settings.ini'
    modified = False
    
    if not os.path.exists(config_file):
        create_default_config()
    else:
        config.read(config_file)
        # Validate and update the configuration if necessary
        for section, values in default_config.items():
            if not config.has_section(section):
                config.add_section(section)
                modified = True
            for key, value in values.items():
                if not config.has_option(section, key):
                    config.set(section, key, value)
                    modified = True
        # Write any updates back to the config file
        with open(config_file, 'w') as configfile:
            config.write(configfile)

    if modified:
        print("\nIntegrity of settings file breached. File has been repaired with default values.")

    return config

def main_menu():
    print("What would you like to do?")
    print("[1] Log Fitness Session")
    print("[2] Settings")
    print("[0] Exit")
    answer = validate_input("Enter Answer: ", numeric_regex)
    case = int(answer)

    # Switch statement
    if case == 1:
        program_loop()
    elif case == 2:
        settings_menu()
    elif case == 0:
        print("\nThank you for using Hercules!")
        return True # Send termination signal to main()

def settings_menu():
    # Check that settings.ini is proper working order before performing on it
    config = load_config()

    print("\nWhat would you like to do?")
    print("[1] Edit Time Zone")
    print("[2] Edit Profile")
    print("[9] View Settings")
    print("[0] Cancel")
    answer = validate_input("Enter Answer: ", numeric_regex)
    case = int(answer)

    # Switch statement
    if case == 1:
        back_to_previous_menu = timezone_settings()
        if back_to_previous_menu:
            settings_menu()
    elif case == 2:
        back_to_previous_menu = profile_settings()
        if back_to_previous_menu:
            settings_menu()
    elif case == 9:
        print("\nCurrent Settings:")
        for section in config.sections():
            print(f"[{section}]")
            for key, value in config.items(section):
                print(f"{key} = {value}")
            print()  # Blank line for better readability
    elif case == 0:
        print("Cancelling...")
        return

def timezone_settings():
    config = load_config()
    
    # Fetch timezone settings from the config file
    selected_iana = config.get('timezone', 'iana')
    selected_utc = config.get('timezone', 'utc')
    print("\nLoading Time Zone Setting Data...")
    print(f"Time zone (IANA format): {selected_iana}")
    print(f"Time zone (UTC format): {selected_utc}")

    print("\nWhat would you like to do?")
    print("[1] Edit Setting")
    print("[2] Reset to Default")
    print("[0] Cancel")
    answer = validate_input("Enter Answer: ", numeric_regex)
    case = int(answer)

    # Switch statement
    if case == 1:
        selected_iana, selected_utc = get_time_zone()
        print(f"\nSelected time zone (IANA format): {selected_iana}")
        print(f"Selected time zone (UTC format): {selected_utc}")
        config.set('timezone', 'iana', selected_iana)
        config.set('timezone', 'utc', selected_utc)
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
        print("Operation complete.")
        return
    elif case == 2:
        selected_iana, selected_utc = "UTC", "UTC"
        config.set('timezone', 'iana', selected_iana)
        config.set('timezone', 'utc', selected_utc)
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
        print("Operation complete.")
        return
    elif case == 0:
        print("Cancelling...")
        return True

def profile_settings():
    config = load_config()
    
    # Fetch timezone settings from the config file
    username = config.get('profile', 'name')
    print("\nLoading Profile Settings Data...")
    print(f"Username: {username}")

    print("\nWhat would you like to do?")
    print("[1] Edit Setting")
    print("[2] Reset to Default")
    print("[0] Cancel")
    answer = validate_input("Enter Answer: ", numeric_regex)
    case = int(answer)

    # Switch statement
    if case == 1:
        username = validate_input("Enter new username (alphanumeric only): ", alphanumeric_regex)
        print(f"\nNew username: {username}")
        config.set('profile', 'name', username)
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
        print("Operation complete.")
        return
    elif case == 2:
        username = "UTC"
        config.set('profile', 'name', username)
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
        print("Operation complete.")
        return
    elif case == 0:
        print("Cancelling...")
        return True

def main():
    while True:
        print_logo()
        termination_signal = main_menu()
        if termination_signal:
            return # Exit the program

if __name__ == "__main__":
    main()  