# File Processor & Flask API Documentation

This document provides a complete manual for your codebase—including file processing, Flask API setup, and integration suggestions. It contains instructions, code samples, and configuration guidelines to help you set up, run, and maintain the project.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [File Processing](#file-processing)
    - [TXT Files](#txt-files)
    - [PDF Files](#pdf-files)
    - [Image Files](#image-files)
  - [Flask API](#flask-api)
  - [Bulk Upload](#bulk-upload)
- [NGINX Configuration](#nginx-configuration)
  - [Installing NGINX](#installing-nginx)
  - [Starting and Stopping NGINX](#starting-and-stopping-nginx)
  - [Modifying the Configuration File](#modifying-the-configuration-file)
  - [Common NGINX Commands](#common-nginx-commands)
- [Commands Summary](#commands-summary)
- [Database Setup](#database-setup)
- [Suggestions and Use Cases](#suggestions-and-use-cases)
- [License](#license)

---

## Overview

This project includes a multi-functional system that processes files and provides a Flask API for file uploads and retrieval. It is divided into two main parts:

1. **File Processing**:  
   - Splits files from a source folder (`data/`) into TXT, PDF, and image categories.
   - **TXT Files** are tokenized using GPT-2's tokenizer and converted to `.bin` files.
   - **PDF Files** are optimized and compressed (using Ghostscript and Zstandard) into `.bin` files.
   - **Image Files** are converted to the WebP format.
   - **Important:** Only the converted files (the `.bin` or `.webp` files) are copied to the `uploads/` folder. Neither the original files nor the restored files are copied.

2. **Flask API**:  
   Provides endpoints to:
   - Upload files (storing the file in the `uploads/` folder and its path in a MySQL database).
   - Retrieve the URL for a specific file using its `user_id`.
   - List all uploaded files.
   - Serve individual files from the `uploads/` folder.

In production, you can run the API with a WSGI server (like Waitress) behind an NGINX reverse proxy.

---

## Features

- **File Processing**  
  - TXT: Tokenization and conversion to `.bin`.
  - PDF: Ghostscript-based optimization and compression to `.bin`.
  - Images: Conversion to WebP.
  - **Only converted files** are moved to the `uploads/` folder.

- **Flask API**  
  - File upload endpoint (`/upload`) that saves files and stores paths in MySQL.
  - File retrieval endpoint (`/file/<user_id>`) that returns the file URL.
  - File serving endpoint (`/uploads/<filename>`) that serves the file.
  - File listing endpoint (`/uploads`) that lists all uploaded files.

- **NGINX Integration**  
  - Configurable reverse proxy to forward requests to your Flask API.
  - Ability to modify NGINX's configuration file (`nginx.conf`) to suit your deployment needs.

---

## Requirements

- Python 3.x
- Flask
- mysql-connector-python
- waitress (or an alternative WSGI server like Gunicorn)
- MySQL Server
- Ghostscript (ensure the path is correct in the code)
- zstandard
- msgpack
- tiktoken
- numpy
- Pillow (PIL)
- tqdm
- NGINX

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository_url>
   cd <repository_directory>

# NGINX Configuration

NGINX is used as a reverse proxy to forward requests to the Flask API running on port 5000 (via Waitress). It is a powerful web server that can also function as a load balancer and HTTP cache.

## Installing NGINX

Download NGINX from the official website: [NGINX Download](http://nginx.org/en/download.html). Choose the version suitable for your operating system.

### For Linux (Ubuntu):

1. **Update the package list:**

    ```bash
    sudo apt-get update
    ```

2. **Install NGINX:**

    ```bash
    sudo apt-get install nginx
    ```

### For Windows:

- Download the Windows version from the [NGINX download page](http://nginx.org/en/download.html).
- Extract the zip file to a directory, e.g., `C:\nginx`.
- NGINX is now installed and ready to run from the extracted directory.

## Starting and Stopping NGINX

### On Linux:

- **Start NGINX:**

    ```bash
    sudo systemctl start nginx
    ```

- **Stop NGINX:**

    ```bash
    sudo systemctl stop nginx
    ```

- **Restart NGINX:**

    ```bash
    sudo systemctl restart nginx
    ```

- **Enable NGINX to start on boot:**

    ```bash
    sudo systemctl enable nginx
    ```

### On Windows:

1. **Navigate to the NGINX directory:**

    ```cmd
    cd C:\nginx
    ```

2. **Start NGINX:**

    ```cmd
    start nginx
    ```

3. **Stop NGINX:**

    ```cmd
    nginx -s stop
    ```

4. **Reload NGINX:**

    ```cmd
    nginx -s reload
    ```

## Modifying the Configuration File

The main NGINX configuration file is `nginx.conf`. Its location depends on your operating system:

- **Linux:** Typically found at `/etc/nginx/nginx.conf`.
- **Windows:** Located in the `conf` directory, e.g., `C:\nginx\conf\nginx.conf`.

To configure NGINX as a reverse proxy for the Flask API:

1. Open `nginx.conf` in a text editor (e.g., `nano` on Linux or Notepad on Windows).
2. Add or edit the following configuration:

    ```text
    server {
        listen 80;
        server_name your_domain.com;

        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
    ```

    - **listen 80:** NGINX listens on port 80.
    - **server_name:** Replace `your_domain.com` with your domain or IP address.
    - **proxy_pass:** Forwards requests to the Flask app running on `127.0.0.1:5000`.

3. Save the file.
4. Test the configuration for syntax errors:

    - **Linux:**

        ```bash
        sudo nginx -t
        ```

    - **Windows:**

        ```cmd
        nginx -t
        ```

5. If the test passes, reload NGINX to apply changes:

    - **Linux:**

        ```bash
        sudo nginx -s reload
        ```

    - **Windows:**

        ```cmd
        nginx -s reload
        ```

## Common NGINX Commands

- **Test configuration syntax:**

    ```bash
    nginx -t
    ```

- **Reload configuration without downtime:**

    ```bash
    nginx -s reload
    ```

- **Stop NGINX immediately:**

    ```bash
    nginx -s stop
    ```

- **Gracefully shut down NGINX:**

    ```bash
    nginx -s quit
    ```

- **Check NGINX version:**

    ```bash
    nginx -v
    ```

- **View compile-time options:**

    ```bash
    nginx -V
    ```

For more details, refer to the [NGINX Documentation](http://nginx.org/en/docs/).

## Commands Summary

- **Process Files:** `python process_files.py`
- **Run Flask API:** `waitress-serve --port=5000 app:app`
- **NGINX Commands:** See above.

## Database Setup

See the **Database Setup** section under Installation for instructions.

## Suggestions and Use Cases

- **Use Case 1:** Automate file processing and API deployment in a production environment.
- **Use Case 2:** Integrate with a frontend to allow users to upload and retrieve files.
- **Suggestion:** Use environment variables for sensitive information like database credentials.



**All rights reserved by Magentabits(C) 2025**   

**conatct: tahmeedtoqi123@gmail.com**