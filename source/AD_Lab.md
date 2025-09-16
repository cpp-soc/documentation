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

*Image showing the 'Install Now' button.*

</details>
<details>
<summary>3. For the operating system, select <strong>Windows Server 2019 Standard Evaluation (Desktop Experience)</strong> and click <strong>Next</strong>.</summary>

> **Note:** Choosing an option without "Desktop Experience" will result in a command-line-only interface (PowerShell).

*Image of the OS selection screen.*

</details>
<details>
<summary>4. Accept the license terms (EULA) and click <strong>Next</strong>.</summary>

*Image of the EULA screen with the 'Next' button highlighted.*

</details>
<details>
<summary>5. Select <strong>Custom: Install Windows only (advanced)</strong>.</summary>

> The "Upgrade" option is not applicable here since we are performing a clean installation.

*Image of the installation type selection screen.*

</details>

### Loading VirtIO Drivers (Proxmox)

If you are using Proxmox or a similar KVM-based hypervisor, you will need to load VirtIO drivers for the installer to recognize the virtual hard disk.

<details>
<summary>1. Click <strong>Load Driver</strong>.</summary>

> **Note:** These drivers are necessary for virtualized hardware to perform correctly. In our lab template, the driver disk is pre-mounted. If you're setting up a VM from scratch in a Proxmox environment, you'll need to mount the VirtIO driver ISO yourself.

*Image showing the 'Load Driver' button.*

</details>
<details>
<summary>2. Click <strong>Browse</strong>.</summary>

*Image showing the 'Browse' button.*

</details>
<details>
<summary>3. Locate the virtual CD drive, which should be labeled something like <code>virtio-win-x.x.xxx</code>.</summary>

*Image showing the file browser with the virtual CD drive highlighted.*

</details>
<details>
<summary>4. Navigate to the <code>vioscsi</code> folder, then select the folder corresponding to your OS version (e.g., <code>2k19</code> for Windows Server 2019), and finally select the <code>amd64</code> folder. Click <strong>OK</strong>.</summary>

*Image showing the folder structure for the VirtIO driver.*

</details>
<details>
<summary>5. The installer should find the <strong>Red Hat VirtIO SCSI pass-through controller</strong> driver. Select it and click <strong>Next</strong> to install it.</summary>

*Image showing the driver selection screen with the correct driver highlighted.*

</details>

### Partitioning and Installation

<details>
<summary>1. After the driver is installed, you will see the virtual drive. Select it and click <strong>New</strong>.</summary>

*Image showing the virtual drive and the 'New' button.*

</details>
<details>
<summary>2. Allocate the maximum available space for the new partition. Windows Setup may create a small, separate "System Reserved" partition; this is normal. Click <strong>Apply</strong> and then <strong>OK</strong>.</summary>

*Image showing the partition size allocation and confirmation prompt.*

</details>
<details>
<summary>3. Select the largest partition (marked as "Primary") and click <strong>Next</strong> to begin the Windows installation.</summary>

*Image showing the primary partition selected and the 'Next' button highlighted.*

</details>
<details>
<summary>4. Windows will now install. This process may take some time.</summary>

*Image of the Windows installation progress screen.*

</details>
<details>
<summary>5. Once the installation is complete, the VM will restart, and you will be prompted to set a password for the local <strong>Administrator</strong> account. Choose a secure password and complete the setup.</summary>

*Image of the password creation screen for the Administrator account.*

</details>