# How the Student SOC Implemented Missile Map!

## Background

After a major rebuild of the infrastructure at the Student Data Center, the Student Security Operations Center (SOC) found that many legacy monitoring processes no longer applied. One critical need was auditing GlobalProtect VPN activity to understand who was connecting to the network and from where. The SOC wanted better visibility into VPN usage and potential anomalies, especially given the changes post-rebuild. To achieve this, they leveraged Splunk SIEM for log collection and even integrated a special map visualization to track user VPN connections geographically. 

## Initial Challenges with VPN Log Queries

In the beginning, querying the GlobalProtect VPN logs in Splunk for *"successful"* logins led to confusing and misleading results. The initial Splunk query was intended to filter for successful connection events, but it ended up including a huge volume of logs from around the world – even places like Russia, Africa, and Asia – suggesting hundreds of thousands of VPN login attempts. This was obviously alarming and pointed to something being off with the query or the logs forwarded.

The root issue was that the log fields were ambiguous. Some events were being marked with fields: action or status with *"success"* even when the login actually failed. For example, certain logs showed an action field of *"success"* but, upon inspecting details, the same log would contain an error message like *"Authentication failed: Invalid username or password	
"*. In some cases, the username field (`src_user`) was literally set to `"success"`, which clearly was not a real user account but rather a misinterpreted field. These were false positives that made it look like users from all over the globe were connecting, when in reality they were failed login attempts or automated brute-force attempts being logged in a misleading way.

