# Email server configuration
DISABLE_SMTP = False  # Dry run
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587  # plain 25, tls 587, ssl 465
SMTP_SEC = 'tls'  # none, tls, ssl
# Check instructions when login as user with MFA enabled
SMTP_NOLOGIN = False
SMTP_USER = 'mymail@gmail.com'
SMTP_PASSWORD = 'base64'

# Email details
FROM_EMAIL = 'mymail@gmail.com'
TO_EMAILS = ['mymail@gmail.com']
EMAIL_SUBJECT = 'Subject of the email'
EMAIL_BODY = 'Body of the email'

# Command to execute
COMMAND = "echo 'this is a test'"
# Where to save (will overwrite)
FILE_PATH = '/tmp/command_alert.txt'
# Send the file as attachment or in the body?
AS_ATTACHMENT = False
# Next execution (in seconds)
SLEEP_INTERVAL = 60  # 0 = run once

def send_email_with_attachment():
    if DISABLE_SMTP:
        print("Email sending disabled. Content of the file and recipients:")
        with open(FILE_PATH, 'r') as file:
            print("File content:")
            print(file.read())
            f.close()
        return

    # Check if file is empty
    if os.path.getsize(FILE_PATH) <= 6:
        print("File content is empty." , "Not sending any notification.")
        return

    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = ', '.join(TO_EMAILS)
    msg['Subject'] = EMAIL_SUBJECT
    
    if AS_ATTACHMENT:    
        msg.attach(MIMEText(EMAIL_BODY, 'plain'))
        with open(FILE_PATH, 'rb') as file:
            attachment = MIMEApplication(file.read(), Name='attachment_name')
            attachment['Content-Disposition'] = 'attachment; filename="{}"'.format(FILE_PATH.split("/")[-1])
            msg.attach(attachment)
        file.close()
    else:             
        EMAIL_BODY2 = EMAIL_BODY + '\n'
        with open(FILE_PATH, 'r') as file:
            EMAIL_BODY2 += file.read()
        msg.attach(MIMEText(EMAIL_BODY2, 'plain'))
        file.close()
                
    try:
        print("Got content to send. Establishing connection to SMTP server:", SMTP_SERVER)
        socket.setdefaulttimeout(5)
        if SMTP_SEC == 'none':
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        elif SMTP_SEC == 'tls':
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
        elif SMTP_SEC == 'ssl':
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

        # Enable debugging
        server.set_debuglevel(0)

        if not SMTP_NOLOGIN:
            server.login(SMTP_USER, decode_base64(SMTP_PASSWORD))

        for EMAIL in TO_EMAILS:
            try:
                server.sendmail(FROM_EMAIL, EMAIL, msg.as_string())
            except Exception as e:
                print("Cannot send to:", EMAIL, e)

            server.rset()

        server.quit()

        print("Email sent to:", TO_EMAILS)
    except Exception as e:
        print("Error:", e)  # Print exception details


def execute_command_and_write_to_file():
    print("Executing command:", COMMAND)
    process = subprocess.Popen(COMMAND, shell=True, stdout=subprocess.PIPE)
    stdout, _ = process.communicate()
    if sys.version_info >= (3, 0):
        stdout_str = str(stdout,'utf-8').replace('\\n', '\n')
    else:
        stdout_str = str(stdout).replace('\\n', '\n')
    with open(FILE_PATH, 'w') as file:
        file.write(stdout_str)
        file.close()

def main():
    while True:        
        execute_command_and_write_to_file()
        send_email_with_attachment()
	if SLEEP_INTERVAL > 0:
           print("Sleeping for:", SLEEP_INTERVAL)
           time.sleep(SLEEP_INTERVAL)
        else:
           print("Only run once. Sleep interval is set to:", SLEEP_INTERVAL)
           return

if __name__ == "__main__":
    pid_file = '/var/run/command_alert.pid'
    if os.path.exists(pid_file):
        print("Daemon is already running.")
        sys.exit(1)

    pid = str(os.getpid())
    with open(pid_file, 'w') as f:
        f.write(pid)

    try:
        main()
    finally:
        os.unlink(pid_file)
