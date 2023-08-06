'''
# AWS::S3ObjectLambda Construct Library

This construct library allows you to define S3 object lambda access points.

```python
# Example automatically generated from non-compiling source. May contain errors.
import monocdk as lambda_
import monocdk as s3
import monocdk as s3objectlambda
import monocdk as cdk


stack = cdk.Stack()
bucket = s3.Bucket(stack, "MyBucket")
handler = lambda_.Function(stack, "MyFunction",
    runtime=lambda_.Runtime.NODEJS_14_X,
    handler="index.handler",
    code=lambda_.Code.from_asset("lambda.zip")
)
s3objectlambda.AccessPoint(stack, "MyObjectLambda",
    bucket=bucket,
    handler=handler,
    access_point_name="my-access-point",
    payload={
        "prop": "value"
    }
)
```

## Handling range and part number requests

Lambdas are currently limited to only transforming `GetObject` requests. However, they can additionally support `GetObject-Range` and `GetObject-PartNumber` requests, which needs to be specified in the access point configuration:

```python
# Example automatically generated from non-compiling source. May contain errors.
import monocdk as lambda_
import monocdk as s3
import monocdk as s3objectlambda
import monocdk as cdk


stack = cdk.Stack()
bucket = s3.Bucket(stack, "MyBucket")
handler = lambda_.Function(stack, "MyFunction",
    runtime=lambda_.Runtime.NODEJS_14_X,
    handler="index.handler",
    code=lambda_.Code.from_asset("lambda.zip")
)
s3objectlambda.AccessPoint(stack, "MyObjectLambda",
    bucket=bucket,
    handler=handler,
    access_point_name="my-access-point",
    supports_get_object_range=True,
    supports_get_object_part_number=True
)
```

## Pass additional data to Lambda function

You can specify an additional object that provides supplemental data to the Lambda function used to transform objects. The data is delivered as a JSON payload to the Lambda:

```python
# Example automatically generated from non-compiling source. May contain errors.
import monocdk as lambda_
import monocdk as s3
import monocdk as s3objectlambda
import monocdk as cdk


stack = cdk.Stack()
bucket = s3.Bucket(stack, "MyBucket")
handler = lambda_.Function(stack, "MyFunction",
    runtime=lambda_.Runtime.NODEJS_14_X,
    handler="index.handler",
    code=lambda_.Code.from_asset("lambda.zip")
)
s3objectlambda.AccessPoint(stack, "MyObjectLambda",
    bucket=bucket,
    handler=handler,
    access_point_name="my-access-point",
    payload={
        "prop": "value"
    }
)
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

import constructs
from .. import (
    CfnResource as _CfnResource_e0a482dc,
    Construct as _Construct_e78e779f,
    IInspectable as _IInspectable_82c04a63,
    IResolvable as _IResolvable_a771d0ef,
    IResource as _IResource_8c1dbbbd,
    Resource as _Resource_abff4495,
    TreeInspector as _TreeInspector_1cd1894e,
)
from ..aws_lambda import IFunction as _IFunction_6e14f09e
from ..aws_s3 import (
    IBucket as _IBucket_73486e29,
    VirtualHostedStyleUrlOptions as _VirtualHostedStyleUrlOptions_89d473e0,
)


@jsii.data_type(
    jsii_type="monocdk.aws_s3objectlambda.AccessPointAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "access_point_arn": "accessPointArn",
        "access_point_creation_date": "accessPointCreationDate",
    },
)
class AccessPointAttributes:
    def __init__(
        self,
        *,
        access_point_arn: builtins.str,
        access_point_creation_date: builtins.str,
    ) -> None:
        '''(experimental) The access point resource attributes.

        :param access_point_arn: (experimental) The ARN of the access point.
        :param access_point_creation_date: (experimental) The creation data of the access point.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_s3objectlambda as s3objectlambda
            
            access_point_attributes = s3objectlambda.AccessPointAttributes(
                access_point_arn="accessPointArn",
                access_point_creation_date="accessPointCreationDate"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AccessPointAttributes.__init__)
            check_type(argname="argument access_point_arn", value=access_point_arn, expected_type=type_hints["access_point_arn"])
            check_type(argname="argument access_point_creation_date", value=access_point_creation_date, expected_type=type_hints["access_point_creation_date"])
        self._values: typing.Dict[str, typing.Any] = {
            "access_point_arn": access_point_arn,
            "access_point_creation_date": access_point_creation_date,
        }

    @builtins.property
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        '''
        result = self._values.get("access_point_arn")
        assert result is not None, "Required property 'access_point_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        '''
        result = self._values.get("access_point_creation_date")
        assert result is not None, "Required property 'access_point_creation_date' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPointAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_s3objectlambda.AccessPointProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "handler": "handler",
        "access_point_name": "accessPointName",
        "cloud_watch_metrics_enabled": "cloudWatchMetricsEnabled",
        "payload": "payload",
        "supports_get_object_part_number": "supportsGetObjectPartNumber",
        "supports_get_object_range": "supportsGetObjectRange",
    },
)
class AccessPointProps:
    def __init__(
        self,
        *,
        bucket: _IBucket_73486e29,
        handler: _IFunction_6e14f09e,
        access_point_name: typing.Optional[builtins.str] = None,
        cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
        payload: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        supports_get_object_part_number: typing.Optional[builtins.bool] = None,
        supports_get_object_range: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) The S3 object lambda access point configuration.

        :param bucket: (experimental) The bucket to which this access point belongs.
        :param handler: (experimental) The Lambda function used to transform objects.
        :param access_point_name: (experimental) The name of the S3 object lambda access point. Default: a unique name will be generated
        :param cloud_watch_metrics_enabled: (experimental) Whether CloudWatch metrics are enabled for the access point. Default: false
        :param payload: (experimental) Additional JSON that provides supplemental data passed to the Lambda function on every request. Default: - No data.
        :param supports_get_object_part_number: (experimental) Whether the Lambda function can process ``GetObject-PartNumber`` requests. Default: false
        :param supports_get_object_range: (experimental) Whether the Lambda function can process ``GetObject-Range`` requests. Default: false

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            import monocdk as lambda_
            import monocdk as s3
            import monocdk as s3objectlambda
            import monocdk as cdk
            
            
            stack = cdk.Stack()
            bucket = s3.Bucket(stack, "MyBucket")
            handler = lambda_.Function(stack, "MyFunction",
                runtime=lambda_.Runtime.NODEJS_14_X,
                handler="index.handler",
                code=lambda_.Code.from_asset("lambda.zip")
            )
            s3objectlambda.AccessPoint(stack, "MyObjectLambda",
                bucket=bucket,
                handler=handler,
                access_point_name="my-access-point",
                payload={
                    "prop": "value"
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AccessPointProps.__init__)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument access_point_name", value=access_point_name, expected_type=type_hints["access_point_name"])
            check_type(argname="argument cloud_watch_metrics_enabled", value=cloud_watch_metrics_enabled, expected_type=type_hints["cloud_watch_metrics_enabled"])
            check_type(argname="argument payload", value=payload, expected_type=type_hints["payload"])
            check_type(argname="argument supports_get_object_part_number", value=supports_get_object_part_number, expected_type=type_hints["supports_get_object_part_number"])
            check_type(argname="argument supports_get_object_range", value=supports_get_object_range, expected_type=type_hints["supports_get_object_range"])
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "handler": handler,
        }
        if access_point_name is not None:
            self._values["access_point_name"] = access_point_name
        if cloud_watch_metrics_enabled is not None:
            self._values["cloud_watch_metrics_enabled"] = cloud_watch_metrics_enabled
        if payload is not None:
            self._values["payload"] = payload
        if supports_get_object_part_number is not None:
            self._values["supports_get_object_part_number"] = supports_get_object_part_number
        if supports_get_object_range is not None:
            self._values["supports_get_object_range"] = supports_get_object_range

    @builtins.property
    def bucket(self) -> _IBucket_73486e29:
        '''(experimental) The bucket to which this access point belongs.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_IBucket_73486e29, result)

    @builtins.property
    def handler(self) -> _IFunction_6e14f09e:
        '''(experimental) The Lambda function used to transform objects.

        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(_IFunction_6e14f09e, result)

    @builtins.property
    def access_point_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the S3 object lambda access point.

        :default: a unique name will be generated

        :stability: experimental
        '''
        result = self._values.get("access_point_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud_watch_metrics_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether CloudWatch metrics are enabled for the access point.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("cloud_watch_metrics_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def payload(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional JSON that provides supplemental data passed to the Lambda function on every request.

        :default: - No data.

        :stability: experimental
        '''
        result = self._values.get("payload")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def supports_get_object_part_number(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the Lambda function can process ``GetObject-PartNumber`` requests.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("supports_get_object_part_number")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def supports_get_object_range(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the Lambda function can process ``GetObject-Range`` requests.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("supports_get_object_range")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_82c04a63)
class CfnAccessPoint(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_s3objectlambda.CfnAccessPoint",
):
    '''A CloudFormation ``AWS::S3ObjectLambda::AccessPoint``.

    The ``AWS::S3ObjectLambda::AccessPoint`` resource specifies an Object Lambda Access Point used to access a bucket.

    :cloudformationResource: AWS::S3ObjectLambda::AccessPoint
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspoint.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_s3objectlambda as s3objectlambda
        
        # content_transformation: Any
        
        cfn_access_point = s3objectlambda.CfnAccessPoint(self, "MyCfnAccessPoint",
            object_lambda_configuration=s3objectlambda.CfnAccessPoint.ObjectLambdaConfigurationProperty(
                supporting_access_point="supportingAccessPoint",
                transformation_configurations=[s3objectlambda.CfnAccessPoint.TransformationConfigurationProperty(
                    actions=["actions"],
                    content_transformation=content_transformation
                )],
        
                # the properties below are optional
                allowed_features=["allowedFeatures"],
                cloud_watch_metrics_enabled=False
            ),
        
            # the properties below are optional
            name="name"
        )
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        object_lambda_configuration: typing.Union[typing.Union["CfnAccessPoint.ObjectLambdaConfigurationProperty", typing.Dict[str, typing.Any]], _IResolvable_a771d0ef],
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::S3ObjectLambda::AccessPoint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param object_lambda_configuration: A configuration used when creating an Object Lambda Access Point.
        :param name: The name of this access point.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CfnAccessPoint.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnAccessPointProps(
            object_lambda_configuration=object_lambda_configuration, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_1cd1894e) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CfnAccessPoint.inspect)
            check_type(argname="argument inspector", value=inspector, expected_type=type_hints["inspector"])
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CfnAccessPoint._render_properties)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''Specifies the ARN for the Object Lambda Access Point.

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreationDate")
    def attr_creation_date(self) -> builtins.str:
        '''The date and time when the specified Object Lambda Access Point was created.

        :cloudformationAttribute: CreationDate
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCreationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLambdaConfiguration")
    def object_lambda_configuration(
        self,
    ) -> typing.Union["CfnAccessPoint.ObjectLambdaConfigurationProperty", _IResolvable_a771d0ef]:
        '''A configuration used when creating an Object Lambda Access Point.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspoint.html#cfn-s3objectlambda-accesspoint-objectlambdaconfiguration
        '''
        return typing.cast(typing.Union["CfnAccessPoint.ObjectLambdaConfigurationProperty", _IResolvable_a771d0ef], jsii.get(self, "objectLambdaConfiguration"))

    @object_lambda_configuration.setter
    def object_lambda_configuration(
        self,
        value: typing.Union["CfnAccessPoint.ObjectLambdaConfigurationProperty", _IResolvable_a771d0ef],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CfnAccessPoint, "object_lambda_configuration").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "objectLambdaConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of this access point.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspoint.html#cfn-s3objectlambda-accesspoint-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CfnAccessPoint, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @jsii.data_type(
        jsii_type="monocdk.aws_s3objectlambda.CfnAccessPoint.ObjectLambdaConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "supporting_access_point": "supportingAccessPoint",
            "transformation_configurations": "transformationConfigurations",
            "allowed_features": "allowedFeatures",
            "cloud_watch_metrics_enabled": "cloudWatchMetricsEnabled",
        },
    )
    class ObjectLambdaConfigurationProperty:
        def __init__(
            self,
            *,
            supporting_access_point: builtins.str,
            transformation_configurations: typing.Union[_IResolvable_a771d0ef, typing.Sequence[typing.Union[typing.Union["CfnAccessPoint.TransformationConfigurationProperty", typing.Dict[str, typing.Any]], _IResolvable_a771d0ef]]],
            allowed_features: typing.Optional[typing.Sequence[builtins.str]] = None,
            cloud_watch_metrics_enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]] = None,
        ) -> None:
            '''A configuration used when creating an Object Lambda Access Point.

            :param supporting_access_point: Standard access point associated with the Object Lambda Access Point.
            :param transformation_configurations: A container for transformation configurations for an Object Lambda Access Point.
            :param allowed_features: A container for allowed features. Valid inputs are ``GetObject-Range`` and ``GetObject-PartNumber`` .
            :param cloud_watch_metrics_enabled: A container for whether the CloudWatch metrics configuration is enabled.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3objectlambda-accesspoint-objectlambdaconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from monocdk import aws_s3objectlambda as s3objectlambda
                
                # content_transformation: Any
                
                object_lambda_configuration_property = s3objectlambda.CfnAccessPoint.ObjectLambdaConfigurationProperty(
                    supporting_access_point="supportingAccessPoint",
                    transformation_configurations=[s3objectlambda.CfnAccessPoint.TransformationConfigurationProperty(
                        actions=["actions"],
                        content_transformation=content_transformation
                    )],
                
                    # the properties below are optional
                    allowed_features=["allowedFeatures"],
                    cloud_watch_metrics_enabled=False
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(CfnAccessPoint.ObjectLambdaConfigurationProperty.__init__)
                check_type(argname="argument supporting_access_point", value=supporting_access_point, expected_type=type_hints["supporting_access_point"])
                check_type(argname="argument transformation_configurations", value=transformation_configurations, expected_type=type_hints["transformation_configurations"])
                check_type(argname="argument allowed_features", value=allowed_features, expected_type=type_hints["allowed_features"])
                check_type(argname="argument cloud_watch_metrics_enabled", value=cloud_watch_metrics_enabled, expected_type=type_hints["cloud_watch_metrics_enabled"])
            self._values: typing.Dict[str, typing.Any] = {
                "supporting_access_point": supporting_access_point,
                "transformation_configurations": transformation_configurations,
            }
            if allowed_features is not None:
                self._values["allowed_features"] = allowed_features
            if cloud_watch_metrics_enabled is not None:
                self._values["cloud_watch_metrics_enabled"] = cloud_watch_metrics_enabled

        @builtins.property
        def supporting_access_point(self) -> builtins.str:
            '''Standard access point associated with the Object Lambda Access Point.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3objectlambda-accesspoint-objectlambdaconfiguration.html#cfn-s3objectlambda-accesspoint-objectlambdaconfiguration-supportingaccesspoint
            '''
            result = self._values.get("supporting_access_point")
            assert result is not None, "Required property 'supporting_access_point' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def transformation_configurations(
            self,
        ) -> typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union["CfnAccessPoint.TransformationConfigurationProperty", _IResolvable_a771d0ef]]]:
            '''A container for transformation configurations for an Object Lambda Access Point.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3objectlambda-accesspoint-objectlambdaconfiguration.html#cfn-s3objectlambda-accesspoint-objectlambdaconfiguration-transformationconfigurations
            '''
            result = self._values.get("transformation_configurations")
            assert result is not None, "Required property 'transformation_configurations' is missing"
            return typing.cast(typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union["CfnAccessPoint.TransformationConfigurationProperty", _IResolvable_a771d0ef]]], result)

        @builtins.property
        def allowed_features(self) -> typing.Optional[typing.List[builtins.str]]:
            '''A container for allowed features.

            Valid inputs are ``GetObject-Range`` and ``GetObject-PartNumber`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3objectlambda-accesspoint-objectlambdaconfiguration.html#cfn-s3objectlambda-accesspoint-objectlambdaconfiguration-allowedfeatures
            '''
            result = self._values.get("allowed_features")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def cloud_watch_metrics_enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]]:
            '''A container for whether the CloudWatch metrics configuration is enabled.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3objectlambda-accesspoint-objectlambdaconfiguration.html#cfn-s3objectlambda-accesspoint-objectlambdaconfiguration-cloudwatchmetricsenabled
            '''
            result = self._values.get("cloud_watch_metrics_enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_a771d0ef]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ObjectLambdaConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="monocdk.aws_s3objectlambda.CfnAccessPoint.TransformationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "actions": "actions",
            "content_transformation": "contentTransformation",
        },
    )
    class TransformationConfigurationProperty:
        def __init__(
            self,
            *,
            actions: typing.Sequence[builtins.str],
            content_transformation: typing.Any,
        ) -> None:
            '''A configuration used when creating an Object Lambda Access Point transformation.

            :param actions: A container for the action of an Object Lambda Access Point configuration. Valid input is ``GetObject`` .
            :param content_transformation: A container for the content transformation of an Object Lambda Access Point configuration. Can include the FunctionArn and FunctionPayload. For more information, see `AwsLambdaTransformation <https://docs.aws.amazon.com/AmazonS3/latest/API/API_control_AwsLambdaTransformation.html>`_ in the *Amazon S3 API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3objectlambda-accesspoint-transformationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from monocdk import aws_s3objectlambda as s3objectlambda
                
                # content_transformation: Any
                
                transformation_configuration_property = s3objectlambda.CfnAccessPoint.TransformationConfigurationProperty(
                    actions=["actions"],
                    content_transformation=content_transformation
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(CfnAccessPoint.TransformationConfigurationProperty.__init__)
                check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
                check_type(argname="argument content_transformation", value=content_transformation, expected_type=type_hints["content_transformation"])
            self._values: typing.Dict[str, typing.Any] = {
                "actions": actions,
                "content_transformation": content_transformation,
            }

        @builtins.property
        def actions(self) -> typing.List[builtins.str]:
            '''A container for the action of an Object Lambda Access Point configuration.

            Valid input is ``GetObject`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3objectlambda-accesspoint-transformationconfiguration.html#cfn-s3objectlambda-accesspoint-transformationconfiguration-actions
            '''
            result = self._values.get("actions")
            assert result is not None, "Required property 'actions' is missing"
            return typing.cast(typing.List[builtins.str], result)

        @builtins.property
        def content_transformation(self) -> typing.Any:
            '''A container for the content transformation of an Object Lambda Access Point configuration.

            Can include the FunctionArn and FunctionPayload. For more information, see `AwsLambdaTransformation <https://docs.aws.amazon.com/AmazonS3/latest/API/API_control_AwsLambdaTransformation.html>`_ in the *Amazon S3 API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3objectlambda-accesspoint-transformationconfiguration.html#cfn-s3objectlambda-accesspoint-transformationconfiguration-contenttransformation
            '''
            result = self._values.get("content_transformation")
            assert result is not None, "Required property 'content_transformation' is missing"
            return typing.cast(typing.Any, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TransformationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.implements(_IInspectable_82c04a63)
class CfnAccessPointPolicy(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_s3objectlambda.CfnAccessPointPolicy",
):
    '''A CloudFormation ``AWS::S3ObjectLambda::AccessPointPolicy``.

    The ``AWS::S3ObjectLambda::AccessPointPolicy`` resource specifies the Object Lambda Access Point resource policy document.

    :cloudformationResource: AWS::S3ObjectLambda::AccessPointPolicy
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspointpolicy.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_s3objectlambda as s3objectlambda
        
        # policy_document: Any
        
        cfn_access_point_policy = s3objectlambda.CfnAccessPointPolicy(self, "MyCfnAccessPointPolicy",
            object_lambda_access_point="objectLambdaAccessPoint",
            policy_document=policy_document
        )
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        object_lambda_access_point: builtins.str,
        policy_document: typing.Any,
    ) -> None:
        '''Create a new ``AWS::S3ObjectLambda::AccessPointPolicy``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param object_lambda_access_point: An access point with an attached AWS Lambda function used to access transformed data from an Amazon S3 bucket.
        :param policy_document: Object Lambda Access Point resource policy document.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CfnAccessPointPolicy.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnAccessPointPolicyProps(
            object_lambda_access_point=object_lambda_access_point,
            policy_document=policy_document,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_1cd1894e) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CfnAccessPointPolicy.inspect)
            check_type(argname="argument inspector", value=inspector, expected_type=type_hints["inspector"])
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CfnAccessPointPolicy._render_properties)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLambdaAccessPoint")
    def object_lambda_access_point(self) -> builtins.str:
        '''An access point with an attached AWS Lambda function used to access transformed data from an Amazon S3 bucket.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspointpolicy.html#cfn-s3objectlambda-accesspointpolicy-objectlambdaaccesspoint
        '''
        return typing.cast(builtins.str, jsii.get(self, "objectLambdaAccessPoint"))

    @object_lambda_access_point.setter
    def object_lambda_access_point(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CfnAccessPointPolicy, "object_lambda_access_point").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "objectLambdaAccessPoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> typing.Any:
        '''Object Lambda Access Point resource policy document.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspointpolicy.html#cfn-s3objectlambda-accesspointpolicy-policydocument
        '''
        return typing.cast(typing.Any, jsii.get(self, "policyDocument"))

    @policy_document.setter
    def policy_document(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CfnAccessPointPolicy, "policy_document").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyDocument", value)


