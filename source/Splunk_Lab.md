# Welcome to the Splunk Lab

## Overview

In this lab, we will teach you how to set up your own Splunk server. You will also learn how you can forward logs from different endpoint devices to your Splunk logs, aka ingesting logs. After you get comfortable ingesting logs, we will also be generating our own log sources and learning how we can ingest those logs too. At the end of this lab, you should be comfortable with operating between different operating systems, familiarity with terminal, and how to parse different types of logs across different operating systems.

### Technologies you will use

- Splunk
- Splunk Universal Forwarder
- Linux - Debian
- Windows
- Sysmon

As more people complete the beginner lab, we will start working on a more advanced lab for people interested in learning more about Splunk.

## Lab Structure

1.  We give you a task. We want you to figure out as much as you can by yourself, so the instructions will be very minimal.
2.  If you get stuck on a task, feel free to take a look at the hints section.
3.  Don't be discouraged, as we also share the answers.

## Setup

To follow along with this lab, you can use the Student Data Center to provision your virtual machines and get comfortable with the remote/cloud environment. Setting this up locally on your own hardware is possible, but these instructions will not outline the setup there.

1.  Start reading through [Getting Started](https://wiki.cppsoc.xyz/en/latest/getting_started.html).

2.  Request Login Credentials (AD) from a Student Director.

3.  Login to [Kamino](https://kamino.sdc.cpp).

4.  Create a pod based off our Template: `SOC intro splunk lab - Splunk Lab 2025`.

5.  Provisioning these pods takes a bit of time; refresh the page periodically to see if 3 Virtual Machines and 1 pfSense Router are created.

6.  Login to [Proxmox VE](https://proxmox.sdc.cpp) to see your provisioned virtual machines in detail.

    > After you log in, we recommend changing your view mode at the top left to 'Pool View' to better see the VMs and Resource Pool Assigned to you.

7.  Power on the VMs provided to you.

You are now ready to start the lab.

## Tips

> **Tip #1: Slow Download Speeds?**
> The SDC is running into internet speed issues depending on where your Virtual Machine is being hosted. In more detail, depending on your Virtual Machine's location, your download speeds over the WAN might be at kb/s when downloading packages, etc.
>
> A cool workaround we have at the moment is that the LAN is not speed-limited at all. If you have a machine that is on the same network (Your Laptop or PC connected to GlobalProtect VPN), you can use a command-line utility called `scp` (Secure Copy) to actually copy files through your remote shell over to the target machine. This will make more sense for Task #1 specifically, but this is your introduction to the `scp` command.

> **Tip #2: External Accessibility**
> On top of that, with that pfSense router provisioned to you, your VMs in your resource pool are 'externally' accessible! 'Externally' in quotes because anyone on the GlobalProtect VPN can access it if they know the subnet and IP of your machines. This is not 'externally' as in on the WAN of the GlobalProtect router. So using the `scp` command-line in combination with knowing how the router is configured will allow you to do many more things outside of the 'Proxmox Virtual Environment', but allow you to SSH into your Virtual Machines and or RDP into your Windows Clients.

## Task 1 - Setting up Splunk Enterprise Server

After you complete the setup of the lab, we will now work with the VM called "server-debian-clone".

The task is to create our very own Splunk server. When I say create, I simply mean install the Splunk Enterprise Trial. So see if you can install that on the Debian VM.

If you are stuck or don't know where to start, check the hints. Good luck!

### Hints

<details>
<summary>Hint 1</summary>
You can download the installer at https://www.splunk.com/.
You will need a Splunk account.
</details>

<details>
<summary>Hint 2</summary>
We need a way to install the package we just downloaded. In Debian, we can use the `dpkg` command to install packages.
</details>

<details>
<summary>Hint 3</summary>
Just because you installed it doesn't mean it's running.
</details>

### Answer
<details>
<summary>Answer</summary>
<details>
<summary>You sure?</summary>

1.  **Download the Splunk Enterprise Trial:**
    Use the following command to download the installer:
    ```bash
    wget -O splunk-9.2.1-78803f08aabb-linux-2.6-amd64.deb "https://download.splunk.com/products/splunk/releases/9.2.1/linux/splunk-9.2.1-78803f08aabb-linux-2.6-amd64.deb"
    ```
    > **Note on slow downloads:** If `wget` is slow, you can download the file on your local machine and use `scp` to transfer it to your VM. For example:
    > ```bash
    > scp ./splunk-9.2.1-78803f08aabb-linux-2.6-amd64.deb root@172.16.x.xxx:/path/on/vm
    > ```

2.  **Install the package:**
    Navigate to the directory where you downloaded the file and run:
    ```bash
    dpkg -i splunk-9.2.1-78803f08aabb-linux-2.6-amd64.deb
    ```

3.  **Start Splunk:**
    Change to the Splunk binary directory and start the service:
    ```bash
    cd /opt/splunk/bin
    ./splunk start
    ```
    You will be prompted to accept the license and create an administrator account.

4.  **Access Splunk Web:**
    Open a web browser on your VM and go to `http://localhost:8000`. Log in with the credentials you just created.

</details>
</details>

## Task 2 - Forwarding Logs from a Windows Machine to your Splunk Server

Congratulations! If you made it this far, that means you successfully set up your own Splunk server!

If you haven't already, I encourage you to explore the UI of Splunk. It will be quite a lot to absorb at first, but I promise you, as you keep using Splunk, you will get used to the UI.

Now that we have set up a Splunk server, we need to figure out how we can ingest logs into it. We ingest logs using something called the **Splunk Universal Forwarder**. This is a tool installed on an endpoint device that tells the computer which logs to send and where to send them.

Task 2 is to install the Splunk Universal Forwarder on the Windows Client and see if you can query the logs using the Splunk Search App.

If you are able to see data when searching `index=main`, you have successfully completed the task.

### Hints

<details>
<summary>Hint 1</summary>
You can also download the Splunk Universal Forwarder at https://www.splunk.com/.
You will need a Splunk account.
</details>

<details>
<summary>Hint 2</summary>
Did you configure your Splunk server to listen?
Did you open up firewall ports?
</details>

<details>
<summary>Hint 3</summary>
When you install the Splunk Universal Forwarder, in the customize option, make sure you are installing with the local account. Using a virtual account may not send logs due to permission issues.
</details>

### Answer

<details>
<summary>Answer</summary>
<details>
<summary>You sure?</summary>

1.  **Download the Splunk Universal Forwarder:**
    You can either log into the Splunk website with your account and download the Windows version, or use this command:
    ```powershell
    Invoke-WebRequest -Uri "https://download.splunk.com/products/universalforwarder/releases/9.2.1/windows/splunkforwarder-9.2.1-78803f08aabb-x64-release.msi" -OutFile splunkforwarder-9.2.1-78803f08aabb-x64-release.msi
    ```

2.  **Install the Forwarder:**
    - Navigate to the folder where you downloaded the file and run the `.msi` installer.
    - Agree to the license and install using custom options.
    - Make sure to choose the **local account** option.
    - Select any logs you want to forward.
    - Input the IP address of the Splunk server and use the default ports.

3.  **Configure Firewall:**
    - Open up Windows Firewall and create outbound rules for TCP and UDP for ports `8089` and `9997`.

4.  **Configure Splunk Server:**
    - On your Splunk Server, log in and go to `Settings` -> `Forwarding and Receiving`.
    - Under the "Receive Data" section, click on `+Add New`.
    - Enter `9997` as the listening port and save.

5.  **Verify Data Ingestion:**
    - Go to your Splunk Search Head and search `index=main`.
    - You should see data in this index after a few minutes.

</details>
</details>

## Task 3 - Forwarding Logs from a Ubuntu Client to your Splunk Server

With this task, it will be similar in its function with the previous forwarder task. Your goal is to install a forwarder on a client, but this time, Linux-based.

There will be less of a GUI to use, unlike Windows, so you will be mainly operating out of your terminal.

I have removed the hints from this section but will give you the short rundown of what you need:

-   Find a `.deb` package from [splunk.com](https://download.splunk.com) for a Universal Forwarder (UF) for a Debian-based machine.
-   The installation steps will be similar to installing your Splunk Server, like reading through the EULA and starting the forwarder.
-   You will also need to make `iptables` rules, similar to how you created firewall rules on Windows, to communicate with your Splunk Server.

Good Luck!

If you struggle with this, that is okay. That was the goal of this task, and instead of walking you through it, you can ask a Student Director for help!

## Task 4 - Generating Custom Log Sources

If you have come this far, pat yourself on the back! You essentially now have a good understanding of how logs are ingested into Splunk, and you know how to query the data.

Task 4 is to install Sysmon and ingest the logs Sysmon generates into Splunk.

If you enjoyed this lab and want to learn more, feel free to reach out to us on Discord!

## Task 5 - Custom Indexes

Wow, you really must like Splunk if you came this far! ;)

Notice how all your indexes are being sent to `main` by default. Imagine ingesting hundreds of log sources into `main`. How messy does that look? It would also be a nightmare and very inefficient to query specific data.

Task 5 is to create a new index and change the behavior of the Universal Forwarder. Let's create an index called `sysmon` and forward the Sysmon logs to this index instead of `main`.

## What's next?

Congratulations, you have completed the Splunk Lab!

Hope you enjoyed the lab! If you want to work on more Splunk stuff or like what you see at the SOC, I encourage you to get involved and start working on your own cool project :). You are now dubbed a Splunk Pro!

Stay tuned for a more advanced Splunk Lab where we plan to tackle the following questions:

-   How do I scale my Splunk deployment?
-   How do I make my Splunk server more resilient?
-   How do I increase search performance?
