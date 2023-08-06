from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import jsons
import pulumi_aws.rds as rds
import pulumi_aws_native.rds as rds_native

def Instance(stem, props, engine=None, engine_version=None, username=None, password=None, storage_type=None, iops=None, allocated_storage=None, max_allocated_storage=None, publicly_accessible=None, license_model=None, skip_final_snapshot=None, performance_insights_enabled=None, backup_retention_period=None, backup_window=None, instance_class=None, apply_immediately=None, snetgrp_name=None, secgrp_ids=None, optgrp_name=None, provider=None, parent=None, depends_on=None):
    db_instance = rds.Instance(
        f'rds-inst-{stem}',
        # name='db-{stem}',
        identifier=f'rds-inst-{stem}',
        instance_class=instance_class,
        engine=engine,
        engine_version=engine_version,
        apply_immediately=apply_immediately,
        username=username,
        password=password,
        storage_type=storage_type,
        iops=iops,
        allocated_storage=allocated_storage,
        max_allocated_storage=max_allocated_storage,
        publicly_accessible=publicly_accessible,
        license_model=license_model,
        skip_final_snapshot=skip_final_snapshot,
        performance_insights_enabled=performance_insights_enabled,
        vpc_security_group_ids=secgrp_ids,
        db_subnet_group_name=snetgrp_name,
        option_group_name=optgrp_name,
        backup_retention_period=backup_retention_period,
        backup_window=backup_window,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return db_instance

def Cluster(stem, props, username=None, password=None, engine=None, engine_version=None, skip_final_snapshot=None, storage_encrypted=None, preferred_backup_window=None, preferred_maintenance_window=None, snetgrp_name=None, paramgrp_name=None, secgrp_ids=None, provider=None, parent=None, depends_on=None):
    db_cluster = rds.Cluster(
        f'rds-clst-{stem}',
        cluster_identifier=f'rds-clst-{stem}',
        engine=engine,
        engine_version=engine_version,
        master_username=username,
        master_password=password,
        skip_final_snapshot=skip_final_snapshot,
        storage_encrypted=storage_encrypted,
        vpc_security_group_ids=secgrp_ids,
        db_subnet_group_name=snetgrp_name,
        db_cluster_parameter_group_name=paramgrp_name,
        preferred_backup_window=preferred_backup_window,
        preferred_maintenance_window=preferred_maintenance_window,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return db_cluster

def ClusterInstance(stem, props, cluster_id, instance_class=None, engine=None, engine_version=None, apply_immediately=None, paramgrp_name=None, publicly_accessible=None, performance_insights_enabled=None, provider=None, parent=None, depends_on=None):
    db_cluster_instance = rds.ClusterInstance(
        f'rds-inst-{stem}',
        identifier=f'rds-inst-{stem}',
        cluster_identifier=cluster_id,
        instance_class=instance_class,
        apply_immediately=apply_immediately,
        engine=engine,
        engine_version=engine_version,
        publicly_accessible=publicly_accessible,
        db_parameter_group_name=paramgrp_name,
        performance_insights_enabled=performance_insights_enabled,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return db_cluster_instance

def SubnetGroup(stem, props, snet_ids=None, provider=None, parent=None, depends_on=None):
    sn_grp =rds.SubnetGroup(
        f'sngrp-{stem}',
        name=f'sngrp-{stem}',
        subnet_ids=snet_ids,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sn_grp

def OptionGroup(stem, props, engine_name=None, major_engine_version=None, iam_role=None, provider=None, parent=None, depends_on=None):
    opt_group = rds.OptionGroup(
        f'optgrp-{stem}',
        name=f'optgrp-{stem}',
        option_group_description="Option Group",
        engine_name=engine_name,
        major_engine_version=major_engine_version,
        options=[
            rds.OptionGroupOptionArgs(
                option_name="SQLSERVER_BACKUP_RESTORE",
                option_settings=[rds.OptionGroupOptionOptionSettingArgs(
                    name="IAM_ROLE_ARN",
                    value=iam_role,
                )],
            )
        ],
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return opt_group

def ParameterGroup(stem, props, family=None, apply_method=None, provider=None, parent=None, depends_on=None):
    param_group = rds.ParameterGroup(
        f'paramgrp-{stem}',
        name=f'pg-{stem}',
        family=family,
        # parameters=[
        #     rds.ParameterGroupParameterArgs(
        #         name="enable_sort",
        #         value="1",
        #         apply_method=apply_method,
        #     )
        # ],
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return param_group

def ClusterParameterGroup(stem, props, family=None, apply_method=None, provider=None, parent=None, depends_on=None):
    cluster_param_group = rds.ClusterParameterGroup(
        f'clstparamgrp-{stem}',
        name=f'clstpg-{stem}',
        family=family,
        parameters=[
            rds.ParameterGroupParameterArgs(
                name="rds.babelfish_status",
                value="on",
                apply_method=apply_method,
            )
        ],
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return cluster_param_group