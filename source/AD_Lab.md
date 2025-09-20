# Active Directory Lab Setup

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

## Lab Setup: Primary Domain Controller

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

Go ahead and open file explorer and navigate to the same virtio-win virtual CD Drive

![File explorer showing virtio-win CD drive](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/15.png)

scroll through the drive

![Scrolling through the drive contents](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/16.png)

find `virtio-win-gt-x64.msi` and run that installer

![Running the virtio-win-gt-x64.msi installer](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/17.png)

Proceed with next and accept the EULA

![Installer EULA screen](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/18.png)

Now after accepting the EULA, you will prompted with installing many different features,

The following feature we are looking to add is marked as "Network", once you select it, click next.

![Selecting Network feature in installer](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/19.png)

Then click install.

![Clicking install](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/20.png)

After a Windows Pop-up will occur asking if you want to make your PC discoverable, you can click yes.

![Windows discoverable PC pop-up](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/21.png)

![Windows discoverable PC pop-up part 2](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/22.png)

Now you the red internet icon you are seeing at the bottom, should have disappeared and your machine should look like you have internet now.

A way to make sure your machine is reachable through the Internet, Open up Command Prompt

Use `Win + R` or Windows Key and type "run" into Search to open the Run Page

![Opening Run dialog](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/23.png)

Program we want to open is `cmd.exe` and click ok

![Running cmd.exe](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/24.png)

Now that we have the Command Prompt open, lets ping a well known source that is reliably online, Google.

type into your command prompt `ping google.com`

Expected results are 4 packets sent with 100% received and 0% loss

![Pinging google.com in command prompt](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/25.png)

Now that we are aware this device is able to reach the actual Internet, now lets figure its local ip address to RDP into the machine.

In the same command prompt box type in `ipconfig`

![Running ipconfig in command prompt](https://www.cppsoc.xyz/assets/documentation/ad-lab/pdc/26.png)

Now that you see all these addresses, the one we are looking for is IPv4 Address, for my current machine its `192.168.1.116`

This IP address is specific to this Virtual Machine and the way

Now you need to understand that this IP address is local to the "Router" you are connected to. In your case we provision a virtual pfSense router to your pod that has an IP Address to the router, typically formatted in `172.16.x.x`, meaning that is your external address. But locally when you are connected to that LAN of this network, you are accessible as `192.168.1.116`, but externally your machine is reached as `172.16.x.116`. The `x` part in that external address will depend on your pod number, typically represented as `10xx_windows_ad_splunk_lab`. taking that `xx` in the pod number will be part of your WAN address. Even if you still cannot find out what your pod number is, you can remote into your virtual router and look at the WAN address that first comes up (If it says `172.16.1.1`, click enter to refresh the page and a different WAN should appear)

This was a bit of a tangent and very surface level understanding on how the router connects, I hope I will shorten it and explain it better later.

If you think you understand how to access the machine externally, try pinging your Windows VM from your own device while connected to the vpn.
