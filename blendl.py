#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

if __name__ != "__main__":
    quit("Do not import this file.")
import requests
from dotenv import load_dotenv
import os
from sys import exit
from tqdm import tqdm


# Colors
class colors:
    reset = "\033[0m"
    bold = "\033[01m"
    disable = "\033[02m"
    underline = "\033[04m"
    reverse = "\033[07m"
    strikethrough = "\033[09m"
    invisible = "\033[08m"

    class fg:
        black = "\033[30m"
        red = "\033[31m"
        green = "\033[32m"
        orange = "\033[33m"
        blue = "\033[34m"
        purple = "\033[35m"
        cyan = "\033[36m"
        lightgrey = "\033[37m"
        darkgrey = "\033[90m"
        lightred = "\033[91m"
        lightgreen = "\033[92m"
        yellow = "\033[93m"
        lightblue = "\033[94m"
        pink = "\033[95m"
        lightcyan = "\033[96m"
        white = "\033[39m"

    class bg:
        black = "\033[40m"
        red = "\033[41m"
        green = "\033[42m"
        orange = "\033[43m"
        blue = "\033[44m"
        purple = "\033[45m"
        cyan = "\033[46m"
        lightgrey = "\033[47m"


fg = colors.fg()
bg = colors.bg()

remote = "https://git.blendos.co/api/v4/projects/32/jobs/artifacts/main/raw/blendOS.iso?job=build-job"
version = "https://git.blendos.co/api/v4/projects/32/jobs/artifacts/main/raw/version?job=build-job"

load_dotenv()
local_iso = str(os.getenv("LOCAL_ISO_FILE"))
local_version = str(os.getenv("LOCAL_VERSION_FILE"))


def critical():
    """Function to display the critical error message and exit."""
    print(
        colors.bold + fg.red + "\nCritical error detected, quitting..." + colors.reset
    )
    exit(1)


# Initial checks
def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        # For Windows, we can use a different method
        import ctypes

        return ctypes.windll.shell32.IsUserAnAdmin()


if is_admin():
    print(
        colors.bold
        + fg.red
        + ">> e:"
        + fg.white
        + " Do not run this script as admin."
        + colors.reset
    )

if local_iso == None:
    print(
        colors.bold
        + fg.red
        + ">> e:"
        + fg.green
        + " LOCAL_ISO_FILE "
        + fg.white
        + "is empty! Please specify this value in your .env file!"
        + colors.reset
    )
    critical()

if local_version == None:
    print(
        colors.bold
        + fg.red
        + ">> e:"
        + fg.green
        + " LOCAL_VERSION_FILE "
        + fg.white
        + "is empty! Please specify this value in your .env file!"
        + colors.reset
    )
    critical()

if os.path.isfile(local_iso) == False:
    print(
        colors.bold
        + fg.red
        + ">> e:"
        + fg.green
        + " LOCAL_ISO_FILE "
        + fg.white
        + "is not a path to a file!"
        + colors.reset
    )
    critical()

if os.path.isfile(local_version) == False:
    print(
        colors.bold
        + fg.red
        + ">> e:"
        + fg.green
        + " LOCAL_VERSION_FILE "
        + fg.white
        + "is not a path to a file!"
        + colors.reset
    )
    critical()

if os.access(local_iso, os.W_OK) == False:
    print(
        colors.bold
        + fg.red
        + ">> e:"
        + fg.white
        + " Cannot write to local ISO file! Please verify this user has write permissions."
    )
    critical()

if os.access(local_version, os.W_OK) == False:
    print(
        colors.bold
        + fg.red
        + ">> e:"
        + fg.white
        + " Cannot write to local version file! Please verify this user has write permissions."
    )
    critical()


def download_iso():
    global remote
    global local_iso
    try:
        response = requests.get(remote, stream=True)
    except requests.exceptions.RequestException as e:
        print(
            colors.bold
            + fg.red
            + ">> e:"
            + fg.white
            + f" Connection failed: {e}"
            + colors.reset
        )
        critical()

    # Check if the status code is 200 (OK)
    if response.status_code != 200:
        print(
            colors.bold
            + fg.red
            + ">> e:"
            + fg.white
            + f" Remote gave a {response.status_code} response"
            + colors.reset
        )
        exit(1)  # Exit the program with a non-zero status code
    else:
        os.remove(local_iso)

    # Get the total file size from the response headers
    total_size = int(response.headers.get("content-length", 0))

    # Create a progress bar using tqdm
    with (
        open(local_iso, "wb") as file,
        tqdm(
            desc="blendOS.iso",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            leave=True,
        ) as bar,
    ):
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
            bar.update(len(data))  # Update the progress bar

    print(
        colors.bold
        + fg.green
        + ">> s:"
        + fg.white
        + " ISO download success!"
        + colors.reset
    )


def download_version():
    global version
    global local_version

    try:
        response = requests.get(version, stream=True)
    except requests.exceptions.RequestException as e:
        print(
            colors.bold
            + fg.red
            + ">> e:"
            + fg.white
            + f" Connection failed: {e}"
            + colors.reset
        )
        critical()
    
    # Check if the status code is 200 (OK)
    if response.status_code != 200:
        print(
            colors.bold
            + fg.red
            + ">> e:"
            + fg.white
            + f" Remote gave a {response.status_code} response"
            + colors.reset
        )
        exit(1)  # Exit the program with a non-zero status code
    
    content = str(response.text)
    with open(local_version, "rb") as f:
        existing = f.read()
        existing2 = str(existing.decode())
    
    if content != existing2:
        print(
            colors.bold
            + fg.lightblue
            + ">> i:"
            + fg.white
            + " Version file is out of date! Updating..."
            + colors.reset
        )

        with open(local_version, "wb") as f:
            content2 = content.encode()
            f.write(content2)
        print(
            colors.bold
            + fg.green
            + ">> s:"
            + fg.white
            + " Version download success!"
            + colors.reset
        )

    else:
        print(
            colors.bold
            + fg.lightblue
            + ">> i:"
            + fg.white
            + " Version files match, ISO is up to date."
            + colors.reset
        )

        exit(0)


download_version()
download_iso()