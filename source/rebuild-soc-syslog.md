# Rebuilding SOC-Syslog: A Complete Journey

## Overview

SOC-Syslog is a dedicated server running RHEL 9.5 that handles log ingestion via RSyslog from our physical Unix endpoints, including:
- ESXI Cluster nodes
- Palo Alto Firewall

## Initial Problem: Disk Space Exhaustion

### Original Configuration

The initial configuration in `/etc/rsyslog.conf` was:

```bash
# Log anything (except mail) of level info or higher.
# Don't log private authentication messages!
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
```

### The Issue

Looking at `df -h` output, we discovered that logs were being saved directly on the OS partition, which was only allocated **70 GB**.

Inevitably, the OS partition filled up and put SOC-Syslog into a read-only state. Logs were no longer being written to disk and therefore were no longer being forwarded to our Splunk Server.

## Phase 1: Emergency Response

### Understanding the Problem

If you've read our previous write-up on how we remediated this type of issue, you're now caught up to how we started solving this problem.

**Key Issues Identified:**
- Logs from all physical endpoints were being written to a **single file** without segregation
- All logs were stored in one place
- Extracting logs from a single endpoint required parsing the entire file
- This became an immediate area of concern

### Immediate Solution

With SOC unable to monitor any logs, the goal was to get SOC-Syslog back online immediately:

1. Entered the emergency shell of the OS
2. Stopped writing to disk
3. Moved the entire messages file to a separate partition that was dedicated for logs but had never been used

**Result:** Moving the messages file relieved the storage issue on the root directory, and restarting the server allowed logs to be ingested and forwarded again.

## Phase 2: Permanent Storage Solution

### The Challenge

This was only a bandaid solution—logs were still continuing to fill up the root directory. We needed a permanent solution to change where logs were being saved.

### Initial Approach: Directory Change

We thought changing the directory in the config would be a simple fix:

```bash
# Log anything (except mail) of level info or higher.
# Don't log private authentication messages!
*.info;mail.none;authpriv.none;cron.none                /mnt/storage/splunk_logs/messages
```

### SELinux Complications

This was **not** the silver bullet solution we expected. Due to RHEL and SELinux:
- Files and folders were tagged with special flags
- We did not understand how to use or edit these flags
- rsyslog would fail to write and complain about permissions

### Attempted Solutions

**Failed Approach:**
- Attempted to mount the storage partition to `/var/log` directory
- Goal: Keep the original config and redirect all content from `/var/log` → `/mnt/storage/var_log/`
- **Result:** This was convoluted and made troubleshooting more difficult

**Successful Approach:**
1. Unmounted and reverted the failed change
2. Disabled SEManage
3. Had someone who understood the flag system apply proper attributes to our new directory
4. This allowed log writing to the directory to work properly

**Final Result:** Logs were being ingested to the proper storage partition and stopped writing to the root directory.

## Phase 3: Reconfiguring Splunk Forwarder

### The Task

The last step was figuring out how to point the Splunk Forwarder to monitor our new directory at `/mnt/storage/splunk_logs/`, since the originally configured directory was no longer receiving logs.

### Solution Steps

1. **Stop the Splunk Forwarder:**
   ```bash
   cd /opt/splunkforwarder/bin
   ./splunk stop
   ```
   
   > **Why?** There are credentials set up when you first install Splunk Forwarder that we did not know. This was a workaround for those credentials.

2. **Add the new monitor:**
   ```bash
   ./splunk add monitor /mnt/storage/splunk_logs
   ```

3. **Restart the Splunk Forwarder:**
   ```bash
   ./splunk start
   ```

**Result:** Logs from `/mnt/storage/splunk_logs` began forwarding and appeared on our Splunk UI.

## Phase 4: Fixing Log Parsing on Splunk

### The New Problem

At this point, we were still attempting to restore SOC-Syslog to its original functionality:

1. ✅ Receiving logs from endpoints
2. ✅ Forwarding to Splunk
3. ❌ Being sorted properly on the Splunk Server

The logs being forwarded to Splunk were **no longer being parsed properly**.

### Understanding the Old Configuration

We realized we needed to update the following files on our Splunk Server: `props.conf` and `transforms.conf`.

**Old Props.conf:**
```ini
#marshall's thing
#[pan:log]
#TRANSFORMS-extract_host = extract_syslog_host
```

**Old Transforms.conf:**
```ini
#marshall's thing
#[extract_syslog_host]
#REGEX = ^\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+([\w\-.]+)
#FORMAT = host::$1
#DEST_KEY = MetaData:Host
```

**What it did:** Used regex to parse out the hostname from the raw log, then set the host value for that field automatically when being ingested.

**The Problem:** This had stopped working, and sourcetypes were all incoming as "syslog". We needed proper sorting of sourcetypes to autogenerate fields from the apps installed on Splunk.

### New Configuration

After trying many solutions, we arrived at this final configuration:

