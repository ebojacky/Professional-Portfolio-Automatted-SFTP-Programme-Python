import logging
import os
import threading
import time
import paramiko
import shutil
import config  # Importing our configuration file
import tools  # Contains utility functions

def download_file(sftp, remote_path, local_path):
    local_path_temp = f"{local_path}.temp"
    try:
        sftp.get(remote_path, local_path_temp)
        shutil.move(local_path_temp, local_path)
        logging.info(f"Successfully downloaded file: {local_path}")
    except Exception as e:
        logging.error(f"Error during SFTP of file: {str(e)}")
        try:
            os.remove(local_path_temp)
        except Exception as remove_error:
            logging.error(f"Error removing temp file: {str(remove_error)}")

def process_files(sftp, remote_dir, local_dir, local_files):
    remote_files = sorted([f for f in sftp.listdir(remote_dir) if f.endswith(".gz")])
    for file in remote_files:
        if file not in local_files:
            remote_path = f"{remote_dir}/{file}"
            local_path = f"{local_dir}/{file}"
            download_file(sftp, remote_path, local_path)

def process_folders(sftp, folder_remote, dates):
    for date in dates:
        try:
            remote_dir = f"{config.CDR_PATH}/{folder_remote}/{date}"
            local_dir = f"{config.PATHS['CDR_PATH']}/{date}"

            ichp_tools.create_directories([local_dir])

            local_files = sorted([f for f in os.listdir(local_dir) if f.endswith(".gz")])
            
            process_files(sftp, remote_dir, local_dir, local_files)
        except Exception as e:
            logging.error(f"Error working on this date: {date} : {str(e)}")

def process_hosts(node):
    while True:
        try:
            logging.info(f"{node['name']} SFTP thread starting")
            dates = tools.get_recent_dates(config.SFTP_PERIOD_IN_DAYS)
            logging.info(f"{node['name']}: Scanning these date folders: {dates}")

            with paramiko.SSHClient() as ssh:
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                logging.info(f"About to connect to {node['name']}")
                ssh.connect(node["host"], username=node["user"], password=node["passwd"])
                logging.info(f"Successfully connected to {node['name']}")

                with ssh.open_sftp() as sftp:
                    remote_folders = [f for f in sftp.listdir(config.CDR_PATH) if f in config.POSSIBLE_FOLDERS]
                    for folder in remote_folders:
                        process_folders(sftp, folder, dates)

            logging.info(f"Successfully disconnected from {node['name']}")
        except Exception as e:
            logging.critical(f"Error with SFTP connection for host: {node['name']} : {str(e)}")
        time.sleep(config.SFTP_SLEEP_IN_SECONDS)


if __name__ == "__main__":
    while True:
        try:
            tools.create_directories(config.PATHS.values())
            tools.setup_logging("ichp_sftp.log")
            tools.write_paramiko_details()
            logging.info("Starting background tasks for SFTP")

            threads = []
            
            def create_thread(node):
                thread = threading.Thread(name=f'sftp_thread_{node["name"]}', target=process_hosts, args=(node,))
                threads.append(thread)
                thread.start()

            for sftp_host in config.SFTP_LIST:
                create_thread(sftp_host)
                logging.info(f"Successfully created SFTP thread for {sftp_host['name']}")
            
            
             while True:
                logging.info(f"Current SFTP threads: {threads}")
                try:
                    for sftp_thread in threads.copy():
                        if not sftp_thread.is_alive():
                            index = threads.index(sftp_thread)
                            name = sftp_thread.name.split("_")[-1]
                            host_to_recreate = next(host for host in config.SFTP_LIST if host['name'] == name)
                            create_thread(host_to_recreate)
                            threads.pop(index)
                            logging.info(f"Successfully re-created SFTP thread for {host_to_recreate['name']}")
                except Exception as e:
                    logging.critical(f"Error re-starting background thread: {str(e)}")

                time.sleep(config.SFTP_SLEEP_IN_SECONDS)

        except Exception as e:
            print(f"Base exception: {str(e)}")

        time.sleep(config.MAIN_LOOP_SLEEP_IN_SECONDS)
