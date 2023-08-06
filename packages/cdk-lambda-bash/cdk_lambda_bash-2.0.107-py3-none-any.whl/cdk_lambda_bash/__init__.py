'''
[![NPM version](https://badge.fury.io/js/cdk-lambda-bash.svg)](https://badge.fury.io/js/cdk-lambda-bash)
[![PyPI version](https://badge.fury.io/py/cdk-lambda-bash.svg)](https://badge.fury.io/py/cdk-lambda-bash)
[![Release](https://github.com/pahud/cdk-lambda-bash/actions/workflows/release.yml/badge.svg)](https://github.com/pahud/cdk-lambda-bash/actions/workflows/release.yml)

# cdk-lambda-bash

Deploy Bash Lambda Functions with AWS CDK

# Why

AWS Lambda has the [docker container image support](https://aws.amazon.com/tw/blogs/aws/new-for-aws-lambda-container-image-support/) since AWS re:Invent 2020 which allows you to run your Lambda code in a custom container image. Inspired by [nikovirtala/cdk-eks-experiment](https://github.com/nikovirtala/cdk-eks-experiment/), `cdk-lambda-bash` allows you to specify a local shell script and bundle it up as a custom resource in your cdk stack. On cdk deployment, your shell script will be executed in a Lambda container environment.

# BashExecFunction

At this moment, we are offering `BashExecFunction` construct class which is a high-level abstraction of `lambda.Function`. By defining the `script` property which poins to your local shell script, on `cdk deploy`, this script will be bundled into a custom docker image and published as a `lambda.DockerImageFunction`.

If you `fn.run()`, a custom resource will be created and the `lambda.DockerImageFunction` will be executed on deployment.

# Install

Use the npm dist tag to opt in CDKv1 or CDKv2:

```sh
// for CDKv2
npm install cdk-lambda-bash
or
npm install cdk-lambda-bash@latest

// for CDKv1
npm install cdk-lambda-bash@cdkv1
```

# Sample

```python
const app = new cdk.App();

const stack = new cdk.Stack(app, 'my-stack');

// bundle your Lambda function to execute the local demo.sh in container
const fn = new BashExecFunction(stack, 'Demo', {
  script: path.join(__dirname, '../demo.sh'),
})

// run it as custom resource on deployment
fn.run();
```

## Re-execution on assets update

By default, if you update your shell script or Dockerfile and re-deploy your CDK application, the `BashExecFunction`
will not be re-executed. Use `runOnUpdate` to enable the re-execution on update.

```python
fn.run({ runOnUpdate: true });
```

## Custom Dockerfile

In some cases, you may customize your own `Dockerfile`, for instances:

1. You need extra tools or utilities such as `kubectl` or `helm`
2. You need build from your own base image

In these cases, create a custom `Dockerfile` as below and add extra utilities i.e. `kubectl`:

<details><summary>click and view custom Dockerfile sample</summary>

```bash
FROM public.ecr.aws/lambda/provided:al2

RUN yum install -y unzip jq

# install aws-cli v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
  unzip awscliv2.zip && \
  ./aws/install

# install kubectl
RUN curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/kubectl && \
  chmod +x kubectl && \
  mv kubectl /usr/local/bin/kubectl

COPY bootstrap /var/runtime/bootstrap
COPY function.sh /var/task/function.sh
COPY main.sh /var/task/main.sh
RUN chmod +x /var/runtime/bootstrap /var/task/function.sh /var/task/main.sh

WORKDIR /var/task
CMD [ "function.sh.handler" ]
```

</details>

Specify your own `Dockerfile` with the `dockerfile` property.

```python
new BashExecFunction(stack, 'Demo', {
  script: path.join(__dirname, '../demo.sh'),
  dockerfile: path.join(__dirname, '../Dockerfile'),
});
```

# Conditional Execution

In the user script(e.g. `demo.sh`), you are allowed to determine the event type and act accordingly.

For example

```python

const installArgoCD = new BashExecFunction(...)

installArgoCD.run({runOnUpdate: true});
```

When you run this sample, `demo.sh` will receive `onCreate` event and you can run your custom logic to "install ArgoCD" like `kubectl apply -f URL`. However, if you comment it off and deploy again:

```python
const installArgoCD = new BashExecFunction(...)

//installArgoCD.run({runOnUpdate: true});
```

Under the hood, `demo.sh` will receive `onDelete` event and you can run your custom logic to "uninstall ArgoCD"
like `kubectl delete -f URL`.

Check the full sample code below:

<details><summary>Click and view the sample code</summary>

```sh
#!/bin/bash

# implement your business logic below
function onCreate() {
  echo "running kubectl apply -f ..."
}

function onUpdate() {
  echo "do nothing on update"
}

function onDelete() {
  echo "running kubectl delete -f ..."
}

function getRequestType() {
  echo $1 | jq -r .RequestType
}

function conditionalExec() {
  requestType=$(getRequestType $EVENT_DATA)

  # determine the original request type
  case $requestType in
    'Create') onCreate $1 ;;
    'Update') onUpdate $1 ;;
    'Delete') onDelete $1 ;;
  esac
}

echo "Hello cdk lambda bash!!"

conditionalExec

exit 0
```

</details>

# In Action

See this [tweet](https://twitter.com/pahudnet/status/1370301964836241408)

![](https://pbs.twimg.com/media/EwRGRxnUcAQBng-?format=jpg&name=4096x4096)

![](https://pbs.twimg.com/media/EwRKGfsUYAENjP-?format=jpg&name=4096x4096)
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

import aws_cdk
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import constructs


class BashExecFunction(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-lambda-bash.BashExecFunction",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        script: builtins.str,
        dockerfile: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param script: The path of the shell script to be executed.
        :param dockerfile: The path of your custom dockerfile.
        :param environment: Lambda environment variables.
        :param role: Custom lambda execution role. Default: - auto generated role.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: - Duration.seconds(60)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BashExecFunction.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BashExecFunctionProps(
            script=script,
            dockerfile=dockerfile,
            environment=environment,
            role=role,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="run")
    def run(
        self,
        *,
        run_on_update: typing.Optional[builtins.bool] = None,
    ) -> aws_cdk.CustomResource:
        '''
        :param run_on_update: whether to run the lambda function again on the provider update. Default: false;
        '''
        ops = RunOps(run_on_update=run_on_update)

        return typing.cast(aws_cdk.CustomResource, jsii.invoke(self, "run", [ops]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.DockerImageFunction:
        return typing.cast(aws_cdk.aws_lambda.DockerImageFunction, jsii.get(self, "handler"))


@jsii.data_type(
    jsii_type="cdk-lambda-bash.BashExecFunctionProps",
    jsii_struct_bases=[],
    name_mapping={
        "script": "script",
        "dockerfile": "dockerfile",
        "environment": "environment",
        "role": "role",
        "timeout": "timeout",
    },
)
class BashExecFunctionProps:
    def __init__(
        self,
        *,
        script: builtins.str,
        dockerfile: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param script: The path of the shell script to be executed.
        :param dockerfile: The path of your custom dockerfile.
        :param environment: Lambda environment variables.
        :param role: Custom lambda execution role. Default: - auto generated role.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: - Duration.seconds(60)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BashExecFunctionProps.__init__)
            check_type(argname="argument script", value=script, expected_type=type_hints["script"])
            check_type(argname="argument dockerfile", value=dockerfile, expected_type=type_hints["dockerfile"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[str, typing.Any] = {
            "script": script,
        }
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if environment is not None:
            self._values["environment"] = environment
        if role is not None:
            self._values["role"] = role
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def script(self) -> builtins.str:
        '''The path of the shell script to be executed.'''
        result = self._values.get("script")
        assert result is not None, "Required property 'script' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''The path of your custom dockerfile.'''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Lambda environment variables.'''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Custom lambda execution role.

        :default: - auto generated role.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        '''The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value based on the function's expected execution time.

        :default: - Duration.seconds(60)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BashExecFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-lambda-bash.RunOps",
    jsii_struct_bases=[],
    name_mapping={"run_on_update": "runOnUpdate"},
)
class RunOps:
    def __init__(self, *, run_on_update: typing.Optional[builtins.bool] = None) -> None:
        '''
        :param run_on_update: whether to run the lambda function again on the provider update. Default: false;
        '''
        if __debug__:
            type_hints = typing.get_type_hints(RunOps.__init__)
            check_type(argname="argument run_on_update", value=run_on_update, expected_type=type_hints["run_on_update"])
        self._values: typing.Dict[str, typing.Any] = {}
        if run_on_update is not None:
            self._values["run_on_update"] = run_on_update

    @builtins.property
    def run_on_update(self) -> typing.Optional[builtins.bool]:
        '''whether to run the lambda function again on the provider update.

        :default: false;
        '''
        result = self._values.get("run_on_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RunOps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BashExecFunction",
    "BashExecFunctionProps",
    "RunOps",
]

publication.publish()
