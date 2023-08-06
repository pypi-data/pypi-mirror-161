from arpeggio.cleanpeg import NOT, prefix
import pulumi
from resources import ec2


def SEC_GRP(stem, props, vpc_id=None, er=None, ir=None, source_sg=None, provider=None, parent=None, depends_on=None):
    # Create Security Group
    sg = ec2.SecurityGroup(
        stem,
        props, 
        vpc_id=vpc_id,
        parent=parent,
        depends_on=depends_on,
        provider=provider
    )

    # Create Security Group Egress Rules
    sg_er = [ec2.SecurityGroupRule(
        stem, 
        props, 
        sg_id=sg.id,
        type='egress',
        from_port=er[i]['from_port'],
        to_port=er[i]['to_port'],
        protocol=er[i]['protocol'],
        cidr=None if "cidr_blocks" not in er[i] else 
            (
                er[i]['cidr_blocks']
            ),
        ipv6_cidr=None if "ipv6_cidr" not in er[i] else
            (
                er[i]['ipv6_cidr']
            ),
        source_sg=None if "source_sg" not in er[i] else 
            (
                er[i]['source_sg']
            ),
        description=er[i]['description'],
        count=i,
        parent=sg,
        depends_on=sg,
        provider=provider
    )
    for i in range(len(er))
    ]

    # Create Security Group Ingress Rules
    sg_ir = [ec2.SecurityGroupRule(
        stem, 
        props, 
        sg_id=sg.id,
        type='ingress',
        from_port=ir[i]['from_port'],
        to_port=ir[i]['to_port'],
        protocol=ir[i]['protocol'],
        cidr=None if "cidr_blocks" not in ir[i] else 
            (
                ir[i]['cidr_blocks']
            ),
        ipv6_cidr=None if "ipv6_cidr" not in ir[i] else
            (
                ir[i]['ipv6_cidr']
            ),
        source_sg=None if "source_sg" not in ir[i] else 
            (
                ir[i]['source_sg']
            ),
        description=ir[i]['description'],
        count=i,
        parent=sg,
        depends_on=sg,
        provider=provider
    )
    for i in range(len(ir))
    ]

    return sg

