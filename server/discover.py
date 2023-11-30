import os
import sys

# List filenames from host named hostname
def discover(hostname):
    files = os.listdir("peers/" + hostname)
    print(files)
    return files

def main():
    # Syntax check
    if len(sys.argv) != 2:
        print("Usage: python discover.py hostname")
        return
        
    # Get hostname (address) from argument | [0] is ALWAYS script name
    hostname = sys.argv[1]

    # Call discover function
    discover(hostname)

if __name__ == '__main__':
    main()
