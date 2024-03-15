# Command alert script
A simple Python script to execute a command, and its contents send via email (when not empty).\
It can be used as a "run once" by setting the SLEEP_INTERVAL to 0, and also be executed with a cronjob. Otherwise, you can create it as a service. See command_alert.service file as example.

This script was tested for Python 2.7, in order to be used in legacy and newer OS, and it should work for Python 3.0+.
