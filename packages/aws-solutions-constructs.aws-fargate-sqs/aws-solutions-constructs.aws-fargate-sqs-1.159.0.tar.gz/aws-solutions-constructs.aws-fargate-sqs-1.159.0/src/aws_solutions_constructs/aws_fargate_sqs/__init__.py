'''
# aws-fargate-sqs module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_fargate_sqs`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-fargate-sqs`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.fargatesqs`|

## Overview

This AWS Solutions Construct implements an AWS Fargate service that can write to an Amazon SQS queue

Here is a minimal deployable pattern definition:

Typescript

```python
import { Construct } from 'constructs';
import { Stack, StackProps } from 'aws-cdk-lib';
import { FargateToSqs, FargateToSqsProps } from '@aws-solutions-constructs/aws-fargate-sqs';

const constructProps: FargateToSqsProps = {
    publicApi: true,
    ecrRepositoryArn: "arn:aws:ecr:us-east-1:123456789012:repository/your-ecr-repo"
};

new FargateToSqs(this, 'test-construct', constructProps);
```

Python

```python
from aws_solutions_constructs.aws_fargate_sqs import FargateToSqs, FargateToSqsProps
from aws_cdk import (
    Stack
)
from constructs import Construct

FargateToSqs(self, 'test_construct',
            public_api=True,
            ecr_repository_arn="arn:aws:ecr:us-east-1:123456789012:repository/your-ecr-repo")
```

Java

```java
import software.constructs.Construct;

import software.amazon.awscdk.Stack;
import software.amazon.awscdk.StackProps;
import software.amazon.awsconstructs.services.fargatesqs.*;

new FargateToSqs(this, "test_construct", new FargateToSqsProps.Builder()
        .publicApi(true)
        .ecrRepositoryArn("arn:aws:ecr:us-east-1:123456789012:repository/your-ecr-repo")
        .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| publicApi | boolean | Whether the construct is deploying a private or public API. This has implications for the VPC. |
| vpcProps? | [ec2.VpcProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.VpcProps.html) | Optional custom properties for a VPC the construct will create. This VPC will be used by any Private Hosted Zone the construct creates (that's why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing both this and existingVpc is an error. |
| existingVpc? | [ec2.IVpc](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html) | An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing load balancer and/or existing Private Hosted Zone, those constructs must exist in this VPC. |
| clusterProps? | [ecs.ClusterProps](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.ClusterProps.html) | Optional properties to create a new ECS cluster. To provide an existing cluster, use the cluster attribute of fargateServiceProps. |
| ecrRepositoryArn? | string | The arn of an ECR Repository containing the image to use to generate the containers. Either this or the image property of containerDefinitionProps must be provided. format: arn:aws:ecr:*region*:*account number*:repository/*Repository Name* |
| ecrImageVersion? | string | The version of the image to use from the repository. Defaults to 'Latest' |
| containerDefinitionProps? | [ecs.ContainerDefinitionProps | any](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.ContainerDefinitionProps.html) | Optional props to define the container created for the Fargate Service (defaults found in fargate-defaults.ts) |
| fargateTaskDefinitionProps? | [ecs.FargateTaskDefinitionProps | any](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.FargateTaskDefinitionProps.html) | Optional props to define the Fargate Task Definition for this construct  (defaults found in fargate-defaults.ts) |
| fargateServiceProps? | [ecs.FargateServiceProps | any](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.FargateServiceProps.html) | Optional values to override default Fargate Task definition properties (fargate-defaults.ts). The construct will default to launching the service is the most isolated subnets available (precedence: Isolated, Private and Public). Override those and other defaults here. |
| existingFargateServiceObject? | [ecs.FargateService](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.FargateService.html) | A Fargate Service already instantiated (probably by another Solutions Construct). If this is specified, then no props defining a new service can be provided, including: ecrImageVersion, containerDefinitionProps, fargateTaskDefinitionProps, ecrRepositoryArn, fargateServiceProps, clusterProps |
| existingContainerDefinitionObject? | [ecs.ContainerDefinition](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.ContainerDefinition.html) | A container definition already instantiated as part of a Fargate service. This must be the container in the existingFargateServiceObject |
|existingQueueObj?|[sqs.Queue](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|An optional, existing SQS queue to be used instead of the default queue. Providing both this and queueProps will cause an error.|
|queueProps?|[sqs.QueueProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.QueueProps.html)|Optional user-provided properties to override the default properties for the SQS queue.|
|deployDeadLetterQueue?|boolean|Whether to create a secondary queue to be used as a dead letter queue. Defaults to `true`.|
|deadLetterQueueProps?|[sqs.QueueProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.QueueProps.html)|Optional user-provided props to override the default props for the dead letter queue. Only used if the `deployDeadLetterQueue` property is set to true.|
|maxReceiveCount?|integer|The number of times a message can be unsuccessfully dequeued before being moved to the dead letter queue. Defaults to `15`.|
|queueUrlEnvironmentVariableName?|string|Optional Name for the container environment variable set to the URL of the queue. Default: SQS_QUEUE_URL |
|queueArnEnvironmentVariableName?|string|Optional Name for the container environment variable set to the arn of the queue. Default: SQS_QUEUE_ARN |
|queuePermissions?|`string[]`|Optional queue permissions to grant to the Fargate service. One or more of the following may be specified: `Read`,`Write`. Default is `Write`|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| vpc | [ec2.IVpc](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html) | The VPC used by the construct (whether created by the construct or provided by the client) |
| service | [ecs.FargateService](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.FargateService.html) | The AWS Fargate service used by this construct (whether created by this construct or passed to this construct at initialization) |
| container | [ecs.ContainerDefinition](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.ContainerDefinition.html) | The container associated with the AWS Fargate service in the service property. |
|sqsQueue|[sqs.Queue](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|Returns an instance of the SQS queue created by the pattern. |
|deadLetterQueue?|[sqs.Queue](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|Returns an instance of the dead letter queue created by the pattern, if one is deployed.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Fargate Service

* Sets up an AWS Fargate service

  * Uses the existing service if provided
  * Creates a new service if none provided.

    * Service will run in isolated subnets if available, then private subnets if available and finally public subnets
  * Adds environment variables to the container with the name of the SQS queue
  * Add permissions to the container IAM role allowing it to publish to the SQS queue

### Amazon SQS Queue

* Sets up an Amazon SQS queue

  * Uses an existing queue if one is provided, otherwise creates a new one
* Adds an Interface Endpoint to the VPC for SQS (the service by default runs in Isolated or Private subnets)

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
import aws_cdk.aws_ecs
import aws_cdk.aws_sqs
import aws_cdk.core


class FargateToSqs(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-fargate-sqs.FargateToSqs",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        public_api: builtins.bool,
        cluster_props: typing.Optional[typing.Union[aws_cdk.aws_ecs.ClusterProps, typing.Dict[str, typing.Any]]] = None,
        container_definition_props: typing.Any = None,
        dead_letter_queue_props: typing.Optional[typing.Union[aws_cdk.aws_sqs.QueueProps, typing.Dict[str, typing.Any]]] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        ecr_image_version: typing.Optional[builtins.str] = None,
        ecr_repository_arn: typing.Optional[builtins.str] = None,
        existing_container_definition_object: typing.Optional[aws_cdk.aws_ecs.ContainerDefinition] = None,
        existing_fargate_service_object: typing.Optional[aws_cdk.aws_ecs.FargateService] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        fargate_service_props: typing.Any = None,
        fargate_task_definition_props: typing.Any = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_arn_environment_variable_name: typing.Optional[builtins.str] = None,
        queue_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
        queue_props: typing.Optional[typing.Union[aws_cdk.aws_sqs.QueueProps, typing.Dict[str, typing.Any]]] = None,
        queue_url_environment_variable_name: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[typing.Union[aws_cdk.aws_ec2.VpcProps, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param public_api: Whether the construct is deploying a private or public API. This has implications for the VPC deployed by this construct. Default: - none
        :param cluster_props: Optional properties to create a new ECS cluster.
        :param container_definition_props: -
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param ecr_image_version: The version of the image to use from the repository. Default: - 'latest'
        :param ecr_repository_arn: The arn of an ECR Repository containing the image to use to generate the containers. format: arn:aws:ecr:[region]:[account number]:repository/[Repository Name]
        :param existing_container_definition_object: -
        :param existing_fargate_service_object: A Fargate Service already instantiated (probably by another Solutions Construct). If this is specified, then no props defining a new service can be provided, including: existingImageObject, ecrImageVersion, containerDefintionProps, fargateTaskDefinitionProps, ecrRepositoryArn, fargateServiceProps, clusterProps, existingClusterInterface. If this value is provided, then existingContainerDefinitionObject must be provided as well. Default: - none
        :param existing_queue_obj: Existing instance of SQS queue object, Providing both this and queueProps will cause an error. Default: - Default props are used
        :param existing_vpc: An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing Fargate service, this value must be the VPC where the service is running. An SQS Interface endpoint will be added to this VPC. Default: - none
        :param fargate_service_props: Optional values to override default Fargate Task definition properties (fargate-defaults.ts). The construct will default to launching the service is the most isolated subnets available (precedence: Isolated, Private and Public). Override those and other defaults here. defaults - fargate-defaults.ts
        :param fargate_task_definition_props: -
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param queue_arn_environment_variable_name: Optional Name for the container environment variable set to the arn of the queue. Default: - SQS_QUEUE_ARN
        :param queue_permissions: Optional queue permissions to grant to the Fargate service. One or more of the following may be specified: ``Read``,``Write``. Default is ``Write`` Default: - Write
        :param queue_props: Optional user-provided props to override the default props for the SQS queue. Default: - Default props are used
        :param queue_url_environment_variable_name: Optional Name for the container environment variable set to the URL of the queue. Default: - SQS_QUEUE_URL
        :param vpc_props: Optional custom properties for a VPC the construct will create. This VPC will be used by the new Fargate service the construct creates (that's why targetGroupProps can't include a VPC). Providing both this and existingVpc is an error. An SQS Interface endpoint will be included in this VPC. Default: - none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(FargateToSqs.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FargateToSqsProps(
            public_api=public_api,
            cluster_props=cluster_props,
            container_definition_props=container_definition_props,
            dead_letter_queue_props=dead_letter_queue_props,
            deploy_dead_letter_queue=deploy_dead_letter_queue,
            ecr_image_version=ecr_image_version,
            ecr_repository_arn=ecr_repository_arn,
            existing_container_definition_object=existing_container_definition_object,
            existing_fargate_service_object=existing_fargate_service_object,
            existing_queue_obj=existing_queue_obj,
            existing_vpc=existing_vpc,
            fargate_service_props=fargate_service_props,
            fargate_task_definition_props=fargate_task_definition_props,
            max_receive_count=max_receive_count,
            queue_arn_environment_variable_name=queue_arn_environment_variable_name,
            queue_permissions=queue_permissions,
            queue_props=queue_props,
            queue_url_environment_variable_name=queue_url_environment_variable_name,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="container")
    def container(self) -> aws_cdk.aws_ecs.ContainerDefinition:
        return typing.cast(aws_cdk.aws_ecs.ContainerDefinition, jsii.get(self, "container"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> aws_cdk.aws_ecs.FargateService:
        return typing.cast(aws_cdk.aws_ecs.FargateService, jsii.get(self, "service"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsQueue")
    def sqs_queue(self) -> aws_cdk.aws_sqs.Queue:
        return typing.cast(aws_cdk.aws_sqs.Queue, jsii.get(self, "sqsQueue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deadLetterQueue")
    def dead_letter_queue(self) -> typing.Optional[aws_cdk.aws_sqs.DeadLetterQueue]:
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.DeadLetterQueue], jsii.get(self, "deadLetterQueue"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-fargate-sqs.FargateToSqsProps",
    jsii_struct_bases=[],
    name_mapping={
        "public_api": "publicApi",
        "cluster_props": "clusterProps",
        "container_definition_props": "containerDefinitionProps",
        "dead_letter_queue_props": "deadLetterQueueProps",
        "deploy_dead_letter_queue": "deployDeadLetterQueue",
        "ecr_image_version": "ecrImageVersion",
        "ecr_repository_arn": "ecrRepositoryArn",
        "existing_container_definition_object": "existingContainerDefinitionObject",
        "existing_fargate_service_object": "existingFargateServiceObject",
        "existing_queue_obj": "existingQueueObj",
        "existing_vpc": "existingVpc",
        "fargate_service_props": "fargateServiceProps",
        "fargate_task_definition_props": "fargateTaskDefinitionProps",
        "max_receive_count": "maxReceiveCount",
        "queue_arn_environment_variable_name": "queueArnEnvironmentVariableName",
        "queue_permissions": "queuePermissions",
        "queue_props": "queueProps",
        "queue_url_environment_variable_name": "queueUrlEnvironmentVariableName",
        "vpc_props": "vpcProps",
    },
)
class FargateToSqsProps:
    def __init__(
        self,
        *,
        public_api: builtins.bool,
        cluster_props: typing.Optional[typing.Union[aws_cdk.aws_ecs.ClusterProps, typing.Dict[str, typing.Any]]] = None,
        container_definition_props: typing.Any = None,
        dead_letter_queue_props: typing.Optional[typing.Union[aws_cdk.aws_sqs.QueueProps, typing.Dict[str, typing.Any]]] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        ecr_image_version: typing.Optional[builtins.str] = None,
        ecr_repository_arn: typing.Optional[builtins.str] = None,
        existing_container_definition_object: typing.Optional[aws_cdk.aws_ecs.ContainerDefinition] = None,
        existing_fargate_service_object: typing.Optional[aws_cdk.aws_ecs.FargateService] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        fargate_service_props: typing.Any = None,
        fargate_task_definition_props: typing.Any = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_arn_environment_variable_name: typing.Optional[builtins.str] = None,
        queue_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
        queue_props: typing.Optional[typing.Union[aws_cdk.aws_sqs.QueueProps, typing.Dict[str, typing.Any]]] = None,
        queue_url_environment_variable_name: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[typing.Union[aws_cdk.aws_ec2.VpcProps, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param public_api: Whether the construct is deploying a private or public API. This has implications for the VPC deployed by this construct. Default: - none
        :param cluster_props: Optional properties to create a new ECS cluster.
        :param container_definition_props: -
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param ecr_image_version: The version of the image to use from the repository. Default: - 'latest'
        :param ecr_repository_arn: The arn of an ECR Repository containing the image to use to generate the containers. format: arn:aws:ecr:[region]:[account number]:repository/[Repository Name]
        :param existing_container_definition_object: -
        :param existing_fargate_service_object: A Fargate Service already instantiated (probably by another Solutions Construct). If this is specified, then no props defining a new service can be provided, including: existingImageObject, ecrImageVersion, containerDefintionProps, fargateTaskDefinitionProps, ecrRepositoryArn, fargateServiceProps, clusterProps, existingClusterInterface. If this value is provided, then existingContainerDefinitionObject must be provided as well. Default: - none
        :param existing_queue_obj: Existing instance of SQS queue object, Providing both this and queueProps will cause an error. Default: - Default props are used
        :param existing_vpc: An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing Fargate service, this value must be the VPC where the service is running. An SQS Interface endpoint will be added to this VPC. Default: - none
        :param fargate_service_props: Optional values to override default Fargate Task definition properties (fargate-defaults.ts). The construct will default to launching the service is the most isolated subnets available (precedence: Isolated, Private and Public). Override those and other defaults here. defaults - fargate-defaults.ts
        :param fargate_task_definition_props: -
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param queue_arn_environment_variable_name: Optional Name for the container environment variable set to the arn of the queue. Default: - SQS_QUEUE_ARN
        :param queue_permissions: Optional queue permissions to grant to the Fargate service. One or more of the following may be specified: ``Read``,``Write``. Default is ``Write`` Default: - Write
        :param queue_props: Optional user-provided props to override the default props for the SQS queue. Default: - Default props are used
        :param queue_url_environment_variable_name: Optional Name for the container environment variable set to the URL of the queue. Default: - SQS_QUEUE_URL
        :param vpc_props: Optional custom properties for a VPC the construct will create. This VPC will be used by the new Fargate service the construct creates (that's why targetGroupProps can't include a VPC). Providing both this and existingVpc is an error. An SQS Interface endpoint will be included in this VPC. Default: - none
        '''
        if isinstance(cluster_props, dict):
            cluster_props = aws_cdk.aws_ecs.ClusterProps(**cluster_props)
        if isinstance(dead_letter_queue_props, dict):
            dead_letter_queue_props = aws_cdk.aws_sqs.QueueProps(**dead_letter_queue_props)
        if isinstance(queue_props, dict):
            queue_props = aws_cdk.aws_sqs.QueueProps(**queue_props)
        if isinstance(vpc_props, dict):
            vpc_props = aws_cdk.aws_ec2.VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(FargateToSqsProps.__init__)
            check_type(argname="argument public_api", value=public_api, expected_type=type_hints["public_api"])
            check_type(argname="argument cluster_props", value=cluster_props, expected_type=type_hints["cluster_props"])
            check_type(argname="argument container_definition_props", value=container_definition_props, expected_type=type_hints["container_definition_props"])
            check_type(argname="argument dead_letter_queue_props", value=dead_letter_queue_props, expected_type=type_hints["dead_letter_queue_props"])
            check_type(argname="argument deploy_dead_letter_queue", value=deploy_dead_letter_queue, expected_type=type_hints["deploy_dead_letter_queue"])
            check_type(argname="argument ecr_image_version", value=ecr_image_version, expected_type=type_hints["ecr_image_version"])
            check_type(argname="argument ecr_repository_arn", value=ecr_repository_arn, expected_type=type_hints["ecr_repository_arn"])
            check_type(argname="argument existing_container_definition_object", value=existing_container_definition_object, expected_type=type_hints["existing_container_definition_object"])
            check_type(argname="argument existing_fargate_service_object", value=existing_fargate_service_object, expected_type=type_hints["existing_fargate_service_object"])
            check_type(argname="argument existing_queue_obj", value=existing_queue_obj, expected_type=type_hints["existing_queue_obj"])
            check_type(argname="argument existing_vpc", value=existing_vpc, expected_type=type_hints["existing_vpc"])
            check_type(argname="argument fargate_service_props", value=fargate_service_props, expected_type=type_hints["fargate_service_props"])
            check_type(argname="argument fargate_task_definition_props", value=fargate_task_definition_props, expected_type=type_hints["fargate_task_definition_props"])
            check_type(argname="argument max_receive_count", value=max_receive_count, expected_type=type_hints["max_receive_count"])
            check_type(argname="argument queue_arn_environment_variable_name", value=queue_arn_environment_variable_name, expected_type=type_hints["queue_arn_environment_variable_name"])
            check_type(argname="argument queue_permissions", value=queue_permissions, expected_type=type_hints["queue_permissions"])
            check_type(argname="argument queue_props", value=queue_props, expected_type=type_hints["queue_props"])
            check_type(argname="argument queue_url_environment_variable_name", value=queue_url_environment_variable_name, expected_type=type_hints["queue_url_environment_variable_name"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[str, typing.Any] = {
            "public_api": public_api,
        }
        if cluster_props is not None:
            self._values["cluster_props"] = cluster_props
        if container_definition_props is not None:
            self._values["container_definition_props"] = container_definition_props
        if dead_letter_queue_props is not None:
            self._values["dead_letter_queue_props"] = dead_letter_queue_props
        if deploy_dead_letter_queue is not None:
            self._values["deploy_dead_letter_queue"] = deploy_dead_letter_queue
        if ecr_image_version is not None:
            self._values["ecr_image_version"] = ecr_image_version
        if ecr_repository_arn is not None:
            self._values["ecr_repository_arn"] = ecr_repository_arn
        if existing_container_definition_object is not None:
            self._values["existing_container_definition_object"] = existing_container_definition_object
        if existing_fargate_service_object is not None:
            self._values["existing_fargate_service_object"] = existing_fargate_service_object
        if existing_queue_obj is not None:
            self._values["existing_queue_obj"] = existing_queue_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if fargate_service_props is not None:
            self._values["fargate_service_props"] = fargate_service_props
        if fargate_task_definition_props is not None:
            self._values["fargate_task_definition_props"] = fargate_task_definition_props
        if max_receive_count is not None:
            self._values["max_receive_count"] = max_receive_count
        if queue_arn_environment_variable_name is not None:
            self._values["queue_arn_environment_variable_name"] = queue_arn_environment_variable_name
        if queue_permissions is not None:
            self._values["queue_permissions"] = queue_permissions
        if queue_props is not None:
            self._values["queue_props"] = queue_props
        if queue_url_environment_variable_name is not None:
            self._values["queue_url_environment_variable_name"] = queue_url_environment_variable_name
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def public_api(self) -> builtins.bool:
        '''Whether the construct is deploying a private or public API.

        This has implications for the VPC deployed
        by this construct.

        :default: - none
        '''
        result = self._values.get("public_api")
        assert result is not None, "Required property 'public_api' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def cluster_props(self) -> typing.Optional[aws_cdk.aws_ecs.ClusterProps]:
        '''Optional properties to create a new ECS cluster.'''
        result = self._values.get("cluster_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ClusterProps], result)

    @builtins.property
    def container_definition_props(self) -> typing.Any:
        result = self._values.get("container_definition_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def dead_letter_queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user provided properties for the dead letter queue.

        :default: - Default props are used
        '''
        result = self._values.get("dead_letter_queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def deploy_dead_letter_queue(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a secondary queue to be used as a dead letter queue.

        :default: - true.
        '''
        result = self._values.get("deploy_dead_letter_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ecr_image_version(self) -> typing.Optional[builtins.str]:
        '''The version of the image to use from the repository.

        :default: - 'latest'
        '''
        result = self._values.get("ecr_image_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecr_repository_arn(self) -> typing.Optional[builtins.str]:
        '''The arn of an ECR Repository containing the image to use to generate the containers.

        format:
        arn:aws:ecr:[region]:[account number]:repository/[Repository Name]
        '''
        result = self._values.get("ecr_repository_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existing_container_definition_object(
        self,
    ) -> typing.Optional[aws_cdk.aws_ecs.ContainerDefinition]:
        result = self._values.get("existing_container_definition_object")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ContainerDefinition], result)

    @builtins.property
    def existing_fargate_service_object(
        self,
    ) -> typing.Optional[aws_cdk.aws_ecs.FargateService]:
        '''A Fargate Service already instantiated (probably by another Solutions Construct).

        If
        this is specified, then no props defining a new service can be provided, including:
        existingImageObject, ecrImageVersion, containerDefintionProps, fargateTaskDefinitionProps,
        ecrRepositoryArn, fargateServiceProps, clusterProps, existingClusterInterface. If this value
        is provided, then existingContainerDefinitionObject must be provided as well.

        :default: - none
        '''
        result = self._values.get("existing_fargate_service_object")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.FargateService], result)

    @builtins.property
    def existing_queue_obj(self) -> typing.Optional[aws_cdk.aws_sqs.Queue]:
        '''Existing instance of SQS queue object, Providing both this and queueProps will cause an error.

        :default: - Default props are used
        '''
        result = self._values.get("existing_queue_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.Queue], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC in which to deploy the construct.

        Providing both this and
        vpcProps is an error. If the client provides an existing Fargate service,
        this value must be the VPC where the service is running. An SQS Interface
        endpoint will be added to this VPC.

        :default: - none
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def fargate_service_props(self) -> typing.Any:
        '''Optional values to override default Fargate Task definition properties (fargate-defaults.ts). The construct will default to launching the service is the most isolated subnets available (precedence: Isolated, Private and Public). Override those and other defaults here.

        defaults - fargate-defaults.ts
        '''
        result = self._values.get("fargate_service_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def fargate_task_definition_props(self) -> typing.Any:
        result = self._values.get("fargate_task_definition_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue.

        :default: - required field if deployDeadLetterQueue=true.
        '''
        result = self._values.get("max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def queue_arn_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the container environment variable set to the arn of the queue.

        :default: - SQS_QUEUE_ARN
        '''
        result = self._values.get("queue_arn_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_permissions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Optional queue permissions to grant to the Fargate service.

        One or more of the following may be specified: ``Read``,``Write``. Default is ``Write``

        :default: - Write
        '''
        result = self._values.get("queue_permissions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user-provided props to override the default props for the SQS queue.

        :default: - Default props are used
        '''
        result = self._values.get("queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def queue_url_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the container environment variable set to the URL of the queue.

        :default: - SQS_QUEUE_URL
        '''
        result = self._values.get("queue_url_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[aws_cdk.aws_ec2.VpcProps]:
        '''Optional custom properties for a VPC the construct will create.

        This VPC will
        be used by the new Fargate service the construct creates (that's
        why targetGroupProps can't include a VPC). Providing
        both this and existingVpc is an error. An SQS Interface
        endpoint will be included in this VPC.

        :default: - none
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateToSqsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "FargateToSqs",
    "FargateToSqsProps",
]

publication.publish()
