#!/usr/bin/env python3
"""
Script to start Celery worker for DerivWorkFlow automation
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

def start_worker(queue_names=None, loglevel="info"):
    """Start Celery worker"""
    
    # Default queues if none specified
    if not queue_names:
        queue_names = [
            "market_scan",
            "position_monitor", 
            "trading",
            "risk_monitor",
            "signals",
            "training",
            "analysis"
        ]
    
    # Build celery command
    cmd = [
        "celery",
        "-A", "app.workers.celery_app",
        "worker",
        "--loglevel", loglevel,
        "--queues", ",".join(queue_names)
    ]
    
    print(f"Starting Celery worker with queues: {', '.join(queue_names)}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        # Set environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(app_dir)
        
        # Start worker
        subprocess.run(cmd, cwd=app_dir, env=env, check=True)
        
    except KeyboardInterrupt:
        print("\nShutting down worker...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting worker: {e}")
        sys.exit(1)


def start_beat(loglevel="info"):
    """Start Celery beat scheduler"""
    
    cmd = [
        "celery",
        "-A", "app.workers.celery_app", 
        "beat",
        "--loglevel", loglevel
    ]
    
    print("Starting Celery beat scheduler")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        # Set environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(app_dir)
        
        # Start beat
        subprocess.run(cmd, cwd=app_dir, env=env, check=True)
        
    except KeyboardInterrupt:
        print("\nShutting down beat scheduler...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting beat: {e}")
        sys.exit(1)


def start_flower(port=5555):
    """Start Celery Flower monitoring"""
    
    cmd = [
        "celery",
        "-A", "app.workers.celery_app",
        "flower",
        "--port", str(port)
    ]
    
    print(f"Starting Celery Flower on port {port}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        # Set environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(app_dir)
        
        # Start flower
        subprocess.run(cmd, cwd=app_dir, env=env, check=True)
        
    except KeyboardInterrupt:
        print("\nShutting down Flower...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting Flower: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start DerivWorkFlow background workers")
    parser.add_argument(
        "component", 
        choices=["worker", "beat", "flower"],
        help="Component to start"
    )
    parser.add_argument(
        "--queues",
        nargs="+",
        help="Queue names for worker (space separated)"
    )
    parser.add_argument(
        "--loglevel",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5555,
        help="Port for Flower (default: 5555)"
    )
    
    args = parser.parse_args()
    
    if args.component == "worker":
        start_worker(args.queues, args.loglevel)
    elif args.component == "beat":
        start_beat(args.loglevel)
    elif args.component == "flower":
        start_flower(args.port)