@jsii.data_type(
    jsii_type="monocdk.aws_s3objectlambda.CfnAccessPointPolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "object_lambda_access_point": "objectLambdaAccessPoint",
        "policy_document": "policyDocument",
    },
)
class CfnAccessPointPolicyProps:
    def __init__(
        self,
        *,
        object_lambda_access_point: builtins.str,
        policy_document: typing.Any,
    ) -> None:
        '''Properties for defining a ``CfnAccessPointPolicy``.

        :param object_lambda_access_point: An access point with an attached AWS Lambda function used to access transformed data from an Amazon S3 bucket.
        :param policy_document: Object Lambda Access Point resource policy document.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspointpolicy.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_s3objectlambda as s3objectlambda
            
            # policy_document: Any
            
            cfn_access_point_policy_props = s3objectlambda.CfnAccessPointPolicyProps(
                object_lambda_access_point="objectLambdaAccessPoint",
                policy_document=policy_document
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CfnAccessPointPolicyProps.__init__)
            check_type(argname="argument object_lambda_access_point", value=object_lambda_access_point, expected_type=type_hints["object_lambda_access_point"])
            check_type(argname="argument policy_document", value=policy_document, expected_type=type_hints["policy_document"])
        self._values: typing.Dict[str, typing.Any] = {
            "object_lambda_access_point": object_lambda_access_point,
            "policy_document": policy_document,
        }

    @builtins.property
    def object_lambda_access_point(self) -> builtins.str:
        '''An access point with an attached AWS Lambda function used to access transformed data from an Amazon S3 bucket.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspointpolicy.html#cfn-s3objectlambda-accesspointpolicy-objectlambdaaccesspoint
        '''
        result = self._values.get("object_lambda_access_point")
        assert result is not None, "Required property 'object_lambda_access_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_document(self) -> typing.Any:
        '''Object Lambda Access Point resource policy document.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspointpolicy.html#cfn-s3objectlambda-accesspointpolicy-policydocument
        '''
        result = self._values.get("policy_document")
        assert result is not None, "Required property 'policy_document' is missing"
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAccessPointPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_s3objectlambda.CfnAccessPointProps",
    jsii_struct_bases=[],
    name_mapping={
        "object_lambda_configuration": "objectLambdaConfiguration",
        "name": "name",
    },
)
class CfnAccessPointProps:
    def __init__(
        self,
        *,
        object_lambda_configuration: typing.Union[typing.Union[CfnAccessPoint.ObjectLambdaConfigurationProperty, typing.Dict[str, typing.Any]], _IResolvable_a771d0ef],
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``CfnAccessPoint``.

        :param object_lambda_configuration: A configuration used when creating an Object Lambda Access Point.
        :param name: The name of this access point.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspoint.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_s3objectlambda as s3objectlambda
            
            # content_transformation: Any
            
            cfn_access_point_props = s3objectlambda.CfnAccessPointProps(
                object_lambda_configuration=s3objectlambda.CfnAccessPoint.ObjectLambdaConfigurationProperty(
                    supporting_access_point="supportingAccessPoint",
                    transformation_configurations=[s3objectlambda.CfnAccessPoint.TransformationConfigurationProperty(
                        actions=["actions"],
                        content_transformation=content_transformation
                    )],
            
                    # the properties below are optional
                    allowed_features=["allowedFeatures"],
                    cloud_watch_metrics_enabled=False
                ),
            
                # the properties below are optional
                name="name"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CfnAccessPointProps.__init__)
            check_type(argname="argument object_lambda_configuration", value=object_lambda_configuration, expected_type=type_hints["object_lambda_configuration"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[str, typing.Any] = {
            "object_lambda_configuration": object_lambda_configuration,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def object_lambda_configuration(
        self,
    ) -> typing.Union[CfnAccessPoint.ObjectLambdaConfigurationProperty, _IResolvable_a771d0ef]:
        '''A configuration used when creating an Object Lambda Access Point.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspoint.html#cfn-s3objectlambda-accesspoint-objectlambdaconfiguration
        '''
        result = self._values.get("object_lambda_configuration")
        assert result is not None, "Required property 'object_lambda_configuration' is missing"
        return typing.cast(typing.Union[CfnAccessPoint.ObjectLambdaConfigurationProperty, _IResolvable_a771d0ef], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of this access point.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3objectlambda-accesspoint.html#cfn-s3objectlambda-accesspoint-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAccessPointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="monocdk.aws_s3objectlambda.IAccessPoint")
class IAccessPoint(_IResource_8c1dbbbd, typing_extensions.Protocol):
    '''(experimental) The interface that represents the AccessPoint resource.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointCreationDate")
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The IPv4 DNS name of the access point.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) The regional domain name of the access point.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="virtualHostedUrlForObject")
    def virtual_hosted_url_for_object(
        self,
        key: typing.Optional[builtins.str] = None,
        *,
        regional: typing.Optional[builtins.bool] = None,
    ) -> builtins.str:
        '''(experimental) The virtual hosted-style URL of an S3 object through this access point.

        Specify ``regional: false`` at the options for non-regional URL.

        :param key: The S3 key of the object. If not specified, the URL of the bucket is returned.
        :param regional: (experimental) Specifies the URL includes the region. Default: - true

        :return: an ObjectS3Url token

        :stability: experimental
        '''
        ...


