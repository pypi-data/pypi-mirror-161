'''
# aws-cognito-apigateway-lambda module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_cognito_apigateway_lambda`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-cognito-apigateway-lambda`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.cognitoapigatewaylambda`|

## Overview

This AWS Solutions Construct implements an Amazon Cognito securing an Amazon API Gateway Lambda backed REST APIs pattern.

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { CognitoToApiGatewayToLambda } from '@aws-solutions-constructs/aws-cognito-apigateway-lambda';
import * as lambda from 'aws-cdk-lib/aws-lambda';

new CognitoToApiGatewayToLambda(this, 'test-cognito-apigateway-lambda', {
  lambdaFunctionProps: {
    code: lambda.Code.fromAsset(`lambda`),
    runtime: lambda.Runtime.NODEJS_14_X,
    handler: 'index.handler'
  }
});
```

Python

```python
from aws_solutions_constructs.aws_cognito_apigateway_lambda import CognitoToApiGatewayToLambda
from aws_cdk import (
    aws_lambda as _lambda,
    Stack
)
from constructs import Construct

CognitoToApiGatewayToLambda(self, 'test-cognito-apigateway-lambda',
                            lambda_function_props=_lambda.FunctionProps(
                                code=_lambda.Code.from_asset('lambda'),
                                runtime=_lambda.Runtime.PYTHON_3_9,
                                handler='index.handler'
                            )
                            )

```

Java

```java
import software.constructs.Construct;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awscdk.services.lambda.*;
import software.amazon.awscdk.services.lambda.Runtime;
import software.amazon.awsconstructs.services.cognitoapigatewaylambda.*;

new CognitoToApiGatewayToLambda(this, "test-cognito-apigateway-lambda",
        new CognitoToApiGatewayToLambdaProps.Builder()
                .lambdaFunctionProps(new FunctionProps.Builder()
                        .runtime(Runtime.NODEJS_14_X)
                        .code(Code.fromAsset("lambda"))
                        .handler("index.handler")
                        .build())
                .build());
```

If you are defining resources and methods on your API (e.g. proxy = false), then you must call addAuthorizers() after the API is fully defined to ensure every method is protected. Here is an example:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { CognitoToApiGatewayToLambda } from '@aws-solutions-constructs/aws-cognito-apigateway-lambda';
import * as lambda from 'aws-cdk-lib/aws-lambda';

const construct = new CognitoToApiGatewayToLambda(this, 'test-cognito-apigateway-lambda', {
    lambdaFunctionProps: {
        code: lambda.Code.fromAsset(`lambda`),
        runtime: lambda.Runtime.NODEJS_14_X,
        handler: 'index.handler'
    },
    apiGatewayProps: {
        proxy: false
    }
});

const resource = construct.apiGateway.root.addResource('foobar');
resource.addMethod('POST');

// Mandatory to call this method to Apply the Cognito Authorizers on all API methods
construct.addAuthorizers();
```

Python

```python
from aws_solutions_constructs.aws_cognito_apigateway_lambda import CognitoToApiGatewayToLambda
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as api,
    Stack
)
from constructs import Construct
from typing import Any

# Overriding LambdaRestApiProps with type Any
gateway_props = dict[Any, Any]

construct = CognitoToApiGatewayToLambda(self, 'test-cognito-apigateway-lambda',
                                        lambda_function_props=_lambda.FunctionProps(
                                            code=_lambda.Code.from_asset(
                                                'lambda'),
                                            runtime=_lambda.Runtime.PYTHON_3_9,
                                            handler='index.handler'
                                        ),
                                        api_gateway_props=gateway_props(
                                            proxy=False
                                        )
                                        )

resource = construct.api_gateway.root.add_resource('foobar')
resource.add_method('POST')

# Mandatory to call this method to Apply the Cognito Authorizers on all API methods
construct.add_authorizers()
```

Java

```java
import software.constructs.Construct;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import software.amazon.awscdk.*;
import software.amazon.awscdk.services.lambda.*;
import software.amazon.awscdk.services.lambda.Runtime;
import software.amazon.awscdk.services.apigateway.IResource;
import software.amazon.awsconstructs.services.cognitoapigatewaylambda.*;

// Overriding LambdaRestApiProps with type Any
Map<String, Optional<?>> gatewayProps = new HashMap<String, Optional<?>>();
gatewayProps.put("proxy", Optional.of(false));

final CognitoToApiGatewayToLambda construct = new CognitoToApiGatewayToLambda(this,
        "test-cognito-apigateway-lambda",
        new CognitoToApiGatewayToLambdaProps.Builder()
                .lambdaFunctionProps(new FunctionProps.Builder()
                        .runtime(Runtime.NODEJS_14_X)
                        .code(Code.fromAsset("lambda"))
                        .handler("index.handler")
                        .build())
                .apiGatewayProps(gatewayProps)
                .build());

final IResource resource = construct.getApiGateway().getRoot().addResource("foobar");
resource.addMethod("POST");

// Mandatory to call this method to Apply the Cognito Authorizers on all API methods
construct.addAuthorizers();
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Existing instance of Lambda Function object, providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|User provided props to override the default props for the Lambda function.|
|apiGatewayProps?|[`api.LambdaRestApiProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.LambdaRestApi.html)|Optional user provided props to override the default props for API Gateway|
|cognitoUserPoolProps?|[`cognito.UserPoolProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cognito.UserPoolProps.html)|Optional user provided props to override the default props for Cognito User Pool|
|cognitoUserPoolClientProps?|[`cognito.UserPoolClientProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cognito.UserPoolClientProps.html)|Optional user provided props to override the default props for Cognito User Pool Client|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|userPool|[`cognito.UserPool`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cognito.UserPool.html)|Returns an instance of cognito.UserPool created by the construct|
|userPoolClient|[`cognito.UserPoolClient`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cognito.UserPoolClient.html)|Returns an instance of cognito.UserPoolClient created by the construct|
|apiGateway|[`api.RestApi`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.RestApi.html)|Returns an instance of api.RestApi created by the construct|
|apiGatewayCloudWatchRole?|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway for CloudWatch access.|
|apiGatewayLogGroup|[`logs.LogGroup`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroup.html)|Returns an instance of the LogGroup created by the construct for API Gateway access logging to CloudWatch.|
|apiGatewayAuthorizer|[`api.CfnAuthorizer`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.CfnAuthorizer.html)|Returns an instance of the api.CfnAuthorizer created by the construct for API Gateway methods authorization.|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of lambda.Function created by the construct|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon Cognito

* Set password policy for User Pools
* Enforce the advanced security mode for User Pools

### Amazon API Gateway

* Deploy an edge-optimized API endpoint
* Enable CloudWatch logging for API Gateway
* Configure least privilege access IAM role for API Gateway
* Set the default authorizationType for all API methods to Cognito User Pool
* Enable X-Ray Tracing

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Set Environment Variables

  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

## Architecture

![Architecture Diagram](architecture.png)

---


© Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import aws_cdk.aws_apigateway
import aws_cdk.aws_cognito
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.core


class CognitoToApiGatewayToLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-cognito-apigateway-lambda.CognitoToApiGatewayToLambda",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        api_gateway_props: typing.Any = None,
        cognito_user_pool_client_props: typing.Any = None,
        cognito_user_pool_props: typing.Optional[typing.Union[aws_cdk.aws_cognito.UserPoolProps, typing.Dict[str, typing.Any]]] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        lambda_function_props: typing.Optional[typing.Union[aws_cdk.aws_lambda.FunctionProps, typing.Dict[str, typing.Any]]] = None,
        log_group_props: typing.Optional[typing.Union[aws_cdk.aws_logs.LogGroupProps, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param api_gateway_props: Optional user provided props to override the default props for the API Gateway. Default: - Default props are used
        :param cognito_user_pool_client_props: Optional user provided props to override the default props. Default: - Default props are used
        :param cognito_user_pool_props: Optional user provided props to override the default props. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the CognitoToApiGatewayToLambda class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoToApiGatewayToLambda.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CognitoToApiGatewayToLambdaProps(
            api_gateway_props=api_gateway_props,
            cognito_user_pool_client_props=cognito_user_pool_client_props,
            cognito_user_pool_props=cognito_user_pool_props,
            existing_lambda_obj=existing_lambda_obj,
            lambda_function_props=lambda_function_props,
            log_group_props=log_group_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addAuthorizers")
    def add_authorizers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "addAuthorizers", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> aws_cdk.aws_apigateway.RestApi:
        return typing.cast(aws_cdk.aws_apigateway.RestApi, jsii.get(self, "apiGateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayAuthorizer")
    def api_gateway_authorizer(self) -> aws_cdk.aws_apigateway.CfnAuthorizer:
        return typing.cast(aws_cdk.aws_apigateway.CfnAuthorizer, jsii.get(self, "apiGatewayAuthorizer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayLogGroup")
    def api_gateway_log_group(self) -> aws_cdk.aws_logs.LogGroup:
        return typing.cast(aws_cdk.aws_logs.LogGroup, jsii.get(self, "apiGatewayLogGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPool")
    def user_pool(self) -> aws_cdk.aws_cognito.UserPool:
        return typing.cast(aws_cdk.aws_cognito.UserPool, jsii.get(self, "userPool"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolClient")
    def user_pool_client(self) -> aws_cdk.aws_cognito.UserPoolClient:
        return typing.cast(aws_cdk.aws_cognito.UserPoolClient, jsii.get(self, "userPoolClient"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], jsii.get(self, "apiGatewayCloudWatchRole"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-cognito-apigateway-lambda.CognitoToApiGatewayToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_gateway_props": "apiGatewayProps",
        "cognito_user_pool_client_props": "cognitoUserPoolClientProps",
        "cognito_user_pool_props": "cognitoUserPoolProps",
        "existing_lambda_obj": "existingLambdaObj",
        "lambda_function_props": "lambdaFunctionProps",
        "log_group_props": "logGroupProps",
    },
)
class CognitoToApiGatewayToLambdaProps:
    def __init__(
        self,
        *,
        api_gateway_props: typing.Any = None,
        cognito_user_pool_client_props: typing.Any = None,
        cognito_user_pool_props: typing.Optional[typing.Union[aws_cdk.aws_cognito.UserPoolProps, typing.Dict[str, typing.Any]]] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        lambda_function_props: typing.Optional[typing.Union[aws_cdk.aws_lambda.FunctionProps, typing.Dict[str, typing.Any]]] = None,
        log_group_props: typing.Optional[typing.Union[aws_cdk.aws_logs.LogGroupProps, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param api_gateway_props: Optional user provided props to override the default props for the API Gateway. Default: - Default props are used
        :param cognito_user_pool_client_props: Optional user provided props to override the default props. Default: - Default props are used
        :param cognito_user_pool_props: Optional user provided props to override the default props. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used

        :summary: The properties for the CognitoToApiGatewayToLambda Construct
        '''
        if isinstance(cognito_user_pool_props, dict):
            cognito_user_pool_props = aws_cdk.aws_cognito.UserPoolProps(**cognito_user_pool_props)
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        if isinstance(log_group_props, dict):
            log_group_props = aws_cdk.aws_logs.LogGroupProps(**log_group_props)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoToApiGatewayToLambdaProps.__init__)
            check_type(argname="argument api_gateway_props", value=api_gateway_props, expected_type=type_hints["api_gateway_props"])
            check_type(argname="argument cognito_user_pool_client_props", value=cognito_user_pool_client_props, expected_type=type_hints["cognito_user_pool_client_props"])
            check_type(argname="argument cognito_user_pool_props", value=cognito_user_pool_props, expected_type=type_hints["cognito_user_pool_props"])
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument log_group_props", value=log_group_props, expected_type=type_hints["log_group_props"])
        self._values: typing.Dict[str, typing.Any] = {}
        if api_gateway_props is not None:
            self._values["api_gateway_props"] = api_gateway_props
        if cognito_user_pool_client_props is not None:
            self._values["cognito_user_pool_client_props"] = cognito_user_pool_client_props
        if cognito_user_pool_props is not None:
            self._values["cognito_user_pool_props"] = cognito_user_pool_props
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props

    @builtins.property
    def api_gateway_props(self) -> typing.Any:
        '''Optional user provided props to override the default props for the API Gateway.

        :default: - Default props are used
        '''
        result = self._values.get("api_gateway_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def cognito_user_pool_client_props(self) -> typing.Any:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("cognito_user_pool_client_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def cognito_user_pool_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_cognito.UserPoolProps]:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("cognito_user_pool_props")
        return typing.cast(typing.Optional[aws_cdk.aws_cognito.UserPoolProps], result)

    @builtins.property
    def existing_lambda_obj(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        '''User provided props to override the default props for the Lambda function.

        :default: - Default props are used
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FunctionProps], result)

    @builtins.property
    def log_group_props(self) -> typing.Optional[aws_cdk.aws_logs.LogGroupProps]:
        '''User provided props to override the default props for the CloudWatchLogs LogGroup.

        :default: - Default props are used
        '''
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.LogGroupProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoToApiGatewayToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CognitoToApiGatewayToLambda",
    "CognitoToApiGatewayToLambdaProps",
]

publication.publish()
