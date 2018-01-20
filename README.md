# Amazon Route 53 DNS A Record Update Utility

### [Instructions on how to use can be found here.](https://www.stephenlecrenski.com/articles/route53)

## Dependencies

pip install requests
pip install route53
pip install PyYAML

## Create an API Token here to use.

[https://console.aws.amazon.com/iam/home?#/security_credential](https://console.aws.amazon.com/iam/home?#/security_credential)

## Usage

python sync_dns.py --help

python sync_dns.py --credentials credentials.yaml --config dns.config.yaml
