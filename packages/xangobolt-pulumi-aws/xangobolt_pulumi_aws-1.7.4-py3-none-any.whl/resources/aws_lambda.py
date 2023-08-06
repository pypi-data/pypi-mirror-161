from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.lambda_ as ldf

def Lambda_Function(stem, props, code=None, role=None , handler=None, runtime=None, environment=None, provider=None, parent=None, depends_on=None):
    lambda_function = ldf.Function(
        f'ldf-{stem}',
        name=f'ldf-{stem}',
        code=code,
        role=role,
        handler=handler,
        runtime=runtime,
        environment=ldf.FunctionEnvironmentArgs(
            variables=environment
        ),
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return lambda_function