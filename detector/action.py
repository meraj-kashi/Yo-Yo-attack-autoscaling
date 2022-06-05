import time
import urllib.request
import boto3
import logger 

elb_client = boto3.client('elbv2')
vpc_client = boto3.client("ec2", region_name= "eu-north-1")

### Adding forwarding rule to Application Loadbalancer
def forwarding_rule(ListenerArn, IpAddress, TargetGroup):
    response = elb_client.create_rule(
    ListenerArn= ListenerArn,
    Conditions=[
        {
            'SourceIpConfig': {
                'Values': [
                    IpAddress,
                ]
            }
        },
    ],
    Priority=1,
    Actions=[
        {
            'Order': 1,
            'ForwardConfig': {
                'TargetGroups': [
                    {
                        'TargetGroupArn': TargetGroup,
                        'Weight': 1
                    },
                ],
                'TargetGroupStickinessConfig': {
                    'Enabled': False,
                    'DurationSeconds': 1
                }
            }
        },
    ]
)
    return response

### Adding rule to Network Access Control List
def create_network_acl_entry(cidr, nacl_id, from_port, to_port, protocol,
                             rule_action, rule_number):
    """
    Creates a network acl entry with the specified configuration.
    """
    try:
        response = vpc_client.create_network_acl_entry(CidrBlock=cidr,
                                                       Egress=False,
                                                       NetworkAclId=nacl_id,
                                                       PortRange={
                                                           'From': from_port,
                                                           'To': to_port,
                                                       },
                                                       Protocol=protocol,
                                                       RuleAction=rule_action,
                                                       RuleNumber=rule_number)

    except ClientError:
        logger.exception('Could not create a network acl entry.')
        raise
    else:
        return response

# Delete rule from Network Access Control List
def delete_network_acl_entry(nacl_id, rule_number):
    """
    Deletes the specified network acl entry.
    """
    try:
        response = vpc_client.delete_network_acl_entry(Egress=False,
                                                       NetworkAclId=nacl_id,
                                                       RuleNumber=rule_number)

    except ClientError:
        logger.exception('Could not delete the network acl entry.')
        raise
    else:
        return response