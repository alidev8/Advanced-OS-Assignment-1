import os
import time
import hashlib

failed_login_tracker = {}
last_login_timestamp = {}
SUBMISSION_LOG_PATH = "submission_log.txt"
MAXIMUM_FILE_SIZE_MB = 5

def calculate_sha256_hash(file_path):
    """
    Generate a cryptographic hash of the file content. We read the file in 
    small chunks to prevent memory overload when processing large documents.
    """
    hash_generator = hashlib.sha256()
    with open(file_path, 'rb') as binary_file:
        file_chunk = binary_file.read(65536)
        while len(file_chunk) > 0:
            hash_generator.update(file_chunk)
            file_chunk = binary_file.read(65536)
    return hash_generator.hexdigest()

def validate_file_criteria(file_path):
    """
    Check if the file exists, matches allowed extensions, and is under the size limit.
    Returns a boolean indicating success or failure.
    """
    if not os.path.exists(file_path):
        print("Error. File not found on disk.")
        return False

    four_letter_extension = file_path[-4:]
    five_letter_extension = file_path[-5:]
    
    if four_letter_extension != ".pdf" and five_letter_extension != ".docx":
        print("Invalid format. The system only accepts pdf and docx files.")
        return False

    file_size_in_bytes = os.path.getsize(file_path)
    file_size_in_mb = file_size_in_bytes / 1048576 
    
    if file_size_in_mb > MAXIMUM_FILE_SIZE_MB:
        print("File is too large. Maximum size is 5MB.")
        return False

    return True

def check_for_duplicate_submission(file_name, file_hash):
    """Scan the log file to ensure the exact same file content has not been uploaded."""
    if not os.path.exists(SUBMISSION_LOG_PATH):
        return False

    with open(SUBMISSION_LOG_PATH, "r") as log_file:
        for logged_entry in log_file:
            if file_name in logged_entry and file_hash in logged_entry:
                return True
    return False

def submit_examination_file():
    """Handle the entire file upload flow using pure validation functions."""
    student_id = input("Enter Student ID: ")
    file_path = input("Enter exact file path: ")

    if not validate_file_criteria(file_path):
        return

    content_hash = calculate_sha256_hash(file_path)
    base_file_name = os.path.basename(file_path)

    if check_for_duplicate_submission(base_file_name, content_hash):
        print("Duplicate file detected. Identical content and name. Rejected.")
        return

    with open(SUBMISSION_LOG_PATH, "a") as log_file:
        log_file.write(str(time.time()) + " - " + student_id + " - " + base_file_name + " - " + content_hash + " - SUCCESS\n")
    print("Assignment submission successful.")

def authenticate_user():
    """
    Process logins while actively monitoring for brute force attacks 
    and suspiciously rapid login frequencies.
    """
    username = input("Enter Username: ")
    current_epoch_time = time.time()

    if username in failed_login_tracker and failed_login_tracker[username] >= 3:
        print("Security Alert. Account locked due to three failed login attempts.")
        return

    if username in last_login_timestamp:
        time_difference = current_epoch_time - last_login_timestamp[username]
        if time_difference < 60:
            print("Suspicious activity detected. Repeated login attempt within sixty seconds.")
            with open(SUBMISSION_LOG_PATH, "a") as log_file:
                log_file.write(str(current_epoch_time) + " - ALERT - Repeated login for " + username + "\n")

    password_input = input("Enter Password: ")
    
    if password_input != "securepass123":
        print("Login attempt failed.")
        failed_login_tracker[username] = failed_login_tracker.get(username, 0) + 1
        last_login_timestamp[username] = current_epoch_time
        
        with open(SUBMISSION_LOG_PATH, "a") as log_file:
            log_file.write(str(current_epoch_time) + " - LOGIN FAILED - " + username + "\n")
    else:
        print("Login success.")
        failed_login_tracker[username] = 0
        last_login_timestamp[username] = current_epoch_time
        
        with open(SUBMISSION_LOG_PATH, "a") as log_file:
            log_file.write(str(current_epoch_time) + " - LOGIN SUCCESS - " + username + "\n")

def display_all_submissions():
    """Print the contents of the submission database."""
    if not os.path.exists(SUBMISSION_LOG_PATH):
        print("No submissions found in the database.")
        return
        
    print("--- All Submitted Assignments ---")
    with open(SUBMISSION_LOG_PATH, "r") as log_file:
        print(log_file.read())

def run_security_interface():
    """Main application loop handling user routing."""
    while True:
        print("--- Exam Access Control Menu ---")
        print("1. Submit an assignment")
        print("2. List all submitted assignments")
        print("3. Simulate login attempt")
        print("Bye. Exit system")

        menu_selection = input("Select an option: ")
        
        if menu_selection == "1":
            submit_examination_file()
        elif menu_selection == "2":
            display_all_submissions()
        elif menu_selection == "3":
            authenticate_user()
        elif menu_selection == "Bye":
            exit_confirmation = input("Confirm exit Y/N: ")
            if exit_confirmation == "Y":
                print("Goodbye.")
                break
        else:
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    run_security_interface()
