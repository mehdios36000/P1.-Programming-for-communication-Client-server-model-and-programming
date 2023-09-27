# xFx Protocol

The client establishes a connection with the server and *informs* the server about the intended action, which could be *list_files*, *download*, or *upload* a file using a *header*.

## List Files

If the client wants to list all shareable files on the server:
- **Header sent from the client:**
  - `list_files\n`

Upon receiving this header, the server responds with the names of all shareable files in the ServerShare directory.
- **Response from the server:**
  - `[file1 name]\n[file2 name]\n...`

## Download

If the client wants to download a file, then the header will be:
- `download [file name] [MD5 hash (optional)] [offset (optional)]\n`

Upon receiving this header, the server searches for the specified file:
- If the file is not found, then the server replies with:
  - **Response from the server:**
    - `NOT FOUND\n`
- If the file is found and the MD5 hash matches (indicating no changes since the last check), then the server replies with:
  - **Response from the server:**
    - `FILE_UNCHANGED\n`
- If the file is found and either there's no MD5 hash or the MD5 hash is different, the server replies:
  - **Response from the server:**
    - `OK [file size]\n`
  - followed by the bytes of the file starting from the optional offset (if provided).

## Upload

If the client wants to upload a file, then the header will be:
- `upload [file name] [file size]\n`

After sending the header, the client sends the bytes of the file.

Upon successfully receiving and saving the file, the server logs that the file has been uploaded successfully from the client's address but does not send a confirmation to the client.