class _IAccessPointProxy(
    jsii.proxy_for(_IResource_8c1dbbbd) # type: ignore[misc]
):
    '''(experimental) The interface that represents the AccessPoint resource.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_s3objectlambda.IAccessPoint"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointCreationDate")
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointCreationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The IPv4 DNS name of the access point.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) The regional domain name of the access point.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "regionalDomainName"))

    @jsii.member(jsii_name="virtualHostedUrlForObject")
    def virtual_hosted_url_for_object(
        self,
        key: typing.Optional[builtins.str] = None,
        *,
        regional: typing.Optional[builtins.bool] = None,
    ) -> builtins.str:
        '''(experimental) The virtual hosted-style URL of an S3 object through this access point.

        Specify ``regional: false`` at the options for non-regional URL.

        :param key: The S3 key of the object. If not specified, the URL of the bucket is returned.
        :param regional: (experimental) Specifies the URL includes the region. Default: - true

        :return: an ObjectS3Url token

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(IAccessPoint.virtual_hosted_url_for_object)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        options = _VirtualHostedStyleUrlOptions_89d473e0(regional=regional)

        return typing.cast(builtins.str, jsii.invoke(self, "virtualHostedUrlForObject", [key, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAccessPoint).__jsii_proxy_class__ = lambda : _IAccessPointProxy


@jsii.implements(IAccessPoint)
class AccessPoint(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_s3objectlambda.AccessPoint",
):
    '''(experimental) An S3 object lambda access point for intercepting and transforming ``GetObject`` requests.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        import monocdk as lambda_
        import monocdk as s3
        import monocdk as s3objectlambda
        import monocdk as cdk
        
        
        stack = cdk.Stack()
        bucket = s3.Bucket(stack, "MyBucket")
        handler = lambda_.Function(stack, "MyFunction",
            runtime=lambda_.Runtime.NODEJS_14_X,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda.zip")
        )
        s3objectlambda.AccessPoint(stack, "MyObjectLambda",
            bucket=bucket,
            handler=handler,
            access_point_name="my-access-point",
            payload={
                "prop": "value"
            }
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: _IBucket_73486e29,
        handler: _IFunction_6e14f09e,
        access_point_name: typing.Optional[builtins.str] = None,
        cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
        payload: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        supports_get_object_part_number: typing.Optional[builtins.bool] = None,
        supports_get_object_range: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket: (experimental) The bucket to which this access point belongs.
        :param handler: (experimental) The Lambda function used to transform objects.
        :param access_point_name: (experimental) The name of the S3 object lambda access point. Default: a unique name will be generated
        :param cloud_watch_metrics_enabled: (experimental) Whether CloudWatch metrics are enabled for the access point. Default: false
        :param payload: (experimental) Additional JSON that provides supplemental data passed to the Lambda function on every request. Default: - No data.
        :param supports_get_object_part_number: (experimental) Whether the Lambda function can process ``GetObject-PartNumber`` requests. Default: false
        :param supports_get_object_range: (experimental) Whether the Lambda function can process ``GetObject-Range`` requests. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AccessPoint.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AccessPointProps(
            bucket=bucket,
            handler=handler,
            access_point_name=access_point_name,
            cloud_watch_metrics_enabled=cloud_watch_metrics_enabled,
            payload=payload,
            supports_get_object_part_number=supports_get_object_part_number,
            supports_get_object_range=supports_get_object_range,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAccessPointAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_access_point_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_point_arn: builtins.str,
        access_point_creation_date: builtins.str,
    ) -> IAccessPoint:
        '''(experimental) Reference an existing AccessPoint defined outside of the CDK code.

        :param scope: -
        :param id: -
        :param access_point_arn: (experimental) The ARN of the access point.
        :param access_point_creation_date: (experimental) The creation data of the access point.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AccessPoint.from_access_point_attributes)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = AccessPointAttributes(
            access_point_arn=access_point_arn,
            access_point_creation_date=access_point_creation_date,
        )

        return typing.cast(IAccessPoint, jsii.sinvoke(cls, "fromAccessPointAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="virtualHostedUrlForObject")
    def virtual_hosted_url_for_object(
        self,
        key: typing.Optional[builtins.str] = None,
        *,
        regional: typing.Optional[builtins.bool] = None,
    ) -> builtins.str:
        '''(experimental) Implement the {@link IAccessPoint.virtualHostedUrlForObject} method.

        :param key: -
        :param regional: (experimental) Specifies the URL includes the region. Default: - true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AccessPoint.virtual_hosted_url_for_object)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        options = _VirtualHostedStyleUrlOptions_89d473e0(regional=regional)

        return typing.cast(builtins.str, jsii.invoke(self, "virtualHostedUrlForObject", [key, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointCreationDate")
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointCreationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointName")
    def access_point_name(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) Implement the {@link IAccessPoint.domainName} field.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) Implement the {@link IAccessPoint.regionalDomainName} field.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "regionalDomainName"))


__all__ = [
    "AccessPoint",
    "AccessPointAttributes",
    "AccessPointProps",
    "CfnAccessPoint",
    "CfnAccessPointPolicy",
    "CfnAccessPointPolicyProps",
    "CfnAccessPointProps",
    "IAccessPoint",
]

publication.publish()
