'''
# Datadog CDK Constructs

[![NPM](https://img.shields.io/npm/v/datadog-cdk-constructs?color=blue&label=npm+cdk+v1)](https://www.npmjs.com/package/datadog-cdk-constructs)
[![NPM](https://img.shields.io/npm/v/datadog-cdk-constructs-v2?color=39a356&label=npm+cdk+v2)](https://www.npmjs.com/package/datadog-cdk-constructs-v2)
[![PyPI](https://img.shields.io/pypi/v/datadog-cdk-constructs?color=blue&label=pypi+cdk+v1)](https://pypi.org/project/datadog-cdk-constructs/)
[![PyPI](https://img.shields.io/pypi/v/datadog-cdk-constructs-v2?color=39a356&label=pypi+cdk+v2)](https://pypi.org/project/datadog-cdk-constructs-v2/)
[![Slack](https://chat.datadoghq.com/badge.svg?bg=632CA6)](https://chat.datadoghq.com/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](https://github.com/DataDog/datadog-cdk-constructs/blob/main/LICENSE)

Use this Datadog CDK Construct Library to deploy serverless applications using AWS CDK .

This CDK library automatically configures ingestion of metrics, traces, and logs from your serverless applications by:

* Installing and configuring the Datadog Lambda library for your [Python](https://github.com/DataDog/datadog-lambda-layer-python) and [Node.js](https://github.com/DataDog/datadog-lambda-layer-js) Lambda functions.
* Enabling the collection of traces and custom metrics from your Lambda functions.
* Managing subscriptions from the Datadog Forwarder to your Lambda and non-Lambda log groups.

## AWS CDK v1 vs AWS CDK v2

Two separate versions of Datadog CDK Constructs exist; `datadog-cdk-constructs` and `datadog-cdk-constructs-v2`. These are designed to work with `AWS CDK v1` and `AWS CDK v2` respectively.

* `datadog-cdk-constructs-v2` requires Node 14+, while `datadog-cdk-constructs-v1` supports Node 12+.
* Otherwise, the use of the two packages is identical.

## npm Package Installation:

For use with AWS CDK v2:

```
yarn add --dev datadog-cdk-constructs-v2
# or
npm install datadog-cdk-constructs-v2 --save-dev
```

For use with AWS CDK v1:

```
yarn add --dev datadog-cdk-constructs
# or
npm install datadog-cdk-constructs --save-dev
```

## PyPI Package Installation:

For use with AWS CDK v2:

```
pip install datadog-cdk-constructs-v2
```

For use with AWS CDK v1:

```
pip install datadog-cdk-constructs
```

### Note:

Pay attention to the output from your package manager as the `Datadog CDK Construct Library` has peer dependencies.

## Usage

### AWS CDK

* *If you are new to AWS CDK then check out this [workshop](https://cdkworkshop.com/15-prerequisites.html).*
* *The following examples assume the use of AWS CDK v2. If you're using CDK v1, import `datadog-cdk-constructs` rather than `datadog-cdk-constructs-v2`.*

Add this to your CDK stack:

```python
# Example automatically generated from non-compiling source. May contain errors.
from datadog_cdk_constructs_v2 import Datadog

datadog = Datadog(self, "Datadog",
    node_layer_version=<LAYER_VERSION>,
    python_layer_version=<LAYER_VERSION>,
    add_layers=<BOOLEAN>,
    extension_layer_version="<EXTENSION_VERSION>",
    forwarder_arn="<FORWARDER_ARN>",
    flush_metrics_to_logs=<BOOLEAN>,
    site="<SITE>",
    api_key="{Datadog_API_Key}",
    api_key_secret_arn="{Secret_ARN_Datadog_API_Key}",
    api_kms_key="{Encrypted_Datadog_API_Key}",
    enable_datadog_tracing=<BOOLEAN>,
    enable_datadog_logs=<BOOLEAN>,
    inject_log_context=<BOOLEAN>,
    log_level=<STRING>,
    env=<STRING>,  # Optional
    service=<STRING>,  # Optional
    version=<STRING>,  # Optional
    tags=<STRING>
)
datadog.add_lambda_functions([<LAMBDA_FUNCTIONS>])
datadog.add_forwarder_to_non_lambda_log_groups([<LOG_GROUPS>])
```

Optionally, if you'd like to enable [source code integration](https://docs.datadoghq.com/integrations/guide/source-code-integration/) (Typescript only), you'll need to make a few changes to your stack setup since the AWS CDK does not support async functions.

Change your initialization function as follows (note: we're changing this to pass the `gitHash` value to the CDK):

```python
# Example automatically generated from non-compiling source. May contain errors.
def main():
    # Make sure to add @datadog/datadog-ci via your package manager
    datadog_ci = require("@datadog/datadog-ci")
    git_hash = await datadogCi.gitMetadata.uploadGitCommitHash('{Datadog_API_Key}', '<SITE>')

    app = cdk.App()
    # Pass in the hash to the ExampleStack constructor
    ExampleStack(app, "ExampleStack", {}, git_hash)
```

In your stack constructor, change to add an optional `gitHash` parameter, and call `addGitCommitMetadata()`:

```python
# Example automatically generated from non-compiling source. May contain errors.
class ExampleStack(cdk.Stack):
    def __init__(self, scope, id, props=None, git_hash=None):
        datadog.add_git_commit_metadata([<YOUR_FUNCTIONS>], git_hash)
```

## Configuration

To further configure your Datadog construct, use the following custom parameters:

*Note*: The descriptions use the npm package parameters, but they also apply to the PyPI package parameters.

| npm package parameter | PyPI package parameter | Description |
| --- | --- | --- |
| `addLayers` | `add_layers` | Whether to add the Lambda Layers or expect the user to bring their own. Defaults to true. When true, the Lambda Library version variables are also required. When false, you must include the Datadog Lambda library in your functions' deployment packages. |
| `pythonLayerVersion` | `python_layer_version` | Version of the Python Lambda layer to install, such as 21. Required if you are deploying at least one Lambda function written in Python and `addLayers` is true. Find the latest version number [here](https://github.com/DataDog/datadog-lambda-python/releases). |
| `nodeLayerVersion` | `node_layer_version` | Version of the Node.js Lambda layer to install, such as 29. Required if you are deploying at least one Lambda function written in Node.js and `addLayers` is true. Find the latest version number from [here](https://github.com/DataDog/datadog-lambda-js/releases). |
| `extensionLayerVersion` | `extension_layer_version` | Version of the Datadog Lambda Extension layer to install, such as 5. When `extensionLayerVersion` is set, `apiKey` (or if encrypted, `apiKMSKey` or `apiKeySecretArn`) needs to be set as well. When enabled, lambda function log groups will not be subscribed by the forwarder. Learn more about the Lambda extension [here](https://docs.datadoghq.com/serverless/datadog_lambda_library/extension/). |
| `forwarderArn` | `forwarder_arn` | When set, the plugin will automatically subscribe the Datadog Forwarder to the functions' log groups. Do not set `forwarderArn` when `extensionLayerVersion` is set. |
| `flushMetricsToLogs` | `flush_metrics_to_logs` | Send custom metrics using CloudWatch logs with the Datadog Forwarder Lambda function (recommended). Defaults to `true` . If you disable this parameter, it's required to set `apiKey` (or if encrypted, `apiKMSKey` or `apiKeySecretArn`). |
| `site` | `site` | Set which Datadog site to send data. This is only used when `flushMetricsToLogs` is `false` or `extensionLayerVersion` is set. Possible values are `datadoghq.com`, `datadoghq.eu`, `us3.datadoghq.com`, `us5.datadoghq.com`, and `ddog-gov.com`. The default is `datadoghq.com`. |
| `apiKey` | `api_key` | Datadog API Key, only needed when `flushMetricsToLogs` is `false` or `extensionLayerVersion` is set. For more information about getting a Datadog API key, see the [API key documentation](https://docs.datadoghq.com/account_management/api-app-keys/#api-keys). |
| `apiKeySecretArn` | `api_key_secret_arn` | The ARN of the secret storing the Datadog API key in AWS Secrets Manager. Use this parameter in place of `apiKey` when `flushMetricsToLogs` is `false` or `extensionLayer` is set. Remember to add the `secretsmanager:GetSecretValue` permission to the Lambda execution role. |
| `apiKmsKey` | `api_kms_key` | Datadog API Key encrypted using KMS. Use this parameter in place of `apiKey` when `flushMetricsToLogs` is `false` or `extensionLayerVersion` is set, and you are using KMS encryption. |
| `enableDatadogTracing` | `enable_datadog_tracing` | Enable Datadog tracing on your Lambda functions. Defaults to `true`. |
| `enableDatadogLogs` | `enable_datadog_logs` | Send Lambda function logs to Datadog via the Datadog Lambda Extension.  Defaults to `true`. Note: This setting has no effect on logs sent via the Datadog Forwarder. |
| `injectLogContext` | `inject_log_context` | When set, the Lambda layer will automatically patch console.log with Datadog's tracing ids. Defaults to `true`. |
| `logLevel` | `log_level` | When set to `debug`, the Datadog Lambda Library and Extension will log additional information to help troubleshoot issues. |
| `env` | `env` | When set along with `extensionLayerVersion`, a `DD_ENV` environment variable is added to all Lambda functions with the provided value. When set along with `forwarderArn`, an `env` tag is added to all Lambda functions with the provided value. |
| `service` | `service` | When set along with `extensionLayerVersion`, a `DD_SERVICE` environment variable is added to all Lambda functions with the provided value. When set along with `forwarderArn`, a `service` tag is added to all Lambda functions with the provided value. |
| `version` | `version` | When set along with `extensionLayerVersion`, a `DD_VERSION` environment variable is added to all Lambda functions with the provided value. When set along with `forwarderArn`, a `version` tag is added to all Lambda functions with the provided value. |
| `tags` | `tags` | A comma separated list of key:value pairs as a single string. When set along with `extensionLayerVersion`, a `DD_TAGS` environment variable is added to all Lambda functions with the provided value. When set along with `forwarderArn`, the cdk parses the string and sets each key:value pair as a tag to all Lambda functions. |

**Note**: `env`, `service`, `version`, and `tags` override function level `DD_XXX` environment variables.

### Tracing

Enable X-Ray Tracing on your Lambda functions. For more information, see [CDK documentation](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Tracing.html).

```python
# Example automatically generated from non-compiling source. May contain errors.
import aws_cdk_lib.aws_lambda as lambda_

lambda_function = lambda_.Function(self, "HelloHandler",
    runtime=lambda_.Runtime.NODEJS_14_X,
    code=lambda_.Code.from_asset("lambda"),
    handler="hello.handler",
    tracing=lambda_.Tracing.ACTIVE
)
```

### Nested Stacks

Add the Datadog CDK Construct to each stack you wish to instrument with Datadog. In the example below, we initialize the Datadog CDK Construct and call `addLambdaFunctions()` in both the `RootStack` and `NestedStack`.

```python
# Example automatically generated from non-compiling source. May contain errors.
from datadog_cdk_constructs_v2 import Datadog
import aws_cdk_lib as cdk
from constructs import Construct

class RootStack(cdk.Stack):
    def __init__(self, scope, id, props=None):
        super().__init__(scope, id, props)
        NestedStack(self, "NestedStack")

        datadog = Datadog(self, "Datadog",
            node_layer_version=<LAYER_VERSION>,
            python_layer_version=<LAYER_VERSION>,
            add_layers=<BOOLEAN>,
            forwarder_arn="<FORWARDER_ARN>",
            flush_metrics_to_logs=<BOOLEAN>,
            site="<SITE>",
            api_key="{Datadog_API_Key}",
            api_key_secret_arn="{Secret_ARN_Datadog_API_Key}",
            api_kms_key="{Encrypted_Datadog_API_Key}",
            enable_datadog_tracing=<BOOLEAN>,
            enable_datadog_logs=<BOOLEAN>,
            inject_log_context=<BOOLEAN>
        )
        datadog.add_lambda_functions([<LAMBDA_FUNCTIONS>])

class NestedStack(cdk.NestedStack):
    def __init__(self, scope, id, props=None):
        super().__init__(scope, id, props)

        datadog = Datadog(self, "Datadog",
            node_layer_version=<LAYER_VERSION>,
            python_layer_version=<LAYER_VERSION>,
            add_layers=<BOOLEAN>,
            forwarder_arn="<FORWARDER_ARN>",
            flush_metrics_to_logs=<BOOLEAN>,
            site="<SITE>",
            api_key="{Datadog_API_Key}",
            api_key_secret_arn="{Secret_ARN_Datadog_API_Key}",
            api_kms_key="{Encrypted_Datadog_API_Key}",
            enable_datadog_tracing=<BOOLEAN>,
            enable_datadog_logs=<BOOLEAN>,
            inject_log_context=<BOOLEAN>
        )
        datadog.add_lambda_functions([<LAMBDA_FUNCTIONS>])
```

### Tags

Add tags to your constructs. We recommend setting an `env` and `service` tag to tie Datadog telemetry together. For more information see [official AWS documentation](https://docs.aws.amazon.com/cdk/latest/guide/tagging.html) and [CDK documentation](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.Tags.html).

## How it works

The Datadog CDK construct takes in a list of lambda functions and installs the Datadog Lambda Library by attaching the Lambda Layers for [Node.js](https://github.com/DataDog/datadog-lambda-layer-js) and [Python](https://github.com/DataDog/datadog-lambda-layer-python) to your functions. It redirects to a replacement handler that initializes the Lambda Library without any required code changes. Additional configurations added to the Datadog CDK construct will also translate into their respective environment variables under each lambda function (if applicable / required).

While Lambda function based log groups are handled by the `addLambdaFunctions` method automatically, the construct has an additional function `addForwarderToNonLambdaLogGroups` which subscribes the forwarder to any additional log groups of your choosing.

## Resources to learn about CDK

* [CDK TypeScript Workshop](https://cdkworkshop.com/20-typescript.html)
* [Video Introducing CDK by AWS with Demo](https://youtu.be/ZWCvNFUN-sU)
* [CDK Concepts](https://youtu.be/9As_ZIjUGmY)

## Repository Structure

In this repository, the folders `v1` and `v2` correspond to the packages `datadog-cdk-constructs` and `datadog-cdk-contructs-v2`. Each can be treated as a separate project (they are separate projen projects with separate dependencies, config files, tests, and scripts).

Additionally, there is a `common` folder that contains shared logic common to both `v1` and `v2` packages. This is done by soft-linking a `common` folder within `v1/src` and `v2/src` to the `common` folder in the root of the repository.

## Using Projen

The `v1` and `v2` Datadog CDK Construct Libraries both use Projen to maintain project configuration files such as the `package.json`, `.gitignore`, `.npmignore`, etc. Most of the configuration files will be protected by Projen via read-only permissions. In order to change these files, edit the `.projenrc.js` file within `v1` or `v2` folders, then run `npx projen` (while in `v1` or `v2`) to synthesize the new changes. Check out [Projen](https://github.com/projen/projen) for more details.

## Opening Issues

If you encounter a bug with this package, we want to hear about it. Before opening a new issue, search the existing issues to avoid duplicates.

When opening an issue, include the Datadog CDK Construct version, Node version, and stack trace if available. In addition, include the steps to reproduce when appropriate.

You can also open an issue for a feature request.

## Contributing

If you find an issue with this package and have a fix, please feel free to open a pull request following the [procedures](https://github.com/DataDog/datadog-cdk-constructs/blob/main/CONTRIBUTING.md).

## Testing

If you contribute to this package you can run the tests using `yarn test` within the `v1` or `v2` folders. This package also includes a sample application for manual testing:

1. Open a seperate terminal and `cd` into `v1` or `v2`.
2. Run `yarn watch`, this will ensure the Typescript files in the `src` directory are compiled to Javascript in the `lib` directory.
3. Navigate to `src/sample`, here you can edit `index.ts` to test your contributions manually.
4. At the root of the `v1` or `v2` directory (whichever you are working on), run `npx cdk --app lib/sample/index.js <CDK Command>`, replacing `<CDK Command>` with common CDK commands like `synth`, `diff`, or `deploy`.

* Note, if you receive "... is not authorized to perform: ..." you may also need to authorize the commands with your AWS credentials.

### Debug Logs

To display the debug logs for this library, set the `DD_CONSTRUCT_DEBUG_LOGS` env var to `true` when running `cdk synth` (use `--quiet` to suppress generated template output).

Example:
*Ensure you are at the root of the `v1` or `v2` directory*

```
DD_CONSTRUCT_DEBUG_LOGS=true npx cdk --app lib/sample/index.js synth --quiet
```

## Community

For product feedback and questions, join the `#serverless` channel in the [Datadog community on Slack](https://chat.datadoghq.com/).

## License

Unless explicitly stated otherwise all files in this repository are licensed under the Apache License Version 2.0.

This product includes software developed at Datadog (https://www.datadoghq.com/). Copyright 2021 Datadog, Inc.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_lambda
import aws_cdk.aws_lambda_nodejs
import aws_cdk.aws_lambda_python
import aws_cdk.aws_logs
import aws_cdk.core


class Datadog(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="datadog-cdk-constructs.Datadog",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        add_layers: typing.Optional[builtins.bool] = None,
        api_key: typing.Optional[builtins.str] = None,
        api_key_secret_arn: typing.Optional[builtins.str] = None,
        api_kms_key: typing.Optional[builtins.str] = None,
        capture_lambda_payload: typing.Optional[builtins.bool] = None,
        enable_datadog_logs: typing.Optional[builtins.bool] = None,
        enable_datadog_tracing: typing.Optional[builtins.bool] = None,
        env: typing.Optional[builtins.str] = None,
        extension_layer_version: typing.Optional[jsii.Number] = None,
        flush_metrics_to_logs: typing.Optional[builtins.bool] = None,
        forwarder_arn: typing.Optional[builtins.str] = None,
        inject_log_context: typing.Optional[builtins.bool] = None,
        log_level: typing.Optional[builtins.str] = None,
        node_layer_version: typing.Optional[jsii.Number] = None,
        python_layer_version: typing.Optional[jsii.Number] = None,
        service: typing.Optional[builtins.str] = None,
        site: typing.Optional[builtins.str] = None,
        tags: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param add_layers: 
        :param api_key: 
        :param api_key_secret_arn: 
        :param api_kms_key: 
        :param capture_lambda_payload: 
        :param enable_datadog_logs: 
        :param enable_datadog_tracing: 
        :param env: 
        :param extension_layer_version: 
        :param flush_metrics_to_logs: 
        :param forwarder_arn: 
        :param inject_log_context: 
        :param log_level: 
        :param node_layer_version: 
        :param python_layer_version: 
        :param service: 
        :param site: 
        :param tags: 
        :param version: 
        '''
        props = DatadogProps(
            add_layers=add_layers,
            api_key=api_key,
            api_key_secret_arn=api_key_secret_arn,
            api_kms_key=api_kms_key,
            capture_lambda_payload=capture_lambda_payload,
            enable_datadog_logs=enable_datadog_logs,
            enable_datadog_tracing=enable_datadog_tracing,
            env=env,
            extension_layer_version=extension_layer_version,
            flush_metrics_to_logs=flush_metrics_to_logs,
            forwarder_arn=forwarder_arn,
            inject_log_context=inject_log_context,
            log_level=log_level,
            node_layer_version=node_layer_version,
            python_layer_version=python_layer_version,
            service=service,
            site=site,
            tags=tags,
            version=version,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addForwarderToNonLambdaLogGroups")
    def add_forwarder_to_non_lambda_log_groups(
        self,
        log_groups: typing.Sequence[aws_cdk.aws_logs.ILogGroup],
    ) -> None:
        '''
        :param log_groups: -
        '''
        return typing.cast(None, jsii.invoke(self, "addForwarderToNonLambdaLogGroups", [log_groups]))

    @jsii.member(jsii_name="addGitCommitMetadata")
    def add_git_commit_metadata(
        self,
        lambda_functions: typing.Sequence[typing.Union[aws_cdk.aws_lambda.Function, aws_cdk.aws_lambda_nodejs.NodejsFunction, aws_cdk.aws_lambda_python.PythonFunction]],
        git_commit_sha: builtins.str,
    ) -> None:
        '''
        :param lambda_functions: -
        :param git_commit_sha: -
        '''
        return typing.cast(None, jsii.invoke(self, "addGitCommitMetadata", [lambda_functions, git_commit_sha]))

    @jsii.member(jsii_name="addLambdaFunctions")
    def add_lambda_functions(
        self,
        lambda_functions: typing.Sequence[typing.Union[aws_cdk.aws_lambda.Function, aws_cdk.aws_lambda_nodejs.NodejsFunction, aws_cdk.aws_lambda_python.PythonFunction]],
    ) -> None:
        '''
        :param lambda_functions: -
        '''
        return typing.cast(None, jsii.invoke(self, "addLambdaFunctions", [lambda_functions]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> "DatadogProps":
        return typing.cast("DatadogProps", jsii.get(self, "props"))

    @props.setter
    def props(self, value: "DatadogProps") -> None:
        jsii.set(self, "props", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> aws_cdk.core.Construct:
        return typing.cast(aws_cdk.core.Construct, jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: aws_cdk.core.Construct) -> None:
        jsii.set(self, "scope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transport")
    def transport(self) -> "Transport":
        return typing.cast("Transport", jsii.get(self, "transport"))

    @transport.setter
    def transport(self, value: "Transport") -> None:
        jsii.set(self, "transport", value)


@jsii.data_type(
    jsii_type="datadog-cdk-constructs.DatadogProps",
    jsii_struct_bases=[],
    name_mapping={
        "add_layers": "addLayers",
        "api_key": "apiKey",
        "api_key_secret_arn": "apiKeySecretArn",
        "api_kms_key": "apiKmsKey",
        "capture_lambda_payload": "captureLambdaPayload",
        "enable_datadog_logs": "enableDatadogLogs",
        "enable_datadog_tracing": "enableDatadogTracing",
        "env": "env",
        "extension_layer_version": "extensionLayerVersion",
        "flush_metrics_to_logs": "flushMetricsToLogs",
        "forwarder_arn": "forwarderArn",
        "inject_log_context": "injectLogContext",
        "log_level": "logLevel",
        "node_layer_version": "nodeLayerVersion",
        "python_layer_version": "pythonLayerVersion",
        "service": "service",
        "site": "site",
        "tags": "tags",
        "version": "version",
    },
)
class DatadogProps:
    def __init__(
        self,
        *,
        add_layers: typing.Optional[builtins.bool] = None,
        api_key: typing.Optional[builtins.str] = None,
        api_key_secret_arn: typing.Optional[builtins.str] = None,
        api_kms_key: typing.Optional[builtins.str] = None,
        capture_lambda_payload: typing.Optional[builtins.bool] = None,
        enable_datadog_logs: typing.Optional[builtins.bool] = None,
        enable_datadog_tracing: typing.Optional[builtins.bool] = None,
        env: typing.Optional[builtins.str] = None,
        extension_layer_version: typing.Optional[jsii.Number] = None,
        flush_metrics_to_logs: typing.Optional[builtins.bool] = None,
        forwarder_arn: typing.Optional[builtins.str] = None,
        inject_log_context: typing.Optional[builtins.bool] = None,
        log_level: typing.Optional[builtins.str] = None,
        node_layer_version: typing.Optional[jsii.Number] = None,
        python_layer_version: typing.Optional[jsii.Number] = None,
        service: typing.Optional[builtins.str] = None,
        site: typing.Optional[builtins.str] = None,
        tags: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param add_layers: 
        :param api_key: 
        :param api_key_secret_arn: 
        :param api_kms_key: 
        :param capture_lambda_payload: 
        :param enable_datadog_logs: 
        :param enable_datadog_tracing: 
        :param env: 
        :param extension_layer_version: 
        :param flush_metrics_to_logs: 
        :param forwarder_arn: 
        :param inject_log_context: 
        :param log_level: 
        :param node_layer_version: 
        :param python_layer_version: 
        :param service: 
        :param site: 
        :param tags: 
        :param version: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if add_layers is not None:
            self._values["add_layers"] = add_layers
        if api_key is not None:
            self._values["api_key"] = api_key
        if api_key_secret_arn is not None:
            self._values["api_key_secret_arn"] = api_key_secret_arn
        if api_kms_key is not None:
            self._values["api_kms_key"] = api_kms_key
        if capture_lambda_payload is not None:
            self._values["capture_lambda_payload"] = capture_lambda_payload
        if enable_datadog_logs is not None:
            self._values["enable_datadog_logs"] = enable_datadog_logs
        if enable_datadog_tracing is not None:
            self._values["enable_datadog_tracing"] = enable_datadog_tracing
        if env is not None:
            self._values["env"] = env
        if extension_layer_version is not None:
            self._values["extension_layer_version"] = extension_layer_version
        if flush_metrics_to_logs is not None:
            self._values["flush_metrics_to_logs"] = flush_metrics_to_logs
        if forwarder_arn is not None:
            self._values["forwarder_arn"] = forwarder_arn
        if inject_log_context is not None:
            self._values["inject_log_context"] = inject_log_context
        if log_level is not None:
            self._values["log_level"] = log_level
        if node_layer_version is not None:
            self._values["node_layer_version"] = node_layer_version
        if python_layer_version is not None:
            self._values["python_layer_version"] = python_layer_version
        if service is not None:
            self._values["service"] = service
        if site is not None:
            self._values["site"] = site
        if tags is not None:
            self._values["tags"] = tags
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def add_layers(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("add_layers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_key_secret_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("api_key_secret_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_kms_key(self) -> typing.Optional[builtins.str]:
        result = self._values.get("api_kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def capture_lambda_payload(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("capture_lambda_payload")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_datadog_logs(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enable_datadog_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_datadog_tracing(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enable_datadog_tracing")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def env(self) -> typing.Optional[builtins.str]:
        result = self._values.get("env")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extension_layer_version(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("extension_layer_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def flush_metrics_to_logs(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("flush_metrics_to_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def forwarder_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("forwarder_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inject_log_context(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("inject_log_context")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_layer_version(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("node_layer_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def python_layer_version(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("python_layer_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def site(self) -> typing.Optional[builtins.str]:
        result = self._values.get("site")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[builtins.str]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatadogProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="datadog-cdk-constructs.DatadogStrictProps",
    jsii_struct_bases=[],
    name_mapping={
        "add_layers": "addLayers",
        "capture_lambda_payload": "captureLambdaPayload",
        "enable_datadog_logs": "enableDatadogLogs",
        "enable_datadog_tracing": "enableDatadogTracing",
        "inject_log_context": "injectLogContext",
        "api_key": "apiKey",
        "api_key_secret_arn": "apiKeySecretArn",
        "api_kms_key": "apiKmsKey",
        "extension_layer_version": "extensionLayerVersion",
        "flush_metrics_to_logs": "flushMetricsToLogs",
        "forwarder_arn": "forwarderArn",
        "log_level": "logLevel",
        "node_layer_version": "nodeLayerVersion",
        "python_layer_version": "pythonLayerVersion",
        "site": "site",
    },
)
class DatadogStrictProps:
    def __init__(
        self,
        *,
        add_layers: builtins.bool,
        capture_lambda_payload: builtins.bool,
        enable_datadog_logs: builtins.bool,
        enable_datadog_tracing: builtins.bool,
        inject_log_context: builtins.bool,
        api_key: typing.Optional[builtins.str] = None,
        api_key_secret_arn: typing.Optional[builtins.str] = None,
        api_kms_key: typing.Optional[builtins.str] = None,
        extension_layer_version: typing.Optional[jsii.Number] = None,
        flush_metrics_to_logs: typing.Optional[builtins.bool] = None,
        forwarder_arn: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
        node_layer_version: typing.Optional[jsii.Number] = None,
        python_layer_version: typing.Optional[jsii.Number] = None,
        site: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param add_layers: 
        :param capture_lambda_payload: 
        :param enable_datadog_logs: 
        :param enable_datadog_tracing: 
        :param inject_log_context: 
        :param api_key: 
        :param api_key_secret_arn: 
        :param api_kms_key: 
        :param extension_layer_version: 
        :param flush_metrics_to_logs: 
        :param forwarder_arn: 
        :param log_level: 
        :param node_layer_version: 
        :param python_layer_version: 
        :param site: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "add_layers": add_layers,
            "capture_lambda_payload": capture_lambda_payload,
            "enable_datadog_logs": enable_datadog_logs,
            "enable_datadog_tracing": enable_datadog_tracing,
            "inject_log_context": inject_log_context,
        }
        if api_key is not None:
            self._values["api_key"] = api_key
        if api_key_secret_arn is not None:
            self._values["api_key_secret_arn"] = api_key_secret_arn
        if api_kms_key is not None:
            self._values["api_kms_key"] = api_kms_key
        if extension_layer_version is not None:
            self._values["extension_layer_version"] = extension_layer_version
        if flush_metrics_to_logs is not None:
            self._values["flush_metrics_to_logs"] = flush_metrics_to_logs
        if forwarder_arn is not None:
            self._values["forwarder_arn"] = forwarder_arn
        if log_level is not None:
            self._values["log_level"] = log_level
        if node_layer_version is not None:
            self._values["node_layer_version"] = node_layer_version
        if python_layer_version is not None:
            self._values["python_layer_version"] = python_layer_version
        if site is not None:
            self._values["site"] = site

    @builtins.property
    def add_layers(self) -> builtins.bool:
        result = self._values.get("add_layers")
        assert result is not None, "Required property 'add_layers' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def capture_lambda_payload(self) -> builtins.bool:
        result = self._values.get("capture_lambda_payload")
        assert result is not None, "Required property 'capture_lambda_payload' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def enable_datadog_logs(self) -> builtins.bool:
        result = self._values.get("enable_datadog_logs")
        assert result is not None, "Required property 'enable_datadog_logs' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def enable_datadog_tracing(self) -> builtins.bool:
        result = self._values.get("enable_datadog_tracing")
        assert result is not None, "Required property 'enable_datadog_tracing' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def inject_log_context(self) -> builtins.bool:
        result = self._values.get("inject_log_context")
        assert result is not None, "Required property 'inject_log_context' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_key_secret_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("api_key_secret_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_kms_key(self) -> typing.Optional[builtins.str]:
        result = self._values.get("api_kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extension_layer_version(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("extension_layer_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def flush_metrics_to_logs(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("flush_metrics_to_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def forwarder_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("forwarder_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_layer_version(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("node_layer_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def python_layer_version(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("python_layer_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def site(self) -> typing.Optional[builtins.str]:
        result = self._values.get("site")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatadogStrictProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="datadog-cdk-constructs.ILambdaFunction")
class ILambdaFunction(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="node")
    def node(self) -> "Node":
        ...

    @node.setter
    def node(self, value: "Node") -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> "Runtime":
        ...

    @runtime.setter
    def runtime(self, value: "Runtime") -> None:
        ...

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(
        self,
        key: builtins.str,
        value: builtins.str,
        options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param key: -
        :param value: -
        :param options: -
        '''
        ...


class _ILambdaFunctionProxy:
    __jsii_type__: typing.ClassVar[str] = "datadog-cdk-constructs.ILambdaFunction"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="node")
    def node(self) -> "Node":
        return typing.cast("Node", jsii.get(self, "node"))

    @node.setter
    def node(self, value: "Node") -> None:
        jsii.set(self, "node", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> "Runtime":
        return typing.cast("Runtime", jsii.get(self, "runtime"))

    @runtime.setter
    def runtime(self, value: "Runtime") -> None:
        jsii.set(self, "runtime", value)

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(
        self,
        key: builtins.str,
        value: builtins.str,
        options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param key: -
        :param value: -
        :param options: -
        '''
        return typing.cast(None, jsii.invoke(self, "addEnvironment", [key, value, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILambdaFunction).__jsii_proxy_class__ = lambda : _ILambdaFunctionProxy


@jsii.data_type(
    jsii_type="datadog-cdk-constructs.Node",
    jsii_struct_bases=[],
    name_mapping={"default_child": "defaultChild"},
)
class Node:
    def __init__(self, *, default_child: typing.Any) -> None:
        '''
        :param default_child: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "default_child": default_child,
        }

    @builtins.property
    def default_child(self) -> typing.Any:
        result = self._values.get("default_child")
        assert result is not None, "Required property 'default_child' is missing"
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Node(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="datadog-cdk-constructs.Runtime",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class Runtime:
    def __init__(self, *, name: builtins.str) -> None:
        '''
        :param name: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Runtime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="datadog-cdk-constructs.RuntimeType")
class RuntimeType(enum.Enum):
    NODE = "NODE"
    PYTHON = "PYTHON"
    UNSUPPORTED = "UNSUPPORTED"


@jsii.enum(jsii_type="datadog-cdk-constructs.TagKeys")
class TagKeys(enum.Enum):
    CDK = "CDK"
    ENV = "ENV"
    SERVICE = "SERVICE"
    VERSION = "VERSION"


class Transport(metaclass=jsii.JSIIMeta, jsii_type="datadog-cdk-constructs.Transport"):
    def __init__(
        self,
        flush_metrics_to_logs: typing.Optional[builtins.bool] = None,
        site: typing.Optional[builtins.str] = None,
        api_key: typing.Optional[builtins.str] = None,
        api_key_secret_arn: typing.Optional[builtins.str] = None,
        api_kms_key: typing.Optional[builtins.str] = None,
        extension_layer_version: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param flush_metrics_to_logs: -
        :param site: -
        :param api_key: -
        :param api_key_secret_arn: -
        :param api_kms_key: -
        :param extension_layer_version: -
        '''
        jsii.create(self.__class__, self, [flush_metrics_to_logs, site, api_key, api_key_secret_arn, api_kms_key, extension_layer_version])

    @jsii.member(jsii_name="applyEnvVars")
    def apply_env_vars(self, lambdas: typing.Sequence[ILambdaFunction]) -> None:
        '''
        :param lambdas: -
        '''
        return typing.cast(None, jsii.invoke(self, "applyEnvVars", [lambdas]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="flushMetricsToLogs")
    def flush_metrics_to_logs(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "flushMetricsToLogs"))

    @flush_metrics_to_logs.setter
    def flush_metrics_to_logs(self, value: builtins.bool) -> None:
        jsii.set(self, "flushMetricsToLogs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="site")
    def site(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "site"))

    @site.setter
    def site(self, value: builtins.str) -> None:
        jsii.set(self, "site", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "apiKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKeySecretArn")
    def api_key_secret_arn(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeySecretArn"))

    @api_key_secret_arn.setter
    def api_key_secret_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "apiKeySecretArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKmsKey")
    def api_kms_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKmsKey"))

    @api_kms_key.setter
    def api_kms_key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "apiKmsKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extensionLayerVersion")
    def extension_layer_version(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "extensionLayerVersion"))

    @extension_layer_version.setter
    def extension_layer_version(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "extensionLayerVersion", value)


__all__ = [
    "Datadog",
    "DatadogProps",
    "DatadogStrictProps",
    "ILambdaFunction",
    "Node",
    "Runtime",
    "RuntimeType",
    "TagKeys",
    "Transport",
]

publication.publish()
