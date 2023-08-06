# Download Medisch Contact and convert to EPUB

> A command line tool and lib to download Medisch Contact and convert to EPUB

## Introduction

[Medisch Contact](https://www.medischcontact.nl/) is a Dutch magazine for medical doctors.

This package provides a Python libary and command line tool for convenient downloading of the online contents to EPUB files.

* Free software: MIT license


## Installation

If you have Python on your system you can do the usual:

    $ pip install medisch-contact-downloader


## Quickstart

### Command line usage examples

List all issues in the current year. For listing only, no authentication is required.

    $ medisch-contact-downloader -l

List all issues in the years 2002, 2004, 2006, 2007, and 2008:

    $ medisch-contact-downloader -l -y 2002 2004 2006-2008

Download the latest issue to the default download-directory. For downloading, a username and password is required for authentication.

    $ medisch-contact-downloader -u username -p password -d


Download the issues with the IDs 2022-4 and 2022-5 to the ~/Downloads download-directory. An ID is composed of the year and number of the issue.

    $ medisch-contact-downloader -u username -p password -d -i 2022-4 2022-5 -w ~/Downloads

Email the latest issue:

    $ medisch-contact-downloader -e -u username -p password --smtp_host smtp.example.com --smtp_port 587 --smtp_username user@example.com --smtp_password <password> --sender user@example.com --recipient info@example.com

Show command line help::

    $ medisch-contact-downloader -h


## Configuration File

The configuration file `config.ini` can change the default values for command line options. It should be written using a standard INI style. The keys should be grouped into sections. For now, the name of the sections are ignored. The section name appears on a line by itself, in square brackets ([ and ]). Configuration files may include comments, prefixed by # or ;. Comments may appear on their own on an otherwise empty line, possibly indented.


### Location

The `config.ini` configuration file should be put in the default config directory. This location is different on different operating systems. A custom configuration file can be provided with the `--config` argument.

* Linux: `$HOME/.config/medisch-contact-downloader/config.ini`, which respects the `XDG_CONFIG_HOME` environment variable.

* MacOS: `$HOME/Library/Application Support/medisch-contact-downloader/config.ini`

* Windows: `%APPDATA%\medisch-contact-downloader\config.ini`


### Precedence / Override order

Command line options override the values in a configuration file.

### Example `config.ini`

```
; This is a comment
# This is another comment
[settings]  ; a section marker is required in INI files
verbose = True
download_dir = /home/folkert/Downloads
username = <username>  ; username for authentication with https://www.medischcontact.nl/
password = <password>  ; password
smtp_host = smtp.example.com  ; host name or ip address of the SMTP server
smtp_port = 587  ; port of the SMTP server
smtp_username = user@example.com  ; accountname, username, or email address of your email account for authentication
smtp_password = <password>  ; password of your email account for authentication.
sender = user@example.com
recipient = info@example.com
```


## Download

When an issue is downloaded, it is copied to the default download directory. This location is different on different operating systems. A custom download directory can be provided with the `--download_dir` argument.

### Location
* macOS: `~/Library/Application Support/medisch-contact-downloader`

* Windows: `%APPDATA%\medisch-contact-downloader`

* Linux (and other Unices): `~/.local/share/medisch-contact-downloader`


## Email

You can send an automated email message with the downloaded Epub as an attachment, for example to [send it to your Kindle](https://www.amazon.com/gp/sendtokindle/email). To use this feature, the `--email` argument should be provided to the command line tool, along with the required arguments: `--smtp_host`, `--smtp_port`, `--smtp_username`, `--smtp_password`, `--sender`, and `--recipient`. This option presumes the `--download` argument.

Please note that if you use 2-step-verification in a Gmail-account, you might need an App Password (see https://support.google.com/accounts/answer/185833)


## Changelog

### [0.2.4] - 2022-08-01
- Fix handling of subject and body arguments

### [0.2.3] - 2022-08-01
- Fix arguments
- Correct Windows default download directory in README

### [0.2.2] - 2022-08-01
- Implement CSRF protection of changed login page

### [0.2.1] - 2022-02-24
- Ensure unique filename by adding id

### [0.2] - 2022-02-23
-  Bugfixes

### [0.1.0] - 2022-02-21
-  First release on PyPI.


## Author
- Folkert van der Beek - https://gitlab.com/fvdbeek
