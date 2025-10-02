# Troubleshooting SOC-Syslog Hardware

Context: What is SOC-Syslog? SOC-Syslog is a dedicated server in the SOC Network that serves as a central collection point for all linux based servers to ingest logs to. We use a protocol called RSyslog, an open-source software utility used on UNIX and Unix-like computer systems for forwarding log messages in an IP network. After logs are ingested to SOC-Syslog, an application called the Splunk Universal Forwarder, forwards all these logs to our Splunk Server for indexing.

Problem: The Security Operations Center was completing a routine search on logs being ingested to our Splunk Server. They noticed a decrease in logs being ingested daily. The SOC noticed on September 17, 2025 the Splunk Universal Forwarder stopped forwarding logs from SOC-Syslog to the Splunk Server. The SOC decided to remotely secure shell into the SOC-Syslog server to check if logs were being successfully sent from the nodes to SOC-Syslog. The SOC noticed they stopped forwarding logs on September 17, 2025. By the time the SOC realized there was ingestion issues on SOC Syslog it had been a few days since SOC-Syslog was essentially non-operational. The server was still online and essentially in a read-only state.

<insert picture of 0 logs on that day> 

In an attempt remediate the issue the SOC decided to do three things in an attempt to fix this issue in this order.

1. Running <code>systemctl restart rsyslog</code> in an attempt to restart the service in case RSyslog was the issue

2. Running <code> cd /opt/splunkforwarder/bin && ./splunk restart</code> in an attempt to restart the forwarding process from soc-syslog to the Splunk Server

3. Running <code>reboot</code> in an attempt restart the entire soc-syslog server.

It was at this time the SOC realized running <code>reboot</code> did not restart the server successfully. Due to the location difference between the SOC and Student Data Center (SDC) it was about 20 minutes until the SOC realized that SOC-Syslog was stuck in a boot loop.

In an attempt to break out of this boot loop, the SOC researched how to enter the Red Hat Enterprise Linux (RHEL) 9.5 Emergency Shell.

During the initial boot sequence, SOC edited the GRUB Loader that edited the following commands into the boot loader.
<code>removed: quiet rhgb
added: systemd.unit=multi-user.target</code>

This process allowed us to see all the system logs that were occurring on system startup, showcasing many services that failed to start. 

<insert picture of failed dbus blah>

But after entering the emergency shell, we were able to actually boot into operating system and run commands.

One of the most concerning commands we realized was <code>df -h</code> This displayed all the filesystems on the operating system and concerns immediately rised. The directory for the operating system (RHEL 9.5) was installed under /dev/mapper/rhel-root and with allocated space of 70GB only 20K was available. 

<insert picture of df -h with barely any space on above directory>

In the intial observation of figuring out what the machine was, we assumed this was actually reserved system space and not understanding this was the actual OS partition and it was full. 

Upon realization that this was the culprit, we scanned the directory to find what files were the largest on the operating system.

We noticed that a directory called /var/log contained more than half of the allotted storage of the entire OS partition (40+ GB)

Moreover, it was a specific file called /var/log/messages that was taking up all the space on the operating system partition which contains all the logs ingested from all our Linux based nodes in a single file.

If you noticed in the above photo we actually have a dedicated directory called /mnt/storage that was not being used at all.

In our attempt to get this soc-syslog back online, our solution was to run <code>mv /var/log/messages /mnt/Storage</code> which immediately relieved our storage issue on the rhel-root directory. We restarted the server immediately without our GRUB loader modification, services started once again and logs that were backlogged were being ingested to SOC-Syslog which then were being successfully forwarded to the Splunk Server.

