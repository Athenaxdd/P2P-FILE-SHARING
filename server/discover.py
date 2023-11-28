import sys

# List published filenames from host named hostname
def discover(hostname):
    files = []
    with open("peers/" + hostname, "r") as f:
        while True:
            data = f.readline()

            #end of file
            if len(data) == 0:
                break
            files.append(data.split(' | ')[1])
    data = "".join(files)
    print(data)
    return data

def main():
    # Syntax check
    if len(sys.argv) != 2:
        print("Usage: python discover.py hostname")
        
    # Get hostname (address) from argument | [0] is ALWAYS script name
    hostname = sys.argv[1]

    # Call discover function
    discover(hostname)



if __name__ == '__main__':
    main()