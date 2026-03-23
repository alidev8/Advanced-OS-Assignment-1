import time
import os

QUEUE_FILE_PATH = "job_queue.txt"
COMPLETED_FILE_PATH = "completed_jobs.txt"
SCHEDULER_LOG_PATH = "scheduler_log.txt"
ROUND_ROBIN_TIME_QUANTUM = 5

def log_scheduler_event(event_description):
    """
    Append events to the log file immediately to ensure the audit trail 
    is preserved even if the system crashes during a scheduling run.
    """
    with open(SCHEDULER_LOG_PATH, "a") as log_file:
        log_file.write(str(time.time()) + " - " + event_description + "\n")

def load_pending_jobs():
    """
    Read the job queue from disk. This allows the queue to persist 
    across system restarts without relying on a complex database.
    """
    if not os.path.exists(QUEUE_FILE_PATH):
        return []
    
    pending_jobs = []
    with open(QUEUE_FILE_PATH, "r") as file_handle:
        for line in file_handle:
            clean_line = line.strip()
            if not clean_line:
                continue
            
            job_data = clean_line.split(",")
            pending_jobs.append({
                "student_id": job_data[0],
                "job_name": job_data[1],
                "execution_time": int(job_data[2]),
                "priority_level": int(job_data[3])
            })
    return pending_jobs

def save_pending_jobs(jobs_list):
    """Overwrite the queue file with the updated list of jobs."""
    with open(QUEUE_FILE_PATH, "w") as file_handle:
        for job in jobs_list:
            file_handle.write(job["student_id"] + "," + job["job_name"] + "," + str(job["execution_time"]) + "," + str(job["priority_level"]) + "\n")

def record_completed_job(job):
    """Store finished jobs in a separate file to keep the active queue clean."""
    with open(COMPLETED_FILE_PATH, "a") as file_handle:
        file_handle.write(job["student_id"] + "," + job["job_name"] + "\n")

def submit_new_job_request():
    """Collect user input and format it safely before adding it to the queue."""
    student_id = input("Enter Student ID (e.g. 212072): ")
    job_name = input("Enter Job Name (e.g. VR-Stroke-Rehab-Data): ")
    execution_time = int(input("Enter Estimated Execution Time in seconds: "))
    priority_level = int(input("Enter Priority Level (1 to 10): "))

    current_jobs = load_pending_jobs()
    current_jobs.append({
        "student_id": student_id, 
        "job_name": job_name, 
        "execution_time": execution_time, 
        "priority_level": priority_level
    })
    
    save_pending_jobs(current_jobs)
    log_scheduler_event("Submitted job " + job_name + " for student " + student_id)
    print("Job successfully added to the queue.")

def execute_round_robin_scheduling():
    """
    Process jobs in small bursts. Jobs requiring more time than the quantum 
    are pushed to the back of the line to ensure fair resource allocation.
    """
    active_jobs = load_pending_jobs()
    
    if not active_jobs:
        print("No pending jobs to run.")
        return

    print("Starting Round Robin Scheduling.")
    
    while len(active_jobs) > 0:
        current_job = active_jobs.pop(0)
        print("Running computational job: " + current_job["job_name"])

        if current_job["execution_time"] > ROUND_ROBIN_TIME_QUANTUM:
            current_job["execution_time"] = current_job["execution_time"] - ROUND_ROBIN_TIME_QUANTUM
            active_jobs.append(current_job)
            print("Job paused. Time quantum reached for " + current_job["job_name"])
        else:
            print("Job fully completed: " + current_job["job_name"])
            record_completed_job(current_job)
            log_scheduler_event("Round Robin finished job " + current_job["job_name"])

        save_pending_jobs(active_jobs)
        time.sleep(1) 

    print("All Round Robin processes are finished.")

def execute_priority_scheduling():
    """
    Sort the queue by priority before execution. This ensures critical 
    research tasks run first and minimizes bottleneck risks.
    """
    active_jobs = load_pending_jobs()
    
    if not active_jobs:
        print("No pending jobs available.")
        return

    print("Starting Priority Scheduling.")
    
    active_jobs.sort(key=lambda x: x["priority_level"])

    for current_job in active_jobs:
        print("Executing high priority job: " + current_job["job_name"])
        time.sleep(1)
        record_completed_job(current_job)
        log_scheduler_event("Priority finished job " + current_job["job_name"])

    save_pending_jobs([])
    print("All priority jobs executed successfully.")

def display_completed_jobs():
    """Retrieve and print the log of all finished jobs."""
    if os.path.exists(COMPLETED_FILE_PATH):
        with open(COMPLETED_FILE_PATH, "r") as file_handle:
            print(file_handle.read())
    else:
        print("No jobs have been completed yet.")

def run_scheduler_interface():
    """Main application loop handling user routing."""
    while True:
        print("--- HPC Scheduler Menu ---")
        print("1. View Pending Jobs")
        print("2. Submit a Job Request")
        print("3. Process using Round Robin")
        print("4. Process using Priority Scheduling")
        print("5. View Completed Jobs")
        print("Bye. Exit")

        menu_selection = input("Select an option: ")
        
        if menu_selection == "1":
            jobs = load_pending_jobs()
            for job in jobs:
                print("Pending Job:", job)
        elif menu_selection == "2":
            submit_new_job_request()
        elif menu_selection == "3":
            execute_round_robin_scheduling()
        elif menu_selection == "4":
            execute_priority_scheduling()
        elif menu_selection == "5":
            display_completed_jobs()
        elif menu_selection == "Bye":
            exit_confirmation = input("Confirm system exit? Y/N: ")
            if exit_confirmation == "Y":
                print("Goodbye.")
                break
        else:
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    run_scheduler_interface()
