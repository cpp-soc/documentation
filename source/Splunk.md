# Splunk
Splunk is a log aggregator used to centralize logs and data. At the SOC we are using it as a System Information and Event Management(SIEM) system.

## What you can do with Splunk:
- Collect logs using the Splunk Universal Forwarders
- Create detections and alerts
- Use SOAR to automate tasks
- Create cool dashboards 
- Scale out config deployments using the Splunk Deployment Server.

## How to setup a Splunk Server

1. Download the installer from [Splunk](https://www.splunk.com/en_us/download/splunk-enterprise.html)
2. Install Splunk onto your system

    * **Linux**

        Switch user into root user
        ```
        su root
        ```

        Download the correct file for your Linux distribution. For example for Debian run the command below.
        ```
        wget -O splunk-9.4.1-e3bdab203ac8-linux-amd64.deb "https://download.splunk.com/products/splunk/releases/9.4.1/linux/splunk-9.4.1-e3bdab203ac8-linux-amd64.deb"
        ```
        > Note that the name of the file may be different due to a different version

        Run the command to extract and install the file. For .deb files its the command below. 
        ```
        dpkg -i splunk-9.4.1-e3bdab203ac8-linux-amd64.deb
        ```
        Accept the license and create an admin user. This user will be used to login to the Splunk web interface

        Change directory into the default bin location for Splunk. This is where all Splunk binaries are kept.
        ```
        cd /opt/splunk/bin
        ``` 

        Run the splunk binary to start Splunk.
        ```
        ./splunk start
        ```

        Access Splunk web and login using the admin user you created. The web interface is available on [http://localhost:8000](http://localhost:8000)
        
    * **Windows**

        Run the command below in PowerShell.
        ```
        wget -O splunk-9.4.1-e3bdab203ac8-windows-x64.msi "https://download.splunk.com/products/splunk/releases/9.4.1/windows/splunk-9.4.1-e3bdab203ac8-windows-x64.msi"
        ```

        Double click on the .msi file you downloaded and follow the instructions to install.

## How to setup the Splunk Universal Forwarder

## How to setup a Splunk Deployment Server

