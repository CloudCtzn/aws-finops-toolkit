# AWS FinOPs Toolkit

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-Boto3-orange?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-green?style=for-the-badge)


## CRITICAL WARNING
> **Check your configuration before running!!!** >
> Some scripts in this repo may have ***'DRY_RUN = False'*** set by default due to recent testing. ***ALWAYS*** verify the ***'DRY_RUN'*** variable at the top of the file is set to ***'True'*** before executing against a live environment!!!
>***I am not responsible for the accidental deletion of resource in any production environment***

---

## Overview 
>This repo contains a collection of Python automation scripts designed to optimize AWS costs by identifying and cleaning up "Zombie Assets" (unused resources) and enforcing scheduling policies.
>These tools are built using ***Boto3*** and follow the ***FinOps*** methodology to reduce cloud waste

---

## The Tools

### 1. EC2 Night Watchman (***ec2_night_watchman.py***)  
**GOAL:** Prevent non-production servers from running 24/7.  
**Logic:** Scans for instances with the tag 'Environment: Dev'.  
**Action:**  Stops them immediately to save on compute costs.  
**Filtering:** Uses ***Server-Side-Filtering*** (API Level) to minimize data transfer and latency.


### 2. Snapshot Reaper (***snapshot_reaper.py***)  
**GOAL:** Reduce storage costs by removing stale EBS Volumes.  
**Logic:** Calculates the age of every snapshot owned by the account (self).  
**Action:** Deletes snapshots older than ***30*** days (configurable).  
**Safety:** Uses ***datetime*** math w/ UTC timezone awareness to ensure accuracy.  


### 3. Elastic IP Sweeper (***elastic_ip_sweeper.py***)  
**GOAL:** Eliminate "***hoarding penalties***" for unattached Static IPs.  
**Logic:** Scans all Elastic IPs in the region.  
**Action:** Identifies IPs that lack an ***AssociationId*** and releases them back to the AWS pool.  

---

## Usage   

### Prerequisites  
-Python 3.x installed.  
-AWS CLI configured w/ valid credentials  
-Boto3 library installed (pip install boto3)  


### How to run  
1. Clone the repo:
    bash  
    git clone  [https://github.com/CloudCtzn/aws-finops-toolkit.git](https://github.com/CloudCtzn/aws-finops-toolkit.git)

2. Open the desired script
3. Verfiy the ***DRY_RUN*** variable (True/False)
4. Run via Terminal