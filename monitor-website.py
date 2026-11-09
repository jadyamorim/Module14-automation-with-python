import requests
import smtplib
import os
import paramiko
import linode_api4
import time
import schedule

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
SSH_PASSPHRASE = os.environ.get('SSH_PASSPHRASE')
LINODE_TOKEN = os.environ.get('LINODE_TOKEN')
SSH_KEY_PATH = os.environ.get('SSH_KEY_PATH')
CONTAINER_ID = os.environ.get('CONTAINER_ID')

# send notification
def send_notification(email_msg):
    print('Sending an email...')
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        message = f"Subject: SITE DOWN\n{email_msg}!"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)

# restart linode server
def restart_server_and_container():
    print('Rebooting the server...')
    client = linode_api4.LinodeClient(LINODE_TOKEN)
    nginx_server = client.load(linode_api4.Instance, 109525143)
    nginx_server.reboot()

    # restart the application
    while True:
        nginx_server = client.load(linode_api4.Instance, 109525143)
        
        if nginx_server.status == 'running':
            time.sleep(5)
            restart_container()
            break

        # Stop waiting after 5 mins
        if time.time() - start_time > timeout:
            print('Server reboot timed out!')
            break

        time.sleep(5)

# restart linode container
def restart_container():
    print('Restarting the application...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname='172.238.33.252', 
        username='root', 
        key_filename=SSH_KEY_PATH, 
        passphrase=os.environ.get('SSH_PASSPHRASE')
    )
    stdin, stdout, stderr = ssh.exec_command(f'docker start {CONTAINER_ID}')
    print(stdout.readlines())
    ssh.close()

def monitor_application():
    try:
        # Add requests timeout
        response = requests.get(
            'http://172-238-33-252.ip.linodeusercontent.com:8080/',
            timeout=10         
        )
        if response.status_code == 200:
            print('Application is running successfully!')
        else:
            print('Application Down. Fix it!')
            msg = f'Application returned {response.status_code}'
            send_notification(msg)
            restart_container()
    except Exception as ex:
        print(f'Connection error happened: {ex}')
        msg = 'Application not accessible at all'
        send_notification(msg)
        restart_server_and_container()

# checks application status every 5 minutes
schedule.every(5).minute.do(monitor_application)

while True:
    schedule.run_pending()
    time.sleep(1)  # Prevent unnecessary CPU usage
