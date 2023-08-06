'''
# `cdk-secret-manager-wrapper-layer`

that Lambda layer uses a wrapper script to fetch information from Secrets Manager and create environmental variables.

> idea from [source](https://github.com/aws-samples/aws-lambda-environmental-variables-from-aws-secrets-manager)

## Example

```python
import { App, Stack, CfnOutput, Duration } from 'aws-cdk-lib';
import { Effect, PolicyStatement } from 'aws-cdk-lib/aws-iam';
import { Function, Runtime, Code, FunctionUrlAuthType } from 'aws-cdk-lib/aws-lambda';
import { CfnSecret } from 'aws-cdk-lib/aws-secretsmanager';
import { SecretManagerWrapperLayer } from 'cdk-secret-manager-wrapper-layer';
const env = {
  region: process.env.CDK_DEFAULT_REGION,
  account: process.env.CDK_DEFAULT_ACCOUNT,
};
const app = new App();
const stack = new Stack(app, 'testing-stack', { env });

/**
 * Example create an Secret for testing.
 */
const secret = new CfnSecret(stack, 'Mysecret', {
  secretString: JSON.stringify({
    KEY1: 'VALUE1',
    KEY2: 'VALUE2',
    KEY3: 'VALUE3',
  }),
});

const layer = new SecretManagerWrapperLayer(stack, 'SecretManagerWrapperLayer');

const lambda = new Function(stack, 'fn', {
  runtime: Runtime.PYTHON_3_9,
  code: Code.fromInline(`
import os
def hander(events, contexts):
    env = {}
    env['KEY1'] = os.environ.get('KEY1', 'Not Found')
    env['KEY2'] = os.environ.get('KEY2', 'Not Found')
    env['KEY3'] = os.environ.get('KEY3', 'Not Found')
    return env
    `),
  handler: 'index.hander',
  layers: [layer],
  timeout: Duration.minutes(1),
  /**
   * you need to define this 4 environment various.
   */
  environment: {
    AWS_LAMBDA_EXEC_WRAPPER: '/opt/get-secrets-layer',
    SECRET_REGION: stack.region,
    SECRET_ARN: secret.ref,
    API_TIMEOUT: '5000',
  },
});

/**
 * Add Permission for lambda get secret value from secret manager.
 */
lambda.role!.addToPrincipalPolicy(
  new PolicyStatement({
    effect: Effect.ALLOW,
    actions: ['secretsmanager:GetSecretValue'],
    // Also you can use find from context.
    resources: [secret.ref],
  }),
);

/**
 * For Testing.
 */
const FnUrl = lambda.addFunctionUrl({
  authType: FunctionUrlAuthType.NONE,
});

new CfnOutput(stack, 'FnUrl', {
  value: FnUrl.url,
});
```

## Testing

```bash
# ex: curl https://sdfghjklertyuioxcvbnmghj.lambda-url.us-east-1.on.aws/
curl ${FnUrl}
{"KEY2":"VALUE2","KEY1":"VALUE1","KEY3":"VALUE3"}
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk.aws_lambda
import constructs


class SecretManagerWrapperLayer(
    aws_cdk.aws_lambda.LayerVersion,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-secret-manager-wrapper-layer.SecretManagerWrapperLayer",
):
    '''(experimental) An AWS SecretManager Wrapper layer that includes the AWS CLI, jq etc...

    :stability: experimental
    '''

    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(SecretManagerWrapperLayer.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="getOrCreate") # type: ignore[misc]
    @builtins.classmethod
    def get_or_create(cls, scope: constructs.Construct) -> "SecretManagerWrapperLayer":
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(SecretManagerWrapperLayer.get_or_create)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast("SecretManagerWrapperLayer", jsii.sinvoke(cls, "getOrCreate", [scope]))


__all__ = [
    "SecretManagerWrapperLayer",
]

publication.publish()
