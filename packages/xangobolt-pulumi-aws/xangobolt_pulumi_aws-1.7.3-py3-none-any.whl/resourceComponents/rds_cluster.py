# Copyright 2018-2019, James Nugent.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain
# one at http://mozilla.org/MPL/2.0/.

"""
Contains a Pulumi ComponentResource for creating a good-practice AWS VPC.
"""
import json, time
from typing import Mapping, Sequence
from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi import Input, Output

from resources import rds, ec2, sm, random
from resourceComponents import secrets_manager, security_group


class RDS(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, vpc_props: None, mssql_sg: None, opts:  ResourceOptions = None):
        """
        Constructs an postgresql_cluster Cluster.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('Mssql', name, {}, opts)

        # Make base info available to other methods
        # self.name = name
        # self.description = props.description
        # self.base_tags = props.base_tags

        Resources = [rds, ec2]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags


        # Create RDS Instance Password
        password = random.RandomString(
            name,
            parent=self,
            depends_on=opts.depends_on,
        )

        # Create Cluster Parameter Group
        clusterparamgroup = [rds.ClusterParameterGroup(
            props.postgresql_cluster[i]["paramgrp_name"],
            props,
            family=props.postgresql_cluster[i]["paramgrp_family"],
            apply_method=props.postgresql_cluster[i]["param_apply_method"],
            parent=self, 
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.postgresql_cluster
        ]

        # Create Parameter Group
        paramgroup = [rds.ParameterGroup(
            props.postgresql_cluster[i]["paramgrp_name"],
            props,
            family=props.postgresql_cluster[i]["paramgrp_family"],
            apply_method=props.postgresql_cluster[i]["param_apply_method"],
            parent=self, 
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.postgresql_cluster
        ]



        # Create RDS Cluster
        rds_cluster = [rds.Cluster(
            props.postgresql_cluster[i]["cluster_name"],
            props,
            username=props.postgresql_cluster[i]["setflow_sm"]["secret_version"]["username"],
            password=password.result,
            engine=props.postgresql_cluster[i]["engine"],
            engine_version=props.postgresql_cluster[i]["engine_version"],
            skip_final_snapshot=props.postgresql_cluster[i]["skip_final_snapshot"],
            storage_encrypted=props.postgresql_cluster[i]["storage_encrypted"],
            preferred_backup_window=props.postgresql_cluster[i]["preferred_backup_window"],
            preferred_maintenance_window=props.postgresql_cluster[i]["preferred_maintenance_window"],
            secgrp_ids=mssql_sg,
            snetgrp_name=(rds.SubnetGroup(
                props.postgresql_cluster[i]["snetgrp_name"],
                props,
                # snet_ids=[snet1,snet2,snet3],
                snet_ids=vpc_props["subnets"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).name),
            paramgrp_name=clusterparamgroup[0].name,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.postgresql_cluster
        ]

        # Create Reader Cluster Instances
        rds_cluster_instance = [rds.ClusterInstance(
            props.postgresql_instances[i]["instance_name"],
            props,
            cluster_id=rds_cluster[0].id,
            engine=props.postgresql_instances[i]["engine"],
            engine_version=props.postgresql_instances[i]["engine_version"],
            instance_class=props.postgresql_instances[i]["instance_class"],
            apply_immediately=props.postgresql_instances[i]["apply_immediately"],
            performance_insights_enabled=props.postgresql_instances[i]["performance_insights_enabled"],
            publicly_accessible=props.postgresql_instances[i]["publicly_accessible"],
            paramgrp_name=paramgroup[0].name,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.postgresql_instances
        ]

        # # construct secrets parameters
        # string = Output.all(host=rds_cluster[0].address, pword=password.result).apply(lambda args: sm.rdsJsonify(
        #         username=props.sm["postgresql_cluster-secrets"]["secret_version"]["username"],
        #         password=args['pword'],
        #         engine=props.sm["postgresql_cluster-secrets"]["secret_version"]["engine"],
        #         host=args['host'],
        #         port=props.sm["postgresql_cluster-secrets"]["secret_version"]["port"],
        #         db_id=props.sm["postgresql_cluster-secrets"]["secret_version"]["dbInstanceIdentifier"],
        #         db=props.sm["postgresql_cluster-secrets"]["secret_version"]["database"],
        #     )
        # )

        # # Store Credentials and Properties in Secrets Manager
        # secret = secrets_manager.SecretsManager(
        #     'postgresql_cluster-'+props.stack,
        #     props=props,
        #     name=props.sm["postgresql_cluster-secrets"]["secret_name"],
        #     secrets = string,
        #     parent=self,
        #     depends_on=opts.depends_on,
        #     provider=opts.providers.get(props.stack+'_prov')
        # )