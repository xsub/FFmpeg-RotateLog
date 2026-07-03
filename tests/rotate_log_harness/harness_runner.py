#!/usr/bin/env python3
import subprocess
import os
import glob
import time
import argparse

def run_ffmpeg(args, log_env=None):
    env = os.environ.copy()
    if log_env:
        env.update(log_env)
    
    cmd = ["../../ffmpeg"] + args
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result

def test_filesize_limit():
    print("=== Testing filesize limit ===")
    os.makedirs("test_logs", exist_ok=True)
    for f in glob.glob("test_logs/*.log"):
        os.remove(f)

    # We need a long enough process with enough logs.
    env = {"FFREPORT": "file=test_logs/ffreport-%p-%t.log:level=48"} 

    args = [
        "-rotate_log", 
        "-rotate_on_filesize_limit", "1000",
        "-f", "lavfi", "-i", "testsrc=duration=5", 
        "-f", "null", "-"
    ]
    
    run_ffmpeg(args, env)
    
    logs = glob.glob("test_logs/*.log")
    print(f"Generated {len(logs)} logs.")
    success = False
    for log in logs:
        size = os.path.getsize(log)
        print(f" - {log}: {size} bytes")
        if size > 11000:
            print(f"FAIL: Log file {log} exceeded limit by a lot!")
            return False
            
    if len(logs) > 1:
        print("SUCCESS: Log rotation by size works.")
        success = True
    else:
        print("FAIL: No rotation occurred. Maybe limit is too high or logs are too few.")
        success = False
    return success

def test_period_limit():
    print("=== Testing period limit ===")
    os.makedirs("test_logs", exist_ok=True)
    for f in glob.glob("test_logs/*.log"):
        os.remove(f)

    env = {"FFREPORT": "file=test_logs/ffreport-%p-%t.log:level=48"}

    # Use -re so it processes in real-time
    args = [
        "-re",
        "-rotate_log", 
        "-rotate_by_period", "2",
        "-f", "lavfi", "-i", "testsrc=duration=6", 
        "-f", "null", "-"
    ]
    
    run_ffmpeg(args, env)
    
    logs = glob.glob("test_logs/*.log")
    print(f"Generated {len(logs)} logs.")
    if len(logs) >= 3:
        print("SUCCESS: Log rotation by period works.")
        return True
    else:
        print("FAIL: Expected at least 3 log files.")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
    s1 = test_filesize_limit()
    print("")
    s2 = test_period_limit()
    
    if not (s1 and s2):
        exit(1)
