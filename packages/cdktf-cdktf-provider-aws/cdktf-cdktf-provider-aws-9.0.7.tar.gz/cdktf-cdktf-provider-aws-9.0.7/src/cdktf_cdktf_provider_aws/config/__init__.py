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


class ConfigAggregateAuthorization(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigAggregateAuthorization",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization aws_config_aggregate_authorization}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        account_id: builtins.str,
        region: builtins.str,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization aws_config_aggregate_authorization} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#account_id ConfigAggregateAuthorization#account_id}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#region ConfigAggregateAuthorization#region}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#id ConfigAggregateAuthorization#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#tags ConfigAggregateAuthorization#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#tags_all ConfigAggregateAuthorization#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigAggregateAuthorization.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigAggregateAuthorizationConfig(
            account_id=account_id,
            region=region,
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
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigAggregateAuthorization, "account_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigAggregateAuthorization, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigAggregateAuthorization, "region").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigAggregateAuthorization, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigAggregateAuthorization, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigAggregateAuthorizationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_id": "accountId",
        "region": "region",
        "id": "id",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ConfigAggregateAuthorizationConfig(cdktf.TerraformMetaArguments):
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
        account_id: builtins.str,
        region: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#account_id ConfigAggregateAuthorization#account_id}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#region ConfigAggregateAuthorization#region}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#id ConfigAggregateAuthorization#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#tags ConfigAggregateAuthorization#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#tags_all ConfigAggregateAuthorization#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigAggregateAuthorizationConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "region": region,
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
    def account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#account_id ConfigAggregateAuthorization#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#region ConfigAggregateAuthorization#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#id ConfigAggregateAuthorization#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#tags ConfigAggregateAuthorization#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_aggregate_authorization#tags_all ConfigAggregateAuthorization#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigAggregateAuthorizationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigConfigRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule aws_config_config_rule}.'''

    def __init__(
        self,
        scope_: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        source: typing.Union["ConfigConfigRuleSource", typing.Dict[str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[builtins.str] = None,
        maximum_execution_frequency: typing.Optional[builtins.str] = None,
        scope: typing.Optional[typing.Union["ConfigConfigRuleScope", typing.Dict[str, typing.Any]]] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule aws_config_config_rule} Resource.

        :param scope_: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#name ConfigConfigRule#name}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#source ConfigConfigRule#source}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#description ConfigConfigRule#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#id ConfigConfigRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#input_parameters ConfigConfigRule#input_parameters}.
        :param maximum_execution_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#maximum_execution_frequency ConfigConfigRule#maximum_execution_frequency}.
        :param scope: scope block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#scope ConfigConfigRule#scope}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tags ConfigConfigRule#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tags_all ConfigConfigRule#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigRule.__init__)
            check_type(argname="argument scope_", value=scope_, expected_type=type_hints["scope_"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigConfigRuleConfig(
            name=name,
            source=source,
            description=description,
            id=id,
            input_parameters=input_parameters,
            maximum_execution_frequency=maximum_execution_frequency,
            scope=scope,
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

        jsii.create(self.__class__, self, [scope_, id_, config])

    @jsii.member(jsii_name="putScope")
    def put_scope(
        self,
        *,
        compliance_resource_id: typing.Optional[builtins.str] = None,
        compliance_resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        tag_key: typing.Optional[builtins.str] = None,
        tag_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param compliance_resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#compliance_resource_id ConfigConfigRule#compliance_resource_id}.
        :param compliance_resource_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#compliance_resource_types ConfigConfigRule#compliance_resource_types}.
        :param tag_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tag_key ConfigConfigRule#tag_key}.
        :param tag_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tag_value ConfigConfigRule#tag_value}.
        '''
        value = ConfigConfigRuleScope(
            compliance_resource_id=compliance_resource_id,
            compliance_resource_types=compliance_resource_types,
            tag_key=tag_key,
            tag_value=tag_value,
        )

        return typing.cast(None, jsii.invoke(self, "putScope", [value]))

    @jsii.member(jsii_name="putSource")
    def put_source(
        self,
        *,
        owner: builtins.str,
        custom_policy_details: typing.Optional[typing.Union["ConfigConfigRuleSourceCustomPolicyDetails", typing.Dict[str, typing.Any]]] = None,
        source_detail: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigConfigRuleSourceSourceDetail", typing.Dict[str, typing.Any]]]]] = None,
        source_identifier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#owner ConfigConfigRule#owner}.
        :param custom_policy_details: custom_policy_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#custom_policy_details ConfigConfigRule#custom_policy_details}
        :param source_detail: source_detail block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#source_detail ConfigConfigRule#source_detail}
        :param source_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#source_identifier ConfigConfigRule#source_identifier}.
        '''
        value = ConfigConfigRuleSource(
            owner=owner,
            custom_policy_details=custom_policy_details,
            source_detail=source_detail,
            source_identifier=source_identifier,
        )

        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInputParameters")
    def reset_input_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInputParameters", []))

    @jsii.member(jsii_name="resetMaximumExecutionFrequency")
    def reset_maximum_execution_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumExecutionFrequency", []))

    @jsii.member(jsii_name="resetScope")
    def reset_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScope", []))

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
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> "ConfigConfigRuleScopeOutputReference":
        return typing.cast("ConfigConfigRuleScopeOutputReference", jsii.get(self, "scope"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> "ConfigConfigRuleSourceOutputReference":
        return typing.cast("ConfigConfigRuleSourceOutputReference", jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputParametersInput")
    def input_parameters_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumExecutionFrequencyInput")
    def maximum_execution_frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maximumExecutionFrequencyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeInput")
    def scope_input(self) -> typing.Optional["ConfigConfigRuleScope"]:
        return typing.cast(typing.Optional["ConfigConfigRuleScope"], jsii.get(self, "scopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional["ConfigConfigRuleSource"]:
        return typing.cast(typing.Optional["ConfigConfigRuleSource"], jsii.get(self, "sourceInput"))

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
            type_hints = typing.get_type_hints(getattr(ConfigConfigRule, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRule, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputParameters")
    def input_parameters(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inputParameters"))

    @input_parameters.setter
    def input_parameters(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRule, "input_parameters").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumExecutionFrequency")
    def maximum_execution_frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maximumExecutionFrequency"))

    @maximum_execution_frequency.setter
    def maximum_execution_frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRule, "maximum_execution_frequency").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximumExecutionFrequency", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRule, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRule, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRule, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRuleConfig",
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
        "source": "source",
        "description": "description",
        "id": "id",
        "input_parameters": "inputParameters",
        "maximum_execution_frequency": "maximumExecutionFrequency",
        "scope": "scope",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ConfigConfigRuleConfig(cdktf.TerraformMetaArguments):
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
        source: typing.Union["ConfigConfigRuleSource", typing.Dict[str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[builtins.str] = None,
        maximum_execution_frequency: typing.Optional[builtins.str] = None,
        scope: typing.Optional[typing.Union["ConfigConfigRuleScope", typing.Dict[str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#name ConfigConfigRule#name}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#source ConfigConfigRule#source}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#description ConfigConfigRule#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#id ConfigConfigRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#input_parameters ConfigConfigRule#input_parameters}.
        :param maximum_execution_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#maximum_execution_frequency ConfigConfigRule#maximum_execution_frequency}.
        :param scope: scope block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#scope ConfigConfigRule#scope}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tags ConfigConfigRule#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tags_all ConfigConfigRule#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(source, dict):
            source = ConfigConfigRuleSource(**source)
        if isinstance(scope, dict):
            scope = ConfigConfigRuleScope(**scope)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigRuleConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument input_parameters", value=input_parameters, expected_type=type_hints["input_parameters"])
            check_type(argname="argument maximum_execution_frequency", value=maximum_execution_frequency, expected_type=type_hints["maximum_execution_frequency"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "source": source,
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
        if id is not None:
            self._values["id"] = id
        if input_parameters is not None:
            self._values["input_parameters"] = input_parameters
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency
        if scope is not None:
            self._values["scope"] = scope
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#name ConfigConfigRule#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source(self) -> "ConfigConfigRuleSource":
        '''source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#source ConfigConfigRule#source}
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast("ConfigConfigRuleSource", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#description ConfigConfigRule#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#id ConfigConfigRule#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_parameters(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#input_parameters ConfigConfigRule#input_parameters}.'''
        result = self._values.get("input_parameters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#maximum_execution_frequency ConfigConfigRule#maximum_execution_frequency}.'''
        result = self._values.get("maximum_execution_frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scope(self) -> typing.Optional["ConfigConfigRuleScope"]:
        '''scope block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#scope ConfigConfigRule#scope}
        '''
        result = self._values.get("scope")
        return typing.cast(typing.Optional["ConfigConfigRuleScope"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tags ConfigConfigRule#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tags_all ConfigConfigRule#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfigRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRuleScope",
    jsii_struct_bases=[],
    name_mapping={
        "compliance_resource_id": "complianceResourceId",
        "compliance_resource_types": "complianceResourceTypes",
        "tag_key": "tagKey",
        "tag_value": "tagValue",
    },
)
class ConfigConfigRuleScope:
    def __init__(
        self,
        *,
        compliance_resource_id: typing.Optional[builtins.str] = None,
        compliance_resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        tag_key: typing.Optional[builtins.str] = None,
        tag_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param compliance_resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#compliance_resource_id ConfigConfigRule#compliance_resource_id}.
        :param compliance_resource_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#compliance_resource_types ConfigConfigRule#compliance_resource_types}.
        :param tag_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tag_key ConfigConfigRule#tag_key}.
        :param tag_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tag_value ConfigConfigRule#tag_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigRuleScope.__init__)
            check_type(argname="argument compliance_resource_id", value=compliance_resource_id, expected_type=type_hints["compliance_resource_id"])
            check_type(argname="argument compliance_resource_types", value=compliance_resource_types, expected_type=type_hints["compliance_resource_types"])
            check_type(argname="argument tag_key", value=tag_key, expected_type=type_hints["tag_key"])
            check_type(argname="argument tag_value", value=tag_value, expected_type=type_hints["tag_value"])
        self._values: typing.Dict[str, typing.Any] = {}
        if compliance_resource_id is not None:
            self._values["compliance_resource_id"] = compliance_resource_id
        if compliance_resource_types is not None:
            self._values["compliance_resource_types"] = compliance_resource_types
        if tag_key is not None:
            self._values["tag_key"] = tag_key
        if tag_value is not None:
            self._values["tag_value"] = tag_value

    @builtins.property
    def compliance_resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#compliance_resource_id ConfigConfigRule#compliance_resource_id}.'''
        result = self._values.get("compliance_resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compliance_resource_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#compliance_resource_types ConfigConfigRule#compliance_resource_types}.'''
        result = self._values.get("compliance_resource_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tag_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tag_key ConfigConfigRule#tag_key}.'''
        result = self._values.get("tag_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#tag_value ConfigConfigRule#tag_value}.'''
        result = self._values.get("tag_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfigRuleScope(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigConfigRuleScopeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRuleScopeOutputReference",
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
            type_hints = typing.get_type_hints(ConfigConfigRuleScopeOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetComplianceResourceId")
    def reset_compliance_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComplianceResourceId", []))

    @jsii.member(jsii_name="resetComplianceResourceTypes")
    def reset_compliance_resource_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComplianceResourceTypes", []))

    @jsii.member(jsii_name="resetTagKey")
    def reset_tag_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagKey", []))

    @jsii.member(jsii_name="resetTagValue")
    def reset_tag_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="complianceResourceIdInput")
    def compliance_resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "complianceResourceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="complianceResourceTypesInput")
    def compliance_resource_types_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "complianceResourceTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagKeyInput")
    def tag_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagValueInput")
    def tag_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="complianceResourceId")
    def compliance_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "complianceResourceId"))

    @compliance_resource_id.setter
    def compliance_resource_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleScopeOutputReference, "compliance_resource_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "complianceResourceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="complianceResourceTypes")
    def compliance_resource_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "complianceResourceTypes"))

    @compliance_resource_types.setter
    def compliance_resource_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleScopeOutputReference, "compliance_resource_types").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "complianceResourceTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagKey")
    def tag_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagKey"))

    @tag_key.setter
    def tag_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleScopeOutputReference, "tag_key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagValue")
    def tag_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagValue"))

    @tag_value.setter
    def tag_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleScopeOutputReference, "tag_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ConfigConfigRuleScope]:
        return typing.cast(typing.Optional[ConfigConfigRuleScope], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ConfigConfigRuleScope]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleScopeOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRuleSource",
    jsii_struct_bases=[],
    name_mapping={
        "owner": "owner",
        "custom_policy_details": "customPolicyDetails",
        "source_detail": "sourceDetail",
        "source_identifier": "sourceIdentifier",
    },
)
class ConfigConfigRuleSource:
    def __init__(
        self,
        *,
        owner: builtins.str,
        custom_policy_details: typing.Optional[typing.Union["ConfigConfigRuleSourceCustomPolicyDetails", typing.Dict[str, typing.Any]]] = None,
        source_detail: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigConfigRuleSourceSourceDetail", typing.Dict[str, typing.Any]]]]] = None,
        source_identifier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#owner ConfigConfigRule#owner}.
        :param custom_policy_details: custom_policy_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#custom_policy_details ConfigConfigRule#custom_policy_details}
        :param source_detail: source_detail block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#source_detail ConfigConfigRule#source_detail}
        :param source_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#source_identifier ConfigConfigRule#source_identifier}.
        '''
        if isinstance(custom_policy_details, dict):
            custom_policy_details = ConfigConfigRuleSourceCustomPolicyDetails(**custom_policy_details)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigRuleSource.__init__)
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument custom_policy_details", value=custom_policy_details, expected_type=type_hints["custom_policy_details"])
            check_type(argname="argument source_detail", value=source_detail, expected_type=type_hints["source_detail"])
            check_type(argname="argument source_identifier", value=source_identifier, expected_type=type_hints["source_identifier"])
        self._values: typing.Dict[str, typing.Any] = {
            "owner": owner,
        }
        if custom_policy_details is not None:
            self._values["custom_policy_details"] = custom_policy_details
        if source_detail is not None:
            self._values["source_detail"] = source_detail
        if source_identifier is not None:
            self._values["source_identifier"] = source_identifier

    @builtins.property
    def owner(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#owner ConfigConfigRule#owner}.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_policy_details(
        self,
    ) -> typing.Optional["ConfigConfigRuleSourceCustomPolicyDetails"]:
        '''custom_policy_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#custom_policy_details ConfigConfigRule#custom_policy_details}
        '''
        result = self._values.get("custom_policy_details")
        return typing.cast(typing.Optional["ConfigConfigRuleSourceCustomPolicyDetails"], result)

    @builtins.property
    def source_detail(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigConfigRuleSourceSourceDetail"]]]:
        '''source_detail block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#source_detail ConfigConfigRule#source_detail}
        '''
        result = self._values.get("source_detail")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigConfigRuleSourceSourceDetail"]]], result)

    @builtins.property
    def source_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#source_identifier ConfigConfigRule#source_identifier}.'''
        result = self._values.get("source_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfigRuleSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRuleSourceCustomPolicyDetails",
    jsii_struct_bases=[],
    name_mapping={
        "policy_runtime": "policyRuntime",
        "policy_text": "policyText",
        "enable_debug_log_delivery": "enableDebugLogDelivery",
    },
)
class ConfigConfigRuleSourceCustomPolicyDetails:
    def __init__(
        self,
        *,
        policy_runtime: builtins.str,
        policy_text: builtins.str,
        enable_debug_log_delivery: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param policy_runtime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#policy_runtime ConfigConfigRule#policy_runtime}.
        :param policy_text: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#policy_text ConfigConfigRule#policy_text}.
        :param enable_debug_log_delivery: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#enable_debug_log_delivery ConfigConfigRule#enable_debug_log_delivery}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigRuleSourceCustomPolicyDetails.__init__)
            check_type(argname="argument policy_runtime", value=policy_runtime, expected_type=type_hints["policy_runtime"])
            check_type(argname="argument policy_text", value=policy_text, expected_type=type_hints["policy_text"])
            check_type(argname="argument enable_debug_log_delivery", value=enable_debug_log_delivery, expected_type=type_hints["enable_debug_log_delivery"])
        self._values: typing.Dict[str, typing.Any] = {
            "policy_runtime": policy_runtime,
            "policy_text": policy_text,
        }
        if enable_debug_log_delivery is not None:
            self._values["enable_debug_log_delivery"] = enable_debug_log_delivery

    @builtins.property
    def policy_runtime(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#policy_runtime ConfigConfigRule#policy_runtime}.'''
        result = self._values.get("policy_runtime")
        assert result is not None, "Required property 'policy_runtime' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_text(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#policy_text ConfigConfigRule#policy_text}.'''
        result = self._values.get("policy_text")
        assert result is not None, "Required property 'policy_text' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enable_debug_log_delivery(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#enable_debug_log_delivery ConfigConfigRule#enable_debug_log_delivery}.'''
        result = self._values.get("enable_debug_log_delivery")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfigRuleSourceCustomPolicyDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigConfigRuleSourceCustomPolicyDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRuleSourceCustomPolicyDetailsOutputReference",
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
            type_hints = typing.get_type_hints(ConfigConfigRuleSourceCustomPolicyDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnableDebugLogDelivery")
    def reset_enable_debug_log_delivery(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableDebugLogDelivery", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableDebugLogDeliveryInput")
    def enable_debug_log_delivery_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableDebugLogDeliveryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyRuntimeInput")
    def policy_runtime_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyRuntimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyTextInput")
    def policy_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyTextInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableDebugLogDelivery")
    def enable_debug_log_delivery(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableDebugLogDelivery"))

    @enable_debug_log_delivery.setter
    def enable_debug_log_delivery(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceCustomPolicyDetailsOutputReference, "enable_debug_log_delivery").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableDebugLogDelivery", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyRuntime")
    def policy_runtime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyRuntime"))

    @policy_runtime.setter
    def policy_runtime(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceCustomPolicyDetailsOutputReference, "policy_runtime").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyRuntime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyText")
    def policy_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyText"))

    @policy_text.setter
    def policy_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceCustomPolicyDetailsOutputReference, "policy_text").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyText", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigConfigRuleSourceCustomPolicyDetails]:
        return typing.cast(typing.Optional[ConfigConfigRuleSourceCustomPolicyDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigConfigRuleSourceCustomPolicyDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceCustomPolicyDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigConfigRuleSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRuleSourceOutputReference",
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
            type_hints = typing.get_type_hints(ConfigConfigRuleSourceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCustomPolicyDetails")
    def put_custom_policy_details(
        self,
        *,
        policy_runtime: builtins.str,
        policy_text: builtins.str,
        enable_debug_log_delivery: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param policy_runtime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#policy_runtime ConfigConfigRule#policy_runtime}.
        :param policy_text: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#policy_text ConfigConfigRule#policy_text}.
        :param enable_debug_log_delivery: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#enable_debug_log_delivery ConfigConfigRule#enable_debug_log_delivery}.
        '''
        value = ConfigConfigRuleSourceCustomPolicyDetails(
            policy_runtime=policy_runtime,
            policy_text=policy_text,
            enable_debug_log_delivery=enable_debug_log_delivery,
        )

        return typing.cast(None, jsii.invoke(self, "putCustomPolicyDetails", [value]))

    @jsii.member(jsii_name="putSourceDetail")
    def put_source_detail(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigConfigRuleSourceSourceDetail", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigRuleSourceOutputReference.put_source_detail)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSourceDetail", [value]))

    @jsii.member(jsii_name="resetCustomPolicyDetails")
    def reset_custom_policy_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomPolicyDetails", []))

    @jsii.member(jsii_name="resetSourceDetail")
    def reset_source_detail(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceDetail", []))

    @jsii.member(jsii_name="resetSourceIdentifier")
    def reset_source_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceIdentifier", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customPolicyDetails")
    def custom_policy_details(
        self,
    ) -> ConfigConfigRuleSourceCustomPolicyDetailsOutputReference:
        return typing.cast(ConfigConfigRuleSourceCustomPolicyDetailsOutputReference, jsii.get(self, "customPolicyDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDetail")
    def source_detail(self) -> "ConfigConfigRuleSourceSourceDetailList":
        return typing.cast("ConfigConfigRuleSourceSourceDetailList", jsii.get(self, "sourceDetail"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customPolicyDetailsInput")
    def custom_policy_details_input(
        self,
    ) -> typing.Optional[ConfigConfigRuleSourceCustomPolicyDetails]:
        return typing.cast(typing.Optional[ConfigConfigRuleSourceCustomPolicyDetails], jsii.get(self, "customPolicyDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDetailInput")
    def source_detail_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigConfigRuleSourceSourceDetail"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigConfigRuleSourceSourceDetail"]]], jsii.get(self, "sourceDetailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceIdentifierInput")
    def source_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceOutputReference, "owner").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "owner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceIdentifier")
    def source_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceIdentifier"))

    @source_identifier.setter
    def source_identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceOutputReference, "source_identifier").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ConfigConfigRuleSource]:
        return typing.cast(typing.Optional[ConfigConfigRuleSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ConfigConfigRuleSource]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRuleSourceSourceDetail",
    jsii_struct_bases=[],
    name_mapping={
        "event_source": "eventSource",
        "maximum_execution_frequency": "maximumExecutionFrequency",
        "message_type": "messageType",
    },
)
class ConfigConfigRuleSourceSourceDetail:
    def __init__(
        self,
        *,
        event_source: typing.Optional[builtins.str] = None,
        maximum_execution_frequency: typing.Optional[builtins.str] = None,
        message_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param event_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#event_source ConfigConfigRule#event_source}.
        :param maximum_execution_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#maximum_execution_frequency ConfigConfigRule#maximum_execution_frequency}.
        :param message_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#message_type ConfigConfigRule#message_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigRuleSourceSourceDetail.__init__)
            check_type(argname="argument event_source", value=event_source, expected_type=type_hints["event_source"])
            check_type(argname="argument maximum_execution_frequency", value=maximum_execution_frequency, expected_type=type_hints["maximum_execution_frequency"])
            check_type(argname="argument message_type", value=message_type, expected_type=type_hints["message_type"])
        self._values: typing.Dict[str, typing.Any] = {}
        if event_source is not None:
            self._values["event_source"] = event_source
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency
        if message_type is not None:
            self._values["message_type"] = message_type

    @builtins.property
    def event_source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#event_source ConfigConfigRule#event_source}.'''
        result = self._values.get("event_source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#maximum_execution_frequency ConfigConfigRule#maximum_execution_frequency}.'''
        result = self._values.get("maximum_execution_frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_config_rule#message_type ConfigConfigRule#message_type}.'''
        result = self._values.get("message_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfigRuleSourceSourceDetail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigConfigRuleSourceSourceDetailList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRuleSourceSourceDetailList",
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
            type_hints = typing.get_type_hints(ConfigConfigRuleSourceSourceDetailList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigConfigRuleSourceSourceDetailOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigRuleSourceSourceDetailList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigConfigRuleSourceSourceDetailOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceSourceDetailList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceSourceDetailList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceSourceDetailList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigConfigRuleSourceSourceDetail]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigConfigRuleSourceSourceDetail]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigConfigRuleSourceSourceDetail]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceSourceDetailList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigConfigRuleSourceSourceDetailOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigRuleSourceSourceDetailOutputReference",
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
            type_hints = typing.get_type_hints(ConfigConfigRuleSourceSourceDetailOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEventSource")
    def reset_event_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventSource", []))

    @jsii.member(jsii_name="resetMaximumExecutionFrequency")
    def reset_maximum_execution_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumExecutionFrequency", []))

    @jsii.member(jsii_name="resetMessageType")
    def reset_message_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventSourceInput")
    def event_source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumExecutionFrequencyInput")
    def maximum_execution_frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maximumExecutionFrequencyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageTypeInput")
    def message_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventSource")
    def event_source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventSource"))

    @event_source.setter
    def event_source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceSourceDetailOutputReference, "event_source").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventSource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumExecutionFrequency")
    def maximum_execution_frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maximumExecutionFrequency"))

    @maximum_execution_frequency.setter
    def maximum_execution_frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceSourceDetailOutputReference, "maximum_execution_frequency").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximumExecutionFrequency", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageType")
    def message_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageType"))

    @message_type.setter
    def message_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceSourceDetailOutputReference, "message_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ConfigConfigRuleSourceSourceDetail, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ConfigConfigRuleSourceSourceDetail, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ConfigConfigRuleSourceSourceDetail, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigRuleSourceSourceDetailOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigConfigurationAggregator(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationAggregator",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator aws_config_configuration_aggregator}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        account_aggregation_source: typing.Optional[typing.Union["ConfigConfigurationAggregatorAccountAggregationSource", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        organization_aggregation_source: typing.Optional[typing.Union["ConfigConfigurationAggregatorOrganizationAggregationSource", typing.Dict[str, typing.Any]]] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator aws_config_configuration_aggregator} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#name ConfigConfigurationAggregator#name}.
        :param account_aggregation_source: account_aggregation_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#account_aggregation_source ConfigConfigurationAggregator#account_aggregation_source}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#id ConfigConfigurationAggregator#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param organization_aggregation_source: organization_aggregation_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#organization_aggregation_source ConfigConfigurationAggregator#organization_aggregation_source}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#tags ConfigConfigurationAggregator#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#tags_all ConfigConfigurationAggregator#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigurationAggregator.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigConfigurationAggregatorConfig(
            name=name,
            account_aggregation_source=account_aggregation_source,
            id=id,
            organization_aggregation_source=organization_aggregation_source,
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

    @jsii.member(jsii_name="putAccountAggregationSource")
    def put_account_aggregation_source(
        self,
        *,
        account_ids: typing.Sequence[builtins.str],
        all_regions: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param account_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#account_ids ConfigConfigurationAggregator#account_ids}.
        :param all_regions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#all_regions ConfigConfigurationAggregator#all_regions}.
        :param regions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#regions ConfigConfigurationAggregator#regions}.
        '''
        value = ConfigConfigurationAggregatorAccountAggregationSource(
            account_ids=account_ids, all_regions=all_regions, regions=regions
        )

        return typing.cast(None, jsii.invoke(self, "putAccountAggregationSource", [value]))

    @jsii.member(jsii_name="putOrganizationAggregationSource")
    def put_organization_aggregation_source(
        self,
        *,
        role_arn: builtins.str,
        all_regions: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#role_arn ConfigConfigurationAggregator#role_arn}.
        :param all_regions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#all_regions ConfigConfigurationAggregator#all_regions}.
        :param regions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#regions ConfigConfigurationAggregator#regions}.
        '''
        value = ConfigConfigurationAggregatorOrganizationAggregationSource(
            role_arn=role_arn, all_regions=all_regions, regions=regions
        )

        return typing.cast(None, jsii.invoke(self, "putOrganizationAggregationSource", [value]))

    @jsii.member(jsii_name="resetAccountAggregationSource")
    def reset_account_aggregation_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountAggregationSource", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOrganizationAggregationSource")
    def reset_organization_aggregation_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationAggregationSource", []))

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
    @jsii.member(jsii_name="accountAggregationSource")
    def account_aggregation_source(
        self,
    ) -> "ConfigConfigurationAggregatorAccountAggregationSourceOutputReference":
        return typing.cast("ConfigConfigurationAggregatorAccountAggregationSourceOutputReference", jsii.get(self, "accountAggregationSource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationAggregationSource")
    def organization_aggregation_source(
        self,
    ) -> "ConfigConfigurationAggregatorOrganizationAggregationSourceOutputReference":
        return typing.cast("ConfigConfigurationAggregatorOrganizationAggregationSourceOutputReference", jsii.get(self, "organizationAggregationSource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountAggregationSourceInput")
    def account_aggregation_source_input(
        self,
    ) -> typing.Optional["ConfigConfigurationAggregatorAccountAggregationSource"]:
        return typing.cast(typing.Optional["ConfigConfigurationAggregatorAccountAggregationSource"], jsii.get(self, "accountAggregationSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationAggregationSourceInput")
    def organization_aggregation_source_input(
        self,
    ) -> typing.Optional["ConfigConfigurationAggregatorOrganizationAggregationSource"]:
        return typing.cast(typing.Optional["ConfigConfigurationAggregatorOrganizationAggregationSource"], jsii.get(self, "organizationAggregationSourceInput"))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregator, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregator, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregator, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregator, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationAggregatorAccountAggregationSource",
    jsii_struct_bases=[],
    name_mapping={
        "account_ids": "accountIds",
        "all_regions": "allRegions",
        "regions": "regions",
    },
)
class ConfigConfigurationAggregatorAccountAggregationSource:
    def __init__(
        self,
        *,
        account_ids: typing.Sequence[builtins.str],
        all_regions: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param account_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#account_ids ConfigConfigurationAggregator#account_ids}.
        :param all_regions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#all_regions ConfigConfigurationAggregator#all_regions}.
        :param regions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#regions ConfigConfigurationAggregator#regions}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigurationAggregatorAccountAggregationSource.__init__)
            check_type(argname="argument account_ids", value=account_ids, expected_type=type_hints["account_ids"])
            check_type(argname="argument all_regions", value=all_regions, expected_type=type_hints["all_regions"])
            check_type(argname="argument regions", value=regions, expected_type=type_hints["regions"])
        self._values: typing.Dict[str, typing.Any] = {
            "account_ids": account_ids,
        }
        if all_regions is not None:
            self._values["all_regions"] = all_regions
        if regions is not None:
            self._values["regions"] = regions

    @builtins.property
    def account_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#account_ids ConfigConfigurationAggregator#account_ids}.'''
        result = self._values.get("account_ids")
        assert result is not None, "Required property 'account_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def all_regions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#all_regions ConfigConfigurationAggregator#all_regions}.'''
        result = self._values.get("all_regions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#regions ConfigConfigurationAggregator#regions}.'''
        result = self._values.get("regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfigurationAggregatorAccountAggregationSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigConfigurationAggregatorAccountAggregationSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationAggregatorAccountAggregationSourceOutputReference",
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
            type_hints = typing.get_type_hints(ConfigConfigurationAggregatorAccountAggregationSourceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllRegions")
    def reset_all_regions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllRegions", []))

    @jsii.member(jsii_name="resetRegions")
    def reset_regions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegions", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdsInput")
    def account_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "accountIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allRegionsInput")
    def all_regions_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allRegionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionsInput")
    def regions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "regionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIds")
    def account_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "accountIds"))

    @account_ids.setter
    def account_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregatorAccountAggregationSourceOutputReference, "account_ids").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allRegions")
    def all_regions(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allRegions"))

    @all_regions.setter
    def all_regions(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregatorAccountAggregationSourceOutputReference, "all_regions").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allRegions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regions")
    def regions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "regions"))

    @regions.setter
    def regions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregatorAccountAggregationSourceOutputReference, "regions").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigConfigurationAggregatorAccountAggregationSource]:
        return typing.cast(typing.Optional[ConfigConfigurationAggregatorAccountAggregationSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigConfigurationAggregatorAccountAggregationSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregatorAccountAggregationSourceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationAggregatorConfig",
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
        "account_aggregation_source": "accountAggregationSource",
        "id": "id",
        "organization_aggregation_source": "organizationAggregationSource",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ConfigConfigurationAggregatorConfig(cdktf.TerraformMetaArguments):
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
        account_aggregation_source: typing.Optional[typing.Union[ConfigConfigurationAggregatorAccountAggregationSource, typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        organization_aggregation_source: typing.Optional[typing.Union["ConfigConfigurationAggregatorOrganizationAggregationSource", typing.Dict[str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#name ConfigConfigurationAggregator#name}.
        :param account_aggregation_source: account_aggregation_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#account_aggregation_source ConfigConfigurationAggregator#account_aggregation_source}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#id ConfigConfigurationAggregator#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param organization_aggregation_source: organization_aggregation_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#organization_aggregation_source ConfigConfigurationAggregator#organization_aggregation_source}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#tags ConfigConfigurationAggregator#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#tags_all ConfigConfigurationAggregator#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(account_aggregation_source, dict):
            account_aggregation_source = ConfigConfigurationAggregatorAccountAggregationSource(**account_aggregation_source)
        if isinstance(organization_aggregation_source, dict):
            organization_aggregation_source = ConfigConfigurationAggregatorOrganizationAggregationSource(**organization_aggregation_source)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigurationAggregatorConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument account_aggregation_source", value=account_aggregation_source, expected_type=type_hints["account_aggregation_source"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument organization_aggregation_source", value=organization_aggregation_source, expected_type=type_hints["organization_aggregation_source"])
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
        if account_aggregation_source is not None:
            self._values["account_aggregation_source"] = account_aggregation_source
        if id is not None:
            self._values["id"] = id
        if organization_aggregation_source is not None:
            self._values["organization_aggregation_source"] = organization_aggregation_source
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#name ConfigConfigurationAggregator#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_aggregation_source(
        self,
    ) -> typing.Optional[ConfigConfigurationAggregatorAccountAggregationSource]:
        '''account_aggregation_source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#account_aggregation_source ConfigConfigurationAggregator#account_aggregation_source}
        '''
        result = self._values.get("account_aggregation_source")
        return typing.cast(typing.Optional[ConfigConfigurationAggregatorAccountAggregationSource], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#id ConfigConfigurationAggregator#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization_aggregation_source(
        self,
    ) -> typing.Optional["ConfigConfigurationAggregatorOrganizationAggregationSource"]:
        '''organization_aggregation_source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#organization_aggregation_source ConfigConfigurationAggregator#organization_aggregation_source}
        '''
        result = self._values.get("organization_aggregation_source")
        return typing.cast(typing.Optional["ConfigConfigurationAggregatorOrganizationAggregationSource"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#tags ConfigConfigurationAggregator#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#tags_all ConfigConfigurationAggregator#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfigurationAggregatorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationAggregatorOrganizationAggregationSource",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "all_regions": "allRegions",
        "regions": "regions",
    },
)
class ConfigConfigurationAggregatorOrganizationAggregationSource:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        all_regions: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#role_arn ConfigConfigurationAggregator#role_arn}.
        :param all_regions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#all_regions ConfigConfigurationAggregator#all_regions}.
        :param regions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#regions ConfigConfigurationAggregator#regions}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigurationAggregatorOrganizationAggregationSource.__init__)
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument all_regions", value=all_regions, expected_type=type_hints["all_regions"])
            check_type(argname="argument regions", value=regions, expected_type=type_hints["regions"])
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
        }
        if all_regions is not None:
            self._values["all_regions"] = all_regions
        if regions is not None:
            self._values["regions"] = regions

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#role_arn ConfigConfigurationAggregator#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def all_regions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#all_regions ConfigConfigurationAggregator#all_regions}.'''
        result = self._values.get("all_regions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_aggregator#regions ConfigConfigurationAggregator#regions}.'''
        result = self._values.get("regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfigurationAggregatorOrganizationAggregationSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigConfigurationAggregatorOrganizationAggregationSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationAggregatorOrganizationAggregationSourceOutputReference",
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
            type_hints = typing.get_type_hints(ConfigConfigurationAggregatorOrganizationAggregationSourceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllRegions")
    def reset_all_regions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllRegions", []))

    @jsii.member(jsii_name="resetRegions")
    def reset_regions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegions", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allRegionsInput")
    def all_regions_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allRegionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionsInput")
    def regions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "regionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allRegions")
    def all_regions(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allRegions"))

    @all_regions.setter
    def all_regions(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregatorOrganizationAggregationSourceOutputReference, "all_regions").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allRegions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regions")
    def regions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "regions"))

    @regions.setter
    def regions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregatorOrganizationAggregationSourceOutputReference, "regions").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregatorOrganizationAggregationSourceOutputReference, "role_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigConfigurationAggregatorOrganizationAggregationSource]:
        return typing.cast(typing.Optional[ConfigConfigurationAggregatorOrganizationAggregationSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigConfigurationAggregatorOrganizationAggregationSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationAggregatorOrganizationAggregationSourceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigConfigurationRecorder(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationRecorder",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder aws_config_configuration_recorder}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        role_arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        recording_group: typing.Optional[typing.Union["ConfigConfigurationRecorderRecordingGroup", typing.Dict[str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder aws_config_configuration_recorder} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#role_arn ConfigConfigurationRecorder#role_arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#id ConfigConfigurationRecorder#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#name ConfigConfigurationRecorder#name}.
        :param recording_group: recording_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#recording_group ConfigConfigurationRecorder#recording_group}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigurationRecorder.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigConfigurationRecorderConfig(
            role_arn=role_arn,
            id=id,
            name=name,
            recording_group=recording_group,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putRecordingGroup")
    def put_recording_group(
        self,
        *,
        all_supported: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_global_resource_types: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param all_supported: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#all_supported ConfigConfigurationRecorder#all_supported}.
        :param include_global_resource_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#include_global_resource_types ConfigConfigurationRecorder#include_global_resource_types}.
        :param resource_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#resource_types ConfigConfigurationRecorder#resource_types}.
        '''
        value = ConfigConfigurationRecorderRecordingGroup(
            all_supported=all_supported,
            include_global_resource_types=include_global_resource_types,
            resource_types=resource_types,
        )

        return typing.cast(None, jsii.invoke(self, "putRecordingGroup", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetRecordingGroup")
    def reset_recording_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecordingGroup", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recordingGroup")
    def recording_group(
        self,
    ) -> "ConfigConfigurationRecorderRecordingGroupOutputReference":
        return typing.cast("ConfigConfigurationRecorderRecordingGroupOutputReference", jsii.get(self, "recordingGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recordingGroupInput")
    def recording_group_input(
        self,
    ) -> typing.Optional["ConfigConfigurationRecorderRecordingGroup"]:
        return typing.cast(typing.Optional["ConfigConfigurationRecorderRecordingGroup"], jsii.get(self, "recordingGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationRecorder, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationRecorder, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationRecorder, "role_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationRecorderConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "role_arn": "roleArn",
        "id": "id",
        "name": "name",
        "recording_group": "recordingGroup",
    },
)
class ConfigConfigurationRecorderConfig(cdktf.TerraformMetaArguments):
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
        role_arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        recording_group: typing.Optional[typing.Union["ConfigConfigurationRecorderRecordingGroup", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#role_arn ConfigConfigurationRecorder#role_arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#id ConfigConfigurationRecorder#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#name ConfigConfigurationRecorder#name}.
        :param recording_group: recording_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#recording_group ConfigConfigurationRecorder#recording_group}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(recording_group, dict):
            recording_group = ConfigConfigurationRecorderRecordingGroup(**recording_group)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigurationRecorderConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument recording_group", value=recording_group, expected_type=type_hints["recording_group"])
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
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
        if name is not None:
            self._values["name"] = name
        if recording_group is not None:
            self._values["recording_group"] = recording_group

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
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#role_arn ConfigConfigurationRecorder#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#id ConfigConfigurationRecorder#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#name ConfigConfigurationRecorder#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recording_group(
        self,
    ) -> typing.Optional["ConfigConfigurationRecorderRecordingGroup"]:
        '''recording_group block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#recording_group ConfigConfigurationRecorder#recording_group}
        '''
        result = self._values.get("recording_group")
        return typing.cast(typing.Optional["ConfigConfigurationRecorderRecordingGroup"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfigurationRecorderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationRecorderRecordingGroup",
    jsii_struct_bases=[],
    name_mapping={
        "all_supported": "allSupported",
        "include_global_resource_types": "includeGlobalResourceTypes",
        "resource_types": "resourceTypes",
    },
)
class ConfigConfigurationRecorderRecordingGroup:
    def __init__(
        self,
        *,
        all_supported: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_global_resource_types: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param all_supported: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#all_supported ConfigConfigurationRecorder#all_supported}.
        :param include_global_resource_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#include_global_resource_types ConfigConfigurationRecorder#include_global_resource_types}.
        :param resource_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#resource_types ConfigConfigurationRecorder#resource_types}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigurationRecorderRecordingGroup.__init__)
            check_type(argname="argument all_supported", value=all_supported, expected_type=type_hints["all_supported"])
            check_type(argname="argument include_global_resource_types", value=include_global_resource_types, expected_type=type_hints["include_global_resource_types"])
            check_type(argname="argument resource_types", value=resource_types, expected_type=type_hints["resource_types"])
        self._values: typing.Dict[str, typing.Any] = {}
        if all_supported is not None:
            self._values["all_supported"] = all_supported
        if include_global_resource_types is not None:
            self._values["include_global_resource_types"] = include_global_resource_types
        if resource_types is not None:
            self._values["resource_types"] = resource_types

    @builtins.property
    def all_supported(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#all_supported ConfigConfigurationRecorder#all_supported}.'''
        result = self._values.get("all_supported")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_global_resource_types(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#include_global_resource_types ConfigConfigurationRecorder#include_global_resource_types}.'''
        result = self._values.get("include_global_resource_types")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def resource_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder#resource_types ConfigConfigurationRecorder#resource_types}.'''
        result = self._values.get("resource_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfigurationRecorderRecordingGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigConfigurationRecorderRecordingGroupOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationRecorderRecordingGroupOutputReference",
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
            type_hints = typing.get_type_hints(ConfigConfigurationRecorderRecordingGroupOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllSupported")
    def reset_all_supported(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllSupported", []))

    @jsii.member(jsii_name="resetIncludeGlobalResourceTypes")
    def reset_include_global_resource_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeGlobalResourceTypes", []))

    @jsii.member(jsii_name="resetResourceTypes")
    def reset_resource_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTypes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allSupportedInput")
    def all_supported_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allSupportedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeGlobalResourceTypesInput")
    def include_global_resource_types_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeGlobalResourceTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypesInput")
    def resource_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allSupported")
    def all_supported(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allSupported"))

    @all_supported.setter
    def all_supported(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationRecorderRecordingGroupOutputReference, "all_supported").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allSupported", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeGlobalResourceTypes")
    def include_global_resource_types(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeGlobalResourceTypes"))

    @include_global_resource_types.setter
    def include_global_resource_types(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationRecorderRecordingGroupOutputReference, "include_global_resource_types").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeGlobalResourceTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypes")
    def resource_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceTypes"))

    @resource_types.setter
    def resource_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationRecorderRecordingGroupOutputReference, "resource_types").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigConfigurationRecorderRecordingGroup]:
        return typing.cast(typing.Optional[ConfigConfigurationRecorderRecordingGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigConfigurationRecorderRecordingGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationRecorderRecordingGroupOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigConfigurationRecorderStatus(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationRecorderStatus",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status aws_config_configuration_recorder_status}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        is_enabled: typing.Union[builtins.bool, cdktf.IResolvable],
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status aws_config_configuration_recorder_status} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param is_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status#is_enabled ConfigConfigurationRecorderStatus#is_enabled}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status#name ConfigConfigurationRecorderStatus#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status#id ConfigConfigurationRecorderStatus#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigurationRecorderStatus.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigConfigurationRecorderStatusConfig(
            is_enabled=is_enabled,
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
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "isEnabledInput"))

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
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationRecorderStatus, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isEnabled")
    def is_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "isEnabled"))

    @is_enabled.setter
    def is_enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationRecorderStatus, "is_enabled").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConfigurationRecorderStatus, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConfigurationRecorderStatusConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "is_enabled": "isEnabled",
        "name": "name",
        "id": "id",
    },
)
class ConfigConfigurationRecorderStatusConfig(cdktf.TerraformMetaArguments):
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
        is_enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param is_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status#is_enabled ConfigConfigurationRecorderStatus#is_enabled}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status#name ConfigConfigurationRecorderStatus#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status#id ConfigConfigurationRecorderStatus#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConfigurationRecorderStatusConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "is_enabled": is_enabled,
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
    def is_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status#is_enabled ConfigConfigurationRecorderStatus#is_enabled}.'''
        result = self._values.get("is_enabled")
        assert result is not None, "Required property 'is_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status#name ConfigConfigurationRecorderStatus#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder_status#id ConfigConfigurationRecorderStatus#id}.

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
        return "ConfigConfigurationRecorderStatusConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigConformancePack(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConformancePack",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack aws_config_conformance_pack}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        delivery_s3_bucket: typing.Optional[builtins.str] = None,
        delivery_s3_key_prefix: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        input_parameter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigConformancePackInputParameter", typing.Dict[str, typing.Any]]]]] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_s3_uri: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack aws_config_conformance_pack} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#name ConfigConformancePack#name}.
        :param delivery_s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#delivery_s3_bucket ConfigConformancePack#delivery_s3_bucket}.
        :param delivery_s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#delivery_s3_key_prefix ConfigConformancePack#delivery_s3_key_prefix}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#id ConfigConformancePack#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input_parameter: input_parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#input_parameter ConfigConformancePack#input_parameter}
        :param template_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#template_body ConfigConformancePack#template_body}.
        :param template_s3_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#template_s3_uri ConfigConformancePack#template_s3_uri}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConformancePack.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigConformancePackConfig(
            name=name,
            delivery_s3_bucket=delivery_s3_bucket,
            delivery_s3_key_prefix=delivery_s3_key_prefix,
            id=id,
            input_parameter=input_parameter,
            template_body=template_body,
            template_s3_uri=template_s3_uri,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putInputParameter")
    def put_input_parameter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigConformancePackInputParameter", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConformancePack.put_input_parameter)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInputParameter", [value]))

    @jsii.member(jsii_name="resetDeliveryS3Bucket")
    def reset_delivery_s3_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryS3Bucket", []))

    @jsii.member(jsii_name="resetDeliveryS3KeyPrefix")
    def reset_delivery_s3_key_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryS3KeyPrefix", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInputParameter")
    def reset_input_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInputParameter", []))

    @jsii.member(jsii_name="resetTemplateBody")
    def reset_template_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplateBody", []))

    @jsii.member(jsii_name="resetTemplateS3Uri")
    def reset_template_s3_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplateS3Uri", []))

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
    @jsii.member(jsii_name="inputParameter")
    def input_parameter(self) -> "ConfigConformancePackInputParameterList":
        return typing.cast("ConfigConformancePackInputParameterList", jsii.get(self, "inputParameter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryS3BucketInput")
    def delivery_s3_bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryS3BucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryS3KeyPrefixInput")
    def delivery_s3_key_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryS3KeyPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputParameterInput")
    def input_parameter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigConformancePackInputParameter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigConformancePackInputParameter"]]], jsii.get(self, "inputParameterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateBodyInput")
    def template_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateS3UriInput")
    def template_s3_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateS3UriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryS3Bucket")
    def delivery_s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryS3Bucket"))

    @delivery_s3_bucket.setter
    def delivery_s3_bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePack, "delivery_s3_bucket").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deliveryS3Bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryS3KeyPrefix")
    def delivery_s3_key_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryS3KeyPrefix"))

    @delivery_s3_key_prefix.setter
    def delivery_s3_key_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePack, "delivery_s3_key_prefix").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deliveryS3KeyPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePack, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePack, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateBody")
    def template_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateBody"))

    @template_body.setter
    def template_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePack, "template_body").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "templateBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateS3Uri")
    def template_s3_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateS3Uri"))

    @template_s3_uri.setter
    def template_s3_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePack, "template_s3_uri").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "templateS3Uri", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConformancePackConfig",
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
        "delivery_s3_bucket": "deliveryS3Bucket",
        "delivery_s3_key_prefix": "deliveryS3KeyPrefix",
        "id": "id",
        "input_parameter": "inputParameter",
        "template_body": "templateBody",
        "template_s3_uri": "templateS3Uri",
    },
)
class ConfigConformancePackConfig(cdktf.TerraformMetaArguments):
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
        delivery_s3_bucket: typing.Optional[builtins.str] = None,
        delivery_s3_key_prefix: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        input_parameter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigConformancePackInputParameter", typing.Dict[str, typing.Any]]]]] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_s3_uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#name ConfigConformancePack#name}.
        :param delivery_s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#delivery_s3_bucket ConfigConformancePack#delivery_s3_bucket}.
        :param delivery_s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#delivery_s3_key_prefix ConfigConformancePack#delivery_s3_key_prefix}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#id ConfigConformancePack#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input_parameter: input_parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#input_parameter ConfigConformancePack#input_parameter}
        :param template_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#template_body ConfigConformancePack#template_body}.
        :param template_s3_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#template_s3_uri ConfigConformancePack#template_s3_uri}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConformancePackConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument delivery_s3_bucket", value=delivery_s3_bucket, expected_type=type_hints["delivery_s3_bucket"])
            check_type(argname="argument delivery_s3_key_prefix", value=delivery_s3_key_prefix, expected_type=type_hints["delivery_s3_key_prefix"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument input_parameter", value=input_parameter, expected_type=type_hints["input_parameter"])
            check_type(argname="argument template_body", value=template_body, expected_type=type_hints["template_body"])
            check_type(argname="argument template_s3_uri", value=template_s3_uri, expected_type=type_hints["template_s3_uri"])
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
        if delivery_s3_bucket is not None:
            self._values["delivery_s3_bucket"] = delivery_s3_bucket
        if delivery_s3_key_prefix is not None:
            self._values["delivery_s3_key_prefix"] = delivery_s3_key_prefix
        if id is not None:
            self._values["id"] = id
        if input_parameter is not None:
            self._values["input_parameter"] = input_parameter
        if template_body is not None:
            self._values["template_body"] = template_body
        if template_s3_uri is not None:
            self._values["template_s3_uri"] = template_s3_uri

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#name ConfigConformancePack#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delivery_s3_bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#delivery_s3_bucket ConfigConformancePack#delivery_s3_bucket}.'''
        result = self._values.get("delivery_s3_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delivery_s3_key_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#delivery_s3_key_prefix ConfigConformancePack#delivery_s3_key_prefix}.'''
        result = self._values.get("delivery_s3_key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#id ConfigConformancePack#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_parameter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigConformancePackInputParameter"]]]:
        '''input_parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#input_parameter ConfigConformancePack#input_parameter}
        '''
        result = self._values.get("input_parameter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigConformancePackInputParameter"]]], result)

    @builtins.property
    def template_body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#template_body ConfigConformancePack#template_body}.'''
        result = self._values.get("template_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template_s3_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#template_s3_uri ConfigConformancePack#template_s3_uri}.'''
        result = self._values.get("template_s3_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConformancePackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigConformancePackInputParameter",
    jsii_struct_bases=[],
    name_mapping={
        "parameter_name": "parameterName",
        "parameter_value": "parameterValue",
    },
)
class ConfigConformancePackInputParameter:
    def __init__(
        self,
        *,
        parameter_name: builtins.str,
        parameter_value: builtins.str,
    ) -> None:
        '''
        :param parameter_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#parameter_name ConfigConformancePack#parameter_name}.
        :param parameter_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#parameter_value ConfigConformancePack#parameter_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConformancePackInputParameter.__init__)
            check_type(argname="argument parameter_name", value=parameter_name, expected_type=type_hints["parameter_name"])
            check_type(argname="argument parameter_value", value=parameter_value, expected_type=type_hints["parameter_value"])
        self._values: typing.Dict[str, typing.Any] = {
            "parameter_name": parameter_name,
            "parameter_value": parameter_value,
        }

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#parameter_name ConfigConformancePack#parameter_name}.'''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_conformance_pack#parameter_value ConfigConformancePack#parameter_value}.'''
        result = self._values.get("parameter_value")
        assert result is not None, "Required property 'parameter_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConformancePackInputParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigConformancePackInputParameterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConformancePackInputParameterList",
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
            type_hints = typing.get_type_hints(ConfigConformancePackInputParameterList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigConformancePackInputParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigConformancePackInputParameterList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigConformancePackInputParameterOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePackInputParameterList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(ConfigConformancePackInputParameterList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(ConfigConformancePackInputParameterList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigConformancePackInputParameter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigConformancePackInputParameter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigConformancePackInputParameter]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePackInputParameterList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigConformancePackInputParameterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigConformancePackInputParameterOutputReference",
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
            type_hints = typing.get_type_hints(ConfigConformancePackInputParameterOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterNameInput")
    def parameter_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterValueInput")
    def parameter_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterName")
    def parameter_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterName"))

    @parameter_name.setter
    def parameter_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePackInputParameterOutputReference, "parameter_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterValue")
    def parameter_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterValue"))

    @parameter_value.setter
    def parameter_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePackInputParameterOutputReference, "parameter_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ConfigConformancePackInputParameter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ConfigConformancePackInputParameter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ConfigConformancePackInputParameter, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigConformancePackInputParameterOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigDeliveryChannel(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigDeliveryChannel",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel aws_config_delivery_channel}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        s3_bucket_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        s3_key_prefix: typing.Optional[builtins.str] = None,
        s3_kms_key_arn: typing.Optional[builtins.str] = None,
        snapshot_delivery_properties: typing.Optional[typing.Union["ConfigDeliveryChannelSnapshotDeliveryProperties", typing.Dict[str, typing.Any]]] = None,
        sns_topic_arn: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel aws_config_delivery_channel} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param s3_bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#s3_bucket_name ConfigDeliveryChannel#s3_bucket_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#id ConfigDeliveryChannel#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#name ConfigDeliveryChannel#name}.
        :param s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#s3_key_prefix ConfigDeliveryChannel#s3_key_prefix}.
        :param s3_kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#s3_kms_key_arn ConfigDeliveryChannel#s3_kms_key_arn}.
        :param snapshot_delivery_properties: snapshot_delivery_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#snapshot_delivery_properties ConfigDeliveryChannel#snapshot_delivery_properties}
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#sns_topic_arn ConfigDeliveryChannel#sns_topic_arn}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigDeliveryChannel.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigDeliveryChannelConfig(
            s3_bucket_name=s3_bucket_name,
            id=id,
            name=name,
            s3_key_prefix=s3_key_prefix,
            s3_kms_key_arn=s3_kms_key_arn,
            snapshot_delivery_properties=snapshot_delivery_properties,
            sns_topic_arn=sns_topic_arn,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putSnapshotDeliveryProperties")
    def put_snapshot_delivery_properties(
        self,
        *,
        delivery_frequency: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delivery_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#delivery_frequency ConfigDeliveryChannel#delivery_frequency}.
        '''
        value = ConfigDeliveryChannelSnapshotDeliveryProperties(
            delivery_frequency=delivery_frequency
        )

        return typing.cast(None, jsii.invoke(self, "putSnapshotDeliveryProperties", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetS3KeyPrefix")
    def reset_s3_key_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3KeyPrefix", []))

    @jsii.member(jsii_name="resetS3KmsKeyArn")
    def reset_s3_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3KmsKeyArn", []))

    @jsii.member(jsii_name="resetSnapshotDeliveryProperties")
    def reset_snapshot_delivery_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotDeliveryProperties", []))

    @jsii.member(jsii_name="resetSnsTopicArn")
    def reset_sns_topic_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnsTopicArn", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotDeliveryProperties")
    def snapshot_delivery_properties(
        self,
    ) -> "ConfigDeliveryChannelSnapshotDeliveryPropertiesOutputReference":
        return typing.cast("ConfigDeliveryChannelSnapshotDeliveryPropertiesOutputReference", jsii.get(self, "snapshotDeliveryProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketNameInput")
    def s3_bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3BucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyPrefixInput")
    def s3_key_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3KeyPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KmsKeyArnInput")
    def s3_kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3KmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotDeliveryPropertiesInput")
    def snapshot_delivery_properties_input(
        self,
    ) -> typing.Optional["ConfigDeliveryChannelSnapshotDeliveryProperties"]:
        return typing.cast(typing.Optional["ConfigDeliveryChannelSnapshotDeliveryProperties"], jsii.get(self, "snapshotDeliveryPropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArnInput")
    def sns_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigDeliveryChannel, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigDeliveryChannel, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketName")
    def s3_bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3BucketName"))

    @s3_bucket_name.setter
    def s3_bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigDeliveryChannel, "s3_bucket_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3BucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyPrefix")
    def s3_key_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3KeyPrefix"))

    @s3_key_prefix.setter
    def s3_key_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigDeliveryChannel, "s3_key_prefix").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3KeyPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KmsKeyArn")
    def s3_kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3KmsKeyArn"))

    @s3_kms_key_arn.setter
    def s3_kms_key_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigDeliveryChannel, "s3_kms_key_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3KmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsTopicArn"))

    @sns_topic_arn.setter
    def sns_topic_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigDeliveryChannel, "sns_topic_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "snsTopicArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigDeliveryChannelConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "s3_bucket_name": "s3BucketName",
        "id": "id",
        "name": "name",
        "s3_key_prefix": "s3KeyPrefix",
        "s3_kms_key_arn": "s3KmsKeyArn",
        "snapshot_delivery_properties": "snapshotDeliveryProperties",
        "sns_topic_arn": "snsTopicArn",
    },
)
class ConfigDeliveryChannelConfig(cdktf.TerraformMetaArguments):
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
        s3_bucket_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        s3_key_prefix: typing.Optional[builtins.str] = None,
        s3_kms_key_arn: typing.Optional[builtins.str] = None,
        snapshot_delivery_properties: typing.Optional[typing.Union["ConfigDeliveryChannelSnapshotDeliveryProperties", typing.Dict[str, typing.Any]]] = None,
        sns_topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param s3_bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#s3_bucket_name ConfigDeliveryChannel#s3_bucket_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#id ConfigDeliveryChannel#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#name ConfigDeliveryChannel#name}.
        :param s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#s3_key_prefix ConfigDeliveryChannel#s3_key_prefix}.
        :param s3_kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#s3_kms_key_arn ConfigDeliveryChannel#s3_kms_key_arn}.
        :param snapshot_delivery_properties: snapshot_delivery_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#snapshot_delivery_properties ConfigDeliveryChannel#snapshot_delivery_properties}
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#sns_topic_arn ConfigDeliveryChannel#sns_topic_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(snapshot_delivery_properties, dict):
            snapshot_delivery_properties = ConfigDeliveryChannelSnapshotDeliveryProperties(**snapshot_delivery_properties)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigDeliveryChannelConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument s3_bucket_name", value=s3_bucket_name, expected_type=type_hints["s3_bucket_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument s3_key_prefix", value=s3_key_prefix, expected_type=type_hints["s3_key_prefix"])
            check_type(argname="argument s3_kms_key_arn", value=s3_kms_key_arn, expected_type=type_hints["s3_kms_key_arn"])
            check_type(argname="argument snapshot_delivery_properties", value=snapshot_delivery_properties, expected_type=type_hints["snapshot_delivery_properties"])
            check_type(argname="argument sns_topic_arn", value=sns_topic_arn, expected_type=type_hints["sns_topic_arn"])
        self._values: typing.Dict[str, typing.Any] = {
            "s3_bucket_name": s3_bucket_name,
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
        if name is not None:
            self._values["name"] = name
        if s3_key_prefix is not None:
            self._values["s3_key_prefix"] = s3_key_prefix
        if s3_kms_key_arn is not None:
            self._values["s3_kms_key_arn"] = s3_kms_key_arn
        if snapshot_delivery_properties is not None:
            self._values["snapshot_delivery_properties"] = snapshot_delivery_properties
        if sns_topic_arn is not None:
            self._values["sns_topic_arn"] = sns_topic_arn

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
    def s3_bucket_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#s3_bucket_name ConfigDeliveryChannel#s3_bucket_name}.'''
        result = self._values.get("s3_bucket_name")
        assert result is not None, "Required property 's3_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#id ConfigDeliveryChannel#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#name ConfigDeliveryChannel#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_key_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#s3_key_prefix ConfigDeliveryChannel#s3_key_prefix}.'''
        result = self._values.get("s3_key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#s3_kms_key_arn ConfigDeliveryChannel#s3_kms_key_arn}.'''
        result = self._values.get("s3_kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_delivery_properties(
        self,
    ) -> typing.Optional["ConfigDeliveryChannelSnapshotDeliveryProperties"]:
        '''snapshot_delivery_properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#snapshot_delivery_properties ConfigDeliveryChannel#snapshot_delivery_properties}
        '''
        result = self._values.get("snapshot_delivery_properties")
        return typing.cast(typing.Optional["ConfigDeliveryChannelSnapshotDeliveryProperties"], result)

    @builtins.property
    def sns_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#sns_topic_arn ConfigDeliveryChannel#sns_topic_arn}.'''
        result = self._values.get("sns_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigDeliveryChannelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigDeliveryChannelSnapshotDeliveryProperties",
    jsii_struct_bases=[],
    name_mapping={"delivery_frequency": "deliveryFrequency"},
)
class ConfigDeliveryChannelSnapshotDeliveryProperties:
    def __init__(
        self,
        *,
        delivery_frequency: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delivery_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#delivery_frequency ConfigDeliveryChannel#delivery_frequency}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigDeliveryChannelSnapshotDeliveryProperties.__init__)
            check_type(argname="argument delivery_frequency", value=delivery_frequency, expected_type=type_hints["delivery_frequency"])
        self._values: typing.Dict[str, typing.Any] = {}
        if delivery_frequency is not None:
            self._values["delivery_frequency"] = delivery_frequency

    @builtins.property
    def delivery_frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_delivery_channel#delivery_frequency ConfigDeliveryChannel#delivery_frequency}.'''
        result = self._values.get("delivery_frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigDeliveryChannelSnapshotDeliveryProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigDeliveryChannelSnapshotDeliveryPropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigDeliveryChannelSnapshotDeliveryPropertiesOutputReference",
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
            type_hints = typing.get_type_hints(ConfigDeliveryChannelSnapshotDeliveryPropertiesOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDeliveryFrequency")
    def reset_delivery_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryFrequency", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryFrequencyInput")
    def delivery_frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryFrequencyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryFrequency")
    def delivery_frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryFrequency"))

    @delivery_frequency.setter
    def delivery_frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigDeliveryChannelSnapshotDeliveryPropertiesOutputReference, "delivery_frequency").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deliveryFrequency", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigDeliveryChannelSnapshotDeliveryProperties]:
        return typing.cast(typing.Optional[ConfigDeliveryChannelSnapshotDeliveryProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigDeliveryChannelSnapshotDeliveryProperties],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigDeliveryChannelSnapshotDeliveryPropertiesOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigOrganizationConformancePack(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationConformancePack",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack aws_config_organization_conformance_pack}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        delivery_s3_bucket: typing.Optional[builtins.str] = None,
        delivery_s3_key_prefix: typing.Optional[builtins.str] = None,
        excluded_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        input_parameter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigOrganizationConformancePackInputParameter", typing.Dict[str, typing.Any]]]]] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_s3_uri: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["ConfigOrganizationConformancePackTimeouts", typing.Dict[str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack aws_config_organization_conformance_pack} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#name ConfigOrganizationConformancePack#name}.
        :param delivery_s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#delivery_s3_bucket ConfigOrganizationConformancePack#delivery_s3_bucket}.
        :param delivery_s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#delivery_s3_key_prefix ConfigOrganizationConformancePack#delivery_s3_key_prefix}.
        :param excluded_accounts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#excluded_accounts ConfigOrganizationConformancePack#excluded_accounts}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#id ConfigOrganizationConformancePack#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input_parameter: input_parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#input_parameter ConfigOrganizationConformancePack#input_parameter}
        :param template_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#template_body ConfigOrganizationConformancePack#template_body}.
        :param template_s3_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#template_s3_uri ConfigOrganizationConformancePack#template_s3_uri}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#timeouts ConfigOrganizationConformancePack#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationConformancePack.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigOrganizationConformancePackConfig(
            name=name,
            delivery_s3_bucket=delivery_s3_bucket,
            delivery_s3_key_prefix=delivery_s3_key_prefix,
            excluded_accounts=excluded_accounts,
            id=id,
            input_parameter=input_parameter,
            template_body=template_body,
            template_s3_uri=template_s3_uri,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putInputParameter")
    def put_input_parameter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigOrganizationConformancePackInputParameter", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationConformancePack.put_input_parameter)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInputParameter", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#create ConfigOrganizationConformancePack#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#delete ConfigOrganizationConformancePack#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#update ConfigOrganizationConformancePack#update}.
        '''
        value = ConfigOrganizationConformancePackTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDeliveryS3Bucket")
    def reset_delivery_s3_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryS3Bucket", []))

    @jsii.member(jsii_name="resetDeliveryS3KeyPrefix")
    def reset_delivery_s3_key_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryS3KeyPrefix", []))

    @jsii.member(jsii_name="resetExcludedAccounts")
    def reset_excluded_accounts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedAccounts", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInputParameter")
    def reset_input_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInputParameter", []))

    @jsii.member(jsii_name="resetTemplateBody")
    def reset_template_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplateBody", []))

    @jsii.member(jsii_name="resetTemplateS3Uri")
    def reset_template_s3_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplateS3Uri", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="inputParameter")
    def input_parameter(self) -> "ConfigOrganizationConformancePackInputParameterList":
        return typing.cast("ConfigOrganizationConformancePackInputParameterList", jsii.get(self, "inputParameter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ConfigOrganizationConformancePackTimeoutsOutputReference":
        return typing.cast("ConfigOrganizationConformancePackTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryS3BucketInput")
    def delivery_s3_bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryS3BucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryS3KeyPrefixInput")
    def delivery_s3_key_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryS3KeyPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludedAccountsInput")
    def excluded_accounts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedAccountsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputParameterInput")
    def input_parameter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigOrganizationConformancePackInputParameter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigOrganizationConformancePackInputParameter"]]], jsii.get(self, "inputParameterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateBodyInput")
    def template_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateS3UriInput")
    def template_s3_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateS3UriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["ConfigOrganizationConformancePackTimeouts", cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["ConfigOrganizationConformancePackTimeouts", cdktf.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryS3Bucket")
    def delivery_s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryS3Bucket"))

    @delivery_s3_bucket.setter
    def delivery_s3_bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePack, "delivery_s3_bucket").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deliveryS3Bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryS3KeyPrefix")
    def delivery_s3_key_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryS3KeyPrefix"))

    @delivery_s3_key_prefix.setter
    def delivery_s3_key_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePack, "delivery_s3_key_prefix").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deliveryS3KeyPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludedAccounts")
    def excluded_accounts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedAccounts"))

    @excluded_accounts.setter
    def excluded_accounts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePack, "excluded_accounts").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedAccounts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePack, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePack, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateBody")
    def template_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateBody"))

    @template_body.setter
    def template_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePack, "template_body").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "templateBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateS3Uri")
    def template_s3_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateS3Uri"))

    @template_s3_uri.setter
    def template_s3_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePack, "template_s3_uri").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "templateS3Uri", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationConformancePackConfig",
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
        "delivery_s3_bucket": "deliveryS3Bucket",
        "delivery_s3_key_prefix": "deliveryS3KeyPrefix",
        "excluded_accounts": "excludedAccounts",
        "id": "id",
        "input_parameter": "inputParameter",
        "template_body": "templateBody",
        "template_s3_uri": "templateS3Uri",
        "timeouts": "timeouts",
    },
)
class ConfigOrganizationConformancePackConfig(cdktf.TerraformMetaArguments):
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
        delivery_s3_bucket: typing.Optional[builtins.str] = None,
        delivery_s3_key_prefix: typing.Optional[builtins.str] = None,
        excluded_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        input_parameter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigOrganizationConformancePackInputParameter", typing.Dict[str, typing.Any]]]]] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_s3_uri: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["ConfigOrganizationConformancePackTimeouts", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#name ConfigOrganizationConformancePack#name}.
        :param delivery_s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#delivery_s3_bucket ConfigOrganizationConformancePack#delivery_s3_bucket}.
        :param delivery_s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#delivery_s3_key_prefix ConfigOrganizationConformancePack#delivery_s3_key_prefix}.
        :param excluded_accounts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#excluded_accounts ConfigOrganizationConformancePack#excluded_accounts}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#id ConfigOrganizationConformancePack#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input_parameter: input_parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#input_parameter ConfigOrganizationConformancePack#input_parameter}
        :param template_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#template_body ConfigOrganizationConformancePack#template_body}.
        :param template_s3_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#template_s3_uri ConfigOrganizationConformancePack#template_s3_uri}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#timeouts ConfigOrganizationConformancePack#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = ConfigOrganizationConformancePackTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationConformancePackConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument delivery_s3_bucket", value=delivery_s3_bucket, expected_type=type_hints["delivery_s3_bucket"])
            check_type(argname="argument delivery_s3_key_prefix", value=delivery_s3_key_prefix, expected_type=type_hints["delivery_s3_key_prefix"])
            check_type(argname="argument excluded_accounts", value=excluded_accounts, expected_type=type_hints["excluded_accounts"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument input_parameter", value=input_parameter, expected_type=type_hints["input_parameter"])
            check_type(argname="argument template_body", value=template_body, expected_type=type_hints["template_body"])
            check_type(argname="argument template_s3_uri", value=template_s3_uri, expected_type=type_hints["template_s3_uri"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
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
        if delivery_s3_bucket is not None:
            self._values["delivery_s3_bucket"] = delivery_s3_bucket
        if delivery_s3_key_prefix is not None:
            self._values["delivery_s3_key_prefix"] = delivery_s3_key_prefix
        if excluded_accounts is not None:
            self._values["excluded_accounts"] = excluded_accounts
        if id is not None:
            self._values["id"] = id
        if input_parameter is not None:
            self._values["input_parameter"] = input_parameter
        if template_body is not None:
            self._values["template_body"] = template_body
        if template_s3_uri is not None:
            self._values["template_s3_uri"] = template_s3_uri
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#name ConfigOrganizationConformancePack#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delivery_s3_bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#delivery_s3_bucket ConfigOrganizationConformancePack#delivery_s3_bucket}.'''
        result = self._values.get("delivery_s3_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delivery_s3_key_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#delivery_s3_key_prefix ConfigOrganizationConformancePack#delivery_s3_key_prefix}.'''
        result = self._values.get("delivery_s3_key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def excluded_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#excluded_accounts ConfigOrganizationConformancePack#excluded_accounts}.'''
        result = self._values.get("excluded_accounts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#id ConfigOrganizationConformancePack#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_parameter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigOrganizationConformancePackInputParameter"]]]:
        '''input_parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#input_parameter ConfigOrganizationConformancePack#input_parameter}
        '''
        result = self._values.get("input_parameter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigOrganizationConformancePackInputParameter"]]], result)

    @builtins.property
    def template_body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#template_body ConfigOrganizationConformancePack#template_body}.'''
        result = self._values.get("template_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template_s3_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#template_s3_uri ConfigOrganizationConformancePack#template_s3_uri}.'''
        result = self._values.get("template_s3_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ConfigOrganizationConformancePackTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#timeouts ConfigOrganizationConformancePack#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ConfigOrganizationConformancePackTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigOrganizationConformancePackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationConformancePackInputParameter",
    jsii_struct_bases=[],
    name_mapping={
        "parameter_name": "parameterName",
        "parameter_value": "parameterValue",
    },
)
class ConfigOrganizationConformancePackInputParameter:
    def __init__(
        self,
        *,
        parameter_name: builtins.str,
        parameter_value: builtins.str,
    ) -> None:
        '''
        :param parameter_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#parameter_name ConfigOrganizationConformancePack#parameter_name}.
        :param parameter_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#parameter_value ConfigOrganizationConformancePack#parameter_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationConformancePackInputParameter.__init__)
            check_type(argname="argument parameter_name", value=parameter_name, expected_type=type_hints["parameter_name"])
            check_type(argname="argument parameter_value", value=parameter_value, expected_type=type_hints["parameter_value"])
        self._values: typing.Dict[str, typing.Any] = {
            "parameter_name": parameter_name,
            "parameter_value": parameter_value,
        }

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#parameter_name ConfigOrganizationConformancePack#parameter_name}.'''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#parameter_value ConfigOrganizationConformancePack#parameter_value}.'''
        result = self._values.get("parameter_value")
        assert result is not None, "Required property 'parameter_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigOrganizationConformancePackInputParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigOrganizationConformancePackInputParameterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationConformancePackInputParameterList",
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
            type_hints = typing.get_type_hints(ConfigOrganizationConformancePackInputParameterList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigOrganizationConformancePackInputParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationConformancePackInputParameterList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigOrganizationConformancePackInputParameterOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackInputParameterList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackInputParameterList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackInputParameterList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigOrganizationConformancePackInputParameter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigOrganizationConformancePackInputParameter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigOrganizationConformancePackInputParameter]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackInputParameterList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigOrganizationConformancePackInputParameterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationConformancePackInputParameterOutputReference",
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
            type_hints = typing.get_type_hints(ConfigOrganizationConformancePackInputParameterOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterNameInput")
    def parameter_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterValueInput")
    def parameter_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterName")
    def parameter_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterName"))

    @parameter_name.setter
    def parameter_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackInputParameterOutputReference, "parameter_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterValue")
    def parameter_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterValue"))

    @parameter_value.setter
    def parameter_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackInputParameterOutputReference, "parameter_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ConfigOrganizationConformancePackInputParameter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ConfigOrganizationConformancePackInputParameter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ConfigOrganizationConformancePackInputParameter, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackInputParameterOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationConformancePackTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class ConfigOrganizationConformancePackTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#create ConfigOrganizationConformancePack#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#delete ConfigOrganizationConformancePack#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#update ConfigOrganizationConformancePack#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationConformancePackTimeouts.__init__)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#create ConfigOrganizationConformancePack#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#delete ConfigOrganizationConformancePack#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_conformance_pack#update ConfigOrganizationConformancePack#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigOrganizationConformancePackTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigOrganizationConformancePackTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationConformancePackTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(ConfigOrganizationConformancePackTimeoutsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackTimeoutsOutputReference, "create").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackTimeoutsOutputReference, "delete").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackTimeoutsOutputReference, "update").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ConfigOrganizationConformancePackTimeouts, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ConfigOrganizationConformancePackTimeouts, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ConfigOrganizationConformancePackTimeouts, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationConformancePackTimeoutsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigOrganizationCustomRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationCustomRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule aws_config_organization_custom_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        lambda_function_arn: builtins.str,
        name: builtins.str,
        trigger_types: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        excluded_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[builtins.str] = None,
        maximum_execution_frequency: typing.Optional[builtins.str] = None,
        resource_id_scope: typing.Optional[builtins.str] = None,
        resource_types_scope: typing.Optional[typing.Sequence[builtins.str]] = None,
        tag_key_scope: typing.Optional[builtins.str] = None,
        tag_value_scope: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["ConfigOrganizationCustomRuleTimeouts", typing.Dict[str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule aws_config_organization_custom_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param lambda_function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#lambda_function_arn ConfigOrganizationCustomRule#lambda_function_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#name ConfigOrganizationCustomRule#name}.
        :param trigger_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#trigger_types ConfigOrganizationCustomRule#trigger_types}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#description ConfigOrganizationCustomRule#description}.
        :param excluded_accounts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#excluded_accounts ConfigOrganizationCustomRule#excluded_accounts}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#id ConfigOrganizationCustomRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#input_parameters ConfigOrganizationCustomRule#input_parameters}.
        :param maximum_execution_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#maximum_execution_frequency ConfigOrganizationCustomRule#maximum_execution_frequency}.
        :param resource_id_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#resource_id_scope ConfigOrganizationCustomRule#resource_id_scope}.
        :param resource_types_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#resource_types_scope ConfigOrganizationCustomRule#resource_types_scope}.
        :param tag_key_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#tag_key_scope ConfigOrganizationCustomRule#tag_key_scope}.
        :param tag_value_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#tag_value_scope ConfigOrganizationCustomRule#tag_value_scope}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#timeouts ConfigOrganizationCustomRule#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationCustomRule.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigOrganizationCustomRuleConfig(
            lambda_function_arn=lambda_function_arn,
            name=name,
            trigger_types=trigger_types,
            description=description,
            excluded_accounts=excluded_accounts,
            id=id,
            input_parameters=input_parameters,
            maximum_execution_frequency=maximum_execution_frequency,
            resource_id_scope=resource_id_scope,
            resource_types_scope=resource_types_scope,
            tag_key_scope=tag_key_scope,
            tag_value_scope=tag_value_scope,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#create ConfigOrganizationCustomRule#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#delete ConfigOrganizationCustomRule#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#update ConfigOrganizationCustomRule#update}.
        '''
        value = ConfigOrganizationCustomRuleTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExcludedAccounts")
    def reset_excluded_accounts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedAccounts", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInputParameters")
    def reset_input_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInputParameters", []))

    @jsii.member(jsii_name="resetMaximumExecutionFrequency")
    def reset_maximum_execution_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumExecutionFrequency", []))

    @jsii.member(jsii_name="resetResourceIdScope")
    def reset_resource_id_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceIdScope", []))

    @jsii.member(jsii_name="resetResourceTypesScope")
    def reset_resource_types_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTypesScope", []))

    @jsii.member(jsii_name="resetTagKeyScope")
    def reset_tag_key_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagKeyScope", []))

    @jsii.member(jsii_name="resetTagValueScope")
    def reset_tag_value_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagValueScope", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ConfigOrganizationCustomRuleTimeoutsOutputReference":
        return typing.cast("ConfigOrganizationCustomRuleTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludedAccountsInput")
    def excluded_accounts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedAccountsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputParametersInput")
    def input_parameters_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunctionArnInput")
    def lambda_function_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaFunctionArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumExecutionFrequencyInput")
    def maximum_execution_frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maximumExecutionFrequencyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdScopeInput")
    def resource_id_scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceIdScopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypesScopeInput")
    def resource_types_scope_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceTypesScopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagKeyScopeInput")
    def tag_key_scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagKeyScopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagValueScopeInput")
    def tag_value_scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagValueScopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["ConfigOrganizationCustomRuleTimeouts", cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["ConfigOrganizationCustomRuleTimeouts", cdktf.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggerTypesInput")
    def trigger_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "triggerTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludedAccounts")
    def excluded_accounts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedAccounts"))

    @excluded_accounts.setter
    def excluded_accounts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "excluded_accounts").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedAccounts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputParameters")
    def input_parameters(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inputParameters"))

    @input_parameters.setter
    def input_parameters(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "input_parameters").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunctionArn")
    def lambda_function_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaFunctionArn"))

    @lambda_function_arn.setter
    def lambda_function_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "lambda_function_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lambdaFunctionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumExecutionFrequency")
    def maximum_execution_frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maximumExecutionFrequency"))

    @maximum_execution_frequency.setter
    def maximum_execution_frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "maximum_execution_frequency").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximumExecutionFrequency", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdScope")
    def resource_id_scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceIdScope"))

    @resource_id_scope.setter
    def resource_id_scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "resource_id_scope").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceIdScope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypesScope")
    def resource_types_scope(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceTypesScope"))

    @resource_types_scope.setter
    def resource_types_scope(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "resource_types_scope").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceTypesScope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagKeyScope")
    def tag_key_scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagKeyScope"))

    @tag_key_scope.setter
    def tag_key_scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "tag_key_scope").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagKeyScope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagValueScope")
    def tag_value_scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagValueScope"))

    @tag_value_scope.setter
    def tag_value_scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "tag_value_scope").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagValueScope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggerTypes")
    def trigger_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "triggerTypes"))

    @trigger_types.setter
    def trigger_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRule, "trigger_types").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerTypes", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationCustomRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "lambda_function_arn": "lambdaFunctionArn",
        "name": "name",
        "trigger_types": "triggerTypes",
        "description": "description",
        "excluded_accounts": "excludedAccounts",
        "id": "id",
        "input_parameters": "inputParameters",
        "maximum_execution_frequency": "maximumExecutionFrequency",
        "resource_id_scope": "resourceIdScope",
        "resource_types_scope": "resourceTypesScope",
        "tag_key_scope": "tagKeyScope",
        "tag_value_scope": "tagValueScope",
        "timeouts": "timeouts",
    },
)
class ConfigOrganizationCustomRuleConfig(cdktf.TerraformMetaArguments):
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
        lambda_function_arn: builtins.str,
        name: builtins.str,
        trigger_types: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        excluded_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[builtins.str] = None,
        maximum_execution_frequency: typing.Optional[builtins.str] = None,
        resource_id_scope: typing.Optional[builtins.str] = None,
        resource_types_scope: typing.Optional[typing.Sequence[builtins.str]] = None,
        tag_key_scope: typing.Optional[builtins.str] = None,
        tag_value_scope: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["ConfigOrganizationCustomRuleTimeouts", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param lambda_function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#lambda_function_arn ConfigOrganizationCustomRule#lambda_function_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#name ConfigOrganizationCustomRule#name}.
        :param trigger_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#trigger_types ConfigOrganizationCustomRule#trigger_types}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#description ConfigOrganizationCustomRule#description}.
        :param excluded_accounts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#excluded_accounts ConfigOrganizationCustomRule#excluded_accounts}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#id ConfigOrganizationCustomRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#input_parameters ConfigOrganizationCustomRule#input_parameters}.
        :param maximum_execution_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#maximum_execution_frequency ConfigOrganizationCustomRule#maximum_execution_frequency}.
        :param resource_id_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#resource_id_scope ConfigOrganizationCustomRule#resource_id_scope}.
        :param resource_types_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#resource_types_scope ConfigOrganizationCustomRule#resource_types_scope}.
        :param tag_key_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#tag_key_scope ConfigOrganizationCustomRule#tag_key_scope}.
        :param tag_value_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#tag_value_scope ConfigOrganizationCustomRule#tag_value_scope}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#timeouts ConfigOrganizationCustomRule#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = ConfigOrganizationCustomRuleTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationCustomRuleConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument lambda_function_arn", value=lambda_function_arn, expected_type=type_hints["lambda_function_arn"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument trigger_types", value=trigger_types, expected_type=type_hints["trigger_types"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument excluded_accounts", value=excluded_accounts, expected_type=type_hints["excluded_accounts"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument input_parameters", value=input_parameters, expected_type=type_hints["input_parameters"])
            check_type(argname="argument maximum_execution_frequency", value=maximum_execution_frequency, expected_type=type_hints["maximum_execution_frequency"])
            check_type(argname="argument resource_id_scope", value=resource_id_scope, expected_type=type_hints["resource_id_scope"])
            check_type(argname="argument resource_types_scope", value=resource_types_scope, expected_type=type_hints["resource_types_scope"])
            check_type(argname="argument tag_key_scope", value=tag_key_scope, expected_type=type_hints["tag_key_scope"])
            check_type(argname="argument tag_value_scope", value=tag_value_scope, expected_type=type_hints["tag_value_scope"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[str, typing.Any] = {
            "lambda_function_arn": lambda_function_arn,
            "name": name,
            "trigger_types": trigger_types,
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
        if excluded_accounts is not None:
            self._values["excluded_accounts"] = excluded_accounts
        if id is not None:
            self._values["id"] = id
        if input_parameters is not None:
            self._values["input_parameters"] = input_parameters
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency
        if resource_id_scope is not None:
            self._values["resource_id_scope"] = resource_id_scope
        if resource_types_scope is not None:
            self._values["resource_types_scope"] = resource_types_scope
        if tag_key_scope is not None:
            self._values["tag_key_scope"] = tag_key_scope
        if tag_value_scope is not None:
            self._values["tag_value_scope"] = tag_value_scope
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def lambda_function_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#lambda_function_arn ConfigOrganizationCustomRule#lambda_function_arn}.'''
        result = self._values.get("lambda_function_arn")
        assert result is not None, "Required property 'lambda_function_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#name ConfigOrganizationCustomRule#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def trigger_types(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#trigger_types ConfigOrganizationCustomRule#trigger_types}.'''
        result = self._values.get("trigger_types")
        assert result is not None, "Required property 'trigger_types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#description ConfigOrganizationCustomRule#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def excluded_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#excluded_accounts ConfigOrganizationCustomRule#excluded_accounts}.'''
        result = self._values.get("excluded_accounts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#id ConfigOrganizationCustomRule#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_parameters(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#input_parameters ConfigOrganizationCustomRule#input_parameters}.'''
        result = self._values.get("input_parameters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#maximum_execution_frequency ConfigOrganizationCustomRule#maximum_execution_frequency}.'''
        result = self._values.get("maximum_execution_frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_id_scope(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#resource_id_scope ConfigOrganizationCustomRule#resource_id_scope}.'''
        result = self._values.get("resource_id_scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_types_scope(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#resource_types_scope ConfigOrganizationCustomRule#resource_types_scope}.'''
        result = self._values.get("resource_types_scope")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tag_key_scope(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#tag_key_scope ConfigOrganizationCustomRule#tag_key_scope}.'''
        result = self._values.get("tag_key_scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_value_scope(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#tag_value_scope ConfigOrganizationCustomRule#tag_value_scope}.'''
        result = self._values.get("tag_value_scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ConfigOrganizationCustomRuleTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#timeouts ConfigOrganizationCustomRule#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ConfigOrganizationCustomRuleTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigOrganizationCustomRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationCustomRuleTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class ConfigOrganizationCustomRuleTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#create ConfigOrganizationCustomRule#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#delete ConfigOrganizationCustomRule#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#update ConfigOrganizationCustomRule#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationCustomRuleTimeouts.__init__)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#create ConfigOrganizationCustomRule#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#delete ConfigOrganizationCustomRule#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_custom_rule#update ConfigOrganizationCustomRule#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigOrganizationCustomRuleTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigOrganizationCustomRuleTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationCustomRuleTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(ConfigOrganizationCustomRuleTimeoutsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRuleTimeoutsOutputReference, "create").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRuleTimeoutsOutputReference, "delete").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRuleTimeoutsOutputReference, "update").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ConfigOrganizationCustomRuleTimeouts, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ConfigOrganizationCustomRuleTimeouts, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ConfigOrganizationCustomRuleTimeouts, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationCustomRuleTimeoutsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigOrganizationManagedRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationManagedRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule aws_config_organization_managed_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        rule_identifier: builtins.str,
        description: typing.Optional[builtins.str] = None,
        excluded_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[builtins.str] = None,
        maximum_execution_frequency: typing.Optional[builtins.str] = None,
        resource_id_scope: typing.Optional[builtins.str] = None,
        resource_types_scope: typing.Optional[typing.Sequence[builtins.str]] = None,
        tag_key_scope: typing.Optional[builtins.str] = None,
        tag_value_scope: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["ConfigOrganizationManagedRuleTimeouts", typing.Dict[str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule aws_config_organization_managed_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#name ConfigOrganizationManagedRule#name}.
        :param rule_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#rule_identifier ConfigOrganizationManagedRule#rule_identifier}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#description ConfigOrganizationManagedRule#description}.
        :param excluded_accounts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#excluded_accounts ConfigOrganizationManagedRule#excluded_accounts}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#id ConfigOrganizationManagedRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#input_parameters ConfigOrganizationManagedRule#input_parameters}.
        :param maximum_execution_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#maximum_execution_frequency ConfigOrganizationManagedRule#maximum_execution_frequency}.
        :param resource_id_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#resource_id_scope ConfigOrganizationManagedRule#resource_id_scope}.
        :param resource_types_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#resource_types_scope ConfigOrganizationManagedRule#resource_types_scope}.
        :param tag_key_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#tag_key_scope ConfigOrganizationManagedRule#tag_key_scope}.
        :param tag_value_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#tag_value_scope ConfigOrganizationManagedRule#tag_value_scope}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#timeouts ConfigOrganizationManagedRule#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationManagedRule.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigOrganizationManagedRuleConfig(
            name=name,
            rule_identifier=rule_identifier,
            description=description,
            excluded_accounts=excluded_accounts,
            id=id,
            input_parameters=input_parameters,
            maximum_execution_frequency=maximum_execution_frequency,
            resource_id_scope=resource_id_scope,
            resource_types_scope=resource_types_scope,
            tag_key_scope=tag_key_scope,
            tag_value_scope=tag_value_scope,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#create ConfigOrganizationManagedRule#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#delete ConfigOrganizationManagedRule#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#update ConfigOrganizationManagedRule#update}.
        '''
        value = ConfigOrganizationManagedRuleTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExcludedAccounts")
    def reset_excluded_accounts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedAccounts", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInputParameters")
    def reset_input_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInputParameters", []))

    @jsii.member(jsii_name="resetMaximumExecutionFrequency")
    def reset_maximum_execution_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumExecutionFrequency", []))

    @jsii.member(jsii_name="resetResourceIdScope")
    def reset_resource_id_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceIdScope", []))

    @jsii.member(jsii_name="resetResourceTypesScope")
    def reset_resource_types_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTypesScope", []))

    @jsii.member(jsii_name="resetTagKeyScope")
    def reset_tag_key_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagKeyScope", []))

    @jsii.member(jsii_name="resetTagValueScope")
    def reset_tag_value_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagValueScope", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ConfigOrganizationManagedRuleTimeoutsOutputReference":
        return typing.cast("ConfigOrganizationManagedRuleTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludedAccountsInput")
    def excluded_accounts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedAccountsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputParametersInput")
    def input_parameters_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumExecutionFrequencyInput")
    def maximum_execution_frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maximumExecutionFrequencyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdScopeInput")
    def resource_id_scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceIdScopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypesScopeInput")
    def resource_types_scope_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceTypesScopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleIdentifierInput")
    def rule_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagKeyScopeInput")
    def tag_key_scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagKeyScopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagValueScopeInput")
    def tag_value_scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagValueScopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["ConfigOrganizationManagedRuleTimeouts", cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["ConfigOrganizationManagedRuleTimeouts", cdktf.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludedAccounts")
    def excluded_accounts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedAccounts"))

    @excluded_accounts.setter
    def excluded_accounts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "excluded_accounts").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedAccounts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputParameters")
    def input_parameters(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inputParameters"))

    @input_parameters.setter
    def input_parameters(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "input_parameters").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumExecutionFrequency")
    def maximum_execution_frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maximumExecutionFrequency"))

    @maximum_execution_frequency.setter
    def maximum_execution_frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "maximum_execution_frequency").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximumExecutionFrequency", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdScope")
    def resource_id_scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceIdScope"))

    @resource_id_scope.setter
    def resource_id_scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "resource_id_scope").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceIdScope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypesScope")
    def resource_types_scope(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceTypesScope"))

    @resource_types_scope.setter
    def resource_types_scope(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "resource_types_scope").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceTypesScope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleIdentifier")
    def rule_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleIdentifier"))

    @rule_identifier.setter
    def rule_identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "rule_identifier").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagKeyScope")
    def tag_key_scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagKeyScope"))

    @tag_key_scope.setter
    def tag_key_scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "tag_key_scope").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagKeyScope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagValueScope")
    def tag_value_scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagValueScope"))

    @tag_value_scope.setter
    def tag_value_scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRule, "tag_value_scope").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagValueScope", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationManagedRuleConfig",
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
        "rule_identifier": "ruleIdentifier",
        "description": "description",
        "excluded_accounts": "excludedAccounts",
        "id": "id",
        "input_parameters": "inputParameters",
        "maximum_execution_frequency": "maximumExecutionFrequency",
        "resource_id_scope": "resourceIdScope",
        "resource_types_scope": "resourceTypesScope",
        "tag_key_scope": "tagKeyScope",
        "tag_value_scope": "tagValueScope",
        "timeouts": "timeouts",
    },
)
class ConfigOrganizationManagedRuleConfig(cdktf.TerraformMetaArguments):
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
        rule_identifier: builtins.str,
        description: typing.Optional[builtins.str] = None,
        excluded_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[builtins.str] = None,
        maximum_execution_frequency: typing.Optional[builtins.str] = None,
        resource_id_scope: typing.Optional[builtins.str] = None,
        resource_types_scope: typing.Optional[typing.Sequence[builtins.str]] = None,
        tag_key_scope: typing.Optional[builtins.str] = None,
        tag_value_scope: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["ConfigOrganizationManagedRuleTimeouts", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#name ConfigOrganizationManagedRule#name}.
        :param rule_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#rule_identifier ConfigOrganizationManagedRule#rule_identifier}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#description ConfigOrganizationManagedRule#description}.
        :param excluded_accounts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#excluded_accounts ConfigOrganizationManagedRule#excluded_accounts}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#id ConfigOrganizationManagedRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input_parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#input_parameters ConfigOrganizationManagedRule#input_parameters}.
        :param maximum_execution_frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#maximum_execution_frequency ConfigOrganizationManagedRule#maximum_execution_frequency}.
        :param resource_id_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#resource_id_scope ConfigOrganizationManagedRule#resource_id_scope}.
        :param resource_types_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#resource_types_scope ConfigOrganizationManagedRule#resource_types_scope}.
        :param tag_key_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#tag_key_scope ConfigOrganizationManagedRule#tag_key_scope}.
        :param tag_value_scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#tag_value_scope ConfigOrganizationManagedRule#tag_value_scope}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#timeouts ConfigOrganizationManagedRule#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = ConfigOrganizationManagedRuleTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationManagedRuleConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument rule_identifier", value=rule_identifier, expected_type=type_hints["rule_identifier"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument excluded_accounts", value=excluded_accounts, expected_type=type_hints["excluded_accounts"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument input_parameters", value=input_parameters, expected_type=type_hints["input_parameters"])
            check_type(argname="argument maximum_execution_frequency", value=maximum_execution_frequency, expected_type=type_hints["maximum_execution_frequency"])
            check_type(argname="argument resource_id_scope", value=resource_id_scope, expected_type=type_hints["resource_id_scope"])
            check_type(argname="argument resource_types_scope", value=resource_types_scope, expected_type=type_hints["resource_types_scope"])
            check_type(argname="argument tag_key_scope", value=tag_key_scope, expected_type=type_hints["tag_key_scope"])
            check_type(argname="argument tag_value_scope", value=tag_value_scope, expected_type=type_hints["tag_value_scope"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "rule_identifier": rule_identifier,
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
        if excluded_accounts is not None:
            self._values["excluded_accounts"] = excluded_accounts
        if id is not None:
            self._values["id"] = id
        if input_parameters is not None:
            self._values["input_parameters"] = input_parameters
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency
        if resource_id_scope is not None:
            self._values["resource_id_scope"] = resource_id_scope
        if resource_types_scope is not None:
            self._values["resource_types_scope"] = resource_types_scope
        if tag_key_scope is not None:
            self._values["tag_key_scope"] = tag_key_scope
        if tag_value_scope is not None:
            self._values["tag_value_scope"] = tag_value_scope
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#name ConfigOrganizationManagedRule#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#rule_identifier ConfigOrganizationManagedRule#rule_identifier}.'''
        result = self._values.get("rule_identifier")
        assert result is not None, "Required property 'rule_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#description ConfigOrganizationManagedRule#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def excluded_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#excluded_accounts ConfigOrganizationManagedRule#excluded_accounts}.'''
        result = self._values.get("excluded_accounts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#id ConfigOrganizationManagedRule#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_parameters(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#input_parameters ConfigOrganizationManagedRule#input_parameters}.'''
        result = self._values.get("input_parameters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#maximum_execution_frequency ConfigOrganizationManagedRule#maximum_execution_frequency}.'''
        result = self._values.get("maximum_execution_frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_id_scope(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#resource_id_scope ConfigOrganizationManagedRule#resource_id_scope}.'''
        result = self._values.get("resource_id_scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_types_scope(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#resource_types_scope ConfigOrganizationManagedRule#resource_types_scope}.'''
        result = self._values.get("resource_types_scope")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tag_key_scope(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#tag_key_scope ConfigOrganizationManagedRule#tag_key_scope}.'''
        result = self._values.get("tag_key_scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_value_scope(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#tag_value_scope ConfigOrganizationManagedRule#tag_value_scope}.'''
        result = self._values.get("tag_value_scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ConfigOrganizationManagedRuleTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#timeouts ConfigOrganizationManagedRule#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ConfigOrganizationManagedRuleTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigOrganizationManagedRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationManagedRuleTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class ConfigOrganizationManagedRuleTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#create ConfigOrganizationManagedRule#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#delete ConfigOrganizationManagedRule#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#update ConfigOrganizationManagedRule#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigOrganizationManagedRuleTimeouts.__init__)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#create ConfigOrganizationManagedRule#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#delete ConfigOrganizationManagedRule#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_organization_managed_rule#update ConfigOrganizationManagedRule#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigOrganizationManagedRuleTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigOrganizationManagedRuleTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigOrganizationManagedRuleTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(ConfigOrganizationManagedRuleTimeoutsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRuleTimeoutsOutputReference, "create").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRuleTimeoutsOutputReference, "delete").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRuleTimeoutsOutputReference, "update").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ConfigOrganizationManagedRuleTimeouts, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ConfigOrganizationManagedRuleTimeouts, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ConfigOrganizationManagedRuleTimeouts, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigOrganizationManagedRuleTimeoutsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigRemediationConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigRemediationConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration aws_config_remediation_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        config_rule_name: builtins.str,
        target_id: builtins.str,
        target_type: builtins.str,
        automatic: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        execution_controls: typing.Optional[typing.Union["ConfigRemediationConfigurationExecutionControls", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        maximum_automatic_attempts: typing.Optional[jsii.Number] = None,
        parameter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigRemediationConfigurationParameter", typing.Dict[str, typing.Any]]]]] = None,
        resource_type: typing.Optional[builtins.str] = None,
        retry_attempt_seconds: typing.Optional[jsii.Number] = None,
        target_version: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration aws_config_remediation_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param config_rule_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#config_rule_name ConfigRemediationConfiguration#config_rule_name}.
        :param target_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#target_id ConfigRemediationConfiguration#target_id}.
        :param target_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#target_type ConfigRemediationConfiguration#target_type}.
        :param automatic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#automatic ConfigRemediationConfiguration#automatic}.
        :param execution_controls: execution_controls block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#execution_controls ConfigRemediationConfiguration#execution_controls}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#id ConfigRemediationConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param maximum_automatic_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#maximum_automatic_attempts ConfigRemediationConfiguration#maximum_automatic_attempts}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#parameter ConfigRemediationConfiguration#parameter}
        :param resource_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#resource_type ConfigRemediationConfiguration#resource_type}.
        :param retry_attempt_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#retry_attempt_seconds ConfigRemediationConfiguration#retry_attempt_seconds}.
        :param target_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#target_version ConfigRemediationConfiguration#target_version}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigRemediationConfiguration.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigRemediationConfigurationConfig(
            config_rule_name=config_rule_name,
            target_id=target_id,
            target_type=target_type,
            automatic=automatic,
            execution_controls=execution_controls,
            id=id,
            maximum_automatic_attempts=maximum_automatic_attempts,
            parameter=parameter,
            resource_type=resource_type,
            retry_attempt_seconds=retry_attempt_seconds,
            target_version=target_version,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putExecutionControls")
    def put_execution_controls(
        self,
        *,
        ssm_controls: typing.Optional[typing.Union["ConfigRemediationConfigurationExecutionControlsSsmControls", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param ssm_controls: ssm_controls block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#ssm_controls ConfigRemediationConfiguration#ssm_controls}
        '''
        value = ConfigRemediationConfigurationExecutionControls(
            ssm_controls=ssm_controls
        )

        return typing.cast(None, jsii.invoke(self, "putExecutionControls", [value]))

    @jsii.member(jsii_name="putParameter")
    def put_parameter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigRemediationConfigurationParameter", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigRemediationConfiguration.put_parameter)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putParameter", [value]))

    @jsii.member(jsii_name="resetAutomatic")
    def reset_automatic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomatic", []))

    @jsii.member(jsii_name="resetExecutionControls")
    def reset_execution_controls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExecutionControls", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaximumAutomaticAttempts")
    def reset_maximum_automatic_attempts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumAutomaticAttempts", []))

    @jsii.member(jsii_name="resetParameter")
    def reset_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameter", []))

    @jsii.member(jsii_name="resetResourceType")
    def reset_resource_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceType", []))

    @jsii.member(jsii_name="resetRetryAttemptSeconds")
    def reset_retry_attempt_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryAttemptSeconds", []))

    @jsii.member(jsii_name="resetTargetVersion")
    def reset_target_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetVersion", []))

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
    @jsii.member(jsii_name="executionControls")
    def execution_controls(
        self,
    ) -> "ConfigRemediationConfigurationExecutionControlsOutputReference":
        return typing.cast("ConfigRemediationConfigurationExecutionControlsOutputReference", jsii.get(self, "executionControls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> "ConfigRemediationConfigurationParameterList":
        return typing.cast("ConfigRemediationConfigurationParameterList", jsii.get(self, "parameter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticInput")
    def automatic_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "automaticInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configRuleNameInput")
    def config_rule_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configRuleNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionControlsInput")
    def execution_controls_input(
        self,
    ) -> typing.Optional["ConfigRemediationConfigurationExecutionControls"]:
        return typing.cast(typing.Optional["ConfigRemediationConfigurationExecutionControls"], jsii.get(self, "executionControlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumAutomaticAttemptsInput")
    def maximum_automatic_attempts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maximumAutomaticAttemptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterInput")
    def parameter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigRemediationConfigurationParameter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigRemediationConfigurationParameter"]]], jsii.get(self, "parameterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypeInput")
    def resource_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryAttemptSecondsInput")
    def retry_attempt_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryAttemptSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetIdInput")
    def target_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetTypeInput")
    def target_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetVersionInput")
    def target_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automatic")
    def automatic(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "automatic"))

    @automatic.setter
    def automatic(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfiguration, "automatic").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automatic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configRuleName"))

    @config_rule_name.setter
    def config_rule_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfiguration, "config_rule_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configRuleName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfiguration, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumAutomaticAttempts")
    def maximum_automatic_attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maximumAutomaticAttempts"))

    @maximum_automatic_attempts.setter
    def maximum_automatic_attempts(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfiguration, "maximum_automatic_attempts").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximumAutomaticAttempts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceType"))

    @resource_type.setter
    def resource_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfiguration, "resource_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryAttemptSeconds")
    def retry_attempt_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retryAttemptSeconds"))

    @retry_attempt_seconds.setter
    def retry_attempt_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfiguration, "retry_attempt_seconds").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retryAttemptSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetId")
    def target_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetId"))

    @target_id.setter
    def target_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfiguration, "target_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetType")
    def target_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetType"))

    @target_type.setter
    def target_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfiguration, "target_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetVersion")
    def target_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetVersion"))

    @target_version.setter
    def target_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfiguration, "target_version").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetVersion", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigRemediationConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "config_rule_name": "configRuleName",
        "target_id": "targetId",
        "target_type": "targetType",
        "automatic": "automatic",
        "execution_controls": "executionControls",
        "id": "id",
        "maximum_automatic_attempts": "maximumAutomaticAttempts",
        "parameter": "parameter",
        "resource_type": "resourceType",
        "retry_attempt_seconds": "retryAttemptSeconds",
        "target_version": "targetVersion",
    },
)
class ConfigRemediationConfigurationConfig(cdktf.TerraformMetaArguments):
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
        config_rule_name: builtins.str,
        target_id: builtins.str,
        target_type: builtins.str,
        automatic: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        execution_controls: typing.Optional[typing.Union["ConfigRemediationConfigurationExecutionControls", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        maximum_automatic_attempts: typing.Optional[jsii.Number] = None,
        parameter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["ConfigRemediationConfigurationParameter", typing.Dict[str, typing.Any]]]]] = None,
        resource_type: typing.Optional[builtins.str] = None,
        retry_attempt_seconds: typing.Optional[jsii.Number] = None,
        target_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Config.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param config_rule_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#config_rule_name ConfigRemediationConfiguration#config_rule_name}.
        :param target_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#target_id ConfigRemediationConfiguration#target_id}.
        :param target_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#target_type ConfigRemediationConfiguration#target_type}.
        :param automatic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#automatic ConfigRemediationConfiguration#automatic}.
        :param execution_controls: execution_controls block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#execution_controls ConfigRemediationConfiguration#execution_controls}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#id ConfigRemediationConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param maximum_automatic_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#maximum_automatic_attempts ConfigRemediationConfiguration#maximum_automatic_attempts}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#parameter ConfigRemediationConfiguration#parameter}
        :param resource_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#resource_type ConfigRemediationConfiguration#resource_type}.
        :param retry_attempt_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#retry_attempt_seconds ConfigRemediationConfiguration#retry_attempt_seconds}.
        :param target_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#target_version ConfigRemediationConfiguration#target_version}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(execution_controls, dict):
            execution_controls = ConfigRemediationConfigurationExecutionControls(**execution_controls)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigRemediationConfigurationConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument config_rule_name", value=config_rule_name, expected_type=type_hints["config_rule_name"])
            check_type(argname="argument target_id", value=target_id, expected_type=type_hints["target_id"])
            check_type(argname="argument target_type", value=target_type, expected_type=type_hints["target_type"])
            check_type(argname="argument automatic", value=automatic, expected_type=type_hints["automatic"])
            check_type(argname="argument execution_controls", value=execution_controls, expected_type=type_hints["execution_controls"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument maximum_automatic_attempts", value=maximum_automatic_attempts, expected_type=type_hints["maximum_automatic_attempts"])
            check_type(argname="argument parameter", value=parameter, expected_type=type_hints["parameter"])
            check_type(argname="argument resource_type", value=resource_type, expected_type=type_hints["resource_type"])
            check_type(argname="argument retry_attempt_seconds", value=retry_attempt_seconds, expected_type=type_hints["retry_attempt_seconds"])
            check_type(argname="argument target_version", value=target_version, expected_type=type_hints["target_version"])
        self._values: typing.Dict[str, typing.Any] = {
            "config_rule_name": config_rule_name,
            "target_id": target_id,
            "target_type": target_type,
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
        if automatic is not None:
            self._values["automatic"] = automatic
        if execution_controls is not None:
            self._values["execution_controls"] = execution_controls
        if id is not None:
            self._values["id"] = id
        if maximum_automatic_attempts is not None:
            self._values["maximum_automatic_attempts"] = maximum_automatic_attempts
        if parameter is not None:
            self._values["parameter"] = parameter
        if resource_type is not None:
            self._values["resource_type"] = resource_type
        if retry_attempt_seconds is not None:
            self._values["retry_attempt_seconds"] = retry_attempt_seconds
        if target_version is not None:
            self._values["target_version"] = target_version

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
    def config_rule_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#config_rule_name ConfigRemediationConfiguration#config_rule_name}.'''
        result = self._values.get("config_rule_name")
        assert result is not None, "Required property 'config_rule_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#target_id ConfigRemediationConfiguration#target_id}.'''
        result = self._values.get("target_id")
        assert result is not None, "Required property 'target_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#target_type ConfigRemediationConfiguration#target_type}.'''
        result = self._values.get("target_type")
        assert result is not None, "Required property 'target_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def automatic(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#automatic ConfigRemediationConfiguration#automatic}.'''
        result = self._values.get("automatic")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def execution_controls(
        self,
    ) -> typing.Optional["ConfigRemediationConfigurationExecutionControls"]:
        '''execution_controls block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#execution_controls ConfigRemediationConfiguration#execution_controls}
        '''
        result = self._values.get("execution_controls")
        return typing.cast(typing.Optional["ConfigRemediationConfigurationExecutionControls"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#id ConfigRemediationConfiguration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maximum_automatic_attempts(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#maximum_automatic_attempts ConfigRemediationConfiguration#maximum_automatic_attempts}.'''
        result = self._values.get("maximum_automatic_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigRemediationConfigurationParameter"]]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#parameter ConfigRemediationConfiguration#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ConfigRemediationConfigurationParameter"]]], result)

    @builtins.property
    def resource_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#resource_type ConfigRemediationConfiguration#resource_type}.'''
        result = self._values.get("resource_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retry_attempt_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#retry_attempt_seconds ConfigRemediationConfiguration#retry_attempt_seconds}.'''
        result = self._values.get("retry_attempt_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#target_version ConfigRemediationConfiguration#target_version}.'''
        result = self._values.get("target_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigRemediationConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigRemediationConfigurationExecutionControls",
    jsii_struct_bases=[],
    name_mapping={"ssm_controls": "ssmControls"},
)
class ConfigRemediationConfigurationExecutionControls:
    def __init__(
        self,
        *,
        ssm_controls: typing.Optional[typing.Union["ConfigRemediationConfigurationExecutionControlsSsmControls", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param ssm_controls: ssm_controls block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#ssm_controls ConfigRemediationConfiguration#ssm_controls}
        '''
        if isinstance(ssm_controls, dict):
            ssm_controls = ConfigRemediationConfigurationExecutionControlsSsmControls(**ssm_controls)
        if __debug__:
            type_hints = typing.get_type_hints(ConfigRemediationConfigurationExecutionControls.__init__)
            check_type(argname="argument ssm_controls", value=ssm_controls, expected_type=type_hints["ssm_controls"])
        self._values: typing.Dict[str, typing.Any] = {}
        if ssm_controls is not None:
            self._values["ssm_controls"] = ssm_controls

    @builtins.property
    def ssm_controls(
        self,
    ) -> typing.Optional["ConfigRemediationConfigurationExecutionControlsSsmControls"]:
        '''ssm_controls block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#ssm_controls ConfigRemediationConfiguration#ssm_controls}
        '''
        result = self._values.get("ssm_controls")
        return typing.cast(typing.Optional["ConfigRemediationConfigurationExecutionControlsSsmControls"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigRemediationConfigurationExecutionControls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigRemediationConfigurationExecutionControlsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigRemediationConfigurationExecutionControlsOutputReference",
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
            type_hints = typing.get_type_hints(ConfigRemediationConfigurationExecutionControlsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSsmControls")
    def put_ssm_controls(
        self,
        *,
        concurrent_execution_rate_percentage: typing.Optional[jsii.Number] = None,
        error_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param concurrent_execution_rate_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#concurrent_execution_rate_percentage ConfigRemediationConfiguration#concurrent_execution_rate_percentage}.
        :param error_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#error_percentage ConfigRemediationConfiguration#error_percentage}.
        '''
        value = ConfigRemediationConfigurationExecutionControlsSsmControls(
            concurrent_execution_rate_percentage=concurrent_execution_rate_percentage,
            error_percentage=error_percentage,
        )

        return typing.cast(None, jsii.invoke(self, "putSsmControls", [value]))

    @jsii.member(jsii_name="resetSsmControls")
    def reset_ssm_controls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsmControls", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssmControls")
    def ssm_controls(
        self,
    ) -> "ConfigRemediationConfigurationExecutionControlsSsmControlsOutputReference":
        return typing.cast("ConfigRemediationConfigurationExecutionControlsSsmControlsOutputReference", jsii.get(self, "ssmControls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssmControlsInput")
    def ssm_controls_input(
        self,
    ) -> typing.Optional["ConfigRemediationConfigurationExecutionControlsSsmControls"]:
        return typing.cast(typing.Optional["ConfigRemediationConfigurationExecutionControlsSsmControls"], jsii.get(self, "ssmControlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigRemediationConfigurationExecutionControls]:
        return typing.cast(typing.Optional[ConfigRemediationConfigurationExecutionControls], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigRemediationConfigurationExecutionControls],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationExecutionControlsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigRemediationConfigurationExecutionControlsSsmControls",
    jsii_struct_bases=[],
    name_mapping={
        "concurrent_execution_rate_percentage": "concurrentExecutionRatePercentage",
        "error_percentage": "errorPercentage",
    },
)
class ConfigRemediationConfigurationExecutionControlsSsmControls:
    def __init__(
        self,
        *,
        concurrent_execution_rate_percentage: typing.Optional[jsii.Number] = None,
        error_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param concurrent_execution_rate_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#concurrent_execution_rate_percentage ConfigRemediationConfiguration#concurrent_execution_rate_percentage}.
        :param error_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#error_percentage ConfigRemediationConfiguration#error_percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigRemediationConfigurationExecutionControlsSsmControls.__init__)
            check_type(argname="argument concurrent_execution_rate_percentage", value=concurrent_execution_rate_percentage, expected_type=type_hints["concurrent_execution_rate_percentage"])
            check_type(argname="argument error_percentage", value=error_percentage, expected_type=type_hints["error_percentage"])
        self._values: typing.Dict[str, typing.Any] = {}
        if concurrent_execution_rate_percentage is not None:
            self._values["concurrent_execution_rate_percentage"] = concurrent_execution_rate_percentage
        if error_percentage is not None:
            self._values["error_percentage"] = error_percentage

    @builtins.property
    def concurrent_execution_rate_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#concurrent_execution_rate_percentage ConfigRemediationConfiguration#concurrent_execution_rate_percentage}.'''
        result = self._values.get("concurrent_execution_rate_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def error_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#error_percentage ConfigRemediationConfiguration#error_percentage}.'''
        result = self._values.get("error_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigRemediationConfigurationExecutionControlsSsmControls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigRemediationConfigurationExecutionControlsSsmControlsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigRemediationConfigurationExecutionControlsSsmControlsOutputReference",
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
            type_hints = typing.get_type_hints(ConfigRemediationConfigurationExecutionControlsSsmControlsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConcurrentExecutionRatePercentage")
    def reset_concurrent_execution_rate_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConcurrentExecutionRatePercentage", []))

    @jsii.member(jsii_name="resetErrorPercentage")
    def reset_error_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetErrorPercentage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="concurrentExecutionRatePercentageInput")
    def concurrent_execution_rate_percentage_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "concurrentExecutionRatePercentageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorPercentageInput")
    def error_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "errorPercentageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="concurrentExecutionRatePercentage")
    def concurrent_execution_rate_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "concurrentExecutionRatePercentage"))

    @concurrent_execution_rate_percentage.setter
    def concurrent_execution_rate_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationExecutionControlsSsmControlsOutputReference, "concurrent_execution_rate_percentage").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "concurrentExecutionRatePercentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorPercentage")
    def error_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "errorPercentage"))

    @error_percentage.setter
    def error_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationExecutionControlsSsmControlsOutputReference, "error_percentage").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "errorPercentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigRemediationConfigurationExecutionControlsSsmControls]:
        return typing.cast(typing.Optional[ConfigRemediationConfigurationExecutionControlsSsmControls], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigRemediationConfigurationExecutionControlsSsmControls],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationExecutionControlsSsmControlsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.config.ConfigRemediationConfigurationParameter",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "resource_value": "resourceValue",
        "static_value": "staticValue",
        "static_values": "staticValues",
    },
)
class ConfigRemediationConfigurationParameter:
    def __init__(
        self,
        *,
        name: builtins.str,
        resource_value: typing.Optional[builtins.str] = None,
        static_value: typing.Optional[builtins.str] = None,
        static_values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#name ConfigRemediationConfiguration#name}.
        :param resource_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#resource_value ConfigRemediationConfiguration#resource_value}.
        :param static_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#static_value ConfigRemediationConfiguration#static_value}.
        :param static_values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#static_values ConfigRemediationConfiguration#static_values}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigRemediationConfigurationParameter.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_value", value=resource_value, expected_type=type_hints["resource_value"])
            check_type(argname="argument static_value", value=static_value, expected_type=type_hints["static_value"])
            check_type(argname="argument static_values", value=static_values, expected_type=type_hints["static_values"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if resource_value is not None:
            self._values["resource_value"] = resource_value
        if static_value is not None:
            self._values["static_value"] = static_value
        if static_values is not None:
            self._values["static_values"] = static_values

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#name ConfigRemediationConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#resource_value ConfigRemediationConfiguration#resource_value}.'''
        result = self._values.get("resource_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def static_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#static_value ConfigRemediationConfiguration#static_value}.'''
        result = self._values.get("static_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def static_values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/config_remediation_configuration#static_values ConfigRemediationConfiguration#static_values}.'''
        result = self._values.get("static_values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigRemediationConfigurationParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigRemediationConfigurationParameterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigRemediationConfigurationParameterList",
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
            type_hints = typing.get_type_hints(ConfigRemediationConfigurationParameterList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigRemediationConfigurationParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ConfigRemediationConfigurationParameterList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigRemediationConfigurationParameterOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationParameterList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationParameterList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationParameterList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigRemediationConfigurationParameter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigRemediationConfigurationParameter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ConfigRemediationConfigurationParameter]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationParameterList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class ConfigRemediationConfigurationParameterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.config.ConfigRemediationConfigurationParameterOutputReference",
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
            type_hints = typing.get_type_hints(ConfigRemediationConfigurationParameterOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetResourceValue")
    def reset_resource_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceValue", []))

    @jsii.member(jsii_name="resetStaticValue")
    def reset_static_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaticValue", []))

    @jsii.member(jsii_name="resetStaticValues")
    def reset_static_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaticValues", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceValueInput")
    def resource_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="staticValueInput")
    def static_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "staticValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="staticValuesInput")
    def static_values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "staticValuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationParameterOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceValue")
    def resource_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceValue"))

    @resource_value.setter
    def resource_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationParameterOutputReference, "resource_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="staticValue")
    def static_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "staticValue"))

    @static_value.setter
    def static_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationParameterOutputReference, "static_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "staticValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="staticValues")
    def static_values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "staticValues"))

    @static_values.setter
    def static_values(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationParameterOutputReference, "static_values").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "staticValues", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ConfigRemediationConfigurationParameter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ConfigRemediationConfigurationParameter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ConfigRemediationConfigurationParameter, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ConfigRemediationConfigurationParameterOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "ConfigAggregateAuthorization",
    "ConfigAggregateAuthorizationConfig",
    "ConfigConfigRule",
    "ConfigConfigRuleConfig",
    "ConfigConfigRuleScope",
    "ConfigConfigRuleScopeOutputReference",
    "ConfigConfigRuleSource",
    "ConfigConfigRuleSourceCustomPolicyDetails",
    "ConfigConfigRuleSourceCustomPolicyDetailsOutputReference",
    "ConfigConfigRuleSourceOutputReference",
    "ConfigConfigRuleSourceSourceDetail",
    "ConfigConfigRuleSourceSourceDetailList",
    "ConfigConfigRuleSourceSourceDetailOutputReference",
    "ConfigConfigurationAggregator",
    "ConfigConfigurationAggregatorAccountAggregationSource",
    "ConfigConfigurationAggregatorAccountAggregationSourceOutputReference",
    "ConfigConfigurationAggregatorConfig",
    "ConfigConfigurationAggregatorOrganizationAggregationSource",
    "ConfigConfigurationAggregatorOrganizationAggregationSourceOutputReference",
    "ConfigConfigurationRecorder",
    "ConfigConfigurationRecorderConfig",
    "ConfigConfigurationRecorderRecordingGroup",
    "ConfigConfigurationRecorderRecordingGroupOutputReference",
    "ConfigConfigurationRecorderStatus",
    "ConfigConfigurationRecorderStatusConfig",
    "ConfigConformancePack",
    "ConfigConformancePackConfig",
    "ConfigConformancePackInputParameter",
    "ConfigConformancePackInputParameterList",
    "ConfigConformancePackInputParameterOutputReference",
    "ConfigDeliveryChannel",
    "ConfigDeliveryChannelConfig",
    "ConfigDeliveryChannelSnapshotDeliveryProperties",
    "ConfigDeliveryChannelSnapshotDeliveryPropertiesOutputReference",
    "ConfigOrganizationConformancePack",
    "ConfigOrganizationConformancePackConfig",
    "ConfigOrganizationConformancePackInputParameter",
    "ConfigOrganizationConformancePackInputParameterList",
    "ConfigOrganizationConformancePackInputParameterOutputReference",
    "ConfigOrganizationConformancePackTimeouts",
    "ConfigOrganizationConformancePackTimeoutsOutputReference",
    "ConfigOrganizationCustomRule",
    "ConfigOrganizationCustomRuleConfig",
    "ConfigOrganizationCustomRuleTimeouts",
    "ConfigOrganizationCustomRuleTimeoutsOutputReference",
    "ConfigOrganizationManagedRule",
    "ConfigOrganizationManagedRuleConfig",
    "ConfigOrganizationManagedRuleTimeouts",
    "ConfigOrganizationManagedRuleTimeoutsOutputReference",
    "ConfigRemediationConfiguration",
    "ConfigRemediationConfigurationConfig",
    "ConfigRemediationConfigurationExecutionControls",
    "ConfigRemediationConfigurationExecutionControlsOutputReference",
    "ConfigRemediationConfigurationExecutionControlsSsmControls",
    "ConfigRemediationConfigurationExecutionControlsSsmControlsOutputReference",
    "ConfigRemediationConfigurationParameter",
    "ConfigRemediationConfigurationParameterList",
    "ConfigRemediationConfigurationParameterOutputReference",
]

publication.publish()