**Props.conf:**
```ini
[source::/mnt/storage/splunk_logs/messages]
TRANSFORMS-set_host = set_syslog_host
TRANSFORMS-routing = set_netfw_index, set_sourcetype_globalprotect, set_esxi_index

[too_small]
PREFIX_SOURCETYPE = false
```

**Transforms.conf:**
```ini
[set_syslog_host]
REGEX = ^\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+([\w\-.]+)
FORMAT = host::$1
DEST_KEY = MetaData:Host

[set_netfw_index]
REGEX = .*GLOBALPROTECT.*
DEST_KEY = _MetaData:Index
FORMAT = netfw

[set_esxi_index]
REGEX = (?i)(?:sdc.cpp)
DEST_KEY = _MetaData:Index
FORMAT = esxi

[set_sourcetype_globalprotect]
REGEX = .*GLOBALPROTECT.*
DEST_KEY = MetaData:Sourcetype
FORMAT = pan:globalprotect
```

### How It Works

This configuration was **better** because we were explicit in what we were doing:

- **Props.conf:** Runs "modules" or "rules" on logs being ingested from that directory
- **`too_small` rule:** Disabled because it was randomly adding to our sourcetype
- **Transforms.conf:** Contains the actual definitions of those rules

#### Rule Explanations

| Rule | Purpose |
|------|---------|
| `set_syslog_host` | Similar regex to before (which worked), but changed how the rule was applied |
| `set_netfw_index` & `set_sourcetype_globalprotect` | Searches for GlobalProtect-related logs and sends them to the `netfw` index with `pan:globalprotect` sourcetype for special fields |
| `set_esxi_index` | Identifies logs with `sdc.cpp` in the hostname (from the cluster) and places them in the `esxi` index |

## Phase 5: Building a Better Solution

### Reflection on the "Frankenstein Solution"

As mentioned above, our goal was to get everything back online to what we once had. This became our **Frankenstein solution** of cobbling together a previous implementation of Syslog—a dedicated Syslog server integrated into a Splunk Server—without documentation.

### Problems with the Current Implementation

Although we accomplished our goal, the implementation was still messy:

- ❌ Logs were being ingested into one single file
- ❌ No differentiation in how logs were saved
- ❌ Unclear on how to set up rsyslog on the endpoints
- ⚠️ Endpoints were still spamming attempts to forward logs when the server wasn't functional

### Starting Fresh: Dynamic Log Segregation

In our attempt to build SOC-Syslog from scratch (or at least learn all parts of setting this server up), we started somewhat fresh.

#### New Directory Structure

Created a new directory: `/mnt/storage/new_rsyslog` (alongside existing `old_rsyslog` & `rsyslog`)

#### New Configuration: `/etc/rsyslog.d/dynamic_hosts.conf`

```bash
# Dynamic log file generation by hostname

# Match logs from any host and direct them to a file based on hostname
$template HostLogFile,"/mnt/storage/new_rsyslog/%HOSTNAME%/uma.log"

# Use the template to write logs to the respective file
*.*  ?HostLogFile
```

#### Result

Logs are now written to their respective hostname directories:

**Example:**
- GlobalProtect/Palo Alto Firewall logs → `/mnt/storage/new_rsyslog/sdc-fw.csupomona.net/uma.log`

### Legacy Configuration

> **Note:** At this time, our `rsyslog.conf` file was still writing to the `splunk_logs` directory on the storage partition, but that's a topic for another time.

<details>
<summary><b>Legacy rsyslog.conf Rules (Click to expand)</b></summary>

```bash
#### RULES ####

# Log all kernel messages to the console.
# Logging much else clutters up the screen.
#kern.*                                                 /dev/console

# Log anything (except mail) of level info or higher.
# Don't log private authentication messages!
*.info;mail.none;authpriv.none;cron.none                /mnt/storage/splunk_logs/messages

# The authpriv file has restricted access.
authpriv.*                                              /mnt/storage/splunk_logs/secure

# Log all the mail messages in one place.
mail.*                                                  -/var/log/maillog

# Log cron stuff
cron.*                                                  /mnt/storage/splunk_logs/cron

# Everybody gets emergency messages
*.emerg                                                 :omusrmsg:*

# Save news errors of level crit and higher in a special file.
uucp,news.crit                                          /mnt/storage/splunk_logs/spooler

# Save boot messages also to boot.log
local7.*                                                /mnt/storage/splunk_logs/boot.log
```

</details>

### Updating Splunk Monitor for New Directory Structure

With logs now properly segregated by our custom rule, we needed to update the Splunk Monitor for the new directories.

**Steps:**

1. Restart the rsyslog service
2. Confirm logs are being ingested into `/mnt/storage/new_rsyslog`
3. Stop the Splunk Forwarder
4. Set up monitoring of `/mnt/storage/new_rsyslog`
5. This would pick up any new hosts whenever we added them to rsyslog

**Known Limitation:** Whenever a new host was added, we would need to restart Splunk Universal Forwarder on SOC-Syslog.

### Updating Splunk Server Configuration

With this whole different setup for how logs were being saved, most of the work was done on the SOC-Syslog server. The only change needed on our Splunk Server (since we had hardcoded it) was to update `props.conf` to apply the rules to the right directory.

