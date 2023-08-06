'''
# @dontirun/state-machine-semaphore

[![npm version](https://img.shields.io/npm/v/donti/state-machine-semaphore.svg)](https://www.npmjs.com/package/@donti%2Fstate-machine-semaphore)
[![PyPI version](https://img.shields.io/pypi/v/state-machine-semaphore.svg)](https://pypi.org/project/state-machine-semaphore)
[![NuGet version](https://img.shields.io/nuget/v/Dontirun.StateMachineSemaphore)](https://www.nuget.org/packages/Dontirun.StateMachineSemaphore)

[![View on Construct Hub](https://constructs.dev/badge?package=%40dontirun%2Fstate-machine-semaphore)](https://constructs.dev/packages/@dontirun/state-machine-semaphore)

An [aws-cdk](https://github.com/aws/aws-cdk) construct that enables you to use AWS Step Functions to control concurrency in your distributed system. You can use this construct to distributed state machine semaphores to control concurrent invocations of contentious work.

This construct is based off of [Justin Callison's](https://github.com/JustinCallison) example [code](https://github.com/aws-samples/aws-stepfunctions-examples/blob/main/sam/app-control-concurrency-with-dynamodb/statemachines/dynamodb-semaphore.asl.json). Make sure to check out Justin's [blogpost](https://aws.amazon.com/blogs/compute/controlling-concurrency-in-distributed-systems-using-aws-step-functions/) to learn about how the system works.

## Examples

### Example 1) A state machine with a controlled job

<table border-collapse="collapse">
<tr>
<th</th>
<th></th>
</tr>
<tr>
<td>

```python
import { Function } from 'aws-cdk-lib/aws-lambda';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { StateMachine, Succeed, Wait, WaitTime } from 'aws-cdk-lib/aws-stepfunctions';
import { LambdaInvoke } from 'aws-cdk-lib/aws-stepfunctions-tasks';
import { Construct } from 'constructs';
import { SemaphoreGenerator } from '@dontirun/state-machine-semaphore';


export class CdkTestStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const contestedJob = new LambdaInvoke(this, 'ContestedJobPart1', {
      lambdaFunction: Function.fromFunctionName(this, 'JobFunctionPart1', 'cool-function'),
    }).next(new Wait(this, 'Wait', { time: WaitTime.duration(Duration.seconds(7)) }))
      .next(new Wait(this, 'AnotherWait', { time: WaitTime.duration(Duration.seconds(7)) }))
      .next(new Wait(this, 'YetAnotherWait', { time: WaitTime.duration(Duration.seconds(7)) }));

    const afterContestedJob = new Succeed(this, 'Succeed');

    const generator = new SemaphoreGenerator(this, 'SemaphoreGenerator');
    const stateMachineFragment = generator.generateSemaphoredJob('life', 42, contestedJob, afterContestedJob);

    new StateMachine(this, 'StateMachine', {
      definition: stateMachineFragment,
    });
  }
}
```

</td>
<td>

![Example 1 Definition](./images/Example1_Graph_Edit.png)

</td>
</tr>
</table>

### Example 2) A state machine with multiple semaphores

<table border-collapse="collapse">
<tr>
<th></th>
<th></th>
</tr>
<tr>
<td>

```python
import { Function } from 'aws-cdk-lib/aws-lambda';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { StateMachine, Succeed, Wait, WaitTime } from 'aws-cdk-lib/aws-stepfunctions';
import { LambdaInvoke } from 'aws-cdk-lib/aws-stepfunctions-tasks';
import { Construct } from 'constructs';
import { SemaphoreGenerator } from '@dontirun/state-machine-semaphore';


export class CdkTestStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const contestedJob = new LambdaInvoke(this, 'ContestedJobPart1', {
      lambdaFunction: Function.fromFunctionName(this, 'JobFunctionPart1', 'cool-function'),
    })
    const notContestedJob = new LambdaInvoke(this, 'NotContestedJob', {
      lambdaFunction: Function.fromFunctionName(this, 'NotContestedJobFunction', 'cooler-function'),
    })
    const contestedJob2 = new LambdaInvoke(this, 'ContestedJobPart2', {
      lambdaFunction: Function.fromFunctionName(this, 'JobFunctionPart2', 'coolest-function'),
    })
    const afterContestedJob2 = new Succeed(this, 'Succeed');

    const generator = new SemaphoreGenerator(this, 'SemaphoreGenerator');
    const stateMachineFragment = generator.generateSemaphoredJob('life', 42, contestedJob, notContestedJob);
    const stateMachineFragment2 = generator.generateSemaphoredJob('liberty', 7, contestedJob2, afterContestedJob2);

    new StateMachine(this, 'StateMachine', {
      definition: stateMachineFragment.next(stateMachineFragment2),
    });
  }
}
```

</td>
<td>

![Example 2 Definition](./images/Example2_Graph_Edit.png)

</td>
</tr>
</table>

## API Reference

See [API.md](./API.md).

## License

This project is licensed under the Apache-2.0 License.
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

import aws_cdk.aws_stepfunctions
import constructs


@jsii.interface(jsii_type="@dontirun/state-machine-semaphore.IChainNextable")
class IChainNextable(
    aws_cdk.aws_stepfunctions.IChainable,
    aws_cdk.aws_stepfunctions.INextable,
    typing_extensions.Protocol,
):
    pass


class _IChainNextableProxy(
    jsii.proxy_for(aws_cdk.aws_stepfunctions.IChainable), # type: ignore[misc]
    jsii.proxy_for(aws_cdk.aws_stepfunctions.INextable), # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "@dontirun/state-machine-semaphore.IChainNextable"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IChainNextable).__jsii_proxy_class__ = lambda : _IChainNextableProxy


class SemaphoreGenerator(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@dontirun/state-machine-semaphore.SemaphoreGenerator",
):
    '''Sets up up the DynamoDB table that stores the State Machine semaphores.

    Call ``generateSemaphoredJob`` to generate semaphored jobs.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        table_read_write_capacity: typing.Optional[typing.Union["TableReadWriteCapacity", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param table_read_write_capacity: Optionally set the DynamoDB table to have a specific read/write capacity with PROVISIONED billing. Default: PAY_PER_REQUEST
        '''
        if __debug__:
            type_hints = typing.get_type_hints(SemaphoreGenerator.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SemaphoreGeneratorProps(
            table_read_write_capacity=table_read_write_capacity
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="generateSemaphoredJob")
    def generate_semaphored_job(
        self,
        lock_name: builtins.str,
        limit: jsii.Number,
        job: IChainNextable,
        next_state: aws_cdk.aws_stepfunctions.State,
        reuse_lock: typing.Optional[builtins.bool] = None,
        comments: typing.Optional[builtins.bool] = None,
    ) -> aws_cdk.aws_stepfunctions.StateMachineFragment:
        '''Generates a semaphore for a StepFunction job (or chained set of jobs) to limit parallelism across executions.

        :param lock_name: The name of the semaphore.
        :param limit: The maximum number of concurrent executions for the given lock.
        :param job: The job (or chained jobs) to be semaphored.
        :param next_state: The State to go to after the semaphored job completes.
        :param reuse_lock: Explicility allow the reuse of a named lock from a previously generated job. Throws an error if a different ``limit`` is specified. Default: false.
        :param comments: Adds detailed comments to lock related states. Significantly increases CloudFormation template size. Default: false.

        :return: A StateMachineFragment that can chained to other states in the State Machine.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(SemaphoreGenerator.generate_semaphored_job)
            check_type(argname="argument lock_name", value=lock_name, expected_type=type_hints["lock_name"])
            check_type(argname="argument limit", value=limit, expected_type=type_hints["limit"])
            check_type(argname="argument job", value=job, expected_type=type_hints["job"])
            check_type(argname="argument next_state", value=next_state, expected_type=type_hints["next_state"])
            check_type(argname="argument reuse_lock", value=reuse_lock, expected_type=type_hints["reuse_lock"])
            check_type(argname="argument comments", value=comments, expected_type=type_hints["comments"])
        return typing.cast(aws_cdk.aws_stepfunctions.StateMachineFragment, jsii.invoke(self, "generateSemaphoredJob", [lock_name, limit, job, next_state, reuse_lock, comments]))


@jsii.data_type(
    jsii_type="@dontirun/state-machine-semaphore.SemaphoreGeneratorProps",
    jsii_struct_bases=[],
    name_mapping={"table_read_write_capacity": "tableReadWriteCapacity"},
)
class SemaphoreGeneratorProps:
    def __init__(
        self,
        *,
        table_read_write_capacity: typing.Optional[typing.Union["TableReadWriteCapacity", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''Interface for creating a SemaphoreGenerator.

        :param table_read_write_capacity: Optionally set the DynamoDB table to have a specific read/write capacity with PROVISIONED billing. Default: PAY_PER_REQUEST
        '''
        if isinstance(table_read_write_capacity, dict):
            table_read_write_capacity = TableReadWriteCapacity(**table_read_write_capacity)
        if __debug__:
            type_hints = typing.get_type_hints(SemaphoreGeneratorProps.__init__)
            check_type(argname="argument table_read_write_capacity", value=table_read_write_capacity, expected_type=type_hints["table_read_write_capacity"])
        self._values: typing.Dict[str, typing.Any] = {}
        if table_read_write_capacity is not None:
            self._values["table_read_write_capacity"] = table_read_write_capacity

    @builtins.property
    def table_read_write_capacity(self) -> typing.Optional["TableReadWriteCapacity"]:
        '''Optionally set the DynamoDB table to have a specific read/write capacity with PROVISIONED billing.

        :default: PAY_PER_REQUEST
        '''
        result = self._values.get("table_read_write_capacity")
        return typing.cast(typing.Optional["TableReadWriteCapacity"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SemaphoreGeneratorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@dontirun/state-machine-semaphore.TableReadWriteCapacity",
    jsii_struct_bases=[],
    name_mapping={"read_capacity": "readCapacity", "write_capacity": "writeCapacity"},
)
class TableReadWriteCapacity:
    def __init__(
        self,
        *,
        read_capacity: jsii.Number,
        write_capacity: jsii.Number,
    ) -> None:
        '''Read and write capacity for a PROVISIONED billing DynamoDB table.

        :param read_capacity: 
        :param write_capacity: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TableReadWriteCapacity.__init__)
            check_type(argname="argument read_capacity", value=read_capacity, expected_type=type_hints["read_capacity"])
            check_type(argname="argument write_capacity", value=write_capacity, expected_type=type_hints["write_capacity"])
        self._values: typing.Dict[str, typing.Any] = {
            "read_capacity": read_capacity,
            "write_capacity": write_capacity,
        }

    @builtins.property
    def read_capacity(self) -> jsii.Number:
        result = self._values.get("read_capacity")
        assert result is not None, "Required property 'read_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def write_capacity(self) -> jsii.Number:
        result = self._values.get("write_capacity")
        assert result is not None, "Required property 'write_capacity' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TableReadWriteCapacity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IChainNextable",
    "SemaphoreGenerator",
    "SemaphoreGeneratorProps",
    "TableReadWriteCapacity",
]

publication.publish()
