#!/usr/bin/env python3
"""
PDF GPT Health Check Script
Monitors the health of all services
"""

import requests
import sys
import time
from datetime import datetime

def check_service(name, url, timeout=10):
    """Check if a service is healthy"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: Healthy")
            return True
        else:
            print(f"❌ {name}: Error (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Unreachable ({e})")
        return False

def main():
    """Main health check function"""
    print(f"🏥 PDF GPT Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    services = [
        ("Backend API", "http://localhost:5000/health"),
        ("Frontend", "http://localhost:8501"),
        ("Ollama", "http://localhost:11434/api/tags"),
        ("Nginx Proxy", "http://localhost:80/health"),
    ]
    
    healthy_services = 0
    total_services = len(services)
    
    for name, url in services:
        if check_service(name, url):
            healthy_services += 1
        time.sleep(1)  # Small delay between checks
    
    print("-" * 50)
    print(f"📊 Summary: {healthy_services}/{total_services} services healthy")
    
    if healthy_services == total_services:
        print("🎉 All systems operational!")
        sys.exit(0)
    else:
        print("⚠️ Some services need attention")
        sys.exit(1)

if __name__ == "__main__":
    main()
