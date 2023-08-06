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


class WorklinkFleet(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.worklink.WorklinkFleet",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet aws_worklink_fleet}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        audit_stream_arn: typing.Optional[builtins.str] = None,
        device_ca_certificate: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        identity_provider: typing.Optional[typing.Union["WorklinkFleetIdentityProvider", typing.Dict[str, typing.Any]]] = None,
        network: typing.Optional[typing.Union["WorklinkFleetNetwork", typing.Dict[str, typing.Any]]] = None,
        optimize_for_end_user_location: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet aws_worklink_fleet} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#name WorklinkFleet#name}.
        :param audit_stream_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#audit_stream_arn WorklinkFleet#audit_stream_arn}.
        :param device_ca_certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#device_ca_certificate WorklinkFleet#device_ca_certificate}.
        :param display_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#display_name WorklinkFleet#display_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#id WorklinkFleet#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider: identity_provider block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#identity_provider WorklinkFleet#identity_provider}
        :param network: network block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#network WorklinkFleet#network}
        :param optimize_for_end_user_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#optimize_for_end_user_location WorklinkFleet#optimize_for_end_user_location}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WorklinkFleet.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = WorklinkFleetConfig(
            name=name,
            audit_stream_arn=audit_stream_arn,
            device_ca_certificate=device_ca_certificate,
            display_name=display_name,
            id=id,
            identity_provider=identity_provider,
            network=network,
            optimize_for_end_user_location=optimize_for_end_user_location,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putIdentityProvider")
    def put_identity_provider(
        self,
        *,
        saml_metadata: builtins.str,
        type: builtins.str,
    ) -> None:
        '''
        :param saml_metadata: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#saml_metadata WorklinkFleet#saml_metadata}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#type WorklinkFleet#type}.
        '''
        value = WorklinkFleetIdentityProvider(saml_metadata=saml_metadata, type=type)

        return typing.cast(None, jsii.invoke(self, "putIdentityProvider", [value]))

    @jsii.member(jsii_name="putNetwork")
    def put_network(
        self,
        *,
        security_group_ids: typing.Sequence[builtins.str],
        subnet_ids: typing.Sequence[builtins.str],
        vpc_id: builtins.str,
    ) -> None:
        '''
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#security_group_ids WorklinkFleet#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#subnet_ids WorklinkFleet#subnet_ids}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#vpc_id WorklinkFleet#vpc_id}.
        '''
        value = WorklinkFleetNetwork(
            security_group_ids=security_group_ids, subnet_ids=subnet_ids, vpc_id=vpc_id
        )

        return typing.cast(None, jsii.invoke(self, "putNetwork", [value]))

    @jsii.member(jsii_name="resetAuditStreamArn")
    def reset_audit_stream_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditStreamArn", []))

    @jsii.member(jsii_name="resetDeviceCaCertificate")
    def reset_device_ca_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceCaCertificate", []))

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdentityProvider")
    def reset_identity_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityProvider", []))

    @jsii.member(jsii_name="resetNetwork")
    def reset_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetwork", []))

    @jsii.member(jsii_name="resetOptimizeForEndUserLocation")
    def reset_optimize_for_end_user_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptimizeForEndUserLocation", []))

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
    @jsii.member(jsii_name="companyCode")
    def company_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "companyCode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdTime")
    def created_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProvider")
    def identity_provider(self) -> "WorklinkFleetIdentityProviderOutputReference":
        return typing.cast("WorklinkFleetIdentityProviderOutputReference", jsii.get(self, "identityProvider"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastUpdatedTime")
    def last_updated_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdatedTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="network")
    def network(self) -> "WorklinkFleetNetworkOutputReference":
        return typing.cast("WorklinkFleetNetworkOutputReference", jsii.get(self, "network"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditStreamArnInput")
    def audit_stream_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "auditStreamArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceCaCertificateInput")
    def device_ca_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceCaCertificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderInput")
    def identity_provider_input(
        self,
    ) -> typing.Optional["WorklinkFleetIdentityProvider"]:
        return typing.cast(typing.Optional["WorklinkFleetIdentityProvider"], jsii.get(self, "identityProviderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional["WorklinkFleetNetwork"]:
        return typing.cast(typing.Optional["WorklinkFleetNetwork"], jsii.get(self, "networkInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optimizeForEndUserLocationInput")
    def optimize_for_end_user_location_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "optimizeForEndUserLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditStreamArn")
    def audit_stream_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "auditStreamArn"))

    @audit_stream_arn.setter
    def audit_stream_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleet, "audit_stream_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditStreamArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceCaCertificate")
    def device_ca_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceCaCertificate"))

    @device_ca_certificate.setter
    def device_ca_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleet, "device_ca_certificate").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deviceCaCertificate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleet, "display_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleet, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleet, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optimizeForEndUserLocation")
    def optimize_for_end_user_location(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "optimizeForEndUserLocation"))

    @optimize_for_end_user_location.setter
    def optimize_for_end_user_location(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleet, "optimize_for_end_user_location").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "optimizeForEndUserLocation", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.worklink.WorklinkFleetConfig",
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
        "audit_stream_arn": "auditStreamArn",
        "device_ca_certificate": "deviceCaCertificate",
        "display_name": "displayName",
        "id": "id",
        "identity_provider": "identityProvider",
        "network": "network",
        "optimize_for_end_user_location": "optimizeForEndUserLocation",
    },
)
class WorklinkFleetConfig(cdktf.TerraformMetaArguments):
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
        audit_stream_arn: typing.Optional[builtins.str] = None,
        device_ca_certificate: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        identity_provider: typing.Optional[typing.Union["WorklinkFleetIdentityProvider", typing.Dict[str, typing.Any]]] = None,
        network: typing.Optional[typing.Union["WorklinkFleetNetwork", typing.Dict[str, typing.Any]]] = None,
        optimize_for_end_user_location: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS WorkLink.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#name WorklinkFleet#name}.
        :param audit_stream_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#audit_stream_arn WorklinkFleet#audit_stream_arn}.
        :param device_ca_certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#device_ca_certificate WorklinkFleet#device_ca_certificate}.
        :param display_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#display_name WorklinkFleet#display_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#id WorklinkFleet#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider: identity_provider block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#identity_provider WorklinkFleet#identity_provider}
        :param network: network block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#network WorklinkFleet#network}
        :param optimize_for_end_user_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#optimize_for_end_user_location WorklinkFleet#optimize_for_end_user_location}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(identity_provider, dict):
            identity_provider = WorklinkFleetIdentityProvider(**identity_provider)
        if isinstance(network, dict):
            network = WorklinkFleetNetwork(**network)
        if __debug__:
            type_hints = typing.get_type_hints(WorklinkFleetConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument audit_stream_arn", value=audit_stream_arn, expected_type=type_hints["audit_stream_arn"])
            check_type(argname="argument device_ca_certificate", value=device_ca_certificate, expected_type=type_hints["device_ca_certificate"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider", value=identity_provider, expected_type=type_hints["identity_provider"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument optimize_for_end_user_location", value=optimize_for_end_user_location, expected_type=type_hints["optimize_for_end_user_location"])
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
        if audit_stream_arn is not None:
            self._values["audit_stream_arn"] = audit_stream_arn
        if device_ca_certificate is not None:
            self._values["device_ca_certificate"] = device_ca_certificate
        if display_name is not None:
            self._values["display_name"] = display_name
        if id is not None:
            self._values["id"] = id
        if identity_provider is not None:
            self._values["identity_provider"] = identity_provider
        if network is not None:
            self._values["network"] = network
        if optimize_for_end_user_location is not None:
            self._values["optimize_for_end_user_location"] = optimize_for_end_user_location

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#name WorklinkFleet#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audit_stream_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#audit_stream_arn WorklinkFleet#audit_stream_arn}.'''
        result = self._values.get("audit_stream_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def device_ca_certificate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#device_ca_certificate WorklinkFleet#device_ca_certificate}.'''
        result = self._values.get("device_ca_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#display_name WorklinkFleet#display_name}.'''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#id WorklinkFleet#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_provider(self) -> typing.Optional["WorklinkFleetIdentityProvider"]:
        '''identity_provider block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#identity_provider WorklinkFleet#identity_provider}
        '''
        result = self._values.get("identity_provider")
        return typing.cast(typing.Optional["WorklinkFleetIdentityProvider"], result)

    @builtins.property
    def network(self) -> typing.Optional["WorklinkFleetNetwork"]:
        '''network block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#network WorklinkFleet#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional["WorklinkFleetNetwork"], result)

    @builtins.property
    def optimize_for_end_user_location(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#optimize_for_end_user_location WorklinkFleet#optimize_for_end_user_location}.'''
        result = self._values.get("optimize_for_end_user_location")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorklinkFleetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.worklink.WorklinkFleetIdentityProvider",
    jsii_struct_bases=[],
    name_mapping={"saml_metadata": "samlMetadata", "type": "type"},
)
class WorklinkFleetIdentityProvider:
    def __init__(self, *, saml_metadata: builtins.str, type: builtins.str) -> None:
        '''
        :param saml_metadata: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#saml_metadata WorklinkFleet#saml_metadata}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#type WorklinkFleet#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WorklinkFleetIdentityProvider.__init__)
            check_type(argname="argument saml_metadata", value=saml_metadata, expected_type=type_hints["saml_metadata"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[str, typing.Any] = {
            "saml_metadata": saml_metadata,
            "type": type,
        }

    @builtins.property
    def saml_metadata(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#saml_metadata WorklinkFleet#saml_metadata}.'''
        result = self._values.get("saml_metadata")
        assert result is not None, "Required property 'saml_metadata' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#type WorklinkFleet#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorklinkFleetIdentityProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorklinkFleetIdentityProviderOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.worklink.WorklinkFleetIdentityProviderOutputReference",
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
            type_hints = typing.get_type_hints(WorklinkFleetIdentityProviderOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samlMetadataInput")
    def saml_metadata_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "samlMetadataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samlMetadata")
    def saml_metadata(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samlMetadata"))

    @saml_metadata.setter
    def saml_metadata(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleetIdentityProviderOutputReference, "saml_metadata").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samlMetadata", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleetIdentityProviderOutputReference, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorklinkFleetIdentityProvider]:
        return typing.cast(typing.Optional[WorklinkFleetIdentityProvider], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorklinkFleetIdentityProvider],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleetIdentityProviderOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.worklink.WorklinkFleetNetwork",
    jsii_struct_bases=[],
    name_mapping={
        "security_group_ids": "securityGroupIds",
        "subnet_ids": "subnetIds",
        "vpc_id": "vpcId",
    },
)
class WorklinkFleetNetwork:
    def __init__(
        self,
        *,
        security_group_ids: typing.Sequence[builtins.str],
        subnet_ids: typing.Sequence[builtins.str],
        vpc_id: builtins.str,
    ) -> None:
        '''
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#security_group_ids WorklinkFleet#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#subnet_ids WorklinkFleet#subnet_ids}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#vpc_id WorklinkFleet#vpc_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WorklinkFleetNetwork.__init__)
            check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
            check_type(argname="argument subnet_ids", value=subnet_ids, expected_type=type_hints["subnet_ids"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
        self._values: typing.Dict[str, typing.Any] = {
            "security_group_ids": security_group_ids,
            "subnet_ids": subnet_ids,
            "vpc_id": vpc_id,
        }

    @builtins.property
    def security_group_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#security_group_ids WorklinkFleet#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        assert result is not None, "Required property 'security_group_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#subnet_ids WorklinkFleet#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_fleet#vpc_id WorklinkFleet#vpc_id}.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorklinkFleetNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorklinkFleetNetworkOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.worklink.WorklinkFleetNetworkOutputReference",
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
            type_hints = typing.get_type_hints(WorklinkFleetNetworkOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleetNetworkOutputReference, "security_group_ids").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleetNetworkOutputReference, "subnet_ids").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleetNetworkOutputReference, "vpc_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorklinkFleetNetwork]:
        return typing.cast(typing.Optional[WorklinkFleetNetwork], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[WorklinkFleetNetwork]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkFleetNetworkOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class WorklinkWebsiteCertificateAuthorityAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.worklink.WorklinkWebsiteCertificateAuthorityAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association aws_worklink_website_certificate_authority_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        certificate: builtins.str,
        fleet_arn: builtins.str,
        display_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association aws_worklink_website_certificate_authority_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#certificate WorklinkWebsiteCertificateAuthorityAssociation#certificate}.
        :param fleet_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#fleet_arn WorklinkWebsiteCertificateAuthorityAssociation#fleet_arn}.
        :param display_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#display_name WorklinkWebsiteCertificateAuthorityAssociation#display_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#id WorklinkWebsiteCertificateAuthorityAssociation#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WorklinkWebsiteCertificateAuthorityAssociation.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = WorklinkWebsiteCertificateAuthorityAssociationConfig(
            certificate=certificate,
            fleet_arn=fleet_arn,
            display_name=display_name,
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

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

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
    @jsii.member(jsii_name="websiteCaId")
    def website_ca_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "websiteCaId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fleetArnInput")
    def fleet_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fleetArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkWebsiteCertificateAuthorityAssociation, "certificate").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkWebsiteCertificateAuthorityAssociation, "display_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fleetArn")
    def fleet_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fleetArn"))

    @fleet_arn.setter
    def fleet_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkWebsiteCertificateAuthorityAssociation, "fleet_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fleetArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(WorklinkWebsiteCertificateAuthorityAssociation, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.worklink.WorklinkWebsiteCertificateAuthorityAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "certificate": "certificate",
        "fleet_arn": "fleetArn",
        "display_name": "displayName",
        "id": "id",
    },
)
class WorklinkWebsiteCertificateAuthorityAssociationConfig(
    cdktf.TerraformMetaArguments,
):
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
        certificate: builtins.str,
        fleet_arn: builtins.str,
        display_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS WorkLink.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#certificate WorklinkWebsiteCertificateAuthorityAssociation#certificate}.
        :param fleet_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#fleet_arn WorklinkWebsiteCertificateAuthorityAssociation#fleet_arn}.
        :param display_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#display_name WorklinkWebsiteCertificateAuthorityAssociation#display_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#id WorklinkWebsiteCertificateAuthorityAssociation#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(WorklinkWebsiteCertificateAuthorityAssociationConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument fleet_arn", value=fleet_arn, expected_type=type_hints["fleet_arn"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "certificate": certificate,
            "fleet_arn": fleet_arn,
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
        if display_name is not None:
            self._values["display_name"] = display_name
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
    def certificate(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#certificate WorklinkWebsiteCertificateAuthorityAssociation#certificate}.'''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def fleet_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#fleet_arn WorklinkWebsiteCertificateAuthorityAssociation#fleet_arn}.'''
        result = self._values.get("fleet_arn")
        assert result is not None, "Required property 'fleet_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#display_name WorklinkWebsiteCertificateAuthorityAssociation#display_name}.'''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/worklink_website_certificate_authority_association#id WorklinkWebsiteCertificateAuthorityAssociation#id}.

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
        return "WorklinkWebsiteCertificateAuthorityAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "WorklinkFleet",
    "WorklinkFleetConfig",
    "WorklinkFleetIdentityProvider",
    "WorklinkFleetIdentityProviderOutputReference",
    "WorklinkFleetNetwork",
    "WorklinkFleetNetworkOutputReference",
    "WorklinkWebsiteCertificateAuthorityAssociation",
    "WorklinkWebsiteCertificateAuthorityAssociationConfig",
]

publication.publish()
