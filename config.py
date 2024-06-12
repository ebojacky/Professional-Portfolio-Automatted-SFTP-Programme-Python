# config.py

CDR_PATH = "/remote/path/to/cdr"
SFTP_PERIOD_IN_DAYS = 7
SFTP_SLEEP_IN_SECONDS = 3600
MAIN_LOOP_SLEEP_IN_SECONDS = 600

PATHS = {
    "CDR_PATH": "/local/path/to/storage",
}

POSSIBLE_FOLDERS = ["folder1", "folder2"]

SFTP_LIST = [
    {
        "name": "host1",
        "host": "10.2.3.5",
        "user": "username",
        "passwd": "password"
    }
    {
        "name": "host2",
        "host": "10.2.3.4",
        "user": "username",
        "passwd": "password"
    }

]
