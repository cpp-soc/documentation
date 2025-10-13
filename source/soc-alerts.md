# How Does the SOC Monitor Our Endpoints?

After ingesting logs from numerous endpoints, manually reviewing logs in our SIEM is both tedious and time-consuming. However, by leveraging our SIEM alongside an application that appropriately categorizes raw logs based on expected fields, we can automatically alert SOC employees when critical events occur.

## What Are We Monitoring with Alerts?

We currently monitor three endpoints with configured alerts that trigger when specific events occur:

1. **GlobalProtect connections** - Tracks VPN access to our infrastructure
2. **Active Directory account creation** - Monitors new user account provisioning
3. **Active Directory account deletion** - Tracks account removal from our infrastructure

These three event types enable us to monitor connections into our infrastructure and maintain visibility over account lifecycle management.

## How Are Alerts Configured?

Alerts in Splunk function as scheduled searches that run periodically on the SIEM. When a new event is triggered or matching results appear, we activate a Discord webhook to send a structured message containing the search results to our `#incident-alerts` channel. Each event type has a unique, tailored webhook configuration.

**Examples of alerts:**

<Three Pictures>

---

### Alert: GlobalProtect VPN - Unusual Location Detected

This alert identifies VPN connections originating from unusual geographic locations.

**Search Query:**

```splunk
index="netfw" portal IN ("gp-mgmt","gp-user") event_id="gateway-connected" src_user=*
| iplocation src_ip
| where isnotnull(lat) AND isnotnull(lon)
| eval start_lat=lat, start_lon=lon, end_lat=34.0597, end_lon=-117.8200
| eval pi=3.14159, earth_mi=3958.7613
| eval rlat1=start_lat * pi / 180, rlon1=start_lon * pi / 180, rlat2=end_lat * pi / 180, rlon2=end_lon * pi / 180
| eval dlat=rlat2 - rlat1, dlon=rlon2 - rlon1
| eval a=pow(sin(dlat/2),2) + cos(rlat1) * cos(rlat2) * pow(sin(dlon/2),2)
| eval c=2 * atan2(sqrt(a), sqrt(1 - a))
| eval distance_miles=round(earth_mi * c, 2)
| where distance_miles > 10
| eval severity=case(
    distance_miles > 25, "high",
    distance_miles > 15, "medium",
    distance_miles > 10,  "low",
    true(),              "none"
  )
| stats count AS events earliest(_time) AS first_seen latest(_time) AS last_seen BY severity, portal, src_user, src_ip, start_lat, start_lon, distance_miles
| eval severity_rank=case(severity=="high",3, severity=="medium",2, severity=="low",1, true(),0)
| sort 0 - severity_rank - events
| fields - severity_rank
```

![GlobalProtect Alert Example](https://cppsoc.xyz/assets/documentation/soc-alerts/1.png)

**Query Breakdown:**

The first line specifies our data source: the `netfw` index, which stores all GlobalProtect logs. We specifically monitor two authentication portals (`gp-mgmt` and `gp-user`) and search for the `event_id="gateway-connected"` event, which represents the final step establishing a connection to the server. The wildcard `src_user=*` captures all usernames.

The `iplocation src_ip` command translates the source IP address into geolocation coordinates. These coordinates are then used to calculate the distance between the connection origin and our campus (specifically the CLA building) using the Haversine formula.

**Severity Classification:**

Connections are classified based on distance from campus:
- **Low severity:** > 10 miles
- **Medium severity:** > 15 miles  
- **High severity:** > 25 miles

**Alert Details:**

Each alert provides comprehensive context about the login, including:
- Severity level (low, medium, or high)
- Username
- Portal used for authentication
- Distance from campus in miles
- Number of connection attempts

The severity indicator displayed below the connection details is a default flag configured in the Splunk Alert System and serves as a general classification. Using the built-in Splunk Alert System, analysts can trace back to the original login event with a single click (VPN connection required).

---

### Alert: WinEventLogs:Security Monitoring EventID 4720

This alert monitors Active Directory for new user account creation events, helping us track when accounts are provisioned in our infrastructure.

**Search Query:**

```splunk
index=* source=WinEventLog:Security sourcetype=WinEventLog EventCode=4720
| eval created_user=coalesce(New_Account_Account_Name, SAM_Account_Name, Account_Name, user, user_name)
| eval created_domain=coalesce(New_Account_Domain, Account_Domain, dest_nt_domain, Subject_Account_Domain)
| eval created_by=coalesce(Subject_Account_Name, src_user, src_user_name)
| eval dc=coalesce(ComputerName, dvc_nt_host, dest_nt_host, dvc, host)
| where isnotnull(created_user) AND NOT like(created_user, "%$")
| table _time created_user created_domain created_by dc
| sort - _time
```

**Query Breakdown:**

The query searches across all indexes for Windows Security Event Logs with `EventCode=4720`, which is generated whenever a user account is created in Active Directory.

The `coalesce()` functions normalize field names across different log formats and Windows versions, ensuring we capture the relevant information regardless of how it's labeled in the raw logs. Specifically:
- `created_user` extracts the newly created account name
- `created_domain` identifies the domain where the account was created
- `created_by` captures who performed the account creation
- `dc` identifies the domain controller that logged the event

The `where` clause filters out system accounts (ending with `$`) and ensures we only alert on legitimate user account creations.

**Alert Details:**

Each alert provides essential information about the account creation event:
- Timestamp of when the account was created
- Created username
- Domain where the account resides
- Administrator who created the account
- Domain controller that processed the creation

This visibility helps us maintain accountability for account provisioning and detect unauthorized account creation attempts.

---

### Alert: WinEventLogs:Security Monitoring EventID 4726

This alert monitors Active Directory for user account deletion events, ensuring we maintain visibility over account lifecycle management and detect unauthorized removals.

**Search Query:**

```splunk
index=* source=WinEventLog:Security sourcetype=WinEventLog EventCode=4726
| eval deleted_user=coalesce(Target_Account_Name, Account_Name, user, user_name)
| eval deleted_domain=coalesce(Target_Account_Domain, Account_Domain, dest_nt_domain, Subject_Account_Domain, src_nt_domain)
| eval deleted_by=coalesce(Subject_Account_Name, src_user, src_user_name)
| eval dc=coalesce(ComputerName, dvc_nt_host, dest_nt_host, dvc)
| where isnotnull(deleted_user) AND NOT like(deleted_user, "%$") 
| table _time deleted_user deleted_domain deleted_by dc
| sort - _time
```

**Query Breakdown:**

The query searches across all indexes for Windows Security Event Logs with `EventCode=4726`, which is generated whenever a user account is deleted from Active Directory.

Similar to the account creation alert, the `coalesce()` functions normalize field names to ensure consistent data extraction:
- `deleted_user` extracts the name of the deleted account
- `deleted_domain` identifies the domain where the account existed
- `deleted_by` captures who performed the account deletion
- `dc` identifies the domain controller that logged the event

The `where` clause filters out system accounts (ending with `$`) to focus on user account deletions that require tracking and review.

**Alert Details:**

Each alert provides critical information about the account deletion event:
- Timestamp of when the account was deleted
- Deleted username
- Domain where the account existed
- Administrator who deleted the account
- Domain controller that processed the deletion

This monitoring enables us to track account offboarding, detect unauthorized deletions, and maintain an audit trail for compliance purposes.

---


