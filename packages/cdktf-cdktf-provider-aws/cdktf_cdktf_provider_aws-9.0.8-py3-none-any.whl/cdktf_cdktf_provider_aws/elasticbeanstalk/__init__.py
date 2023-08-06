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

import cdktf
import constructs


class DataAwsElasticBeanstalkApplication(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.DataAwsElasticBeanstalkApplication",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_application aws_elastic_beanstalk_application}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_application aws_elastic_beanstalk_application} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_application#name DataAwsElasticBeanstalkApplication#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_application#id DataAwsElasticBeanstalkApplication#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsElasticBeanstalkApplication.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsElasticBeanstalkApplicationConfig(
            name=name,
            id=id,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appversionLifecycle")
    def appversion_lifecycle(
        self,
    ) -> "DataAwsElasticBeanstalkApplicationAppversionLifecycleList":
        return typing.cast("DataAwsElasticBeanstalkApplicationAppversionLifecycleList", jsii.get(self, "appversionLifecycle"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkApplication, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkApplication, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.DataAwsElasticBeanstalkApplicationAppversionLifecycle",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsElasticBeanstalkApplicationAppversionLifecycle:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsElasticBeanstalkApplicationAppversionLifecycle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsElasticBeanstalkApplicationAppversionLifecycleList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.DataAwsElasticBeanstalkApplicationAppversionLifecycleList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsElasticBeanstalkApplicationAppversionLifecycleList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsElasticBeanstalkApplicationAppversionLifecycleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsElasticBeanstalkApplicationAppversionLifecycleList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsElasticBeanstalkApplicationAppversionLifecycleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkApplicationAppversionLifecycleList, "_terraform_attribute").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkApplicationAppversionLifecycleList, "_terraform_resource").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkApplicationAppversionLifecycleList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsElasticBeanstalkApplicationAppversionLifecycleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.DataAwsElasticBeanstalkApplicationAppversionLifecycleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsElasticBeanstalkApplicationAppversionLifecycleOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteSourceFromS3")
    def delete_source_from_s3(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "deleteSourceFromS3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAgeInDays")
    def max_age_in_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAgeInDays"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxCount")
    def max_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsElasticBeanstalkApplicationAppversionLifecycle]:
        return typing.cast(typing.Optional[DataAwsElasticBeanstalkApplicationAppversionLifecycle], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsElasticBeanstalkApplicationAppversionLifecycle],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkApplicationAppversionLifecycleOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.DataAwsElasticBeanstalkApplicationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "id": "id",
    },
)
class DataAwsElasticBeanstalkApplicationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Elastic Beanstalk.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_application#name DataAwsElasticBeanstalkApplication#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_application#id DataAwsElasticBeanstalkApplication#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsElasticBeanstalkApplicationConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[cdktf.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[cdktf.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_application#name DataAwsElasticBeanstalkApplication#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_application#id DataAwsElasticBeanstalkApplication#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsElasticBeanstalkApplicationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsElasticBeanstalkHostedZone(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.DataAwsElasticBeanstalkHostedZone",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_hosted_zone aws_elastic_beanstalk_hosted_zone}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_hosted_zone aws_elastic_beanstalk_hosted_zone} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_hosted_zone#id DataAwsElasticBeanstalkHostedZone#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_hosted_zone#region DataAwsElasticBeanstalkHostedZone#region}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsElasticBeanstalkHostedZone.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsElasticBeanstalkHostedZoneConfig(
            id=id,
            region=region,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkHostedZone, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkHostedZone, "region").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.DataAwsElasticBeanstalkHostedZoneConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "id": "id",
        "region": "region",
    },
)
class DataAwsElasticBeanstalkHostedZoneConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
        id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Elastic Beanstalk.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_hosted_zone#id DataAwsElasticBeanstalkHostedZone#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_hosted_zone#region DataAwsElasticBeanstalkHostedZone#region}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsElasticBeanstalkHostedZoneConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[str, typing.Any] = {}
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if id is not None:
            self._values["id"] = id
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[cdktf.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[cdktf.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_hosted_zone#id DataAwsElasticBeanstalkHostedZone#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_hosted_zone#region DataAwsElasticBeanstalkHostedZone#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsElasticBeanstalkHostedZoneConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsElasticBeanstalkSolutionStack(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.DataAwsElasticBeanstalkSolutionStack",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack aws_elastic_beanstalk_solution_stack}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name_regex: builtins.str,
        id: typing.Optional[builtins.str] = None,
        most_recent: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack aws_elastic_beanstalk_solution_stack} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack#name_regex DataAwsElasticBeanstalkSolutionStack#name_regex}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack#id DataAwsElasticBeanstalkSolutionStack#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param most_recent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack#most_recent DataAwsElasticBeanstalkSolutionStack#most_recent}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsElasticBeanstalkSolutionStack.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsElasticBeanstalkSolutionStackConfig(
            name_regex=name_regex,
            id=id,
            most_recent=most_recent,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMostRecent")
    def reset_most_recent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMostRecent", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRecentInput")
    def most_recent_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "mostRecentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameRegexInput")
    def name_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameRegexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkSolutionStack, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRecent")
    def most_recent(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "mostRecent"))

    @most_recent.setter
    def most_recent(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkSolutionStack, "most_recent").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mostRecent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameRegex")
    def name_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameRegex"))

    @name_regex.setter
    def name_regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsElasticBeanstalkSolutionStack, "name_regex").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nameRegex", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.DataAwsElasticBeanstalkSolutionStackConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name_regex": "nameRegex",
        "id": "id",
        "most_recent": "mostRecent",
    },
)
class DataAwsElasticBeanstalkSolutionStackConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
        name_regex: builtins.str,
        id: typing.Optional[builtins.str] = None,
        most_recent: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Elastic Beanstalk.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack#name_regex DataAwsElasticBeanstalkSolutionStack#name_regex}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack#id DataAwsElasticBeanstalkSolutionStack#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param most_recent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack#most_recent DataAwsElasticBeanstalkSolutionStack#most_recent}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsElasticBeanstalkSolutionStackConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name_regex", value=name_regex, expected_type=type_hints["name_regex"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument most_recent", value=most_recent, expected_type=type_hints["most_recent"])
        self._values: typing.Dict[str, typing.Any] = {
            "name_regex": name_regex,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if id is not None:
            self._values["id"] = id
        if most_recent is not None:
            self._values["most_recent"] = most_recent

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[cdktf.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[cdktf.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]], result)

    @builtins.property
    def name_regex(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack#name_regex DataAwsElasticBeanstalkSolutionStack#name_regex}.'''
        result = self._values.get("name_regex")
        assert result is not None, "Required property 'name_regex' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack#id DataAwsElasticBeanstalkSolutionStack#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def most_recent(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elastic_beanstalk_solution_stack#most_recent DataAwsElasticBeanstalkSolutionStack#most_recent}.'''
        result = self._values.get("most_recent")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsElasticBeanstalkSolutionStackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticBeanstalkApplication(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkApplication",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application aws_elastic_beanstalk_application}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        appversion_lifecycle: typing.Optional[typing.Union["ElasticBeanstalkApplicationAppversionLifecycle", typing.Dict[str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application aws_elastic_beanstalk_application} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#name ElasticBeanstalkApplication#name}.
        :param appversion_lifecycle: appversion_lifecycle block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#appversion_lifecycle ElasticBeanstalkApplication#appversion_lifecycle}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#description ElasticBeanstalkApplication#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#id ElasticBeanstalkApplication#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#tags ElasticBeanstalkApplication#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#tags_all ElasticBeanstalkApplication#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkApplication.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ElasticBeanstalkApplicationConfig(
            name=name,
            appversion_lifecycle=appversion_lifecycle,
            description=description,
            id=id,
            tags=tags,
            tags_all=tags_all,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putAppversionLifecycle")
    def put_appversion_lifecycle(
        self,
        *,
        service_role: builtins.str,
        delete_source_from_s3: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_age_in_days: typing.Optional[jsii.Number] = None,
        max_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param service_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#service_role ElasticBeanstalkApplication#service_role}.
        :param delete_source_from_s3: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#delete_source_from_s3 ElasticBeanstalkApplication#delete_source_from_s3}.
        :param max_age_in_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#max_age_in_days ElasticBeanstalkApplication#max_age_in_days}.
        :param max_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#max_count ElasticBeanstalkApplication#max_count}.
        '''
        value = ElasticBeanstalkApplicationAppversionLifecycle(
            service_role=service_role,
            delete_source_from_s3=delete_source_from_s3,
            max_age_in_days=max_age_in_days,
            max_count=max_count,
        )

        return typing.cast(None, jsii.invoke(self, "putAppversionLifecycle", [value]))

    @jsii.member(jsii_name="resetAppversionLifecycle")
    def reset_appversion_lifecycle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppversionLifecycle", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appversionLifecycle")
    def appversion_lifecycle(
        self,
    ) -> "ElasticBeanstalkApplicationAppversionLifecycleOutputReference":
        return typing.cast("ElasticBeanstalkApplicationAppversionLifecycleOutputReference", jsii.get(self, "appversionLifecycle"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appversionLifecycleInput")
    def appversion_lifecycle_input(
        self,
    ) -> typing.Optional["ElasticBeanstalkApplicationAppversionLifecycle"]:
        return typing.cast(typing.Optional["ElasticBeanstalkApplicationAppversionLifecycle"], jsii.get(self, "appversionLifecycleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplication, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplication, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplication, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplication, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplication, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkApplicationAppversionLifecycle",
    jsii_struct_bases=[],
    name_mapping={
        "service_role": "serviceRole",
        "delete_source_from_s3": "deleteSourceFromS3",
        "max_age_in_days": "maxAgeInDays",
        "max_count": "maxCount",
    },
)
class ElasticBeanstalkApplicationAppversionLifecycle:
    def __init__(
        self,
        *,
        service_role: builtins.str,
        delete_source_from_s3: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_age_in_days: typing.Optional[jsii.Number] = None,
        max_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param service_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#service_role ElasticBeanstalkApplication#service_role}.
        :param delete_source_from_s3: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#delete_source_from_s3 ElasticBeanstalkApplication#delete_source_from_s3}.
        :param max_age_in_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#max_age_in_days ElasticBeanstalkApplication#max_age_in_days}.
        :param max_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#max_count ElasticBeanstalkApplication#max_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkApplicationAppversionLifecycle.__init__)
            check_type(argname="argument service_role", value=service_role, expected_type=type_hints["service_role"])
            check_type(argname="argument delete_source_from_s3", value=delete_source_from_s3, expected_type=type_hints["delete_source_from_s3"])
            check_type(argname="argument max_age_in_days", value=max_age_in_days, expected_type=type_hints["max_age_in_days"])
            check_type(argname="argument max_count", value=max_count, expected_type=type_hints["max_count"])
        self._values: typing.Dict[str, typing.Any] = {
            "service_role": service_role,
        }
        if delete_source_from_s3 is not None:
            self._values["delete_source_from_s3"] = delete_source_from_s3
        if max_age_in_days is not None:
            self._values["max_age_in_days"] = max_age_in_days
        if max_count is not None:
            self._values["max_count"] = max_count

    @builtins.property
    def service_role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#service_role ElasticBeanstalkApplication#service_role}.'''
        result = self._values.get("service_role")
        assert result is not None, "Required property 'service_role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_source_from_s3(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#delete_source_from_s3 ElasticBeanstalkApplication#delete_source_from_s3}.'''
        result = self._values.get("delete_source_from_s3")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def max_age_in_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#max_age_in_days ElasticBeanstalkApplication#max_age_in_days}.'''
        result = self._values.get("max_age_in_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#max_count ElasticBeanstalkApplication#max_count}.'''
        result = self._values.get("max_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticBeanstalkApplicationAppversionLifecycle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticBeanstalkApplicationAppversionLifecycleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkApplicationAppversionLifecycleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkApplicationAppversionLifecycleOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDeleteSourceFromS3")
    def reset_delete_source_from_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteSourceFromS3", []))

    @jsii.member(jsii_name="resetMaxAgeInDays")
    def reset_max_age_in_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAgeInDays", []))

    @jsii.member(jsii_name="resetMaxCount")
    def reset_max_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxCount", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteSourceFromS3Input")
    def delete_source_from_s3_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deleteSourceFromS3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAgeInDaysInput")
    def max_age_in_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAgeInDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxCountInput")
    def max_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleInput")
    def service_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteSourceFromS3")
    def delete_source_from_s3(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deleteSourceFromS3"))

    @delete_source_from_s3.setter
    def delete_source_from_s3(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationAppversionLifecycleOutputReference, "delete_source_from_s3").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteSourceFromS3", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAgeInDays")
    def max_age_in_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAgeInDays"))

    @max_age_in_days.setter
    def max_age_in_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationAppversionLifecycleOutputReference, "max_age_in_days").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAgeInDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxCount")
    def max_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxCount"))

    @max_count.setter
    def max_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationAppversionLifecycleOutputReference, "max_count").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @service_role.setter
    def service_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationAppversionLifecycleOutputReference, "service_role").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElasticBeanstalkApplicationAppversionLifecycle]:
        return typing.cast(typing.Optional[ElasticBeanstalkApplicationAppversionLifecycle], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElasticBeanstalkApplicationAppversionLifecycle],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationAppversionLifecycleOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkApplicationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "appversion_lifecycle": "appversionLifecycle",
        "description": "description",
        "id": "id",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ElasticBeanstalkApplicationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
        name: builtins.str,
        appversion_lifecycle: typing.Optional[typing.Union[ElasticBeanstalkApplicationAppversionLifecycle, typing.Dict[str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Elastic Beanstalk.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#name ElasticBeanstalkApplication#name}.
        :param appversion_lifecycle: appversion_lifecycle block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#appversion_lifecycle ElasticBeanstalkApplication#appversion_lifecycle}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#description ElasticBeanstalkApplication#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#id ElasticBeanstalkApplication#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#tags ElasticBeanstalkApplication#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#tags_all ElasticBeanstalkApplication#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(appversion_lifecycle, dict):
            appversion_lifecycle = ElasticBeanstalkApplicationAppversionLifecycle(**appversion_lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkApplicationConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument appversion_lifecycle", value=appversion_lifecycle, expected_type=type_hints["appversion_lifecycle"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if appversion_lifecycle is not None:
            self._values["appversion_lifecycle"] = appversion_lifecycle
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[cdktf.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[cdktf.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#name ElasticBeanstalkApplication#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def appversion_lifecycle(
        self,
    ) -> typing.Optional[ElasticBeanstalkApplicationAppversionLifecycle]:
        '''appversion_lifecycle block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#appversion_lifecycle ElasticBeanstalkApplication#appversion_lifecycle}
        '''
        result = self._values.get("appversion_lifecycle")
        return typing.cast(typing.Optional[ElasticBeanstalkApplicationAppversionLifecycle], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#description ElasticBeanstalkApplication#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#id ElasticBeanstalkApplication#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#tags ElasticBeanstalkApplication#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application#tags_all ElasticBeanstalkApplication#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticBeanstalkApplicationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticBeanstalkApplicationVersion(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkApplicationVersion",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version aws_elastic_beanstalk_application_version}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        application: builtins.str,
        bucket: builtins.str,
        key: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        force_delete: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version aws_elastic_beanstalk_application_version} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param application: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#application ElasticBeanstalkApplicationVersion#application}.
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#bucket ElasticBeanstalkApplicationVersion#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#key ElasticBeanstalkApplicationVersion#key}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#name ElasticBeanstalkApplicationVersion#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#description ElasticBeanstalkApplicationVersion#description}.
        :param force_delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#force_delete ElasticBeanstalkApplicationVersion#force_delete}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#id ElasticBeanstalkApplicationVersion#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#tags ElasticBeanstalkApplicationVersion#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#tags_all ElasticBeanstalkApplicationVersion#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkApplicationVersion.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ElasticBeanstalkApplicationVersionConfig(
            application=application,
            bucket=bucket,
            key=key,
            name=name,
            description=description,
            force_delete=force_delete,
            id=id,
            tags=tags,
            tags_all=tags_all,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetForceDelete")
    def reset_force_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDelete", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationInput")
    def application_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDeleteInput")
    def force_delete_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDeleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="application")
    def application(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "application"))

    @application.setter
    def application(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationVersion, "application").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "application", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationVersion, "bucket").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationVersion, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDelete")
    def force_delete(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceDelete"))

    @force_delete.setter
    def force_delete(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationVersion, "force_delete").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceDelete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationVersion, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationVersion, "key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationVersion, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationVersion, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkApplicationVersion, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkApplicationVersionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "application": "application",
        "bucket": "bucket",
        "key": "key",
        "name": "name",
        "description": "description",
        "force_delete": "forceDelete",
        "id": "id",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ElasticBeanstalkApplicationVersionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
        application: builtins.str,
        bucket: builtins.str,
        key: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        force_delete: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Elastic Beanstalk.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param application: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#application ElasticBeanstalkApplicationVersion#application}.
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#bucket ElasticBeanstalkApplicationVersion#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#key ElasticBeanstalkApplicationVersion#key}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#name ElasticBeanstalkApplicationVersion#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#description ElasticBeanstalkApplicationVersion#description}.
        :param force_delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#force_delete ElasticBeanstalkApplicationVersion#force_delete}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#id ElasticBeanstalkApplicationVersion#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#tags ElasticBeanstalkApplicationVersion#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#tags_all ElasticBeanstalkApplicationVersion#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkApplicationVersionConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument force_delete", value=force_delete, expected_type=type_hints["force_delete"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "application": application,
            "bucket": bucket,
            "key": key,
            "name": name,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if description is not None:
            self._values["description"] = description
        if force_delete is not None:
            self._values["force_delete"] = force_delete
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[cdktf.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[cdktf.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]], result)

    @builtins.property
    def application(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#application ElasticBeanstalkApplicationVersion#application}.'''
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#bucket ElasticBeanstalkApplicationVersion#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#key ElasticBeanstalkApplicationVersion#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#name ElasticBeanstalkApplicationVersion#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#description ElasticBeanstalkApplicationVersion#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_delete(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#force_delete ElasticBeanstalkApplicationVersion#force_delete}.'''
        result = self._values.get("force_delete")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#id ElasticBeanstalkApplicationVersion#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#tags ElasticBeanstalkApplicationVersion#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_application_version#tags_all ElasticBeanstalkApplicationVersion#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticBeanstalkApplicationVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticBeanstalkConfigurationTemplate(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkConfigurationTemplate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template aws_elastic_beanstalk_configuration_template}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        application: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        environment_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        setting: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ElasticBeanstalkConfigurationTemplateSetting", typing.Dict[str, typing.Any]]]]] = None,
        solution_stack_name: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template aws_elastic_beanstalk_configuration_template} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param application: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#application ElasticBeanstalkConfigurationTemplate#application}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#name ElasticBeanstalkConfigurationTemplate#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#description ElasticBeanstalkConfigurationTemplate#description}.
        :param environment_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#environment_id ElasticBeanstalkConfigurationTemplate#environment_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#id ElasticBeanstalkConfigurationTemplate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param setting: setting block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#setting ElasticBeanstalkConfigurationTemplate#setting}
        :param solution_stack_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#solution_stack_name ElasticBeanstalkConfigurationTemplate#solution_stack_name}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkConfigurationTemplate.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ElasticBeanstalkConfigurationTemplateConfig(
            application=application,
            name=name,
            description=description,
            environment_id=environment_id,
            id=id,
            setting=setting,
            solution_stack_name=solution_stack_name,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putSetting")
    def put_setting(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ElasticBeanstalkConfigurationTemplateSetting", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkConfigurationTemplate.put_setting)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSetting", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnvironmentId")
    def reset_environment_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironmentId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSetting")
    def reset_setting(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetting", []))

    @jsii.member(jsii_name="resetSolutionStackName")
    def reset_solution_stack_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSolutionStackName", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setting")
    def setting(self) -> "ElasticBeanstalkConfigurationTemplateSettingList":
        return typing.cast("ElasticBeanstalkConfigurationTemplateSettingList", jsii.get(self, "setting"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationInput")
    def application_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentIdInput")
    def environment_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "environmentIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="settingInput")
    def setting_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ElasticBeanstalkConfigurationTemplateSetting"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ElasticBeanstalkConfigurationTemplateSetting"]]], jsii.get(self, "settingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="solutionStackNameInput")
    def solution_stack_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "solutionStackNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="application")
    def application(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "application"))

    @application.setter
    def application(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplate, "application").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "application", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplate, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentId")
    def environment_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environmentId"))

    @environment_id.setter
    def environment_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplate, "environment_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environmentId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplate, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplate, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="solutionStackName")
    def solution_stack_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "solutionStackName"))

    @solution_stack_name.setter
    def solution_stack_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplate, "solution_stack_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "solutionStackName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkConfigurationTemplateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "application": "application",
        "name": "name",
        "description": "description",
        "environment_id": "environmentId",
        "id": "id",
        "setting": "setting",
        "solution_stack_name": "solutionStackName",
    },
)
class ElasticBeanstalkConfigurationTemplateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
        application: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        environment_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        setting: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ElasticBeanstalkConfigurationTemplateSetting", typing.Dict[str, typing.Any]]]]] = None,
        solution_stack_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Elastic Beanstalk.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param application: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#application ElasticBeanstalkConfigurationTemplate#application}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#name ElasticBeanstalkConfigurationTemplate#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#description ElasticBeanstalkConfigurationTemplate#description}.
        :param environment_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#environment_id ElasticBeanstalkConfigurationTemplate#environment_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#id ElasticBeanstalkConfigurationTemplate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param setting: setting block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#setting ElasticBeanstalkConfigurationTemplate#setting}
        :param solution_stack_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#solution_stack_name ElasticBeanstalkConfigurationTemplate#solution_stack_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkConfigurationTemplateConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument environment_id", value=environment_id, expected_type=type_hints["environment_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument setting", value=setting, expected_type=type_hints["setting"])
            check_type(argname="argument solution_stack_name", value=solution_stack_name, expected_type=type_hints["solution_stack_name"])
        self._values: typing.Dict[str, typing.Any] = {
            "application": application,
            "name": name,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if description is not None:
            self._values["description"] = description
        if environment_id is not None:
            self._values["environment_id"] = environment_id
        if id is not None:
            self._values["id"] = id
        if setting is not None:
            self._values["setting"] = setting
        if solution_stack_name is not None:
            self._values["solution_stack_name"] = solution_stack_name

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[cdktf.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[cdktf.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]], result)

    @builtins.property
    def application(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#application ElasticBeanstalkConfigurationTemplate#application}.'''
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#name ElasticBeanstalkConfigurationTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#description ElasticBeanstalkConfigurationTemplate#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#environment_id ElasticBeanstalkConfigurationTemplate#environment_id}.'''
        result = self._values.get("environment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#id ElasticBeanstalkConfigurationTemplate#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def setting(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ElasticBeanstalkConfigurationTemplateSetting"]]]:
        '''setting block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#setting ElasticBeanstalkConfigurationTemplate#setting}
        '''
        result = self._values.get("setting")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ElasticBeanstalkConfigurationTemplateSetting"]]], result)

    @builtins.property
    def solution_stack_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#solution_stack_name ElasticBeanstalkConfigurationTemplate#solution_stack_name}.'''
        result = self._values.get("solution_stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticBeanstalkConfigurationTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkConfigurationTemplateSetting",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "namespace": "namespace",
        "value": "value",
        "resource": "resource",
    },
)
class ElasticBeanstalkConfigurationTemplateSetting:
    def __init__(
        self,
        *,
        name: builtins.str,
        namespace: builtins.str,
        value: builtins.str,
        resource: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#name ElasticBeanstalkConfigurationTemplate#name}.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#namespace ElasticBeanstalkConfigurationTemplate#namespace}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#value ElasticBeanstalkConfigurationTemplate#value}.
        :param resource: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#resource ElasticBeanstalkConfigurationTemplate#resource}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkConfigurationTemplateSetting.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "namespace": namespace,
            "value": value,
        }
        if resource is not None:
            self._values["resource"] = resource

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#name ElasticBeanstalkConfigurationTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#namespace ElasticBeanstalkConfigurationTemplate#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#value ElasticBeanstalkConfigurationTemplate#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_configuration_template#resource ElasticBeanstalkConfigurationTemplate#resource}.'''
        result = self._values.get("resource")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticBeanstalkConfigurationTemplateSetting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticBeanstalkConfigurationTemplateSettingList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkConfigurationTemplateSettingList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkConfigurationTemplateSettingList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElasticBeanstalkConfigurationTemplateSettingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkConfigurationTemplateSettingList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElasticBeanstalkConfigurationTemplateSettingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplateSettingList, "_terraform_attribute").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplateSettingList, "_terraform_resource").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplateSettingList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ElasticBeanstalkConfigurationTemplateSetting]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ElasticBeanstalkConfigurationTemplateSetting]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ElasticBeanstalkConfigurationTemplateSetting]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplateSettingList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ElasticBeanstalkConfigurationTemplateSettingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkConfigurationTemplateSettingOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkConfigurationTemplateSettingOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetResource")
    def reset_resource(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResource", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceInput")
    def resource_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplateSettingOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplateSettingOutputReference, "namespace").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resource"))

    @resource.setter
    def resource(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplateSettingOutputReference, "resource").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplateSettingOutputReference, "value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ElasticBeanstalkConfigurationTemplateSetting, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ElasticBeanstalkConfigurationTemplateSetting, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ElasticBeanstalkConfigurationTemplateSetting, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkConfigurationTemplateSettingOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ElasticBeanstalkEnvironment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkEnvironment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment aws_elastic_beanstalk_environment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        application: builtins.str,
        name: builtins.str,
        cname_prefix: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        platform_arn: typing.Optional[builtins.str] = None,
        poll_interval: typing.Optional[builtins.str] = None,
        setting: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ElasticBeanstalkEnvironmentSetting", typing.Dict[str, typing.Any]]]]] = None,
        solution_stack_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        template_name: typing.Optional[builtins.str] = None,
        tier: typing.Optional[builtins.str] = None,
        version_label: typing.Optional[builtins.str] = None,
        wait_for_ready_timeout: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment aws_elastic_beanstalk_environment} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param application: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#application ElasticBeanstalkEnvironment#application}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#name ElasticBeanstalkEnvironment#name}.
        :param cname_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#cname_prefix ElasticBeanstalkEnvironment#cname_prefix}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#description ElasticBeanstalkEnvironment#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#id ElasticBeanstalkEnvironment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param platform_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#platform_arn ElasticBeanstalkEnvironment#platform_arn}.
        :param poll_interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#poll_interval ElasticBeanstalkEnvironment#poll_interval}.
        :param setting: setting block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#setting ElasticBeanstalkEnvironment#setting}
        :param solution_stack_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#solution_stack_name ElasticBeanstalkEnvironment#solution_stack_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#tags ElasticBeanstalkEnvironment#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#tags_all ElasticBeanstalkEnvironment#tags_all}.
        :param template_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#template_name ElasticBeanstalkEnvironment#template_name}.
        :param tier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#tier ElasticBeanstalkEnvironment#tier}.
        :param version_label: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#version_label ElasticBeanstalkEnvironment#version_label}.
        :param wait_for_ready_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#wait_for_ready_timeout ElasticBeanstalkEnvironment#wait_for_ready_timeout}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkEnvironment.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ElasticBeanstalkEnvironmentConfig(
            application=application,
            name=name,
            cname_prefix=cname_prefix,
            description=description,
            id=id,
            platform_arn=platform_arn,
            poll_interval=poll_interval,
            setting=setting,
            solution_stack_name=solution_stack_name,
            tags=tags,
            tags_all=tags_all,
            template_name=template_name,
            tier=tier,
            version_label=version_label,
            wait_for_ready_timeout=wait_for_ready_timeout,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putSetting")
    def put_setting(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ElasticBeanstalkEnvironmentSetting", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkEnvironment.put_setting)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSetting", [value]))

    @jsii.member(jsii_name="resetCnamePrefix")
    def reset_cname_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCnamePrefix", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPlatformArn")
    def reset_platform_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlatformArn", []))

    @jsii.member(jsii_name="resetPollInterval")
    def reset_poll_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPollInterval", []))

    @jsii.member(jsii_name="resetSetting")
    def reset_setting(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetting", []))

    @jsii.member(jsii_name="resetSolutionStackName")
    def reset_solution_stack_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSolutionStackName", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTemplateName")
    def reset_template_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplateName", []))

    @jsii.member(jsii_name="resetTier")
    def reset_tier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTier", []))

    @jsii.member(jsii_name="resetVersionLabel")
    def reset_version_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersionLabel", []))

    @jsii.member(jsii_name="resetWaitForReadyTimeout")
    def reset_wait_for_ready_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitForReadyTimeout", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allSettings")
    def all_settings(self) -> "ElasticBeanstalkEnvironmentAllSettingsList":
        return typing.cast("ElasticBeanstalkEnvironmentAllSettingsList", jsii.get(self, "allSettings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingGroups")
    def autoscaling_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "autoscalingGroups"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cname")
    def cname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cname"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointUrl")
    def endpoint_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instances")
    def instances(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instances"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchConfigurations")
    def launch_configurations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "launchConfigurations"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadBalancers")
    def load_balancers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "loadBalancers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queues")
    def queues(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "queues"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setting")
    def setting(self) -> "ElasticBeanstalkEnvironmentSettingList":
        return typing.cast("ElasticBeanstalkEnvironmentSettingList", jsii.get(self, "setting"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggers")
    def triggers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "triggers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationInput")
    def application_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cnamePrefixInput")
    def cname_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cnamePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformArnInput")
    def platform_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "platformArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pollIntervalInput")
    def poll_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pollIntervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="settingInput")
    def setting_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ElasticBeanstalkEnvironmentSetting"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ElasticBeanstalkEnvironmentSetting"]]], jsii.get(self, "settingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="solutionStackNameInput")
    def solution_stack_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "solutionStackNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateNameInput")
    def template_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tierInput")
    def tier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionLabelInput")
    def version_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionLabelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitForReadyTimeoutInput")
    def wait_for_ready_timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "waitForReadyTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="application")
    def application(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "application"))

    @application.setter
    def application(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "application").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "application", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cnamePrefix")
    def cname_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cnamePrefix"))

    @cname_prefix.setter
    def cname_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "cname_prefix").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cnamePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformArn")
    def platform_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformArn"))

    @platform_arn.setter
    def platform_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "platform_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "platformArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pollInterval")
    def poll_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pollInterval"))

    @poll_interval.setter
    def poll_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "poll_interval").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollInterval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="solutionStackName")
    def solution_stack_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "solutionStackName"))

    @solution_stack_name.setter
    def solution_stack_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "solution_stack_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "solutionStackName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateName")
    def template_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateName"))

    @template_name.setter
    def template_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "template_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "templateName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tier")
    def tier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tier"))

    @tier.setter
    def tier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "tier").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionLabel")
    def version_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionLabel"))

    @version_label.setter
    def version_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "version_label").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "versionLabel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitForReadyTimeout")
    def wait_for_ready_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "waitForReadyTimeout"))

    @wait_for_ready_timeout.setter
    def wait_for_ready_timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironment, "wait_for_ready_timeout").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waitForReadyTimeout", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkEnvironmentAllSettings",
    jsii_struct_bases=[],
    name_mapping={},
)
class ElasticBeanstalkEnvironmentAllSettings:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticBeanstalkEnvironmentAllSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticBeanstalkEnvironmentAllSettingsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkEnvironmentAllSettingsList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkEnvironmentAllSettingsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElasticBeanstalkEnvironmentAllSettingsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkEnvironmentAllSettingsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElasticBeanstalkEnvironmentAllSettingsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentAllSettingsList, "_terraform_attribute").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentAllSettingsList, "_terraform_resource").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentAllSettingsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class ElasticBeanstalkEnvironmentAllSettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkEnvironmentAllSettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkEnvironmentAllSettingsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElasticBeanstalkEnvironmentAllSettings]:
        return typing.cast(typing.Optional[ElasticBeanstalkEnvironmentAllSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElasticBeanstalkEnvironmentAllSettings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentAllSettingsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkEnvironmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "application": "application",
        "name": "name",
        "cname_prefix": "cnamePrefix",
        "description": "description",
        "id": "id",
        "platform_arn": "platformArn",
        "poll_interval": "pollInterval",
        "setting": "setting",
        "solution_stack_name": "solutionStackName",
        "tags": "tags",
        "tags_all": "tagsAll",
        "template_name": "templateName",
        "tier": "tier",
        "version_label": "versionLabel",
        "wait_for_ready_timeout": "waitForReadyTimeout",
    },
)
class ElasticBeanstalkEnvironmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
        application: builtins.str,
        name: builtins.str,
        cname_prefix: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        platform_arn: typing.Optional[builtins.str] = None,
        poll_interval: typing.Optional[builtins.str] = None,
        setting: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ElasticBeanstalkEnvironmentSetting", typing.Dict[str, typing.Any]]]]] = None,
        solution_stack_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        template_name: typing.Optional[builtins.str] = None,
        tier: typing.Optional[builtins.str] = None,
        version_label: typing.Optional[builtins.str] = None,
        wait_for_ready_timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Elastic Beanstalk.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param application: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#application ElasticBeanstalkEnvironment#application}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#name ElasticBeanstalkEnvironment#name}.
        :param cname_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#cname_prefix ElasticBeanstalkEnvironment#cname_prefix}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#description ElasticBeanstalkEnvironment#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#id ElasticBeanstalkEnvironment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param platform_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#platform_arn ElasticBeanstalkEnvironment#platform_arn}.
        :param poll_interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#poll_interval ElasticBeanstalkEnvironment#poll_interval}.
        :param setting: setting block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#setting ElasticBeanstalkEnvironment#setting}
        :param solution_stack_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#solution_stack_name ElasticBeanstalkEnvironment#solution_stack_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#tags ElasticBeanstalkEnvironment#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#tags_all ElasticBeanstalkEnvironment#tags_all}.
        :param template_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#template_name ElasticBeanstalkEnvironment#template_name}.
        :param tier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#tier ElasticBeanstalkEnvironment#tier}.
        :param version_label: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#version_label ElasticBeanstalkEnvironment#version_label}.
        :param wait_for_ready_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#wait_for_ready_timeout ElasticBeanstalkEnvironment#wait_for_ready_timeout}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkEnvironmentConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument cname_prefix", value=cname_prefix, expected_type=type_hints["cname_prefix"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument platform_arn", value=platform_arn, expected_type=type_hints["platform_arn"])
            check_type(argname="argument poll_interval", value=poll_interval, expected_type=type_hints["poll_interval"])
            check_type(argname="argument setting", value=setting, expected_type=type_hints["setting"])
            check_type(argname="argument solution_stack_name", value=solution_stack_name, expected_type=type_hints["solution_stack_name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
            check_type(argname="argument template_name", value=template_name, expected_type=type_hints["template_name"])
            check_type(argname="argument tier", value=tier, expected_type=type_hints["tier"])
            check_type(argname="argument version_label", value=version_label, expected_type=type_hints["version_label"])
            check_type(argname="argument wait_for_ready_timeout", value=wait_for_ready_timeout, expected_type=type_hints["wait_for_ready_timeout"])
        self._values: typing.Dict[str, typing.Any] = {
            "application": application,
            "name": name,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if cname_prefix is not None:
            self._values["cname_prefix"] = cname_prefix
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if platform_arn is not None:
            self._values["platform_arn"] = platform_arn
        if poll_interval is not None:
            self._values["poll_interval"] = poll_interval
        if setting is not None:
            self._values["setting"] = setting
        if solution_stack_name is not None:
            self._values["solution_stack_name"] = solution_stack_name
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if template_name is not None:
            self._values["template_name"] = template_name
        if tier is not None:
            self._values["tier"] = tier
        if version_label is not None:
            self._values["version_label"] = version_label
        if wait_for_ready_timeout is not None:
            self._values["wait_for_ready_timeout"] = wait_for_ready_timeout

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[cdktf.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[cdktf.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]], result)

    @builtins.property
    def application(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#application ElasticBeanstalkEnvironment#application}.'''
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#name ElasticBeanstalkEnvironment#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cname_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#cname_prefix ElasticBeanstalkEnvironment#cname_prefix}.'''
        result = self._values.get("cname_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#description ElasticBeanstalkEnvironment#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#id ElasticBeanstalkEnvironment#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def platform_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#platform_arn ElasticBeanstalkEnvironment#platform_arn}.'''
        result = self._values.get("platform_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def poll_interval(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#poll_interval ElasticBeanstalkEnvironment#poll_interval}.'''
        result = self._values.get("poll_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def setting(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ElasticBeanstalkEnvironmentSetting"]]]:
        '''setting block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#setting ElasticBeanstalkEnvironment#setting}
        '''
        result = self._values.get("setting")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ElasticBeanstalkEnvironmentSetting"]]], result)

    @builtins.property
    def solution_stack_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#solution_stack_name ElasticBeanstalkEnvironment#solution_stack_name}.'''
        result = self._values.get("solution_stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#tags ElasticBeanstalkEnvironment#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#tags_all ElasticBeanstalkEnvironment#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def template_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#template_name ElasticBeanstalkEnvironment#template_name}.'''
        result = self._values.get("template_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#tier ElasticBeanstalkEnvironment#tier}.'''
        result = self._values.get("tier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#version_label ElasticBeanstalkEnvironment#version_label}.'''
        result = self._values.get("version_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wait_for_ready_timeout(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#wait_for_ready_timeout ElasticBeanstalkEnvironment#wait_for_ready_timeout}.'''
        result = self._values.get("wait_for_ready_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticBeanstalkEnvironmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkEnvironmentSetting",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "namespace": "namespace",
        "value": "value",
        "resource": "resource",
    },
)
class ElasticBeanstalkEnvironmentSetting:
    def __init__(
        self,
        *,
        name: builtins.str,
        namespace: builtins.str,
        value: builtins.str,
        resource: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#name ElasticBeanstalkEnvironment#name}.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#namespace ElasticBeanstalkEnvironment#namespace}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#value ElasticBeanstalkEnvironment#value}.
        :param resource: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#resource ElasticBeanstalkEnvironment#resource}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkEnvironmentSetting.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "namespace": namespace,
            "value": value,
        }
        if resource is not None:
            self._values["resource"] = resource

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#name ElasticBeanstalkEnvironment#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#namespace ElasticBeanstalkEnvironment#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#value ElasticBeanstalkEnvironment#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elastic_beanstalk_environment#resource ElasticBeanstalkEnvironment#resource}.'''
        result = self._values.get("resource")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticBeanstalkEnvironmentSetting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticBeanstalkEnvironmentSettingList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkEnvironmentSettingList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkEnvironmentSettingList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElasticBeanstalkEnvironmentSettingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkEnvironmentSettingList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElasticBeanstalkEnvironmentSettingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentSettingList, "_terraform_attribute").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentSettingList, "_terraform_resource").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentSettingList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ElasticBeanstalkEnvironmentSetting]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ElasticBeanstalkEnvironmentSetting]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ElasticBeanstalkEnvironmentSetting]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentSettingList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ElasticBeanstalkEnvironmentSettingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticbeanstalk.ElasticBeanstalkEnvironmentSettingOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ElasticBeanstalkEnvironmentSettingOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetResource")
    def reset_resource(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResource", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceInput")
    def resource_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentSettingOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentSettingOutputReference, "namespace").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resource"))

    @resource.setter
    def resource(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentSettingOutputReference, "resource").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentSettingOutputReference, "value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ElasticBeanstalkEnvironmentSetting, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ElasticBeanstalkEnvironmentSetting, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ElasticBeanstalkEnvironmentSetting, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ElasticBeanstalkEnvironmentSettingOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsElasticBeanstalkApplication",
    "DataAwsElasticBeanstalkApplicationAppversionLifecycle",
    "DataAwsElasticBeanstalkApplicationAppversionLifecycleList",
    "DataAwsElasticBeanstalkApplicationAppversionLifecycleOutputReference",
    "DataAwsElasticBeanstalkApplicationConfig",
    "DataAwsElasticBeanstalkHostedZone",
    "DataAwsElasticBeanstalkHostedZoneConfig",
    "DataAwsElasticBeanstalkSolutionStack",
    "DataAwsElasticBeanstalkSolutionStackConfig",
    "ElasticBeanstalkApplication",
    "ElasticBeanstalkApplicationAppversionLifecycle",
    "ElasticBeanstalkApplicationAppversionLifecycleOutputReference",
    "ElasticBeanstalkApplicationConfig",
    "ElasticBeanstalkApplicationVersion",
    "ElasticBeanstalkApplicationVersionConfig",
    "ElasticBeanstalkConfigurationTemplate",
    "ElasticBeanstalkConfigurationTemplateConfig",
    "ElasticBeanstalkConfigurationTemplateSetting",
    "ElasticBeanstalkConfigurationTemplateSettingList",
    "ElasticBeanstalkConfigurationTemplateSettingOutputReference",
    "ElasticBeanstalkEnvironment",
    "ElasticBeanstalkEnvironmentAllSettings",
    "ElasticBeanstalkEnvironmentAllSettingsList",
    "ElasticBeanstalkEnvironmentAllSettingsOutputReference",
    "ElasticBeanstalkEnvironmentConfig",
    "ElasticBeanstalkEnvironmentSetting",
    "ElasticBeanstalkEnvironmentSettingList",
    "ElasticBeanstalkEnvironmentSettingOutputReference",
]

publication.publish()
