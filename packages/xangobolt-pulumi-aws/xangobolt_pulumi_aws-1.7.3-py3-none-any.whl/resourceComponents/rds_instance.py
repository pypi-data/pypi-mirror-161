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
        Constructs an Rediss Cluster.

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

        # Create RDS Instance
        rds_instance = [rds.Instance(
            props.mssql[i]["instance_name"],
            props,
            engine=props.mssql[i]["engine"],
            engine_version=props.mssql[i]["engine_version"],
            username=props.mssql[i]["setflow_sm"]["secret_version"]["username"],
            password=password.result,
            instance_class=props.mssql[i]["instance_class"],
            storage_type=props.mssql[i]["storage_type"],
            iops=props.mssql[i]["iops"],
            allocated_storage=props.mssql[i]["allocated_storage"],
            max_allocated_storage=props.mssql[i]["max_allocated_storage"],
            publicly_accessible=props.mssql[i]["publicly_accessible"],
            apply_immediately=props.mssql[i]["apply_immediately"],
            license_model=props.mssql[i]["license_model"],
            skip_final_snapshot=props.mssql[i]["skip_final_snapshot"],
            performance_insights_enabled=props.mssql[i]["performance_insights_enabled"],
            backup_retention_period=props.mssql[i]["backup_retention_period"],
            backup_window=props.mssql[i]["backup_window"],
            secgrp_ids=mssql_sg,
            snetgrp_name=(rds.SubnetGroup(
                props.mssql[i]["snetgrp_name"],
                props,
                # snet_ids=[snet1,snet2,snet3],
                snet_ids=vpc_props["subnets"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).name),
            optgrp_name=(rds.OptionGroup(
                props.mssql[i]['option_group']["optgrp_name"],
                props,
                engine_name=props.mssql[i]['option_group']["engine_name"], 
                major_engine_version=props.mssql[i]['option_group']["major_engine_version"], 
                iam_role=props.mssql[i]['option_group']["iam_role"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).name),
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.mssql
        ]

        # construct secrets parameters
        string = Output.all(host=rds_instance[0].address, pword=password.result).apply(lambda args: sm.rdsJsonify(
                username=props.sm["mssql-secrets"]["secret_version"]["username"],
                password=args['pword'],
                engine=props.sm["mssql-secrets"]["secret_version"]["engine"],
                host=args['host'],
                port=props.sm["mssql-secrets"]["secret_version"]["port"],
                db_id=props.sm["mssql-secrets"]["secret_version"]["dbInstanceIdentifier"],
                db=props.sm["mssql-secrets"]["secret_version"]["database"],
            )
        )

        # Store Credentials and Properties in Secrets Manager
        secret = secrets_manager.SecretsManager(
            'mssql-'+props.stack,
            props=props,
            name=props.sm["mssql-secrets"]["secret_name"],
            secrets = string,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )

        # Store Credentials and Properties in Secrets Manager
        secret_reader = secrets_manager.SecretsManager(
            'mssql-reader'+props.stack,
            props=props,
            name=props.sm["mssql-reader-secrets"]["secret_name"],
            secrets = string,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )



        