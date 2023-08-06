'''
# aws-lambda-elasticachememcached module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_lambda_elasticachememcached`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-lambda-elasticachememcached`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.lambdaelasticachememcached`|

## Overview

This AWS Solutions Construct implements an AWS Lambda function connected to an Amazon Elasticache Memcached cluster.

Here is a minimal deployable pattern definition :

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { LambdaToElasticachememcached } from '@aws-solutions-constructs/aws-lambda-elasticachememcached';
import * as lambda from 'aws-cdk-lib/aws-lambda';

new LambdaToElasticachememcached(this, 'LambdaToElasticachememcachedPattern', {
    lambdaFunctionProps: {
        runtime: lambda.Runtime.NODEJS_14_X,
        handler: 'index.handler',
        code: lambda.Code.fromAsset(`lambda`)
    }
});
```

Python

```python
from aws_solutions_constructs.aws_lambda_elasticachememcached import LambdaToElasticachememcached
from aws_cdk import (
    aws_lambda as _lambda,
    Stack
)
from constructs import Construct

LambdaToElasticachememcached(self, 'LambdaToCachePattern',
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
import software.amazon.awsconstructs.services.lambdaelasticachememcached.*;

new LambdaToElasticachememcached(this, "LambdaToCachePattern", new LambdaToElasticachememcachedProps.Builder()
        .lambdaFunctionProps(new FunctionProps.Builder()
                .runtime(Runtime.NODEJS_14_X)
                .code(Code.fromAsset("lambda"))
                .handler("index.handler")
                .build())
        .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Existing instance of Lambda Function object, providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|Optional user provided props to override the default props for the Lambda function.|
|existingVpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|An optional, existing VPC into which this pattern should be deployed. When deployed in a VPC, the Lambda function will use ENIs in the VPC to access network resources and an Interface Endpoint will be created in the VPC for Amazon SQS. If an existing VPC is provided, the `deployVpc` property cannot be `true`. This uses `ec2.IVpc` to allow clients to supply VPCs that exist outside the stack using the [`ec2.Vpc.fromLookup()`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.Vpc.html#static-fromwbrlookupscope-id-options) method.|
|vpcProps?|[`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.VpcProps.html)|Optional user provided properties to override the default properties for the new VPC. `subnetConfiguration` is set by the pattern, so any values for those properties supplied here will be overrriden. |
| cacheEndpointEnvironmentVariableName?| string | Optional Name for the Lambda function environment variable set to the cache endpoint. Default: CACHE_ENDPOINT |
| cacheProps? | [`cache.CfnCacheClusterProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_elasticache.CfnCacheClusterProps.html) | Optional user provided props to override the default props for the Elasticache Cluster. Providing both this and `existingCache` will cause an error. |
| existingCache? | [`cache.CfnCacheCluster`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_elasticache.CfnCacheCluster.html#attrconfigurationendpointport) | Existing instance of Elasticache Cluster object, providing both this and `cacheProps` will cause an error. If you provide this, you must provide the associated VPC in existingVpc. |

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of the Lambda function used by the pattern.|
|vpc |[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|Returns an interface on the VPC used by the pattern. This may be a VPC created by the pattern or the VPC supplied to the pattern constructor.|
| cache | [`cache.CfnCacheCluster`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_elasticache.CfnCacheCluster.html#attrconfigurationendpointport) | The Elasticache Memcached cluster used by the construct. |

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Attached to self referencing security group to grant access to cache
* Set Environment Variables

  * (default) CACHE_ENDPOINT
  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

### Amazon Elasticache Memcached Cluster

* Creates multi node, cross-az cluster by default

  * 2 cache nodes, type: cache.t3.medium
* Self referencing security group attached to cluster endpoint

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

import aws_cdk.aws_ec2
import aws_cdk.aws_elasticache
import aws_cdk.aws_lambda
import aws_cdk.core


class LambdaToElasticachememcached(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-elasticachememcached.LambdaToElasticachememcached",
):
    '''
    :summary: The LambdaToElasticachememcached class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cache_endpoint_environment_variable_name: typing.Optional[builtins.str] = None,
        cache_props: typing.Any = None,
        existing_cache: typing.Optional[aws_cdk.aws_elasticache.CfnCacheCluster] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        lambda_function_props: typing.Optional[typing.Union[aws_cdk.aws_lambda.FunctionProps, typing.Dict[str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[aws_cdk.aws_ec2.VpcProps, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param cache_endpoint_environment_variable_name: Optional Name for the Lambda function environment variable set to the cache endpoint. Default: - CACHE_ENDPOINT
        :param cache_props: Optional user provided props to override the default props for the Elasticache cache. Providing both this and ``existingCache`` will cause an error. If you provide this, you must provide the associated VPC in existingVpc. Default: - Default properties are used (core/lib/elasticacahe-defaults.ts)
        :param existing_cache: Existing instance of Elasticache Cluster object, providing both this and ``cacheProps`` will cause an error. Default: - none
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case). Default: - none
        :param lambda_function_props: Optional user provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param vpc_props: Properties to override default properties if deployVpc is true. Default: - DefaultIsolatedVpcProps() in vpc-defaults.ts

        :access: public
        :summary: Constructs a new instance of the LambdaToElasticachememcached class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(LambdaToElasticachememcached.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LambdaToElasticachememcachedProps(
            cache_endpoint_environment_variable_name=cache_endpoint_environment_variable_name,
            cache_props=cache_props,
            existing_cache=existing_cache,
            existing_lambda_obj=existing_lambda_obj,
            existing_vpc=existing_vpc,
            lambda_function_props=lambda_function_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cache")
    def cache(self) -> aws_cdk.aws_elasticache.CfnCacheCluster:
        return typing.cast(aws_cdk.aws_elasticache.CfnCacheCluster, jsii.get(self, "cache"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-lambda-elasticachememcached.LambdaToElasticachememcachedProps",
    jsii_struct_bases=[],
    name_mapping={
        "cache_endpoint_environment_variable_name": "cacheEndpointEnvironmentVariableName",
        "cache_props": "cacheProps",
        "existing_cache": "existingCache",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_vpc": "existingVpc",
        "lambda_function_props": "lambdaFunctionProps",
        "vpc_props": "vpcProps",
    },
)
class LambdaToElasticachememcachedProps:
    def __init__(
        self,
        *,
        cache_endpoint_environment_variable_name: typing.Optional[builtins.str] = None,
        cache_props: typing.Any = None,
        existing_cache: typing.Optional[aws_cdk.aws_elasticache.CfnCacheCluster] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        lambda_function_props: typing.Optional[typing.Union[aws_cdk.aws_lambda.FunctionProps, typing.Dict[str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[aws_cdk.aws_ec2.VpcProps, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cache_endpoint_environment_variable_name: Optional Name for the Lambda function environment variable set to the cache endpoint. Default: - CACHE_ENDPOINT
        :param cache_props: Optional user provided props to override the default props for the Elasticache cache. Providing both this and ``existingCache`` will cause an error. If you provide this, you must provide the associated VPC in existingVpc. Default: - Default properties are used (core/lib/elasticacahe-defaults.ts)
        :param existing_cache: Existing instance of Elasticache Cluster object, providing both this and ``cacheProps`` will cause an error. Default: - none
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case). Default: - none
        :param lambda_function_props: Optional user provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param vpc_props: Properties to override default properties if deployVpc is true. Default: - DefaultIsolatedVpcProps() in vpc-defaults.ts

        :summary: The properties for the LambdaToElasticachememcached class.
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        if isinstance(vpc_props, dict):
            vpc_props = aws_cdk.aws_ec2.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(LambdaToElasticachememcachedProps.__init__)
            check_type(argname="argument cache_endpoint_environment_variable_name", value=cache_endpoint_environment_variable_name, expected_type=type_hints["cache_endpoint_environment_variable_name"])
            check_type(argname="argument cache_props", value=cache_props, expected_type=type_hints["cache_props"])
            check_type(argname="argument existing_cache", value=existing_cache, expected_type=type_hints["existing_cache"])
            check_type(argname="argument existing_lambda_obj", value=existing_lambda_obj, expected_type=type_hints["existing_lambda_obj"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument lambda_function_props", value=lambda_function_props, expected_type=type_hints["lambda_function_props"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[str, typing.Any] = {}
        if cache_endpoint_environment_variable_name is not None:
            self._values["cache_endpoint_environment_variable_name"] = cache_endpoint_environment_variable_name
        if cache_props is not None:
            self._values["cache_props"] = cache_props
        if existing_cache is not None:
            self._values["existing_cache"] = existing_cache
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def cache_endpoint_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the Lambda function environment variable set to the cache endpoint.

        :default: - CACHE_ENDPOINT
        '''
        result = self._values.get("cache_endpoint_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_props(self) -> typing.Any:
        '''Optional user provided props to override the default props for the Elasticache cache.

        Providing both this and ``existingCache`` will cause an error.  If you provide this,
        you must provide the associated VPC in existingVpc.

        :default: - Default properties are used (core/lib/elasticacahe-defaults.ts)
        '''
        result = self._values.get("cache_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def existing_cache(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticache.CfnCacheCluster]:
        '''Existing instance of Elasticache Cluster object, providing both this and ``cacheProps`` will cause an error.

        :default: - none
        '''
        result = self._values.get("existing_cache")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticache.CfnCacheCluster], result)

    @builtins.property
    def existing_lambda_obj(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).

        :default: - none
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        '''Optional user provided props to override the default props for the Lambda function.

        :default: - Default properties are used.
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FunctionProps], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[aws_cdk.aws_ec2.VpcProps]:
        '''Properties to override default properties if deployVpc is true.

        :default: - DefaultIsolatedVpcProps() in vpc-defaults.ts
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaToElasticachememcachedProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToElasticachememcached",
    "LambdaToElasticachememcachedProps",
]

publication.publish()
