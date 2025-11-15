# Splunk CTF Lab 

## Overview

This lab provides hands-on practice with Splunk and its Search Processing Language (SPL). It is designed for users who already understand the fundamentals of Splunk but want to deepen their skills by generating logs, analyzing them, and simulating real-world SOC investigations.

Participants act as SOC analysts, using SPL to uncover hidden flags, identify attacker behaviors, and analyze intrusion logs. Two options are available for generating data (a realistic VM-based attack environment or a simplified static dataset).

By the end of this lab, you will be comfortable:

- Investigating security incidents using real or simulated logs  
- Writing targeted SPL queries  
- Understanding common attacker patterns  
- Identifying flags hidden across different log fields  
- Building saved alerts  

---

## Lab Structure

You are provided access to a Splunk server where logs will be ingested from either virtual machines (Option 1) or imported datasets (Option 2).

**Splunk Server:** `192.168.1.112`  
**Splunk UI:** `https://192.168.1.112:8000`  
**Credentials:**  
- `user: splunklab`  
- `pass: splunk123`

### Virtual Machine Setup (Option 1)

| Machine | Purpose | IP | Credentials |
|--------|---------|----|-------------|
| Splunk Server | Indexes logs & provides UI | 192.168.1.112 | splunklab / splunk123 |
| Web Server (Ubuntu) | Generates logs via attacks | 192.168.1.113 | client / soc123 |
| Attacker (Kali) | Performs attacks | 192.168.1.115 | kali / kali123 |

Web logs are forwarded from Ubuntu to Splunk using the Universal Forwarder.

### Dataset Import Setup (Option 2)

Only the Splunk server is required. Intrusion logs are imported manually into Splunk.

---

# Option 1  
# Simulated Attack Environment with Virtual Machines

## Overview

This option provides a realistic SOC experience using a 3-VM attack environment. Participants use SPL to investigate attacks carried out by a Kali attacker against an Ubuntu web server.

### What You Need

- Kali Linux VM (attacker)  
- Ubuntu Web Server with Splunk Universal Forwarder  
- Splunk Enterprise Server  

### What Happens

1. Kali launches attacks (bruteforce, scans, SQL injection, etc.).  
2. Ubuntu Web Server logs the activity.  
3. Logs are forwarded to Splunk.  
4. You investigate to find hidden CTF flags and answer questions.

---

## CTF Challenge Questions (Option 1)

### **Easy Challenges (50 pts each)**

---

### **1) URI Flag**  
Many flags were placed in a query parameter and requested from the webserver by the attacker. However, only one is *legit*. Find it.   

<details><summary>Hint</summary>
Look for `update.flag` in the URI.
</details>

<details><summary>Query</summary>

```
index=web_log uri="*update.flag*" OR uri="*flag*"
```
</details>

<details><summary>Answer</summary>
update.flag{TOTALLY_LEGIT_URI}
</details>

---

### **2) User-Agent Flag**  
Many flags were also hidden in the UserAgent field. Find the one that is the most *suspicious*.
<details><summary>Query</summary>

```
index=web_log useragent="*flag*"
```
</details>

<details><summary>Answer</summary>
update.flag{SUSPICIOUS_USERAGENT}
</details>

---

## **Medium Challenges (100 pts each)**

---

