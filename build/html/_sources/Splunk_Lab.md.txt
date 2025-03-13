# Welcome to the Splunk Lab

## Overview
In this lab we will teach you how to setup your own Splunk server. You will also learn how you can forward logs from different endpoint devices to your Splunk logs, aka ingesting logs. After you get comfortable ingesting logs we will also be generating our own log sources and learning how we can ingest those logs too. 

### Technologies you will use
- Splunk Enterprise
- Splunk Universal Forwarder
- Linux - Debian
- Windows
- Sysmon

As more and more people complete the beginner lab we will start working on a more advanced lab for people interested in learning more about Splunk.

## Lab Structure
1. We give you a task. We want you to figure out as much as you can by yourself so the instructions will be very minimal.
2. If you get stuck on a task feel free to take a look at the hints section.
3. Don't be discouraged as we also share the answers.

## Setup

You have 2 options for this lab. To follow along this lab you can either use the SDC cloud or use your local machine to build the lab. I recommend the SDC cloud as it is simpler than trying to install your own virtual machine on your own computer. 

### Cloud instance

1. First you will need to download and install [Pritunl](https://client.pritunl.com/#install)

2. Next contact the Student Data Center to get VPN credentials

3. Import the profile provided to you by the MC Hill bot. Dont enter a profile url

4. Once Imported, connect to the sdc_vpn and use the credentials given to you

5. Open up a web browser and navigate to https://kamino.calpolyswift.org/#/

6. Register an account and login

7. Create a pod 

8. In a new tab navigate to https://elsa.sdc.cpp/

9. Login using the account you created in step 6

10. Power on the VMs provided

You are now ready to start the lab.


### Local Instance

1. Download and install Virtual Box or Vmware Player
2. Download the Debian ISO file
3. Create a new VM using the Debian ISO file
4. Start the VM
Install Splunk on a debian machine.


## Task 1 - Setting up Splunk Server
After you complete the setup of the lab, we will now work with the vm called "debian". 

The task is to create our very own Splunk server. When I say create I simply mean install the Splunk Enterprise Trial. So see if you can install that on the debian vm.

If you are stuck or donno where to start check the hints. Good luck!

### Hints
<details close>
<summary>Hint 1</summary>
You can download the installer at https://www.splunk.com/
<br> You will need a Splunk account.
</details>

<details close>
<summary>Hint 2</summary>
We need a way to install the package we just downloaded. In debian we can use the dpkg command to install packages.
</details>

<details close>
<summary>Hint 3</summary>
Just because you installed it doesnt mean its running.
</details>

### Answer
<details close>
<summary>Answer</summary>
<details close>
<summary>You sure?</summary>
Download the Splunk Enterprise Trial with the command below
<br>  
<code>
wget -O splunk-9.2.1-78803f08aabb-linux-2.6-amd64.deb "https://download.splunk.com/products/splunk/releases/9.2.1/linux/splunk-9.2.1-78803f08aabb-linux-2.6-amd64.deb"
</code>
<br> 
Navigate to the folder you downloaded the file and run the command 
<code>
dpkg -i plunk-9.2.1-78803f08aabb-linux-2.6-amd64.deb
</code>
 
Navigate to the folder /opt/splunk/bin and run 
<code>
cd /opt/splunk/bin
./splunk start
</code>

Open up firefox and browse to localhost:8000
Login with the user account you created when installing Splunk
</details>
</details>



## Task 2 - Forwarding Logs to Splunk
Congratulations if you made it this far that means you successfully setup your own Splunk server!

If you havent already, I encourage you to take explore the UI of Splunk. It will be quite a lot to absorb at first but I promise you as you keep using Splunk you will get used to the UI. 

Now that we set up a Splunk server we need to figure out how we can ingest logs into it. We ingest logs using something called the Splunk Universal Forwarder. This is a tool installed on an endpoint device that tells the computer which logs to send and where to send them. 

Task 2 is to install the Splunk Universal Forwarder on the Windows Client and see if you can query the logs using the Splunk Search App.

If you are able to see data when searching index=main you have successfully completed the task.

### Hints
<details close>
<summary>Hint 1</summary>
You can also download the Splunk Universal Forwarder at https://www.splunk.com/
<br> You will need a Splunk account.
</details>

<details close>
<summary>Hint 2</summary>
Did you configure your Splunk server to listen?
Did you open up firewall ports?
</details>

<details close>
<summary>Hint 3</summary>
When you install the Splunk Universal Forwarder in the customize option make sure you are installing with the local account. Using a virtual account may not send logs due to permission issues.
</details>

### Answer
<details close>
<summary>Answer</summary>
<details close>
<summary>You sure?</summary>
Download the Splunk Universal Forwarder. You can either log into the Splunk website with your account and download the windows version. Or do the same with this command
<br>  
<code>
wget -O splunkforwarder-9.2.1-78803f08aabb-x64-release.msi "https://download.splunk.com/products/universalforwarder/releases/9.2.1/windows/splunkforwarder-9.2.1-78803f08aabb-x64-release.msi"
</code>
<br> 
Navigate to the folder you downloaded the file and run the msi file 
Agree to the license and install using custom options. Make sure to choose option local account. Select any logs you want to forward. Input the IP address of the Splunk server and use the default ports. 
  
Open up Windows Firewall and open up outbound ports for TCP AND UDP for 8089 and 9997.
  
On your Splunk Server login using the credentials you created and go to Settings->Forwarding and Receiving and nder the Receive Data section click on +Add New. Enter 9997 as listening port and save.
  
Go to your Splunk Search Head and search index=main.
You should see data in this index after a few minutes.
  
  </details>
</details>

## Task 3 - Generating Custom Log Sources
If you come this far pat yourself on the back!
You essentially now have a good understanding on how logs are ingested into Splunk and you know how to query the data.


Task 3 is to install Sysmon and ingest the logs Sysmon generates into Splunk.

  
If you enjoyed this lab and want to learn more feel free to reach out to us on Discord!

## Task 4 - Custom Indexes
Wow you really must like Splunk if you came this far ;)
Notice how all your indexes are being sent to main by default. Imagine ingesting 100s of log sources into main. How messy does that look. It would also be a nightmare querying specific data and very inefficient. 

Task 4 is to create a new index and change the behaviour of the Universal Forwarder. 
Let create an index called Sysmon and forward the Sysmon logs to this index called Sysmon instead of main.



## Whats next?
Congratulations you have completed the Splunk Lab! 

Hope you enjoyed the lab! If you want to work on more Splunk stuff or like what you see at the SOC, I encourage you to get involved and start working on your own cool project :). You are now dubbed Splunk Pro!

Stay tuned for a more advanced Splunk Lab where we plan to tackle the following questions:

-How do I scale my Splunk deployment?
-How do I make my Splunk server more resilient?
-How do I increase search performance?