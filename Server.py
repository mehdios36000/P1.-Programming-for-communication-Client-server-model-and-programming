import socket
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


def handle_download(conn, args):
    print("Handling download")
    parts = args[0].split()
    file_name = parts[0]
    client_hash = parts[1] if len(parts) > 1 else None
    offset = int(parts[2]) if len(parts) > 2 else 0
    file_path = f"ServerShare/{file_name}"

    if os.path.exists(file_path):
        print("File exists")
        server_hash = compute_md5(file_path)
        if client_hash == server_hash:
            conn.sendall(b"FILE_UNCHANGED\n")
            return

        with open(file_path, 'rb') as f:
            print("Sending file from offset", offset)
            f.seek(offset)  # Start from the client's offset

            # Get the size to be sent
            remaining_size = os.path.getsize(file_path) - offset
            response = f"OK {remaining_size}\n"
            conn.sendall(response.encode())

            # Send the file in chunks
            chunk_size = 4096
            while remaining_size > 0:
                data = f.read(min(chunk_size, remaining_size))
                conn.sendall(data)
                remaining_size -= len(data)
    else:
        print("File does not exist")
        error_message = "NOT FOUND\n"
        conn.sendall(error_message.encode())



def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('localhost', 80))
        server_socket.listen()

        while True:
            print("Server waiting...")
            conn, addr = server_socket.accept()

            with conn:
                print(f"Server got a connection from {addr}")

                header = recv_line(conn)
                command, *args = header.split(maxsplit=1)

                if command == "download":
                    handle_download(conn, args)

                elif command == "upload":
                    file_name, size = args[0].split(maxsplit=1)
                    size = int(size)
                    file_data = conn.recv(size)
                    with open(f"ServerShare/{file_name}", 'wb') as f:
                        f.write(file_data)
                    print(f"File {file_name} uploaded successfully from {addr}")

                elif command == "list_files":
                    files = os.listdir("ServerShare")
                    response = "\n".join(files) + "\n"
                    conn.sendall(response.encode())

                else:
                    print("Connection got from an incompatible client")

if __name__ == "__main__":
    main()
