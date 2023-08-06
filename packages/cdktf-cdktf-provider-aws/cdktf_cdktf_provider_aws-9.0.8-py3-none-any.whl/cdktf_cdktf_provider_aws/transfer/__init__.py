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


class DataAwsTransferServer(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.DataAwsTransferServer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/transfer_server aws_transfer_server}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        server_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/transfer_server aws_transfer_server} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/transfer_server#server_id DataAwsTransferServer#server_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/transfer_server#id DataAwsTransferServer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsTransferServer.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsTransferServerConfig(
            server_id=server_id,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderType")
    def identity_provider_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invocationRole")
    def invocation_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invocationRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingRole")
    def logging_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "loggingRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocols")
    def protocols(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "protocols"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityPolicyName")
    def security_policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityPolicyName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdInput")
    def server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsTransferServer, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverId"))

    @server_id.setter
    def server_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsTransferServer, "server_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.DataAwsTransferServerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "server_id": "serverId",
        "id": "id",
    },
)
class DataAwsTransferServerConfig(cdktf.TerraformMetaArguments):
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
        server_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Transfer.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/transfer_server#server_id DataAwsTransferServer#server_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/transfer_server#id DataAwsTransferServer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsTransferServerConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument server_id", value=server_id, expected_type=type_hints["server_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "server_id": server_id,
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
    def server_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/transfer_server#server_id DataAwsTransferServer#server_id}.'''
        result = self._values.get("server_id")
        assert result is not None, "Required property 'server_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/transfer_server#id DataAwsTransferServer#id}.

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
        return "DataAwsTransferServerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferAccess(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferAccess",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/transfer_access aws_transfer_access}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        external_id: builtins.str,
        server_id: builtins.str,
        home_directory: typing.Optional[builtins.str] = None,
        home_directory_mappings: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferAccessHomeDirectoryMappings", typing.Dict[str, typing.Any]]]]] = None,
        home_directory_type: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        posix_profile: typing.Optional[typing.Union["TransferAccessPosixProfile", typing.Dict[str, typing.Any]]] = None,
        role: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/transfer_access aws_transfer_access} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#external_id TransferAccess#external_id}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#server_id TransferAccess#server_id}.
        :param home_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory TransferAccess#home_directory}.
        :param home_directory_mappings: home_directory_mappings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_mappings TransferAccess#home_directory_mappings}
        :param home_directory_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_type TransferAccess#home_directory_type}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#id TransferAccess#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#policy TransferAccess#policy}.
        :param posix_profile: posix_profile block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#posix_profile TransferAccess#posix_profile}
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#role TransferAccess#role}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferAccess.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TransferAccessConfig(
            external_id=external_id,
            server_id=server_id,
            home_directory=home_directory,
            home_directory_mappings=home_directory_mappings,
            home_directory_type=home_directory_type,
            id=id,
            policy=policy,
            posix_profile=posix_profile,
            role=role,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putHomeDirectoryMappings")
    def put_home_directory_mappings(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferAccessHomeDirectoryMappings", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferAccess.put_home_directory_mappings)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHomeDirectoryMappings", [value]))

    @jsii.member(jsii_name="putPosixProfile")
    def put_posix_profile(
        self,
        *,
        gid: jsii.Number,
        uid: jsii.Number,
        secondary_gids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#gid TransferAccess#gid}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#uid TransferAccess#uid}.
        :param secondary_gids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#secondary_gids TransferAccess#secondary_gids}.
        '''
        value = TransferAccessPosixProfile(
            gid=gid, uid=uid, secondary_gids=secondary_gids
        )

        return typing.cast(None, jsii.invoke(self, "putPosixProfile", [value]))

    @jsii.member(jsii_name="resetHomeDirectory")
    def reset_home_directory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectory", []))

    @jsii.member(jsii_name="resetHomeDirectoryMappings")
    def reset_home_directory_mappings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectoryMappings", []))

    @jsii.member(jsii_name="resetHomeDirectoryType")
    def reset_home_directory_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectoryType", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @jsii.member(jsii_name="resetPosixProfile")
    def reset_posix_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPosixProfile", []))

    @jsii.member(jsii_name="resetRole")
    def reset_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRole", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryMappings")
    def home_directory_mappings(self) -> "TransferAccessHomeDirectoryMappingsList":
        return typing.cast("TransferAccessHomeDirectoryMappingsList", jsii.get(self, "homeDirectoryMappings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixProfile")
    def posix_profile(self) -> "TransferAccessPosixProfileOutputReference":
        return typing.cast("TransferAccessPosixProfileOutputReference", jsii.get(self, "posixProfile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalIdInput")
    def external_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryInput")
    def home_directory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homeDirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryMappingsInput")
    def home_directory_mappings_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferAccessHomeDirectoryMappings"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferAccessHomeDirectoryMappings"]]], jsii.get(self, "homeDirectoryMappingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryTypeInput")
    def home_directory_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homeDirectoryTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixProfileInput")
    def posix_profile_input(self) -> typing.Optional["TransferAccessPosixProfile"]:
        return typing.cast(typing.Optional["TransferAccessPosixProfile"], jsii.get(self, "posixProfileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdInput")
    def server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @external_id.setter
    def external_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccess, "external_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "externalId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectory")
    def home_directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homeDirectory"))

    @home_directory.setter
    def home_directory(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccess, "home_directory").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "homeDirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryType")
    def home_directory_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homeDirectoryType"))

    @home_directory_type.setter
    def home_directory_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccess, "home_directory_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "homeDirectoryType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccess, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccess, "policy").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccess, "role").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverId"))

    @server_id.setter
    def server_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccess, "server_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferAccessConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "external_id": "externalId",
        "server_id": "serverId",
        "home_directory": "homeDirectory",
        "home_directory_mappings": "homeDirectoryMappings",
        "home_directory_type": "homeDirectoryType",
        "id": "id",
        "policy": "policy",
        "posix_profile": "posixProfile",
        "role": "role",
    },
)
class TransferAccessConfig(cdktf.TerraformMetaArguments):
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
        external_id: builtins.str,
        server_id: builtins.str,
        home_directory: typing.Optional[builtins.str] = None,
        home_directory_mappings: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferAccessHomeDirectoryMappings", typing.Dict[str, typing.Any]]]]] = None,
        home_directory_type: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        posix_profile: typing.Optional[typing.Union["TransferAccessPosixProfile", typing.Dict[str, typing.Any]]] = None,
        role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Transfer.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#external_id TransferAccess#external_id}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#server_id TransferAccess#server_id}.
        :param home_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory TransferAccess#home_directory}.
        :param home_directory_mappings: home_directory_mappings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_mappings TransferAccess#home_directory_mappings}
        :param home_directory_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_type TransferAccess#home_directory_type}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#id TransferAccess#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#policy TransferAccess#policy}.
        :param posix_profile: posix_profile block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#posix_profile TransferAccess#posix_profile}
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#role TransferAccess#role}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(posix_profile, dict):
            posix_profile = TransferAccessPosixProfile(**posix_profile)
        if __debug__:
            type_hints = typing.get_type_hints(TransferAccessConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument external_id", value=external_id, expected_type=type_hints["external_id"])
            check_type(argname="argument server_id", value=server_id, expected_type=type_hints["server_id"])
            check_type(argname="argument home_directory", value=home_directory, expected_type=type_hints["home_directory"])
            check_type(argname="argument home_directory_mappings", value=home_directory_mappings, expected_type=type_hints["home_directory_mappings"])
            check_type(argname="argument home_directory_type", value=home_directory_type, expected_type=type_hints["home_directory_type"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument posix_profile", value=posix_profile, expected_type=type_hints["posix_profile"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[str, typing.Any] = {
            "external_id": external_id,
            "server_id": server_id,
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
        if home_directory is not None:
            self._values["home_directory"] = home_directory
        if home_directory_mappings is not None:
            self._values["home_directory_mappings"] = home_directory_mappings
        if home_directory_type is not None:
            self._values["home_directory_type"] = home_directory_type
        if id is not None:
            self._values["id"] = id
        if policy is not None:
            self._values["policy"] = policy
        if posix_profile is not None:
            self._values["posix_profile"] = posix_profile
        if role is not None:
            self._values["role"] = role

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
    def external_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#external_id TransferAccess#external_id}.'''
        result = self._values.get("external_id")
        assert result is not None, "Required property 'external_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#server_id TransferAccess#server_id}.'''
        result = self._values.get("server_id")
        assert result is not None, "Required property 'server_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def home_directory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory TransferAccess#home_directory}.'''
        result = self._values.get("home_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def home_directory_mappings(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferAccessHomeDirectoryMappings"]]]:
        '''home_directory_mappings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_mappings TransferAccess#home_directory_mappings}
        '''
        result = self._values.get("home_directory_mappings")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferAccessHomeDirectoryMappings"]]], result)

    @builtins.property
    def home_directory_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_type TransferAccess#home_directory_type}.'''
        result = self._values.get("home_directory_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#id TransferAccess#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#policy TransferAccess#policy}.'''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def posix_profile(self) -> typing.Optional["TransferAccessPosixProfile"]:
        '''posix_profile block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#posix_profile TransferAccess#posix_profile}
        '''
        result = self._values.get("posix_profile")
        return typing.cast(typing.Optional["TransferAccessPosixProfile"], result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#role TransferAccess#role}.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferAccessConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferAccessHomeDirectoryMappings",
    jsii_struct_bases=[],
    name_mapping={"entry": "entry", "target": "target"},
)
class TransferAccessHomeDirectoryMappings:
    def __init__(self, *, entry: builtins.str, target: builtins.str) -> None:
        '''
        :param entry: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#entry TransferAccess#entry}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#target TransferAccess#target}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferAccessHomeDirectoryMappings.__init__)
            check_type(argname="argument entry", value=entry, expected_type=type_hints["entry"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        self._values: typing.Dict[str, typing.Any] = {
            "entry": entry,
            "target": target,
        }

    @builtins.property
    def entry(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#entry TransferAccess#entry}.'''
        result = self._values.get("entry")
        assert result is not None, "Required property 'entry' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#target TransferAccess#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferAccessHomeDirectoryMappings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferAccessHomeDirectoryMappingsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferAccessHomeDirectoryMappingsList",
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
            type_hints = typing.get_type_hints(TransferAccessHomeDirectoryMappingsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "TransferAccessHomeDirectoryMappingsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferAccessHomeDirectoryMappingsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("TransferAccessHomeDirectoryMappingsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccessHomeDirectoryMappingsList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferAccessHomeDirectoryMappingsList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferAccessHomeDirectoryMappingsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferAccessHomeDirectoryMappings]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferAccessHomeDirectoryMappings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferAccessHomeDirectoryMappings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccessHomeDirectoryMappingsList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferAccessHomeDirectoryMappingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferAccessHomeDirectoryMappingsOutputReference",
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
            type_hints = typing.get_type_hints(TransferAccessHomeDirectoryMappingsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entryInput")
    def entry_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entry")
    def entry(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entry"))

    @entry.setter
    def entry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccessHomeDirectoryMappingsOutputReference, "entry").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entry", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccessHomeDirectoryMappingsOutputReference, "target").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[TransferAccessHomeDirectoryMappings, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[TransferAccessHomeDirectoryMappings, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[TransferAccessHomeDirectoryMappings, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccessHomeDirectoryMappingsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferAccessPosixProfile",
    jsii_struct_bases=[],
    name_mapping={"gid": "gid", "uid": "uid", "secondary_gids": "secondaryGids"},
)
class TransferAccessPosixProfile:
    def __init__(
        self,
        *,
        gid: jsii.Number,
        uid: jsii.Number,
        secondary_gids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#gid TransferAccess#gid}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#uid TransferAccess#uid}.
        :param secondary_gids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#secondary_gids TransferAccess#secondary_gids}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferAccessPosixProfile.__init__)
            check_type(argname="argument gid", value=gid, expected_type=type_hints["gid"])
            check_type(argname="argument uid", value=uid, expected_type=type_hints["uid"])
            check_type(argname="argument secondary_gids", value=secondary_gids, expected_type=type_hints["secondary_gids"])
        self._values: typing.Dict[str, typing.Any] = {
            "gid": gid,
            "uid": uid,
        }
        if secondary_gids is not None:
            self._values["secondary_gids"] = secondary_gids

    @builtins.property
    def gid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#gid TransferAccess#gid}.'''
        result = self._values.get("gid")
        assert result is not None, "Required property 'gid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def uid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#uid TransferAccess#uid}.'''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def secondary_gids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#secondary_gids TransferAccess#secondary_gids}.'''
        result = self._values.get("secondary_gids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferAccessPosixProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferAccessPosixProfileOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferAccessPosixProfileOutputReference",
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
            type_hints = typing.get_type_hints(TransferAccessPosixProfileOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSecondaryGids")
    def reset_secondary_gids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondaryGids", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gidInput")
    def gid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGidsInput")
    def secondary_gids_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "secondaryGidsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uidInput")
    def uid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "uidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gid")
    def gid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gid"))

    @gid.setter
    def gid(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccessPosixProfileOutputReference, "gid").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGids")
    def secondary_gids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "secondaryGids"))

    @secondary_gids.setter
    def secondary_gids(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccessPosixProfileOutputReference, "secondary_gids").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryGids", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uid")
    def uid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "uid"))

    @uid.setter
    def uid(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccessPosixProfileOutputReference, "uid").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferAccessPosixProfile]:
        return typing.cast(typing.Optional[TransferAccessPosixProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferAccessPosixProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferAccessPosixProfileOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferServer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferServer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/transfer_server aws_transfer_server}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        certificate: typing.Optional[builtins.str] = None,
        directory_id: typing.Optional[builtins.str] = None,
        domain: typing.Optional[builtins.str] = None,
        endpoint_details: typing.Optional[typing.Union["TransferServerEndpointDetails", typing.Dict[str, typing.Any]]] = None,
        endpoint_type: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        function: typing.Optional[builtins.str] = None,
        host_key: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        identity_provider_type: typing.Optional[builtins.str] = None,
        invocation_role: typing.Optional[builtins.str] = None,
        logging_role: typing.Optional[builtins.str] = None,
        post_authentication_login_banner: typing.Optional[builtins.str] = None,
        pre_authentication_login_banner: typing.Optional[builtins.str] = None,
        protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_policy_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        url: typing.Optional[builtins.str] = None,
        workflow_details: typing.Optional[typing.Union["TransferServerWorkflowDetails", typing.Dict[str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/transfer_server aws_transfer_server} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#certificate TransferServer#certificate}.
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#directory_id TransferServer#directory_id}.
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#domain TransferServer#domain}.
        :param endpoint_details: endpoint_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_details TransferServer#endpoint_details}
        :param endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_type TransferServer#endpoint_type}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#force_destroy TransferServer#force_destroy}.
        :param function: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#function TransferServer#function}.
        :param host_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#host_key TransferServer#host_key}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#id TransferServer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#identity_provider_type TransferServer#identity_provider_type}.
        :param invocation_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#invocation_role TransferServer#invocation_role}.
        :param logging_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#logging_role TransferServer#logging_role}.
        :param post_authentication_login_banner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#post_authentication_login_banner TransferServer#post_authentication_login_banner}.
        :param pre_authentication_login_banner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#pre_authentication_login_banner TransferServer#pre_authentication_login_banner}.
        :param protocols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#protocols TransferServer#protocols}.
        :param security_policy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_policy_name TransferServer#security_policy_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags TransferServer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags_all TransferServer#tags_all}.
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#url TransferServer#url}.
        :param workflow_details: workflow_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#workflow_details TransferServer#workflow_details}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferServer.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TransferServerConfig(
            certificate=certificate,
            directory_id=directory_id,
            domain=domain,
            endpoint_details=endpoint_details,
            endpoint_type=endpoint_type,
            force_destroy=force_destroy,
            function=function,
            host_key=host_key,
            id=id,
            identity_provider_type=identity_provider_type,
            invocation_role=invocation_role,
            logging_role=logging_role,
            post_authentication_login_banner=post_authentication_login_banner,
            pre_authentication_login_banner=pre_authentication_login_banner,
            protocols=protocols,
            security_policy_name=security_policy_name,
            tags=tags,
            tags_all=tags_all,
            url=url,
            workflow_details=workflow_details,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putEndpointDetails")
    def put_endpoint_details(
        self,
        *,
        address_allocation_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc_endpoint_id: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address_allocation_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#address_allocation_ids TransferServer#address_allocation_ids}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_group_ids TransferServer#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#subnet_ids TransferServer#subnet_ids}.
        :param vpc_endpoint_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_endpoint_id TransferServer#vpc_endpoint_id}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_id TransferServer#vpc_id}.
        '''
        value = TransferServerEndpointDetails(
            address_allocation_ids=address_allocation_ids,
            security_group_ids=security_group_ids,
            subnet_ids=subnet_ids,
            vpc_endpoint_id=vpc_endpoint_id,
            vpc_id=vpc_id,
        )

        return typing.cast(None, jsii.invoke(self, "putEndpointDetails", [value]))

    @jsii.member(jsii_name="putWorkflowDetails")
    def put_workflow_details(
        self,
        *,
        on_upload: typing.Optional[typing.Union["TransferServerWorkflowDetailsOnUpload", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param on_upload: on_upload block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#on_upload TransferServer#on_upload}
        '''
        value = TransferServerWorkflowDetails(on_upload=on_upload)

        return typing.cast(None, jsii.invoke(self, "putWorkflowDetails", [value]))

    @jsii.member(jsii_name="resetCertificate")
    def reset_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificate", []))

    @jsii.member(jsii_name="resetDirectoryId")
    def reset_directory_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirectoryId", []))

    @jsii.member(jsii_name="resetDomain")
    def reset_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomain", []))

    @jsii.member(jsii_name="resetEndpointDetails")
    def reset_endpoint_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointDetails", []))

    @jsii.member(jsii_name="resetEndpointType")
    def reset_endpoint_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointType", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetFunction")
    def reset_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunction", []))

    @jsii.member(jsii_name="resetHostKey")
    def reset_host_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostKey", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdentityProviderType")
    def reset_identity_provider_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityProviderType", []))

    @jsii.member(jsii_name="resetInvocationRole")
    def reset_invocation_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInvocationRole", []))

    @jsii.member(jsii_name="resetLoggingRole")
    def reset_logging_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoggingRole", []))

    @jsii.member(jsii_name="resetPostAuthenticationLoginBanner")
    def reset_post_authentication_login_banner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostAuthenticationLoginBanner", []))

    @jsii.member(jsii_name="resetPreAuthenticationLoginBanner")
    def reset_pre_authentication_login_banner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreAuthenticationLoginBanner", []))

    @jsii.member(jsii_name="resetProtocols")
    def reset_protocols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocols", []))

    @jsii.member(jsii_name="resetSecurityPolicyName")
    def reset_security_policy_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityPolicyName", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetWorkflowDetails")
    def reset_workflow_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkflowDetails", []))

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
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointDetails")
    def endpoint_details(self) -> "TransferServerEndpointDetailsOutputReference":
        return typing.cast("TransferServerEndpointDetailsOutputReference", jsii.get(self, "endpointDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostKeyFingerprint")
    def host_key_fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostKeyFingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflowDetails")
    def workflow_details(self) -> "TransferServerWorkflowDetailsOutputReference":
        return typing.cast("TransferServerWorkflowDetailsOutputReference", jsii.get(self, "workflowDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryIdInput")
    def directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointDetailsInput")
    def endpoint_details_input(
        self,
    ) -> typing.Optional["TransferServerEndpointDetails"]:
        return typing.cast(typing.Optional["TransferServerEndpointDetails"], jsii.get(self, "endpointDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointTypeInput")
    def endpoint_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionInput")
    def function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostKeyInput")
    def host_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderTypeInput")
    def identity_provider_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invocationRoleInput")
    def invocation_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "invocationRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingRoleInput")
    def logging_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loggingRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postAuthenticationLoginBannerInput")
    def post_authentication_login_banner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postAuthenticationLoginBannerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preAuthenticationLoginBannerInput")
    def pre_authentication_login_banner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preAuthenticationLoginBannerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocolsInput")
    def protocols_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "protocolsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityPolicyNameInput")
    def security_policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityPolicyNameInput"))

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
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflowDetailsInput")
    def workflow_details_input(
        self,
    ) -> typing.Optional["TransferServerWorkflowDetails"]:
        return typing.cast(typing.Optional["TransferServerWorkflowDetails"], jsii.get(self, "workflowDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "certificate").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "directory_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directoryId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "domain").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointType"))

    @endpoint_type.setter
    def endpoint_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "endpoint_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpointType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroy")
    def force_destroy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceDestroy"))

    @force_destroy.setter
    def force_destroy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "force_destroy").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceDestroy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="function")
    def function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "function"))

    @function.setter
    def function(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "function").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "function", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostKey")
    def host_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostKey"))

    @host_key.setter
    def host_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "host_key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderType")
    def identity_provider_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderType"))

    @identity_provider_type.setter
    def identity_provider_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "identity_provider_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invocationRole")
    def invocation_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invocationRole"))

    @invocation_role.setter
    def invocation_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "invocation_role").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "invocationRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingRole")
    def logging_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "loggingRole"))

    @logging_role.setter
    def logging_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "logging_role").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loggingRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postAuthenticationLoginBanner")
    def post_authentication_login_banner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postAuthenticationLoginBanner"))

    @post_authentication_login_banner.setter
    def post_authentication_login_banner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "post_authentication_login_banner").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postAuthenticationLoginBanner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preAuthenticationLoginBanner")
    def pre_authentication_login_banner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preAuthenticationLoginBanner"))

    @pre_authentication_login_banner.setter
    def pre_authentication_login_banner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "pre_authentication_login_banner").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preAuthenticationLoginBanner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocols")
    def protocols(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "protocols"))

    @protocols.setter
    def protocols(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "protocols").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocols", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityPolicyName")
    def security_policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityPolicyName"))

    @security_policy_name.setter
    def security_policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "security_policy_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityPolicyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServer, "url").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferServerConfig",
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
        "directory_id": "directoryId",
        "domain": "domain",
        "endpoint_details": "endpointDetails",
        "endpoint_type": "endpointType",
        "force_destroy": "forceDestroy",
        "function": "function",
        "host_key": "hostKey",
        "id": "id",
        "identity_provider_type": "identityProviderType",
        "invocation_role": "invocationRole",
        "logging_role": "loggingRole",
        "post_authentication_login_banner": "postAuthenticationLoginBanner",
        "pre_authentication_login_banner": "preAuthenticationLoginBanner",
        "protocols": "protocols",
        "security_policy_name": "securityPolicyName",
        "tags": "tags",
        "tags_all": "tagsAll",
        "url": "url",
        "workflow_details": "workflowDetails",
    },
)
class TransferServerConfig(cdktf.TerraformMetaArguments):
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
        certificate: typing.Optional[builtins.str] = None,
        directory_id: typing.Optional[builtins.str] = None,
        domain: typing.Optional[builtins.str] = None,
        endpoint_details: typing.Optional[typing.Union["TransferServerEndpointDetails", typing.Dict[str, typing.Any]]] = None,
        endpoint_type: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        function: typing.Optional[builtins.str] = None,
        host_key: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        identity_provider_type: typing.Optional[builtins.str] = None,
        invocation_role: typing.Optional[builtins.str] = None,
        logging_role: typing.Optional[builtins.str] = None,
        post_authentication_login_banner: typing.Optional[builtins.str] = None,
        pre_authentication_login_banner: typing.Optional[builtins.str] = None,
        protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_policy_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        url: typing.Optional[builtins.str] = None,
        workflow_details: typing.Optional[typing.Union["TransferServerWorkflowDetails", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''AWS Transfer.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#certificate TransferServer#certificate}.
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#directory_id TransferServer#directory_id}.
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#domain TransferServer#domain}.
        :param endpoint_details: endpoint_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_details TransferServer#endpoint_details}
        :param endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_type TransferServer#endpoint_type}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#force_destroy TransferServer#force_destroy}.
        :param function: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#function TransferServer#function}.
        :param host_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#host_key TransferServer#host_key}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#id TransferServer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#identity_provider_type TransferServer#identity_provider_type}.
        :param invocation_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#invocation_role TransferServer#invocation_role}.
        :param logging_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#logging_role TransferServer#logging_role}.
        :param post_authentication_login_banner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#post_authentication_login_banner TransferServer#post_authentication_login_banner}.
        :param pre_authentication_login_banner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#pre_authentication_login_banner TransferServer#pre_authentication_login_banner}.
        :param protocols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#protocols TransferServer#protocols}.
        :param security_policy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_policy_name TransferServer#security_policy_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags TransferServer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags_all TransferServer#tags_all}.
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#url TransferServer#url}.
        :param workflow_details: workflow_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#workflow_details TransferServer#workflow_details}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(endpoint_details, dict):
            endpoint_details = TransferServerEndpointDetails(**endpoint_details)
        if isinstance(workflow_details, dict):
            workflow_details = TransferServerWorkflowDetails(**workflow_details)
        if __debug__:
            type_hints = typing.get_type_hints(TransferServerConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument directory_id", value=directory_id, expected_type=type_hints["directory_id"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument endpoint_details", value=endpoint_details, expected_type=type_hints["endpoint_details"])
            check_type(argname="argument endpoint_type", value=endpoint_type, expected_type=type_hints["endpoint_type"])
            check_type(argname="argument force_destroy", value=force_destroy, expected_type=type_hints["force_destroy"])
            check_type(argname="argument function", value=function, expected_type=type_hints["function"])
            check_type(argname="argument host_key", value=host_key, expected_type=type_hints["host_key"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_type", value=identity_provider_type, expected_type=type_hints["identity_provider_type"])
            check_type(argname="argument invocation_role", value=invocation_role, expected_type=type_hints["invocation_role"])
            check_type(argname="argument logging_role", value=logging_role, expected_type=type_hints["logging_role"])
            check_type(argname="argument post_authentication_login_banner", value=post_authentication_login_banner, expected_type=type_hints["post_authentication_login_banner"])
            check_type(argname="argument pre_authentication_login_banner", value=pre_authentication_login_banner, expected_type=type_hints["pre_authentication_login_banner"])
            check_type(argname="argument protocols", value=protocols, expected_type=type_hints["protocols"])
            check_type(argname="argument security_policy_name", value=security_policy_name, expected_type=type_hints["security_policy_name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument workflow_details", value=workflow_details, expected_type=type_hints["workflow_details"])
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
        if certificate is not None:
            self._values["certificate"] = certificate
        if directory_id is not None:
            self._values["directory_id"] = directory_id
        if domain is not None:
            self._values["domain"] = domain
        if endpoint_details is not None:
            self._values["endpoint_details"] = endpoint_details
        if endpoint_type is not None:
            self._values["endpoint_type"] = endpoint_type
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if function is not None:
            self._values["function"] = function
        if host_key is not None:
            self._values["host_key"] = host_key
        if id is not None:
            self._values["id"] = id
        if identity_provider_type is not None:
            self._values["identity_provider_type"] = identity_provider_type
        if invocation_role is not None:
            self._values["invocation_role"] = invocation_role
        if logging_role is not None:
            self._values["logging_role"] = logging_role
        if post_authentication_login_banner is not None:
            self._values["post_authentication_login_banner"] = post_authentication_login_banner
        if pre_authentication_login_banner is not None:
            self._values["pre_authentication_login_banner"] = pre_authentication_login_banner
        if protocols is not None:
            self._values["protocols"] = protocols
        if security_policy_name is not None:
            self._values["security_policy_name"] = security_policy_name
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if url is not None:
            self._values["url"] = url
        if workflow_details is not None:
            self._values["workflow_details"] = workflow_details

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
    def certificate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#certificate TransferServer#certificate}.'''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def directory_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#directory_id TransferServer#directory_id}.'''
        result = self._values.get("directory_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#domain TransferServer#domain}.'''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_details(self) -> typing.Optional["TransferServerEndpointDetails"]:
        '''endpoint_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_details TransferServer#endpoint_details}
        '''
        result = self._values.get("endpoint_details")
        return typing.cast(typing.Optional["TransferServerEndpointDetails"], result)

    @builtins.property
    def endpoint_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_type TransferServer#endpoint_type}.'''
        result = self._values.get("endpoint_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#force_destroy TransferServer#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def function(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#function TransferServer#function}.'''
        result = self._values.get("function")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#host_key TransferServer#host_key}.'''
        result = self._values.get("host_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#id TransferServer#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_provider_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#identity_provider_type TransferServer#identity_provider_type}.'''
        result = self._values.get("identity_provider_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invocation_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#invocation_role TransferServer#invocation_role}.'''
        result = self._values.get("invocation_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#logging_role TransferServer#logging_role}.'''
        result = self._values.get("logging_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_authentication_login_banner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#post_authentication_login_banner TransferServer#post_authentication_login_banner}.'''
        result = self._values.get("post_authentication_login_banner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_authentication_login_banner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#pre_authentication_login_banner TransferServer#pre_authentication_login_banner}.'''
        result = self._values.get("pre_authentication_login_banner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocols(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#protocols TransferServer#protocols}.'''
        result = self._values.get("protocols")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def security_policy_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_policy_name TransferServer#security_policy_name}.'''
        result = self._values.get("security_policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags TransferServer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags_all TransferServer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#url TransferServer#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_details(self) -> typing.Optional["TransferServerWorkflowDetails"]:
        '''workflow_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#workflow_details TransferServer#workflow_details}
        '''
        result = self._values.get("workflow_details")
        return typing.cast(typing.Optional["TransferServerWorkflowDetails"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferServerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferServerEndpointDetails",
    jsii_struct_bases=[],
    name_mapping={
        "address_allocation_ids": "addressAllocationIds",
        "security_group_ids": "securityGroupIds",
        "subnet_ids": "subnetIds",
        "vpc_endpoint_id": "vpcEndpointId",
        "vpc_id": "vpcId",
    },
)
class TransferServerEndpointDetails:
    def __init__(
        self,
        *,
        address_allocation_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc_endpoint_id: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address_allocation_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#address_allocation_ids TransferServer#address_allocation_ids}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_group_ids TransferServer#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#subnet_ids TransferServer#subnet_ids}.
        :param vpc_endpoint_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_endpoint_id TransferServer#vpc_endpoint_id}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_id TransferServer#vpc_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferServerEndpointDetails.__init__)
            check_type(argname="argument address_allocation_ids", value=address_allocation_ids, expected_type=type_hints["address_allocation_ids"])
            check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
            check_type(argname="argument subnet_ids", value=subnet_ids, expected_type=type_hints["subnet_ids"])
            check_type(argname="argument vpc_endpoint_id", value=vpc_endpoint_id, expected_type=type_hints["vpc_endpoint_id"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
        self._values: typing.Dict[str, typing.Any] = {}
        if address_allocation_ids is not None:
            self._values["address_allocation_ids"] = address_allocation_ids
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if subnet_ids is not None:
            self._values["subnet_ids"] = subnet_ids
        if vpc_endpoint_id is not None:
            self._values["vpc_endpoint_id"] = vpc_endpoint_id
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id

    @builtins.property
    def address_allocation_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#address_allocation_ids TransferServer#address_allocation_ids}.'''
        result = self._values.get("address_allocation_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_group_ids TransferServer#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#subnet_ids TransferServer#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vpc_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_endpoint_id TransferServer#vpc_endpoint_id}.'''
        result = self._values.get("vpc_endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_id TransferServer#vpc_id}.'''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferServerEndpointDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferServerEndpointDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferServerEndpointDetailsOutputReference",
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
            type_hints = typing.get_type_hints(TransferServerEndpointDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAddressAllocationIds")
    def reset_address_allocation_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddressAllocationIds", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetSubnetIds")
    def reset_subnet_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetIds", []))

    @jsii.member(jsii_name="resetVpcEndpointId")
    def reset_vpc_endpoint_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcEndpointId", []))

    @jsii.member(jsii_name="resetVpcId")
    def reset_vpc_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcId", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressAllocationIdsInput")
    def address_allocation_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "addressAllocationIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointIdInput")
    def vpc_endpoint_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcEndpointIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressAllocationIds")
    def address_allocation_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "addressAllocationIds"))

    @address_allocation_ids.setter
    def address_allocation_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServerEndpointDetailsOutputReference, "address_allocation_ids").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addressAllocationIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServerEndpointDetailsOutputReference, "security_group_ids").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServerEndpointDetailsOutputReference, "subnet_ids").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcEndpointId"))

    @vpc_endpoint_id.setter
    def vpc_endpoint_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServerEndpointDetailsOutputReference, "vpc_endpoint_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcEndpointId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServerEndpointDetailsOutputReference, "vpc_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferServerEndpointDetails]:
        return typing.cast(typing.Optional[TransferServerEndpointDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferServerEndpointDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServerEndpointDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferServerWorkflowDetails",
    jsii_struct_bases=[],
    name_mapping={"on_upload": "onUpload"},
)
class TransferServerWorkflowDetails:
    def __init__(
        self,
        *,
        on_upload: typing.Optional[typing.Union["TransferServerWorkflowDetailsOnUpload", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param on_upload: on_upload block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#on_upload TransferServer#on_upload}
        '''
        if isinstance(on_upload, dict):
            on_upload = TransferServerWorkflowDetailsOnUpload(**on_upload)
        if __debug__:
            type_hints = typing.get_type_hints(TransferServerWorkflowDetails.__init__)
            check_type(argname="argument on_upload", value=on_upload, expected_type=type_hints["on_upload"])
        self._values: typing.Dict[str, typing.Any] = {}
        if on_upload is not None:
            self._values["on_upload"] = on_upload

    @builtins.property
    def on_upload(self) -> typing.Optional["TransferServerWorkflowDetailsOnUpload"]:
        '''on_upload block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#on_upload TransferServer#on_upload}
        '''
        result = self._values.get("on_upload")
        return typing.cast(typing.Optional["TransferServerWorkflowDetailsOnUpload"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferServerWorkflowDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferServerWorkflowDetailsOnUpload",
    jsii_struct_bases=[],
    name_mapping={"execution_role": "executionRole", "workflow_id": "workflowId"},
)
class TransferServerWorkflowDetailsOnUpload:
    def __init__(
        self,
        *,
        execution_role: builtins.str,
        workflow_id: builtins.str,
    ) -> None:
        '''
        :param execution_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#execution_role TransferServer#execution_role}.
        :param workflow_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#workflow_id TransferServer#workflow_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferServerWorkflowDetailsOnUpload.__init__)
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument workflow_id", value=workflow_id, expected_type=type_hints["workflow_id"])
        self._values: typing.Dict[str, typing.Any] = {
            "execution_role": execution_role,
            "workflow_id": workflow_id,
        }

    @builtins.property
    def execution_role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#execution_role TransferServer#execution_role}.'''
        result = self._values.get("execution_role")
        assert result is not None, "Required property 'execution_role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workflow_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#workflow_id TransferServer#workflow_id}.'''
        result = self._values.get("workflow_id")
        assert result is not None, "Required property 'workflow_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferServerWorkflowDetailsOnUpload(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferServerWorkflowDetailsOnUploadOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferServerWorkflowDetailsOnUploadOutputReference",
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
            type_hints = typing.get_type_hints(TransferServerWorkflowDetailsOnUploadOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleInput")
    def execution_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "executionRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflowIdInput")
    def workflow_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workflowIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionRole"))

    @execution_role.setter
    def execution_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServerWorkflowDetailsOnUploadOutputReference, "execution_role").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "executionRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflowId")
    def workflow_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workflowId"))

    @workflow_id.setter
    def workflow_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServerWorkflowDetailsOnUploadOutputReference, "workflow_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workflowId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferServerWorkflowDetailsOnUpload]:
        return typing.cast(typing.Optional[TransferServerWorkflowDetailsOnUpload], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferServerWorkflowDetailsOnUpload],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServerWorkflowDetailsOnUploadOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferServerWorkflowDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferServerWorkflowDetailsOutputReference",
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
            type_hints = typing.get_type_hints(TransferServerWorkflowDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOnUpload")
    def put_on_upload(
        self,
        *,
        execution_role: builtins.str,
        workflow_id: builtins.str,
    ) -> None:
        '''
        :param execution_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#execution_role TransferServer#execution_role}.
        :param workflow_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#workflow_id TransferServer#workflow_id}.
        '''
        value = TransferServerWorkflowDetailsOnUpload(
            execution_role=execution_role, workflow_id=workflow_id
        )

        return typing.cast(None, jsii.invoke(self, "putOnUpload", [value]))

    @jsii.member(jsii_name="resetOnUpload")
    def reset_on_upload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnUpload", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onUpload")
    def on_upload(self) -> TransferServerWorkflowDetailsOnUploadOutputReference:
        return typing.cast(TransferServerWorkflowDetailsOnUploadOutputReference, jsii.get(self, "onUpload"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onUploadInput")
    def on_upload_input(self) -> typing.Optional[TransferServerWorkflowDetailsOnUpload]:
        return typing.cast(typing.Optional[TransferServerWorkflowDetailsOnUpload], jsii.get(self, "onUploadInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferServerWorkflowDetails]:
        return typing.cast(typing.Optional[TransferServerWorkflowDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferServerWorkflowDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferServerWorkflowDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferSshKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferSshKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key aws_transfer_ssh_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        body: builtins.str,
        server_id: builtins.str,
        user_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key aws_transfer_ssh_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#body TransferSshKey#body}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#server_id TransferSshKey#server_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#user_name TransferSshKey#user_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#id TransferSshKey#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferSshKey.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TransferSshKeyConfig(
            body=body,
            server_id=server_id,
            user_name=user_name,
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
    @jsii.member(jsii_name="bodyInput")
    def body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdInput")
    def server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @body.setter
    def body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferSshKey, "body").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "body", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferSshKey, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverId"))

    @server_id.setter
    def server_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferSshKey, "server_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferSshKey, "user_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferSshKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "body": "body",
        "server_id": "serverId",
        "user_name": "userName",
        "id": "id",
    },
)
class TransferSshKeyConfig(cdktf.TerraformMetaArguments):
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
        body: builtins.str,
        server_id: builtins.str,
        user_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Transfer.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#body TransferSshKey#body}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#server_id TransferSshKey#server_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#user_name TransferSshKey#user_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#id TransferSshKey#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(TransferSshKeyConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument body", value=body, expected_type=type_hints["body"])
            check_type(argname="argument server_id", value=server_id, expected_type=type_hints["server_id"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "body": body,
            "server_id": server_id,
            "user_name": user_name,
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
    def body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#body TransferSshKey#body}.'''
        result = self._values.get("body")
        assert result is not None, "Required property 'body' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#server_id TransferSshKey#server_id}.'''
        result = self._values.get("server_id")
        assert result is not None, "Required property 'server_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#user_name TransferSshKey#user_name}.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#id TransferSshKey#id}.

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
        return "TransferSshKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferUser(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/transfer_user aws_transfer_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        role: builtins.str,
        server_id: builtins.str,
        user_name: builtins.str,
        home_directory: typing.Optional[builtins.str] = None,
        home_directory_mappings: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferUserHomeDirectoryMappings", typing.Dict[str, typing.Any]]]]] = None,
        home_directory_type: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        posix_profile: typing.Optional[typing.Union["TransferUserPosixProfile", typing.Dict[str, typing.Any]]] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/transfer_user aws_transfer_user} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#role TransferUser#role}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#server_id TransferUser#server_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#user_name TransferUser#user_name}.
        :param home_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory TransferUser#home_directory}.
        :param home_directory_mappings: home_directory_mappings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_mappings TransferUser#home_directory_mappings}
        :param home_directory_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_type TransferUser#home_directory_type}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#id TransferUser#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#policy TransferUser#policy}.
        :param posix_profile: posix_profile block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#posix_profile TransferUser#posix_profile}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags TransferUser#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags_all TransferUser#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferUser.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TransferUserConfig(
            role=role,
            server_id=server_id,
            user_name=user_name,
            home_directory=home_directory,
            home_directory_mappings=home_directory_mappings,
            home_directory_type=home_directory_type,
            id=id,
            policy=policy,
            posix_profile=posix_profile,
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

    @jsii.member(jsii_name="putHomeDirectoryMappings")
    def put_home_directory_mappings(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferUserHomeDirectoryMappings", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferUser.put_home_directory_mappings)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHomeDirectoryMappings", [value]))

    @jsii.member(jsii_name="putPosixProfile")
    def put_posix_profile(
        self,
        *,
        gid: jsii.Number,
        uid: jsii.Number,
        secondary_gids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#gid TransferUser#gid}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#uid TransferUser#uid}.
        :param secondary_gids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#secondary_gids TransferUser#secondary_gids}.
        '''
        value = TransferUserPosixProfile(
            gid=gid, uid=uid, secondary_gids=secondary_gids
        )

        return typing.cast(None, jsii.invoke(self, "putPosixProfile", [value]))

    @jsii.member(jsii_name="resetHomeDirectory")
    def reset_home_directory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectory", []))

    @jsii.member(jsii_name="resetHomeDirectoryMappings")
    def reset_home_directory_mappings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectoryMappings", []))

    @jsii.member(jsii_name="resetHomeDirectoryType")
    def reset_home_directory_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectoryType", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @jsii.member(jsii_name="resetPosixProfile")
    def reset_posix_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPosixProfile", []))

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
    @jsii.member(jsii_name="homeDirectoryMappings")
    def home_directory_mappings(self) -> "TransferUserHomeDirectoryMappingsList":
        return typing.cast("TransferUserHomeDirectoryMappingsList", jsii.get(self, "homeDirectoryMappings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixProfile")
    def posix_profile(self) -> "TransferUserPosixProfileOutputReference":
        return typing.cast("TransferUserPosixProfileOutputReference", jsii.get(self, "posixProfile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryInput")
    def home_directory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homeDirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryMappingsInput")
    def home_directory_mappings_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferUserHomeDirectoryMappings"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferUserHomeDirectoryMappings"]]], jsii.get(self, "homeDirectoryMappingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryTypeInput")
    def home_directory_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homeDirectoryTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixProfileInput")
    def posix_profile_input(self) -> typing.Optional["TransferUserPosixProfile"]:
        return typing.cast(typing.Optional["TransferUserPosixProfile"], jsii.get(self, "posixProfileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdInput")
    def server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverIdInput"))

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
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectory")
    def home_directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homeDirectory"))

    @home_directory.setter
    def home_directory(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUser, "home_directory").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "homeDirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryType")
    def home_directory_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homeDirectoryType"))

    @home_directory_type.setter
    def home_directory_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUser, "home_directory_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "homeDirectoryType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUser, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUser, "policy").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUser, "role").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverId"))

    @server_id.setter
    def server_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUser, "server_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUser, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUser, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUser, "user_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "role": "role",
        "server_id": "serverId",
        "user_name": "userName",
        "home_directory": "homeDirectory",
        "home_directory_mappings": "homeDirectoryMappings",
        "home_directory_type": "homeDirectoryType",
        "id": "id",
        "policy": "policy",
        "posix_profile": "posixProfile",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class TransferUserConfig(cdktf.TerraformMetaArguments):
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
        role: builtins.str,
        server_id: builtins.str,
        user_name: builtins.str,
        home_directory: typing.Optional[builtins.str] = None,
        home_directory_mappings: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferUserHomeDirectoryMappings", typing.Dict[str, typing.Any]]]]] = None,
        home_directory_type: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        posix_profile: typing.Optional[typing.Union["TransferUserPosixProfile", typing.Dict[str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Transfer.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#role TransferUser#role}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#server_id TransferUser#server_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#user_name TransferUser#user_name}.
        :param home_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory TransferUser#home_directory}.
        :param home_directory_mappings: home_directory_mappings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_mappings TransferUser#home_directory_mappings}
        :param home_directory_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_type TransferUser#home_directory_type}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#id TransferUser#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#policy TransferUser#policy}.
        :param posix_profile: posix_profile block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#posix_profile TransferUser#posix_profile}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags TransferUser#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags_all TransferUser#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(posix_profile, dict):
            posix_profile = TransferUserPosixProfile(**posix_profile)
        if __debug__:
            type_hints = typing.get_type_hints(TransferUserConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument server_id", value=server_id, expected_type=type_hints["server_id"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
            check_type(argname="argument home_directory", value=home_directory, expected_type=type_hints["home_directory"])
            check_type(argname="argument home_directory_mappings", value=home_directory_mappings, expected_type=type_hints["home_directory_mappings"])
            check_type(argname="argument home_directory_type", value=home_directory_type, expected_type=type_hints["home_directory_type"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument posix_profile", value=posix_profile, expected_type=type_hints["posix_profile"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "role": role,
            "server_id": server_id,
            "user_name": user_name,
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
        if home_directory is not None:
            self._values["home_directory"] = home_directory
        if home_directory_mappings is not None:
            self._values["home_directory_mappings"] = home_directory_mappings
        if home_directory_type is not None:
            self._values["home_directory_type"] = home_directory_type
        if id is not None:
            self._values["id"] = id
        if policy is not None:
            self._values["policy"] = policy
        if posix_profile is not None:
            self._values["posix_profile"] = posix_profile
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
    def role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#role TransferUser#role}.'''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#server_id TransferUser#server_id}.'''
        result = self._values.get("server_id")
        assert result is not None, "Required property 'server_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#user_name TransferUser#user_name}.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def home_directory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory TransferUser#home_directory}.'''
        result = self._values.get("home_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def home_directory_mappings(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferUserHomeDirectoryMappings"]]]:
        '''home_directory_mappings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_mappings TransferUser#home_directory_mappings}
        '''
        result = self._values.get("home_directory_mappings")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferUserHomeDirectoryMappings"]]], result)

    @builtins.property
    def home_directory_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_type TransferUser#home_directory_type}.'''
        result = self._values.get("home_directory_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#id TransferUser#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#policy TransferUser#policy}.'''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def posix_profile(self) -> typing.Optional["TransferUserPosixProfile"]:
        '''posix_profile block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#posix_profile TransferUser#posix_profile}
        '''
        result = self._values.get("posix_profile")
        return typing.cast(typing.Optional["TransferUserPosixProfile"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags TransferUser#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags_all TransferUser#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferUserHomeDirectoryMappings",
    jsii_struct_bases=[],
    name_mapping={"entry": "entry", "target": "target"},
)
class TransferUserHomeDirectoryMappings:
    def __init__(self, *, entry: builtins.str, target: builtins.str) -> None:
        '''
        :param entry: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#entry TransferUser#entry}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#target TransferUser#target}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferUserHomeDirectoryMappings.__init__)
            check_type(argname="argument entry", value=entry, expected_type=type_hints["entry"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        self._values: typing.Dict[str, typing.Any] = {
            "entry": entry,
            "target": target,
        }

    @builtins.property
    def entry(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#entry TransferUser#entry}.'''
        result = self._values.get("entry")
        assert result is not None, "Required property 'entry' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#target TransferUser#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferUserHomeDirectoryMappings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferUserHomeDirectoryMappingsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferUserHomeDirectoryMappingsList",
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
            type_hints = typing.get_type_hints(TransferUserHomeDirectoryMappingsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "TransferUserHomeDirectoryMappingsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferUserHomeDirectoryMappingsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("TransferUserHomeDirectoryMappingsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUserHomeDirectoryMappingsList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferUserHomeDirectoryMappingsList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferUserHomeDirectoryMappingsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferUserHomeDirectoryMappings]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferUserHomeDirectoryMappings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferUserHomeDirectoryMappings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUserHomeDirectoryMappingsList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferUserHomeDirectoryMappingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferUserHomeDirectoryMappingsOutputReference",
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
            type_hints = typing.get_type_hints(TransferUserHomeDirectoryMappingsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entryInput")
    def entry_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entry")
    def entry(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entry"))

    @entry.setter
    def entry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUserHomeDirectoryMappingsOutputReference, "entry").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entry", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUserHomeDirectoryMappingsOutputReference, "target").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[TransferUserHomeDirectoryMappings, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[TransferUserHomeDirectoryMappings, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[TransferUserHomeDirectoryMappings, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUserHomeDirectoryMappingsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferUserPosixProfile",
    jsii_struct_bases=[],
    name_mapping={"gid": "gid", "uid": "uid", "secondary_gids": "secondaryGids"},
)
class TransferUserPosixProfile:
    def __init__(
        self,
        *,
        gid: jsii.Number,
        uid: jsii.Number,
        secondary_gids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#gid TransferUser#gid}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#uid TransferUser#uid}.
        :param secondary_gids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#secondary_gids TransferUser#secondary_gids}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferUserPosixProfile.__init__)
            check_type(argname="argument gid", value=gid, expected_type=type_hints["gid"])
            check_type(argname="argument uid", value=uid, expected_type=type_hints["uid"])
            check_type(argname="argument secondary_gids", value=secondary_gids, expected_type=type_hints["secondary_gids"])
        self._values: typing.Dict[str, typing.Any] = {
            "gid": gid,
            "uid": uid,
        }
        if secondary_gids is not None:
            self._values["secondary_gids"] = secondary_gids

    @builtins.property
    def gid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#gid TransferUser#gid}.'''
        result = self._values.get("gid")
        assert result is not None, "Required property 'gid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def uid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#uid TransferUser#uid}.'''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def secondary_gids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#secondary_gids TransferUser#secondary_gids}.'''
        result = self._values.get("secondary_gids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferUserPosixProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferUserPosixProfileOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferUserPosixProfileOutputReference",
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
            type_hints = typing.get_type_hints(TransferUserPosixProfileOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSecondaryGids")
    def reset_secondary_gids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondaryGids", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gidInput")
    def gid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGidsInput")
    def secondary_gids_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "secondaryGidsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uidInput")
    def uid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "uidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gid")
    def gid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gid"))

    @gid.setter
    def gid(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUserPosixProfileOutputReference, "gid").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGids")
    def secondary_gids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "secondaryGids"))

    @secondary_gids.setter
    def secondary_gids(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUserPosixProfileOutputReference, "secondary_gids").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryGids", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uid")
    def uid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "uid"))

    @uid.setter
    def uid(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUserPosixProfileOutputReference, "uid").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferUserPosixProfile]:
        return typing.cast(typing.Optional[TransferUserPosixProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[TransferUserPosixProfile]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferUserPosixProfileOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflow(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflow",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow aws_transfer_workflow}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        steps: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowSteps", typing.Dict[str, typing.Any]]]],
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        on_exception_steps: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowOnExceptionSteps", typing.Dict[str, typing.Any]]]]] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow aws_transfer_workflow} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param steps: steps block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#steps TransferWorkflow#steps}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#description TransferWorkflow#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#id TransferWorkflow#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param on_exception_steps: on_exception_steps block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#on_exception_steps TransferWorkflow#on_exception_steps}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags TransferWorkflow#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags_all TransferWorkflow#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflow.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TransferWorkflowConfig(
            steps=steps,
            description=description,
            id=id,
            on_exception_steps=on_exception_steps,
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

    @jsii.member(jsii_name="putOnExceptionSteps")
    def put_on_exception_steps(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowOnExceptionSteps", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflow.put_on_exception_steps)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOnExceptionSteps", [value]))

    @jsii.member(jsii_name="putSteps")
    def put_steps(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowSteps", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflow.put_steps)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSteps", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOnExceptionSteps")
    def reset_on_exception_steps(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnExceptionSteps", []))

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
    @jsii.member(jsii_name="onExceptionSteps")
    def on_exception_steps(self) -> "TransferWorkflowOnExceptionStepsList":
        return typing.cast("TransferWorkflowOnExceptionStepsList", jsii.get(self, "onExceptionSteps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="steps")
    def steps(self) -> "TransferWorkflowStepsList":
        return typing.cast("TransferWorkflowStepsList", jsii.get(self, "steps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onExceptionStepsInput")
    def on_exception_steps_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowOnExceptionSteps"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowOnExceptionSteps"]]], jsii.get(self, "onExceptionStepsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stepsInput")
    def steps_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowSteps"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowSteps"]]], jsii.get(self, "stepsInput"))

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
            type_hints = typing.get_type_hints(getattr(TransferWorkflow, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflow, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflow, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflow, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "steps": "steps",
        "description": "description",
        "id": "id",
        "on_exception_steps": "onExceptionSteps",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class TransferWorkflowConfig(cdktf.TerraformMetaArguments):
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
        steps: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowSteps", typing.Dict[str, typing.Any]]]],
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        on_exception_steps: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowOnExceptionSteps", typing.Dict[str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Transfer.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param steps: steps block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#steps TransferWorkflow#steps}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#description TransferWorkflow#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#id TransferWorkflow#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param on_exception_steps: on_exception_steps block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#on_exception_steps TransferWorkflow#on_exception_steps}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags TransferWorkflow#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags_all TransferWorkflow#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument on_exception_steps", value=on_exception_steps, expected_type=type_hints["on_exception_steps"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "steps": steps,
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
        if on_exception_steps is not None:
            self._values["on_exception_steps"] = on_exception_steps
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
    def steps(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowSteps"]]:
        '''steps block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#steps TransferWorkflow#steps}
        '''
        result = self._values.get("steps")
        assert result is not None, "Required property 'steps' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowSteps"]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#description TransferWorkflow#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#id TransferWorkflow#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_exception_steps(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowOnExceptionSteps"]]]:
        '''on_exception_steps block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#on_exception_steps TransferWorkflow#on_exception_steps}
        '''
        result = self._values.get("on_exception_steps")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowOnExceptionSteps"]]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags TransferWorkflow#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags_all TransferWorkflow#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionSteps",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "copy_step_details": "copyStepDetails",
        "custom_step_details": "customStepDetails",
        "delete_step_details": "deleteStepDetails",
        "tag_step_details": "tagStepDetails",
    },
)
class TransferWorkflowOnExceptionSteps:
    def __init__(
        self,
        *,
        type: builtins.str,
        copy_step_details: typing.Optional[typing.Union["TransferWorkflowOnExceptionStepsCopyStepDetails", typing.Dict[str, typing.Any]]] = None,
        custom_step_details: typing.Optional[typing.Union["TransferWorkflowOnExceptionStepsCustomStepDetails", typing.Dict[str, typing.Any]]] = None,
        delete_step_details: typing.Optional[typing.Union["TransferWorkflowOnExceptionStepsDeleteStepDetails", typing.Dict[str, typing.Any]]] = None,
        tag_step_details: typing.Optional[typing.Union["TransferWorkflowOnExceptionStepsTagStepDetails", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#type TransferWorkflow#type}.
        :param copy_step_details: copy_step_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#copy_step_details TransferWorkflow#copy_step_details}
        :param custom_step_details: custom_step_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#custom_step_details TransferWorkflow#custom_step_details}
        :param delete_step_details: delete_step_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#delete_step_details TransferWorkflow#delete_step_details}
        :param tag_step_details: tag_step_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tag_step_details TransferWorkflow#tag_step_details}
        '''
        if isinstance(copy_step_details, dict):
            copy_step_details = TransferWorkflowOnExceptionStepsCopyStepDetails(**copy_step_details)
        if isinstance(custom_step_details, dict):
            custom_step_details = TransferWorkflowOnExceptionStepsCustomStepDetails(**custom_step_details)
        if isinstance(delete_step_details, dict):
            delete_step_details = TransferWorkflowOnExceptionStepsDeleteStepDetails(**delete_step_details)
        if isinstance(tag_step_details, dict):
            tag_step_details = TransferWorkflowOnExceptionStepsTagStepDetails(**tag_step_details)
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionSteps.__init__)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument copy_step_details", value=copy_step_details, expected_type=type_hints["copy_step_details"])
            check_type(argname="argument custom_step_details", value=custom_step_details, expected_type=type_hints["custom_step_details"])
            check_type(argname="argument delete_step_details", value=delete_step_details, expected_type=type_hints["delete_step_details"])
            check_type(argname="argument tag_step_details", value=tag_step_details, expected_type=type_hints["tag_step_details"])
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if copy_step_details is not None:
            self._values["copy_step_details"] = copy_step_details
        if custom_step_details is not None:
            self._values["custom_step_details"] = custom_step_details
        if delete_step_details is not None:
            self._values["delete_step_details"] = delete_step_details
        if tag_step_details is not None:
            self._values["tag_step_details"] = tag_step_details

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#type TransferWorkflow#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def copy_step_details(
        self,
    ) -> typing.Optional["TransferWorkflowOnExceptionStepsCopyStepDetails"]:
        '''copy_step_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#copy_step_details TransferWorkflow#copy_step_details}
        '''
        result = self._values.get("copy_step_details")
        return typing.cast(typing.Optional["TransferWorkflowOnExceptionStepsCopyStepDetails"], result)

    @builtins.property
    def custom_step_details(
        self,
    ) -> typing.Optional["TransferWorkflowOnExceptionStepsCustomStepDetails"]:
        '''custom_step_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#custom_step_details TransferWorkflow#custom_step_details}
        '''
        result = self._values.get("custom_step_details")
        return typing.cast(typing.Optional["TransferWorkflowOnExceptionStepsCustomStepDetails"], result)

    @builtins.property
    def delete_step_details(
        self,
    ) -> typing.Optional["TransferWorkflowOnExceptionStepsDeleteStepDetails"]:
        '''delete_step_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#delete_step_details TransferWorkflow#delete_step_details}
        '''
        result = self._values.get("delete_step_details")
        return typing.cast(typing.Optional["TransferWorkflowOnExceptionStepsDeleteStepDetails"], result)

    @builtins.property
    def tag_step_details(
        self,
    ) -> typing.Optional["TransferWorkflowOnExceptionStepsTagStepDetails"]:
        '''tag_step_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tag_step_details TransferWorkflow#tag_step_details}
        '''
        result = self._values.get("tag_step_details")
        return typing.cast(typing.Optional["TransferWorkflowOnExceptionStepsTagStepDetails"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowOnExceptionSteps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsCopyStepDetails",
    jsii_struct_bases=[],
    name_mapping={
        "destination_file_location": "destinationFileLocation",
        "name": "name",
        "overwrite_existing": "overwriteExisting",
        "source_file_location": "sourceFileLocation",
    },
)
class TransferWorkflowOnExceptionStepsCopyStepDetails:
    def __init__(
        self,
        *,
        destination_file_location: typing.Optional[typing.Union["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation", typing.Dict[str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        overwrite_existing: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination_file_location: destination_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#destination_file_location TransferWorkflow#destination_file_location}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param overwrite_existing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#overwrite_existing TransferWorkflow#overwrite_existing}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        '''
        if isinstance(destination_file_location, dict):
            destination_file_location = TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation(**destination_file_location)
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsCopyStepDetails.__init__)
            check_type(argname="argument destination_file_location", value=destination_file_location, expected_type=type_hints["destination_file_location"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument overwrite_existing", value=overwrite_existing, expected_type=type_hints["overwrite_existing"])
            check_type(argname="argument source_file_location", value=source_file_location, expected_type=type_hints["source_file_location"])
        self._values: typing.Dict[str, typing.Any] = {}
        if destination_file_location is not None:
            self._values["destination_file_location"] = destination_file_location
        if name is not None:
            self._values["name"] = name
        if overwrite_existing is not None:
            self._values["overwrite_existing"] = overwrite_existing
        if source_file_location is not None:
            self._values["source_file_location"] = source_file_location

    @builtins.property
    def destination_file_location(
        self,
    ) -> typing.Optional["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation"]:
        '''destination_file_location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#destination_file_location TransferWorkflow#destination_file_location}
        '''
        result = self._values.get("destination_file_location")
        return typing.cast(typing.Optional["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def overwrite_existing(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#overwrite_existing TransferWorkflow#overwrite_existing}.'''
        result = self._values.get("overwrite_existing")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.'''
        result = self._values.get("source_file_location")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowOnExceptionStepsCopyStepDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation",
    jsii_struct_bases=[],
    name_mapping={
        "efs_file_location": "efsFileLocation",
        "s3_file_location": "s3FileLocation",
    },
)
class TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation:
    def __init__(
        self,
        *,
        efs_file_location: typing.Optional[typing.Union["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation", typing.Dict[str, typing.Any]]] = None,
        s3_file_location: typing.Optional[typing.Union["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param efs_file_location: efs_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#efs_file_location TransferWorkflow#efs_file_location}
        :param s3_file_location: s3_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#s3_file_location TransferWorkflow#s3_file_location}
        '''
        if isinstance(efs_file_location, dict):
            efs_file_location = TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation(**efs_file_location)
        if isinstance(s3_file_location, dict):
            s3_file_location = TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation(**s3_file_location)
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation.__init__)
            check_type(argname="argument efs_file_location", value=efs_file_location, expected_type=type_hints["efs_file_location"])
            check_type(argname="argument s3_file_location", value=s3_file_location, expected_type=type_hints["s3_file_location"])
        self._values: typing.Dict[str, typing.Any] = {}
        if efs_file_location is not None:
            self._values["efs_file_location"] = efs_file_location
        if s3_file_location is not None:
            self._values["s3_file_location"] = s3_file_location

    @builtins.property
    def efs_file_location(
        self,
    ) -> typing.Optional["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation"]:
        '''efs_file_location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#efs_file_location TransferWorkflow#efs_file_location}
        '''
        result = self._values.get("efs_file_location")
        return typing.cast(typing.Optional["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation"], result)

    @builtins.property
    def s3_file_location(
        self,
    ) -> typing.Optional["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation"]:
        '''s3_file_location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#s3_file_location TransferWorkflow#s3_file_location}
        '''
        result = self._values.get("s3_file_location")
        return typing.cast(typing.Optional["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation",
    jsii_struct_bases=[],
    name_mapping={"file_system_id": "fileSystemId", "path": "path"},
)
class TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation:
    def __init__(
        self,
        *,
        file_system_id: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#file_system_id TransferWorkflow#file_system_id}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#path TransferWorkflow#path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation.__init__)
            check_type(argname="argument file_system_id", value=file_system_id, expected_type=type_hints["file_system_id"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[str, typing.Any] = {}
        if file_system_id is not None:
            self._values["file_system_id"] = file_system_id
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def file_system_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#file_system_id TransferWorkflow#file_system_id}.'''
        result = self._values.get("file_system_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#path TransferWorkflow#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFileSystemId")
    def reset_file_system_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileSystemId", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference, "file_system_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileSystemId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference, "path").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEfsFileLocation")
    def put_efs_file_location(
        self,
        *,
        file_system_id: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#file_system_id TransferWorkflow#file_system_id}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#path TransferWorkflow#path}.
        '''
        value = TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation(
            file_system_id=file_system_id, path=path
        )

        return typing.cast(None, jsii.invoke(self, "putEfsFileLocation", [value]))

    @jsii.member(jsii_name="putS3FileLocation")
    def put_s3_file_location(
        self,
        *,
        bucket: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#bucket TransferWorkflow#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#key TransferWorkflow#key}.
        '''
        value = TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation(
            bucket=bucket, key=key
        )

        return typing.cast(None, jsii.invoke(self, "putS3FileLocation", [value]))

    @jsii.member(jsii_name="resetEfsFileLocation")
    def reset_efs_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEfsFileLocation", []))

    @jsii.member(jsii_name="resetS3FileLocation")
    def reset_s3_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3FileLocation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="efsFileLocation")
    def efs_file_location(
        self,
    ) -> TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference:
        return typing.cast(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference, jsii.get(self, "efsFileLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3FileLocation")
    def s3_file_location(
        self,
    ) -> "TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference":
        return typing.cast("TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference", jsii.get(self, "s3FileLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="efsFileLocationInput")
    def efs_file_location_input(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation], jsii.get(self, "efsFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3FileLocationInput")
    def s3_file_location_input(
        self,
    ) -> typing.Optional["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation"]:
        return typing.cast(typing.Optional["TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation"], jsii.get(self, "s3FileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "key": "key"},
)
class TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation:
    def __init__(
        self,
        *,
        bucket: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#bucket TransferWorkflow#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#key TransferWorkflow#key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation.__init__)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket is not None:
            self._values["bucket"] = bucket
        if key is not None:
            self._values["key"] = key

    @builtins.property
    def bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#bucket TransferWorkflow#bucket}.'''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#key TransferWorkflow#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBucket")
    def reset_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucket", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference, "bucket").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference, "key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflowOnExceptionStepsCopyStepDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsCopyStepDetailsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsCopyStepDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDestinationFileLocation")
    def put_destination_file_location(
        self,
        *,
        efs_file_location: typing.Optional[typing.Union[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation, typing.Dict[str, typing.Any]]] = None,
        s3_file_location: typing.Optional[typing.Union[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param efs_file_location: efs_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#efs_file_location TransferWorkflow#efs_file_location}
        :param s3_file_location: s3_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#s3_file_location TransferWorkflow#s3_file_location}
        '''
        value = TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation(
            efs_file_location=efs_file_location, s3_file_location=s3_file_location
        )

        return typing.cast(None, jsii.invoke(self, "putDestinationFileLocation", [value]))

    @jsii.member(jsii_name="resetDestinationFileLocation")
    def reset_destination_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationFileLocation", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOverwriteExisting")
    def reset_overwrite_existing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverwriteExisting", []))

    @jsii.member(jsii_name="resetSourceFileLocation")
    def reset_source_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFileLocation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationFileLocation")
    def destination_file_location(
        self,
    ) -> TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationOutputReference:
        return typing.cast(TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationOutputReference, jsii.get(self, "destinationFileLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationFileLocationInput")
    def destination_file_location_input(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation], jsii.get(self, "destinationFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overwriteExistingInput")
    def overwrite_existing_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "overwriteExistingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocationInput")
    def source_file_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overwriteExisting")
    def overwrite_existing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overwriteExisting"))

    @overwrite_existing.setter
    def overwrite_existing(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsOutputReference, "overwrite_existing").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "overwriteExisting", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocation")
    def source_file_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFileLocation"))

    @source_file_location.setter
    def source_file_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsOutputReference, "source_file_location").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFileLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCopyStepDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsCustomStepDetails",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "source_file_location": "sourceFileLocation",
        "target": "target",
        "timeout_seconds": "timeoutSeconds",
    },
)
class TransferWorkflowOnExceptionStepsCustomStepDetails:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        timeout_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#target TransferWorkflow#target}.
        :param timeout_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#timeout_seconds TransferWorkflow#timeout_seconds}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsCustomStepDetails.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument source_file_location", value=source_file_location, expected_type=type_hints["source_file_location"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument timeout_seconds", value=timeout_seconds, expected_type=type_hints["timeout_seconds"])
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if source_file_location is not None:
            self._values["source_file_location"] = source_file_location
        if target is not None:
            self._values["target"] = target
        if timeout_seconds is not None:
            self._values["timeout_seconds"] = timeout_seconds

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.'''
        result = self._values.get("source_file_location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#target TransferWorkflow#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#timeout_seconds TransferWorkflow#timeout_seconds}.'''
        result = self._values.get("timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowOnExceptionStepsCustomStepDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSourceFileLocation")
    def reset_source_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFileLocation", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @jsii.member(jsii_name="resetTimeoutSeconds")
    def reset_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutSeconds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocationInput")
    def source_file_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutSecondsInput")
    def timeout_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocation")
    def source_file_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFileLocation"))

    @source_file_location.setter
    def source_file_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference, "source_file_location").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFileLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference, "target").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutSeconds")
    def timeout_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutSeconds"))

    @timeout_seconds.setter
    def timeout_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference, "timeout_seconds").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeoutSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsCustomStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsCustomStepDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowOnExceptionStepsCustomStepDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsDeleteStepDetails",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "source_file_location": "sourceFileLocation"},
)
class TransferWorkflowOnExceptionStepsDeleteStepDetails:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsDeleteStepDetails.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument source_file_location", value=source_file_location, expected_type=type_hints["source_file_location"])
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if source_file_location is not None:
            self._values["source_file_location"] = source_file_location

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.'''
        result = self._values.get("source_file_location")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowOnExceptionStepsDeleteStepDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowOnExceptionStepsDeleteStepDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsDeleteStepDetailsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsDeleteStepDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSourceFileLocation")
    def reset_source_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFileLocation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocationInput")
    def source_file_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsDeleteStepDetailsOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocation")
    def source_file_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFileLocation"))

    @source_file_location.setter
    def source_file_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsDeleteStepDetailsOutputReference, "source_file_location").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFileLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsDeleteStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsDeleteStepDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowOnExceptionStepsDeleteStepDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsDeleteStepDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflowOnExceptionStepsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsList",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "TransferWorkflowOnExceptionStepsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("TransferWorkflowOnExceptionStepsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowOnExceptionSteps]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowOnExceptionSteps]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowOnExceptionSteps]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflowOnExceptionStepsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCopyStepDetails")
    def put_copy_step_details(
        self,
        *,
        destination_file_location: typing.Optional[typing.Union[TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation, typing.Dict[str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        overwrite_existing: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination_file_location: destination_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#destination_file_location TransferWorkflow#destination_file_location}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param overwrite_existing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#overwrite_existing TransferWorkflow#overwrite_existing}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        '''
        value = TransferWorkflowOnExceptionStepsCopyStepDetails(
            destination_file_location=destination_file_location,
            name=name,
            overwrite_existing=overwrite_existing,
            source_file_location=source_file_location,
        )

        return typing.cast(None, jsii.invoke(self, "putCopyStepDetails", [value]))

    @jsii.member(jsii_name="putCustomStepDetails")
    def put_custom_step_details(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        timeout_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#target TransferWorkflow#target}.
        :param timeout_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#timeout_seconds TransferWorkflow#timeout_seconds}.
        '''
        value = TransferWorkflowOnExceptionStepsCustomStepDetails(
            name=name,
            source_file_location=source_file_location,
            target=target,
            timeout_seconds=timeout_seconds,
        )

        return typing.cast(None, jsii.invoke(self, "putCustomStepDetails", [value]))

    @jsii.member(jsii_name="putDeleteStepDetails")
    def put_delete_step_details(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        '''
        value = TransferWorkflowOnExceptionStepsDeleteStepDetails(
            name=name, source_file_location=source_file_location
        )

        return typing.cast(None, jsii.invoke(self, "putDeleteStepDetails", [value]))

    @jsii.member(jsii_name="putTagStepDetails")
    def put_tag_step_details(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowOnExceptionStepsTagStepDetailsTags", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags TransferWorkflow#tags}
        '''
        value = TransferWorkflowOnExceptionStepsTagStepDetails(
            name=name, source_file_location=source_file_location, tags=tags
        )

        return typing.cast(None, jsii.invoke(self, "putTagStepDetails", [value]))

    @jsii.member(jsii_name="resetCopyStepDetails")
    def reset_copy_step_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyStepDetails", []))

    @jsii.member(jsii_name="resetCustomStepDetails")
    def reset_custom_step_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomStepDetails", []))

    @jsii.member(jsii_name="resetDeleteStepDetails")
    def reset_delete_step_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteStepDetails", []))

    @jsii.member(jsii_name="resetTagStepDetails")
    def reset_tag_step_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagStepDetails", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyStepDetails")
    def copy_step_details(
        self,
    ) -> TransferWorkflowOnExceptionStepsCopyStepDetailsOutputReference:
        return typing.cast(TransferWorkflowOnExceptionStepsCopyStepDetailsOutputReference, jsii.get(self, "copyStepDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customStepDetails")
    def custom_step_details(
        self,
    ) -> TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference:
        return typing.cast(TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference, jsii.get(self, "customStepDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteStepDetails")
    def delete_step_details(
        self,
    ) -> TransferWorkflowOnExceptionStepsDeleteStepDetailsOutputReference:
        return typing.cast(TransferWorkflowOnExceptionStepsDeleteStepDetailsOutputReference, jsii.get(self, "deleteStepDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagStepDetails")
    def tag_step_details(
        self,
    ) -> "TransferWorkflowOnExceptionStepsTagStepDetailsOutputReference":
        return typing.cast("TransferWorkflowOnExceptionStepsTagStepDetailsOutputReference", jsii.get(self, "tagStepDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyStepDetailsInput")
    def copy_step_details_input(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsCopyStepDetails], jsii.get(self, "copyStepDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customStepDetailsInput")
    def custom_step_details_input(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsCustomStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsCustomStepDetails], jsii.get(self, "customStepDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteStepDetailsInput")
    def delete_step_details_input(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsDeleteStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsDeleteStepDetails], jsii.get(self, "deleteStepDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagStepDetailsInput")
    def tag_step_details_input(
        self,
    ) -> typing.Optional["TransferWorkflowOnExceptionStepsTagStepDetails"]:
        return typing.cast(typing.Optional["TransferWorkflowOnExceptionStepsTagStepDetails"], jsii.get(self, "tagStepDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsOutputReference, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[TransferWorkflowOnExceptionSteps, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[TransferWorkflowOnExceptionSteps, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[TransferWorkflowOnExceptionSteps, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsTagStepDetails",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "source_file_location": "sourceFileLocation",
        "tags": "tags",
    },
)
class TransferWorkflowOnExceptionStepsTagStepDetails:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowOnExceptionStepsTagStepDetailsTags", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags TransferWorkflow#tags}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsTagStepDetails.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument source_file_location", value=source_file_location, expected_type=type_hints["source_file_location"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if source_file_location is not None:
            self._values["source_file_location"] = source_file_location
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.'''
        result = self._values.get("source_file_location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowOnExceptionStepsTagStepDetailsTags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags TransferWorkflow#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowOnExceptionStepsTagStepDetailsTags"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowOnExceptionStepsTagStepDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowOnExceptionStepsTagStepDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsTagStepDetailsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsTagStepDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowOnExceptionStepsTagStepDetailsTags", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsTagStepDetailsOutputReference.put_tags)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSourceFileLocation")
    def reset_source_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFileLocation", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> "TransferWorkflowOnExceptionStepsTagStepDetailsTagsList":
        return typing.cast("TransferWorkflowOnExceptionStepsTagStepDetailsTagsList", jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocationInput")
    def source_file_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowOnExceptionStepsTagStepDetailsTags"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowOnExceptionStepsTagStepDetailsTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsTagStepDetailsOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocation")
    def source_file_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFileLocation"))

    @source_file_location.setter
    def source_file_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsTagStepDetailsOutputReference, "source_file_location").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFileLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TransferWorkflowOnExceptionStepsTagStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowOnExceptionStepsTagStepDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowOnExceptionStepsTagStepDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsTagStepDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsTagStepDetailsTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class TransferWorkflowOnExceptionStepsTagStepDetailsTags:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#key TransferWorkflow#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#value TransferWorkflow#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsTagStepDetailsTags.__init__)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#key TransferWorkflow#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#value TransferWorkflow#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowOnExceptionStepsTagStepDetailsTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowOnExceptionStepsTagStepDetailsTagsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsTagStepDetailsTagsList",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsTagStepDetailsTagsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "TransferWorkflowOnExceptionStepsTagStepDetailsTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsTagStepDetailsTagsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("TransferWorkflowOnExceptionStepsTagStepDetailsTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsTagStepDetailsTagsList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsTagStepDetailsTagsList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsTagStepDetailsTagsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowOnExceptionStepsTagStepDetailsTags]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowOnExceptionStepsTagStepDetailsTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowOnExceptionStepsTagStepDetailsTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsTagStepDetailsTagsList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflowOnExceptionStepsTagStepDetailsTagsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowOnExceptionStepsTagStepDetailsTagsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowOnExceptionStepsTagStepDetailsTagsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsTagStepDetailsTagsOutputReference, "key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsTagStepDetailsTagsOutputReference, "value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[TransferWorkflowOnExceptionStepsTagStepDetailsTags, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[TransferWorkflowOnExceptionStepsTagStepDetailsTags, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[TransferWorkflowOnExceptionStepsTagStepDetailsTags, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowOnExceptionStepsTagStepDetailsTagsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowSteps",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "copy_step_details": "copyStepDetails",
        "custom_step_details": "customStepDetails",
        "delete_step_details": "deleteStepDetails",
        "tag_step_details": "tagStepDetails",
    },
)
class TransferWorkflowSteps:
    def __init__(
        self,
        *,
        type: builtins.str,
        copy_step_details: typing.Optional[typing.Union["TransferWorkflowStepsCopyStepDetails", typing.Dict[str, typing.Any]]] = None,
        custom_step_details: typing.Optional[typing.Union["TransferWorkflowStepsCustomStepDetails", typing.Dict[str, typing.Any]]] = None,
        delete_step_details: typing.Optional[typing.Union["TransferWorkflowStepsDeleteStepDetails", typing.Dict[str, typing.Any]]] = None,
        tag_step_details: typing.Optional[typing.Union["TransferWorkflowStepsTagStepDetails", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#type TransferWorkflow#type}.
        :param copy_step_details: copy_step_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#copy_step_details TransferWorkflow#copy_step_details}
        :param custom_step_details: custom_step_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#custom_step_details TransferWorkflow#custom_step_details}
        :param delete_step_details: delete_step_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#delete_step_details TransferWorkflow#delete_step_details}
        :param tag_step_details: tag_step_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tag_step_details TransferWorkflow#tag_step_details}
        '''
        if isinstance(copy_step_details, dict):
            copy_step_details = TransferWorkflowStepsCopyStepDetails(**copy_step_details)
        if isinstance(custom_step_details, dict):
            custom_step_details = TransferWorkflowStepsCustomStepDetails(**custom_step_details)
        if isinstance(delete_step_details, dict):
            delete_step_details = TransferWorkflowStepsDeleteStepDetails(**delete_step_details)
        if isinstance(tag_step_details, dict):
            tag_step_details = TransferWorkflowStepsTagStepDetails(**tag_step_details)
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowSteps.__init__)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument copy_step_details", value=copy_step_details, expected_type=type_hints["copy_step_details"])
            check_type(argname="argument custom_step_details", value=custom_step_details, expected_type=type_hints["custom_step_details"])
            check_type(argname="argument delete_step_details", value=delete_step_details, expected_type=type_hints["delete_step_details"])
            check_type(argname="argument tag_step_details", value=tag_step_details, expected_type=type_hints["tag_step_details"])
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if copy_step_details is not None:
            self._values["copy_step_details"] = copy_step_details
        if custom_step_details is not None:
            self._values["custom_step_details"] = custom_step_details
        if delete_step_details is not None:
            self._values["delete_step_details"] = delete_step_details
        if tag_step_details is not None:
            self._values["tag_step_details"] = tag_step_details

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#type TransferWorkflow#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def copy_step_details(
        self,
    ) -> typing.Optional["TransferWorkflowStepsCopyStepDetails"]:
        '''copy_step_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#copy_step_details TransferWorkflow#copy_step_details}
        '''
        result = self._values.get("copy_step_details")
        return typing.cast(typing.Optional["TransferWorkflowStepsCopyStepDetails"], result)

    @builtins.property
    def custom_step_details(
        self,
    ) -> typing.Optional["TransferWorkflowStepsCustomStepDetails"]:
        '''custom_step_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#custom_step_details TransferWorkflow#custom_step_details}
        '''
        result = self._values.get("custom_step_details")
        return typing.cast(typing.Optional["TransferWorkflowStepsCustomStepDetails"], result)

    @builtins.property
    def delete_step_details(
        self,
    ) -> typing.Optional["TransferWorkflowStepsDeleteStepDetails"]:
        '''delete_step_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#delete_step_details TransferWorkflow#delete_step_details}
        '''
        result = self._values.get("delete_step_details")
        return typing.cast(typing.Optional["TransferWorkflowStepsDeleteStepDetails"], result)

    @builtins.property
    def tag_step_details(
        self,
    ) -> typing.Optional["TransferWorkflowStepsTagStepDetails"]:
        '''tag_step_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tag_step_details TransferWorkflow#tag_step_details}
        '''
        result = self._values.get("tag_step_details")
        return typing.cast(typing.Optional["TransferWorkflowStepsTagStepDetails"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowSteps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsCopyStepDetails",
    jsii_struct_bases=[],
    name_mapping={
        "destination_file_location": "destinationFileLocation",
        "name": "name",
        "overwrite_existing": "overwriteExisting",
        "source_file_location": "sourceFileLocation",
    },
)
class TransferWorkflowStepsCopyStepDetails:
    def __init__(
        self,
        *,
        destination_file_location: typing.Optional[typing.Union["TransferWorkflowStepsCopyStepDetailsDestinationFileLocation", typing.Dict[str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        overwrite_existing: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination_file_location: destination_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#destination_file_location TransferWorkflow#destination_file_location}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param overwrite_existing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#overwrite_existing TransferWorkflow#overwrite_existing}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        '''
        if isinstance(destination_file_location, dict):
            destination_file_location = TransferWorkflowStepsCopyStepDetailsDestinationFileLocation(**destination_file_location)
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsCopyStepDetails.__init__)
            check_type(argname="argument destination_file_location", value=destination_file_location, expected_type=type_hints["destination_file_location"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument overwrite_existing", value=overwrite_existing, expected_type=type_hints["overwrite_existing"])
            check_type(argname="argument source_file_location", value=source_file_location, expected_type=type_hints["source_file_location"])
        self._values: typing.Dict[str, typing.Any] = {}
        if destination_file_location is not None:
            self._values["destination_file_location"] = destination_file_location
        if name is not None:
            self._values["name"] = name
        if overwrite_existing is not None:
            self._values["overwrite_existing"] = overwrite_existing
        if source_file_location is not None:
            self._values["source_file_location"] = source_file_location

    @builtins.property
    def destination_file_location(
        self,
    ) -> typing.Optional["TransferWorkflowStepsCopyStepDetailsDestinationFileLocation"]:
        '''destination_file_location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#destination_file_location TransferWorkflow#destination_file_location}
        '''
        result = self._values.get("destination_file_location")
        return typing.cast(typing.Optional["TransferWorkflowStepsCopyStepDetailsDestinationFileLocation"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def overwrite_existing(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#overwrite_existing TransferWorkflow#overwrite_existing}.'''
        result = self._values.get("overwrite_existing")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.'''
        result = self._values.get("source_file_location")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowStepsCopyStepDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsCopyStepDetailsDestinationFileLocation",
    jsii_struct_bases=[],
    name_mapping={
        "efs_file_location": "efsFileLocation",
        "s3_file_location": "s3FileLocation",
    },
)
class TransferWorkflowStepsCopyStepDetailsDestinationFileLocation:
    def __init__(
        self,
        *,
        efs_file_location: typing.Optional[typing.Union["TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation", typing.Dict[str, typing.Any]]] = None,
        s3_file_location: typing.Optional[typing.Union["TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param efs_file_location: efs_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#efs_file_location TransferWorkflow#efs_file_location}
        :param s3_file_location: s3_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#s3_file_location TransferWorkflow#s3_file_location}
        '''
        if isinstance(efs_file_location, dict):
            efs_file_location = TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation(**efs_file_location)
        if isinstance(s3_file_location, dict):
            s3_file_location = TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation(**s3_file_location)
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsCopyStepDetailsDestinationFileLocation.__init__)
            check_type(argname="argument efs_file_location", value=efs_file_location, expected_type=type_hints["efs_file_location"])
            check_type(argname="argument s3_file_location", value=s3_file_location, expected_type=type_hints["s3_file_location"])
        self._values: typing.Dict[str, typing.Any] = {}
        if efs_file_location is not None:
            self._values["efs_file_location"] = efs_file_location
        if s3_file_location is not None:
            self._values["s3_file_location"] = s3_file_location

    @builtins.property
    def efs_file_location(
        self,
    ) -> typing.Optional["TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation"]:
        '''efs_file_location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#efs_file_location TransferWorkflow#efs_file_location}
        '''
        result = self._values.get("efs_file_location")
        return typing.cast(typing.Optional["TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation"], result)

    @builtins.property
    def s3_file_location(
        self,
    ) -> typing.Optional["TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation"]:
        '''s3_file_location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#s3_file_location TransferWorkflow#s3_file_location}
        '''
        result = self._values.get("s3_file_location")
        return typing.cast(typing.Optional["TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowStepsCopyStepDetailsDestinationFileLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation",
    jsii_struct_bases=[],
    name_mapping={"file_system_id": "fileSystemId", "path": "path"},
)
class TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation:
    def __init__(
        self,
        *,
        file_system_id: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#file_system_id TransferWorkflow#file_system_id}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#path TransferWorkflow#path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation.__init__)
            check_type(argname="argument file_system_id", value=file_system_id, expected_type=type_hints["file_system_id"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[str, typing.Any] = {}
        if file_system_id is not None:
            self._values["file_system_id"] = file_system_id
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def file_system_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#file_system_id TransferWorkflow#file_system_id}.'''
        result = self._values.get("file_system_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#path TransferWorkflow#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFileSystemId")
    def reset_file_system_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileSystemId", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference, "file_system_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileSystemId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference, "path").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation]:
        return typing.cast(typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflowStepsCopyStepDetailsDestinationFileLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsCopyStepDetailsDestinationFileLocationOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEfsFileLocation")
    def put_efs_file_location(
        self,
        *,
        file_system_id: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#file_system_id TransferWorkflow#file_system_id}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#path TransferWorkflow#path}.
        '''
        value = TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation(
            file_system_id=file_system_id, path=path
        )

        return typing.cast(None, jsii.invoke(self, "putEfsFileLocation", [value]))

    @jsii.member(jsii_name="putS3FileLocation")
    def put_s3_file_location(
        self,
        *,
        bucket: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#bucket TransferWorkflow#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#key TransferWorkflow#key}.
        '''
        value = TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation(
            bucket=bucket, key=key
        )

        return typing.cast(None, jsii.invoke(self, "putS3FileLocation", [value]))

    @jsii.member(jsii_name="resetEfsFileLocation")
    def reset_efs_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEfsFileLocation", []))

    @jsii.member(jsii_name="resetS3FileLocation")
    def reset_s3_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3FileLocation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="efsFileLocation")
    def efs_file_location(
        self,
    ) -> TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference:
        return typing.cast(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference, jsii.get(self, "efsFileLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3FileLocation")
    def s3_file_location(
        self,
    ) -> "TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference":
        return typing.cast("TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference", jsii.get(self, "s3FileLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="efsFileLocationInput")
    def efs_file_location_input(
        self,
    ) -> typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation]:
        return typing.cast(typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation], jsii.get(self, "efsFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3FileLocationInput")
    def s3_file_location_input(
        self,
    ) -> typing.Optional["TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation"]:
        return typing.cast(typing.Optional["TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation"], jsii.get(self, "s3FileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocation]:
        return typing.cast(typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "key": "key"},
)
class TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation:
    def __init__(
        self,
        *,
        bucket: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#bucket TransferWorkflow#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#key TransferWorkflow#key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation.__init__)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket is not None:
            self._values["bucket"] = bucket
        if key is not None:
            self._values["key"] = key

    @builtins.property
    def bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#bucket TransferWorkflow#bucket}.'''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#key TransferWorkflow#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBucket")
    def reset_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucket", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference, "bucket").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference, "key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation]:
        return typing.cast(typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflowStepsCopyStepDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsCopyStepDetailsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsCopyStepDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDestinationFileLocation")
    def put_destination_file_location(
        self,
        *,
        efs_file_location: typing.Optional[typing.Union[TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation, typing.Dict[str, typing.Any]]] = None,
        s3_file_location: typing.Optional[typing.Union[TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param efs_file_location: efs_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#efs_file_location TransferWorkflow#efs_file_location}
        :param s3_file_location: s3_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#s3_file_location TransferWorkflow#s3_file_location}
        '''
        value = TransferWorkflowStepsCopyStepDetailsDestinationFileLocation(
            efs_file_location=efs_file_location, s3_file_location=s3_file_location
        )

        return typing.cast(None, jsii.invoke(self, "putDestinationFileLocation", [value]))

    @jsii.member(jsii_name="resetDestinationFileLocation")
    def reset_destination_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationFileLocation", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOverwriteExisting")
    def reset_overwrite_existing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverwriteExisting", []))

    @jsii.member(jsii_name="resetSourceFileLocation")
    def reset_source_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFileLocation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationFileLocation")
    def destination_file_location(
        self,
    ) -> TransferWorkflowStepsCopyStepDetailsDestinationFileLocationOutputReference:
        return typing.cast(TransferWorkflowStepsCopyStepDetailsDestinationFileLocationOutputReference, jsii.get(self, "destinationFileLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationFileLocationInput")
    def destination_file_location_input(
        self,
    ) -> typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocation]:
        return typing.cast(typing.Optional[TransferWorkflowStepsCopyStepDetailsDestinationFileLocation], jsii.get(self, "destinationFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overwriteExistingInput")
    def overwrite_existing_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "overwriteExistingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocationInput")
    def source_file_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overwriteExisting")
    def overwrite_existing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overwriteExisting"))

    @overwrite_existing.setter
    def overwrite_existing(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsOutputReference, "overwrite_existing").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "overwriteExisting", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocation")
    def source_file_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFileLocation"))

    @source_file_location.setter
    def source_file_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsOutputReference, "source_file_location").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFileLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferWorkflowStepsCopyStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowStepsCopyStepDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowStepsCopyStepDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCopyStepDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsCustomStepDetails",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "source_file_location": "sourceFileLocation",
        "target": "target",
        "timeout_seconds": "timeoutSeconds",
    },
)
class TransferWorkflowStepsCustomStepDetails:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        timeout_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#target TransferWorkflow#target}.
        :param timeout_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#timeout_seconds TransferWorkflow#timeout_seconds}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsCustomStepDetails.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument source_file_location", value=source_file_location, expected_type=type_hints["source_file_location"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument timeout_seconds", value=timeout_seconds, expected_type=type_hints["timeout_seconds"])
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if source_file_location is not None:
            self._values["source_file_location"] = source_file_location
        if target is not None:
            self._values["target"] = target
        if timeout_seconds is not None:
            self._values["timeout_seconds"] = timeout_seconds

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.'''
        result = self._values.get("source_file_location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#target TransferWorkflow#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#timeout_seconds TransferWorkflow#timeout_seconds}.'''
        result = self._values.get("timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowStepsCustomStepDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowStepsCustomStepDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsCustomStepDetailsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsCustomStepDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSourceFileLocation")
    def reset_source_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFileLocation", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @jsii.member(jsii_name="resetTimeoutSeconds")
    def reset_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutSeconds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocationInput")
    def source_file_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutSecondsInput")
    def timeout_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCustomStepDetailsOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocation")
    def source_file_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFileLocation"))

    @source_file_location.setter
    def source_file_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCustomStepDetailsOutputReference, "source_file_location").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFileLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCustomStepDetailsOutputReference, "target").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutSeconds")
    def timeout_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutSeconds"))

    @timeout_seconds.setter
    def timeout_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCustomStepDetailsOutputReference, "timeout_seconds").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeoutSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferWorkflowStepsCustomStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowStepsCustomStepDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowStepsCustomStepDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsCustomStepDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsDeleteStepDetails",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "source_file_location": "sourceFileLocation"},
)
class TransferWorkflowStepsDeleteStepDetails:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsDeleteStepDetails.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument source_file_location", value=source_file_location, expected_type=type_hints["source_file_location"])
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if source_file_location is not None:
            self._values["source_file_location"] = source_file_location

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.'''
        result = self._values.get("source_file_location")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowStepsDeleteStepDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowStepsDeleteStepDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsDeleteStepDetailsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsDeleteStepDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSourceFileLocation")
    def reset_source_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFileLocation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocationInput")
    def source_file_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsDeleteStepDetailsOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocation")
    def source_file_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFileLocation"))

    @source_file_location.setter
    def source_file_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsDeleteStepDetailsOutputReference, "source_file_location").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFileLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferWorkflowStepsDeleteStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowStepsDeleteStepDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowStepsDeleteStepDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsDeleteStepDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflowStepsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsList",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "TransferWorkflowStepsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("TransferWorkflowStepsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowSteps]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowSteps]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowSteps]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflowStepsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCopyStepDetails")
    def put_copy_step_details(
        self,
        *,
        destination_file_location: typing.Optional[typing.Union[TransferWorkflowStepsCopyStepDetailsDestinationFileLocation, typing.Dict[str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        overwrite_existing: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination_file_location: destination_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#destination_file_location TransferWorkflow#destination_file_location}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param overwrite_existing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#overwrite_existing TransferWorkflow#overwrite_existing}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        '''
        value = TransferWorkflowStepsCopyStepDetails(
            destination_file_location=destination_file_location,
            name=name,
            overwrite_existing=overwrite_existing,
            source_file_location=source_file_location,
        )

        return typing.cast(None, jsii.invoke(self, "putCopyStepDetails", [value]))

    @jsii.member(jsii_name="putCustomStepDetails")
    def put_custom_step_details(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        timeout_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#target TransferWorkflow#target}.
        :param timeout_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#timeout_seconds TransferWorkflow#timeout_seconds}.
        '''
        value = TransferWorkflowStepsCustomStepDetails(
            name=name,
            source_file_location=source_file_location,
            target=target,
            timeout_seconds=timeout_seconds,
        )

        return typing.cast(None, jsii.invoke(self, "putCustomStepDetails", [value]))

    @jsii.member(jsii_name="putDeleteStepDetails")
    def put_delete_step_details(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        '''
        value = TransferWorkflowStepsDeleteStepDetails(
            name=name, source_file_location=source_file_location
        )

        return typing.cast(None, jsii.invoke(self, "putDeleteStepDetails", [value]))

    @jsii.member(jsii_name="putTagStepDetails")
    def put_tag_step_details(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowStepsTagStepDetailsTags", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags TransferWorkflow#tags}
        '''
        value = TransferWorkflowStepsTagStepDetails(
            name=name, source_file_location=source_file_location, tags=tags
        )

        return typing.cast(None, jsii.invoke(self, "putTagStepDetails", [value]))

    @jsii.member(jsii_name="resetCopyStepDetails")
    def reset_copy_step_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyStepDetails", []))

    @jsii.member(jsii_name="resetCustomStepDetails")
    def reset_custom_step_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomStepDetails", []))

    @jsii.member(jsii_name="resetDeleteStepDetails")
    def reset_delete_step_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteStepDetails", []))

    @jsii.member(jsii_name="resetTagStepDetails")
    def reset_tag_step_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagStepDetails", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyStepDetails")
    def copy_step_details(self) -> TransferWorkflowStepsCopyStepDetailsOutputReference:
        return typing.cast(TransferWorkflowStepsCopyStepDetailsOutputReference, jsii.get(self, "copyStepDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customStepDetails")
    def custom_step_details(
        self,
    ) -> TransferWorkflowStepsCustomStepDetailsOutputReference:
        return typing.cast(TransferWorkflowStepsCustomStepDetailsOutputReference, jsii.get(self, "customStepDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteStepDetails")
    def delete_step_details(
        self,
    ) -> TransferWorkflowStepsDeleteStepDetailsOutputReference:
        return typing.cast(TransferWorkflowStepsDeleteStepDetailsOutputReference, jsii.get(self, "deleteStepDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagStepDetails")
    def tag_step_details(self) -> "TransferWorkflowStepsTagStepDetailsOutputReference":
        return typing.cast("TransferWorkflowStepsTagStepDetailsOutputReference", jsii.get(self, "tagStepDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyStepDetailsInput")
    def copy_step_details_input(
        self,
    ) -> typing.Optional[TransferWorkflowStepsCopyStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowStepsCopyStepDetails], jsii.get(self, "copyStepDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customStepDetailsInput")
    def custom_step_details_input(
        self,
    ) -> typing.Optional[TransferWorkflowStepsCustomStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowStepsCustomStepDetails], jsii.get(self, "customStepDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteStepDetailsInput")
    def delete_step_details_input(
        self,
    ) -> typing.Optional[TransferWorkflowStepsDeleteStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowStepsDeleteStepDetails], jsii.get(self, "deleteStepDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagStepDetailsInput")
    def tag_step_details_input(
        self,
    ) -> typing.Optional["TransferWorkflowStepsTagStepDetails"]:
        return typing.cast(typing.Optional["TransferWorkflowStepsTagStepDetails"], jsii.get(self, "tagStepDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsOutputReference, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[TransferWorkflowSteps, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[TransferWorkflowSteps, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[TransferWorkflowSteps, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsTagStepDetails",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "source_file_location": "sourceFileLocation",
        "tags": "tags",
    },
)
class TransferWorkflowStepsTagStepDetails:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        source_file_location: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowStepsTagStepDetailsTags", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.
        :param source_file_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags TransferWorkflow#tags}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsTagStepDetails.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument source_file_location", value=source_file_location, expected_type=type_hints["source_file_location"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if source_file_location is not None:
            self._values["source_file_location"] = source_file_location
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#name TransferWorkflow#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#source_file_location TransferWorkflow#source_file_location}.'''
        result = self._values.get("source_file_location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowStepsTagStepDetailsTags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#tags TransferWorkflow#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowStepsTagStepDetailsTags"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowStepsTagStepDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowStepsTagStepDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsTagStepDetailsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsTagStepDetailsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["TransferWorkflowStepsTagStepDetailsTags", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsTagStepDetailsOutputReference.put_tags)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSourceFileLocation")
    def reset_source_file_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFileLocation", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> "TransferWorkflowStepsTagStepDetailsTagsList":
        return typing.cast("TransferWorkflowStepsTagStepDetailsTagsList", jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocationInput")
    def source_file_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowStepsTagStepDetailsTags"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["TransferWorkflowStepsTagStepDetailsTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsTagStepDetailsOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileLocation")
    def source_file_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFileLocation"))

    @source_file_location.setter
    def source_file_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsTagStepDetailsOutputReference, "source_file_location").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFileLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferWorkflowStepsTagStepDetails]:
        return typing.cast(typing.Optional[TransferWorkflowStepsTagStepDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferWorkflowStepsTagStepDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsTagStepDetailsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsTagStepDetailsTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class TransferWorkflowStepsTagStepDetailsTags:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#key TransferWorkflow#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#value TransferWorkflow#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsTagStepDetailsTags.__init__)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#key TransferWorkflow#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_workflow#value TransferWorkflow#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferWorkflowStepsTagStepDetailsTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferWorkflowStepsTagStepDetailsTagsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsTagStepDetailsTagsList",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsTagStepDetailsTagsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "TransferWorkflowStepsTagStepDetailsTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TransferWorkflowStepsTagStepDetailsTagsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("TransferWorkflowStepsTagStepDetailsTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsTagStepDetailsTagsList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsTagStepDetailsTagsList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsTagStepDetailsTagsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowStepsTagStepDetailsTags]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowStepsTagStepDetailsTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[TransferWorkflowStepsTagStepDetailsTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsTagStepDetailsTagsList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class TransferWorkflowStepsTagStepDetailsTagsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferWorkflowStepsTagStepDetailsTagsOutputReference",
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
            type_hints = typing.get_type_hints(TransferWorkflowStepsTagStepDetailsTagsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsTagStepDetailsTagsOutputReference, "key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsTagStepDetailsTagsOutputReference, "value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[TransferWorkflowStepsTagStepDetailsTags, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[TransferWorkflowStepsTagStepDetailsTags, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[TransferWorkflowStepsTagStepDetailsTags, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(TransferWorkflowStepsTagStepDetailsTagsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsTransferServer",
    "DataAwsTransferServerConfig",
    "TransferAccess",
    "TransferAccessConfig",
    "TransferAccessHomeDirectoryMappings",
    "TransferAccessHomeDirectoryMappingsList",
    "TransferAccessHomeDirectoryMappingsOutputReference",
    "TransferAccessPosixProfile",
    "TransferAccessPosixProfileOutputReference",
    "TransferServer",
    "TransferServerConfig",
    "TransferServerEndpointDetails",
    "TransferServerEndpointDetailsOutputReference",
    "TransferServerWorkflowDetails",
    "TransferServerWorkflowDetailsOnUpload",
    "TransferServerWorkflowDetailsOnUploadOutputReference",
    "TransferServerWorkflowDetailsOutputReference",
    "TransferSshKey",
    "TransferSshKeyConfig",
    "TransferUser",
    "TransferUserConfig",
    "TransferUserHomeDirectoryMappings",
    "TransferUserHomeDirectoryMappingsList",
    "TransferUserHomeDirectoryMappingsOutputReference",
    "TransferUserPosixProfile",
    "TransferUserPosixProfileOutputReference",
    "TransferWorkflow",
    "TransferWorkflowConfig",
    "TransferWorkflowOnExceptionSteps",
    "TransferWorkflowOnExceptionStepsCopyStepDetails",
    "TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocation",
    "TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocation",
    "TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference",
    "TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationOutputReference",
    "TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocation",
    "TransferWorkflowOnExceptionStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference",
    "TransferWorkflowOnExceptionStepsCopyStepDetailsOutputReference",
    "TransferWorkflowOnExceptionStepsCustomStepDetails",
    "TransferWorkflowOnExceptionStepsCustomStepDetailsOutputReference",
    "TransferWorkflowOnExceptionStepsDeleteStepDetails",
    "TransferWorkflowOnExceptionStepsDeleteStepDetailsOutputReference",
    "TransferWorkflowOnExceptionStepsList",
    "TransferWorkflowOnExceptionStepsOutputReference",
    "TransferWorkflowOnExceptionStepsTagStepDetails",
    "TransferWorkflowOnExceptionStepsTagStepDetailsOutputReference",
    "TransferWorkflowOnExceptionStepsTagStepDetailsTags",
    "TransferWorkflowOnExceptionStepsTagStepDetailsTagsList",
    "TransferWorkflowOnExceptionStepsTagStepDetailsTagsOutputReference",
    "TransferWorkflowSteps",
    "TransferWorkflowStepsCopyStepDetails",
    "TransferWorkflowStepsCopyStepDetailsDestinationFileLocation",
    "TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocation",
    "TransferWorkflowStepsCopyStepDetailsDestinationFileLocationEfsFileLocationOutputReference",
    "TransferWorkflowStepsCopyStepDetailsDestinationFileLocationOutputReference",
    "TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocation",
    "TransferWorkflowStepsCopyStepDetailsDestinationFileLocationS3FileLocationOutputReference",
    "TransferWorkflowStepsCopyStepDetailsOutputReference",
    "TransferWorkflowStepsCustomStepDetails",
    "TransferWorkflowStepsCustomStepDetailsOutputReference",
    "TransferWorkflowStepsDeleteStepDetails",
    "TransferWorkflowStepsDeleteStepDetailsOutputReference",
    "TransferWorkflowStepsList",
    "TransferWorkflowStepsOutputReference",
    "TransferWorkflowStepsTagStepDetails",
    "TransferWorkflowStepsTagStepDetailsOutputReference",
    "TransferWorkflowStepsTagStepDetailsTags",
    "TransferWorkflowStepsTagStepDetailsTagsList",
    "TransferWorkflowStepsTagStepDetailsTagsOutputReference",
]

publication.publish()