### **3) Brute Force / Credential Stuffing**  
Find the attacker IP with the most failed login attempts as well as the total count of failed attempts. Format the flag in the following format: flag{8.8.8.8_#####).

<details><summary>Hint</summary>
Login and sign in attempts have a URI of “/login” and “/signin” respectively.
</details>

<details><summary>Query</summary>

```
index=web_log (uri="/login" OR uri="/signin")
| stats count by clientip
```
</details>

<details><summary>Answer</summary>
flag{192.168.1.115_76693}
</details>

---

### **4) Nikto Scan Detection**  
A Nikto scan was ran against the server. Find the unique evidence (a specific vulnerability it found) and list it. Format the flag in the following format: flag{VULNERABILITY.txt}.

<details><summary>Query</summary>

```
index=web_log uri="*Nikto*" | stats count by uri
```
</details>

<details><summary>Answer</summary>
flag{rfiinc.txt}
</details>

---

### **5) Hidden Referer Flag**  
While running an attack, the attacker left evidence of a Common Vulnerability (CVE) they were attempting to exploit. The vulnerability is seeded in the Referer header. Find it. Format the flag in the following format: flag{CVE-1234-5678}.

<details><summary>Query</summary>

```
index=web_log referer="*CVE*"
```
</details>

<details><summary>Answer</summary>
flag{CVE-2014-6278}
</details>

---

### **6) Web Scanner / Tool Identification**  
Identify the four scanning tools used against the server based on User-Agent strings. Furthermore, identify how many times each were utilized and list them in order from most used to least used.  Format the flag in the following format: flag{tool1_tool2_tool3_tool4}. 

**Note:**  
Nikto was run **108 times** but does **not** appear under User-Agent.

<details><summary>Query</summary>

```
index=web_log 
| search useragent=* 
| stats count by useragent 
| sort - count
```
</details>

<details><summary>Answer</summary>
flag{Hydra_Nikto_Nmap_SQLMap}
</details>

---

## **Hard Challenges (150 pts each)**

---

### **7) Encoded Flag (Hex/URL Encoding)**  
The attacker tried to hide a flag by URL encoding or hex-encoding it. Find the encoded hex string and decode the flag.

<details><summary>Hint</summary>
%75%70%64....</details>
<details><summary>Query</summary>

```
index=web_log uri="*%75%*"
```
</details>

<details><summary>Answer</summary>
update.flag{URL_ENCODED}
</details>

---

### **8) Create a Saved Alert**  
Create a Splunk saved search that triggers when any update.flag string appears in any of uri, host, useragent, or referer. Include the time, clientip, uri, useragent, and referrer. On the attacker VM, try to trigger the alert and then rerun the search to see if a new event appears. 

<details><summary>Query</summary>

```
index=web_log (uri="*update.flag*" OR useragent="*update.flag*" OR referer="*update.flag*")
| table _time clientip uri useragent referer
```
</details>

---

# Option 2  
# Importing a Pre-Existing Dataset (Cisco Firewall Intrusion Logs)

## Overview

This option uses a static dataset imported into Splunk. It is easier to set up but less dynamic than Option 1.

### What You Need

- Splunk Server `192.168.1.112`  
- Cisco Firewall Intrusion Event Dataset  

### Dataset Details

Data is indexed under:

**`index=main sourcetype=Sample_Data_Test`**

---

# CTF Challenge Questions (Option 2)

## **Basic Exploration — Easy (50 pts)**

---

### **1) Total Intrusion Events**
How many total intrusion events were recorded?

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test | stats count
```
</details>

<details><summary>Answer</summary>
224
</details>

---

### **2) List All Fields**

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test | fields * | head 1
```
</details>

---

### **3) Most Common Protocol**
What protocol is most commonly used in intrusion events? 

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test | stats count by Protocol | sort -count
```
</details>

<details><summary>Answer</summary>
TCP
</details>

---

## **Counting & Classifying Intrusions — Medium (100 pts)**

---

### **4) Top Intrusion Rule & Total Rules**
What is the Top Intrusion Rules/How Many Different Intrusion Rules are there?

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test 
| stats count by IntrusionRuleMessage 
| sort - count
```

</details>

<details><summary>Answer</summary>
FILE-EXECUTABLE download of executable content (8 rules total).
</details>

---

### **5) Top Classification & Total Classifications**
What is the Top classification?/How many different Classifications are there?

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test 
| stats count by Classification 
| sort -count
```
</details>

<details><summary>Answer</summary>
Potential Corporate Policy Violation (5 total)
</details>

---

### **6) Level 5 Impact Events**

How many Level 5 Impact Intrusion Event Categories do we have?
<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test Impact>4 
| stats count by IntrusionRuleMessage Impact 
| sort -Impact
```
</details>

<details><summary>Answer</summary>
5
</details>

---

## **Network Source / Destination — Medium (100 pts)**

---

### **7) Attacker from Germany**

What's the IP of the external attacker from Germany?

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test 
| stats count by InitiatorIP InitiatorCountry
```
</details>

<details><summary>Answer</summary>
192.168.1.100
</details>

---

### **8) Most Targeted Internal IP**

What's the IP of the most targeted internal IP?

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test 
| stats count by ResponderIP | sort -count
```
</details>

<details><summary>Answer</summary>
172.16.3.110
</details>

---

### **9) Most Active Attacker IP**

What external/attacker IP had the highest number of intrusion attempts?

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test 
| stats count by InitiatorIP | sort -count
```
</details>

<details><summary>Answer</summary>
146.75.78.172
</details>

---

### **10) Port 4444 — Target Ports**
Attackers are starting a connection and sending initial requests through port 4444. What are the two different corresponding ports that are receiving and responding to this connection? 

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test InitiatorPort=4444
| stats count by InitiatorPort, ResponderPort | sort -count
```
</details>

<details><summary>Answer</summary>
58090 and 8342
</details>

---

## **Suspicious Activity Detection — Hard (150 pts)**

---

### **11) Most Common Attack Pattern**

What's the most common attack pattern (Signature ID and Classification and in what country is it being deployed in?

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test
| stats count by InitiatorCountry, SignatureID, Classification, 
| sort -count
```
</details>

<details><summary>Answer</summary>
15306 : Potential_Corporate_Policy_Violation : United_States
</details>

---

### **12) Web App Triggering Most Alerts**

Which web application triggered the most intrusion alerts?

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test | stats count by WebApplication | sort -count
```
</details>

<details><summary>Answer</summary>
Microsoft_Update
</details>

---

### **13) Hidden .txt File**
Look for the hidden .txt file containing a flag.

<details><summary>Query</summary>

```
index=firewall sourcetype=intrusion_logs HTTP_URI="*.txt"
```
</details>

<details><summary>Answer</summary>
FLAG{The_SOC_IS_AWESOME}
</details>

---

### **14) Flag Hidden in Hostname**

The flag is hidden in the hostname. Try filtering to find the specific hostname.

<details><summary>Query</summary>

```
index=firewall sourcetype=intrusion_logs HTTP_Hostname="*flag*"
```
</details>

<details><summary>Answer</summary>
flag{SplunkHunters_HTTP_Challenge_2025}
</details>

---

### **15) Attacker with Most Unique Classifications**

Which initiator/attacker IP is associated with the most multiple classifications?

<details><summary>Query</summary>

```
index=main sourcetype=Sample_Data_Test 
| stats dc(Classification) as unique_classes by InitiatorIP 
| sort -unique_classes
```
</details>

<details><summary>Answer</summary>
23.48.99.12
</details>

---

# Conclusion

You now have hands-on experience with:

- SPL fundamentals  
- Investigating attacker patterns  
- Identifying encoded/hidden data  
- Working with web, firewall, and intrusion logs  
- Building Splunk alerts  
- Performing SOC-style investigations  

Feel free to expand the lab, create your own datasets, or build new challenges!