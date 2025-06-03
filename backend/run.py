import subprocess
import sys
import os
import signal
import time

def run_servers():
    # Get the current directory (now in backend folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths to both backend scripts
    main_py = os.path.join(current_dir, "main.py")  # main.py is now in the same directory
    app_py = os.path.join(current_dir, "api", "app.py")  # Updated path to app.py
    
    # Start both servers
    try:
        # Start main.py (Legal Help backend)
        main_process = subprocess.Popen([sys.executable, main_py],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      text=True,
                                      bufsize=1,
                                      universal_newlines=True)
        
        # Start app.py (Government Schemes backend)
        app_process = subprocess.Popen([sys.executable, app_py],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True,
                                     bufsize=1,
                                     universal_newlines=True)
        
        print("Starting both backend servers...")
        print("Legal Help backend running on http://localhost:8000")
        print("Government Schemes backend running on http://localhost:5000")
        print("\nPress Ctrl+C to stop both servers")
        
        # Keep the script running and handle output
        while True:
            # Print output from main.py
            main_output = main_process.stdout.readline()
            if main_output:
                print(f"[Legal Help] {main_output.strip()}")
            
            # Print output from app.py
            app_output = app_process.stdout.readline()
            if app_output:
                print(f"[Govt Schemes] {app_output.strip()}")
            
            # Print errors from both processes
            main_error = main_process.stderr.readline()
            if main_error:
                print(f"[Legal Help Error] {main_error.strip()}")
            
            app_error = app_process.stderr.readline()
            if app_error:
                print(f"[Govt Schemes Error] {app_error.strip()}")
            
            # Check if either process has ended
            if main_process.poll() is not None:
                print("\nLegal Help backend stopped unexpectedly!")
                print("Error output:")
                print(main_process.stderr.read())
                break
                
            if app_process.poll() is not None:
                print("\nGovernment Schemes backend stopped unexpectedly!")
                print("Error output:")
                print(app_process.stderr.read())
                break
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping both servers...")
        # Send SIGTERM to both processes
        main_process.terminate()
        app_process.terminate()
        
        # Wait for processes to terminate
        main_process.wait()
        app_process.wait()
        print("Servers stopped successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Clean up processes if they're still running
        if main_process.poll() is None:
            main_process.terminate()
        if app_process.poll() is None:
            app_process.terminate()

if __name__ == "__main__":
    run_servers() 