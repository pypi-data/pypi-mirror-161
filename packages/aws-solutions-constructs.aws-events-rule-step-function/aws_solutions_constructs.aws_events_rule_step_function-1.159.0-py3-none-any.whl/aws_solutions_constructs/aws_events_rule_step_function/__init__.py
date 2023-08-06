'''
# aws-events-rule-step-function module

<!--BEGIN STABILITY BANNER-->---


![Stability: Deprecated](https://img.shields.io/badge/STABILITY-DEPRECATED-red?style=for-the-badge)

> Some of our early constructs don’t meet the naming standards that evolved for the library. We are releasing completely feature compatible versions with corrected names. The underlying implementation code is the same regardless of whether you deploy the construct using the old or new name. We will support both names for all 1.x releases, but in 2.x we will only publish the correctly named constructs. This construct is being replaced by the functionally identical aws-eventbridge-stepfunctions.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_events_rule_step_function`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-events-rule-step-function`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.eventsrulestepfunction`|

## Overview

This AWS Solutions Construct implements an AWS Events rule and an AWS Step function.

Here is a minimal deployable pattern definition:

Typescript

```python
// aws-events-rule-step-function has been deprecated for CDK V2 in favor of aws-eventbridge-stepfunctions.
// This sample uses the CDK V1 syntax
import * as cdk from '@aws-cdk/core';
import * as events from '@aws-cdk/aws-events';
import * as stepfunctions from '@aws-cdk/aws-stepfunctions';
import { EventsRuleToStepFunction, EventsRuleToStepFunctionProps } from '@aws-solutions-constructs/aws-events-rule-step-function';

const startState = new stepfunctions.Pass(this, 'StartState');

const constructProps: EventsRuleToStepFunctionProps = {
  stateMachineProps: {
    definition: startState
  },
  eventRuleProps: {
    schedule: events.Schedule.rate(cdk.Duration.minutes(5))
  }
};

new EventsRuleToStepFunction(this, 'test-events-rules-step-function-stack', constructProps);
```

Python

```Python
# aws-events-rule-step-function has been deprecated for CDK V2 in favor of aws-eventbridge-stepfunctions.
# This sample uses the CDK V1 syntax
from aws_solutions_constructs.aws_events_rule_step_function import EventsRuleToStepFunction, EventsRuleToStepFunctionProps
from aws_cdk import (
    aws_stepfunctions as stepfunctions,
    aws_events as events,
    core
)

startState = stepfunctions.Pass(self, 'StartState')

EventsRuleToStepFunction(self, 'test',
                            state_machine_props=stepfunctions.StateMachineProps(
                                definition=startState
                            ),
                            event_rule_props=events.RuleProps(
                                schedule=events.Schedule.rate(
                                    core.Duration.minutes(5))
                            ))

```

Java

```java
// aws-events-rule-step-function has been deprecated for CDK V2 in favor of aws-eventbridge-stepfunctions.
// This sample uses the CDK V1 syntax
import software.constructs.Construct;

import software.amazon.awscdk.core.*;
import software.amazon.awscdk.services.events.*;
import software.amazon.awscdk.services.stepfunctions.*;
import software.amazon.awsconstructs.services.eventsrulestepfunction.*;

final Pass startState = new Pass(this, "StartState");

new EventsRuleToStepFunction(this,
        "test-eventbridge-stepfunctions-stack",
        new EventsRuleToStepFunctionProps.Builder()
                .stateMachineProps(new StateMachineProps.Builder()
                        .definition(startState)
                        .build())
                .eventRuleProps(new RuleProps.Builder()
                        .schedule(Schedule.rate(Duration.minutes(5)))
                        .build())
                .build());
```

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|stateMachineProps|[`sfn.StateMachineProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-stepfunctions.StateMachineProps.html)|Optional user provided props to override the default props for sfn.StateMachine|
|existingEventBusInterface?|[`events.IEventBus`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-events.IEventBus.html)| Optional user-provided custom EventBus for construct to use. Providing both this and `eventBusProps` results an error.|
|eventBusProps?|[`events.EventBusProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-events.EventBusProps.html)|Optional user-provided properties to override the default properties when creating a custom EventBus. Setting this value to `{}` will create a custom EventBus using all default properties. If neither this nor `existingEventBusInterface` is provided the construct will use the `default` EventBus. Providing both this and `existingEventBusInterface` results an error.|
|eventRuleProps|[`events.RuleProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-events.RuleProps.html)|User provided eventRuleProps to override the defaults|
|createCloudWatchAlarms|`boolean`|Whether to create recommended CloudWatch alarms|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|eventBus?|[`events.IEventBus`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-events.IEventBus.html)|Returns the instance of events.IEventBus used by the construct|
|eventsRule|[`events.Rule`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-events.Rule.html)|Returns an instance of events.Rule created by the construct|
|stateMachine|[`sfn.StateMachine`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-stepfunctions.StateMachine.html)|Returns an instance of sfn.StateMachine created by the construct|
|stateMachineLogGroup|[`logs.ILogGroup`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.ILogGroup.html)|Returns an instance of the ILogGroup created by the construct for StateMachine|
|cloudwatchAlarms?|[`cloudwatch.Alarm[]`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudwatch.Alarm.html)|Returns a list of cloudwatch.Alarm created by the construct|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon CloudWatch Events Rule

* Grant least privilege permissions to CloudWatch Events to trigger the Lambda Function

### AWS Step Function

* Enable CloudWatch logging for API Gateway
* Deploy best practices CloudWatch Alarms for the Step Function

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

import aws_cdk.aws_cloudwatch
import aws_cdk.aws_events
import aws_cdk.aws_logs
import aws_cdk.aws_stepfunctions
import aws_cdk.core


class EventsRuleToStepFunction(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-events-rule-step-function.EventsRuleToStepFunction",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        event_rule_props: typing.Union[aws_cdk.aws_events.RuleProps, typing.Dict[str, typing.Any]],
        state_machine_props: typing.Union[aws_cdk.aws_stepfunctions.StateMachineProps, typing.Dict[str, typing.Any]],
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        event_bus_props: typing.Optional[typing.Union[aws_cdk.aws_events.EventBusProps, typing.Dict[str, typing.Any]]] = None,
        existing_event_bus_interface: typing.Optional[aws_cdk.aws_events.IEventBus] = None,
        log_group_props: typing.Optional[typing.Union[aws_cdk.aws_logs.LogGroupProps, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param event_rule_props: User provided eventRuleProps to override the defaults. Default: - None
        :param state_machine_props: User provided StateMachineProps to override the defaults. Default: - None
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param event_bus_props: A new custom EventBus is created with provided props. Default: - None
        :param existing_event_bus_interface: Existing instance of a custom EventBus. Default: - None
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used

        :access: public
        :summary: Constructs a new instance of the EventsRuleToStepFunction class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(EventsRuleToStepFunction.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EventsRuleToStepFunctionProps(
            event_rule_props=event_rule_props,
            state_machine_props=state_machine_props,
            create_cloud_watch_alarms=create_cloud_watch_alarms,
            event_bus_props=event_bus_props,
            existing_event_bus_interface=existing_event_bus_interface,
            log_group_props=log_group_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventsRule")
    def events_rule(self) -> aws_cdk.aws_events.Rule:
        return typing.cast(aws_cdk.aws_events.Rule, jsii.get(self, "eventsRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> aws_cdk.aws_stepfunctions.StateMachine:
        return typing.cast(aws_cdk.aws_stepfunctions.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachineLogGroup")
    def state_machine_log_group(self) -> aws_cdk.aws_logs.ILogGroup:
        return typing.cast(aws_cdk.aws_logs.ILogGroup, jsii.get(self, "stateMachineLogGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchAlarms")
    def cloudwatch_alarms(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]]:
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]], jsii.get(self, "cloudwatchAlarms"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventBus")
    def event_bus(self) -> typing.Optional[aws_cdk.aws_events.IEventBus]:
        return typing.cast(typing.Optional[aws_cdk.aws_events.IEventBus], jsii.get(self, "eventBus"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-events-rule-step-function.EventsRuleToStepFunctionProps",
    jsii_struct_bases=[],
    name_mapping={
        "event_rule_props": "eventRuleProps",
        "state_machine_props": "stateMachineProps",
        "create_cloud_watch_alarms": "createCloudWatchAlarms",
        "event_bus_props": "eventBusProps",
        "existing_event_bus_interface": "existingEventBusInterface",
        "log_group_props": "logGroupProps",
    },
)
class EventsRuleToStepFunctionProps:
    def __init__(
        self,
        *,
        event_rule_props: typing.Union[aws_cdk.aws_events.RuleProps, typing.Dict[str, typing.Any]],
        state_machine_props: typing.Union[aws_cdk.aws_stepfunctions.StateMachineProps, typing.Dict[str, typing.Any]],
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        event_bus_props: typing.Optional[typing.Union[aws_cdk.aws_events.EventBusProps, typing.Dict[str, typing.Any]]] = None,
        existing_event_bus_interface: typing.Optional[aws_cdk.aws_events.IEventBus] = None,
        log_group_props: typing.Optional[typing.Union[aws_cdk.aws_logs.LogGroupProps, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param event_rule_props: User provided eventRuleProps to override the defaults. Default: - None
        :param state_machine_props: User provided StateMachineProps to override the defaults. Default: - None
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param event_bus_props: A new custom EventBus is created with provided props. Default: - None
        :param existing_event_bus_interface: Existing instance of a custom EventBus. Default: - None
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used

        :summary: The properties for the EventsRuleToStepFunction Construct
        '''
        if isinstance(event_rule_props, dict):
            event_rule_props = aws_cdk.aws_events.RuleProps(**event_rule_props)
        if isinstance(state_machine_props, dict):
            state_machine_props = aws_cdk.aws_stepfunctions.StateMachineProps(**state_machine_props)
        if isinstance(event_bus_props, dict):
            event_bus_props = aws_cdk.aws_events.EventBusProps(**event_bus_props)
        if isinstance(log_group_props, dict):
            log_group_props = aws_cdk.aws_logs.LogGroupProps(**log_group_props)
        if __debug__:
            type_hints = typing.get_type_hints(EventsRuleToStepFunctionProps.__init__)
            check_type(argname="argument event_rule_props", value=event_rule_props, expected_type=type_hints["event_rule_props"])
            check_type(argname="argument state_machine_props", value=state_machine_props, expected_type=type_hints["state_machine_props"])
            check_type(argname="argument create_cloud_watch_alarms", value=create_cloud_watch_alarms, expected_type=type_hints["create_cloud_watch_alarms"])
            check_type(argname="argument event_bus_props", value=event_bus_props, expected_type=type_hints["event_bus_props"])
            check_type(argname="argument existing_event_bus_interface", value=existing_event_bus_interface, expected_type=type_hints["existing_event_bus_interface"])
            check_type(argname="argument log_group_props", value=log_group_props, expected_type=type_hints["log_group_props"])
        self._values: typing.Dict[str, typing.Any] = {
            "event_rule_props": event_rule_props,
            "state_machine_props": state_machine_props,
        }
        if create_cloud_watch_alarms is not None:
            self._values["create_cloud_watch_alarms"] = create_cloud_watch_alarms
        if event_bus_props is not None:
            self._values["event_bus_props"] = event_bus_props
        if existing_event_bus_interface is not None:
            self._values["existing_event_bus_interface"] = existing_event_bus_interface
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props

    @builtins.property
    def event_rule_props(self) -> aws_cdk.aws_events.RuleProps:
        '''User provided eventRuleProps to override the defaults.

        :default: - None
        '''
        result = self._values.get("event_rule_props")
        assert result is not None, "Required property 'event_rule_props' is missing"
        return typing.cast(aws_cdk.aws_events.RuleProps, result)

    @builtins.property
    def state_machine_props(self) -> aws_cdk.aws_stepfunctions.StateMachineProps:
        '''User provided StateMachineProps to override the defaults.

        :default: - None
        '''
        result = self._values.get("state_machine_props")
        assert result is not None, "Required property 'state_machine_props' is missing"
        return typing.cast(aws_cdk.aws_stepfunctions.StateMachineProps, result)

    @builtins.property
    def create_cloud_watch_alarms(self) -> typing.Optional[builtins.bool]:
        '''Whether to create recommended CloudWatch alarms.

        :default: - Alarms are created
        '''
        result = self._values.get("create_cloud_watch_alarms")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_bus_props(self) -> typing.Optional[aws_cdk.aws_events.EventBusProps]:
        '''A new custom EventBus is created with provided props.

        :default: - None
        '''
        result = self._values.get("event_bus_props")
        return typing.cast(typing.Optional[aws_cdk.aws_events.EventBusProps], result)

    @builtins.property
    def existing_event_bus_interface(
        self,
    ) -> typing.Optional[aws_cdk.aws_events.IEventBus]:
        '''Existing instance of a custom EventBus.

        :default: - None
        '''
        result = self._values.get("existing_event_bus_interface")
        return typing.cast(typing.Optional[aws_cdk.aws_events.IEventBus], result)

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
        return "EventsRuleToStepFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EventsRuleToStepFunction",
    "EventsRuleToStepFunctionProps",
]

publication.publish()
