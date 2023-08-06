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


class DataAwsServicequotasService(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicequotas.DataAwsServicequotasService",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service aws_servicequotas_service}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        service_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service aws_servicequotas_service} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param service_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service#service_name DataAwsServicequotasService#service_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service#id DataAwsServicequotasService#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsServicequotasService.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsServicequotasServiceConfig(
            service_name=service_name,
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
    @jsii.member(jsii_name="serviceCode")
    def service_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceCode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceNameInput")
    def service_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsServicequotasService, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @service_name.setter
    def service_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsServicequotasService, "service_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.servicequotas.DataAwsServicequotasServiceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "service_name": "serviceName",
        "id": "id",
    },
)
class DataAwsServicequotasServiceConfig(cdktf.TerraformMetaArguments):
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
        service_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Service Quotas.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param service_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service#service_name DataAwsServicequotasService#service_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service#id DataAwsServicequotasService#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsServicequotasServiceConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "service_name": service_name,
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
    def service_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service#service_name DataAwsServicequotasService#service_name}.'''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service#id DataAwsServicequotasService#id}.

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
        return "DataAwsServicequotasServiceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsServicequotasServiceQuota(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicequotas.DataAwsServicequotasServiceQuota",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota aws_servicequotas_service_quota}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        service_code: builtins.str,
        id: typing.Optional[builtins.str] = None,
        quota_code: typing.Optional[builtins.str] = None,
        quota_name: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota aws_servicequotas_service_quota} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param service_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#service_code DataAwsServicequotasServiceQuota#service_code}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#id DataAwsServicequotasServiceQuota#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param quota_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#quota_code DataAwsServicequotasServiceQuota#quota_code}.
        :param quota_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#quota_name DataAwsServicequotasServiceQuota#quota_name}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsServicequotasServiceQuota.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsServicequotasServiceQuotaConfig(
            service_code=service_code,
            id=id,
            quota_code=quota_code,
            quota_name=quota_name,
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

    @jsii.member(jsii_name="resetQuotaCode")
    def reset_quota_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuotaCode", []))

    @jsii.member(jsii_name="resetQuotaName")
    def reset_quota_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuotaName", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adjustable")
    def adjustable(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "adjustable"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultValue")
    def default_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalQuota")
    def global_quota(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "globalQuota"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="quotaCodeInput")
    def quota_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "quotaCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="quotaNameInput")
    def quota_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "quotaNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceCodeInput")
    def service_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsServicequotasServiceQuota, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="quotaCode")
    def quota_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quotaCode"))

    @quota_code.setter
    def quota_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsServicequotasServiceQuota, "quota_code").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quotaCode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="quotaName")
    def quota_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quotaName"))

    @quota_name.setter
    def quota_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsServicequotasServiceQuota, "quota_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quotaName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceCode")
    def service_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceCode"))

    @service_code.setter
    def service_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsServicequotasServiceQuota, "service_code").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceCode", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.servicequotas.DataAwsServicequotasServiceQuotaConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "service_code": "serviceCode",
        "id": "id",
        "quota_code": "quotaCode",
        "quota_name": "quotaName",
    },
)
class DataAwsServicequotasServiceQuotaConfig(cdktf.TerraformMetaArguments):
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
        service_code: builtins.str,
        id: typing.Optional[builtins.str] = None,
        quota_code: typing.Optional[builtins.str] = None,
        quota_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Service Quotas.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param service_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#service_code DataAwsServicequotasServiceQuota#service_code}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#id DataAwsServicequotasServiceQuota#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param quota_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#quota_code DataAwsServicequotasServiceQuota#quota_code}.
        :param quota_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#quota_name DataAwsServicequotasServiceQuota#quota_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsServicequotasServiceQuotaConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument service_code", value=service_code, expected_type=type_hints["service_code"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument quota_code", value=quota_code, expected_type=type_hints["quota_code"])
            check_type(argname="argument quota_name", value=quota_name, expected_type=type_hints["quota_name"])
        self._values: typing.Dict[str, typing.Any] = {
            "service_code": service_code,
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
        if quota_code is not None:
            self._values["quota_code"] = quota_code
        if quota_name is not None:
            self._values["quota_name"] = quota_name

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
    def service_code(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#service_code DataAwsServicequotasServiceQuota#service_code}.'''
        result = self._values.get("service_code")
        assert result is not None, "Required property 'service_code' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#id DataAwsServicequotasServiceQuota#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def quota_code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#quota_code DataAwsServicequotasServiceQuota#quota_code}.'''
        result = self._values.get("quota_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def quota_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/servicequotas_service_quota#quota_name DataAwsServicequotasServiceQuota#quota_name}.'''
        result = self._values.get("quota_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsServicequotasServiceQuotaConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServicequotasServiceQuota(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicequotas.ServicequotasServiceQuota",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota aws_servicequotas_service_quota}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        quota_code: builtins.str,
        service_code: builtins.str,
        value: jsii.Number,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota aws_servicequotas_service_quota} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param quota_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#quota_code ServicequotasServiceQuota#quota_code}.
        :param service_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#service_code ServicequotasServiceQuota#service_code}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#value ServicequotasServiceQuota#value}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#id ServicequotasServiceQuota#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ServicequotasServiceQuota.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ServicequotasServiceQuotaConfig(
            quota_code=quota_code,
            service_code=service_code,
            value=value,
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
    @jsii.member(jsii_name="adjustable")
    def adjustable(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "adjustable"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultValue")
    def default_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="quotaName")
    def quota_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quotaName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestId")
    def request_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestStatus")
    def request_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="quotaCodeInput")
    def quota_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "quotaCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceCodeInput")
    def service_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ServicequotasServiceQuota, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="quotaCode")
    def quota_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quotaCode"))

    @quota_code.setter
    def quota_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ServicequotasServiceQuota, "quota_code").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quotaCode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceCode")
    def service_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceCode"))

    @service_code.setter
    def service_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ServicequotasServiceQuota, "service_code").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceCode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ServicequotasServiceQuota, "value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.servicequotas.ServicequotasServiceQuotaConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "quota_code": "quotaCode",
        "service_code": "serviceCode",
        "value": "value",
        "id": "id",
    },
)
class ServicequotasServiceQuotaConfig(cdktf.TerraformMetaArguments):
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
        quota_code: builtins.str,
        service_code: builtins.str,
        value: jsii.Number,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Service Quotas.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param quota_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#quota_code ServicequotasServiceQuota#quota_code}.
        :param service_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#service_code ServicequotasServiceQuota#service_code}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#value ServicequotasServiceQuota#value}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#id ServicequotasServiceQuota#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(ServicequotasServiceQuotaConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument quota_code", value=quota_code, expected_type=type_hints["quota_code"])
            check_type(argname="argument service_code", value=service_code, expected_type=type_hints["service_code"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "quota_code": quota_code,
            "service_code": service_code,
            "value": value,
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
    def quota_code(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#quota_code ServicequotasServiceQuota#quota_code}.'''
        result = self._values.get("quota_code")
        assert result is not None, "Required property 'quota_code' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_code(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#service_code ServicequotasServiceQuota#service_code}.'''
        result = self._values.get("service_code")
        assert result is not None, "Required property 'service_code' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#value ServicequotasServiceQuota#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/servicequotas_service_quota#id ServicequotasServiceQuota#id}.

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
        return "ServicequotasServiceQuotaConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsServicequotasService",
    "DataAwsServicequotasServiceConfig",
    "DataAwsServicequotasServiceQuota",
    "DataAwsServicequotasServiceQuotaConfig",
    "ServicequotasServiceQuota",
    "ServicequotasServiceQuotaConfig",
]

publication.publish()
