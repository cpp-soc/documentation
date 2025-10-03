# Active Directory Lab Setup test

## Introduction

This guide provides a step-by-step walkthrough for setting up a basic Active Directory lab environment. You will learn how to configure a Domain Controller (DC), manage static IPs, create a domain, and join client machines to that domain. Additionally, we will cover DNS record creation and log forwarding.

## Lab Objectives

This lab simulates a typical corporate or homelab infrastructure, enabling you to:
- Centralize user authentication and management.
- Regulate user access to devices.
- Establish a secure process for network and computer access.

This lab integrates concepts from **Networking**, **Infrastructure**, and **Security**.

## Requirements

To complete this lab, you will need the following:

1.  **GlobalProtect**: To access the SDC Environment.
2.  **Windows Server 20XX**: To act as our Primary DC.
3.  **Windows Server 20XX**: To act as our Secondary DC for fault tolerance.
4.  **Windows 1X**: To act as a client machine.
5.  **Windows 1X**: To act as another client machine.
6.  **Linux**: To act as our Splunk Server for log forwarding and AD-based authentication.

**Note on Fault Tolerance:** Having a secondary DC is crucial for redundancy and backup, as services can fail unexpectedly.

These Windows VMs should be generated from a template. If not, ensure you have four VMs that can communicate with each other, preferably on the same VLAN.

All these Virtual Machine's are going to be left in a setup phase, meaning you will be spending time download packages, setting passwords, etc.

## Primary Domain Controller

Let's begin by configuring our first VM, which will serve as the Primary Domain Controller (PDC). For this guide, we are using a **Windows Server 2019** virtual machine.

<details>
<summary>1. Start the <strong>Windows Server 2019 - PDC</strong> virtual machine. You should be greeted with the Windows Setup screen.</summary>

*Image of the Windows Setup screen.*

</details>
<details>
<summary>2. Click <strong>Install Now</strong>.</summary>

![Image showing the 'Install Now' button.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/1.png)

</details>
<details>
<summary>3. For the operating system, select <strong>Windows Server 2019 Standard Evaluation (Desktop Experience)</strong> and click <strong>Next</strong>.</summary>

> **Note:** Choosing an option without "Desktop Experience" will result in a command-line-only interface (PowerShell).

![Image of the OS selection screen.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/2.png)

</details>
<details>
<summary>4. Accept the license terms (EULA) and click <strong>Next</strong>.</summary>

![Image of the EULA screen with the 'Next' button highlighted.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/3.png)

</details>
<details>
<summary>5. Select <strong>Custom: Install Windows only (advanced)</strong>.</summary>

> The "Upgrade" option is not applicable here since we are performing a clean installation.

![Image of the installation type selection screen.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/4.png)

</details>

### Loading VirtIO Drivers (Proxmox)

If you are using Proxmox or a similar KVM-based hypervisor, you will need to load VirtIO drivers for the installer to recognize the virtual hard disk.

<details>
<summary>1. Click <strong>Load Driver</strong>.</summary>

> **Note:** These drivers are necessary for virtualized hardware to perform correctly. In our lab template, the driver disk is pre-mounted. If you're setting up a VM from scratch in a Proxmox environment, you'll need to mount the VirtIO driver ISO yourself.

![Image showing the 'Load Driver' button.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/5.png)

</details>
<details>
<summary>2. Click <strong>Browse</strong>.</summary>

![Image showing the 'Browse' button.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/6.png)

</details>
<details>
<summary>3. Locate the virtual CD drive, which should be labeled something like <code>virtio-win-x.x.xxx</code>.</summary>

![Image showing the file browser with the virtual CD drive highlighted.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/7.png)

</details>
<details>
<summary>4. Navigate to the <code>vioscsi</code> folder, then select the folder corresponding to your OS version (e.g., <code>2k19</code> for Windows Server 2019), and finally select the <code>amd64</code> folder. Click <strong>OK</strong>.</summary>

![Image showing the folder structure for the VirtIO driver.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/8.png)

</details>
<details>
<summary>5. The installer should find the <strong>Red Hat VirtIO SCSI pass-through controller</strong> driver. Select it and click <strong>Next</strong> to install it.</summary>

![Image showing the driver selection screen with the correct driver highlighted.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/9.png)

</details>

### Partitioning and Installation

