# Troubleshooting SOC-Syslog Hardware

## Context: What is SOC-Syslog?

SOC-Syslog is a dedicated server in the SOC Network serving as the central collection point for logs from all of our Linux-based servers. We use RSyslog, an open-source program for UNIX and Unix-like computer systems, to forward log messages in our IP network. After logs are ingested to SOC-Syslog, an application called the Splunk Universal Forwarder forwards all these logs to our Splunk Server for indexing.

## Problem Description

The Security Operations Center was completing a routine search on logs being ingested to our Splunk Server. We noticed a decrease in the number of daily ingested logs. The SOC discovered that on **September 17, 2025**, the Splunk Universal Forwarder stopped forwarding logs from SOC-Syslog to the Splunk Server. 

We SSH'ed into the SOC-Syslog server to check if logs were being sent from the nodes to SOC-Syslog. We confirmed the logs stopped being forwarded on September 17, 2025. By the time we realized there were ingestion issues on SOC-Syslog, it had been days since SOC-Syslog was non-operational. The server was online but essentially in a read-only state.

![Zero logs ingested on September 17, 2025](https://www.cppsoc.xyz/assets/documentation/syslog/3.png)

## Initial Remediation Attempts

In an attempt to remediate the issue, the SOC decided to try three things in the following order:

1. **Restart RSyslog Service**  
   ```bash
   systemctl restart rsyslog
   ```
   Attempted to restart the service in case RSyslog was the issue.

2. **Restart Splunk Universal Forwarder**  
   ```bash
   cd /opt/splunkforwarder/bin && ./splunk restart
   ```
   Attempted to restart the forwarding process from SOC-Syslog to the Splunk Server.

3. **Reboot the Server**  
   ```bash
   reboot
   ```
   Attempted to restart the entire SOC-Syslog server.

## Boot Loop Issue

After running the `reboot` command, the SOC realized the server did not restart successfully. Due to the location difference between the SOC and Student Data Center (SDC), it took about 20 minutes until the SOC realized that SOC-Syslog was stuck in a boot loop.

### Entering Emergency Shell

In an attempt to break out of this boot loop, the SOC researched how to enter the Red Hat Enterprise Linux (RHEL) 9.5 Emergency Shell.

During the initial boot sequence, the SOC edited the GRUB Loader with the following modifications:

```bash
# Removed parameters:
quiet rhgb

# Added parameters:
systemd.unit=multi-user.target
```

This process allowed us to see all the system logs that were occurring on system startup, showcasing many services that failed to start.

![Failed dbus services during boot](https://www.cppsoc.xyz/assets/documentation/syslog/1.jpg)

After entering the emergency shell, we were able to boot into the operating system and run commands.

## Root Cause Analysis

One of the most concerning findings came from running:

```bash
df -h
```

This command displayed all the filesystems on the operating system, and concerns immediately arose. The directory for the operating system (RHEL 9.5) was installed under `/dev/mapper/rhel-root` with 70GB allocated space, but **only 20KB was available**.

![Disk usage showing minimal space on rhel-root](https://www.cppsoc.xyz/assets/documentation/syslog/2.jpg)

Initially, we assumed this was reserved system space and didn't understand this was the actual OS partition that was full.

### Identifying the Culprit

Upon realization that this was the culprit, we scanned the directory to find the largest files on the operating system.

We discovered that:
- The `/var/log` directory contained more than half of the allotted storage of the entire OS partition (**40+ GB**)
- Specifically, the file `/var/log/messages` was taking up all the space on the operating system partition, as it contained all the logs ingested from all our Linux-based nodes in a single file

Interestingly, we noticed that a dedicated directory called `/mnt/storage` was not being used at all.

## Resolution

To get SOC-Syslog back online, our solution was to move the problematic log file:

```bash
mv /var/log/messages /mnt/storage
```

This command immediately relieved our storage issue on the `rhel-root` directory. 

### Results

After moving the file:
1. We restarted the server without the GRUB loader modification
2. Services started successfully once again
3. Backlogged logs began being ingested to SOC-Syslog
4. Logs were successfully forwarded to the Splunk Server

## Lessons Learned

- Monitor disk space on critical logging infrastructure
- Utilize dedicated storage partitions (like `/mnt/storage`) for log collection
- In a future write-up we will showcase how we revamped our logging infrastructure entirely!