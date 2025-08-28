# Getting Started Guide

## Introduction

Hello everyone! I am creating this page to help improve your start process at either the **Student Security Operations Center (SOC)** or the **Student Data Center (SDC)**.

All operations done on either side will require you to connect to our VPN to access any resources we host.

## VPN Access Setup

1. **Request Access**: Please fill out this Microsoft Form for User Access to our VPN. [Form]((https://forms.cloud.microsoft/r/5BtvPPTJku))
2. **Install VPN Client**: If you have never logged in to Kamino, please install Palo Alto's GlobalProtect application. We are now completing authentication using Cal Poly Pomona's SSO.
3. **Initial Connection**:
   - After installing the application, you will be prompted with the following windows <insert pictures i forgot lol>
   - When asked to enter our Portal Address use: `mgmt.sdc.cpp.edu`
   - This will prompt you to login using Cal Poly SSO

> Note: Access to the Management VPN Portal depends on when you submitted the User Access Request through Microsoft Forms.

## Accessing Kamino

1. Once you are given access to Management Portal, head over to [https://kamino.sdc.cpp](https://kamino.sdc.cpp)
2. This is only available when you are connected to the VPN
3. Use your AD Credentials to login

If you do not have credentials or do not remember the details, ask a Student Director to help resolve this for you.

## Working with Pods

1. After logging in to Kamino, you can provision pods using the Web Interface
2. Try using the premade templates as they are ideal for starting fresh without sitting through standard installation experience
3. Recommended setup: provision two pods
   - One for your server
   - One client to forward logs to said server

---

**Known Issue (August 27)**: Students who provision pods on Kamino are not having them assigned in Proxmox, showing an empty list with just nodes.