<details>
<summary>1. After the driver is installed, you will see the virtual drive. Select it and click <strong>New</strong>.</summary>

![Image showing the virtual drive and the 'New' button.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/10.png)

</details>
<details>
<summary>2. Allocate the maximum available space for the new partition. Windows Setup may create a small, separate "System Reserved" partition; this is normal. Click <strong>Apply</strong> and then <strong>OK</strong>.</summary>

![Image showing the partition size allocation and confirmation prompt.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/11.png)

</details>
<details>
<summary>3. Select the largest partition (marked as "Primary") and click <strong>Next</strong> to begin the Windows installation.</summary>

![Image showing the primary partition selected and the 'Next' button highlighted.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/12.png)

![Image of the Windows installation progress screen.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/13.png)

</details>
<details>
<summary>4. Windows will now install. This process may take some time.</summary>

![Image of the password creation screen for the Administrator account.](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/14.png)

</details>
<details>
<summary>5. Once the installation is complete, the VM will restart, and you will be prompted to set a password for the local <strong>Administrator</strong> account. Choose a secure password and complete the setup.</summary>

*No photo taken; but if you need help, reach out!*

</details>

### Post-Installation Setup

Okay, now at this point of the setup, you have been interacting with this VM through the browser, through the Console tab. If that is your preference, you can continue to do this lab in that experience, but in my personal preference, I very much enjoy either my own machine and to RDP into client (specifically for Windows).

I recommend you to use RDP instead of the browser in case of compatibility issues and overall better user experience.

The following steps will explain you how to connect this device to the internet, setting an IP and enabling remote desktop.

So first, now that your VM has finished setting up, let's login to your Administrator account you just setup for yourself.

You might notice that your machine although you assigned virtual i/o drivers before hand is still having internet connectivity issues.

That is okay, we will resolve that right now.

<details>
<summary>1. Go ahead and open file explorer and navigate to the same virtio-win virtual CD Drive.</summary>

![File explorer showing virtio-win CD drive](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/15.png)

</details>
<details>
<summary>2. Scroll through the drive.</summary>

![Scrolling through the drive contents](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/16.png)

</details>
<details>
<summary>3. Find <code>virtio-win-gt-x64.msi</code> and run that installer.</summary>

![Running the virtio-win-gt-x64.msi installer](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/17.png)

</details>
<details>
<summary>4. Proceed with next and accept the EULA.</summary>

![Installer EULA screen](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/18.png)

</details>
<details>
<summary>5. After accepting the EULA, you will be prompted with installing many different features. The feature we are looking to add is marked as "Network". Once you select it, click next.</summary>

![Selecting Network feature in installer](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/19.png)

</details>
<details>
<summary>6. Then click install.</summary>

![Clicking install](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/20.png)

</details>
<details>
<summary>7. A Windows Pop-up will occur asking if you want to make your PC discoverable. You can click yes.</summary>

![Windows discoverable PC pop-up](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/21.png)

![Windows discoverable PC pop-up part 2](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/22.png)

</details>

Now you the red internet icon you are seeing at the bottom, should have disappeared and your machine should look like you have internet now.

A way to make sure your machine is reachable through the Internet, Open up Command Prompt.

<details>
<summary>1. Use <code>Win + R</code> or Windows Key and type "run" into Search to open the Run Page.</summary>

![Opening Run dialog](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/23.png)

</details>
<details>
<summary>2. The program we want to open is <code>cmd.exe</code>. Click OK.</summary>

![Running cmd.exe](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/24.png)

</details>
<details>
<summary>3. Now that we have the Command Prompt open, lets ping a well known source that is reliably online, Google. Type into your command prompt <code>ping google.com</code>.</summary>

Expected results are 4 packets sent with 100% received and 0% loss

![Pinging google.com in command prompt](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/25.png)

</details>

Now that we are aware this device is able to reach the actual Internet, now lets figure its local ip address to RDP into the machine.

<details>
<summary>1. In the same command prompt box type in <code>ipconfig</code>.</summary>

![Running ipconfig in command prompt](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/26.png)

</details>

Now that you see all these addresses, the one we are looking for is IPv4 Address, for my current machine its `192.168.1.116`

This IP address is specific to this Virtual Machine and the way

