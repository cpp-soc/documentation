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

*[Content to be added]*

---

### Alert: WinEventLogs:Security Monitoring EventID 4726

*[Content to be added]*

---


