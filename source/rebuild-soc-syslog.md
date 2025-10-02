# Rebuilding SOC-Syslog logging Infrastructure

Context: if you are reading this in a specific order, these events occur after we remediated the SOC-Syslog server not coming back online after rebooting it. The TLDR is that logs that were being sent from the other nodes were being stored on the OS Partition. When it eventually filled up, the OS refuse to write anymore data and essentially entered in a read-only state. We entered the emergency shell and moved the entire log file into another partition originally intended for where the logs should be stored. We restarted the server and everything came back online. If you can tell this solution was only temporary as all we did was move all the logs out of the OS partition and just wait before it filled back up.

So in this write-up we will document and showcase our processes of how we redesigned how logs are stored and saved on our server.

In the first attempt of the rebuild we wanted to simplify the process by editing the rsyslog.conf and changing this line

<code>
# Log anything (except mail) of level info or higher.
# Don't log private authentication messages!
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
</code>

<code>
# Log anything (except mail) of level info or higher.
# Don't log private authentication messages!
*.info;mail.none;authpriv.none;cron.none                /mnt/storage/splunk_logs/messages
</code>

In an attempt to just try and just port over all the files that were in the /var/log/. directory we ran cp -r /var/log/. into /mnt/storage/splunk_logs to try and mimic the entire directory incase there were any files necessary from /var/log that were necessary in this new directory.

What we didn't know at this time was how files are tagged in Linux in this exact event when files are just copied over. These tagged files and config change did not work as expected and broke the rsyslog process. 

It would be a few days until we realized how to disable this file tagging enforcement and make it easier move the files

<I am not sure how semanage/enforcement works dat was done by bill thanks bill >


After Bill fixed it, we were able to have all the logs forward to the new path /mnt/storage/splunk_logs/ which had a file in there called 'messages' and allowed us to save the logs in a partition with much more space and that is intended for storage. 

This was still more of a temporary fix as now all we did was offload the location of where logs are stored from rhel-root to /mnt/storage. Logs were still being aggregated into one file called messages where all the nodes aggregate into one file, messages.

<Forgot about ESXI Cluster>
<Forgot about Proxmox and our install instructions>
<Special Config to save new logs like below>

Ideally we wanted to have the logs placed in a directory style like /mnt/storage/new_rsyslog/hostname/uma.log

