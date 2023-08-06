'''
# S3 Bucket Notifications Destinations

This module includes integration classes for using Topics, Queues or Lambdas
as S3 Notification Destinations.

## Examples

The following example shows how to send a notification to an SNS
topic when an object is created in an S3 bucket:

```python
import monocdk as sns


bucket = s3.Bucket(self, "Bucket")
topic = sns.Topic(self, "Topic")

bucket.add_event_notification(s3.EventType.OBJECT_CREATED_PUT, s3n.SnsDestination(topic))
```

The following example shows how to send a notification to an SQS queue
when an object is created in an S3 bucket:

```python
import monocdk as sqs


bucket = s3.Bucket(self, "Bucket")
queue = sqs.Queue(self, "Queue")

bucket.add_event_notification(s3.EventType.OBJECT_CREATED_PUT, s3n.SqsDestination(queue))
```

The following example shows how to send a notification to a Lambda function when an object is created in an S3 bucket:

```python
import monocdk as lambda_


bucket = s3.Bucket(self, "Bucket")
fn = lambda_.Function(self, "MyFunction",
    runtime=lambda_.Runtime.NODEJS_12_X,
    handler="index.handler",
    code=lambda_.Code.from_asset(path.join(__dirname, "lambda-handler"))
)

bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3n.LambdaDestination(fn))
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

from .._jsii import *

from .. import Construct as _Construct_e78e779f
from ..aws_lambda import IFunction as _IFunction_6e14f09e
from ..aws_s3 import (
    BucketNotificationDestinationConfig as _BucketNotificationDestinationConfig_6250d0a4,
    IBucket as _IBucket_73486e29,
    IBucketNotificationDestination as _IBucketNotificationDestination_45dee433,
)
from ..aws_sns import ITopic as _ITopic_465e36b9
from ..aws_sqs import IQueue as _IQueue_45a01ab4


@jsii.implements(_IBucketNotificationDestination_45dee433)
class LambdaDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_s3_notifications.LambdaDestination",
):
    '''(experimental) Use a Lambda function as a bucket notification destination.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # my_lambda: lambda.Function
        
        bucket = s3.Bucket.from_bucket_attributes(self, "ImportedBucket",
            bucket_arn="arn:aws:s3:::my-bucket"
        )
        
        # now you can just call methods on the bucket
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3n.LambdaDestination(my_lambda), prefix="home/myusername/*")
    '''

    def __init__(self, fn: _IFunction_6e14f09e) -> None:
        '''
        :param fn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(LambdaDestination.__init__)
            check_type(argname="argument fn", value=fn, expected_type=type_hints["fn"])
        jsii.create(self.__class__, self, [fn])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _Construct_e78e779f,
        bucket: _IBucket_73486e29,
    ) -> _BucketNotificationDestinationConfig_6250d0a4:
        '''(experimental) Registers this resource to receive notifications for the specified bucket.

        This method will only be called once for each destination/bucket
        pair and the result will be cached, so there is no need to implement
        idempotency in each destination.

        :param _scope: -
        :param bucket: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(LambdaDestination.bind)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
        return typing.cast(_BucketNotificationDestinationConfig_6250d0a4, jsii.invoke(self, "bind", [_scope, bucket]))


@jsii.implements(_IBucketNotificationDestination_45dee433)
class SnsDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_s3_notifications.SnsDestination",
):
    '''(experimental) Use an SNS topic as a bucket notification destination.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        bucket = s3.Bucket(self, "MyBucket")
        topic = sns.Topic(self, "MyTopic")
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3n.SnsDestination(topic))
    '''

    def __init__(self, topic: _ITopic_465e36b9) -> None:
        '''
        :param topic: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(SnsDestination.__init__)
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
        jsii.create(self.__class__, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _Construct_e78e779f,
        bucket: _IBucket_73486e29,
    ) -> _BucketNotificationDestinationConfig_6250d0a4:
        '''(experimental) Registers this resource to receive notifications for the specified bucket.

        This method will only be called once for each destination/bucket
        pair and the result will be cached, so there is no need to implement
        idempotency in each destination.

        :param _scope: -
        :param bucket: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(SnsDestination.bind)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
        return typing.cast(_BucketNotificationDestinationConfig_6250d0a4, jsii.invoke(self, "bind", [_scope, bucket]))


@jsii.implements(_IBucketNotificationDestination_45dee433)
class SqsDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_s3_notifications.SqsDestination",
):
    '''(experimental) Use an SQS queue as a bucket notification destination.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # my_queue: sqs.Queue
        
        bucket = s3.Bucket(self, "MyBucket")
        bucket.add_event_notification(s3.EventType.OBJECT_REMOVED,
            s3n.SqsDestination(my_queue), prefix="foo/", suffix=".jpg")
    '''

    def __init__(self, queue: _IQueue_45a01ab4) -> None:
        '''
        :param queue: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(SqsDestination.__init__)
            check_type(argname="argument queue", value=queue, expected_type=type_hints["queue"])
        jsii.create(self.__class__, self, [queue])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _Construct_e78e779f,
        bucket: _IBucket_73486e29,
    ) -> _BucketNotificationDestinationConfig_6250d0a4:
        '''(experimental) Allows using SQS queues as destinations for bucket notifications.

        Use ``bucket.onEvent(event, queue)`` to subscribe.

        :param _scope: -
        :param bucket: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(SqsDestination.bind)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
        return typing.cast(_BucketNotificationDestinationConfig_6250d0a4, jsii.invoke(self, "bind", [_scope, bucket]))


__all__ = [
    "LambdaDestination",
    "SnsDestination",
    "SqsDestination",
]

publication.publish()
