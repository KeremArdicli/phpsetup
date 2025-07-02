import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import re
import time
import threading

selected_PHP_version = None
class ServiceControlPanel:
    def __init__(self, master):
        self.master = master
        master.title("Local Dev Control Panel")
        master.geometry("450x400")
        master.resizable(False, False)
        master.configure(bg="#f0f0f0")

        # --- Configuration Paths ---
        # Base directory for PHP versions
        self.php_base_dir = r"C:\PHP"
        # Directory where your Apache BAT scripts are located
        self.apache_bat_dir = r"C:\Apache24"
        # Directory where your MySQL BAT scripts are located
        self.mysql_bat_dir = r"C:\mysql"

        # BAT script paths (ensure these paths are correct on your system)
        self.bat_apache_start = os.path.join(self.apache_bat_dir, "start_apache.bat")
        self.bat_apache_stop = os.path.join(self.apache_bat_dir, "stop_apache.bat")
        self.bat_mysql_start = os.path.join(self.mysql_bat_dir, "start_mysql.bat")
        self.bat_mysql_stop = os.path.join(self.mysql_bat_dir, "stop_mysql.bat")

        # --- UI Elements ---
        self.create_widgets()
        self.update_status() # Initial status update

    def create_widgets(self):
        # Styling
        style = ttk.Style()
        style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Inter', 10))
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=5, relief="raised", borderwidth=2,
                        foreground='#333', background='#e0e0e0')
        style.map('TButton',
                  background=[('active', '#d0d0d0'), ('pressed', '#c0c0c0')],
                  foreground=[('active', '#000')])
        style.configure('Status.TLabel', font=('Inter', 11, 'bold'))
        style.configure('Feedback.TLabel', font=('Inter', 9), foreground='#555')
        style.configure('TCombobox', font=('Inter', 10))

        # Main Frame
        main_frame = ttk.Frame(self.master, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # PHP Version Selection
        php_frame = ttk.LabelFrame(main_frame, text="PHP Version", padding="10")
        php_frame.pack(pady=10, fill=tk.X)

        self.php_versions = self.get_php_versions()
        if not self.php_versions:
            self.php_versions = ["No PHP versions found"]
            messagebox.showwarning("Warning", f"No valid PHP versions found in {self.php_base_dir}. Please ensure 'phpXX' folders exist and contain 'php8apache2_4.dll'.")

        self.selected_php_version = tk.StringVar(self.master)
        self.selected_php_version.set(self.php_versions[0] if self.php_versions and self.php_versions[0] != "No PHP versions found" else "")

        php_label = ttk.Label(php_frame, text="Select PHP Version:")
        php_label.pack(side=tk.LEFT, padx=5)

        # Set state to 'readonly' only if there are actual versions to select
        dropdown_state = "readonly" if self.php_versions and self.php_versions[0] != "No PHP versions found" else "disabled"
        self.php_dropdown = ttk.Combobox(php_frame, textvariable=self.selected_php_version,
                                         values=self.php_versions, state=dropdown_state, width=15)
        self.php_dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Apache Control
        apache_frame = ttk.LabelFrame(main_frame, text="Apache Control", padding="10")
        apache_frame.pack(pady=10, fill=tk.X)

        self.apache_status_label = ttk.Label(apache_frame, text="Status: Unknown", style='Status.TLabel')
        self.apache_status_label.pack(pady=5)

        apache_buttons_frame = ttk.Frame(apache_frame)
        apache_buttons_frame.pack(pady=5)

        start_apache_btn = ttk.Button(apache_buttons_frame, text="Start Apache", command=self.start_apache)
        start_apache_btn.pack(side=tk.LEFT, padx=5)

        stop_apache_btn = ttk.Button(apache_buttons_frame, text="Stop Apache", command=self.stop_apache)
        stop_apache_btn.pack(side=tk.LEFT, padx=5)

        # MySQL Control
        mysql_frame = ttk.LabelFrame(main_frame, text="MySQL Control", padding="10")
        mysql_frame.pack(pady=10, fill=tk.X)

        self.mysql_status_label = ttk.Label(mysql_frame, text="Status: Unknown", style='Status.TLabel')
        self.mysql_status_label.pack(pady=5)

        mysql_buttons_frame = ttk.Frame(mysql_frame)
        mysql_buttons_frame.pack(pady=5)

        start_mysql_btn = ttk.Button(mysql_buttons_frame, text="Start MySQL", command=self.start_mysql)
        start_mysql_btn.pack(side=tk.LEFT, padx=5)

        stop_mysql_btn = ttk.Button(mysql_buttons_frame, text="Stop MySQL", command=self.stop_mysql)
        stop_mysql_btn.pack(side=tk.LEFT, padx=5)

        # Feedback Area
        self.feedback_label = ttk.Label(main_frame, text="Ready.", style='Feedback.TLabel', wraplength=400)
        self.feedback_label.pack(pady=10)

        # Refresh Button
        refresh_btn = ttk.Button(main_frame, text="Refresh Status", command=self.update_status)
        refresh_btn.pack(pady=10)

    def get_php_versions(self):
        """
        Scans the PHP base directory for folders like 'php81', 'php82'
        and verifies if 'php8apache2_4.dll' exists within them.
        """
        php_versions = []
        if os.path.exists(self.php_base_dir):
            for item in os.listdir(self.php_base_dir):
                php_version_path = os.path.join(self.php_base_dir, item)
                # Check if it's a directory and matches the phpXX pattern
                if os.path.isdir(php_version_path) and re.match(r"php\d{2}", item):
                    # Check for the presence of php8apache2_4.dll
                    php_dll_path = os.path.join(php_version_path, "php8apache2_4.dll")
                    if os.path.exists(php_dll_path):
                        php_versions.append(item)
                    else:
                        print(f"Skipping {item}: php8apache2_4.dll not found in {php_version_path}") # Debugging print
        php_versions.sort(key=lambda x: int(x[3:]), reverse=True) # Sort numerically, e.g., php83, php82, php81
        return php_versions

    def check_process_status(self, process_name):
        """Checks if a process is running using tasklist."""
        try:
            # Use 'tasklist /fi "imagename eq <process_name>"' to check for the process
            # and pipe to findstr /i to check for the process name in the output
            command = f'tasklist /fi "imagename eq {process_name}"'
            result = subprocess.run(command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return process_name.lower() in result.stdout.lower()
        except Exception as e:
            self.log_feedback(f"Error checking status for {process_name}: {e}", "red")
            return False
        
    def get_running_php_version(self):
        command = "php -v"  # Command to check PHP version
        try:
            # Run the command without creating a window (Windows only)
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                # Extract version (first line of output)
                version_line = stdout.decode('utf-8').split('(cli)')[0]
                return version_line.strip()
            else:
                return f"Error: {stderr.decode('utf-8').strip()}"
        except FileNotFoundError:
            return "PHP is not installed or not in PATH."
        
    def get_service_description(self, service_name):
        command = f'sc qdescription {service_name}'
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                # Extract the description (after "DESCRIPTION:")
                description = stdout.split("DESCRIPTION:", 1)[-1].strip()
                return description if description else "No description available."
            else:
                return f"Error: {stderr.strip() or 'Service not found.'}"
        except Exception as e:
            return f"Failed to query service: {e}"


    def update_status(self):
        """Updates the status labels for Apache and MySQL."""
        apache_running = self.check_process_status("httpd.exe")
        mysql_running = self.check_process_status("mysqld.exe")

        if apache_running:
            time.sleep(2)
            service = self.get_service_description("Apache24")
            self.apache_status_label.config(text="Status: Running " + service, foreground="green")
        else:
            self.apache_status_label.config(text="Status: Stopped", foreground="red")

        if mysql_running:
            self.mysql_status_label.config(text="Status: Running", foreground="green")
        else:
            self.mysql_status_label.config(text="Status: Stopped", foreground="red")

        self.log_feedback("Status refreshed.")

    def log_feedback(self, message, color="black"):
        """Displays feedback messages in the GUI."""
        self.feedback_label.config(text=message, foreground=color)
        self.master.update_idletasks() # Update GUI immediately

    def run_bat_script(self, script_path, args=""):
        """Executes a BAT script in a separate, hidden process."""
        if not os.path.exists(script_path):
            self.log_feedback(f"Error: Batch script not found: {script_path}", "red")
            messagebox.showerror("Script Error", f"The batch script was not found at:\n{script_path}\nPlease check your configuration paths.")
            return False

        try:
            command = f'"{script_path}" {args}'
            self.log_feedback(f"Executing: {command}")
            # Use Popen to run in background, shell=True to allow shell commands like 'start',
            # creationflags=subprocess.CREATE_NO_WINDOW to hide the console window.
            subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except Exception as e:
            self.log_feedback(f"Failed to execute {os.path.basename(script_path)}: {e}", "red")
            messagebox.showerror("Execution Error", f"Failed to execute {os.path.basename(script_path)}.\nError: {e}")
            return False

    def start_apache(self):
        """Starts Apache with the selected PHP version."""
        php_version = self.selected_php_version.get()
        if not php_version or php_version == "No PHP versions found":
            self.log_feedback("Please select a valid PHP version.", "orange")
            messagebox.showwarning("Selection Error", "Please select a valid PHP version before starting Apache.")
            return

        self.log_feedback(f"Attempting to start Apache with PHP {php_version}...")
        # The start_apache.bat expects the PHP version as an argument like --php83
        args = f'--{php_version}'
        if self.run_bat_script(self.bat_apache_start, args):
            # Give some time for the service to start
            threading.Thread(target=self._delayed_status_update, args=("Apache",)).start()

    def stop_apache(self):
        """Stops Apache."""
        self.log_feedback("Attempting to stop Apache...")
        if self.run_bat_script(self.bat_apache_stop):
            threading.Thread(target=self._delayed_status_update, args=("Apache",)).start()

    def start_mysql(self):
        """Starts MySQL."""
        self.log_feedback("Attempting to start MySQL...")
        if self.run_bat_script(self.bat_mysql_start):
            threading.Thread(target=self._delayed_status_update, args=("MySQL",)).start()

    def stop_mysql(self):
        """Stops MySQL."""
        self.log_feedback("Attempting to stop MySQL...")
        if self.run_bat_script(self.bat_mysql_stop):
            threading.Thread(target=self._delayed_status_update, args=("MySQL",)).start()

    def _delayed_status_update(self, service_name):
        """Helper to update status after a delay in a separate thread."""
        self.log_feedback(f"Waiting for {service_name} to update status...", "blue")
        time.sleep(3) # Wait for 3 seconds for the service to respond
        self.master.after(0, self.update_status) # Schedule update_status on the main thread
        self.log_feedback(f"{service_name} status updated.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceControlPanel(root)
    root.mainloop()
