import socket
import sys
import os
import hashlib


def recv_line(sock):
    '''Receive data from the socket until a newline character is encountered.'''
    data = b""
    while True:
        part = sock.recv(1)
        if part == b'\n' or part == b'':
            break
        data += part
    return data.decode()


def compute_md5(file_path):
    '''Compute the MD5 hash of a file.'''
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def handle_download(client_socket, file_name):
    '''Handle a download request from the client.'''
    header = f"download {file_name}"
    offset = 0

    # If file exists, get its size and hash
    local_path = f"ClientShare/{file_name}"
    if os.path.exists(local_path):
        offset = os.path.getsize(local_path)
        local_hash = compute_md5(local_path)
        header += f" {local_hash} {offset}"

    header += "\n"
    client_socket.sendall(header.encode())

    response = recv_line(client_socket)

    if response == "NOT FOUND":
        print("The requested file was not found on the server.")
    elif response == "FILE_UNCHANGED":
        print(f"{file_name} is up-to-date.")
    elif response.startswith("OK"):
        _, size = response.split(maxsplit=1)
        size = int(size)
        with open(local_path, 'ab') as f:  # Open in append mode
            received_size = 0
            while received_size < size:
                data = client_socket.recv(4096)
                received_size += len(data)
                f.write(data)
        print(f"{file_name} has been downloaded successfully.")


def handle_upload(client_socket, file_name):
    local_path = f"ClientShare/{file_name}"
    
    if os.path.exists(local_path):
        file_hash = compute_md5(local_path)
        header = f"upload {file_name} {file_hash}\n"
        client_socket.sendall(header.encode())
        
    server_response = recv_line(client_socket)
    if server_response == "FILE_UNCHANGED":
        print(f"{file_name} is already up-to-date on the server.")
    elif server_response == "PROCEED_WITH_UPLOAD":
        print(f"Uploading {file_name}...")
        with open(local_path, 'rb') as f:
            chunk = f.read(4096)
            while chunk:
                client_socket.sendall(chunk)
                chunk = f.read(4096)
        print(f"{file_name} uploaded successfully!")
    else:
        print("Unexpected response from the server.")


def list_files(client_socket):
    header = "list_files\n"
    client_socket.sendall(header.encode())
    file_list = client_socket.recv(4096).decode()
    print("Shareable files:")
    print(file_list)


def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <command> [<filename> if needed]")
        sys.exit(1)

    command = sys.argv[1]

    if command not in ['l', 'd', 'u']:
        print("Unknown command.")
        sys.exit(1)

    file_name = sys.argv[2] if command != 'l' else None

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 80))

        if command == 'l':  # List all shareable files
          list_files(client_socket)

        elif command == 'd':  # Download file
            handle_download(client_socket, file_name)

        elif command == 'u':  # Upload file
            handle_upload(client_socket, file_name)
        else:
            print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