Now you need to understand that this IP address is local to the "Router" you are connected to. In your case we provision a virtual pfSense router to your pod that has an IP Address to the router, typically formatted in `172.16.x.x`, meaning that is your external address. But locally when you are connected to that LAN of this network, you are accessible as `192.168.1.116`, but externally your machine is reached as `172.16.x.116`. The `x` part in that external address will depend on your pod number, typically represented as `10xx_windows_ad_splunk_lab`. taking that `xx` in the pod number will be part of your WAN address. Even if you still cannot find out what your pod number is, you can remote into your virtual router and look at the WAN address that first comes up (If it says `172.16.1.1`, click enter to refresh the page and a different WAN should appear)

This was a bit of a tangent and very surface level understanding on how the router connects, I hope I will shorten it and explain it better later.

If you think you understand how to access the machine externally, try pinging your Windows VM from your own device while connected to the GlobalProtect VPN. If this still does not work and you cannot ping your virtual machine from your physical machine, check the IP address and make sure you understand how we are getting each octet of the address.

### Enabling Remote Desktop Access

<details>
<summary>1. If you can ping your machine from your physical machine, you should now know the address of the machine and can access it externally. Go back to Proxmox and open the console for the Windows VM one more time to enable Remote Desktop.</summary>

> **Note:** You can access the machine using either the External IP of your VM or the actual Computer Name if you know it. You might encounter issues regarding Network Level Authentication, which must be disabled in the Remote Desktop settings.

</details>

At this point of the lab, you should have a ready Windows Server 2019 Machine and have an understanding of how the networking works within your deployed pod. This next part of the lab will now focus on setting up your domain and will be more hands-on and less of a tutorial.

### Server Manager Configuration

<details>
<summary>1. Open <strong>Server Manager</strong> and browse around to see what features are available in this Server edition of Windows.</summary>

> From the Server Manager, you can see many different features typically not available on Home and even Pro editions of Windows.

</details>

### Setting Computer Name and Static IP

<details>
<summary>1. Change the <strong>Computer name</strong> to something more recognizable so you can type in a name instead of remembering the IP Address when remoting in.</summary>

> For the sake of this lab environment, we will have a consistent naming system for all clients. Rename your Windows VM to **FirstInitialLastName-DC01** (e.g., **JMama-DC01**) and then click **Apply**.

</details>

<details>
<summary>2. Before restarting your computer, set a <strong>static IP</strong> for your machine to ensure that when you restart, the IP doesn't change and you can still remote back into the machine.</summary>

> **Tip:** If you are unsure about all the settings you need for the IPv4 configuration, running `ipconfig` in Command Prompt will help guide you with the current network settings.

</details>

<details>
<summary>3. After you set the computer name and static IP for your machine, restart your VM through Windows to ensure all settings are applied.</summary>

> This restart ensures that both the computer name change and static IP configuration take effect properly.

</details>

### Installing Server Roles and Features

<details>
<summary>1. Now that you have browsed around, locate the <strong>Manage > Add Roles and Features</strong> button at the top right of Server Manager.</summary>

Install the following server roles and features:
- **Active Directory Domain Services**
- **Active Directory Federation Services** 
- **Active Directory Lightweight Directory Services**
- **Active Directory Rights Management Services**
- **DNS Server**

</details>

<details>
<summary>2. Proceed through the Add Roles and Features Wizard, accepting any dependency services that are required.</summary>

> **Note:** The wizard may prompt you to install additional features that are dependencies for the roles you selected. Accept these to ensure proper functionality.

</details>

<details>
<summary>3. Once the feature installation completes, restart your server.</summary>

> After restarting, your Server Manager may show red indicators - this is normal and expected at this stage.

</details>

### Promoting to Domain Controller

<details>
<summary>1. We are going to configure this server step by step to handle all the issues. Open the <strong>AD DS</strong> tab and promote this machine to being a Domain Controller.</summary>

> **Note:** You will likely see a yellow message saying "configuration required" - this is what we're addressing now.

</details>

<details>
<summary>2. When you attempt to promote this machine to a Domain Controller, an <strong>Active Directory Domain Services Configuration Wizard</strong> should appear. Work through the wizard.</summary>

> Continue through the initial setup screens of the configuration wizard.

</details>

<details>
<summary>3. When it comes to choosing your domain, use a similar naming style as we used for the machine names. Create a new forest and set your domain to <strong>FirstInitialLastName.soc</strong> (e.g., <code>tphao.soc</code>).</summary>

