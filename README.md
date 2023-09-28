# xFx Protocol

The \`xFx Protocol\` facilitates file operations between a client and server. This document outlines the supported operations and their corresponding communication structures.

## 1. Establishing a Connection

To initiate any action, the client must first establish a connection with the server. Once connected, the client sends a *header* to inform the server about the intended operation.

## 2. Operations

### 2.1. List Files

When the client wishes to view all shareable files on the server:

- **Client Header:**

`list_files\n`

- **Server Response:**
The server replies with the names of all shareable files in the ServerShare directory:
`[file1 name]\n [file2 name]\n ...`


### 2.2. Download

To download a file, the client sends the following:

- **Client Header:**

`download [file name] [MD5 hash (optional)] [offset (optional)]\n`

- **Server Responses:**

  - If the file is not found:
    `NOT FOUND\n`
  - If the file is found and the MD5 hash matches (no changes since the last check):
    `FILE_UNCHANGED\n`
  - If the file is found but either there's no MD5 hash or the hash differs:
    `OK [file size]\n`
    This is followed by the bytes of the file, starting from the optional offset (if provided).

### 2.3. Upload

To upload a file:

- **Client Header:**
`upload [file name] [MD5 hash]\n`

- **Server Responses:**

  - If the uploaded file's hash matches an existing file on the server:
    `FILE_UNCHANGED\n`
  - If the file doesn't match or doesn't exist on the server:
    `PROCEED_WITH_UPLOAD\n`

  After receiving `PROCEED_WITH_UPLOAD\n`, the client sends the bytes of the file. The server successfully receives and saves the file and logs the event. No confirmation is sent to the client.