![Raw user Logs](https://www.cppsoc.xyz/assets/documentation/missile-map/missile_map1.jpg)
![Redacted fields but user is known as 'success'](https://www.cppsoc.xyz/assets/documentation/missile-map/missile_map2.jpg)

To illustrate the problem, the SOC’s first query was roughly:

```splunk
index="netfw" sourcetype="pan:globalprotect" status=success
| iplocation src_ip
| eval start_lat=lat, start_lon=lon, end_lat=34.0597, end_lon=-117.8200
| stats count by start_lat, start_lon, end_lat, end_lon, src_ip
```

This attempted to find any logs with the term *"success"* and map their source IP locations. However, it swept up events that were not true successes. The resulting visualization showed an explosion of connection lines from virtually every continent, which was not an accurate picture of actual VPN usage. As shown below, the initial query’s output (on a world map) was cluttered with false-positive connections:
 *Note: image below was taken on 9/13 and I restricted the view to up to 9 hours for the purposes of proper and useful visualization*
![Redacted fields but user is known as 'success'](https://www.cppsoc.xyz/assets/documentation/missile-map/missile_map3.jpg)

The team investigated a few suspicious log entries to understand why they were being counted as successful. They found, for instance, logs where the user field was set to “success” and the action was “success” as well – yet further details in the log indicated a bad password. In contrast, a truly successful login log would show a real username and no such error. The screenshot below compares a suspicious log vs. a clean log in Splunk: the left side event is flagged as *"success"* but is actually a failed login attempt (with an error in the details), whereas the right side is a genuine successful VPN connection event.

*Comparison of a suspicious "success" log (left) vs. a genuine successful login log (right)*
![Logins where usernames are marked as 'success'](https://www.cppsoc.xyz/assets/documentation/missile-map/missile_map4.jpg)
![Splunk View of those incorrectly marked logs'](https://www.cppsoc.xyz/assets/documentation/missile-map/missile_map5.jpg)
Below is a proper login where an individual logged out and fields are marked properly, redacted parts are PII.
![Redacted Image of a Proper Login by Bill :D'](https://www.cppsoc.xyz/assets/documentation/missile-map/missile_map6.jpg)

This initial hurdle highlighted that not all *"success"* logs were equal. The SOC needed a better way to filter the data so that only true successful VPN connections would be visualized.

## Portal Types Overview

While auditing the GlobalProtect logs to solve the above mystery, the team discovered that logs referenced multiple “portal” types. GlobalProtect has a concept of portals and gateways, and the logs contained a field (`portal`) that could take on values like `gp-user`, `gp-user-portal`, `gp-mgmt`, `gp-mgmt-portal`, etc. Through careful analysis and by correlating with known VPN URLs, the SOC deciphered the meaning of each:

*   **`gp-mgmt-portal`**: This corresponds to the main GlobalProtect management portal – essentially the web interface or SSO login portal used by authorized users. In our case, this is the portal at `mgmt.sdc.cpp.edu` that staff would normally use to authenticate (it uses single-sign-on/SAML for authentication). It handles the user login process (authenticating credentials via SSO) before the VPN tunnel is established.
*   **`gp-mgmt`**: This refers to the GlobalProtect gateway management process that takes over after a user is authenticated. Once you successfully log in via the portal, the system uses `gp-mgmt` to actually set up the VPN connection (assign an IP, establish the tunnel, etc.). In short, `gp-mgmt` events are part of establishing the connection once credentials are validated.
*   **`gp-user-portal`**: This turned out to be a secondary user portal that does not use SSO. In our environment this was the URL `vpn.sdc.cpp.edu`, which presents a simple username/password login screen. It was legacy and supposed to be retired, but our audit revealed it was still running. Essentially, `gp-user-portal` logs indicate someone using this older portal login page (likely with a local account credential). We only discovered its significance when we noticed logins coming from external universities and unexpected locations – those users were accessing this portal during special events.
*   **`gp-user`**: Similar to `gp-mgmt` above, `gp-user` refers to the connection process initiated via the user portal. If someone logs in through the `gp-user-portal` (the old login page), the system then generates `gp-user` events to handle the VPN connection setup for that session.

The SOC initially assumed only one portal was relevant (the main SSO portal `mgmt.sdc.cpp.edu`) and perhaps also the campus-wide VPN (`vpn.connect.cpp.edu` managed by central IT). The log analysis, however, exposed that two different portal interfaces were in play for the Student Data Center: the expected SSO portal and the forgotten legacy portal. This discovery was pivotal – it explained why there were logs of connections from places and organizations that didn’t line up with our usual user base. Those turned out to be external participants (for instance, students from other universities) who were given access during events like SWIFT competitions or tryouts, using the legacy portal that was opened up for them.

## Security Concerns with the Legacy Portal

Uncovering the existence of `vpn.sdc.cpp.edu` (the `gp-user-portal`) raised immediate security concerns. This portal uses only a basic username/password authentication without the protection of single sign-on or multifactor, and it was exposed to the internet for the sake of external user access. As a result, it had become a target for brute-force login attempts. The Splunk logs clearly showed automated attacks hitting this portal – the source of the “success” noise was largely bots or malicious actors trying to guess passwords on the public-facing login page.

Having a secondary portal publicly accessible is a risk, but at the time the SOC faced a dilemma: they needed this portal to remain available during certain external events (where non-Cal Poly users needed VPN access to participate, and those users could not use our SSO). During events like the SWIFT tryouts, the legacy portal was intentionally left open so outside participants could log in with credentials we provided them. This was a temporary necessity that unfortunately expanded our attack surface.

The screenshot below shows what the `vpn.sdc.cpp.edu` login interface looks like – a simple login form without SSO. This simplicity is exactly what makes it a brute-force target, as any internet user can reach this page and attempt to log in:

*Legacy VPN Portal login page (vpn.sdc.cpp.edu) with basic username/password prompt*
![Legacy Portal](https://www.cppsoc.xyz/assets/documentation/missile-map/missile_map7.jpg)

### Brute-force exposure
With just a username and password field and no second-factor or SSO, bots around the world constantly probed this portal. The SOC observed many login attempts from foreign IPs (which initially masqueraded in the logs as “successful” due to the logging quirk). This underscored the importance of a plan to either better secure this portal (rate limiting, MFA, or network restrictions) or fully decommission it as soon as external-event needs allow.

## Improved Log Fingerprinting for True Successes

To filter out the noise and focus only on truly successful VPN connections, the SOC refined their Splunk queries using a more reliable field: `event_id`. By examining the available event identifiers in the GlobalProtect logs (Splunk makes it easy to see distinct field values, as shown below), they found that one specific event code consistently corresponds to a completed VPN login. The `event_id` field value `gateway-connected` is logged only when a GlobalProtect client has successfully connected to the gateway (i.e., the VPN tunnel is fully established)[1]. This is exactly the kind of event they wanted to track.

*Splunk interface showing sample event_id field values (including "gateway-connected")*

According to Palo Alto Networks’ documentation, a `gateway-connected` event “indicates a GlobalProtect client successful connection for tunnel or non-tunnel mode”[1] – in other words, a real VPN session. Armed with this knowledge, the SOC adjusted their Splunk search to zero in on those events and ignore the rest. They also narrowed the search to the relevant portals (`gp-mgmt` and `gp-user`, which are the ones that produce the gateway connection logs after authentication).

The refined Splunk query looked something like this:

```splunk
index="netfw" sourcetype="pan:globalprotect" (portal="gp-mgmt" OR portal="gp-user") event_id="gateway-connected" src_user=*
| iplocation src_ip 
| eval start_lat=lat, start_lon=lon, end_lat=34.0597, end_lon=-117.8200 
| stats count by action, src_user, src_ip, start_lat, start_lon, end_lat, end_lon
```
*As of 9/23, 'sourcetype' was no longer a applicable field to search by or to be included when we searched on Splunk. It could be fixed, but below is the refined search query.
```splunk
index="netfw" (portal="gp-mgmt" OR portal="gp-user") event_id="gateway-connected" src_user=*
| iplocation src_ip 
| eval start_lat=lat, start_lon=lon, end_lat=34.0597, end_lon=-117.8200 
| stats count by action, src_user, src_ip, start_lat, start_lon, end_lat, end_lon
```

Let’s break down what this does:
-   **Base search**: We search the firewall logs (`index="netfw"`) of type `pan:globalprotect` for events where the `portal` field is either `gp-mgmt` or `gp-user` (i.e. the connection-establishment stage for either portal) and `event_id="gateway-connected"`. We also ensure `src_user=*` to pick up only events tied to a user account (excluding any system or empty entries).
-   **Geo IP lookup**: Using Splunk’s `iplocation` command on the source IP (`src_ip`) populates latitude (`lat`) and longitude (`lon`) fields based on geo-IP data.
-   **Define map coordinates**: We then create `start_lat`/`start_lon` from the looked-up coordinates (the user’s approximate location), and set a fixed `end_lat`/`end_lon` corresponding to our campus’s CLA Building location (roughly 34.06 N, -117.82 W in Pomona, CA). This essentially prepares the data for mapping an arc from the user to the campus.
-   **Stats aggregation**: Finally, we use `stats count by ...` to group events. In practice, for visualization we might not even need the count, but this method ensures we have one line per unique combination of user and location. The `action` field (which in these events should indicate "success/allow") can also be included just for reference.

With this refined “fingerprint” query, false positives disappeared. Only genuine successful VPN connection events were returned. The volume of events was now sane (e.g., dozens per day instead of thousands) and the sources were all expected user locations. This was the “silver bullet” the team was looking for to get clean data for visualization.

## Missile Map Implementation (Geographic VPN Visualization)

Having obtained clean data on successful VPN connections, the SOC proceeded to implement the Missile Map visualization in Splunk. Missile Map is a Splunk app/visualization that displays data as arcs on a world map[2] – much like the “cyber attack” maps often seen in security dashboards. Each arc requires a starting and ending coordinate. In our case, the starting point is the geographic location of the user’s IP address, and the ending point is the fixed location of Cal Poly Pomona’s CLA Tower (representing our data center).

We configured the Missile Map by providing it the fields it expects (our query already yielded `start_lat`, `start_lon`, `end_lat`, `end_lon` for each event)[3]. We chose a fixed color for the arcs and set the map’s center/zoom to focus on the areas of interest. Every time a new VPN login occurs and meets our query criteria, the dashboard displays a new arc from the user’s city to campus. Because all arcs share the same destination (Pomona, CA), the visualization looks like a set of missiles or arrows converging on a single point – hence the name “Missile Map.”

We also included additional context in the data points if needed. For example, we could label arcs with the username or mark if an event came from the legacy portal vs the main portal (using different colors or labels). In this case, since we filtered out the legacy portal’s unsuccessful noise and only tracked actual connections, most arcs represent valid user sessions. If any unusual connection does appear (say, a valid login from an atypical country), it stands out prominently on the map for further investigation.

Below is a placeholder for what the final Missile Map dashboard looks like. The real visualization shows a world map with arcs originating from various user locations (across the U.S. and occasionally abroad) all terminating at the CLA Building location in California:

*Missile Map visualization of VPN connections (each arc from user’s geolocation to campus)*

*Figure: The Missile Map in Splunk showing successful VPN connections. Each arc represents a user VPN session connecting from the origin (determined by IP geolocation) to the campus network (destination fixed at CLA Building coordinates). We can see, for example, connections coming from other parts of California, some from out-of-state (perhaps students traveling or out-of-state participants during events), and so on. The map gives an immediate sense of where users are connecting from and can reveal patterns (like clusters of connections from an unexpected region).*

By integrating this Missile Map, the Student SOC significantly improved its situational awareness. Rather than combing through text logs, analysts can glance at the dashboard and spot if something looks off (such as an arc from an unusual country or an unusually high number of arcs at once which might indicate a surge in usage or an event).

## Data Anomalies & Lessons Learned

Throughout this project, a few anomalies were discovered in the data, underscoring lessons for the team:
-   **Geo-IP mismatches**: On a few occasions, the user’s IP address and the provided geolocation did not line up. For example, one user’s IP traced to a Southern California ISP, yet the latitude/longitude from `iplocation` placed the point in New York. In another case, a user’s IP was clearly from Florida, but the geo lookup showed a location in Illinois. These discrepancies might be due to outdated GeoIP data, VPN exit nodes, or how GlobalProtect reports location (possibly using a different source of geo info). It was a reminder that GeoIP isn’t 100% accurate – we saw “Florida user connecting from Illinois” which prompted us to double-check those cases manually.
-   **False success logs**: We learned that not all log fields mean what one might assume at face value. The presence of *"success"* in a log message or an action field did not always indicate a successful login. This was a critical lesson: always validate using reliable fields (in our case, `event_id="gateway-connected"` was the reliable indicator of success).
-   **Legacy portal noise**: The fact that a second portal was still running led to a lot of noise in the logs. This taught us the importance of maintaining an accurate inventory of active services. If something is supposed to be retired but isn’t, it can both pose a security risk and muddy your monitoring data. We’ve since communicated this to the infrastructure team. The plan is to properly decommission or lock down `vpn.sdc.cpp.edu` when external events are not happening, and to explore more secure ways to grant guest access when they are.
-   **Visualization value**: Implementing the Missile Map has proven the value of visualization in security operations. Issues that were not obvious from raw logs became very clear when plotted geographically. For instance, seeing a line from an unexpected country immediately raises a flag to investigate if that was a legitimate user or something that slipped through.
-   **Continuous tuning**: Finally, we recognize that our queries and dashboards will need continuous tuning. As a next step, we might incorporate additional filters (for example, excluding any log where `src_user` equals `"success"` just as an extra sanity check, or updating our GeoIP database to the latest version to improve accuracy). We’re also considering setting up alerts for unusual patterns, such as multiple VPN connections from one foreign country in a short time or connections from countries where we normally have no users.

## Summary

The Student SOC’s implementation of the Missile Map was a success – both in terms of the technical Splunk solution and in the lessons learned along the way. We now have a clear, real-time view of VPN login activity, and we’ve hardened our approach to analyzing logs (focusing on the right markers and understanding the data better). This project not only helps us audit VPN usage but also has improved our security posture by highlighting an overlooked exposure and by giving us a tool to spot abnormal connection locations at a glance. The journey involved unraveling confusing logs, learning the ins and outs of GlobalProtect portals, and ultimately integrating an innovative visualization to make sense of it all. The result is an informative documentation and a powerful operations dashboard that can be used by future Student SOC members to monitor and investigate VPN activities efficiently.

---
 
[1] [Event Descriptions for the GlobalProtect Logs in PAN-OS](https://docs.paloaltonetworks.com/globalprotect/10-1/globalprotect-admin/logging-for-globalprotect-in-pan-os/event-descriptions-for-the-globalprotect-logs-in-pan-os)

[2, 3] [GitHub - lukemonahan/missile_map: Missile Map Splunk visualisation](https://github.com/lukemonahan/missile_map)

*AI used to improve language and markdown