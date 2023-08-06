from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.redshift as redshift
import pulumi_aws_native.redshift as redshift_native

def Cluster(stem, props, db_name=None, node_type=None, node_count=None, cluster_type=None, username=None, password=None, secgrp_ids=None, snetgrp_name=None, iam_roles=None, publicly_accessible=None, skip_final_snapshot=None, provider=None, parent=None, depends_on=None):
    rs_cluster = redshift.Cluster(
        f'redshift-{stem}',
        cluster_identifier=f'redshift-{stem}',
        database_name=db_name,
        cluster_type=cluster_type,
        node_type=node_type,
        number_of_nodes=node_count,
        master_username=username,
        master_password=password,
        cluster_subnet_group_name=snetgrp_name,
        vpc_security_group_ids=secgrp_ids,
        iam_roles=iam_roles,
        publicly_accessible=publicly_accessible,
        skip_final_snapshot=skip_final_snapshot,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return rs_cluster


def SubnetGroup(stem, props, snet_ids=None, provider=None, parent=None, depends_on=None):
    sn_grp =redshift.SubnetGroup(
        f'sngrp-{stem}',
        name=f'sngrp-{stem}',
        subnet_ids=snet_ids,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sn_grp