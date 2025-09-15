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

## Lab Setup: Primary Domain Controller

Let's begin by configuring our first VM, **Windows Server 2025**, as the Primary DC.