**Updated Props.conf:**
```ini
[source::/mnt/storage/new_rsyslog/*/uma.log]
TRANSFORMS-set_host = set_syslog_host
TRANSFORMS-routing = set_netfw_index, set_sourcetype_globalprotect, set_esxiindex
```

This is a basic regex pattern: any folder inside `new_rsyslog` with a `uma.log` file would get these modules/rules applied.

### System Now Fully Scalable

At this point, **SOC-Syslog was prepared to handle anything:**

- ✅ More logs (storage)
- ✅ New hosts
- ✅ Proper sorting
- ✅ Clear understanding of how to resolve issues

---

## Phase 6: Transitioning to Proxmox

### Decommissioning ESXI Cluster

At this point in time, it was finally time to decommission our ESXI Cluster and take it offline.

> **Irony:** Yes, we worked this hard to get everything back to normal with all these endpoints, only to end up taking it offline!

After decommissioning, our Splunk server was only receiving logs from **2 endpoints:**
- Our router
- Our secondary Domain Controller (yes, not the primary)

### New Challenge: Monitoring Proxmox Cluster

We officially had to start monitoring our new Proxmox Cluster, which had been in deployment since the end of Spring 2025.

#### The Air-Gap Problem

**Challenge:** The endpoints were configured to be air-gapped from the Internet and only accessible through the LAN.

This meant:
- Running `apt-get update` and `apt-install rsyslog` would **not** install the application and its dependencies
- Normal package installation was impossible

#### Package Mirror Solution (Failed)

We had a broken package mirror setup:

**Intended Design:**
1. VM connected to both Internet and LAN
2. VM installs packages and dependencies
3. Edit Proxmox nodes' source list to point to this mirror/VM
4. Download packages directly from that machine
5. Keep nodes offline

**Reality:** The mirror did not work as intended, and the security team was not aware of how to fix it, leaving it to infrastructure to solve.

#### Manual Installation Solution (Success)

Security decided the best solution was to manually transfer and install packages:

**Process:**
1. Use SCP to transfer the package and its **3 dependencies** to each machine
2. Install manually on each node
3. **Result:** Tiresome? Yes. But it worked!

### Configuring Proxmox Nodes

After securely copying (SCP) the files from our machines to the nodes, we configured rsyslog on the nodes to send everything to our Splunk server.

**Configuration: `/etc/rsyslog.conf`**

```bash
# IP replaced with hostname
*.* @soc-syslog.sdc.cpp:514
```

We copied that line across all the Proxmox nodes after installing rsyslog on them.

### Verification Steps

1. **Restart the service** → Confirmed rsyslog was active and writing logs
2. **Check SOC-Syslog** → Verified `/mnt/storage/new_rsyslog` directory showed logs separated into respective hostname directories
3. **Restart Splunk Forwarder** → Updated monitoring for new folders and started forwarding logs from newly ingested hosts to Splunk

### Configuring Transforms for Proxmox

#### Previous Approach
- Had a rule/module looking for `sdc.cpp` domain in the hostname (for ESXI)

#### New Approach
Since we had **6 Proxmox nodes**, we wrote a simpler regex:

**File: `/opt/splunk/etc/system/local/transforms.local`**

```ini
[set_proxmox_index]
REGEX = (?i)(?:commando|gemini|godfrey|gonk|malenia|radahn)
DEST_KEY = _MetaData:Index
FORMAT = proxmox
```

**Proxmox Node Names:**
- commando
- gemini
- godfrey
- gonk
- malenia
- radahn

We created a new `proxmox` index on Splunk Web UI to:
- Place these new logs
- Keep our ESXI logs separated in case we ever needed to look them up later

---

## Phase 7: Expanding Monitoring to Other VMs

To keep this shorter: we installed rsyslog on our other critical VMs that were UNIX-based, which was **much easier** since those were not air-gapped.

---

## Final Result

### Current Monitoring Status

🎉 **SOC via SOC-Syslog is now ingesting logs from 14 different machines into our Splunk Server for monitoring!**

### Summary of Achievements

| Phase | Achievement |
|-------|-------------|
| 1 | Resolved disk space exhaustion emergency |
| 2 | Implemented permanent storage solution |
| 3 | Reconfigured Splunk Forwarder |
| 4 | Fixed log parsing on Splunk |
| 5 | Built scalable log segregation system |
| 6 | Successfully migrated to Proxmox Cluster |
| 7 | Expanded monitoring to all critical VMs |

### Key Improvements

- ✅ **Storage:** Moved from 70 GB OS partition to dedicated storage partition
- ✅ **Organization:** Logs segregated by hostname instead of single file
- ✅ **Scalability:** Can easily add new hosts without major reconfiguration
- ✅ **Parsing:** Proper sourcetype assignment and field generation
- ✅ **Indexing:** Separate indexes for different infrastructure (netfw, esxi, proxmox)
- ✅ **Monitoring:** 14 different machines actively monitored
