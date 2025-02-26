# Service Screener
Modified from [AWS/Samples/service-screener-v2](https://github.com/aws-samples/service-screener-v2) to support China region.

An open source guidance tool for the AWS environment. Click [here](https://bit.ly/ssv2demo) for sample report.

Disclaimer: The generated report has to be hosted locally and MUST NOT be internet accessible


## Overview
Service Screener is a tool that runs automated checks on AWS environments and provides recommendations based on AWS and community best practices. 

AWS customers can use this tool on their own environments and use the recommendations to improve the Security, Reliability, Operational Excellence, Performance Efficiency and Cost Optimisation at the service level. 

This tool aims to complement the [AWS Well Architected Tool](https://aws.amazon.com/well-architected-tool/). 

## How does it work?
Service Screener uses [AWS Cloudshell](https://aws.amazon.com/cloudshell/), a free serivce that provides a browser-based shell to run scripts using the AWS CLI. It runs multiple `describe` and `get` API calls to determine the configuration of your environment.

## How much does it cost?
Running this tool is free as it is covered under the AWS Free Tier. If you have exceeded the free tier limits, each run will cost less than $0.01.

## Prerequisites
1. Please review the [DISCLAIMER](./DISCLAIMER.md) before proceeding. 
2. You must have an existing AWS Account.
3. You must have an IAM User with sufficient read permissions. Here is a sample [policy](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/ReadOnlyAccess.html). Additionally, the IAM User must also have the following permissions:
   a. AWSCloudShellFullAccess
   b. cloudformation:CreateStack
   c. cloudformation:DeleteStack

## Installing service-screener V2
此Repo专门用于中国区。
因中国区无Cloudshell支持，在中国区运行screener需要自行安装环境。
可以使用EC2，安装Python3环境，并配置权限（IAM ROle，需要能够创建cloudformation stack的权限及需要扫描资源的只读权限）。
也可以在本地环境（Mac Terminal）运行此工具。

In the terminal, run this script this to install the dependencies:
```bash
cd /tmp
python3 -m venv .
source bin/activate
python3 -m pip install --upgrade pip
rm -rf service-screener-v2
git clone https://github.com/aws-samples/service-screener-v2.git
cd service-screener-v2
pip install -r requirements.txt
python3 unzip_botocore_lambda_runtime.py
alias screener="python3 $(pwd)/main.py"

```
<details>
<summary>Install Dependecies Walkthrough</summary>
   
![Install dependencies](https://d39bs20xyg7k53.cloudfront.net/services-screener/p2-dependencies.gif)
</details>

## Using Service Screener
When running Service Screener, you will need to specify the regions and services you would like it to run on. It currently supports Amazon Cloudfront, AWS Cloudtrail, Amazon Dynamodb, Amazon EC2, Amazon EFS, Amazon RDS, Amazon EKS, Amazon Elasticache, Amazon Guardduty, AWS IAM, Amazon Opensearch, AWS Lambda, and Amazon S3.

We recommend running it in all regions where you have deployed workloads in. Adjust the code samples below to suit your needs then copy and paste it into Cloudshell to run Service Screener. 

**Example 1: (Recommended) Run in the Ningxia region, check all services with beta features enabled**
```
screener --regions cn-northwest-1 --beta 1
```

**Example 1a: Run in the Ningxia region, check all services on stable releases**
```
screener --regions cn-northwest-1
```

**Example 2: Run in the Ningxia region, check only Amazon S3**
```
screener --regions cn-northwest-1 --services s3
```

**Example 3: Run in the Ningxia & Beijing regions, check all services**
```
screener --regions cn-northwest-1,cn-north-1
```

**Example 4: Run in the Ningxia & Beijing regions, check RDS and IAM**
```
screener --regions cn-northwest-1,cn-north-1 --services rds,iam
```

**Example 5: Run in the Ningxia region, filter resources based on tags (e.g: Name=env Values=prod and Name=department Values=hr,coe)**
```
screener --regions cn-northwest-1 --tags env=prod%department=hr,coe
```

**Example 6: Run in all regions and all services**
```
screener --regions ALL
```


### Other parameters
```bash
##mode
--mode api-full | api-raw | report

# api-full: give full results in JSON format
# api-raw: raw findings
# report: generate default web html

##others
# AWS Partner used, migration evaluation id
--others '{"mpe": {"id": "aaaa-1111-cccc"}}'

# To override default Well Architected Tools integration parameter
--others '{"WA": {"region": "cn-northwest-1", "reportName":"SS_Report", "newMileStone":0}}'

# you can combine both
--others '{"WA": {"region": "cn-northwest-1", "reportName":"SS_Report", "newMileStone":0}, "mpe": {"id": "aaaa-1111-cccc"}}'
```
<details>
<summary>Get Report Walkthrough</summary>
   
![Get Report](https://d39bs20xyg7k53.cloudfront.net/services-screener/p3-getreport.gif)
</details>

### Downloading the report
The output is generated as a ~/service-screener-v2/output.zip file. 

<details>
<summary>Download Output & Report Viewing Walkthrough</summary>
   
![Download Output](https://d39bs20xyg7k53.cloudfront.net/services-screener/p4-outputzip.gif)

Once downloaded, unzip the file and open 'index.html' in your browser. You should see a page like this:

![front page](https://d39bs20xyg7k53.cloudfront.net/services-screener/service-screener.jpg?v1)

Ensure that you can see the service(s) run on listed on the left pane.
You can navigate to the service(s) listed to see detailed findings on each service. 
</details>

<details>
<summary>Sample Output Walkthrough</summary>
   
![Sample Output](https://d39bs20xyg7k53.cloudfront.net/services-screener/p5-sample.gif)
</details>

## Using the report 
The report provides you an easy-to-navigate dashboard of the various best-practice checks that were run. 

Use the left navigation bar to explore the checks for each service. Expand each check to read the description, find out which resources were highlighted, and get recommendations on how to remediate the findings.  

## Contributing to service-screener
We encourage public contributions! Please review [CONTRIBUTING](./CONTRIBUTING.md) for details on our code of conduct and development process.

## Contact
Please review [CONTRIBUTING](./CONTRIBUTING.md) to raise any issues. 

## Security
See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License
This project is licensed under the Apache-2.0 License.