> **Important:** This domain name will be used throughout your other DNS services like Splunk later in the lab.

</details>

<details>
<summary>4. Continue through the wizard and complete promoting this VM to being a Domain Controller.</summary>

> Follow the remaining prompts in the wizard, accepting the default settings unless you have specific requirements.

</details>

### Post-Promotion Configuration

<details>
<summary>1. Once promotion is complete, a restart will occur where the Group Policy Client gets installed. You should see a user appear with the first part of the root domain you chose (e.g., <code>JMama\ADMINISTRATOR</code>).</summary>

> Log in with the password you set beforehand - this is now your Administrator account for your Domain.

</details>

<details>
<summary>2. Now that you have completed the domain setup, you can explore your domain by opening <strong>Active Directory Users and Computers</strong>.</summary>

> Right-click and manage the new domain you created. You can see default created organizational units (OUs), users, group policy objects, etc.

> Let's open up the folder called Users and create a user inside there. I am going to call mine Test and use this as an account to test if my clients join the domain successfully and I can login under this domain.

</details>

### Lab Progress Check

At this point in the lab, you should be proud of what you have accomplished:

- ✅ Deployed a Windows Server 2019 Virtual Machine
- ✅ Loaded necessary drivers for Virtual Hard Disk and Virtual Networking
- ✅ Utilized the virtual router and 1:1 NAT to remotely access your machine
- ✅ Set static names and IP addresses for VM stability
- ✅ Installed Windows Server features like Active Directory Domain Services
- ✅ Promoted the VM to a Domain Controller
- ✅ Created a domain for clients to join

### Final Verification

<details>
<summary>1. As a final check before continuing, open <strong>PowerShell</strong> and run the following command to verify domain membership:</summary>

```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object Domain, PartOfDomain
```

Your results should look similar to this:

```
Domain    PartOfDomain
------    ------------
tphao.soc         True
```

</details>

### What's Next?

We are going to proceed with adding clients to this domain and joining Windows 10 client machines to our newly created domain!

## Windows Client - 1

Now that you are experienced in deploying virtual machines in our environment, the instructions will be less guided and focus on specific goals and objectives.

### Windows 10 Installation

<details>
<summary>1. Start up one of your two <strong>Windows 10</strong> virtual machines and proceed with completing the installation on the VM.</summary>

> Follow the standard Windows 10 installation process. The steps should be familiar from the Windows Server installation you just completed.

</details>

### Client Configuration

<details>
<summary>1. Once Windows 10 boots, set a <strong>static IP</strong> for this machine to ensure network stability.</summary>

> Use a different IP address than your Domain Controller, but within the same subnet (e.g., if your DC is `192.168.1.116`, use `192.168.1.117` for the client).

> Note for the DNS settings, set your primary DNS to be the same IP as your domain controller!

</details>
<details>
<summary>2. Set a common name for this PC following our naming convention: <strong>FirstInitialLastName-client01</strong> (e.g., <code>JMama-client01</code>).</summary>

> This naming convention helps maintain consistency across your lab environment and makes it easier to identify different machines.

</details>

### Joining the Domain

<details>
<summary>1. Now we are going to join the domain we created earlier (e.g., <code>JMama.soc</code>). Locate the field where you can join this computer to that domain.</summary>

> **Hint:** Look in the System Properties under "Computer name, domain, and workgroup settings." You'll need to change from a workgroup to a domain.

</details>
<details>
<summary>2. When prompted for credentials during the domain join process, use your Domain Administrator account.</summary>

> Use the domain administrator credentials you set up on your Domain Controller (e.g., `JMama\Administrator`).

</details>

### Domain Login Testing

<details>
<summary>1. If configured correctly and joining the domain was successful, log out and log back in using the test account we created on the Domain Controller.</summary>

> Switch from the local machine login to the domain login. You should be able to select your domain from the login screen and use the test account credentials.

</details>
<details>
<summary>2. If you forgot your test account password, resetting it on the Domain Controller is easy - simply right-click the user in Active Directory Users and Computers and select "Reset Password".</summary>

> This demonstrates the centralized user management capability of Active Directory.

</details>


### What's Next?

Congratulations! You now have a Windows 10 client successfully joined to your Active Directory domain. This client can now authenticate against your Domain Controller and access domain resources based on the permissions you configure.
