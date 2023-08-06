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


class DataAwsNetworkfirewallFirewallPolicy(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy aws_networkfirewall_firewall_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        arn: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy aws_networkfirewall_firewall_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#arn DataAwsNetworkfirewallFirewallPolicy#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#id DataAwsNetworkfirewallFirewallPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#name DataAwsNetworkfirewallFirewallPolicy#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#tags DataAwsNetworkfirewallFirewallPolicy#tags}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicy.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsNetworkfirewallFirewallPolicyConfig(
            arn=arn,
            id=id,
            name=name,
            tags=tags,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetArn")
    def reset_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArn", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicy")
    def firewall_policy(
        self,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyList":
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyList", jsii.get(self, "firewallPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateToken")
    def update_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicy, "arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicy, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicy, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicy, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "arn": "arn",
        "id": "id",
        "name": "name",
        "tags": "tags",
    },
)
class DataAwsNetworkfirewallFirewallPolicyConfig(cdktf.TerraformMetaArguments):
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
        arn: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Network Firewall.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#arn DataAwsNetworkfirewallFirewallPolicy#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#id DataAwsNetworkfirewallFirewallPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#name DataAwsNetworkfirewallFirewallPolicy#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#tags DataAwsNetworkfirewallFirewallPolicy#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
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
        if arn is not None:
            self._values["arn"] = arn
        if id is not None:
            self._values["id"] = id
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

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
    def arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#arn DataAwsNetworkfirewallFirewallPolicy#arn}.'''
        result = self._values.get("arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#id DataAwsNetworkfirewallFirewallPolicy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#name DataAwsNetworkfirewallFirewallPolicy#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/networkfirewall_firewall_policy#tags DataAwsNetworkfirewallFirewallPolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNetworkfirewallFirewallPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicy",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsNetworkfirewallFirewallPolicyFirewallPolicy:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNetworkfirewallFirewallPolicyFirewallPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyList",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulDefaultActions")
    def stateful_default_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statefulDefaultActions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulEngineOptions")
    def stateful_engine_options(
        self,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsList":
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsList", jsii.get(self, "statefulEngineOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleGroupReference")
    def stateful_rule_group_reference(
        self,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList":
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList", jsii.get(self, "statefulRuleGroupReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessCustomAction")
    def stateless_custom_action(
        self,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList":
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList", jsii.get(self, "statelessCustomAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessDefaultActions")
    def stateless_default_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statelessDefaultActions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessFragmentDefaultActions")
    def stateless_fragment_default_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statelessFragmentDefaultActions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRuleGroupReference")
    def stateless_rule_group_reference(
        self,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList":
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList", jsii.get(self, "statelessRuleGroupReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicy]:
        return typing.cast(typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsList",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleOrder")
    def rule_order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleOrder"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions]:
        return typing.cast(typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference]:
        return typing.cast(typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionList",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishMetricAction")
    def publish_metric_action(
        self,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionList":
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionList", jsii.get(self, "publishMetricAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition]:
        return typing.cast(typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension]:
        return typing.cast(typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionList",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimension")
    def dimension(
        self,
    ) -> DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList:
        return typing.cast(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList, jsii.get(self, "dimension"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction]:
        return typing.cast(typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionDefinition")
    def action_definition(
        self,
    ) -> DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionList:
        return typing.cast(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionList, jsii.get(self, "actionDefinition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionName")
    def action_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction]:
        return typing.cast(typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference]:
        return typing.cast(typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallFirewall(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewall",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall aws_networkfirewall_firewall}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        firewall_policy_arn: builtins.str,
        name: builtins.str,
        subnet_mapping: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallSubnetMapping", typing.Dict[str, typing.Any]]]],
        vpc_id: builtins.str,
        delete_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        firewall_policy_change_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        subnet_change_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall aws_networkfirewall_firewall} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param firewall_policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_arn NetworkfirewallFirewall#firewall_policy_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#name NetworkfirewallFirewall#name}.
        :param subnet_mapping: subnet_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_mapping NetworkfirewallFirewall#subnet_mapping}
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#vpc_id NetworkfirewallFirewall#vpc_id}.
        :param delete_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#delete_protection NetworkfirewallFirewall#delete_protection}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#description NetworkfirewallFirewall#description}.
        :param firewall_policy_change_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_change_protection NetworkfirewallFirewall#firewall_policy_change_protection}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#id NetworkfirewallFirewall#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param subnet_change_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_change_protection NetworkfirewallFirewall#subnet_change_protection}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags NetworkfirewallFirewall#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags_all NetworkfirewallFirewall#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewall.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = NetworkfirewallFirewallConfig(
            firewall_policy_arn=firewall_policy_arn,
            name=name,
            subnet_mapping=subnet_mapping,
            vpc_id=vpc_id,
            delete_protection=delete_protection,
            description=description,
            firewall_policy_change_protection=firewall_policy_change_protection,
            id=id,
            subnet_change_protection=subnet_change_protection,
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

    @jsii.member(jsii_name="putSubnetMapping")
    def put_subnet_mapping(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallSubnetMapping", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewall.put_subnet_mapping)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSubnetMapping", [value]))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFirewallPolicyChangeProtection")
    def reset_firewall_policy_change_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirewallPolicyChangeProtection", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSubnetChangeProtection")
    def reset_subnet_change_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetChangeProtection", []))

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
    @jsii.member(jsii_name="firewallStatus")
    def firewall_status(self) -> "NetworkfirewallFirewallFirewallStatusList":
        return typing.cast("NetworkfirewallFirewallFirewallStatusList", jsii.get(self, "firewallStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetMapping")
    def subnet_mapping(self) -> "NetworkfirewallFirewallSubnetMappingList":
        return typing.cast("NetworkfirewallFirewallSubnetMappingList", jsii.get(self, "subnetMapping"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateToken")
    def update_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deleteProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicyArnInput")
    def firewall_policy_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "firewallPolicyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicyChangeProtectionInput")
    def firewall_policy_change_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "firewallPolicyChangeProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetChangeProtectionInput")
    def subnet_change_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "subnetChangeProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetMappingInput")
    def subnet_mapping_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallSubnetMapping"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallSubnetMapping"]]], jsii.get(self, "subnetMappingInput"))

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
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewall, "delete_protection").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewall, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicyArn")
    def firewall_policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firewallPolicyArn"))

    @firewall_policy_arn.setter
    def firewall_policy_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewall, "firewall_policy_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firewallPolicyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicyChangeProtection")
    def firewall_policy_change_protection(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "firewallPolicyChangeProtection"))

    @firewall_policy_change_protection.setter
    def firewall_policy_change_protection(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewall, "firewall_policy_change_protection").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firewallPolicyChangeProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewall, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewall, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetChangeProtection")
    def subnet_change_protection(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "subnetChangeProtection"))

    @subnet_change_protection.setter
    def subnet_change_protection(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewall, "subnet_change_protection").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetChangeProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewall, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewall, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewall, "vpc_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "firewall_policy_arn": "firewallPolicyArn",
        "name": "name",
        "subnet_mapping": "subnetMapping",
        "vpc_id": "vpcId",
        "delete_protection": "deleteProtection",
        "description": "description",
        "firewall_policy_change_protection": "firewallPolicyChangeProtection",
        "id": "id",
        "subnet_change_protection": "subnetChangeProtection",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class NetworkfirewallFirewallConfig(cdktf.TerraformMetaArguments):
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
        firewall_policy_arn: builtins.str,
        name: builtins.str,
        subnet_mapping: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallSubnetMapping", typing.Dict[str, typing.Any]]]],
        vpc_id: builtins.str,
        delete_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        firewall_policy_change_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        subnet_change_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Network Firewall.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param firewall_policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_arn NetworkfirewallFirewall#firewall_policy_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#name NetworkfirewallFirewall#name}.
        :param subnet_mapping: subnet_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_mapping NetworkfirewallFirewall#subnet_mapping}
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#vpc_id NetworkfirewallFirewall#vpc_id}.
        :param delete_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#delete_protection NetworkfirewallFirewall#delete_protection}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#description NetworkfirewallFirewall#description}.
        :param firewall_policy_change_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_change_protection NetworkfirewallFirewall#firewall_policy_change_protection}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#id NetworkfirewallFirewall#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param subnet_change_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_change_protection NetworkfirewallFirewall#subnet_change_protection}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags NetworkfirewallFirewall#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags_all NetworkfirewallFirewall#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument firewall_policy_arn", value=firewall_policy_arn, expected_type=type_hints["firewall_policy_arn"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument subnet_mapping", value=subnet_mapping, expected_type=type_hints["subnet_mapping"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument firewall_policy_change_protection", value=firewall_policy_change_protection, expected_type=type_hints["firewall_policy_change_protection"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument subnet_change_protection", value=subnet_change_protection, expected_type=type_hints["subnet_change_protection"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "firewall_policy_arn": firewall_policy_arn,
            "name": name,
            "subnet_mapping": subnet_mapping,
            "vpc_id": vpc_id,
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
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if firewall_policy_change_protection is not None:
            self._values["firewall_policy_change_protection"] = firewall_policy_change_protection
        if id is not None:
            self._values["id"] = id
        if subnet_change_protection is not None:
            self._values["subnet_change_protection"] = subnet_change_protection
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
    def firewall_policy_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_arn NetworkfirewallFirewall#firewall_policy_arn}.'''
        result = self._values.get("firewall_policy_arn")
        assert result is not None, "Required property 'firewall_policy_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#name NetworkfirewallFirewall#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_mapping(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallSubnetMapping"]]:
        '''subnet_mapping block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_mapping NetworkfirewallFirewall#subnet_mapping}
        '''
        result = self._values.get("subnet_mapping")
        assert result is not None, "Required property 'subnet_mapping' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallSubnetMapping"]], result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#vpc_id NetworkfirewallFirewall#vpc_id}.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#delete_protection NetworkfirewallFirewall#delete_protection}.'''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#description NetworkfirewallFirewall#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def firewall_policy_change_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#firewall_policy_change_protection NetworkfirewallFirewall#firewall_policy_change_protection}.'''
        result = self._values.get("firewall_policy_change_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#id NetworkfirewallFirewall#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_change_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_change_protection NetworkfirewallFirewall#subnet_change_protection}.'''
        result = self._values.get("subnet_change_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags NetworkfirewallFirewall#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#tags_all NetworkfirewallFirewall#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class NetworkfirewallFirewallFirewallStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallFirewallStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallFirewallStatusList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatusList",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallFirewallStatusList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallFirewallFirewallStatusOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallFirewallStatusList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallFirewallFirewallStatusOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class NetworkfirewallFirewallFirewallStatusOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatusOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallFirewallStatusOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="syncStates")
    def sync_states(self) -> "NetworkfirewallFirewallFirewallStatusSyncStatesList":
        return typing.cast("NetworkfirewallFirewallFirewallStatusSyncStatesList", jsii.get(self, "syncStates"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NetworkfirewallFirewallFirewallStatus]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallFirewallStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallFirewallStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatusSyncStates",
    jsii_struct_bases=[],
    name_mapping={},
)
class NetworkfirewallFirewallFirewallStatusSyncStates:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallFirewallStatusSyncStates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatusSyncStatesAttachment",
    jsii_struct_bases=[],
    name_mapping={},
)
class NetworkfirewallFirewallFirewallStatusSyncStatesAttachment:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallFirewallStatusSyncStatesAttachment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentList",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointId")
    def endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallFirewallStatusSyncStatesAttachment]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallFirewallStatusSyncStatesAttachment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallFirewallStatusSyncStatesAttachment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallFirewallFirewallStatusSyncStatesList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatusSyncStatesList",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallFirewallStatusSyncStatesList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallFirewallFirewallStatusSyncStatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallFirewallStatusSyncStatesList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallFirewallFirewallStatusSyncStatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusSyncStatesList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusSyncStatesList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusSyncStatesList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class NetworkfirewallFirewallFirewallStatusSyncStatesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallFirewallStatusSyncStatesOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallFirewallStatusSyncStatesOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attachment")
    def attachment(
        self,
    ) -> NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentList:
        return typing.cast(NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentList, jsii.get(self, "attachment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallFirewallStatusSyncStates]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallFirewallStatusSyncStates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallFirewallStatusSyncStates],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallFirewallStatusSyncStatesOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallFirewallPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy aws_networkfirewall_firewall_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        firewall_policy: typing.Union["NetworkfirewallFirewallPolicyFirewallPolicy", typing.Dict[str, typing.Any]],
        name: builtins.str,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy aws_networkfirewall_firewall_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param firewall_policy: firewall_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#firewall_policy NetworkfirewallFirewallPolicy#firewall_policy}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#name NetworkfirewallFirewallPolicy#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#description NetworkfirewallFirewallPolicy#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#id NetworkfirewallFirewallPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags NetworkfirewallFirewallPolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags_all NetworkfirewallFirewallPolicy#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicy.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = NetworkfirewallFirewallPolicyConfig(
            firewall_policy=firewall_policy,
            name=name,
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

    @jsii.member(jsii_name="putFirewallPolicy")
    def put_firewall_policy(
        self,
        *,
        stateless_default_actions: typing.Sequence[builtins.str],
        stateless_fragment_default_actions: typing.Sequence[builtins.str],
        stateful_default_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        stateful_engine_options: typing.Optional[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions", typing.Dict[str, typing.Any]]] = None,
        stateful_rule_group_reference: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference", typing.Dict[str, typing.Any]]]]] = None,
        stateless_custom_action: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction", typing.Dict[str, typing.Any]]]]] = None,
        stateless_rule_group_reference: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param stateless_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_default_actions NetworkfirewallFirewallPolicy#stateless_default_actions}.
        :param stateless_fragment_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_fragment_default_actions NetworkfirewallFirewallPolicy#stateless_fragment_default_actions}.
        :param stateful_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_default_actions NetworkfirewallFirewallPolicy#stateful_default_actions}.
        :param stateful_engine_options: stateful_engine_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_engine_options NetworkfirewallFirewallPolicy#stateful_engine_options}
        :param stateful_rule_group_reference: stateful_rule_group_reference block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_rule_group_reference NetworkfirewallFirewallPolicy#stateful_rule_group_reference}
        :param stateless_custom_action: stateless_custom_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_custom_action NetworkfirewallFirewallPolicy#stateless_custom_action}
        :param stateless_rule_group_reference: stateless_rule_group_reference block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_rule_group_reference NetworkfirewallFirewallPolicy#stateless_rule_group_reference}
        '''
        value = NetworkfirewallFirewallPolicyFirewallPolicy(
            stateless_default_actions=stateless_default_actions,
            stateless_fragment_default_actions=stateless_fragment_default_actions,
            stateful_default_actions=stateful_default_actions,
            stateful_engine_options=stateful_engine_options,
            stateful_rule_group_reference=stateful_rule_group_reference,
            stateless_custom_action=stateless_custom_action,
            stateless_rule_group_reference=stateless_rule_group_reference,
        )

        return typing.cast(None, jsii.invoke(self, "putFirewallPolicy", [value]))

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicy")
    def firewall_policy(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyOutputReference":
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyOutputReference", jsii.get(self, "firewallPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateToken")
    def update_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallPolicyInput")
    def firewall_policy_input(
        self,
    ) -> typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicy"]:
        return typing.cast(typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicy"], jsii.get(self, "firewallPolicyInput"))

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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicy, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicy, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicy, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicy, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicy, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "firewall_policy": "firewallPolicy",
        "name": "name",
        "description": "description",
        "id": "id",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class NetworkfirewallFirewallPolicyConfig(cdktf.TerraformMetaArguments):
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
        firewall_policy: typing.Union["NetworkfirewallFirewallPolicyFirewallPolicy", typing.Dict[str, typing.Any]],
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Network Firewall.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param firewall_policy: firewall_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#firewall_policy NetworkfirewallFirewallPolicy#firewall_policy}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#name NetworkfirewallFirewallPolicy#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#description NetworkfirewallFirewallPolicy#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#id NetworkfirewallFirewallPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags NetworkfirewallFirewallPolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags_all NetworkfirewallFirewallPolicy#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(firewall_policy, dict):
            firewall_policy = NetworkfirewallFirewallPolicyFirewallPolicy(**firewall_policy)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument firewall_policy", value=firewall_policy, expected_type=type_hints["firewall_policy"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "firewall_policy": firewall_policy,
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
    def firewall_policy(self) -> "NetworkfirewallFirewallPolicyFirewallPolicy":
        '''firewall_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#firewall_policy NetworkfirewallFirewallPolicy#firewall_policy}
        '''
        result = self._values.get("firewall_policy")
        assert result is not None, "Required property 'firewall_policy' is missing"
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicy", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#name NetworkfirewallFirewallPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#description NetworkfirewallFirewallPolicy#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#id NetworkfirewallFirewallPolicy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags NetworkfirewallFirewallPolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#tags_all NetworkfirewallFirewallPolicy#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "stateless_default_actions": "statelessDefaultActions",
        "stateless_fragment_default_actions": "statelessFragmentDefaultActions",
        "stateful_default_actions": "statefulDefaultActions",
        "stateful_engine_options": "statefulEngineOptions",
        "stateful_rule_group_reference": "statefulRuleGroupReference",
        "stateless_custom_action": "statelessCustomAction",
        "stateless_rule_group_reference": "statelessRuleGroupReference",
    },
)
class NetworkfirewallFirewallPolicyFirewallPolicy:
    def __init__(
        self,
        *,
        stateless_default_actions: typing.Sequence[builtins.str],
        stateless_fragment_default_actions: typing.Sequence[builtins.str],
        stateful_default_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        stateful_engine_options: typing.Optional[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions", typing.Dict[str, typing.Any]]] = None,
        stateful_rule_group_reference: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference", typing.Dict[str, typing.Any]]]]] = None,
        stateless_custom_action: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction", typing.Dict[str, typing.Any]]]]] = None,
        stateless_rule_group_reference: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param stateless_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_default_actions NetworkfirewallFirewallPolicy#stateless_default_actions}.
        :param stateless_fragment_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_fragment_default_actions NetworkfirewallFirewallPolicy#stateless_fragment_default_actions}.
        :param stateful_default_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_default_actions NetworkfirewallFirewallPolicy#stateful_default_actions}.
        :param stateful_engine_options: stateful_engine_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_engine_options NetworkfirewallFirewallPolicy#stateful_engine_options}
        :param stateful_rule_group_reference: stateful_rule_group_reference block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_rule_group_reference NetworkfirewallFirewallPolicy#stateful_rule_group_reference}
        :param stateless_custom_action: stateless_custom_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_custom_action NetworkfirewallFirewallPolicy#stateless_custom_action}
        :param stateless_rule_group_reference: stateless_rule_group_reference block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_rule_group_reference NetworkfirewallFirewallPolicy#stateless_rule_group_reference}
        '''
        if isinstance(stateful_engine_options, dict):
            stateful_engine_options = NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions(**stateful_engine_options)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicy.__init__)
            check_type(argname="argument stateless_default_actions", value=stateless_default_actions, expected_type=type_hints["stateless_default_actions"])
            check_type(argname="argument stateless_fragment_default_actions", value=stateless_fragment_default_actions, expected_type=type_hints["stateless_fragment_default_actions"])
            check_type(argname="argument stateful_default_actions", value=stateful_default_actions, expected_type=type_hints["stateful_default_actions"])
            check_type(argname="argument stateful_engine_options", value=stateful_engine_options, expected_type=type_hints["stateful_engine_options"])
            check_type(argname="argument stateful_rule_group_reference", value=stateful_rule_group_reference, expected_type=type_hints["stateful_rule_group_reference"])
            check_type(argname="argument stateless_custom_action", value=stateless_custom_action, expected_type=type_hints["stateless_custom_action"])
            check_type(argname="argument stateless_rule_group_reference", value=stateless_rule_group_reference, expected_type=type_hints["stateless_rule_group_reference"])
        self._values: typing.Dict[str, typing.Any] = {
            "stateless_default_actions": stateless_default_actions,
            "stateless_fragment_default_actions": stateless_fragment_default_actions,
        }
        if stateful_default_actions is not None:
            self._values["stateful_default_actions"] = stateful_default_actions
        if stateful_engine_options is not None:
            self._values["stateful_engine_options"] = stateful_engine_options
        if stateful_rule_group_reference is not None:
            self._values["stateful_rule_group_reference"] = stateful_rule_group_reference
        if stateless_custom_action is not None:
            self._values["stateless_custom_action"] = stateless_custom_action
        if stateless_rule_group_reference is not None:
            self._values["stateless_rule_group_reference"] = stateless_rule_group_reference

    @builtins.property
    def stateless_default_actions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_default_actions NetworkfirewallFirewallPolicy#stateless_default_actions}.'''
        result = self._values.get("stateless_default_actions")
        assert result is not None, "Required property 'stateless_default_actions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def stateless_fragment_default_actions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_fragment_default_actions NetworkfirewallFirewallPolicy#stateless_fragment_default_actions}.'''
        result = self._values.get("stateless_fragment_default_actions")
        assert result is not None, "Required property 'stateless_fragment_default_actions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def stateful_default_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_default_actions NetworkfirewallFirewallPolicy#stateful_default_actions}.'''
        result = self._values.get("stateful_default_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def stateful_engine_options(
        self,
    ) -> typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions"]:
        '''stateful_engine_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_engine_options NetworkfirewallFirewallPolicy#stateful_engine_options}
        '''
        result = self._values.get("stateful_engine_options")
        return typing.cast(typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions"], result)

    @builtins.property
    def stateful_rule_group_reference(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]]]:
        '''stateful_rule_group_reference block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateful_rule_group_reference NetworkfirewallFirewallPolicy#stateful_rule_group_reference}
        '''
        result = self._values.get("stateful_rule_group_reference")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]]], result)

    @builtins.property
    def stateless_custom_action(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]]]:
        '''stateless_custom_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_custom_action NetworkfirewallFirewallPolicy#stateless_custom_action}
        '''
        result = self._values.get("stateless_custom_action")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]]], result)

    @builtins.property
    def stateless_rule_group_reference(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]]]:
        '''stateless_rule_group_reference block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#stateless_rule_group_reference NetworkfirewallFirewallPolicy#stateless_rule_group_reference}
        '''
        result = self._values.get("stateless_rule_group_reference")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallPolicyFirewallPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putStatefulEngineOptions")
    def put_stateful_engine_options(self, *, rule_order: builtins.str) -> None:
        '''
        :param rule_order: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#rule_order NetworkfirewallFirewallPolicy#rule_order}.
        '''
        value = NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions(
            rule_order=rule_order
        )

        return typing.cast(None, jsii.invoke(self, "putStatefulEngineOptions", [value]))

    @jsii.member(jsii_name="putStatefulRuleGroupReference")
    def put_stateful_rule_group_reference(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyOutputReference.put_stateful_rule_group_reference)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStatefulRuleGroupReference", [value]))

    @jsii.member(jsii_name="putStatelessCustomAction")
    def put_stateless_custom_action(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyOutputReference.put_stateless_custom_action)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStatelessCustomAction", [value]))

    @jsii.member(jsii_name="putStatelessRuleGroupReference")
    def put_stateless_rule_group_reference(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyOutputReference.put_stateless_rule_group_reference)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStatelessRuleGroupReference", [value]))

    @jsii.member(jsii_name="resetStatefulDefaultActions")
    def reset_stateful_default_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatefulDefaultActions", []))

    @jsii.member(jsii_name="resetStatefulEngineOptions")
    def reset_stateful_engine_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatefulEngineOptions", []))

    @jsii.member(jsii_name="resetStatefulRuleGroupReference")
    def reset_stateful_rule_group_reference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatefulRuleGroupReference", []))

    @jsii.member(jsii_name="resetStatelessCustomAction")
    def reset_stateless_custom_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatelessCustomAction", []))

    @jsii.member(jsii_name="resetStatelessRuleGroupReference")
    def reset_stateless_rule_group_reference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatelessRuleGroupReference", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulEngineOptions")
    def stateful_engine_options(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference":
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference", jsii.get(self, "statefulEngineOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleGroupReference")
    def stateful_rule_group_reference(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList":
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList", jsii.get(self, "statefulRuleGroupReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessCustomAction")
    def stateless_custom_action(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList":
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList", jsii.get(self, "statelessCustomAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRuleGroupReference")
    def stateless_rule_group_reference(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList":
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList", jsii.get(self, "statelessRuleGroupReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulDefaultActionsInput")
    def stateful_default_actions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "statefulDefaultActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulEngineOptionsInput")
    def stateful_engine_options_input(
        self,
    ) -> typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions"]:
        return typing.cast(typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions"], jsii.get(self, "statefulEngineOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleGroupReferenceInput")
    def stateful_rule_group_reference_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference"]]], jsii.get(self, "statefulRuleGroupReferenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessCustomActionInput")
    def stateless_custom_action_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction"]]], jsii.get(self, "statelessCustomActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessDefaultActionsInput")
    def stateless_default_actions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "statelessDefaultActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessFragmentDefaultActionsInput")
    def stateless_fragment_default_actions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "statelessFragmentDefaultActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRuleGroupReferenceInput")
    def stateless_rule_group_reference_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference"]]], jsii.get(self, "statelessRuleGroupReferenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulDefaultActions")
    def stateful_default_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statefulDefaultActions"))

    @stateful_default_actions.setter
    def stateful_default_actions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyOutputReference, "stateful_default_actions").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statefulDefaultActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessDefaultActions")
    def stateless_default_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statelessDefaultActions"))

    @stateless_default_actions.setter
    def stateless_default_actions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyOutputReference, "stateless_default_actions").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statelessDefaultActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessFragmentDefaultActions")
    def stateless_fragment_default_actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statelessFragmentDefaultActions"))

    @stateless_fragment_default_actions.setter
    def stateless_fragment_default_actions(
        self,
        value: typing.List[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyOutputReference, "stateless_fragment_default_actions").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statelessFragmentDefaultActions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicy]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions",
    jsii_struct_bases=[],
    name_mapping={"rule_order": "ruleOrder"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions:
    def __init__(self, *, rule_order: builtins.str) -> None:
        '''
        :param rule_order: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#rule_order NetworkfirewallFirewallPolicy#rule_order}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions.__init__)
            check_type(argname="argument rule_order", value=rule_order, expected_type=type_hints["rule_order"])
        self._values: typing.Dict[str, typing.Any] = {
            "rule_order": rule_order,
        }

    @builtins.property
    def rule_order(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#rule_order NetworkfirewallFirewallPolicy#rule_order}.'''
        result = self._values.get("rule_order")
        assert result is not None, "Required property 'rule_order' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleOrderInput")
    def rule_order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleOrderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleOrder")
    def rule_order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleOrder"))

    @rule_order.setter
    def rule_order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference, "rule_order").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleOrder", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference",
    jsii_struct_bases=[],
    name_mapping={"resource_arn": "resourceArn", "priority": "priority"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference:
    def __init__(
        self,
        *,
        resource_arn: builtins.str,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#resource_arn NetworkfirewallFirewallPolicy#resource_arn}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#priority NetworkfirewallFirewallPolicy#priority}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference.__init__)
            check_type(argname="argument resource_arn", value=resource_arn, expected_type=type_hints["resource_arn"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
        self._values: typing.Dict[str, typing.Any] = {
            "resource_arn": resource_arn,
        }
        if priority is not None:
            self._values["priority"] = priority

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#resource_arn NetworkfirewallFirewallPolicy#resource_arn}.'''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#priority NetworkfirewallFirewallPolicy#priority}.'''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetPriority")
    def reset_priority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPriority", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArnInput")
    def resource_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference, "priority").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceArn"))

    @resource_arn.setter
    def resource_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference, "resource_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction",
    jsii_struct_bases=[],
    name_mapping={
        "action_definition": "actionDefinition",
        "action_name": "actionName",
    },
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction:
    def __init__(
        self,
        *,
        action_definition: typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition", typing.Dict[str, typing.Any]],
        action_name: builtins.str,
    ) -> None:
        '''
        :param action_definition: action_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#action_definition NetworkfirewallFirewallPolicy#action_definition}
        :param action_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#action_name NetworkfirewallFirewallPolicy#action_name}.
        '''
        if isinstance(action_definition, dict):
            action_definition = NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition(**action_definition)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction.__init__)
            check_type(argname="argument action_definition", value=action_definition, expected_type=type_hints["action_definition"])
            check_type(argname="argument action_name", value=action_name, expected_type=type_hints["action_name"])
        self._values: typing.Dict[str, typing.Any] = {
            "action_definition": action_definition,
            "action_name": action_name,
        }

    @builtins.property
    def action_definition(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition":
        '''action_definition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#action_definition NetworkfirewallFirewallPolicy#action_definition}
        '''
        result = self._values.get("action_definition")
        assert result is not None, "Required property 'action_definition' is missing"
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition", result)

    @builtins.property
    def action_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#action_name NetworkfirewallFirewallPolicy#action_name}.'''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition",
    jsii_struct_bases=[],
    name_mapping={"publish_metric_action": "publishMetricAction"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition:
    def __init__(
        self,
        *,
        publish_metric_action: typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction", typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param publish_metric_action: publish_metric_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#publish_metric_action NetworkfirewallFirewallPolicy#publish_metric_action}
        '''
        if isinstance(publish_metric_action, dict):
            publish_metric_action = NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction(**publish_metric_action)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition.__init__)
            check_type(argname="argument publish_metric_action", value=publish_metric_action, expected_type=type_hints["publish_metric_action"])
        self._values: typing.Dict[str, typing.Any] = {
            "publish_metric_action": publish_metric_action,
        }

    @builtins.property
    def publish_metric_action(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction":
        '''publish_metric_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#publish_metric_action NetworkfirewallFirewallPolicy#publish_metric_action}
        '''
        result = self._values.get("publish_metric_action")
        assert result is not None, "Required property 'publish_metric_action' is missing"
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPublishMetricAction")
    def put_publish_metric_action(
        self,
        *,
        dimension: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#dimension NetworkfirewallFirewallPolicy#dimension}
        '''
        value = NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction(
            dimension=dimension
        )

        return typing.cast(None, jsii.invoke(self, "putPublishMetricAction", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishMetricAction")
    def publish_metric_action(
        self,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference":
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference", jsii.get(self, "publishMetricAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishMetricActionInput")
    def publish_metric_action_input(
        self,
    ) -> typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction"]:
        return typing.cast(typing.Optional["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction"], jsii.get(self, "publishMetricActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction",
    jsii_struct_bases=[],
    name_mapping={"dimension": "dimension"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction:
    def __init__(
        self,
        *,
        dimension: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#dimension NetworkfirewallFirewallPolicy#dimension}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction.__init__)
            check_type(argname="argument dimension", value=dimension, expected_type=type_hints["dimension"])
        self._values: typing.Dict[str, typing.Any] = {
            "dimension": dimension,
        }

    @builtins.property
    def dimension(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension"]]:
        '''dimension block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#dimension NetworkfirewallFirewallPolicy#dimension}
        '''
        result = self._values.get("dimension")
        assert result is not None, "Required property 'dimension' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#value NetworkfirewallFirewallPolicy#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension.__init__)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#value NetworkfirewallFirewallPolicy#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference, "value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDimension")
    def put_dimension(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension, typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference.put_dimension)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDimension", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimension")
    def dimension(
        self,
    ) -> NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList:
        return typing.cast(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList, jsii.get(self, "dimension"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimensionInput")
    def dimension_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension]]], jsii.get(self, "dimensionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putActionDefinition")
    def put_action_definition(
        self,
        *,
        publish_metric_action: typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction, typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param publish_metric_action: publish_metric_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#publish_metric_action NetworkfirewallFirewallPolicy#publish_metric_action}
        '''
        value = NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition(
            publish_metric_action=publish_metric_action
        )

        return typing.cast(None, jsii.invoke(self, "putActionDefinition", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionDefinition")
    def action_definition(
        self,
    ) -> NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference:
        return typing.cast(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference, jsii.get(self, "actionDefinition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionDefinitionInput")
    def action_definition_input(
        self,
    ) -> typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition]:
        return typing.cast(typing.Optional[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition], jsii.get(self, "actionDefinitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionNameInput")
    def action_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionName")
    def action_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionName"))

    @action_name.setter
    def action_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference, "action_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference",
    jsii_struct_bases=[],
    name_mapping={"priority": "priority", "resource_arn": "resourceArn"},
)
class NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference:
    def __init__(self, *, priority: jsii.Number, resource_arn: builtins.str) -> None:
        '''
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#priority NetworkfirewallFirewallPolicy#priority}.
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#resource_arn NetworkfirewallFirewallPolicy#resource_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference.__init__)
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument resource_arn", value=resource_arn, expected_type=type_hints["resource_arn"])
        self._values: typing.Dict[str, typing.Any] = {
            "priority": priority,
            "resource_arn": resource_arn,
        }

    @builtins.property
    def priority(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#priority NetworkfirewallFirewallPolicy#priority}.'''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall_policy#resource_arn NetworkfirewallFirewallPolicy#resource_arn}.'''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArnInput")
    def resource_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference, "priority").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceArn"))

    @resource_arn.setter
    def resource_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference, "resource_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallSubnetMapping",
    jsii_struct_bases=[],
    name_mapping={"subnet_id": "subnetId"},
)
class NetworkfirewallFirewallSubnetMapping:
    def __init__(self, *, subnet_id: builtins.str) -> None:
        '''
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_id NetworkfirewallFirewall#subnet_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallSubnetMapping.__init__)
            check_type(argname="argument subnet_id", value=subnet_id, expected_type=type_hints["subnet_id"])
        self._values: typing.Dict[str, typing.Any] = {
            "subnet_id": subnet_id,
        }

    @builtins.property
    def subnet_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_firewall#subnet_id NetworkfirewallFirewall#subnet_id}.'''
        result = self._values.get("subnet_id")
        assert result is not None, "Required property 'subnet_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallFirewallSubnetMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallFirewallSubnetMappingList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallSubnetMappingList",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallSubnetMappingList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallFirewallSubnetMappingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallFirewallSubnetMappingList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallFirewallSubnetMappingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallSubnetMappingList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallSubnetMappingList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallSubnetMappingList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallSubnetMapping]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallSubnetMapping]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallFirewallSubnetMapping]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallSubnetMappingList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallFirewallSubnetMappingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallFirewallSubnetMappingOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallFirewallSubnetMappingOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdInput")
    def subnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @subnet_id.setter
    def subnet_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallSubnetMappingOutputReference, "subnet_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallFirewallSubnetMapping, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallFirewallSubnetMapping, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallFirewallSubnetMapping, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallFirewallSubnetMappingOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallLoggingConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration aws_networkfirewall_logging_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        firewall_arn: builtins.str,
        logging_configuration: typing.Union["NetworkfirewallLoggingConfigurationLoggingConfiguration", typing.Dict[str, typing.Any]],
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration aws_networkfirewall_logging_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param firewall_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#firewall_arn NetworkfirewallLoggingConfiguration#firewall_arn}.
        :param logging_configuration: logging_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#logging_configuration NetworkfirewallLoggingConfiguration#logging_configuration}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#id NetworkfirewallLoggingConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallLoggingConfiguration.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = NetworkfirewallLoggingConfigurationConfig(
            firewall_arn=firewall_arn,
            logging_configuration=logging_configuration,
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

    @jsii.member(jsii_name="putLoggingConfiguration")
    def put_logging_configuration(
        self,
        *,
        log_destination_config: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param log_destination_config: log_destination_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination_config NetworkfirewallLoggingConfiguration#log_destination_config}
        '''
        value = NetworkfirewallLoggingConfigurationLoggingConfiguration(
            log_destination_config=log_destination_config
        )

        return typing.cast(None, jsii.invoke(self, "putLoggingConfiguration", [value]))

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
    @jsii.member(jsii_name="loggingConfiguration")
    def logging_configuration(
        self,
    ) -> "NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference":
        return typing.cast("NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference", jsii.get(self, "loggingConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallArnInput")
    def firewall_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "firewallArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingConfigurationInput")
    def logging_configuration_input(
        self,
    ) -> typing.Optional["NetworkfirewallLoggingConfigurationLoggingConfiguration"]:
        return typing.cast(typing.Optional["NetworkfirewallLoggingConfigurationLoggingConfiguration"], jsii.get(self, "loggingConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallArn")
    def firewall_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firewallArn"))

    @firewall_arn.setter
    def firewall_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfiguration, "firewall_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firewallArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfiguration, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "firewall_arn": "firewallArn",
        "logging_configuration": "loggingConfiguration",
        "id": "id",
    },
)
class NetworkfirewallLoggingConfigurationConfig(cdktf.TerraformMetaArguments):
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
        firewall_arn: builtins.str,
        logging_configuration: typing.Union["NetworkfirewallLoggingConfigurationLoggingConfiguration", typing.Dict[str, typing.Any]],
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Network Firewall.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param firewall_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#firewall_arn NetworkfirewallLoggingConfiguration#firewall_arn}.
        :param logging_configuration: logging_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#logging_configuration NetworkfirewallLoggingConfiguration#logging_configuration}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#id NetworkfirewallLoggingConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(logging_configuration, dict):
            logging_configuration = NetworkfirewallLoggingConfigurationLoggingConfiguration(**logging_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallLoggingConfigurationConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument firewall_arn", value=firewall_arn, expected_type=type_hints["firewall_arn"])
            check_type(argname="argument logging_configuration", value=logging_configuration, expected_type=type_hints["logging_configuration"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "firewall_arn": firewall_arn,
            "logging_configuration": logging_configuration,
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
    def firewall_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#firewall_arn NetworkfirewallLoggingConfiguration#firewall_arn}.'''
        result = self._values.get("firewall_arn")
        assert result is not None, "Required property 'firewall_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging_configuration(
        self,
    ) -> "NetworkfirewallLoggingConfigurationLoggingConfiguration":
        '''logging_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#logging_configuration NetworkfirewallLoggingConfiguration#logging_configuration}
        '''
        result = self._values.get("logging_configuration")
        assert result is not None, "Required property 'logging_configuration' is missing"
        return typing.cast("NetworkfirewallLoggingConfigurationLoggingConfiguration", result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#id NetworkfirewallLoggingConfiguration#id}.

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
        return "NetworkfirewallLoggingConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfigurationLoggingConfiguration",
    jsii_struct_bases=[],
    name_mapping={"log_destination_config": "logDestinationConfig"},
)
class NetworkfirewallLoggingConfigurationLoggingConfiguration:
    def __init__(
        self,
        *,
        log_destination_config: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param log_destination_config: log_destination_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination_config NetworkfirewallLoggingConfiguration#log_destination_config}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallLoggingConfigurationLoggingConfiguration.__init__)
            check_type(argname="argument log_destination_config", value=log_destination_config, expected_type=type_hints["log_destination_config"])
        self._values: typing.Dict[str, typing.Any] = {
            "log_destination_config": log_destination_config,
        }

    @builtins.property
    def log_destination_config(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig"]]:
        '''log_destination_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination_config NetworkfirewallLoggingConfiguration#log_destination_config}
        '''
        result = self._values.get("log_destination_config")
        assert result is not None, "Required property 'log_destination_config' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallLoggingConfigurationLoggingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig",
    jsii_struct_bases=[],
    name_mapping={
        "log_destination": "logDestination",
        "log_destination_type": "logDestinationType",
        "log_type": "logType",
    },
)
class NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig:
    def __init__(
        self,
        *,
        log_destination: typing.Mapping[builtins.str, builtins.str],
        log_destination_type: builtins.str,
        log_type: builtins.str,
    ) -> None:
        '''
        :param log_destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination NetworkfirewallLoggingConfiguration#log_destination}.
        :param log_destination_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination_type NetworkfirewallLoggingConfiguration#log_destination_type}.
        :param log_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_type NetworkfirewallLoggingConfiguration#log_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig.__init__)
            check_type(argname="argument log_destination", value=log_destination, expected_type=type_hints["log_destination"])
            check_type(argname="argument log_destination_type", value=log_destination_type, expected_type=type_hints["log_destination_type"])
            check_type(argname="argument log_type", value=log_type, expected_type=type_hints["log_type"])
        self._values: typing.Dict[str, typing.Any] = {
            "log_destination": log_destination,
            "log_destination_type": log_destination_type,
            "log_type": log_type,
        }

    @builtins.property
    def log_destination(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination NetworkfirewallLoggingConfiguration#log_destination}.'''
        result = self._values.get("log_destination")
        assert result is not None, "Required property 'log_destination' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def log_destination_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_destination_type NetworkfirewallLoggingConfiguration#log_destination_type}.'''
        result = self._values.get("log_destination_type")
        assert result is not None, "Required property 'log_destination_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_logging_configuration#log_type NetworkfirewallLoggingConfiguration#log_type}.'''
        result = self._values.get("log_type")
        assert result is not None, "Required property 'log_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList",
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
            type_hints = typing.get_type_hints(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDestinationInput")
    def log_destination_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "logDestinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDestinationTypeInput")
    def log_destination_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logDestinationTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logTypeInput")
    def log_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDestination")
    def log_destination(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "logDestination"))

    @log_destination.setter
    def log_destination(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigOutputReference, "log_destination").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logDestination", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDestinationType")
    def log_destination_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logDestinationType"))

    @log_destination_type.setter
    def log_destination_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigOutputReference, "log_destination_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logDestinationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logType")
    def log_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logType"))

    @log_type.setter
    def log_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigOutputReference, "log_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putLogDestinationConfig")
    def put_log_destination_config(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig, typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference.put_log_destination_config)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLogDestinationConfig", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDestinationConfig")
    def log_destination_config(
        self,
    ) -> NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList:
        return typing.cast(NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList, jsii.get(self, "logDestinationConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDestinationConfigInput")
    def log_destination_config_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig]]], jsii.get(self, "logDestinationConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallLoggingConfigurationLoggingConfiguration]:
        return typing.cast(typing.Optional[NetworkfirewallLoggingConfigurationLoggingConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallLoggingConfigurationLoggingConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallResourcePolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallResourcePolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy aws_networkfirewall_resource_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        policy: builtins.str,
        resource_arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy aws_networkfirewall_resource_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#policy NetworkfirewallResourcePolicy#policy}.
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#resource_arn NetworkfirewallResourcePolicy#resource_arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#id NetworkfirewallResourcePolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallResourcePolicy.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = NetworkfirewallResourcePolicyConfig(
            policy=policy,
            resource_arn=resource_arn,
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
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArnInput")
    def resource_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallResourcePolicy, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallResourcePolicy, "policy").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceArn"))

    @resource_arn.setter
    def resource_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallResourcePolicy, "resource_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallResourcePolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "policy": "policy",
        "resource_arn": "resourceArn",
        "id": "id",
    },
)
class NetworkfirewallResourcePolicyConfig(cdktf.TerraformMetaArguments):
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
        policy: builtins.str,
        resource_arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Network Firewall.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#policy NetworkfirewallResourcePolicy#policy}.
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#resource_arn NetworkfirewallResourcePolicy#resource_arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#id NetworkfirewallResourcePolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallResourcePolicyConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument resource_arn", value=resource_arn, expected_type=type_hints["resource_arn"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "policy": policy,
            "resource_arn": resource_arn,
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
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#policy NetworkfirewallResourcePolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#resource_arn NetworkfirewallResourcePolicy#resource_arn}.'''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_resource_policy#id NetworkfirewallResourcePolicy#id}.

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
        return "NetworkfirewallResourcePolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group aws_networkfirewall_rule_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        capacity: jsii.Number,
        name: builtins.str,
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        rule_group: typing.Optional[typing.Union["NetworkfirewallRuleGroupRuleGroup", typing.Dict[str, typing.Any]]] = None,
        rules: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group aws_networkfirewall_rule_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#capacity NetworkfirewallRuleGroup#capacity}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#name NetworkfirewallRuleGroup#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#type NetworkfirewallRuleGroup#type}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#description NetworkfirewallRuleGroup#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#id NetworkfirewallRuleGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rule_group: rule_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_group NetworkfirewallRuleGroup#rule_group}
        :param rules: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules NetworkfirewallRuleGroup#rules}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags NetworkfirewallRuleGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags_all NetworkfirewallRuleGroup#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroup.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = NetworkfirewallRuleGroupConfig(
            capacity=capacity,
            name=name,
            type=type,
            description=description,
            id=id,
            rule_group=rule_group,
            rules=rules,
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

    @jsii.member(jsii_name="putRuleGroup")
    def put_rule_group(
        self,
        *,
        rules_source: typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSource", typing.Dict[str, typing.Any]],
        rule_variables: typing.Optional[typing.Union["NetworkfirewallRuleGroupRuleGroupRuleVariables", typing.Dict[str, typing.Any]]] = None,
        stateful_rule_options: typing.Optional[typing.Union["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param rules_source: rules_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source NetworkfirewallRuleGroup#rules_source}
        :param rule_variables: rule_variables block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_variables NetworkfirewallRuleGroup#rule_variables}
        :param stateful_rule_options: stateful_rule_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule_options NetworkfirewallRuleGroup#stateful_rule_options}
        '''
        value = NetworkfirewallRuleGroupRuleGroup(
            rules_source=rules_source,
            rule_variables=rule_variables,
            stateful_rule_options=stateful_rule_options,
        )

        return typing.cast(None, jsii.invoke(self, "putRuleGroup", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRuleGroup")
    def reset_rule_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuleGroup", []))

    @jsii.member(jsii_name="resetRules")
    def reset_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRules", []))

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
    @jsii.member(jsii_name="ruleGroup")
    def rule_group(self) -> "NetworkfirewallRuleGroupRuleGroupOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupOutputReference", jsii.get(self, "ruleGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateToken")
    def update_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capacityInput")
    def capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "capacityInput"))

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
    @jsii.member(jsii_name="ruleGroupInput")
    def rule_group_input(self) -> typing.Optional["NetworkfirewallRuleGroupRuleGroup"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroup"], jsii.get(self, "ruleGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesInput")
    def rules_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rulesInput"))

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
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "capacity"))

    @capacity.setter
    def capacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroup, "capacity").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroup, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroup, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroup, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rules")
    def rules(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rules"))

    @rules.setter
    def rules(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroup, "rules").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rules", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroup, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroup, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroup, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "capacity": "capacity",
        "name": "name",
        "type": "type",
        "description": "description",
        "id": "id",
        "rule_group": "ruleGroup",
        "rules": "rules",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class NetworkfirewallRuleGroupConfig(cdktf.TerraformMetaArguments):
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
        capacity: jsii.Number,
        name: builtins.str,
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        rule_group: typing.Optional[typing.Union["NetworkfirewallRuleGroupRuleGroup", typing.Dict[str, typing.Any]]] = None,
        rules: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Network Firewall.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#capacity NetworkfirewallRuleGroup#capacity}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#name NetworkfirewallRuleGroup#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#type NetworkfirewallRuleGroup#type}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#description NetworkfirewallRuleGroup#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#id NetworkfirewallRuleGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rule_group: rule_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_group NetworkfirewallRuleGroup#rule_group}
        :param rules: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules NetworkfirewallRuleGroup#rules}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags NetworkfirewallRuleGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags_all NetworkfirewallRuleGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(rule_group, dict):
            rule_group = NetworkfirewallRuleGroupRuleGroup(**rule_group)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument rule_group", value=rule_group, expected_type=type_hints["rule_group"])
            check_type(argname="argument rules", value=rules, expected_type=type_hints["rules"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "capacity": capacity,
            "name": name,
            "type": type,
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
        if rule_group is not None:
            self._values["rule_group"] = rule_group
        if rules is not None:
            self._values["rules"] = rules
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
    def capacity(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#capacity NetworkfirewallRuleGroup#capacity}.'''
        result = self._values.get("capacity")
        assert result is not None, "Required property 'capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#name NetworkfirewallRuleGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#type NetworkfirewallRuleGroup#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#description NetworkfirewallRuleGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#id NetworkfirewallRuleGroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rule_group(self) -> typing.Optional["NetworkfirewallRuleGroupRuleGroup"]:
        '''rule_group block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_group NetworkfirewallRuleGroup#rule_group}
        '''
        result = self._values.get("rule_group")
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroup"], result)

    @builtins.property
    def rules(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules NetworkfirewallRuleGroup#rules}.'''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags NetworkfirewallRuleGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tags_all NetworkfirewallRuleGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroup",
    jsii_struct_bases=[],
    name_mapping={
        "rules_source": "rulesSource",
        "rule_variables": "ruleVariables",
        "stateful_rule_options": "statefulRuleOptions",
    },
)
class NetworkfirewallRuleGroupRuleGroup:
    def __init__(
        self,
        *,
        rules_source: typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSource", typing.Dict[str, typing.Any]],
        rule_variables: typing.Optional[typing.Union["NetworkfirewallRuleGroupRuleGroupRuleVariables", typing.Dict[str, typing.Any]]] = None,
        stateful_rule_options: typing.Optional[typing.Union["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param rules_source: rules_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source NetworkfirewallRuleGroup#rules_source}
        :param rule_variables: rule_variables block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_variables NetworkfirewallRuleGroup#rule_variables}
        :param stateful_rule_options: stateful_rule_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule_options NetworkfirewallRuleGroup#stateful_rule_options}
        '''
        if isinstance(rules_source, dict):
            rules_source = NetworkfirewallRuleGroupRuleGroupRulesSource(**rules_source)
        if isinstance(rule_variables, dict):
            rule_variables = NetworkfirewallRuleGroupRuleGroupRuleVariables(**rule_variables)
        if isinstance(stateful_rule_options, dict):
            stateful_rule_options = NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions(**stateful_rule_options)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroup.__init__)
            check_type(argname="argument rules_source", value=rules_source, expected_type=type_hints["rules_source"])
            check_type(argname="argument rule_variables", value=rule_variables, expected_type=type_hints["rule_variables"])
            check_type(argname="argument stateful_rule_options", value=stateful_rule_options, expected_type=type_hints["stateful_rule_options"])
        self._values: typing.Dict[str, typing.Any] = {
            "rules_source": rules_source,
        }
        if rule_variables is not None:
            self._values["rule_variables"] = rule_variables
        if stateful_rule_options is not None:
            self._values["stateful_rule_options"] = stateful_rule_options

    @builtins.property
    def rules_source(self) -> "NetworkfirewallRuleGroupRuleGroupRulesSource":
        '''rules_source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source NetworkfirewallRuleGroup#rules_source}
        '''
        result = self._values.get("rules_source")
        assert result is not None, "Required property 'rules_source' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSource", result)

    @builtins.property
    def rule_variables(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariables"]:
        '''rule_variables block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_variables NetworkfirewallRuleGroup#rule_variables}
        '''
        result = self._values.get("rule_variables")
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariables"], result)

    @builtins.property
    def stateful_rule_options(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions"]:
        '''stateful_rule_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule_options NetworkfirewallRuleGroup#stateful_rule_options}
        '''
        result = self._values.get("stateful_rule_options")
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRulesSource")
    def put_rules_source(
        self,
        *,
        rules_source_list: typing.Optional[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList", typing.Dict[str, typing.Any]]] = None,
        rules_string: typing.Optional[builtins.str] = None,
        stateful_rule: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule", typing.Dict[str, typing.Any]]]]] = None,
        stateless_rules_and_custom_actions: typing.Optional[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param rules_source_list: rules_source_list block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source_list NetworkfirewallRuleGroup#rules_source_list}
        :param rules_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_string NetworkfirewallRuleGroup#rules_string}.
        :param stateful_rule: stateful_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule NetworkfirewallRuleGroup#stateful_rule}
        :param stateless_rules_and_custom_actions: stateless_rules_and_custom_actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rules_and_custom_actions NetworkfirewallRuleGroup#stateless_rules_and_custom_actions}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSource(
            rules_source_list=rules_source_list,
            rules_string=rules_string,
            stateful_rule=stateful_rule,
            stateless_rules_and_custom_actions=stateless_rules_and_custom_actions,
        )

        return typing.cast(None, jsii.invoke(self, "putRulesSource", [value]))

    @jsii.member(jsii_name="putRuleVariables")
    def put_rule_variables(
        self,
        *,
        ip_sets: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets", typing.Dict[str, typing.Any]]]]] = None,
        port_sets: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param ip_sets: ip_sets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#ip_sets NetworkfirewallRuleGroup#ip_sets}
        :param port_sets: port_sets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#port_sets NetworkfirewallRuleGroup#port_sets}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRuleVariables(
            ip_sets=ip_sets, port_sets=port_sets
        )

        return typing.cast(None, jsii.invoke(self, "putRuleVariables", [value]))

    @jsii.member(jsii_name="putStatefulRuleOptions")
    def put_stateful_rule_options(self, *, rule_order: builtins.str) -> None:
        '''
        :param rule_order: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_order NetworkfirewallRuleGroup#rule_order}.
        '''
        value = NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions(
            rule_order=rule_order
        )

        return typing.cast(None, jsii.invoke(self, "putStatefulRuleOptions", [value]))

    @jsii.member(jsii_name="resetRuleVariables")
    def reset_rule_variables(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuleVariables", []))

    @jsii.member(jsii_name="resetStatefulRuleOptions")
    def reset_stateful_rule_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatefulRuleOptions", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesSource")
    def rules_source(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference", jsii.get(self, "rulesSource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleVariables")
    def rule_variables(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference", jsii.get(self, "ruleVariables"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleOptions")
    def stateful_rule_options(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference", jsii.get(self, "statefulRuleOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesSourceInput")
    def rules_source_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSource"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSource"], jsii.get(self, "rulesSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleVariablesInput")
    def rule_variables_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariables"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariables"], jsii.get(self, "ruleVariablesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleOptionsInput")
    def stateful_rule_options_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions"], jsii.get(self, "statefulRuleOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NetworkfirewallRuleGroupRuleGroup]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariables",
    jsii_struct_bases=[],
    name_mapping={"ip_sets": "ipSets", "port_sets": "portSets"},
)
class NetworkfirewallRuleGroupRuleGroupRuleVariables:
    def __init__(
        self,
        *,
        ip_sets: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets", typing.Dict[str, typing.Any]]]]] = None,
        port_sets: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param ip_sets: ip_sets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#ip_sets NetworkfirewallRuleGroup#ip_sets}
        :param port_sets: port_sets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#port_sets NetworkfirewallRuleGroup#port_sets}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariables.__init__)
            check_type(argname="argument ip_sets", value=ip_sets, expected_type=type_hints["ip_sets"])
            check_type(argname="argument port_sets", value=port_sets, expected_type=type_hints["port_sets"])
        self._values: typing.Dict[str, typing.Any] = {}
        if ip_sets is not None:
            self._values["ip_sets"] = ip_sets
        if port_sets is not None:
            self._values["port_sets"] = port_sets

    @builtins.property
    def ip_sets(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets"]]]:
        '''ip_sets block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#ip_sets NetworkfirewallRuleGroup#ip_sets}
        '''
        result = self._values.get("ip_sets")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets"]]], result)

    @builtins.property
    def port_sets(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]]]:
        '''port_sets block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#port_sets NetworkfirewallRuleGroup#port_sets}
        '''
        result = self._values.get("port_sets")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRuleVariables(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets",
    jsii_struct_bases=[],
    name_mapping={"ip_set": "ipSet", "key": "key"},
)
class NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets:
    def __init__(
        self,
        *,
        ip_set: typing.Union["NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet", typing.Dict[str, typing.Any]],
        key: builtins.str,
    ) -> None:
        '''
        :param ip_set: ip_set block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#ip_set NetworkfirewallRuleGroup#ip_set}
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#key NetworkfirewallRuleGroup#key}.
        '''
        if isinstance(ip_set, dict):
            ip_set = NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet(**ip_set)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets.__init__)
            check_type(argname="argument ip_set", value=ip_set, expected_type=type_hints["ip_set"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[str, typing.Any] = {
            "ip_set": ip_set,
            "key": key,
        }

    @builtins.property
    def ip_set(self) -> "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet":
        '''ip_set block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#ip_set NetworkfirewallRuleGroup#ip_set}
        '''
        result = self._values.get("ip_set")
        assert result is not None, "Required property 'ip_set' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet", result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#key NetworkfirewallRuleGroup#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet",
    jsii_struct_bases=[],
    name_mapping={"definition": "definition"},
)
class NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet:
    def __init__(self, *, definition: typing.Sequence[builtins.str]) -> None:
        '''
        :param definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#definition NetworkfirewallRuleGroup#definition}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet.__init__)
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
        self._values: typing.Dict[str, typing.Any] = {
            "definition": definition,
        }

    @builtins.property
    def definition(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#definition NetworkfirewallRuleGroup#definition}.'''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definitionInput")
    def definition_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "definitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "definition"))

    @definition.setter
    def definition(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference, "definition").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "definition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putIpSet")
    def put_ip_set(self, *, definition: typing.Sequence[builtins.str]) -> None:
        '''
        :param definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#definition NetworkfirewallRuleGroup#definition}.
        '''
        value = NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet(
            definition=definition
        )

        return typing.cast(None, jsii.invoke(self, "putIpSet", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipSet")
    def ip_set(
        self,
    ) -> NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference:
        return typing.cast(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference, jsii.get(self, "ipSet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipSetInput")
    def ip_set_input(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet], jsii.get(self, "ipSetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsOutputReference, "key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putIpSets")
    def put_ip_sets(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets, typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference.put_ip_sets)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putIpSets", [value]))

    @jsii.member(jsii_name="putPortSets")
    def put_port_sets(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference.put_port_sets)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPortSets", [value]))

    @jsii.member(jsii_name="resetIpSets")
    def reset_ip_sets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpSets", []))

    @jsii.member(jsii_name="resetPortSets")
    def reset_port_sets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortSets", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipSets")
    def ip_sets(self) -> NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList:
        return typing.cast(NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList, jsii.get(self, "ipSets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portSets")
    def port_sets(self) -> "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList", jsii.get(self, "portSets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipSetsInput")
    def ip_sets_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets]]], jsii.get(self, "ipSetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portSetsInput")
    def port_sets_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets"]]], jsii.get(self, "portSetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariables]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariables], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariables],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "port_set": "portSet"},
)
class NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets:
    def __init__(
        self,
        *,
        key: builtins.str,
        port_set: typing.Union["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet", typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#key NetworkfirewallRuleGroup#key}.
        :param port_set: port_set block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#port_set NetworkfirewallRuleGroup#port_set}
        '''
        if isinstance(port_set, dict):
            port_set = NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet(**port_set)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets.__init__)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument port_set", value=port_set, expected_type=type_hints["port_set"])
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "port_set": port_set,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#key NetworkfirewallRuleGroup#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port_set(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet":
        '''port_set block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#port_set NetworkfirewallRuleGroup#port_set}
        '''
        result = self._values.get("port_set")
        assert result is not None, "Required property 'port_set' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putPortSet")
    def put_port_set(self, *, definition: typing.Sequence[builtins.str]) -> None:
        '''
        :param definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#definition NetworkfirewallRuleGroup#definition}.
        '''
        value = NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet(
            definition=definition
        )

        return typing.cast(None, jsii.invoke(self, "putPortSet", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portSet")
    def port_set(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference", jsii.get(self, "portSet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portSetInput")
    def port_set_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet"], jsii.get(self, "portSetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsOutputReference, "key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet",
    jsii_struct_bases=[],
    name_mapping={"definition": "definition"},
)
class NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet:
    def __init__(self, *, definition: typing.Sequence[builtins.str]) -> None:
        '''
        :param definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#definition NetworkfirewallRuleGroup#definition}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet.__init__)
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
        self._values: typing.Dict[str, typing.Any] = {
            "definition": definition,
        }

    @builtins.property
    def definition(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#definition NetworkfirewallRuleGroup#definition}.'''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definitionInput")
    def definition_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "definitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "definition"))

    @definition.setter
    def definition(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference, "definition").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "definition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSource",
    jsii_struct_bases=[],
    name_mapping={
        "rules_source_list": "rulesSourceList",
        "rules_string": "rulesString",
        "stateful_rule": "statefulRule",
        "stateless_rules_and_custom_actions": "statelessRulesAndCustomActions",
    },
)
class NetworkfirewallRuleGroupRuleGroupRulesSource:
    def __init__(
        self,
        *,
        rules_source_list: typing.Optional[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList", typing.Dict[str, typing.Any]]] = None,
        rules_string: typing.Optional[builtins.str] = None,
        stateful_rule: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule", typing.Dict[str, typing.Any]]]]] = None,
        stateless_rules_and_custom_actions: typing.Optional[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param rules_source_list: rules_source_list block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source_list NetworkfirewallRuleGroup#rules_source_list}
        :param rules_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_string NetworkfirewallRuleGroup#rules_string}.
        :param stateful_rule: stateful_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule NetworkfirewallRuleGroup#stateful_rule}
        :param stateless_rules_and_custom_actions: stateless_rules_and_custom_actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rules_and_custom_actions NetworkfirewallRuleGroup#stateless_rules_and_custom_actions}
        '''
        if isinstance(rules_source_list, dict):
            rules_source_list = NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList(**rules_source_list)
        if isinstance(stateless_rules_and_custom_actions, dict):
            stateless_rules_and_custom_actions = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions(**stateless_rules_and_custom_actions)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSource.__init__)
            check_type(argname="argument rules_source_list", value=rules_source_list, expected_type=type_hints["rules_source_list"])
            check_type(argname="argument rules_string", value=rules_string, expected_type=type_hints["rules_string"])
            check_type(argname="argument stateful_rule", value=stateful_rule, expected_type=type_hints["stateful_rule"])
            check_type(argname="argument stateless_rules_and_custom_actions", value=stateless_rules_and_custom_actions, expected_type=type_hints["stateless_rules_and_custom_actions"])
        self._values: typing.Dict[str, typing.Any] = {}
        if rules_source_list is not None:
            self._values["rules_source_list"] = rules_source_list
        if rules_string is not None:
            self._values["rules_string"] = rules_string
        if stateful_rule is not None:
            self._values["stateful_rule"] = stateful_rule
        if stateless_rules_and_custom_actions is not None:
            self._values["stateless_rules_and_custom_actions"] = stateless_rules_and_custom_actions

    @builtins.property
    def rules_source_list(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList"]:
        '''rules_source_list block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_source_list NetworkfirewallRuleGroup#rules_source_list}
        '''
        result = self._values.get("rules_source_list")
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList"], result)

    @builtins.property
    def rules_string(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rules_string NetworkfirewallRuleGroup#rules_string}.'''
        result = self._values.get("rules_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stateful_rule(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]]]:
        '''stateful_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateful_rule NetworkfirewallRuleGroup#stateful_rule}
        '''
        result = self._values.get("stateful_rule")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]]], result)

    @builtins.property
    def stateless_rules_and_custom_actions(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions"]:
        '''stateless_rules_and_custom_actions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rules_and_custom_actions NetworkfirewallRuleGroup#stateless_rules_and_custom_actions}
        '''
        result = self._values.get("stateless_rules_and_custom_actions")
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRulesSourceList")
    def put_rules_source_list(
        self,
        *,
        generated_rules_type: builtins.str,
        targets: typing.Sequence[builtins.str],
        target_types: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param generated_rules_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#generated_rules_type NetworkfirewallRuleGroup#generated_rules_type}.
        :param targets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#targets NetworkfirewallRuleGroup#targets}.
        :param target_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#target_types NetworkfirewallRuleGroup#target_types}.
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList(
            generated_rules_type=generated_rules_type,
            targets=targets,
            target_types=target_types,
        )

        return typing.cast(None, jsii.invoke(self, "putRulesSourceList", [value]))

    @jsii.member(jsii_name="putStatefulRule")
    def put_stateful_rule(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference.put_stateful_rule)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStatefulRule", [value]))

    @jsii.member(jsii_name="putStatelessRulesAndCustomActions")
    def put_stateless_rules_and_custom_actions(
        self,
        *,
        stateless_rule: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule", typing.Dict[str, typing.Any]]]],
        custom_action: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param stateless_rule: stateless_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rule NetworkfirewallRuleGroup#stateless_rule}
        :param custom_action: custom_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#custom_action NetworkfirewallRuleGroup#custom_action}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions(
            stateless_rule=stateless_rule, custom_action=custom_action
        )

        return typing.cast(None, jsii.invoke(self, "putStatelessRulesAndCustomActions", [value]))

    @jsii.member(jsii_name="resetRulesSourceList")
    def reset_rules_source_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRulesSourceList", []))

    @jsii.member(jsii_name="resetRulesString")
    def reset_rules_string(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRulesString", []))

    @jsii.member(jsii_name="resetStatefulRule")
    def reset_stateful_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatefulRule", []))

    @jsii.member(jsii_name="resetStatelessRulesAndCustomActions")
    def reset_stateless_rules_and_custom_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatelessRulesAndCustomActions", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesSourceList")
    def rules_source_list(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference", jsii.get(self, "rulesSourceList"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRule")
    def stateful_rule(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList", jsii.get(self, "statefulRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRulesAndCustomActions")
    def stateless_rules_and_custom_actions(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference", jsii.get(self, "statelessRulesAndCustomActions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesSourceListInput")
    def rules_source_list_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList"], jsii.get(self, "rulesSourceListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesStringInput")
    def rules_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rulesStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statefulRuleInput")
    def stateful_rule_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule"]]], jsii.get(self, "statefulRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRulesAndCustomActionsInput")
    def stateless_rules_and_custom_actions_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions"], jsii.get(self, "statelessRulesAndCustomActionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesString")
    def rules_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rulesString"))

    @rules_string.setter
    def rules_string(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference, "rules_string").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rulesString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSource]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList",
    jsii_struct_bases=[],
    name_mapping={
        "generated_rules_type": "generatedRulesType",
        "targets": "targets",
        "target_types": "targetTypes",
    },
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList:
    def __init__(
        self,
        *,
        generated_rules_type: builtins.str,
        targets: typing.Sequence[builtins.str],
        target_types: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param generated_rules_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#generated_rules_type NetworkfirewallRuleGroup#generated_rules_type}.
        :param targets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#targets NetworkfirewallRuleGroup#targets}.
        :param target_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#target_types NetworkfirewallRuleGroup#target_types}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList.__init__)
            check_type(argname="argument generated_rules_type", value=generated_rules_type, expected_type=type_hints["generated_rules_type"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument target_types", value=target_types, expected_type=type_hints["target_types"])
        self._values: typing.Dict[str, typing.Any] = {
            "generated_rules_type": generated_rules_type,
            "targets": targets,
            "target_types": target_types,
        }

    @builtins.property
    def generated_rules_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#generated_rules_type NetworkfirewallRuleGroup#generated_rules_type}.'''
        result = self._values.get("generated_rules_type")
        assert result is not None, "Required property 'generated_rules_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def targets(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#targets NetworkfirewallRuleGroup#targets}.'''
        result = self._values.get("targets")
        assert result is not None, "Required property 'targets' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def target_types(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#target_types NetworkfirewallRuleGroup#target_types}.'''
        result = self._values.get("target_types")
        assert result is not None, "Required property 'target_types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatedRulesTypeInput")
    def generated_rules_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "generatedRulesTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetsInput")
    def targets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetTypesInput")
    def target_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatedRulesType")
    def generated_rules_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "generatedRulesType"))

    @generated_rules_type.setter
    def generated_rules_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference, "generated_rules_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "generatedRulesType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targets")
    def targets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targets"))

    @targets.setter
    def targets(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference, "targets").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetTypes")
    def target_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetTypes"))

    @target_types.setter
    def target_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference, "target_types").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule",
    jsii_struct_bases=[],
    name_mapping={"action": "action", "header": "header", "rule_option": "ruleOption"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule:
    def __init__(
        self,
        *,
        action: builtins.str,
        header: typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader", typing.Dict[str, typing.Any]],
        rule_option: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action NetworkfirewallRuleGroup#action}.
        :param header: header block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#header NetworkfirewallRuleGroup#header}
        :param rule_option: rule_option block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_option NetworkfirewallRuleGroup#rule_option}
        '''
        if isinstance(header, dict):
            header = NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader(**header)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule.__init__)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument header", value=header, expected_type=type_hints["header"])
            check_type(argname="argument rule_option", value=rule_option, expected_type=type_hints["rule_option"])
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
            "header": header,
            "rule_option": rule_option,
        }

    @builtins.property
    def action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action NetworkfirewallRuleGroup#action}.'''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def header(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader":
        '''header block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#header NetworkfirewallRuleGroup#header}
        '''
        result = self._values.get("header")
        assert result is not None, "Required property 'header' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader", result)

    @builtins.property
    def rule_option(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption"]]:
        '''rule_option block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_option NetworkfirewallRuleGroup#rule_option}
        '''
        result = self._values.get("rule_option")
        assert result is not None, "Required property 'rule_option' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "destination_port": "destinationPort",
        "direction": "direction",
        "protocol": "protocol",
        "source": "source",
        "source_port": "sourcePort",
    },
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader:
    def __init__(
        self,
        *,
        destination: builtins.str,
        destination_port: builtins.str,
        direction: builtins.str,
        protocol: builtins.str,
        source: builtins.str,
        source_port: builtins.str,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}.
        :param destination_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}.
        :param direction: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#direction NetworkfirewallRuleGroup#direction}.
        :param protocol: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocol NetworkfirewallRuleGroup#protocol}.
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}.
        :param source_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader.__init__)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument destination_port", value=destination_port, expected_type=type_hints["destination_port"])
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument source_port", value=source_port, expected_type=type_hints["source_port"])
        self._values: typing.Dict[str, typing.Any] = {
            "destination": destination,
            "destination_port": destination_port,
            "direction": direction,
            "protocol": protocol,
            "source": source,
            "source_port": source_port,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_port(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}.'''
        result = self._values.get("destination_port")
        assert result is not None, "Required property 'destination_port' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def direction(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#direction NetworkfirewallRuleGroup#direction}.'''
        result = self._values.get("direction")
        assert result is not None, "Required property 'direction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def protocol(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocol NetworkfirewallRuleGroup#protocol}.'''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}.'''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_port(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}.'''
        result = self._values.get("source_port")
        assert result is not None, "Required property 'source_port' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationPortInput")
    def destination_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directionInput")
    def direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourcePortInput")
    def source_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourcePortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference, "destination").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationPort")
    def destination_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationPort"))

    @destination_port.setter
    def destination_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference, "destination_port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference, "direction").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference, "protocol").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference, "source").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourcePort")
    def source_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourcePort"))

    @source_port.setter
    def source_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference, "source_port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourcePort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putHeader")
    def put_header(
        self,
        *,
        destination: builtins.str,
        destination_port: builtins.str,
        direction: builtins.str,
        protocol: builtins.str,
        source: builtins.str,
        source_port: builtins.str,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}.
        :param destination_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}.
        :param direction: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#direction NetworkfirewallRuleGroup#direction}.
        :param protocol: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocol NetworkfirewallRuleGroup#protocol}.
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}.
        :param source_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}.
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader(
            destination=destination,
            destination_port=destination_port,
            direction=direction,
            protocol=protocol,
            source=source,
            source_port=source_port,
        )

        return typing.cast(None, jsii.invoke(self, "putHeader", [value]))

    @jsii.member(jsii_name="putRuleOption")
    def put_rule_option(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleOutputReference.put_rule_option)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRuleOption", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="header")
    def header(
        self,
    ) -> NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference:
        return typing.cast(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference, jsii.get(self, "header"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleOption")
    def rule_option(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList", jsii.get(self, "ruleOption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headerInput")
    def header_input(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader], jsii.get(self, "headerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleOptionInput")
    def rule_option_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption"]]], jsii.get(self, "ruleOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleOutputReference, "action").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption",
    jsii_struct_bases=[],
    name_mapping={"keyword": "keyword", "settings": "settings"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption:
    def __init__(
        self,
        *,
        keyword: builtins.str,
        settings: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param keyword: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#keyword NetworkfirewallRuleGroup#keyword}.
        :param settings: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#settings NetworkfirewallRuleGroup#settings}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption.__init__)
            check_type(argname="argument keyword", value=keyword, expected_type=type_hints["keyword"])
            check_type(argname="argument settings", value=settings, expected_type=type_hints["settings"])
        self._values: typing.Dict[str, typing.Any] = {
            "keyword": keyword,
        }
        if settings is not None:
            self._values["settings"] = settings

    @builtins.property
    def keyword(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#keyword NetworkfirewallRuleGroup#keyword}.'''
        result = self._values.get("keyword")
        assert result is not None, "Required property 'keyword' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def settings(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#settings NetworkfirewallRuleGroup#settings}.'''
        result = self._values.get("settings")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetSettings")
    def reset_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSettings", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keywordInput")
    def keyword_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keywordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="settingsInput")
    def settings_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "settingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyword")
    def keyword(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyword"))

    @keyword.setter
    def keyword(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionOutputReference, "keyword").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="settings")
    def settings(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "settings"))

    @settings.setter
    def settings(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionOutputReference, "settings").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "settings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions",
    jsii_struct_bases=[],
    name_mapping={"stateless_rule": "statelessRule", "custom_action": "customAction"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions:
    def __init__(
        self,
        *,
        stateless_rule: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule", typing.Dict[str, typing.Any]]]],
        custom_action: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param stateless_rule: stateless_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rule NetworkfirewallRuleGroup#stateless_rule}
        :param custom_action: custom_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#custom_action NetworkfirewallRuleGroup#custom_action}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions.__init__)
            check_type(argname="argument stateless_rule", value=stateless_rule, expected_type=type_hints["stateless_rule"])
            check_type(argname="argument custom_action", value=custom_action, expected_type=type_hints["custom_action"])
        self._values: typing.Dict[str, typing.Any] = {
            "stateless_rule": stateless_rule,
        }
        if custom_action is not None:
            self._values["custom_action"] = custom_action

    @builtins.property
    def stateless_rule(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"]]:
        '''stateless_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#stateless_rule NetworkfirewallRuleGroup#stateless_rule}
        '''
        result = self._values.get("stateless_rule")
        assert result is not None, "Required property 'stateless_rule' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"]], result)

    @builtins.property
    def custom_action(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction"]]]:
        '''custom_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#custom_action NetworkfirewallRuleGroup#custom_action}
        '''
        result = self._values.get("custom_action")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction",
    jsii_struct_bases=[],
    name_mapping={
        "action_definition": "actionDefinition",
        "action_name": "actionName",
    },
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction:
    def __init__(
        self,
        *,
        action_definition: typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition", typing.Dict[str, typing.Any]],
        action_name: builtins.str,
    ) -> None:
        '''
        :param action_definition: action_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action_definition NetworkfirewallRuleGroup#action_definition}
        :param action_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action_name NetworkfirewallRuleGroup#action_name}.
        '''
        if isinstance(action_definition, dict):
            action_definition = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition(**action_definition)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction.__init__)
            check_type(argname="argument action_definition", value=action_definition, expected_type=type_hints["action_definition"])
            check_type(argname="argument action_name", value=action_name, expected_type=type_hints["action_name"])
        self._values: typing.Dict[str, typing.Any] = {
            "action_definition": action_definition,
            "action_name": action_name,
        }

    @builtins.property
    def action_definition(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition":
        '''action_definition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action_definition NetworkfirewallRuleGroup#action_definition}
        '''
        result = self._values.get("action_definition")
        assert result is not None, "Required property 'action_definition' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition", result)

    @builtins.property
    def action_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#action_name NetworkfirewallRuleGroup#action_name}.'''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition",
    jsii_struct_bases=[],
    name_mapping={"publish_metric_action": "publishMetricAction"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition:
    def __init__(
        self,
        *,
        publish_metric_action: typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction", typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param publish_metric_action: publish_metric_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#publish_metric_action NetworkfirewallRuleGroup#publish_metric_action}
        '''
        if isinstance(publish_metric_action, dict):
            publish_metric_action = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction(**publish_metric_action)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition.__init__)
            check_type(argname="argument publish_metric_action", value=publish_metric_action, expected_type=type_hints["publish_metric_action"])
        self._values: typing.Dict[str, typing.Any] = {
            "publish_metric_action": publish_metric_action,
        }

    @builtins.property
    def publish_metric_action(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction":
        '''publish_metric_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#publish_metric_action NetworkfirewallRuleGroup#publish_metric_action}
        '''
        result = self._values.get("publish_metric_action")
        assert result is not None, "Required property 'publish_metric_action' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPublishMetricAction")
    def put_publish_metric_action(
        self,
        *,
        dimension: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#dimension NetworkfirewallRuleGroup#dimension}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction(
            dimension=dimension
        )

        return typing.cast(None, jsii.invoke(self, "putPublishMetricAction", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishMetricAction")
    def publish_metric_action(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference", jsii.get(self, "publishMetricAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishMetricActionInput")
    def publish_metric_action_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction"], jsii.get(self, "publishMetricActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction",
    jsii_struct_bases=[],
    name_mapping={"dimension": "dimension"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction:
    def __init__(
        self,
        *,
        dimension: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#dimension NetworkfirewallRuleGroup#dimension}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction.__init__)
            check_type(argname="argument dimension", value=dimension, expected_type=type_hints["dimension"])
        self._values: typing.Dict[str, typing.Any] = {
            "dimension": dimension,
        }

    @builtins.property
    def dimension(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension"]]:
        '''dimension block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#dimension NetworkfirewallRuleGroup#dimension}
        '''
        result = self._values.get("dimension")
        assert result is not None, "Required property 'dimension' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#value NetworkfirewallRuleGroup#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension.__init__)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#value NetworkfirewallRuleGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionOutputReference, "value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDimension")
    def put_dimension(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension, typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference.put_dimension)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDimension", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimension")
    def dimension(
        self,
    ) -> NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList:
        return typing.cast(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList, jsii.get(self, "dimension"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimensionInput")
    def dimension_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension]]], jsii.get(self, "dimensionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putActionDefinition")
    def put_action_definition(
        self,
        *,
        publish_metric_action: typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction, typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param publish_metric_action: publish_metric_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#publish_metric_action NetworkfirewallRuleGroup#publish_metric_action}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition(
            publish_metric_action=publish_metric_action
        )

        return typing.cast(None, jsii.invoke(self, "putActionDefinition", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionDefinition")
    def action_definition(
        self,
    ) -> NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionOutputReference:
        return typing.cast(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionOutputReference, jsii.get(self, "actionDefinition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionDefinitionInput")
    def action_definition_input(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition], jsii.get(self, "actionDefinitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionNameInput")
    def action_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionName")
    def action_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionName"))

    @action_name.setter
    def action_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionOutputReference, "action_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCustomAction")
    def put_custom_action(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction, typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference.put_custom_action)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCustomAction", [value]))

    @jsii.member(jsii_name="putStatelessRule")
    def put_stateless_rule(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference.put_stateless_rule)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStatelessRule", [value]))

    @jsii.member(jsii_name="resetCustomAction")
    def reset_custom_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAction", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customAction")
    def custom_action(
        self,
    ) -> NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList:
        return typing.cast(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList, jsii.get(self, "customAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRule")
    def stateless_rule(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList", jsii.get(self, "statelessRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customActionInput")
    def custom_action_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction]]], jsii.get(self, "customActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statelessRuleInput")
    def stateless_rule_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule"]]], jsii.get(self, "statelessRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule",
    jsii_struct_bases=[],
    name_mapping={"priority": "priority", "rule_definition": "ruleDefinition"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule:
    def __init__(
        self,
        *,
        priority: jsii.Number,
        rule_definition: typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition", typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#priority NetworkfirewallRuleGroup#priority}.
        :param rule_definition: rule_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_definition NetworkfirewallRuleGroup#rule_definition}
        '''
        if isinstance(rule_definition, dict):
            rule_definition = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition(**rule_definition)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule.__init__)
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument rule_definition", value=rule_definition, expected_type=type_hints["rule_definition"])
        self._values: typing.Dict[str, typing.Any] = {
            "priority": priority,
            "rule_definition": rule_definition,
        }

    @builtins.property
    def priority(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#priority NetworkfirewallRuleGroup#priority}.'''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def rule_definition(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition":
        '''rule_definition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_definition NetworkfirewallRuleGroup#rule_definition}
        '''
        result = self._values.get("rule_definition")
        assert result is not None, "Required property 'rule_definition' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putRuleDefinition")
    def put_rule_definition(
        self,
        *,
        actions: typing.Sequence[builtins.str],
        match_attributes: typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes", typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#actions NetworkfirewallRuleGroup#actions}.
        :param match_attributes: match_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#match_attributes NetworkfirewallRuleGroup#match_attributes}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition(
            actions=actions, match_attributes=match_attributes
        )

        return typing.cast(None, jsii.invoke(self, "putRuleDefinition", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleDefinition")
    def rule_definition(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference", jsii.get(self, "ruleDefinition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleDefinitionInput")
    def rule_definition_input(
        self,
    ) -> typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition"]:
        return typing.cast(typing.Optional["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition"], jsii.get(self, "ruleDefinitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleOutputReference, "priority").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition",
    jsii_struct_bases=[],
    name_mapping={"actions": "actions", "match_attributes": "matchAttributes"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition:
    def __init__(
        self,
        *,
        actions: typing.Sequence[builtins.str],
        match_attributes: typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes", typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#actions NetworkfirewallRuleGroup#actions}.
        :param match_attributes: match_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#match_attributes NetworkfirewallRuleGroup#match_attributes}
        '''
        if isinstance(match_attributes, dict):
            match_attributes = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes(**match_attributes)
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition.__init__)
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument match_attributes", value=match_attributes, expected_type=type_hints["match_attributes"])
        self._values: typing.Dict[str, typing.Any] = {
            "actions": actions,
            "match_attributes": match_attributes,
        }

    @builtins.property
    def actions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#actions NetworkfirewallRuleGroup#actions}.'''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def match_attributes(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes":
        '''match_attributes block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#match_attributes NetworkfirewallRuleGroup#match_attributes}
        '''
        result = self._values.get("match_attributes")
        assert result is not None, "Required property 'match_attributes' is missing"
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "destination_port": "destinationPort",
        "protocols": "protocols",
        "source": "source",
        "source_port": "sourcePort",
        "tcp_flag": "tcpFlag",
    },
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes:
    def __init__(
        self,
        *,
        destination: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination", typing.Dict[str, typing.Any]]]]] = None,
        destination_port: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort", typing.Dict[str, typing.Any]]]]] = None,
        protocols: typing.Optional[typing.Sequence[jsii.Number]] = None,
        source: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource", typing.Dict[str, typing.Any]]]]] = None,
        source_port: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort", typing.Dict[str, typing.Any]]]]] = None,
        tcp_flag: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}
        :param destination_port: destination_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}
        :param protocols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocols NetworkfirewallRuleGroup#protocols}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}
        :param source_port: source_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}
        :param tcp_flag: tcp_flag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tcp_flag NetworkfirewallRuleGroup#tcp_flag}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes.__init__)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument destination_port", value=destination_port, expected_type=type_hints["destination_port"])
            check_type(argname="argument protocols", value=protocols, expected_type=type_hints["protocols"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument source_port", value=source_port, expected_type=type_hints["source_port"])
            check_type(argname="argument tcp_flag", value=tcp_flag, expected_type=type_hints["tcp_flag"])
        self._values: typing.Dict[str, typing.Any] = {}
        if destination is not None:
            self._values["destination"] = destination
        if destination_port is not None:
            self._values["destination_port"] = destination_port
        if protocols is not None:
            self._values["protocols"] = protocols
        if source is not None:
            self._values["source"] = source
        if source_port is not None:
            self._values["source_port"] = source_port
        if tcp_flag is not None:
            self._values["tcp_flag"] = tcp_flag

    @builtins.property
    def destination(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination"]]]:
        '''destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}
        '''
        result = self._values.get("destination")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination"]]], result)

    @builtins.property
    def destination_port(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort"]]]:
        '''destination_port block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}
        '''
        result = self._values.get("destination_port")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort"]]], result)

    @builtins.property
    def protocols(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocols NetworkfirewallRuleGroup#protocols}.'''
        result = self._values.get("protocols")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def source(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"]]]:
        '''source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"]]], result)

    @builtins.property
    def source_port(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"]]]:
        '''source_port block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}
        '''
        result = self._values.get("source_port")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"]]], result)

    @builtins.property
    def tcp_flag(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"]]]:
        '''tcp_flag block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tcp_flag NetworkfirewallRuleGroup#tcp_flag}
        '''
        result = self._values.get("tcp_flag")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination",
    jsii_struct_bases=[],
    name_mapping={"address_definition": "addressDefinition"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination:
    def __init__(self, *, address_definition: builtins.str) -> None:
        '''
        :param address_definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#address_definition NetworkfirewallRuleGroup#address_definition}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination.__init__)
            check_type(argname="argument address_definition", value=address_definition, expected_type=type_hints["address_definition"])
        self._values: typing.Dict[str, typing.Any] = {
            "address_definition": address_definition,
        }

    @builtins.property
    def address_definition(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#address_definition NetworkfirewallRuleGroup#address_definition}.'''
        result = self._values.get("address_definition")
        assert result is not None, "Required property 'address_definition' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressDefinitionInput")
    def address_definition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressDefinitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressDefinition")
    def address_definition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "addressDefinition"))

    @address_definition.setter
    def address_definition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationOutputReference, "address_definition").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addressDefinition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort",
    jsii_struct_bases=[],
    name_mapping={"from_port": "fromPort", "to_port": "toPort"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort:
    def __init__(
        self,
        *,
        from_port: jsii.Number,
        to_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param from_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#from_port NetworkfirewallRuleGroup#from_port}.
        :param to_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#to_port NetworkfirewallRuleGroup#to_port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort.__init__)
            check_type(argname="argument from_port", value=from_port, expected_type=type_hints["from_port"])
            check_type(argname="argument to_port", value=to_port, expected_type=type_hints["to_port"])
        self._values: typing.Dict[str, typing.Any] = {
            "from_port": from_port,
        }
        if to_port is not None:
            self._values["to_port"] = to_port

    @builtins.property
    def from_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#from_port NetworkfirewallRuleGroup#from_port}.'''
        result = self._values.get("from_port")
        assert result is not None, "Required property 'from_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def to_port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#to_port NetworkfirewallRuleGroup#to_port}.'''
        result = self._values.get("to_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetToPort")
    def reset_to_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToPort", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromPortInput")
    def from_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "fromPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="toPortInput")
    def to_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "toPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromPort")
    def from_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "fromPort"))

    @from_port.setter
    def from_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortOutputReference, "from_port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fromPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="toPort")
    def to_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "toPort"))

    @to_port.setter
    def to_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortOutputReference, "to_port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDestination")
    def put_destination(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination, typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference.put_destination)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDestination", [value]))

    @jsii.member(jsii_name="putDestinationPort")
    def put_destination_port(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort, typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference.put_destination_port)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDestinationPort", [value]))

    @jsii.member(jsii_name="putSource")
    def put_source(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference.put_source)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="putSourcePort")
    def put_source_port(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference.put_source_port)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSourcePort", [value]))

    @jsii.member(jsii_name="putTcpFlag")
    def put_tcp_flag(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference.put_tcp_flag)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTcpFlag", [value]))

    @jsii.member(jsii_name="resetDestination")
    def reset_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestination", []))

    @jsii.member(jsii_name="resetDestinationPort")
    def reset_destination_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationPort", []))

    @jsii.member(jsii_name="resetProtocols")
    def reset_protocols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocols", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetSourcePort")
    def reset_source_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourcePort", []))

    @jsii.member(jsii_name="resetTcpFlag")
    def reset_tcp_flag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTcpFlag", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destination")
    def destination(
        self,
    ) -> NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList:
        return typing.cast(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList, jsii.get(self, "destination"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationPort")
    def destination_port(
        self,
    ) -> NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList:
        return typing.cast(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList, jsii.get(self, "destinationPort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList", jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourcePort")
    def source_port(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList", jsii.get(self, "sourcePort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tcpFlag")
    def tcp_flag(
        self,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList":
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList", jsii.get(self, "tcpFlag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationInput")
    def destination_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination]]], jsii.get(self, "destinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationPortInput")
    def destination_port_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort]]], jsii.get(self, "destinationPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocolsInput")
    def protocols_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "protocolsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource"]]], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourcePortInput")
    def source_port_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort"]]], jsii.get(self, "sourcePortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tcpFlagInput")
    def tcp_flag_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag"]]], jsii.get(self, "tcpFlagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocols")
    def protocols(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "protocols"))

    @protocols.setter
    def protocols(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference, "protocols").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocols", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource",
    jsii_struct_bases=[],
    name_mapping={"address_definition": "addressDefinition"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource:
    def __init__(self, *, address_definition: builtins.str) -> None:
        '''
        :param address_definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#address_definition NetworkfirewallRuleGroup#address_definition}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource.__init__)
            check_type(argname="argument address_definition", value=address_definition, expected_type=type_hints["address_definition"])
        self._values: typing.Dict[str, typing.Any] = {
            "address_definition": address_definition,
        }

    @builtins.property
    def address_definition(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#address_definition NetworkfirewallRuleGroup#address_definition}.'''
        result = self._values.get("address_definition")
        assert result is not None, "Required property 'address_definition' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressDefinitionInput")
    def address_definition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressDefinitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressDefinition")
    def address_definition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "addressDefinition"))

    @address_definition.setter
    def address_definition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceOutputReference, "address_definition").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addressDefinition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort",
    jsii_struct_bases=[],
    name_mapping={"from_port": "fromPort", "to_port": "toPort"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort:
    def __init__(
        self,
        *,
        from_port: jsii.Number,
        to_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param from_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#from_port NetworkfirewallRuleGroup#from_port}.
        :param to_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#to_port NetworkfirewallRuleGroup#to_port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort.__init__)
            check_type(argname="argument from_port", value=from_port, expected_type=type_hints["from_port"])
            check_type(argname="argument to_port", value=to_port, expected_type=type_hints["to_port"])
        self._values: typing.Dict[str, typing.Any] = {
            "from_port": from_port,
        }
        if to_port is not None:
            self._values["to_port"] = to_port

    @builtins.property
    def from_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#from_port NetworkfirewallRuleGroup#from_port}.'''
        result = self._values.get("from_port")
        assert result is not None, "Required property 'from_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def to_port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#to_port NetworkfirewallRuleGroup#to_port}.'''
        result = self._values.get("to_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetToPort")
    def reset_to_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToPort", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromPortInput")
    def from_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "fromPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="toPortInput")
    def to_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "toPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromPort")
    def from_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "fromPort"))

    @from_port.setter
    def from_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortOutputReference, "from_port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fromPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="toPort")
    def to_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "toPort"))

    @to_port.setter
    def to_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortOutputReference, "to_port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag",
    jsii_struct_bases=[],
    name_mapping={"flags": "flags", "masks": "masks"},
)
class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag:
    def __init__(
        self,
        *,
        flags: typing.Sequence[builtins.str],
        masks: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param flags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#flags NetworkfirewallRuleGroup#flags}.
        :param masks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#masks NetworkfirewallRuleGroup#masks}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag.__init__)
            check_type(argname="argument flags", value=flags, expected_type=type_hints["flags"])
            check_type(argname="argument masks", value=masks, expected_type=type_hints["masks"])
        self._values: typing.Dict[str, typing.Any] = {
            "flags": flags,
        }
        if masks is not None:
            self._values["masks"] = masks

    @builtins.property
    def flags(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#flags NetworkfirewallRuleGroup#flags}.'''
        result = self._values.get("flags")
        assert result is not None, "Required property 'flags' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def masks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#masks NetworkfirewallRuleGroup#masks}.'''
        result = self._values.get("masks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetMasks")
    def reset_masks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasks", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="flagsInput")
    def flags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "flagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masksInput")
    def masks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "masksInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="flags")
    def flags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "flags"))

    @flags.setter
    def flags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagOutputReference, "flags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "flags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masks")
    def masks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "masks"))

    @masks.setter
    def masks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagOutputReference, "masks").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "masks", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMatchAttributes")
    def put_match_attributes(
        self,
        *,
        destination: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination, typing.Dict[str, typing.Any]]]]] = None,
        destination_port: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort, typing.Dict[str, typing.Any]]]]] = None,
        protocols: typing.Optional[typing.Sequence[jsii.Number]] = None,
        source: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource, typing.Dict[str, typing.Any]]]]] = None,
        source_port: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort, typing.Dict[str, typing.Any]]]]] = None,
        tcp_flag: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag, typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination NetworkfirewallRuleGroup#destination}
        :param destination_port: destination_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#destination_port NetworkfirewallRuleGroup#destination_port}
        :param protocols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#protocols NetworkfirewallRuleGroup#protocols}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source NetworkfirewallRuleGroup#source}
        :param source_port: source_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#source_port NetworkfirewallRuleGroup#source_port}
        :param tcp_flag: tcp_flag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#tcp_flag NetworkfirewallRuleGroup#tcp_flag}
        '''
        value = NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes(
            destination=destination,
            destination_port=destination_port,
            protocols=protocols,
            source=source,
            source_port=source_port,
            tcp_flag=tcp_flag,
        )

        return typing.cast(None, jsii.invoke(self, "putMatchAttributes", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="matchAttributes")
    def match_attributes(
        self,
    ) -> NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference:
        return typing.cast(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference, jsii.get(self, "matchAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionsInput")
    def actions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "actionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="matchAttributesInput")
    def match_attributes_input(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes], jsii.get(self, "matchAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "actions"))

    @actions.setter
    def actions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference, "actions").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions",
    jsii_struct_bases=[],
    name_mapping={"rule_order": "ruleOrder"},
)
class NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions:
    def __init__(self, *, rule_order: builtins.str) -> None:
        '''
        :param rule_order: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_order NetworkfirewallRuleGroup#rule_order}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions.__init__)
            check_type(argname="argument rule_order", value=rule_order, expected_type=type_hints["rule_order"])
        self._values: typing.Dict[str, typing.Any] = {
            "rule_order": rule_order,
        }

    @builtins.property
    def rule_order(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/networkfirewall_rule_group#rule_order NetworkfirewallRuleGroup#rule_order}.'''
        result = self._values.get("rule_order")
        assert result is not None, "Required property 'rule_order' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.networkfirewall.NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference",
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
            type_hints = typing.get_type_hints(NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleOrderInput")
    def rule_order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleOrderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleOrder")
    def rule_order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleOrder"))

    @rule_order.setter
    def rule_order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference, "rule_order").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleOrder", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions]:
        return typing.cast(typing.Optional[NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsNetworkfirewallFirewallPolicy",
    "DataAwsNetworkfirewallFirewallPolicyConfig",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicy",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyList",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyOutputReference",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsList",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionList",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionList",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList",
    "DataAwsNetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference",
    "NetworkfirewallFirewall",
    "NetworkfirewallFirewallConfig",
    "NetworkfirewallFirewallFirewallStatus",
    "NetworkfirewallFirewallFirewallStatusList",
    "NetworkfirewallFirewallFirewallStatusOutputReference",
    "NetworkfirewallFirewallFirewallStatusSyncStates",
    "NetworkfirewallFirewallFirewallStatusSyncStatesAttachment",
    "NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentList",
    "NetworkfirewallFirewallFirewallStatusSyncStatesAttachmentOutputReference",
    "NetworkfirewallFirewallFirewallStatusSyncStatesList",
    "NetworkfirewallFirewallFirewallStatusSyncStatesOutputReference",
    "NetworkfirewallFirewallPolicy",
    "NetworkfirewallFirewallPolicyConfig",
    "NetworkfirewallFirewallPolicyFirewallPolicy",
    "NetworkfirewallFirewallPolicyFirewallPolicyOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptions",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatefulEngineOptionsOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceList",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatefulRuleGroupReferenceOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomAction",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinition",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricAction",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimension",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionList",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionDimensionOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionActionDefinitionPublishMetricActionOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionList",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessCustomActionOutputReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReference",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceList",
    "NetworkfirewallFirewallPolicyFirewallPolicyStatelessRuleGroupReferenceOutputReference",
    "NetworkfirewallFirewallSubnetMapping",
    "NetworkfirewallFirewallSubnetMappingList",
    "NetworkfirewallFirewallSubnetMappingOutputReference",
    "NetworkfirewallLoggingConfiguration",
    "NetworkfirewallLoggingConfigurationConfig",
    "NetworkfirewallLoggingConfigurationLoggingConfiguration",
    "NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfig",
    "NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigList",
    "NetworkfirewallLoggingConfigurationLoggingConfigurationLogDestinationConfigOutputReference",
    "NetworkfirewallLoggingConfigurationLoggingConfigurationOutputReference",
    "NetworkfirewallResourcePolicy",
    "NetworkfirewallResourcePolicyConfig",
    "NetworkfirewallRuleGroup",
    "NetworkfirewallRuleGroupConfig",
    "NetworkfirewallRuleGroupRuleGroup",
    "NetworkfirewallRuleGroupRuleGroupOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRuleVariables",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSets",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSet",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsIpSetOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsList",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesIpSetsOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSets",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsList",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSet",
    "NetworkfirewallRuleGroupRuleGroupRuleVariablesPortSetsPortSetOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSource",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceRulesSourceListOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRule",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeader",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleHeaderOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOption",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatefulRuleRuleOptionOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActions",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomAction",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinition",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricAction",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimension",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionDimensionOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionActionDefinitionPublishMetricActionOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsCustomActionOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRule",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinition",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributes",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestination",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPort",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesDestinationPortOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSource",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourceOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePort",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesSourcePortOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlag",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagList",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionMatchAttributesTcpFlagOutputReference",
    "NetworkfirewallRuleGroupRuleGroupRulesSourceStatelessRulesAndCustomActionsStatelessRuleRuleDefinitionOutputReference",
    "NetworkfirewallRuleGroupRuleGroupStatefulRuleOptions",
    "NetworkfirewallRuleGroupRuleGroupStatefulRuleOptionsOutputReference",
]

publication.publish()
