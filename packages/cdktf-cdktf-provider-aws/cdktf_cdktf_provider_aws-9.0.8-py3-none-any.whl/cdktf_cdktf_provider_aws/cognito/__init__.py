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


class CognitoIdentityPool(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPool",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool aws_cognito_identity_pool}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        identity_pool_name: builtins.str,
        allow_classic_flow: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        allow_unauthenticated_identities: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cognito_identity_providers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoIdentityPoolCognitoIdentityProviders", typing.Dict[str, typing.Any]]]]] = None,
        developer_provider_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        openid_connect_provider_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        saml_provider_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        supported_login_providers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool aws_cognito_identity_pool} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identity_pool_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#identity_pool_name CognitoIdentityPool#identity_pool_name}.
        :param allow_classic_flow: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_classic_flow CognitoIdentityPool#allow_classic_flow}.
        :param allow_unauthenticated_identities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_unauthenticated_identities CognitoIdentityPool#allow_unauthenticated_identities}.
        :param cognito_identity_providers: cognito_identity_providers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#cognito_identity_providers CognitoIdentityPool#cognito_identity_providers}
        :param developer_provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#developer_provider_name CognitoIdentityPool#developer_provider_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#id CognitoIdentityPool#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param openid_connect_provider_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#openid_connect_provider_arns CognitoIdentityPool#openid_connect_provider_arns}.
        :param saml_provider_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#saml_provider_arns CognitoIdentityPool#saml_provider_arns}.
        :param supported_login_providers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#supported_login_providers CognitoIdentityPool#supported_login_providers}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags CognitoIdentityPool#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags_all CognitoIdentityPool#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPool.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoIdentityPoolConfig(
            identity_pool_name=identity_pool_name,
            allow_classic_flow=allow_classic_flow,
            allow_unauthenticated_identities=allow_unauthenticated_identities,
            cognito_identity_providers=cognito_identity_providers,
            developer_provider_name=developer_provider_name,
            id=id,
            openid_connect_provider_arns=openid_connect_provider_arns,
            saml_provider_arns=saml_provider_arns,
            supported_login_providers=supported_login_providers,
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

    @jsii.member(jsii_name="putCognitoIdentityProviders")
    def put_cognito_identity_providers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoIdentityPoolCognitoIdentityProviders", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPool.put_cognito_identity_providers)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCognitoIdentityProviders", [value]))

    @jsii.member(jsii_name="resetAllowClassicFlow")
    def reset_allow_classic_flow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowClassicFlow", []))

    @jsii.member(jsii_name="resetAllowUnauthenticatedIdentities")
    def reset_allow_unauthenticated_identities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowUnauthenticatedIdentities", []))

    @jsii.member(jsii_name="resetCognitoIdentityProviders")
    def reset_cognito_identity_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCognitoIdentityProviders", []))

    @jsii.member(jsii_name="resetDeveloperProviderName")
    def reset_developer_provider_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeveloperProviderName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOpenidConnectProviderArns")
    def reset_openid_connect_provider_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenidConnectProviderArns", []))

    @jsii.member(jsii_name="resetSamlProviderArns")
    def reset_saml_provider_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamlProviderArns", []))

    @jsii.member(jsii_name="resetSupportedLoginProviders")
    def reset_supported_login_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportedLoginProviders", []))

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
    @jsii.member(jsii_name="cognitoIdentityProviders")
    def cognito_identity_providers(
        self,
    ) -> "CognitoIdentityPoolCognitoIdentityProvidersList":
        return typing.cast("CognitoIdentityPoolCognitoIdentityProvidersList", jsii.get(self, "cognitoIdentityProviders"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowClassicFlowInput")
    def allow_classic_flow_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowClassicFlowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowUnauthenticatedIdentitiesInput")
    def allow_unauthenticated_identities_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowUnauthenticatedIdentitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cognitoIdentityProvidersInput")
    def cognito_identity_providers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoIdentityPoolCognitoIdentityProviders"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoIdentityPoolCognitoIdentityProviders"]]], jsii.get(self, "cognitoIdentityProvidersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="developerProviderNameInput")
    def developer_provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "developerProviderNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolNameInput")
    def identity_pool_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityPoolNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openidConnectProviderArnsInput")
    def openid_connect_provider_arns_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "openidConnectProviderArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samlProviderArnsInput")
    def saml_provider_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "samlProviderArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedLoginProvidersInput")
    def supported_login_providers_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "supportedLoginProvidersInput"))

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
    @jsii.member(jsii_name="allowClassicFlow")
    def allow_classic_flow(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowClassicFlow"))

    @allow_classic_flow.setter
    def allow_classic_flow(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPool, "allow_classic_flow").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowClassicFlow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowUnauthenticatedIdentities")
    def allow_unauthenticated_identities(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowUnauthenticatedIdentities"))

    @allow_unauthenticated_identities.setter
    def allow_unauthenticated_identities(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPool, "allow_unauthenticated_identities").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowUnauthenticatedIdentities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="developerProviderName")
    def developer_provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "developerProviderName"))

    @developer_provider_name.setter
    def developer_provider_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPool, "developer_provider_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "developerProviderName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPool, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolName")
    def identity_pool_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityPoolName"))

    @identity_pool_name.setter
    def identity_pool_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPool, "identity_pool_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityPoolName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openidConnectProviderArns")
    def openid_connect_provider_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "openidConnectProviderArns"))

    @openid_connect_provider_arns.setter
    def openid_connect_provider_arns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPool, "openid_connect_provider_arns").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openidConnectProviderArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samlProviderArns")
    def saml_provider_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "samlProviderArns"))

    @saml_provider_arns.setter
    def saml_provider_arns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPool, "saml_provider_arns").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samlProviderArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedLoginProviders")
    def supported_login_providers(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "supportedLoginProviders"))

    @supported_login_providers.setter
    def supported_login_providers(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPool, "supported_login_providers").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "supportedLoginProviders", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPool, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPool, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolCognitoIdentityProviders",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "provider_name": "providerName",
        "server_side_token_check": "serverSideTokenCheck",
    },
)
class CognitoIdentityPoolCognitoIdentityProviders:
    def __init__(
        self,
        *,
        client_id: typing.Optional[builtins.str] = None,
        provider_name: typing.Optional[builtins.str] = None,
        server_side_token_check: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#client_id CognitoIdentityPool#client_id}.
        :param provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#provider_name CognitoIdentityPool#provider_name}.
        :param server_side_token_check: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#server_side_token_check CognitoIdentityPool#server_side_token_check}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolCognitoIdentityProviders.__init__)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument provider_name", value=provider_name, expected_type=type_hints["provider_name"])
            check_type(argname="argument server_side_token_check", value=server_side_token_check, expected_type=type_hints["server_side_token_check"])
        self._values: typing.Dict[str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if provider_name is not None:
            self._values["provider_name"] = provider_name
        if server_side_token_check is not None:
            self._values["server_side_token_check"] = server_side_token_check

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#client_id CognitoIdentityPool#client_id}.'''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#provider_name CognitoIdentityPool#provider_name}.'''
        result = self._values.get("provider_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_side_token_check(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#server_side_token_check CognitoIdentityPool#server_side_token_check}.'''
        result = self._values.get("server_side_token_check")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolCognitoIdentityProviders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoIdentityPoolCognitoIdentityProvidersList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolCognitoIdentityProvidersList",
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
            type_hints = typing.get_type_hints(CognitoIdentityPoolCognitoIdentityProvidersList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CognitoIdentityPoolCognitoIdentityProvidersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolCognitoIdentityProvidersList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CognitoIdentityPoolCognitoIdentityProvidersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolCognitoIdentityProvidersList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolCognitoIdentityProvidersList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolCognitoIdentityProvidersList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolCognitoIdentityProviders]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolCognitoIdentityProviders]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolCognitoIdentityProviders]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolCognitoIdentityProvidersList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoIdentityPoolCognitoIdentityProvidersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolCognitoIdentityProvidersOutputReference",
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
            type_hints = typing.get_type_hints(CognitoIdentityPoolCognitoIdentityProvidersOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetProviderName")
    def reset_provider_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviderName", []))

    @jsii.member(jsii_name="resetServerSideTokenCheck")
    def reset_server_side_token_check(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideTokenCheck", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerNameInput")
    def provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideTokenCheckInput")
    def server_side_token_check_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "serverSideTokenCheckInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolCognitoIdentityProvidersOutputReference, "client_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @provider_name.setter
    def provider_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolCognitoIdentityProvidersOutputReference, "provider_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideTokenCheck")
    def server_side_token_check(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "serverSideTokenCheck"))

    @server_side_token_check.setter
    def server_side_token_check(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolCognitoIdentityProvidersOutputReference, "server_side_token_check").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverSideTokenCheck", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[CognitoIdentityPoolCognitoIdentityProviders, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[CognitoIdentityPoolCognitoIdentityProviders, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[CognitoIdentityPoolCognitoIdentityProviders, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolCognitoIdentityProvidersOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "identity_pool_name": "identityPoolName",
        "allow_classic_flow": "allowClassicFlow",
        "allow_unauthenticated_identities": "allowUnauthenticatedIdentities",
        "cognito_identity_providers": "cognitoIdentityProviders",
        "developer_provider_name": "developerProviderName",
        "id": "id",
        "openid_connect_provider_arns": "openidConnectProviderArns",
        "saml_provider_arns": "samlProviderArns",
        "supported_login_providers": "supportedLoginProviders",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class CognitoIdentityPoolConfig(cdktf.TerraformMetaArguments):
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
        identity_pool_name: builtins.str,
        allow_classic_flow: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        allow_unauthenticated_identities: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cognito_identity_providers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[CognitoIdentityPoolCognitoIdentityProviders, typing.Dict[str, typing.Any]]]]] = None,
        developer_provider_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        openid_connect_provider_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        saml_provider_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        supported_login_providers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param identity_pool_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#identity_pool_name CognitoIdentityPool#identity_pool_name}.
        :param allow_classic_flow: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_classic_flow CognitoIdentityPool#allow_classic_flow}.
        :param allow_unauthenticated_identities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_unauthenticated_identities CognitoIdentityPool#allow_unauthenticated_identities}.
        :param cognito_identity_providers: cognito_identity_providers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#cognito_identity_providers CognitoIdentityPool#cognito_identity_providers}
        :param developer_provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#developer_provider_name CognitoIdentityPool#developer_provider_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#id CognitoIdentityPool#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param openid_connect_provider_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#openid_connect_provider_arns CognitoIdentityPool#openid_connect_provider_arns}.
        :param saml_provider_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#saml_provider_arns CognitoIdentityPool#saml_provider_arns}.
        :param supported_login_providers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#supported_login_providers CognitoIdentityPool#supported_login_providers}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags CognitoIdentityPool#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags_all CognitoIdentityPool#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument identity_pool_name", value=identity_pool_name, expected_type=type_hints["identity_pool_name"])
            check_type(argname="argument allow_classic_flow", value=allow_classic_flow, expected_type=type_hints["allow_classic_flow"])
            check_type(argname="argument allow_unauthenticated_identities", value=allow_unauthenticated_identities, expected_type=type_hints["allow_unauthenticated_identities"])
            check_type(argname="argument cognito_identity_providers", value=cognito_identity_providers, expected_type=type_hints["cognito_identity_providers"])
            check_type(argname="argument developer_provider_name", value=developer_provider_name, expected_type=type_hints["developer_provider_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument openid_connect_provider_arns", value=openid_connect_provider_arns, expected_type=type_hints["openid_connect_provider_arns"])
            check_type(argname="argument saml_provider_arns", value=saml_provider_arns, expected_type=type_hints["saml_provider_arns"])
            check_type(argname="argument supported_login_providers", value=supported_login_providers, expected_type=type_hints["supported_login_providers"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "identity_pool_name": identity_pool_name,
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
        if allow_classic_flow is not None:
            self._values["allow_classic_flow"] = allow_classic_flow
        if allow_unauthenticated_identities is not None:
            self._values["allow_unauthenticated_identities"] = allow_unauthenticated_identities
        if cognito_identity_providers is not None:
            self._values["cognito_identity_providers"] = cognito_identity_providers
        if developer_provider_name is not None:
            self._values["developer_provider_name"] = developer_provider_name
        if id is not None:
            self._values["id"] = id
        if openid_connect_provider_arns is not None:
            self._values["openid_connect_provider_arns"] = openid_connect_provider_arns
        if saml_provider_arns is not None:
            self._values["saml_provider_arns"] = saml_provider_arns
        if supported_login_providers is not None:
            self._values["supported_login_providers"] = supported_login_providers
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
    def identity_pool_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#identity_pool_name CognitoIdentityPool#identity_pool_name}.'''
        result = self._values.get("identity_pool_name")
        assert result is not None, "Required property 'identity_pool_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_classic_flow(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_classic_flow CognitoIdentityPool#allow_classic_flow}.'''
        result = self._values.get("allow_classic_flow")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def allow_unauthenticated_identities(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_unauthenticated_identities CognitoIdentityPool#allow_unauthenticated_identities}.'''
        result = self._values.get("allow_unauthenticated_identities")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def cognito_identity_providers(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolCognitoIdentityProviders]]]:
        '''cognito_identity_providers block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#cognito_identity_providers CognitoIdentityPool#cognito_identity_providers}
        '''
        result = self._values.get("cognito_identity_providers")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolCognitoIdentityProviders]]], result)

    @builtins.property
    def developer_provider_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#developer_provider_name CognitoIdentityPool#developer_provider_name}.'''
        result = self._values.get("developer_provider_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#id CognitoIdentityPool#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openid_connect_provider_arns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#openid_connect_provider_arns CognitoIdentityPool#openid_connect_provider_arns}.'''
        result = self._values.get("openid_connect_provider_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def saml_provider_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#saml_provider_arns CognitoIdentityPool#saml_provider_arns}.'''
        result = self._values.get("saml_provider_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def supported_login_providers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#supported_login_providers CognitoIdentityPool#supported_login_providers}.'''
        result = self._values.get("supported_login_providers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags CognitoIdentityPool#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags_all CognitoIdentityPool#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoIdentityPoolProviderPrincipalTag(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolProviderPrincipalTag",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag aws_cognito_identity_pool_provider_principal_tag}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        identity_pool_id: builtins.str,
        identity_provider_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        principal_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        use_defaults: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag aws_cognito_identity_pool_provider_principal_tag} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identity_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_pool_id CognitoIdentityPoolProviderPrincipalTag#identity_pool_id}.
        :param identity_provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_provider_name CognitoIdentityPoolProviderPrincipalTag#identity_provider_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#id CognitoIdentityPoolProviderPrincipalTag#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param principal_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#principal_tags CognitoIdentityPoolProviderPrincipalTag#principal_tags}.
        :param use_defaults: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#use_defaults CognitoIdentityPoolProviderPrincipalTag#use_defaults}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolProviderPrincipalTag.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoIdentityPoolProviderPrincipalTagConfig(
            identity_pool_id=identity_pool_id,
            identity_provider_name=identity_provider_name,
            id=id,
            principal_tags=principal_tags,
            use_defaults=use_defaults,
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

    @jsii.member(jsii_name="resetPrincipalTags")
    def reset_principal_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrincipalTags", []))

    @jsii.member(jsii_name="resetUseDefaults")
    def reset_use_defaults(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseDefaults", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolIdInput")
    def identity_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderNameInput")
    def identity_provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principalTagsInput")
    def principal_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "principalTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useDefaultsInput")
    def use_defaults_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useDefaultsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolProviderPrincipalTag, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityPoolId"))

    @identity_pool_id.setter
    def identity_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolProviderPrincipalTag, "identity_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityPoolId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderName")
    def identity_provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderName"))

    @identity_provider_name.setter
    def identity_provider_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolProviderPrincipalTag, "identity_provider_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principalTags")
    def principal_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "principalTags"))

    @principal_tags.setter
    def principal_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolProviderPrincipalTag, "principal_tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "principalTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useDefaults")
    def use_defaults(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useDefaults"))

    @use_defaults.setter
    def use_defaults(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolProviderPrincipalTag, "use_defaults").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useDefaults", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolProviderPrincipalTagConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "identity_pool_id": "identityPoolId",
        "identity_provider_name": "identityProviderName",
        "id": "id",
        "principal_tags": "principalTags",
        "use_defaults": "useDefaults",
    },
)
class CognitoIdentityPoolProviderPrincipalTagConfig(cdktf.TerraformMetaArguments):
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
        identity_pool_id: builtins.str,
        identity_provider_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        principal_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        use_defaults: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param identity_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_pool_id CognitoIdentityPoolProviderPrincipalTag#identity_pool_id}.
        :param identity_provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_provider_name CognitoIdentityPoolProviderPrincipalTag#identity_provider_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#id CognitoIdentityPoolProviderPrincipalTag#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param principal_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#principal_tags CognitoIdentityPoolProviderPrincipalTag#principal_tags}.
        :param use_defaults: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#use_defaults CognitoIdentityPoolProviderPrincipalTag#use_defaults}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolProviderPrincipalTagConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument identity_pool_id", value=identity_pool_id, expected_type=type_hints["identity_pool_id"])
            check_type(argname="argument identity_provider_name", value=identity_provider_name, expected_type=type_hints["identity_provider_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument principal_tags", value=principal_tags, expected_type=type_hints["principal_tags"])
            check_type(argname="argument use_defaults", value=use_defaults, expected_type=type_hints["use_defaults"])
        self._values: typing.Dict[str, typing.Any] = {
            "identity_pool_id": identity_pool_id,
            "identity_provider_name": identity_provider_name,
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
        if principal_tags is not None:
            self._values["principal_tags"] = principal_tags
        if use_defaults is not None:
            self._values["use_defaults"] = use_defaults

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
    def identity_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_pool_id CognitoIdentityPoolProviderPrincipalTag#identity_pool_id}.'''
        result = self._values.get("identity_pool_id")
        assert result is not None, "Required property 'identity_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_provider_name CognitoIdentityPoolProviderPrincipalTag#identity_provider_name}.'''
        result = self._values.get("identity_provider_name")
        assert result is not None, "Required property 'identity_provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#id CognitoIdentityPoolProviderPrincipalTag#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def principal_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#principal_tags CognitoIdentityPoolProviderPrincipalTag#principal_tags}.'''
        result = self._values.get("principal_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def use_defaults(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#use_defaults CognitoIdentityPoolProviderPrincipalTag#use_defaults}.'''
        result = self._values.get("use_defaults")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolProviderPrincipalTagConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoIdentityPoolRolesAttachment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment aws_cognito_identity_pool_roles_attachment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        identity_pool_id: builtins.str,
        roles: typing.Mapping[builtins.str, builtins.str],
        id: typing.Optional[builtins.str] = None,
        role_mapping: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoIdentityPoolRolesAttachmentRoleMapping", typing.Dict[str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment aws_cognito_identity_pool_roles_attachment} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identity_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#identity_pool_id CognitoIdentityPoolRolesAttachment#identity_pool_id}.
        :param roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#roles CognitoIdentityPoolRolesAttachment#roles}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#id CognitoIdentityPoolRolesAttachment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param role_mapping: role_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#role_mapping CognitoIdentityPoolRolesAttachment#role_mapping}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachment.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoIdentityPoolRolesAttachmentConfig(
            identity_pool_id=identity_pool_id,
            roles=roles,
            id=id,
            role_mapping=role_mapping,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putRoleMapping")
    def put_role_mapping(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoIdentityPoolRolesAttachmentRoleMapping", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachment.put_role_mapping)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRoleMapping", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRoleMapping")
    def reset_role_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleMapping", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleMapping")
    def role_mapping(self) -> "CognitoIdentityPoolRolesAttachmentRoleMappingList":
        return typing.cast("CognitoIdentityPoolRolesAttachmentRoleMappingList", jsii.get(self, "roleMapping"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolIdInput")
    def identity_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleMappingInput")
    def role_mapping_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"]]], jsii.get(self, "roleMappingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rolesInput")
    def roles_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "rolesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachment, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityPoolId"))

    @identity_pool_id.setter
    def identity_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachment, "identity_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityPoolId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roles")
    def roles(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "roles"))

    @roles.setter
    def roles(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachment, "roles").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roles", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "identity_pool_id": "identityPoolId",
        "roles": "roles",
        "id": "id",
        "role_mapping": "roleMapping",
    },
)
class CognitoIdentityPoolRolesAttachmentConfig(cdktf.TerraformMetaArguments):
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
        identity_pool_id: builtins.str,
        roles: typing.Mapping[builtins.str, builtins.str],
        id: typing.Optional[builtins.str] = None,
        role_mapping: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoIdentityPoolRolesAttachmentRoleMapping", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param identity_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#identity_pool_id CognitoIdentityPoolRolesAttachment#identity_pool_id}.
        :param roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#roles CognitoIdentityPoolRolesAttachment#roles}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#id CognitoIdentityPoolRolesAttachment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param role_mapping: role_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#role_mapping CognitoIdentityPoolRolesAttachment#role_mapping}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachmentConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument identity_pool_id", value=identity_pool_id, expected_type=type_hints["identity_pool_id"])
            check_type(argname="argument roles", value=roles, expected_type=type_hints["roles"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument role_mapping", value=role_mapping, expected_type=type_hints["role_mapping"])
        self._values: typing.Dict[str, typing.Any] = {
            "identity_pool_id": identity_pool_id,
            "roles": roles,
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
        if role_mapping is not None:
            self._values["role_mapping"] = role_mapping

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
    def identity_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#identity_pool_id CognitoIdentityPoolRolesAttachment#identity_pool_id}.'''
        result = self._values.get("identity_pool_id")
        assert result is not None, "Required property 'identity_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def roles(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#roles CognitoIdentityPoolRolesAttachment#roles}.'''
        result = self._values.get("roles")
        assert result is not None, "Required property 'roles' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#id CognitoIdentityPoolRolesAttachment#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_mapping(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"]]]:
        '''role_mapping block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#role_mapping CognitoIdentityPoolRolesAttachment#role_mapping}
        '''
        result = self._values.get("role_mapping")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolRolesAttachmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachmentRoleMapping",
    jsii_struct_bases=[],
    name_mapping={
        "identity_provider": "identityProvider",
        "type": "type",
        "ambiguous_role_resolution": "ambiguousRoleResolution",
        "mapping_rule": "mappingRule",
    },
)
class CognitoIdentityPoolRolesAttachmentRoleMapping:
    def __init__(
        self,
        *,
        identity_provider: builtins.str,
        type: builtins.str,
        ambiguous_role_resolution: typing.Optional[builtins.str] = None,
        mapping_rule: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param identity_provider: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#identity_provider CognitoIdentityPoolRolesAttachment#identity_provider}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#type CognitoIdentityPoolRolesAttachment#type}.
        :param ambiguous_role_resolution: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#ambiguous_role_resolution CognitoIdentityPoolRolesAttachment#ambiguous_role_resolution}.
        :param mapping_rule: mapping_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#mapping_rule CognitoIdentityPoolRolesAttachment#mapping_rule}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachmentRoleMapping.__init__)
            check_type(argname="argument identity_provider", value=identity_provider, expected_type=type_hints["identity_provider"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument ambiguous_role_resolution", value=ambiguous_role_resolution, expected_type=type_hints["ambiguous_role_resolution"])
            check_type(argname="argument mapping_rule", value=mapping_rule, expected_type=type_hints["mapping_rule"])
        self._values: typing.Dict[str, typing.Any] = {
            "identity_provider": identity_provider,
            "type": type,
        }
        if ambiguous_role_resolution is not None:
            self._values["ambiguous_role_resolution"] = ambiguous_role_resolution
        if mapping_rule is not None:
            self._values["mapping_rule"] = mapping_rule

    @builtins.property
    def identity_provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#identity_provider CognitoIdentityPoolRolesAttachment#identity_provider}.'''
        result = self._values.get("identity_provider")
        assert result is not None, "Required property 'identity_provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#type CognitoIdentityPoolRolesAttachment#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ambiguous_role_resolution(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#ambiguous_role_resolution CognitoIdentityPoolRolesAttachment#ambiguous_role_resolution}.'''
        result = self._values.get("ambiguous_role_resolution")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mapping_rule(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule"]]]:
        '''mapping_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#mapping_rule CognitoIdentityPoolRolesAttachment#mapping_rule}
        '''
        result = self._values.get("mapping_rule")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolRolesAttachmentRoleMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoIdentityPoolRolesAttachmentRoleMappingList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachmentRoleMappingList",
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
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachmentRoleMappingList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachmentRoleMappingList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolRolesAttachmentRoleMapping]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolRolesAttachmentRoleMapping]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolRolesAttachmentRoleMapping]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule",
    jsii_struct_bases=[],
    name_mapping={
        "claim": "claim",
        "match_type": "matchType",
        "role_arn": "roleArn",
        "value": "value",
    },
)
class CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule:
    def __init__(
        self,
        *,
        claim: builtins.str,
        match_type: builtins.str,
        role_arn: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param claim: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#claim CognitoIdentityPoolRolesAttachment#claim}.
        :param match_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#match_type CognitoIdentityPoolRolesAttachment#match_type}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#role_arn CognitoIdentityPoolRolesAttachment#role_arn}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#value CognitoIdentityPoolRolesAttachment#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule.__init__)
            check_type(argname="argument claim", value=claim, expected_type=type_hints["claim"])
            check_type(argname="argument match_type", value=match_type, expected_type=type_hints["match_type"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[str, typing.Any] = {
            "claim": claim,
            "match_type": match_type,
            "role_arn": role_arn,
            "value": value,
        }

    @builtins.property
    def claim(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#claim CognitoIdentityPoolRolesAttachment#claim}.'''
        result = self._values.get("claim")
        assert result is not None, "Required property 'claim' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def match_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#match_type CognitoIdentityPoolRolesAttachment#match_type}.'''
        result = self._values.get("match_type")
        assert result is not None, "Required property 'match_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#role_arn CognitoIdentityPoolRolesAttachment#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#value CognitoIdentityPoolRolesAttachment#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList",
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
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference",
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
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="claimInput")
    def claim_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "claimInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="matchTypeInput")
    def match_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "matchTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="claim")
    def claim(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "claim"))

    @claim.setter
    def claim(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference, "claim").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claim", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="matchType")
    def match_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "matchType"))

    @match_type.setter
    def match_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference, "match_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "matchType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference, "role_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference, "value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference",
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
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putMappingRule")
    def put_mapping_rule(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule, typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference.put_mapping_rule)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMappingRule", [value]))

    @jsii.member(jsii_name="resetAmbiguousRoleResolution")
    def reset_ambiguous_role_resolution(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAmbiguousRoleResolution", []))

    @jsii.member(jsii_name="resetMappingRule")
    def reset_mapping_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMappingRule", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mappingRule")
    def mapping_rule(
        self,
    ) -> CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList:
        return typing.cast(CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList, jsii.get(self, "mappingRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ambiguousRoleResolutionInput")
    def ambiguous_role_resolution_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ambiguousRoleResolutionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderInput")
    def identity_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mappingRuleInput")
    def mapping_rule_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule]]], jsii.get(self, "mappingRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ambiguousRoleResolution")
    def ambiguous_role_resolution(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ambiguousRoleResolution"))

    @ambiguous_role_resolution.setter
    def ambiguous_role_resolution(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference, "ambiguous_role_resolution").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ambiguousRoleResolution", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProvider")
    def identity_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProvider"))

    @identity_provider.setter
    def identity_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference, "identity_provider").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProvider", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[CognitoIdentityPoolRolesAttachmentRoleMapping, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[CognitoIdentityPoolRolesAttachmentRoleMapping, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[CognitoIdentityPoolRolesAttachmentRoleMapping, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoIdentityProvider(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider aws_cognito_identity_provider}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        provider_details: typing.Mapping[builtins.str, builtins.str],
        provider_name: builtins.str,
        provider_type: builtins.str,
        user_pool_id: builtins.str,
        attribute_mapping: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        idp_identifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider aws_cognito_identity_provider} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param provider_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_details CognitoIdentityProvider#provider_details}.
        :param provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_name CognitoIdentityProvider#provider_name}.
        :param provider_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_type CognitoIdentityProvider#provider_type}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#user_pool_id CognitoIdentityProvider#user_pool_id}.
        :param attribute_mapping: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#attribute_mapping CognitoIdentityProvider#attribute_mapping}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#id CognitoIdentityProvider#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param idp_identifiers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#idp_identifiers CognitoIdentityProvider#idp_identifiers}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityProvider.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoIdentityProviderConfig(
            provider_details=provider_details,
            provider_name=provider_name,
            provider_type=provider_type,
            user_pool_id=user_pool_id,
            attribute_mapping=attribute_mapping,
            id=id,
            idp_identifiers=idp_identifiers,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetAttributeMapping")
    def reset_attribute_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttributeMapping", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdpIdentifiers")
    def reset_idp_identifiers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpIdentifiers", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeMappingInput")
    def attribute_mapping_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "attributeMappingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idpIdentifiersInput")
    def idp_identifiers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "idpIdentifiersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerDetailsInput")
    def provider_details_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "providerDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerNameInput")
    def provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerTypeInput")
    def provider_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeMapping")
    def attribute_mapping(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "attributeMapping"))

    @attribute_mapping.setter
    def attribute_mapping(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityProvider, "attribute_mapping").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeMapping", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityProvider, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idpIdentifiers")
    def idp_identifiers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "idpIdentifiers"))

    @idp_identifiers.setter
    def idp_identifiers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityProvider, "idp_identifiers").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpIdentifiers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerDetails")
    def provider_details(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "providerDetails"))

    @provider_details.setter
    def provider_details(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityProvider, "provider_details").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerDetails", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @provider_name.setter
    def provider_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityProvider, "provider_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerType")
    def provider_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerType"))

    @provider_type.setter
    def provider_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityProvider, "provider_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoIdentityProvider, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityProviderConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "provider_details": "providerDetails",
        "provider_name": "providerName",
        "provider_type": "providerType",
        "user_pool_id": "userPoolId",
        "attribute_mapping": "attributeMapping",
        "id": "id",
        "idp_identifiers": "idpIdentifiers",
    },
)
class CognitoIdentityProviderConfig(cdktf.TerraformMetaArguments):
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
        provider_details: typing.Mapping[builtins.str, builtins.str],
        provider_name: builtins.str,
        provider_type: builtins.str,
        user_pool_id: builtins.str,
        attribute_mapping: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        idp_identifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param provider_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_details CognitoIdentityProvider#provider_details}.
        :param provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_name CognitoIdentityProvider#provider_name}.
        :param provider_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_type CognitoIdentityProvider#provider_type}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#user_pool_id CognitoIdentityProvider#user_pool_id}.
        :param attribute_mapping: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#attribute_mapping CognitoIdentityProvider#attribute_mapping}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#id CognitoIdentityProvider#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param idp_identifiers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#idp_identifiers CognitoIdentityProvider#idp_identifiers}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoIdentityProviderConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument provider_details", value=provider_details, expected_type=type_hints["provider_details"])
            check_type(argname="argument provider_name", value=provider_name, expected_type=type_hints["provider_name"])
            check_type(argname="argument provider_type", value=provider_type, expected_type=type_hints["provider_type"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument attribute_mapping", value=attribute_mapping, expected_type=type_hints["attribute_mapping"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument idp_identifiers", value=idp_identifiers, expected_type=type_hints["idp_identifiers"])
        self._values: typing.Dict[str, typing.Any] = {
            "provider_details": provider_details,
            "provider_name": provider_name,
            "provider_type": provider_type,
            "user_pool_id": user_pool_id,
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
        if attribute_mapping is not None:
            self._values["attribute_mapping"] = attribute_mapping
        if id is not None:
            self._values["id"] = id
        if idp_identifiers is not None:
            self._values["idp_identifiers"] = idp_identifiers

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
    def provider_details(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_details CognitoIdentityProvider#provider_details}.'''
        result = self._values.get("provider_details")
        assert result is not None, "Required property 'provider_details' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def provider_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_name CognitoIdentityProvider#provider_name}.'''
        result = self._values.get("provider_name")
        assert result is not None, "Required property 'provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_type CognitoIdentityProvider#provider_type}.'''
        result = self._values.get("provider_type")
        assert result is not None, "Required property 'provider_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#user_pool_id CognitoIdentityProvider#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_mapping(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#attribute_mapping CognitoIdentityProvider#attribute_mapping}.'''
        result = self._values.get("attribute_mapping")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#id CognitoIdentityProvider#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idp_identifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#idp_identifiers CognitoIdentityProvider#idp_identifiers}.'''
        result = self._values.get("idp_identifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoResourceServer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoResourceServer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server aws_cognito_resource_server}.'''

    def __init__(
        self,
        scope_: constructs.Construct,
        id_: builtins.str,
        *,
        identifier: builtins.str,
        name: builtins.str,
        user_pool_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        scope: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoResourceServerScope", typing.Dict[str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server aws_cognito_resource_server} Resource.

        :param scope_: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#identifier CognitoResourceServer#identifier}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#name CognitoResourceServer#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#user_pool_id CognitoResourceServer#user_pool_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#id CognitoResourceServer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param scope: scope block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope CognitoResourceServer#scope}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoResourceServer.__init__)
            check_type(argname="argument scope_", value=scope_, expected_type=type_hints["scope_"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoResourceServerConfig(
            identifier=identifier,
            name=name,
            user_pool_id=user_pool_id,
            id=id,
            scope=scope,
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
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoResourceServerScope", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoResourceServer.put_scope)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putScope", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetScope")
    def reset_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScope", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> "CognitoResourceServerScopeList":
        return typing.cast("CognitoResourceServerScopeList", jsii.get(self, "scope"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeIdentifiers")
    def scope_identifiers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "scopeIdentifiers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifierInput")
    def identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeInput")
    def scope_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoResourceServerScope"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoResourceServerScope"]]], jsii.get(self, "scopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoResourceServer, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identifier"))

    @identifier.setter
    def identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoResourceServer, "identifier").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoResourceServer, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoResourceServer, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoResourceServerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "identifier": "identifier",
        "name": "name",
        "user_pool_id": "userPoolId",
        "id": "id",
        "scope": "scope",
    },
)
class CognitoResourceServerConfig(cdktf.TerraformMetaArguments):
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
        identifier: builtins.str,
        name: builtins.str,
        user_pool_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        scope: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoResourceServerScope", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#identifier CognitoResourceServer#identifier}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#name CognitoResourceServer#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#user_pool_id CognitoResourceServer#user_pool_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#id CognitoResourceServer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param scope: scope block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope CognitoResourceServer#scope}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoResourceServerConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        self._values: typing.Dict[str, typing.Any] = {
            "identifier": identifier,
            "name": name,
            "user_pool_id": user_pool_id,
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
        if scope is not None:
            self._values["scope"] = scope

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
    def identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#identifier CognitoResourceServer#identifier}.'''
        result = self._values.get("identifier")
        assert result is not None, "Required property 'identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#name CognitoResourceServer#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#user_pool_id CognitoResourceServer#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#id CognitoResourceServer#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scope(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoResourceServerScope"]]]:
        '''scope block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope CognitoResourceServer#scope}
        '''
        result = self._values.get("scope")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoResourceServerScope"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoResourceServerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoResourceServerScope",
    jsii_struct_bases=[],
    name_mapping={"scope_description": "scopeDescription", "scope_name": "scopeName"},
)
class CognitoResourceServerScope:
    def __init__(
        self,
        *,
        scope_description: builtins.str,
        scope_name: builtins.str,
    ) -> None:
        '''
        :param scope_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope_description CognitoResourceServer#scope_description}.
        :param scope_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope_name CognitoResourceServer#scope_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoResourceServerScope.__init__)
            check_type(argname="argument scope_description", value=scope_description, expected_type=type_hints["scope_description"])
            check_type(argname="argument scope_name", value=scope_name, expected_type=type_hints["scope_name"])
        self._values: typing.Dict[str, typing.Any] = {
            "scope_description": scope_description,
            "scope_name": scope_name,
        }

    @builtins.property
    def scope_description(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope_description CognitoResourceServer#scope_description}.'''
        result = self._values.get("scope_description")
        assert result is not None, "Required property 'scope_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope_name CognitoResourceServer#scope_name}.'''
        result = self._values.get("scope_name")
        assert result is not None, "Required property 'scope_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoResourceServerScope(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoResourceServerScopeList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoResourceServerScopeList",
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
            type_hints = typing.get_type_hints(CognitoResourceServerScopeList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "CognitoResourceServerScopeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoResourceServerScopeList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CognitoResourceServerScopeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoResourceServerScopeList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoResourceServerScopeList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoResourceServerScopeList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoResourceServerScope]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoResourceServerScope]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoResourceServerScope]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoResourceServerScopeList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoResourceServerScopeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoResourceServerScopeOutputReference",
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
            type_hints = typing.get_type_hints(CognitoResourceServerScopeOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeDescriptionInput")
    def scope_description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeDescriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeNameInput")
    def scope_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeDescription")
    def scope_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scopeDescription"))

    @scope_description.setter
    def scope_description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoResourceServerScopeOutputReference, "scope_description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scopeDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeName")
    def scope_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scopeName"))

    @scope_name.setter
    def scope_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoResourceServerScopeOutputReference, "scope_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scopeName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[CognitoResourceServerScope, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[CognitoResourceServerScope, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[CognitoResourceServerScope, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoResourceServerScopeOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoRiskConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration aws_cognito_risk_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        user_pool_id: builtins.str,
        account_takeover_risk_configuration: typing.Optional[typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfiguration", typing.Dict[str, typing.Any]]] = None,
        client_id: typing.Optional[builtins.str] = None,
        compromised_credentials_risk_configuration: typing.Optional[typing.Union["CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        risk_exception_configuration: typing.Optional[typing.Union["CognitoRiskConfigurationRiskExceptionConfiguration", typing.Dict[str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration aws_cognito_risk_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#user_pool_id CognitoRiskConfiguration#user_pool_id}.
        :param account_takeover_risk_configuration: account_takeover_risk_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#account_takeover_risk_configuration CognitoRiskConfiguration#account_takeover_risk_configuration}
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#client_id CognitoRiskConfiguration#client_id}.
        :param compromised_credentials_risk_configuration: compromised_credentials_risk_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#compromised_credentials_risk_configuration CognitoRiskConfiguration#compromised_credentials_risk_configuration}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#id CognitoRiskConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param risk_exception_configuration: risk_exception_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#risk_exception_configuration CognitoRiskConfiguration#risk_exception_configuration}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfiguration.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoRiskConfigurationConfig(
            user_pool_id=user_pool_id,
            account_takeover_risk_configuration=account_takeover_risk_configuration,
            client_id=client_id,
            compromised_credentials_risk_configuration=compromised_credentials_risk_configuration,
            id=id,
            risk_exception_configuration=risk_exception_configuration,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putAccountTakeoverRiskConfiguration")
    def put_account_takeover_risk_configuration(
        self,
        *,
        actions: typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions", typing.Dict[str, typing.Any]],
        notify_configuration: typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration", typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param actions: actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#actions CognitoRiskConfiguration#actions}
        :param notify_configuration: notify_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify_configuration CognitoRiskConfiguration#notify_configuration}
        '''
        value = CognitoRiskConfigurationAccountTakeoverRiskConfiguration(
            actions=actions, notify_configuration=notify_configuration
        )

        return typing.cast(None, jsii.invoke(self, "putAccountTakeoverRiskConfiguration", [value]))

    @jsii.member(jsii_name="putCompromisedCredentialsRiskConfiguration")
    def put_compromised_credentials_risk_configuration(
        self,
        *,
        actions: typing.Union["CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions", typing.Dict[str, typing.Any]],
        event_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param actions: actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#actions CognitoRiskConfiguration#actions}
        :param event_filter: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_filter CognitoRiskConfiguration#event_filter}.
        '''
        value = CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration(
            actions=actions, event_filter=event_filter
        )

        return typing.cast(None, jsii.invoke(self, "putCompromisedCredentialsRiskConfiguration", [value]))

    @jsii.member(jsii_name="putRiskExceptionConfiguration")
    def put_risk_exception_configuration(
        self,
        *,
        blocked_ip_range_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        skipped_ip_range_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param blocked_ip_range_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#blocked_ip_range_list CognitoRiskConfiguration#blocked_ip_range_list}.
        :param skipped_ip_range_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#skipped_ip_range_list CognitoRiskConfiguration#skipped_ip_range_list}.
        '''
        value = CognitoRiskConfigurationRiskExceptionConfiguration(
            blocked_ip_range_list=blocked_ip_range_list,
            skipped_ip_range_list=skipped_ip_range_list,
        )

        return typing.cast(None, jsii.invoke(self, "putRiskExceptionConfiguration", [value]))

    @jsii.member(jsii_name="resetAccountTakeoverRiskConfiguration")
    def reset_account_takeover_risk_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountTakeoverRiskConfiguration", []))

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetCompromisedCredentialsRiskConfiguration")
    def reset_compromised_credentials_risk_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompromisedCredentialsRiskConfiguration", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRiskExceptionConfiguration")
    def reset_risk_exception_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRiskExceptionConfiguration", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountTakeoverRiskConfiguration")
    def account_takeover_risk_configuration(
        self,
    ) -> "CognitoRiskConfigurationAccountTakeoverRiskConfigurationOutputReference":
        return typing.cast("CognitoRiskConfigurationAccountTakeoverRiskConfigurationOutputReference", jsii.get(self, "accountTakeoverRiskConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compromisedCredentialsRiskConfiguration")
    def compromised_credentials_risk_configuration(
        self,
    ) -> "CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationOutputReference":
        return typing.cast("CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationOutputReference", jsii.get(self, "compromisedCredentialsRiskConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="riskExceptionConfiguration")
    def risk_exception_configuration(
        self,
    ) -> "CognitoRiskConfigurationRiskExceptionConfigurationOutputReference":
        return typing.cast("CognitoRiskConfigurationRiskExceptionConfigurationOutputReference", jsii.get(self, "riskExceptionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountTakeoverRiskConfigurationInput")
    def account_takeover_risk_configuration_input(
        self,
    ) -> typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfiguration"]:
        return typing.cast(typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfiguration"], jsii.get(self, "accountTakeoverRiskConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compromisedCredentialsRiskConfigurationInput")
    def compromised_credentials_risk_configuration_input(
        self,
    ) -> typing.Optional["CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration"]:
        return typing.cast(typing.Optional["CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration"], jsii.get(self, "compromisedCredentialsRiskConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="riskExceptionConfigurationInput")
    def risk_exception_configuration_input(
        self,
    ) -> typing.Optional["CognitoRiskConfigurationRiskExceptionConfiguration"]:
        return typing.cast(typing.Optional["CognitoRiskConfigurationRiskExceptionConfiguration"], jsii.get(self, "riskExceptionConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfiguration, "client_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfiguration, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfiguration, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfiguration",
    jsii_struct_bases=[],
    name_mapping={"actions": "actions", "notify_configuration": "notifyConfiguration"},
)
class CognitoRiskConfigurationAccountTakeoverRiskConfiguration:
    def __init__(
        self,
        *,
        actions: typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions", typing.Dict[str, typing.Any]],
        notify_configuration: typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration", typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param actions: actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#actions CognitoRiskConfiguration#actions}
        :param notify_configuration: notify_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify_configuration CognitoRiskConfiguration#notify_configuration}
        '''
        if isinstance(actions, dict):
            actions = CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions(**actions)
        if isinstance(notify_configuration, dict):
            notify_configuration = CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration(**notify_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfiguration.__init__)
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument notify_configuration", value=notify_configuration, expected_type=type_hints["notify_configuration"])
        self._values: typing.Dict[str, typing.Any] = {
            "actions": actions,
            "notify_configuration": notify_configuration,
        }

    @builtins.property
    def actions(
        self,
    ) -> "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions":
        '''actions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#actions CognitoRiskConfiguration#actions}
        '''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast("CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions", result)

    @builtins.property
    def notify_configuration(
        self,
    ) -> "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration":
        '''notify_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify_configuration CognitoRiskConfiguration#notify_configuration}
        '''
        result = self._values.get("notify_configuration")
        assert result is not None, "Required property 'notify_configuration' is missing"
        return typing.cast("CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationAccountTakeoverRiskConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions",
    jsii_struct_bases=[],
    name_mapping={
        "high_action": "highAction",
        "low_action": "lowAction",
        "medium_action": "mediumAction",
    },
)
class CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions:
    def __init__(
        self,
        *,
        high_action: typing.Optional[typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction", typing.Dict[str, typing.Any]]] = None,
        low_action: typing.Optional[typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction", typing.Dict[str, typing.Any]]] = None,
        medium_action: typing.Optional[typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param high_action: high_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#high_action CognitoRiskConfiguration#high_action}
        :param low_action: low_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#low_action CognitoRiskConfiguration#low_action}
        :param medium_action: medium_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#medium_action CognitoRiskConfiguration#medium_action}
        '''
        if isinstance(high_action, dict):
            high_action = CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction(**high_action)
        if isinstance(low_action, dict):
            low_action = CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction(**low_action)
        if isinstance(medium_action, dict):
            medium_action = CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction(**medium_action)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions.__init__)
            check_type(argname="argument high_action", value=high_action, expected_type=type_hints["high_action"])
            check_type(argname="argument low_action", value=low_action, expected_type=type_hints["low_action"])
            check_type(argname="argument medium_action", value=medium_action, expected_type=type_hints["medium_action"])
        self._values: typing.Dict[str, typing.Any] = {}
        if high_action is not None:
            self._values["high_action"] = high_action
        if low_action is not None:
            self._values["low_action"] = low_action
        if medium_action is not None:
            self._values["medium_action"] = medium_action

    @builtins.property
    def high_action(
        self,
    ) -> typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction"]:
        '''high_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#high_action CognitoRiskConfiguration#high_action}
        '''
        result = self._values.get("high_action")
        return typing.cast(typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction"], result)

    @builtins.property
    def low_action(
        self,
    ) -> typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction"]:
        '''low_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#low_action CognitoRiskConfiguration#low_action}
        '''
        result = self._values.get("low_action")
        return typing.cast(typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction"], result)

    @builtins.property
    def medium_action(
        self,
    ) -> typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction"]:
        '''medium_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#medium_action CognitoRiskConfiguration#medium_action}
        '''
        result = self._values.get("medium_action")
        return typing.cast(typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction",
    jsii_struct_bases=[],
    name_mapping={"event_action": "eventAction", "notify": "notify"},
)
class CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction:
    def __init__(
        self,
        *,
        event_action: builtins.str,
        notify: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param event_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.
        :param notify: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify CognitoRiskConfiguration#notify}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction.__init__)
            check_type(argname="argument event_action", value=event_action, expected_type=type_hints["event_action"])
            check_type(argname="argument notify", value=notify, expected_type=type_hints["notify"])
        self._values: typing.Dict[str, typing.Any] = {
            "event_action": event_action,
            "notify": notify,
        }

    @builtins.property
    def event_action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.'''
        result = self._values.get("event_action")
        assert result is not None, "Required property 'event_action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def notify(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify CognitoRiskConfiguration#notify}.'''
        result = self._values.get("notify")
        assert result is not None, "Required property 'notify' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighActionOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighActionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventActionInput")
    def event_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notifyInput")
    def notify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "notifyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventAction")
    def event_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventAction"))

    @event_action.setter
    def event_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighActionOutputReference, "event_action").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notify")
    def notify(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "notify"))

    @notify.setter
    def notify(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighActionOutputReference, "notify").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notify", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighActionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction",
    jsii_struct_bases=[],
    name_mapping={"event_action": "eventAction", "notify": "notify"},
)
class CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction:
    def __init__(
        self,
        *,
        event_action: builtins.str,
        notify: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param event_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.
        :param notify: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify CognitoRiskConfiguration#notify}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction.__init__)
            check_type(argname="argument event_action", value=event_action, expected_type=type_hints["event_action"])
            check_type(argname="argument notify", value=notify, expected_type=type_hints["notify"])
        self._values: typing.Dict[str, typing.Any] = {
            "event_action": event_action,
            "notify": notify,
        }

    @builtins.property
    def event_action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.'''
        result = self._values.get("event_action")
        assert result is not None, "Required property 'event_action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def notify(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify CognitoRiskConfiguration#notify}.'''
        result = self._values.get("notify")
        assert result is not None, "Required property 'notify' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowActionOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowActionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventActionInput")
    def event_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notifyInput")
    def notify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "notifyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventAction")
    def event_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventAction"))

    @event_action.setter
    def event_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowActionOutputReference, "event_action").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notify")
    def notify(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "notify"))

    @notify.setter
    def notify(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowActionOutputReference, "notify").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notify", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowActionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction",
    jsii_struct_bases=[],
    name_mapping={"event_action": "eventAction", "notify": "notify"},
)
class CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction:
    def __init__(
        self,
        *,
        event_action: builtins.str,
        notify: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param event_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.
        :param notify: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify CognitoRiskConfiguration#notify}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction.__init__)
            check_type(argname="argument event_action", value=event_action, expected_type=type_hints["event_action"])
            check_type(argname="argument notify", value=notify, expected_type=type_hints["notify"])
        self._values: typing.Dict[str, typing.Any] = {
            "event_action": event_action,
            "notify": notify,
        }

    @builtins.property
    def event_action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.'''
        result = self._values.get("event_action")
        assert result is not None, "Required property 'event_action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def notify(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify CognitoRiskConfiguration#notify}.'''
        result = self._values.get("notify")
        assert result is not None, "Required property 'notify' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumActionOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumActionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventActionInput")
    def event_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notifyInput")
    def notify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "notifyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventAction")
    def event_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventAction"))

    @event_action.setter
    def event_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumActionOutputReference, "event_action").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notify")
    def notify(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "notify"))

    @notify.setter
    def notify(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumActionOutputReference, "notify").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notify", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumActionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putHighAction")
    def put_high_action(
        self,
        *,
        event_action: builtins.str,
        notify: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param event_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.
        :param notify: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify CognitoRiskConfiguration#notify}.
        '''
        value = CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction(
            event_action=event_action, notify=notify
        )

        return typing.cast(None, jsii.invoke(self, "putHighAction", [value]))

    @jsii.member(jsii_name="putLowAction")
    def put_low_action(
        self,
        *,
        event_action: builtins.str,
        notify: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param event_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.
        :param notify: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify CognitoRiskConfiguration#notify}.
        '''
        value = CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction(
            event_action=event_action, notify=notify
        )

        return typing.cast(None, jsii.invoke(self, "putLowAction", [value]))

    @jsii.member(jsii_name="putMediumAction")
    def put_medium_action(
        self,
        *,
        event_action: builtins.str,
        notify: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param event_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.
        :param notify: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#notify CognitoRiskConfiguration#notify}.
        '''
        value = CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction(
            event_action=event_action, notify=notify
        )

        return typing.cast(None, jsii.invoke(self, "putMediumAction", [value]))

    @jsii.member(jsii_name="resetHighAction")
    def reset_high_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHighAction", []))

    @jsii.member(jsii_name="resetLowAction")
    def reset_low_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLowAction", []))

    @jsii.member(jsii_name="resetMediumAction")
    def reset_medium_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMediumAction", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="highAction")
    def high_action(
        self,
    ) -> CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighActionOutputReference:
        return typing.cast(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighActionOutputReference, jsii.get(self, "highAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lowAction")
    def low_action(
        self,
    ) -> CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowActionOutputReference:
        return typing.cast(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowActionOutputReference, jsii.get(self, "lowAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mediumAction")
    def medium_action(
        self,
    ) -> CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumActionOutputReference:
        return typing.cast(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumActionOutputReference, jsii.get(self, "mediumAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="highActionInput")
    def high_action_input(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction], jsii.get(self, "highActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lowActionInput")
    def low_action_input(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction], jsii.get(self, "lowActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mediumActionInput")
    def medium_action_input(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction], jsii.get(self, "mediumActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "source_arn": "sourceArn",
        "block_email": "blockEmail",
        "from_": "from",
        "mfa_email": "mfaEmail",
        "no_action_email": "noActionEmail",
        "reply_to": "replyTo",
    },
)
class CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration:
    def __init__(
        self,
        *,
        source_arn: builtins.str,
        block_email: typing.Optional[typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail", typing.Dict[str, typing.Any]]] = None,
        from_: typing.Optional[builtins.str] = None,
        mfa_email: typing.Optional[typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail", typing.Dict[str, typing.Any]]] = None,
        no_action_email: typing.Optional[typing.Union["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail", typing.Dict[str, typing.Any]]] = None,
        reply_to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#source_arn CognitoRiskConfiguration#source_arn}.
        :param block_email: block_email block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#block_email CognitoRiskConfiguration#block_email}
        :param from_: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#from CognitoRiskConfiguration#from}.
        :param mfa_email: mfa_email block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#mfa_email CognitoRiskConfiguration#mfa_email}
        :param no_action_email: no_action_email block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#no_action_email CognitoRiskConfiguration#no_action_email}
        :param reply_to: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#reply_to CognitoRiskConfiguration#reply_to}.
        '''
        if isinstance(block_email, dict):
            block_email = CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail(**block_email)
        if isinstance(mfa_email, dict):
            mfa_email = CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail(**mfa_email)
        if isinstance(no_action_email, dict):
            no_action_email = CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail(**no_action_email)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration.__init__)
            check_type(argname="argument source_arn", value=source_arn, expected_type=type_hints["source_arn"])
            check_type(argname="argument block_email", value=block_email, expected_type=type_hints["block_email"])
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument mfa_email", value=mfa_email, expected_type=type_hints["mfa_email"])
            check_type(argname="argument no_action_email", value=no_action_email, expected_type=type_hints["no_action_email"])
            check_type(argname="argument reply_to", value=reply_to, expected_type=type_hints["reply_to"])
        self._values: typing.Dict[str, typing.Any] = {
            "source_arn": source_arn,
        }
        if block_email is not None:
            self._values["block_email"] = block_email
        if from_ is not None:
            self._values["from_"] = from_
        if mfa_email is not None:
            self._values["mfa_email"] = mfa_email
        if no_action_email is not None:
            self._values["no_action_email"] = no_action_email
        if reply_to is not None:
            self._values["reply_to"] = reply_to

    @builtins.property
    def source_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#source_arn CognitoRiskConfiguration#source_arn}.'''
        result = self._values.get("source_arn")
        assert result is not None, "Required property 'source_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def block_email(
        self,
    ) -> typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail"]:
        '''block_email block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#block_email CognitoRiskConfiguration#block_email}
        '''
        result = self._values.get("block_email")
        return typing.cast(typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail"], result)

    @builtins.property
    def from_(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#from CognitoRiskConfiguration#from}.'''
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mfa_email(
        self,
    ) -> typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail"]:
        '''mfa_email block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#mfa_email CognitoRiskConfiguration#mfa_email}
        '''
        result = self._values.get("mfa_email")
        return typing.cast(typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail"], result)

    @builtins.property
    def no_action_email(
        self,
    ) -> typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail"]:
        '''no_action_email block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#no_action_email CognitoRiskConfiguration#no_action_email}
        '''
        result = self._values.get("no_action_email")
        return typing.cast(typing.Optional["CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail"], result)

    @builtins.property
    def reply_to(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#reply_to CognitoRiskConfiguration#reply_to}.'''
        result = self._values.get("reply_to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail",
    jsii_struct_bases=[],
    name_mapping={
        "html_body": "htmlBody",
        "subject": "subject",
        "text_body": "textBody",
    },
)
class CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail:
    def __init__(
        self,
        *,
        html_body: builtins.str,
        subject: builtins.str,
        text_body: builtins.str,
    ) -> None:
        '''
        :param html_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#html_body CognitoRiskConfiguration#html_body}.
        :param subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#subject CognitoRiskConfiguration#subject}.
        :param text_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#text_body CognitoRiskConfiguration#text_body}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail.__init__)
            check_type(argname="argument html_body", value=html_body, expected_type=type_hints["html_body"])
            check_type(argname="argument subject", value=subject, expected_type=type_hints["subject"])
            check_type(argname="argument text_body", value=text_body, expected_type=type_hints["text_body"])
        self._values: typing.Dict[str, typing.Any] = {
            "html_body": html_body,
            "subject": subject,
            "text_body": text_body,
        }

    @builtins.property
    def html_body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#html_body CognitoRiskConfiguration#html_body}.'''
        result = self._values.get("html_body")
        assert result is not None, "Required property 'html_body' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subject(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#subject CognitoRiskConfiguration#subject}.'''
        result = self._values.get("subject")
        assert result is not None, "Required property 'subject' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def text_body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#text_body CognitoRiskConfiguration#text_body}.'''
        result = self._values.get("text_body")
        assert result is not None, "Required property 'text_body' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmailOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmailOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmailOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlBodyInput")
    def html_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "htmlBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subjectInput")
    def subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="textBodyInput")
    def text_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "textBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlBody")
    def html_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlBody"))

    @html_body.setter
    def html_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmailOutputReference, "html_body").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "htmlBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subject")
    def subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subject"))

    @subject.setter
    def subject(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmailOutputReference, "subject").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="textBody")
    def text_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "textBody"))

    @text_body.setter
    def text_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmailOutputReference, "text_body").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "textBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmailOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail",
    jsii_struct_bases=[],
    name_mapping={
        "html_body": "htmlBody",
        "subject": "subject",
        "text_body": "textBody",
    },
)
class CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail:
    def __init__(
        self,
        *,
        html_body: builtins.str,
        subject: builtins.str,
        text_body: builtins.str,
    ) -> None:
        '''
        :param html_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#html_body CognitoRiskConfiguration#html_body}.
        :param subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#subject CognitoRiskConfiguration#subject}.
        :param text_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#text_body CognitoRiskConfiguration#text_body}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail.__init__)
            check_type(argname="argument html_body", value=html_body, expected_type=type_hints["html_body"])
            check_type(argname="argument subject", value=subject, expected_type=type_hints["subject"])
            check_type(argname="argument text_body", value=text_body, expected_type=type_hints["text_body"])
        self._values: typing.Dict[str, typing.Any] = {
            "html_body": html_body,
            "subject": subject,
            "text_body": text_body,
        }

    @builtins.property
    def html_body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#html_body CognitoRiskConfiguration#html_body}.'''
        result = self._values.get("html_body")
        assert result is not None, "Required property 'html_body' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subject(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#subject CognitoRiskConfiguration#subject}.'''
        result = self._values.get("subject")
        assert result is not None, "Required property 'subject' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def text_body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#text_body CognitoRiskConfiguration#text_body}.'''
        result = self._values.get("text_body")
        assert result is not None, "Required property 'text_body' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmailOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmailOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmailOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlBodyInput")
    def html_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "htmlBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subjectInput")
    def subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="textBodyInput")
    def text_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "textBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlBody")
    def html_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlBody"))

    @html_body.setter
    def html_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmailOutputReference, "html_body").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "htmlBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subject")
    def subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subject"))

    @subject.setter
    def subject(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmailOutputReference, "subject").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="textBody")
    def text_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "textBody"))

    @text_body.setter
    def text_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmailOutputReference, "text_body").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "textBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmailOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail",
    jsii_struct_bases=[],
    name_mapping={
        "html_body": "htmlBody",
        "subject": "subject",
        "text_body": "textBody",
    },
)
class CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail:
    def __init__(
        self,
        *,
        html_body: builtins.str,
        subject: builtins.str,
        text_body: builtins.str,
    ) -> None:
        '''
        :param html_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#html_body CognitoRiskConfiguration#html_body}.
        :param subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#subject CognitoRiskConfiguration#subject}.
        :param text_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#text_body CognitoRiskConfiguration#text_body}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail.__init__)
            check_type(argname="argument html_body", value=html_body, expected_type=type_hints["html_body"])
            check_type(argname="argument subject", value=subject, expected_type=type_hints["subject"])
            check_type(argname="argument text_body", value=text_body, expected_type=type_hints["text_body"])
        self._values: typing.Dict[str, typing.Any] = {
            "html_body": html_body,
            "subject": subject,
            "text_body": text_body,
        }

    @builtins.property
    def html_body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#html_body CognitoRiskConfiguration#html_body}.'''
        result = self._values.get("html_body")
        assert result is not None, "Required property 'html_body' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subject(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#subject CognitoRiskConfiguration#subject}.'''
        result = self._values.get("subject")
        assert result is not None, "Required property 'subject' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def text_body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#text_body CognitoRiskConfiguration#text_body}.'''
        result = self._values.get("text_body")
        assert result is not None, "Required property 'text_body' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmailOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmailOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmailOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlBodyInput")
    def html_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "htmlBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subjectInput")
    def subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="textBodyInput")
    def text_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "textBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlBody")
    def html_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "htmlBody"))

    @html_body.setter
    def html_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmailOutputReference, "html_body").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "htmlBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subject")
    def subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subject"))

    @subject.setter
    def subject(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmailOutputReference, "subject").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="textBody")
    def text_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "textBody"))

    @text_body.setter
    def text_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmailOutputReference, "text_body").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "textBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmailOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putBlockEmail")
    def put_block_email(
        self,
        *,
        html_body: builtins.str,
        subject: builtins.str,
        text_body: builtins.str,
    ) -> None:
        '''
        :param html_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#html_body CognitoRiskConfiguration#html_body}.
        :param subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#subject CognitoRiskConfiguration#subject}.
        :param text_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#text_body CognitoRiskConfiguration#text_body}.
        '''
        value = CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail(
            html_body=html_body, subject=subject, text_body=text_body
        )

        return typing.cast(None, jsii.invoke(self, "putBlockEmail", [value]))

    @jsii.member(jsii_name="putMfaEmail")
    def put_mfa_email(
        self,
        *,
        html_body: builtins.str,
        subject: builtins.str,
        text_body: builtins.str,
    ) -> None:
        '''
        :param html_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#html_body CognitoRiskConfiguration#html_body}.
        :param subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#subject CognitoRiskConfiguration#subject}.
        :param text_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#text_body CognitoRiskConfiguration#text_body}.
        '''
        value = CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail(
            html_body=html_body, subject=subject, text_body=text_body
        )

        return typing.cast(None, jsii.invoke(self, "putMfaEmail", [value]))

    @jsii.member(jsii_name="putNoActionEmail")
    def put_no_action_email(
        self,
        *,
        html_body: builtins.str,
        subject: builtins.str,
        text_body: builtins.str,
    ) -> None:
        '''
        :param html_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#html_body CognitoRiskConfiguration#html_body}.
        :param subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#subject CognitoRiskConfiguration#subject}.
        :param text_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#text_body CognitoRiskConfiguration#text_body}.
        '''
        value = CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail(
            html_body=html_body, subject=subject, text_body=text_body
        )

        return typing.cast(None, jsii.invoke(self, "putNoActionEmail", [value]))

    @jsii.member(jsii_name="resetBlockEmail")
    def reset_block_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockEmail", []))

    @jsii.member(jsii_name="resetFrom")
    def reset_from(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrom", []))

    @jsii.member(jsii_name="resetMfaEmail")
    def reset_mfa_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMfaEmail", []))

    @jsii.member(jsii_name="resetNoActionEmail")
    def reset_no_action_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoActionEmail", []))

    @jsii.member(jsii_name="resetReplyTo")
    def reset_reply_to(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplyTo", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockEmail")
    def block_email(
        self,
    ) -> CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmailOutputReference:
        return typing.cast(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmailOutputReference, jsii.get(self, "blockEmail"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mfaEmail")
    def mfa_email(
        self,
    ) -> CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmailOutputReference:
        return typing.cast(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmailOutputReference, jsii.get(self, "mfaEmail"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noActionEmail")
    def no_action_email(
        self,
    ) -> CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmailOutputReference:
        return typing.cast(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmailOutputReference, jsii.get(self, "noActionEmail"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockEmailInput")
    def block_email_input(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail], jsii.get(self, "blockEmailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromInput")
    def from_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mfaEmailInput")
    def mfa_email_input(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail], jsii.get(self, "mfaEmailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noActionEmailInput")
    def no_action_email_input(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail], jsii.get(self, "noActionEmailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replyToInput")
    def reply_to_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replyToInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceArnInput")
    def source_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="from")
    def from_(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "from"))

    @from_.setter
    def from_(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationOutputReference, "from_").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "from", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replyTo")
    def reply_to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replyTo"))

    @reply_to.setter
    def reply_to(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationOutputReference, "reply_to").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replyTo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceArn")
    def source_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceArn"))

    @source_arn.setter
    def source_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationOutputReference, "source_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoRiskConfigurationAccountTakeoverRiskConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationAccountTakeoverRiskConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationAccountTakeoverRiskConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putActions")
    def put_actions(
        self,
        *,
        high_action: typing.Optional[typing.Union[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction, typing.Dict[str, typing.Any]]] = None,
        low_action: typing.Optional[typing.Union[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction, typing.Dict[str, typing.Any]]] = None,
        medium_action: typing.Optional[typing.Union[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param high_action: high_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#high_action CognitoRiskConfiguration#high_action}
        :param low_action: low_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#low_action CognitoRiskConfiguration#low_action}
        :param medium_action: medium_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#medium_action CognitoRiskConfiguration#medium_action}
        '''
        value = CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions(
            high_action=high_action, low_action=low_action, medium_action=medium_action
        )

        return typing.cast(None, jsii.invoke(self, "putActions", [value]))

    @jsii.member(jsii_name="putNotifyConfiguration")
    def put_notify_configuration(
        self,
        *,
        source_arn: builtins.str,
        block_email: typing.Optional[typing.Union[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail, typing.Dict[str, typing.Any]]] = None,
        from_: typing.Optional[builtins.str] = None,
        mfa_email: typing.Optional[typing.Union[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail, typing.Dict[str, typing.Any]]] = None,
        no_action_email: typing.Optional[typing.Union[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail, typing.Dict[str, typing.Any]]] = None,
        reply_to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#source_arn CognitoRiskConfiguration#source_arn}.
        :param block_email: block_email block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#block_email CognitoRiskConfiguration#block_email}
        :param from_: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#from CognitoRiskConfiguration#from}.
        :param mfa_email: mfa_email block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#mfa_email CognitoRiskConfiguration#mfa_email}
        :param no_action_email: no_action_email block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#no_action_email CognitoRiskConfiguration#no_action_email}
        :param reply_to: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#reply_to CognitoRiskConfiguration#reply_to}.
        '''
        value = CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration(
            source_arn=source_arn,
            block_email=block_email,
            from_=from_,
            mfa_email=mfa_email,
            no_action_email=no_action_email,
            reply_to=reply_to,
        )

        return typing.cast(None, jsii.invoke(self, "putNotifyConfiguration", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(
        self,
    ) -> CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsOutputReference:
        return typing.cast(CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsOutputReference, jsii.get(self, "actions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notifyConfiguration")
    def notify_configuration(
        self,
    ) -> CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationOutputReference:
        return typing.cast(CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationOutputReference, jsii.get(self, "notifyConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionsInput")
    def actions_input(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions], jsii.get(self, "actionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notifyConfigurationInput")
    def notify_configuration_input(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration], jsii.get(self, "notifyConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfiguration]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationAccountTakeoverRiskConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration",
    jsii_struct_bases=[],
    name_mapping={"actions": "actions", "event_filter": "eventFilter"},
)
class CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration:
    def __init__(
        self,
        *,
        actions: typing.Union["CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions", typing.Dict[str, typing.Any]],
        event_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param actions: actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#actions CognitoRiskConfiguration#actions}
        :param event_filter: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_filter CognitoRiskConfiguration#event_filter}.
        '''
        if isinstance(actions, dict):
            actions = CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions(**actions)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration.__init__)
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument event_filter", value=event_filter, expected_type=type_hints["event_filter"])
        self._values: typing.Dict[str, typing.Any] = {
            "actions": actions,
        }
        if event_filter is not None:
            self._values["event_filter"] = event_filter

    @builtins.property
    def actions(
        self,
    ) -> "CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions":
        '''actions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#actions CognitoRiskConfiguration#actions}
        '''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast("CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions", result)

    @builtins.property
    def event_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_filter CognitoRiskConfiguration#event_filter}.'''
        result = self._values.get("event_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions",
    jsii_struct_bases=[],
    name_mapping={"event_action": "eventAction"},
)
class CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions:
    def __init__(self, *, event_action: builtins.str) -> None:
        '''
        :param event_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions.__init__)
            check_type(argname="argument event_action", value=event_action, expected_type=type_hints["event_action"])
        self._values: typing.Dict[str, typing.Any] = {
            "event_action": event_action,
        }

    @builtins.property
    def event_action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.'''
        result = self._values.get("event_action")
        assert result is not None, "Required property 'event_action' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActionsOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActionsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventActionInput")
    def event_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventAction")
    def event_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventAction"))

    @event_action.setter
    def event_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActionsOutputReference, "event_action").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActionsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putActions")
    def put_actions(self, *, event_action: builtins.str) -> None:
        '''
        :param event_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#event_action CognitoRiskConfiguration#event_action}.
        '''
        value = CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions(
            event_action=event_action
        )

        return typing.cast(None, jsii.invoke(self, "putActions", [value]))

    @jsii.member(jsii_name="resetEventFilter")
    def reset_event_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventFilter", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(
        self,
    ) -> CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActionsOutputReference:
        return typing.cast(CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActionsOutputReference, jsii.get(self, "actions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionsInput")
    def actions_input(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions], jsii.get(self, "actionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventFilterInput")
    def event_filter_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventFilter")
    def event_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventFilter"))

    @event_filter.setter
    def event_filter(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationOutputReference, "event_filter").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventFilter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "user_pool_id": "userPoolId",
        "account_takeover_risk_configuration": "accountTakeoverRiskConfiguration",
        "client_id": "clientId",
        "compromised_credentials_risk_configuration": "compromisedCredentialsRiskConfiguration",
        "id": "id",
        "risk_exception_configuration": "riskExceptionConfiguration",
    },
)
class CognitoRiskConfigurationConfig(cdktf.TerraformMetaArguments):
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
        user_pool_id: builtins.str,
        account_takeover_risk_configuration: typing.Optional[typing.Union[CognitoRiskConfigurationAccountTakeoverRiskConfiguration, typing.Dict[str, typing.Any]]] = None,
        client_id: typing.Optional[builtins.str] = None,
        compromised_credentials_risk_configuration: typing.Optional[typing.Union[CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration, typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        risk_exception_configuration: typing.Optional[typing.Union["CognitoRiskConfigurationRiskExceptionConfiguration", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#user_pool_id CognitoRiskConfiguration#user_pool_id}.
        :param account_takeover_risk_configuration: account_takeover_risk_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#account_takeover_risk_configuration CognitoRiskConfiguration#account_takeover_risk_configuration}
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#client_id CognitoRiskConfiguration#client_id}.
        :param compromised_credentials_risk_configuration: compromised_credentials_risk_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#compromised_credentials_risk_configuration CognitoRiskConfiguration#compromised_credentials_risk_configuration}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#id CognitoRiskConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param risk_exception_configuration: risk_exception_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#risk_exception_configuration CognitoRiskConfiguration#risk_exception_configuration}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(account_takeover_risk_configuration, dict):
            account_takeover_risk_configuration = CognitoRiskConfigurationAccountTakeoverRiskConfiguration(**account_takeover_risk_configuration)
        if isinstance(compromised_credentials_risk_configuration, dict):
            compromised_credentials_risk_configuration = CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration(**compromised_credentials_risk_configuration)
        if isinstance(risk_exception_configuration, dict):
            risk_exception_configuration = CognitoRiskConfigurationRiskExceptionConfiguration(**risk_exception_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument account_takeover_risk_configuration", value=account_takeover_risk_configuration, expected_type=type_hints["account_takeover_risk_configuration"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument compromised_credentials_risk_configuration", value=compromised_credentials_risk_configuration, expected_type=type_hints["compromised_credentials_risk_configuration"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument risk_exception_configuration", value=risk_exception_configuration, expected_type=type_hints["risk_exception_configuration"])
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool_id": user_pool_id,
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
        if account_takeover_risk_configuration is not None:
            self._values["account_takeover_risk_configuration"] = account_takeover_risk_configuration
        if client_id is not None:
            self._values["client_id"] = client_id
        if compromised_credentials_risk_configuration is not None:
            self._values["compromised_credentials_risk_configuration"] = compromised_credentials_risk_configuration
        if id is not None:
            self._values["id"] = id
        if risk_exception_configuration is not None:
            self._values["risk_exception_configuration"] = risk_exception_configuration

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
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#user_pool_id CognitoRiskConfiguration#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_takeover_risk_configuration(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfiguration]:
        '''account_takeover_risk_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#account_takeover_risk_configuration CognitoRiskConfiguration#account_takeover_risk_configuration}
        '''
        result = self._values.get("account_takeover_risk_configuration")
        return typing.cast(typing.Optional[CognitoRiskConfigurationAccountTakeoverRiskConfiguration], result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#client_id CognitoRiskConfiguration#client_id}.'''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compromised_credentials_risk_configuration(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration]:
        '''compromised_credentials_risk_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#compromised_credentials_risk_configuration CognitoRiskConfiguration#compromised_credentials_risk_configuration}
        '''
        result = self._values.get("compromised_credentials_risk_configuration")
        return typing.cast(typing.Optional[CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#id CognitoRiskConfiguration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def risk_exception_configuration(
        self,
    ) -> typing.Optional["CognitoRiskConfigurationRiskExceptionConfiguration"]:
        '''risk_exception_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#risk_exception_configuration CognitoRiskConfiguration#risk_exception_configuration}
        '''
        result = self._values.get("risk_exception_configuration")
        return typing.cast(typing.Optional["CognitoRiskConfigurationRiskExceptionConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationRiskExceptionConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "blocked_ip_range_list": "blockedIpRangeList",
        "skipped_ip_range_list": "skippedIpRangeList",
    },
)
class CognitoRiskConfigurationRiskExceptionConfiguration:
    def __init__(
        self,
        *,
        blocked_ip_range_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        skipped_ip_range_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param blocked_ip_range_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#blocked_ip_range_list CognitoRiskConfiguration#blocked_ip_range_list}.
        :param skipped_ip_range_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#skipped_ip_range_list CognitoRiskConfiguration#skipped_ip_range_list}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoRiskConfigurationRiskExceptionConfiguration.__init__)
            check_type(argname="argument blocked_ip_range_list", value=blocked_ip_range_list, expected_type=type_hints["blocked_ip_range_list"])
            check_type(argname="argument skipped_ip_range_list", value=skipped_ip_range_list, expected_type=type_hints["skipped_ip_range_list"])
        self._values: typing.Dict[str, typing.Any] = {}
        if blocked_ip_range_list is not None:
            self._values["blocked_ip_range_list"] = blocked_ip_range_list
        if skipped_ip_range_list is not None:
            self._values["skipped_ip_range_list"] = skipped_ip_range_list

    @builtins.property
    def blocked_ip_range_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#blocked_ip_range_list CognitoRiskConfiguration#blocked_ip_range_list}.'''
        result = self._values.get("blocked_ip_range_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def skipped_ip_range_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_risk_configuration#skipped_ip_range_list CognitoRiskConfiguration#skipped_ip_range_list}.'''
        result = self._values.get("skipped_ip_range_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoRiskConfigurationRiskExceptionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoRiskConfigurationRiskExceptionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoRiskConfigurationRiskExceptionConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(CognitoRiskConfigurationRiskExceptionConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBlockedIpRangeList")
    def reset_blocked_ip_range_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockedIpRangeList", []))

    @jsii.member(jsii_name="resetSkippedIpRangeList")
    def reset_skipped_ip_range_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkippedIpRangeList", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockedIpRangeListInput")
    def blocked_ip_range_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "blockedIpRangeListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skippedIpRangeListInput")
    def skipped_ip_range_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "skippedIpRangeListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockedIpRangeList")
    def blocked_ip_range_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "blockedIpRangeList"))

    @blocked_ip_range_list.setter
    def blocked_ip_range_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationRiskExceptionConfigurationOutputReference, "blocked_ip_range_list").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockedIpRangeList", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skippedIpRangeList")
    def skipped_ip_range_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "skippedIpRangeList"))

    @skipped_ip_range_list.setter
    def skipped_ip_range_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationRiskExceptionConfigurationOutputReference, "skipped_ip_range_list").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skippedIpRangeList", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoRiskConfigurationRiskExceptionConfiguration]:
        return typing.cast(typing.Optional[CognitoRiskConfigurationRiskExceptionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoRiskConfigurationRiskExceptionConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoRiskConfigurationRiskExceptionConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoUser(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user aws_cognito_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        username: builtins.str,
        user_pool_id: builtins.str,
        attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        client_metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        desired_delivery_mediums: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        force_alias_creation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        message_action: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        temporary_password: typing.Optional[builtins.str] = None,
        validation_data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user aws_cognito_user} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#username CognitoUser#username}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#user_pool_id CognitoUser#user_pool_id}.
        :param attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#attributes CognitoUser#attributes}.
        :param client_metadata: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#client_metadata CognitoUser#client_metadata}.
        :param desired_delivery_mediums: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#desired_delivery_mediums CognitoUser#desired_delivery_mediums}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#enabled CognitoUser#enabled}.
        :param force_alias_creation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#force_alias_creation CognitoUser#force_alias_creation}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#id CognitoUser#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param message_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#message_action CognitoUser#message_action}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#password CognitoUser#password}.
        :param temporary_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#temporary_password CognitoUser#temporary_password}.
        :param validation_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#validation_data CognitoUser#validation_data}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUser.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoUserConfig(
            username=username,
            user_pool_id=user_pool_id,
            attributes=attributes,
            client_metadata=client_metadata,
            desired_delivery_mediums=desired_delivery_mediums,
            enabled=enabled,
            force_alias_creation=force_alias_creation,
            id=id,
            message_action=message_action,
            password=password,
            temporary_password=temporary_password,
            validation_data=validation_data,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetAttributes")
    def reset_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttributes", []))

    @jsii.member(jsii_name="resetClientMetadata")
    def reset_client_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientMetadata", []))

    @jsii.member(jsii_name="resetDesiredDeliveryMediums")
    def reset_desired_delivery_mediums(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDesiredDeliveryMediums", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetForceAliasCreation")
    def reset_force_alias_creation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceAliasCreation", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMessageAction")
    def reset_message_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageAction", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetTemporaryPassword")
    def reset_temporary_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemporaryPassword", []))

    @jsii.member(jsii_name="resetValidationData")
    def reset_validation_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValidationData", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationDate")
    def creation_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedDate")
    def last_modified_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mfaSettingList")
    def mfa_setting_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "mfaSettingList"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMfaSetting")
    def preferred_mfa_setting(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredMfaSetting"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sub")
    def sub(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sub"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributesInput")
    def attributes_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "attributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientMetadataInput")
    def client_metadata_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "clientMetadataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="desiredDeliveryMediumsInput")
    def desired_delivery_mediums_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "desiredDeliveryMediumsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceAliasCreationInput")
    def force_alias_creation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceAliasCreationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageActionInput")
    def message_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="temporaryPasswordInput")
    def temporary_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "temporaryPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validationDataInput")
    def validation_data_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "validationDataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributes")
    def attributes(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "attributes"))

    @attributes.setter
    def attributes(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "attributes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientMetadata")
    def client_metadata(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "clientMetadata"))

    @client_metadata.setter
    def client_metadata(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "client_metadata").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientMetadata", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="desiredDeliveryMediums")
    def desired_delivery_mediums(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "desiredDeliveryMediums"))

    @desired_delivery_mediums.setter
    def desired_delivery_mediums(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "desired_delivery_mediums").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "desiredDeliveryMediums", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "enabled").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceAliasCreation")
    def force_alias_creation(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceAliasCreation"))

    @force_alias_creation.setter
    def force_alias_creation(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "force_alias_creation").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceAliasCreation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageAction")
    def message_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageAction"))

    @message_action.setter
    def message_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "message_action").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "password").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="temporaryPassword")
    def temporary_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "temporaryPassword"))

    @temporary_password.setter
    def temporary_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "temporary_password").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "temporaryPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "username").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validationData")
    def validation_data(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "validationData"))

    @validation_data.setter
    def validation_data(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUser, "validation_data").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "validationData", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "username": "username",
        "user_pool_id": "userPoolId",
        "attributes": "attributes",
        "client_metadata": "clientMetadata",
        "desired_delivery_mediums": "desiredDeliveryMediums",
        "enabled": "enabled",
        "force_alias_creation": "forceAliasCreation",
        "id": "id",
        "message_action": "messageAction",
        "password": "password",
        "temporary_password": "temporaryPassword",
        "validation_data": "validationData",
    },
)
class CognitoUserConfig(cdktf.TerraformMetaArguments):
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
        username: builtins.str,
        user_pool_id: builtins.str,
        attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        client_metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        desired_delivery_mediums: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        force_alias_creation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        message_action: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        temporary_password: typing.Optional[builtins.str] = None,
        validation_data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#username CognitoUser#username}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#user_pool_id CognitoUser#user_pool_id}.
        :param attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#attributes CognitoUser#attributes}.
        :param client_metadata: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#client_metadata CognitoUser#client_metadata}.
        :param desired_delivery_mediums: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#desired_delivery_mediums CognitoUser#desired_delivery_mediums}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#enabled CognitoUser#enabled}.
        :param force_alias_creation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#force_alias_creation CognitoUser#force_alias_creation}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#id CognitoUser#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param message_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#message_action CognitoUser#message_action}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#password CognitoUser#password}.
        :param temporary_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#temporary_password CognitoUser#temporary_password}.
        :param validation_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#validation_data CognitoUser#validation_data}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument attributes", value=attributes, expected_type=type_hints["attributes"])
            check_type(argname="argument client_metadata", value=client_metadata, expected_type=type_hints["client_metadata"])
            check_type(argname="argument desired_delivery_mediums", value=desired_delivery_mediums, expected_type=type_hints["desired_delivery_mediums"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument force_alias_creation", value=force_alias_creation, expected_type=type_hints["force_alias_creation"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument message_action", value=message_action, expected_type=type_hints["message_action"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument temporary_password", value=temporary_password, expected_type=type_hints["temporary_password"])
            check_type(argname="argument validation_data", value=validation_data, expected_type=type_hints["validation_data"])
        self._values: typing.Dict[str, typing.Any] = {
            "username": username,
            "user_pool_id": user_pool_id,
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
        if attributes is not None:
            self._values["attributes"] = attributes
        if client_metadata is not None:
            self._values["client_metadata"] = client_metadata
        if desired_delivery_mediums is not None:
            self._values["desired_delivery_mediums"] = desired_delivery_mediums
        if enabled is not None:
            self._values["enabled"] = enabled
        if force_alias_creation is not None:
            self._values["force_alias_creation"] = force_alias_creation
        if id is not None:
            self._values["id"] = id
        if message_action is not None:
            self._values["message_action"] = message_action
        if password is not None:
            self._values["password"] = password
        if temporary_password is not None:
            self._values["temporary_password"] = temporary_password
        if validation_data is not None:
            self._values["validation_data"] = validation_data

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
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#username CognitoUser#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#user_pool_id CognitoUser#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attributes(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#attributes CognitoUser#attributes}.'''
        result = self._values.get("attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def client_metadata(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#client_metadata CognitoUser#client_metadata}.'''
        result = self._values.get("client_metadata")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def desired_delivery_mediums(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#desired_delivery_mediums CognitoUser#desired_delivery_mediums}.'''
        result = self._values.get("desired_delivery_mediums")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#enabled CognitoUser#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def force_alias_creation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#force_alias_creation CognitoUser#force_alias_creation}.'''
        result = self._values.get("force_alias_creation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#id CognitoUser#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_action(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#message_action CognitoUser#message_action}.'''
        result = self._values.get("message_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#password CognitoUser#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def temporary_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#temporary_password CognitoUser#temporary_password}.'''
        result = self._values.get("temporary_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def validation_data(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user#validation_data CognitoUser#validation_data}.'''
        result = self._values.get("validation_data")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group aws_cognito_user_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        user_pool_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        precedence: typing.Optional[jsii.Number] = None,
        role_arn: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group aws_cognito_user_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#name CognitoUserGroup#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#user_pool_id CognitoUserGroup#user_pool_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#description CognitoUserGroup#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#id CognitoUserGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param precedence: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#precedence CognitoUserGroup#precedence}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#role_arn CognitoUserGroup#role_arn}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserGroup.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoUserGroupConfig(
            name=name,
            user_pool_id=user_pool_id,
            description=description,
            id=id,
            precedence=precedence,
            role_arn=role_arn,
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

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPrecedence")
    def reset_precedence(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrecedence", []))

    @jsii.member(jsii_name="resetRoleArn")
    def reset_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleArn", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

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
    @jsii.member(jsii_name="precedenceInput")
    def precedence_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "precedenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserGroup, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserGroup, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserGroup, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="precedence")
    def precedence(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precedence"))

    @precedence.setter
    def precedence(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserGroup, "precedence").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "precedence", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserGroup, "role_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserGroup, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserGroupConfig",
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
        "user_pool_id": "userPoolId",
        "description": "description",
        "id": "id",
        "precedence": "precedence",
        "role_arn": "roleArn",
    },
)
class CognitoUserGroupConfig(cdktf.TerraformMetaArguments):
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
        user_pool_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        precedence: typing.Optional[jsii.Number] = None,
        role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#name CognitoUserGroup#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#user_pool_id CognitoUserGroup#user_pool_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#description CognitoUserGroup#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#id CognitoUserGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param precedence: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#precedence CognitoUserGroup#precedence}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#role_arn CognitoUserGroup#role_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserGroupConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument precedence", value=precedence, expected_type=type_hints["precedence"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "user_pool_id": user_pool_id,
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
        if precedence is not None:
            self._values["precedence"] = precedence
        if role_arn is not None:
            self._values["role_arn"] = role_arn

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#name CognitoUserGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#user_pool_id CognitoUserGroup#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#description CognitoUserGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#id CognitoUserGroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def precedence(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#precedence CognitoUserGroup#precedence}.'''
        result = self._values.get("precedence")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#role_arn CognitoUserGroup#role_arn}.'''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserInGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserInGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group aws_cognito_user_in_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        group_name: builtins.str,
        username: builtins.str,
        user_pool_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group aws_cognito_user_in_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#group_name CognitoUserInGroup#group_name}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#username CognitoUserInGroup#username}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#user_pool_id CognitoUserInGroup#user_pool_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#id CognitoUserInGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserInGroup.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoUserInGroupConfig(
            group_name=group_name,
            username=username,
            user_pool_id=user_pool_id,
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
    @jsii.member(jsii_name="groupNameInput")
    def group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupName"))

    @group_name.setter
    def group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserInGroup, "group_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserInGroup, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserInGroup, "username").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserInGroup, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserInGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "group_name": "groupName",
        "username": "username",
        "user_pool_id": "userPoolId",
        "id": "id",
    },
)
class CognitoUserInGroupConfig(cdktf.TerraformMetaArguments):
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
        group_name: builtins.str,
        username: builtins.str,
        user_pool_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#group_name CognitoUserInGroup#group_name}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#username CognitoUserInGroup#username}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#user_pool_id CognitoUserInGroup#user_pool_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#id CognitoUserInGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserInGroupConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument group_name", value=group_name, expected_type=type_hints["group_name"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "group_name": group_name,
            "username": username,
            "user_pool_id": user_pool_id,
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
    def group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#group_name CognitoUserInGroup#group_name}.'''
        result = self._values.get("group_name")
        assert result is not None, "Required property 'group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#username CognitoUserInGroup#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#user_pool_id CognitoUserInGroup#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_in_group#id CognitoUserInGroup#id}.

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
        return "CognitoUserInGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPool(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPool",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool aws_cognito_user_pool}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        account_recovery_setting: typing.Optional[typing.Union["CognitoUserPoolAccountRecoverySetting", typing.Dict[str, typing.Any]]] = None,
        admin_create_user_config: typing.Optional[typing.Union["CognitoUserPoolAdminCreateUserConfig", typing.Dict[str, typing.Any]]] = None,
        alias_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_verified_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        device_configuration: typing.Optional[typing.Union["CognitoUserPoolDeviceConfiguration", typing.Dict[str, typing.Any]]] = None,
        email_configuration: typing.Optional[typing.Union["CognitoUserPoolEmailConfiguration", typing.Dict[str, typing.Any]]] = None,
        email_verification_message: typing.Optional[builtins.str] = None,
        email_verification_subject: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        lambda_config: typing.Optional[typing.Union["CognitoUserPoolLambdaConfig", typing.Dict[str, typing.Any]]] = None,
        mfa_configuration: typing.Optional[builtins.str] = None,
        password_policy: typing.Optional[typing.Union["CognitoUserPoolPasswordPolicy", typing.Dict[str, typing.Any]]] = None,
        schema: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoUserPoolSchema", typing.Dict[str, typing.Any]]]]] = None,
        sms_authentication_message: typing.Optional[builtins.str] = None,
        sms_configuration: typing.Optional[typing.Union["CognitoUserPoolSmsConfiguration", typing.Dict[str, typing.Any]]] = None,
        sms_verification_message: typing.Optional[builtins.str] = None,
        software_token_mfa_configuration: typing.Optional[typing.Union["CognitoUserPoolSoftwareTokenMfaConfiguration", typing.Dict[str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        username_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        username_configuration: typing.Optional[typing.Union["CognitoUserPoolUsernameConfiguration", typing.Dict[str, typing.Any]]] = None,
        user_pool_add_ons: typing.Optional[typing.Union["CognitoUserPoolUserPoolAddOns", typing.Dict[str, typing.Any]]] = None,
        verification_message_template: typing.Optional[typing.Union["CognitoUserPoolVerificationMessageTemplate", typing.Dict[str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool aws_cognito_user_pool} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.
        :param account_recovery_setting: account_recovery_setting block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#account_recovery_setting CognitoUserPool#account_recovery_setting}
        :param admin_create_user_config: admin_create_user_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#admin_create_user_config CognitoUserPool#admin_create_user_config}
        :param alias_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#alias_attributes CognitoUserPool#alias_attributes}.
        :param auto_verified_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#auto_verified_attributes CognitoUserPool#auto_verified_attributes}.
        :param device_configuration: device_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_configuration CognitoUserPool#device_configuration}
        :param email_configuration: email_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_configuration CognitoUserPool#email_configuration}
        :param email_verification_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_message CognitoUserPool#email_verification_message}.
        :param email_verification_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_subject CognitoUserPool#email_verification_subject}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#id CognitoUserPool#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param lambda_config: lambda_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_config CognitoUserPool#lambda_config}
        :param mfa_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#mfa_configuration CognitoUserPool#mfa_configuration}.
        :param password_policy: password_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#password_policy CognitoUserPool#password_policy}
        :param schema: schema block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#schema CognitoUserPool#schema}
        :param sms_authentication_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_authentication_message CognitoUserPool#sms_authentication_message}.
        :param sms_configuration: sms_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_configuration CognitoUserPool#sms_configuration}
        :param sms_verification_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_verification_message CognitoUserPool#sms_verification_message}.
        :param software_token_mfa_configuration: software_token_mfa_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#software_token_mfa_configuration CognitoUserPool#software_token_mfa_configuration}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags CognitoUserPool#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags_all CognitoUserPool#tags_all}.
        :param username_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_attributes CognitoUserPool#username_attributes}.
        :param username_configuration: username_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_configuration CognitoUserPool#username_configuration}
        :param user_pool_add_ons: user_pool_add_ons block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_pool_add_ons CognitoUserPool#user_pool_add_ons}
        :param verification_message_template: verification_message_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verification_message_template CognitoUserPool#verification_message_template}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPool.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoUserPoolConfig(
            name=name,
            account_recovery_setting=account_recovery_setting,
            admin_create_user_config=admin_create_user_config,
            alias_attributes=alias_attributes,
            auto_verified_attributes=auto_verified_attributes,
            device_configuration=device_configuration,
            email_configuration=email_configuration,
            email_verification_message=email_verification_message,
            email_verification_subject=email_verification_subject,
            id=id,
            lambda_config=lambda_config,
            mfa_configuration=mfa_configuration,
            password_policy=password_policy,
            schema=schema,
            sms_authentication_message=sms_authentication_message,
            sms_configuration=sms_configuration,
            sms_verification_message=sms_verification_message,
            software_token_mfa_configuration=software_token_mfa_configuration,
            tags=tags,
            tags_all=tags_all,
            username_attributes=username_attributes,
            username_configuration=username_configuration,
            user_pool_add_ons=user_pool_add_ons,
            verification_message_template=verification_message_template,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putAccountRecoverySetting")
    def put_account_recovery_setting(
        self,
        *,
        recovery_mechanism: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoUserPoolAccountRecoverySettingRecoveryMechanism", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param recovery_mechanism: recovery_mechanism block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#recovery_mechanism CognitoUserPool#recovery_mechanism}
        '''
        value = CognitoUserPoolAccountRecoverySetting(
            recovery_mechanism=recovery_mechanism
        )

        return typing.cast(None, jsii.invoke(self, "putAccountRecoverySetting", [value]))

    @jsii.member(jsii_name="putAdminCreateUserConfig")
    def put_admin_create_user_config(
        self,
        *,
        allow_admin_create_user_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        invite_message_template: typing.Optional[typing.Union["CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param allow_admin_create_user_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#allow_admin_create_user_only CognitoUserPool#allow_admin_create_user_only}.
        :param invite_message_template: invite_message_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#invite_message_template CognitoUserPool#invite_message_template}
        '''
        value = CognitoUserPoolAdminCreateUserConfig(
            allow_admin_create_user_only=allow_admin_create_user_only,
            invite_message_template=invite_message_template,
        )

        return typing.cast(None, jsii.invoke(self, "putAdminCreateUserConfig", [value]))

    @jsii.member(jsii_name="putDeviceConfiguration")
    def put_device_configuration(
        self,
        *,
        challenge_required_on_new_device: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        device_only_remembered_on_user_prompt: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param challenge_required_on_new_device: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#challenge_required_on_new_device CognitoUserPool#challenge_required_on_new_device}.
        :param device_only_remembered_on_user_prompt: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_only_remembered_on_user_prompt CognitoUserPool#device_only_remembered_on_user_prompt}.
        '''
        value = CognitoUserPoolDeviceConfiguration(
            challenge_required_on_new_device=challenge_required_on_new_device,
            device_only_remembered_on_user_prompt=device_only_remembered_on_user_prompt,
        )

        return typing.cast(None, jsii.invoke(self, "putDeviceConfiguration", [value]))

    @jsii.member(jsii_name="putEmailConfiguration")
    def put_email_configuration(
        self,
        *,
        configuration_set: typing.Optional[builtins.str] = None,
        email_sending_account: typing.Optional[builtins.str] = None,
        from_email_address: typing.Optional[builtins.str] = None,
        reply_to_email_address: typing.Optional[builtins.str] = None,
        source_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param configuration_set: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#configuration_set CognitoUserPool#configuration_set}.
        :param email_sending_account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_sending_account CognitoUserPool#email_sending_account}.
        :param from_email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#from_email_address CognitoUserPool#from_email_address}.
        :param reply_to_email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#reply_to_email_address CognitoUserPool#reply_to_email_address}.
        :param source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#source_arn CognitoUserPool#source_arn}.
        '''
        value = CognitoUserPoolEmailConfiguration(
            configuration_set=configuration_set,
            email_sending_account=email_sending_account,
            from_email_address=from_email_address,
            reply_to_email_address=reply_to_email_address,
            source_arn=source_arn,
        )

        return typing.cast(None, jsii.invoke(self, "putEmailConfiguration", [value]))

    @jsii.member(jsii_name="putLambdaConfig")
    def put_lambda_config(
        self,
        *,
        create_auth_challenge: typing.Optional[builtins.str] = None,
        custom_email_sender: typing.Optional[typing.Union["CognitoUserPoolLambdaConfigCustomEmailSender", typing.Dict[str, typing.Any]]] = None,
        custom_message: typing.Optional[builtins.str] = None,
        custom_sms_sender: typing.Optional[typing.Union["CognitoUserPoolLambdaConfigCustomSmsSender", typing.Dict[str, typing.Any]]] = None,
        define_auth_challenge: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        post_authentication: typing.Optional[builtins.str] = None,
        post_confirmation: typing.Optional[builtins.str] = None,
        pre_authentication: typing.Optional[builtins.str] = None,
        pre_sign_up: typing.Optional[builtins.str] = None,
        pre_token_generation: typing.Optional[builtins.str] = None,
        user_migration: typing.Optional[builtins.str] = None,
        verify_auth_challenge_response: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_auth_challenge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#create_auth_challenge CognitoUserPool#create_auth_challenge}.
        :param custom_email_sender: custom_email_sender block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_email_sender CognitoUserPool#custom_email_sender}
        :param custom_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_message CognitoUserPool#custom_message}.
        :param custom_sms_sender: custom_sms_sender block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_sms_sender CognitoUserPool#custom_sms_sender}
        :param define_auth_challenge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#define_auth_challenge CognitoUserPool#define_auth_challenge}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#kms_key_id CognitoUserPool#kms_key_id}.
        :param post_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_authentication CognitoUserPool#post_authentication}.
        :param post_confirmation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_confirmation CognitoUserPool#post_confirmation}.
        :param pre_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_authentication CognitoUserPool#pre_authentication}.
        :param pre_sign_up: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_sign_up CognitoUserPool#pre_sign_up}.
        :param pre_token_generation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_token_generation CognitoUserPool#pre_token_generation}.
        :param user_migration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_migration CognitoUserPool#user_migration}.
        :param verify_auth_challenge_response: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verify_auth_challenge_response CognitoUserPool#verify_auth_challenge_response}.
        '''
        value = CognitoUserPoolLambdaConfig(
            create_auth_challenge=create_auth_challenge,
            custom_email_sender=custom_email_sender,
            custom_message=custom_message,
            custom_sms_sender=custom_sms_sender,
            define_auth_challenge=define_auth_challenge,
            kms_key_id=kms_key_id,
            post_authentication=post_authentication,
            post_confirmation=post_confirmation,
            pre_authentication=pre_authentication,
            pre_sign_up=pre_sign_up,
            pre_token_generation=pre_token_generation,
            user_migration=user_migration,
            verify_auth_challenge_response=verify_auth_challenge_response,
        )

        return typing.cast(None, jsii.invoke(self, "putLambdaConfig", [value]))

    @jsii.member(jsii_name="putPasswordPolicy")
    def put_password_policy(
        self,
        *,
        minimum_length: typing.Optional[jsii.Number] = None,
        require_lowercase: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_numbers: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_symbols: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_uppercase: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        temporary_password_validity_days: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param minimum_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#minimum_length CognitoUserPool#minimum_length}.
        :param require_lowercase: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_lowercase CognitoUserPool#require_lowercase}.
        :param require_numbers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_numbers CognitoUserPool#require_numbers}.
        :param require_symbols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_symbols CognitoUserPool#require_symbols}.
        :param require_uppercase: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_uppercase CognitoUserPool#require_uppercase}.
        :param temporary_password_validity_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#temporary_password_validity_days CognitoUserPool#temporary_password_validity_days}.
        '''
        value = CognitoUserPoolPasswordPolicy(
            minimum_length=minimum_length,
            require_lowercase=require_lowercase,
            require_numbers=require_numbers,
            require_symbols=require_symbols,
            require_uppercase=require_uppercase,
            temporary_password_validity_days=temporary_password_validity_days,
        )

        return typing.cast(None, jsii.invoke(self, "putPasswordPolicy", [value]))

    @jsii.member(jsii_name="putSchema")
    def put_schema(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoUserPoolSchema", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPool.put_schema)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSchema", [value]))

    @jsii.member(jsii_name="putSmsConfiguration")
    def put_sms_configuration(
        self,
        *,
        external_id: builtins.str,
        sns_caller_arn: builtins.str,
    ) -> None:
        '''
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#external_id CognitoUserPool#external_id}.
        :param sns_caller_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sns_caller_arn CognitoUserPool#sns_caller_arn}.
        '''
        value = CognitoUserPoolSmsConfiguration(
            external_id=external_id, sns_caller_arn=sns_caller_arn
        )

        return typing.cast(None, jsii.invoke(self, "putSmsConfiguration", [value]))

    @jsii.member(jsii_name="putSoftwareTokenMfaConfiguration")
    def put_software_token_mfa_configuration(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#enabled CognitoUserPool#enabled}.
        '''
        value = CognitoUserPoolSoftwareTokenMfaConfiguration(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putSoftwareTokenMfaConfiguration", [value]))

    @jsii.member(jsii_name="putUsernameConfiguration")
    def put_username_configuration(
        self,
        *,
        case_sensitive: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param case_sensitive: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#case_sensitive CognitoUserPool#case_sensitive}.
        '''
        value = CognitoUserPoolUsernameConfiguration(case_sensitive=case_sensitive)

        return typing.cast(None, jsii.invoke(self, "putUsernameConfiguration", [value]))

    @jsii.member(jsii_name="putUserPoolAddOns")
    def put_user_pool_add_ons(self, *, advanced_security_mode: builtins.str) -> None:
        '''
        :param advanced_security_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#advanced_security_mode CognitoUserPool#advanced_security_mode}.
        '''
        value = CognitoUserPoolUserPoolAddOns(
            advanced_security_mode=advanced_security_mode
        )

        return typing.cast(None, jsii.invoke(self, "putUserPoolAddOns", [value]))

    @jsii.member(jsii_name="putVerificationMessageTemplate")
    def put_verification_message_template(
        self,
        *,
        default_email_option: typing.Optional[builtins.str] = None,
        email_message: typing.Optional[builtins.str] = None,
        email_message_by_link: typing.Optional[builtins.str] = None,
        email_subject: typing.Optional[builtins.str] = None,
        email_subject_by_link: typing.Optional[builtins.str] = None,
        sms_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_email_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#default_email_option CognitoUserPool#default_email_option}.
        :param email_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.
        :param email_message_by_link: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message_by_link CognitoUserPool#email_message_by_link}.
        :param email_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.
        :param email_subject_by_link: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject_by_link CognitoUserPool#email_subject_by_link}.
        :param sms_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.
        '''
        value = CognitoUserPoolVerificationMessageTemplate(
            default_email_option=default_email_option,
            email_message=email_message,
            email_message_by_link=email_message_by_link,
            email_subject=email_subject,
            email_subject_by_link=email_subject_by_link,
            sms_message=sms_message,
        )

        return typing.cast(None, jsii.invoke(self, "putVerificationMessageTemplate", [value]))

    @jsii.member(jsii_name="resetAccountRecoverySetting")
    def reset_account_recovery_setting(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountRecoverySetting", []))

    @jsii.member(jsii_name="resetAdminCreateUserConfig")
    def reset_admin_create_user_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminCreateUserConfig", []))

    @jsii.member(jsii_name="resetAliasAttributes")
    def reset_alias_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAliasAttributes", []))

    @jsii.member(jsii_name="resetAutoVerifiedAttributes")
    def reset_auto_verified_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoVerifiedAttributes", []))

    @jsii.member(jsii_name="resetDeviceConfiguration")
    def reset_device_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceConfiguration", []))

    @jsii.member(jsii_name="resetEmailConfiguration")
    def reset_email_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailConfiguration", []))

    @jsii.member(jsii_name="resetEmailVerificationMessage")
    def reset_email_verification_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailVerificationMessage", []))

    @jsii.member(jsii_name="resetEmailVerificationSubject")
    def reset_email_verification_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailVerificationSubject", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLambdaConfig")
    def reset_lambda_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambdaConfig", []))

    @jsii.member(jsii_name="resetMfaConfiguration")
    def reset_mfa_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMfaConfiguration", []))

    @jsii.member(jsii_name="resetPasswordPolicy")
    def reset_password_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordPolicy", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

    @jsii.member(jsii_name="resetSmsAuthenticationMessage")
    def reset_sms_authentication_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsAuthenticationMessage", []))

    @jsii.member(jsii_name="resetSmsConfiguration")
    def reset_sms_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsConfiguration", []))

    @jsii.member(jsii_name="resetSmsVerificationMessage")
    def reset_sms_verification_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsVerificationMessage", []))

    @jsii.member(jsii_name="resetSoftwareTokenMfaConfiguration")
    def reset_software_token_mfa_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSoftwareTokenMfaConfiguration", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUsernameAttributes")
    def reset_username_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameAttributes", []))

    @jsii.member(jsii_name="resetUsernameConfiguration")
    def reset_username_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameConfiguration", []))

    @jsii.member(jsii_name="resetUserPoolAddOns")
    def reset_user_pool_add_ons(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserPoolAddOns", []))

    @jsii.member(jsii_name="resetVerificationMessageTemplate")
    def reset_verification_message_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerificationMessageTemplate", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountRecoverySetting")
    def account_recovery_setting(
        self,
    ) -> "CognitoUserPoolAccountRecoverySettingOutputReference":
        return typing.cast("CognitoUserPoolAccountRecoverySettingOutputReference", jsii.get(self, "accountRecoverySetting"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminCreateUserConfig")
    def admin_create_user_config(
        self,
    ) -> "CognitoUserPoolAdminCreateUserConfigOutputReference":
        return typing.cast("CognitoUserPoolAdminCreateUserConfigOutputReference", jsii.get(self, "adminCreateUserConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationDate")
    def creation_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDomain")
    def custom_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceConfiguration")
    def device_configuration(
        self,
    ) -> "CognitoUserPoolDeviceConfigurationOutputReference":
        return typing.cast("CognitoUserPoolDeviceConfigurationOutputReference", jsii.get(self, "deviceConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailConfiguration")
    def email_configuration(self) -> "CognitoUserPoolEmailConfigurationOutputReference":
        return typing.cast("CognitoUserPoolEmailConfigurationOutputReference", jsii.get(self, "emailConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="estimatedNumberOfUsers")
    def estimated_number_of_users(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "estimatedNumberOfUsers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaConfig")
    def lambda_config(self) -> "CognitoUserPoolLambdaConfigOutputReference":
        return typing.cast("CognitoUserPoolLambdaConfigOutputReference", jsii.get(self, "lambdaConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedDate")
    def last_modified_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordPolicy")
    def password_policy(self) -> "CognitoUserPoolPasswordPolicyOutputReference":
        return typing.cast("CognitoUserPoolPasswordPolicyOutputReference", jsii.get(self, "passwordPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schema")
    def schema(self) -> "CognitoUserPoolSchemaList":
        return typing.cast("CognitoUserPoolSchemaList", jsii.get(self, "schema"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsConfiguration")
    def sms_configuration(self) -> "CognitoUserPoolSmsConfigurationOutputReference":
        return typing.cast("CognitoUserPoolSmsConfigurationOutputReference", jsii.get(self, "smsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="softwareTokenMfaConfiguration")
    def software_token_mfa_configuration(
        self,
    ) -> "CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference":
        return typing.cast("CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference", jsii.get(self, "softwareTokenMfaConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameConfiguration")
    def username_configuration(
        self,
    ) -> "CognitoUserPoolUsernameConfigurationOutputReference":
        return typing.cast("CognitoUserPoolUsernameConfigurationOutputReference", jsii.get(self, "usernameConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolAddOns")
    def user_pool_add_ons(self) -> "CognitoUserPoolUserPoolAddOnsOutputReference":
        return typing.cast("CognitoUserPoolUserPoolAddOnsOutputReference", jsii.get(self, "userPoolAddOns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verificationMessageTemplate")
    def verification_message_template(
        self,
    ) -> "CognitoUserPoolVerificationMessageTemplateOutputReference":
        return typing.cast("CognitoUserPoolVerificationMessageTemplateOutputReference", jsii.get(self, "verificationMessageTemplate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountRecoverySettingInput")
    def account_recovery_setting_input(
        self,
    ) -> typing.Optional["CognitoUserPoolAccountRecoverySetting"]:
        return typing.cast(typing.Optional["CognitoUserPoolAccountRecoverySetting"], jsii.get(self, "accountRecoverySettingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminCreateUserConfigInput")
    def admin_create_user_config_input(
        self,
    ) -> typing.Optional["CognitoUserPoolAdminCreateUserConfig"]:
        return typing.cast(typing.Optional["CognitoUserPoolAdminCreateUserConfig"], jsii.get(self, "adminCreateUserConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasAttributesInput")
    def alias_attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "aliasAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoVerifiedAttributesInput")
    def auto_verified_attributes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "autoVerifiedAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceConfigurationInput")
    def device_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolDeviceConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolDeviceConfiguration"], jsii.get(self, "deviceConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailConfigurationInput")
    def email_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolEmailConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolEmailConfiguration"], jsii.get(self, "emailConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailVerificationMessageInput")
    def email_verification_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailVerificationMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailVerificationSubjectInput")
    def email_verification_subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailVerificationSubjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaConfigInput")
    def lambda_config_input(self) -> typing.Optional["CognitoUserPoolLambdaConfig"]:
        return typing.cast(typing.Optional["CognitoUserPoolLambdaConfig"], jsii.get(self, "lambdaConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mfaConfigurationInput")
    def mfa_configuration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mfaConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordPolicyInput")
    def password_policy_input(self) -> typing.Optional["CognitoUserPoolPasswordPolicy"]:
        return typing.cast(typing.Optional["CognitoUserPoolPasswordPolicy"], jsii.get(self, "passwordPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaInput")
    def schema_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoUserPoolSchema"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoUserPoolSchema"]]], jsii.get(self, "schemaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsAuthenticationMessageInput")
    def sms_authentication_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smsAuthenticationMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsConfigurationInput")
    def sms_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolSmsConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolSmsConfiguration"], jsii.get(self, "smsConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsVerificationMessageInput")
    def sms_verification_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smsVerificationMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="softwareTokenMfaConfigurationInput")
    def software_token_mfa_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolSoftwareTokenMfaConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolSoftwareTokenMfaConfiguration"], jsii.get(self, "softwareTokenMfaConfigurationInput"))

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
    @jsii.member(jsii_name="usernameAttributesInput")
    def username_attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "usernameAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameConfigurationInput")
    def username_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolUsernameConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolUsernameConfiguration"], jsii.get(self, "usernameConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolAddOnsInput")
    def user_pool_add_ons_input(
        self,
    ) -> typing.Optional["CognitoUserPoolUserPoolAddOns"]:
        return typing.cast(typing.Optional["CognitoUserPoolUserPoolAddOns"], jsii.get(self, "userPoolAddOnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verificationMessageTemplateInput")
    def verification_message_template_input(
        self,
    ) -> typing.Optional["CognitoUserPoolVerificationMessageTemplate"]:
        return typing.cast(typing.Optional["CognitoUserPoolVerificationMessageTemplate"], jsii.get(self, "verificationMessageTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasAttributes")
    def alias_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "aliasAttributes"))

    @alias_attributes.setter
    def alias_attributes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "alias_attributes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aliasAttributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoVerifiedAttributes")
    def auto_verified_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "autoVerifiedAttributes"))

    @auto_verified_attributes.setter
    def auto_verified_attributes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "auto_verified_attributes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoVerifiedAttributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailVerificationMessage")
    def email_verification_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailVerificationMessage"))

    @email_verification_message.setter
    def email_verification_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "email_verification_message").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailVerificationMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailVerificationSubject")
    def email_verification_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailVerificationSubject"))

    @email_verification_subject.setter
    def email_verification_subject(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "email_verification_subject").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailVerificationSubject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mfaConfiguration")
    def mfa_configuration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mfaConfiguration"))

    @mfa_configuration.setter
    def mfa_configuration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "mfa_configuration").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mfaConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsAuthenticationMessage")
    def sms_authentication_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smsAuthenticationMessage"))

    @sms_authentication_message.setter
    def sms_authentication_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "sms_authentication_message").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smsAuthenticationMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsVerificationMessage")
    def sms_verification_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smsVerificationMessage"))

    @sms_verification_message.setter
    def sms_verification_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "sms_verification_message").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smsVerificationMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameAttributes")
    def username_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usernameAttributes"))

    @username_attributes.setter
    def username_attributes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPool, "username_attributes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameAttributes", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAccountRecoverySetting",
    jsii_struct_bases=[],
    name_mapping={"recovery_mechanism": "recoveryMechanism"},
)
class CognitoUserPoolAccountRecoverySetting:
    def __init__(
        self,
        *,
        recovery_mechanism: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoUserPoolAccountRecoverySettingRecoveryMechanism", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param recovery_mechanism: recovery_mechanism block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#recovery_mechanism CognitoUserPool#recovery_mechanism}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolAccountRecoverySetting.__init__)
            check_type(argname="argument recovery_mechanism", value=recovery_mechanism, expected_type=type_hints["recovery_mechanism"])
        self._values: typing.Dict[str, typing.Any] = {
            "recovery_mechanism": recovery_mechanism,
        }

    @builtins.property
    def recovery_mechanism(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"]]:
        '''recovery_mechanism block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#recovery_mechanism CognitoUserPool#recovery_mechanism}
        '''
        result = self._values.get("recovery_mechanism")
        assert result is not None, "Required property 'recovery_mechanism' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolAccountRecoverySetting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolAccountRecoverySettingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAccountRecoverySettingOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolAccountRecoverySettingOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRecoveryMechanism")
    def put_recovery_mechanism(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoUserPoolAccountRecoverySettingRecoveryMechanism", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolAccountRecoverySettingOutputReference.put_recovery_mechanism)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRecoveryMechanism", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recoveryMechanism")
    def recovery_mechanism(
        self,
    ) -> "CognitoUserPoolAccountRecoverySettingRecoveryMechanismList":
        return typing.cast("CognitoUserPoolAccountRecoverySettingRecoveryMechanismList", jsii.get(self, "recoveryMechanism"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recoveryMechanismInput")
    def recovery_mechanism_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"]]], jsii.get(self, "recoveryMechanismInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolAccountRecoverySetting]:
        return typing.cast(typing.Optional[CognitoUserPoolAccountRecoverySetting], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolAccountRecoverySetting],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAccountRecoverySettingOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAccountRecoverySettingRecoveryMechanism",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "priority": "priority"},
)
class CognitoUserPoolAccountRecoverySettingRecoveryMechanism:
    def __init__(self, *, name: builtins.str, priority: jsii.Number) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#priority CognitoUserPool#priority}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolAccountRecoverySettingRecoveryMechanism.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "priority": priority,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#priority CognitoUserPool#priority}.'''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolAccountRecoverySettingRecoveryMechanism(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolAccountRecoverySettingRecoveryMechanismList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAccountRecoverySettingRecoveryMechanismList",
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
            type_hints = typing.get_type_hints(CognitoUserPoolAccountRecoverySettingRecoveryMechanismList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CognitoUserPoolAccountRecoverySettingRecoveryMechanismOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolAccountRecoverySettingRecoveryMechanismList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CognitoUserPoolAccountRecoverySettingRecoveryMechanismOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAccountRecoverySettingRecoveryMechanismList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAccountRecoverySettingRecoveryMechanismList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAccountRecoverySettingRecoveryMechanismList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoUserPoolAccountRecoverySettingRecoveryMechanism]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoUserPoolAccountRecoverySettingRecoveryMechanism]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoUserPoolAccountRecoverySettingRecoveryMechanism]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAccountRecoverySettingRecoveryMechanismList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoUserPoolAccountRecoverySettingRecoveryMechanismOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAccountRecoverySettingRecoveryMechanismOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolAccountRecoverySettingRecoveryMechanismOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAccountRecoverySettingRecoveryMechanismOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAccountRecoverySettingRecoveryMechanismOutputReference, "priority").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[CognitoUserPoolAccountRecoverySettingRecoveryMechanism, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[CognitoUserPoolAccountRecoverySettingRecoveryMechanism, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[CognitoUserPoolAccountRecoverySettingRecoveryMechanism, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAccountRecoverySettingRecoveryMechanismOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAdminCreateUserConfig",
    jsii_struct_bases=[],
    name_mapping={
        "allow_admin_create_user_only": "allowAdminCreateUserOnly",
        "invite_message_template": "inviteMessageTemplate",
    },
)
class CognitoUserPoolAdminCreateUserConfig:
    def __init__(
        self,
        *,
        allow_admin_create_user_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        invite_message_template: typing.Optional[typing.Union["CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param allow_admin_create_user_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#allow_admin_create_user_only CognitoUserPool#allow_admin_create_user_only}.
        :param invite_message_template: invite_message_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#invite_message_template CognitoUserPool#invite_message_template}
        '''
        if isinstance(invite_message_template, dict):
            invite_message_template = CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate(**invite_message_template)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolAdminCreateUserConfig.__init__)
            check_type(argname="argument allow_admin_create_user_only", value=allow_admin_create_user_only, expected_type=type_hints["allow_admin_create_user_only"])
            check_type(argname="argument invite_message_template", value=invite_message_template, expected_type=type_hints["invite_message_template"])
        self._values: typing.Dict[str, typing.Any] = {}
        if allow_admin_create_user_only is not None:
            self._values["allow_admin_create_user_only"] = allow_admin_create_user_only
        if invite_message_template is not None:
            self._values["invite_message_template"] = invite_message_template

    @builtins.property
    def allow_admin_create_user_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#allow_admin_create_user_only CognitoUserPool#allow_admin_create_user_only}.'''
        result = self._values.get("allow_admin_create_user_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def invite_message_template(
        self,
    ) -> typing.Optional["CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate"]:
        '''invite_message_template block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#invite_message_template CognitoUserPool#invite_message_template}
        '''
        result = self._values.get("invite_message_template")
        return typing.cast(typing.Optional["CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolAdminCreateUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "email_message": "emailMessage",
        "email_subject": "emailSubject",
        "sms_message": "smsMessage",
    },
)
class CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate:
    def __init__(
        self,
        *,
        email_message: typing.Optional[builtins.str] = None,
        email_subject: typing.Optional[builtins.str] = None,
        sms_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param email_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.
        :param email_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.
        :param sms_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate.__init__)
            check_type(argname="argument email_message", value=email_message, expected_type=type_hints["email_message"])
            check_type(argname="argument email_subject", value=email_subject, expected_type=type_hints["email_subject"])
            check_type(argname="argument sms_message", value=sms_message, expected_type=type_hints["sms_message"])
        self._values: typing.Dict[str, typing.Any] = {}
        if email_message is not None:
            self._values["email_message"] = email_message
        if email_subject is not None:
            self._values["email_subject"] = email_subject
        if sms_message is not None:
            self._values["sms_message"] = sms_message

    @builtins.property
    def email_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.'''
        result = self._values.get("email_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_subject(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.'''
        result = self._values.get("email_subject")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sms_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.'''
        result = self._values.get("sms_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEmailMessage")
    def reset_email_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailMessage", []))

    @jsii.member(jsii_name="resetEmailSubject")
    def reset_email_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSubject", []))

    @jsii.member(jsii_name="resetSmsMessage")
    def reset_sms_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsMessage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessageInput")
    def email_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubjectInput")
    def email_subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSubjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsMessageInput")
    def sms_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smsMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessage")
    def email_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailMessage"))

    @email_message.setter
    def email_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference, "email_message").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubject")
    def email_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSubject"))

    @email_subject.setter
    def email_subject(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference, "email_subject").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailSubject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsMessage")
    def sms_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smsMessage"))

    @sms_message.setter
    def sms_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference, "sms_message").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smsMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate]:
        return typing.cast(typing.Optional[CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoUserPoolAdminCreateUserConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAdminCreateUserConfigOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolAdminCreateUserConfigOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putInviteMessageTemplate")
    def put_invite_message_template(
        self,
        *,
        email_message: typing.Optional[builtins.str] = None,
        email_subject: typing.Optional[builtins.str] = None,
        sms_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param email_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.
        :param email_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.
        :param sms_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.
        '''
        value = CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate(
            email_message=email_message,
            email_subject=email_subject,
            sms_message=sms_message,
        )

        return typing.cast(None, jsii.invoke(self, "putInviteMessageTemplate", [value]))

    @jsii.member(jsii_name="resetAllowAdminCreateUserOnly")
    def reset_allow_admin_create_user_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowAdminCreateUserOnly", []))

    @jsii.member(jsii_name="resetInviteMessageTemplate")
    def reset_invite_message_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInviteMessageTemplate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inviteMessageTemplate")
    def invite_message_template(
        self,
    ) -> CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference:
        return typing.cast(CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference, jsii.get(self, "inviteMessageTemplate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowAdminCreateUserOnlyInput")
    def allow_admin_create_user_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowAdminCreateUserOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inviteMessageTemplateInput")
    def invite_message_template_input(
        self,
    ) -> typing.Optional[CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate]:
        return typing.cast(typing.Optional[CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate], jsii.get(self, "inviteMessageTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowAdminCreateUserOnly")
    def allow_admin_create_user_only(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowAdminCreateUserOnly"))

    @allow_admin_create_user_only.setter
    def allow_admin_create_user_only(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAdminCreateUserConfigOutputReference, "allow_admin_create_user_only").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowAdminCreateUserOnly", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolAdminCreateUserConfig]:
        return typing.cast(typing.Optional[CognitoUserPoolAdminCreateUserConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolAdminCreateUserConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolAdminCreateUserConfigOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoUserPoolClient(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClient",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client aws_cognito_user_pool_client}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        user_pool_id: builtins.str,
        access_token_validity: typing.Optional[jsii.Number] = None,
        allowed_oauth_flows: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_oauth_flows_user_pool_client: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        allowed_oauth_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        analytics_configuration: typing.Optional[typing.Union["CognitoUserPoolClientAnalyticsConfiguration", typing.Dict[str, typing.Any]]] = None,
        callback_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_redirect_uri: typing.Optional[builtins.str] = None,
        enable_propagate_additional_user_context_data: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_token_revocation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        explicit_auth_flows: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_secret: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        id_token_validity: typing.Optional[jsii.Number] = None,
        logout_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
        prevent_user_existence_errors: typing.Optional[builtins.str] = None,
        read_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        refresh_token_validity: typing.Optional[jsii.Number] = None,
        supported_identity_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_validity_units: typing.Optional[typing.Union["CognitoUserPoolClientTokenValidityUnits", typing.Dict[str, typing.Any]]] = None,
        write_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client aws_cognito_user_pool_client} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#name CognitoUserPoolClient#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_pool_id CognitoUserPoolClient#user_pool_id}.
        :param access_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token_validity CognitoUserPoolClient#access_token_validity}.
        :param allowed_oauth_flows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows CognitoUserPoolClient#allowed_oauth_flows}.
        :param allowed_oauth_flows_user_pool_client: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows_user_pool_client CognitoUserPoolClient#allowed_oauth_flows_user_pool_client}.
        :param allowed_oauth_scopes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_scopes CognitoUserPoolClient#allowed_oauth_scopes}.
        :param analytics_configuration: analytics_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#analytics_configuration CognitoUserPoolClient#analytics_configuration}
        :param callback_urls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#callback_urls CognitoUserPoolClient#callback_urls}.
        :param default_redirect_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#default_redirect_uri CognitoUserPoolClient#default_redirect_uri}.
        :param enable_propagate_additional_user_context_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#enable_propagate_additional_user_context_data CognitoUserPoolClient#enable_propagate_additional_user_context_data}.
        :param enable_token_revocation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#enable_token_revocation CognitoUserPoolClient#enable_token_revocation}.
        :param explicit_auth_flows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#explicit_auth_flows CognitoUserPoolClient#explicit_auth_flows}.
        :param generate_secret: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#generate_secret CognitoUserPoolClient#generate_secret}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id CognitoUserPoolClient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param id_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token_validity CognitoUserPoolClient#id_token_validity}.
        :param logout_urls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#logout_urls CognitoUserPoolClient#logout_urls}.
        :param prevent_user_existence_errors: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#prevent_user_existence_errors CognitoUserPoolClient#prevent_user_existence_errors}.
        :param read_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#read_attributes CognitoUserPoolClient#read_attributes}.
        :param refresh_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token_validity CognitoUserPoolClient#refresh_token_validity}.
        :param supported_identity_providers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#supported_identity_providers CognitoUserPoolClient#supported_identity_providers}.
        :param token_validity_units: token_validity_units block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#token_validity_units CognitoUserPoolClient#token_validity_units}
        :param write_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#write_attributes CognitoUserPoolClient#write_attributes}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolClient.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoUserPoolClientConfig(
            name=name,
            user_pool_id=user_pool_id,
            access_token_validity=access_token_validity,
            allowed_oauth_flows=allowed_oauth_flows,
            allowed_oauth_flows_user_pool_client=allowed_oauth_flows_user_pool_client,
            allowed_oauth_scopes=allowed_oauth_scopes,
            analytics_configuration=analytics_configuration,
            callback_urls=callback_urls,
            default_redirect_uri=default_redirect_uri,
            enable_propagate_additional_user_context_data=enable_propagate_additional_user_context_data,
            enable_token_revocation=enable_token_revocation,
            explicit_auth_flows=explicit_auth_flows,
            generate_secret=generate_secret,
            id=id,
            id_token_validity=id_token_validity,
            logout_urls=logout_urls,
            prevent_user_existence_errors=prevent_user_existence_errors,
            read_attributes=read_attributes,
            refresh_token_validity=refresh_token_validity,
            supported_identity_providers=supported_identity_providers,
            token_validity_units=token_validity_units,
            write_attributes=write_attributes,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putAnalyticsConfiguration")
    def put_analytics_configuration(
        self,
        *,
        application_arn: typing.Optional[builtins.str] = None,
        application_id: typing.Optional[builtins.str] = None,
        external_id: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        user_data_shared: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param application_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_arn CognitoUserPoolClient#application_arn}.
        :param application_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_id CognitoUserPoolClient#application_id}.
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#external_id CognitoUserPoolClient#external_id}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#role_arn CognitoUserPoolClient#role_arn}.
        :param user_data_shared: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_data_shared CognitoUserPoolClient#user_data_shared}.
        '''
        value = CognitoUserPoolClientAnalyticsConfiguration(
            application_arn=application_arn,
            application_id=application_id,
            external_id=external_id,
            role_arn=role_arn,
            user_data_shared=user_data_shared,
        )

        return typing.cast(None, jsii.invoke(self, "putAnalyticsConfiguration", [value]))

    @jsii.member(jsii_name="putTokenValidityUnits")
    def put_token_validity_units(
        self,
        *,
        access_token: typing.Optional[builtins.str] = None,
        id_token: typing.Optional[builtins.str] = None,
        refresh_token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token CognitoUserPoolClient#access_token}.
        :param id_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token CognitoUserPoolClient#id_token}.
        :param refresh_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token CognitoUserPoolClient#refresh_token}.
        '''
        value = CognitoUserPoolClientTokenValidityUnits(
            access_token=access_token, id_token=id_token, refresh_token=refresh_token
        )

        return typing.cast(None, jsii.invoke(self, "putTokenValidityUnits", [value]))

    @jsii.member(jsii_name="resetAccessTokenValidity")
    def reset_access_token_validity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessTokenValidity", []))

    @jsii.member(jsii_name="resetAllowedOauthFlows")
    def reset_allowed_oauth_flows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOauthFlows", []))

    @jsii.member(jsii_name="resetAllowedOauthFlowsUserPoolClient")
    def reset_allowed_oauth_flows_user_pool_client(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOauthFlowsUserPoolClient", []))

    @jsii.member(jsii_name="resetAllowedOauthScopes")
    def reset_allowed_oauth_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOauthScopes", []))

    @jsii.member(jsii_name="resetAnalyticsConfiguration")
    def reset_analytics_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnalyticsConfiguration", []))

    @jsii.member(jsii_name="resetCallbackUrls")
    def reset_callback_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCallbackUrls", []))

    @jsii.member(jsii_name="resetDefaultRedirectUri")
    def reset_default_redirect_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultRedirectUri", []))

    @jsii.member(jsii_name="resetEnablePropagateAdditionalUserContextData")
    def reset_enable_propagate_additional_user_context_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablePropagateAdditionalUserContextData", []))

    @jsii.member(jsii_name="resetEnableTokenRevocation")
    def reset_enable_token_revocation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableTokenRevocation", []))

    @jsii.member(jsii_name="resetExplicitAuthFlows")
    def reset_explicit_auth_flows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExplicitAuthFlows", []))

    @jsii.member(jsii_name="resetGenerateSecret")
    def reset_generate_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenerateSecret", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdTokenValidity")
    def reset_id_token_validity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdTokenValidity", []))

    @jsii.member(jsii_name="resetLogoutUrls")
    def reset_logout_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogoutUrls", []))

    @jsii.member(jsii_name="resetPreventUserExistenceErrors")
    def reset_prevent_user_existence_errors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreventUserExistenceErrors", []))

    @jsii.member(jsii_name="resetReadAttributes")
    def reset_read_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadAttributes", []))

    @jsii.member(jsii_name="resetRefreshTokenValidity")
    def reset_refresh_token_validity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefreshTokenValidity", []))

    @jsii.member(jsii_name="resetSupportedIdentityProviders")
    def reset_supported_identity_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportedIdentityProviders", []))

    @jsii.member(jsii_name="resetTokenValidityUnits")
    def reset_token_validity_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenValidityUnits", []))

    @jsii.member(jsii_name="resetWriteAttributes")
    def reset_write_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWriteAttributes", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="analyticsConfiguration")
    def analytics_configuration(
        self,
    ) -> "CognitoUserPoolClientAnalyticsConfigurationOutputReference":
        return typing.cast("CognitoUserPoolClientAnalyticsConfigurationOutputReference", jsii.get(self, "analyticsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenValidityUnits")
    def token_validity_units(
        self,
    ) -> "CognitoUserPoolClientTokenValidityUnitsOutputReference":
        return typing.cast("CognitoUserPoolClientTokenValidityUnitsOutputReference", jsii.get(self, "tokenValidityUnits"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessTokenValidityInput")
    def access_token_validity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accessTokenValidityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlowsInput")
    def allowed_oauth_flows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedOauthFlowsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlowsUserPoolClientInput")
    def allowed_oauth_flows_user_pool_client_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowedOauthFlowsUserPoolClientInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthScopesInput")
    def allowed_oauth_scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedOauthScopesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="analyticsConfigurationInput")
    def analytics_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolClientAnalyticsConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolClientAnalyticsConfiguration"], jsii.get(self, "analyticsConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callbackUrlsInput")
    def callback_urls_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "callbackUrlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRedirectUriInput")
    def default_redirect_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultRedirectUriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePropagateAdditionalUserContextDataInput")
    def enable_propagate_additional_user_context_data_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enablePropagateAdditionalUserContextDataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableTokenRevocationInput")
    def enable_token_revocation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableTokenRevocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="explicitAuthFlowsInput")
    def explicit_auth_flows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "explicitAuthFlowsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generateSecretInput")
    def generate_secret_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "generateSecretInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idTokenValidityInput")
    def id_token_validity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idTokenValidityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logoutUrlsInput")
    def logout_urls_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "logoutUrlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preventUserExistenceErrorsInput")
    def prevent_user_existence_errors_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preventUserExistenceErrorsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readAttributesInput")
    def read_attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "readAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshTokenValidityInput")
    def refresh_token_validity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "refreshTokenValidityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedIdentityProvidersInput")
    def supported_identity_providers_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "supportedIdentityProvidersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenValidityUnitsInput")
    def token_validity_units_input(
        self,
    ) -> typing.Optional["CognitoUserPoolClientTokenValidityUnits"]:
        return typing.cast(typing.Optional["CognitoUserPoolClientTokenValidityUnits"], jsii.get(self, "tokenValidityUnitsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writeAttributesInput")
    def write_attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "writeAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessTokenValidity")
    def access_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessTokenValidity"))

    @access_token_validity.setter
    def access_token_validity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "access_token_validity").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessTokenValidity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlows")
    def allowed_oauth_flows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOauthFlows"))

    @allowed_oauth_flows.setter
    def allowed_oauth_flows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "allowed_oauth_flows").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedOauthFlows", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlowsUserPoolClient")
    def allowed_oauth_flows_user_pool_client(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowedOauthFlowsUserPoolClient"))

    @allowed_oauth_flows_user_pool_client.setter
    def allowed_oauth_flows_user_pool_client(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "allowed_oauth_flows_user_pool_client").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedOauthFlowsUserPoolClient", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthScopes")
    def allowed_oauth_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOauthScopes"))

    @allowed_oauth_scopes.setter
    def allowed_oauth_scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "allowed_oauth_scopes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedOauthScopes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callbackUrls")
    def callback_urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "callbackUrls"))

    @callback_urls.setter
    def callback_urls(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "callback_urls").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "callbackUrls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRedirectUri")
    def default_redirect_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultRedirectUri"))

    @default_redirect_uri.setter
    def default_redirect_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "default_redirect_uri").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultRedirectUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePropagateAdditionalUserContextData")
    def enable_propagate_additional_user_context_data(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enablePropagateAdditionalUserContextData"))

    @enable_propagate_additional_user_context_data.setter
    def enable_propagate_additional_user_context_data(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "enable_propagate_additional_user_context_data").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enablePropagateAdditionalUserContextData", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableTokenRevocation")
    def enable_token_revocation(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableTokenRevocation"))

    @enable_token_revocation.setter
    def enable_token_revocation(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "enable_token_revocation").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableTokenRevocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="explicitAuthFlows")
    def explicit_auth_flows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "explicitAuthFlows"))

    @explicit_auth_flows.setter
    def explicit_auth_flows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "explicit_auth_flows").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "explicitAuthFlows", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generateSecret")
    def generate_secret(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "generateSecret"))

    @generate_secret.setter
    def generate_secret(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "generate_secret").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "generateSecret", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idTokenValidity")
    def id_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idTokenValidity"))

    @id_token_validity.setter
    def id_token_validity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "id_token_validity").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idTokenValidity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logoutUrls")
    def logout_urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "logoutUrls"))

    @logout_urls.setter
    def logout_urls(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "logout_urls").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logoutUrls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preventUserExistenceErrors")
    def prevent_user_existence_errors(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preventUserExistenceErrors"))

    @prevent_user_existence_errors.setter
    def prevent_user_existence_errors(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "prevent_user_existence_errors").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preventUserExistenceErrors", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readAttributes")
    def read_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "readAttributes"))

    @read_attributes.setter
    def read_attributes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "read_attributes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readAttributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshTokenValidity")
    def refresh_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "refreshTokenValidity"))

    @refresh_token_validity.setter
    def refresh_token_validity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "refresh_token_validity").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "refreshTokenValidity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedIdentityProviders")
    def supported_identity_providers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedIdentityProviders"))

    @supported_identity_providers.setter
    def supported_identity_providers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "supported_identity_providers").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "supportedIdentityProviders", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writeAttributes")
    def write_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "writeAttributes"))

    @write_attributes.setter
    def write_attributes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClient, "write_attributes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "writeAttributes", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClientAnalyticsConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "application_arn": "applicationArn",
        "application_id": "applicationId",
        "external_id": "externalId",
        "role_arn": "roleArn",
        "user_data_shared": "userDataShared",
    },
)
class CognitoUserPoolClientAnalyticsConfiguration:
    def __init__(
        self,
        *,
        application_arn: typing.Optional[builtins.str] = None,
        application_id: typing.Optional[builtins.str] = None,
        external_id: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        user_data_shared: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param application_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_arn CognitoUserPoolClient#application_arn}.
        :param application_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_id CognitoUserPoolClient#application_id}.
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#external_id CognitoUserPoolClient#external_id}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#role_arn CognitoUserPoolClient#role_arn}.
        :param user_data_shared: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_data_shared CognitoUserPoolClient#user_data_shared}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolClientAnalyticsConfiguration.__init__)
            check_type(argname="argument application_arn", value=application_arn, expected_type=type_hints["application_arn"])
            check_type(argname="argument application_id", value=application_id, expected_type=type_hints["application_id"])
            check_type(argname="argument external_id", value=external_id, expected_type=type_hints["external_id"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument user_data_shared", value=user_data_shared, expected_type=type_hints["user_data_shared"])
        self._values: typing.Dict[str, typing.Any] = {}
        if application_arn is not None:
            self._values["application_arn"] = application_arn
        if application_id is not None:
            self._values["application_id"] = application_id
        if external_id is not None:
            self._values["external_id"] = external_id
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if user_data_shared is not None:
            self._values["user_data_shared"] = user_data_shared

    @builtins.property
    def application_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_arn CognitoUserPoolClient#application_arn}.'''
        result = self._values.get("application_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_id CognitoUserPoolClient#application_id}.'''
        result = self._values.get("application_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#external_id CognitoUserPoolClient#external_id}.'''
        result = self._values.get("external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#role_arn CognitoUserPoolClient#role_arn}.'''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_data_shared(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_data_shared CognitoUserPoolClient#user_data_shared}.'''
        result = self._values.get("user_data_shared")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolClientAnalyticsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolClientAnalyticsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClientAnalyticsConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolClientAnalyticsConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetApplicationArn")
    def reset_application_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationArn", []))

    @jsii.member(jsii_name="resetApplicationId")
    def reset_application_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationId", []))

    @jsii.member(jsii_name="resetExternalId")
    def reset_external_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalId", []))

    @jsii.member(jsii_name="resetRoleArn")
    def reset_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleArn", []))

    @jsii.member(jsii_name="resetUserDataShared")
    def reset_user_data_shared(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserDataShared", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArnInput")
    def application_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationIdInput")
    def application_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalIdInput")
    def external_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataSharedInput")
    def user_data_shared_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "userDataSharedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @application_arn.setter
    def application_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClientAnalyticsConfigurationOutputReference, "application_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @application_id.setter
    def application_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClientAnalyticsConfigurationOutputReference, "application_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @external_id.setter
    def external_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClientAnalyticsConfigurationOutputReference, "external_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "externalId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClientAnalyticsConfigurationOutputReference, "role_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataShared")
    def user_data_shared(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "userDataShared"))

    @user_data_shared.setter
    def user_data_shared(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClientAnalyticsConfigurationOutputReference, "user_data_shared").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userDataShared", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolClientAnalyticsConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolClientAnalyticsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolClientAnalyticsConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClientAnalyticsConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClientConfig",
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
        "user_pool_id": "userPoolId",
        "access_token_validity": "accessTokenValidity",
        "allowed_oauth_flows": "allowedOauthFlows",
        "allowed_oauth_flows_user_pool_client": "allowedOauthFlowsUserPoolClient",
        "allowed_oauth_scopes": "allowedOauthScopes",
        "analytics_configuration": "analyticsConfiguration",
        "callback_urls": "callbackUrls",
        "default_redirect_uri": "defaultRedirectUri",
        "enable_propagate_additional_user_context_data": "enablePropagateAdditionalUserContextData",
        "enable_token_revocation": "enableTokenRevocation",
        "explicit_auth_flows": "explicitAuthFlows",
        "generate_secret": "generateSecret",
        "id": "id",
        "id_token_validity": "idTokenValidity",
        "logout_urls": "logoutUrls",
        "prevent_user_existence_errors": "preventUserExistenceErrors",
        "read_attributes": "readAttributes",
        "refresh_token_validity": "refreshTokenValidity",
        "supported_identity_providers": "supportedIdentityProviders",
        "token_validity_units": "tokenValidityUnits",
        "write_attributes": "writeAttributes",
    },
)
class CognitoUserPoolClientConfig(cdktf.TerraformMetaArguments):
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
        user_pool_id: builtins.str,
        access_token_validity: typing.Optional[jsii.Number] = None,
        allowed_oauth_flows: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_oauth_flows_user_pool_client: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        allowed_oauth_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        analytics_configuration: typing.Optional[typing.Union[CognitoUserPoolClientAnalyticsConfiguration, typing.Dict[str, typing.Any]]] = None,
        callback_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_redirect_uri: typing.Optional[builtins.str] = None,
        enable_propagate_additional_user_context_data: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_token_revocation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        explicit_auth_flows: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_secret: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        id_token_validity: typing.Optional[jsii.Number] = None,
        logout_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
        prevent_user_existence_errors: typing.Optional[builtins.str] = None,
        read_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        refresh_token_validity: typing.Optional[jsii.Number] = None,
        supported_identity_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_validity_units: typing.Optional[typing.Union["CognitoUserPoolClientTokenValidityUnits", typing.Dict[str, typing.Any]]] = None,
        write_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#name CognitoUserPoolClient#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_pool_id CognitoUserPoolClient#user_pool_id}.
        :param access_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token_validity CognitoUserPoolClient#access_token_validity}.
        :param allowed_oauth_flows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows CognitoUserPoolClient#allowed_oauth_flows}.
        :param allowed_oauth_flows_user_pool_client: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows_user_pool_client CognitoUserPoolClient#allowed_oauth_flows_user_pool_client}.
        :param allowed_oauth_scopes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_scopes CognitoUserPoolClient#allowed_oauth_scopes}.
        :param analytics_configuration: analytics_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#analytics_configuration CognitoUserPoolClient#analytics_configuration}
        :param callback_urls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#callback_urls CognitoUserPoolClient#callback_urls}.
        :param default_redirect_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#default_redirect_uri CognitoUserPoolClient#default_redirect_uri}.
        :param enable_propagate_additional_user_context_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#enable_propagate_additional_user_context_data CognitoUserPoolClient#enable_propagate_additional_user_context_data}.
        :param enable_token_revocation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#enable_token_revocation CognitoUserPoolClient#enable_token_revocation}.
        :param explicit_auth_flows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#explicit_auth_flows CognitoUserPoolClient#explicit_auth_flows}.
        :param generate_secret: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#generate_secret CognitoUserPoolClient#generate_secret}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id CognitoUserPoolClient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param id_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token_validity CognitoUserPoolClient#id_token_validity}.
        :param logout_urls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#logout_urls CognitoUserPoolClient#logout_urls}.
        :param prevent_user_existence_errors: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#prevent_user_existence_errors CognitoUserPoolClient#prevent_user_existence_errors}.
        :param read_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#read_attributes CognitoUserPoolClient#read_attributes}.
        :param refresh_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token_validity CognitoUserPoolClient#refresh_token_validity}.
        :param supported_identity_providers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#supported_identity_providers CognitoUserPoolClient#supported_identity_providers}.
        :param token_validity_units: token_validity_units block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#token_validity_units CognitoUserPoolClient#token_validity_units}
        :param write_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#write_attributes CognitoUserPoolClient#write_attributes}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(analytics_configuration, dict):
            analytics_configuration = CognitoUserPoolClientAnalyticsConfiguration(**analytics_configuration)
        if isinstance(token_validity_units, dict):
            token_validity_units = CognitoUserPoolClientTokenValidityUnits(**token_validity_units)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolClientConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument access_token_validity", value=access_token_validity, expected_type=type_hints["access_token_validity"])
            check_type(argname="argument allowed_oauth_flows", value=allowed_oauth_flows, expected_type=type_hints["allowed_oauth_flows"])
            check_type(argname="argument allowed_oauth_flows_user_pool_client", value=allowed_oauth_flows_user_pool_client, expected_type=type_hints["allowed_oauth_flows_user_pool_client"])
            check_type(argname="argument allowed_oauth_scopes", value=allowed_oauth_scopes, expected_type=type_hints["allowed_oauth_scopes"])
            check_type(argname="argument analytics_configuration", value=analytics_configuration, expected_type=type_hints["analytics_configuration"])
            check_type(argname="argument callback_urls", value=callback_urls, expected_type=type_hints["callback_urls"])
            check_type(argname="argument default_redirect_uri", value=default_redirect_uri, expected_type=type_hints["default_redirect_uri"])
            check_type(argname="argument enable_propagate_additional_user_context_data", value=enable_propagate_additional_user_context_data, expected_type=type_hints["enable_propagate_additional_user_context_data"])
            check_type(argname="argument enable_token_revocation", value=enable_token_revocation, expected_type=type_hints["enable_token_revocation"])
            check_type(argname="argument explicit_auth_flows", value=explicit_auth_flows, expected_type=type_hints["explicit_auth_flows"])
            check_type(argname="argument generate_secret", value=generate_secret, expected_type=type_hints["generate_secret"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument id_token_validity", value=id_token_validity, expected_type=type_hints["id_token_validity"])
            check_type(argname="argument logout_urls", value=logout_urls, expected_type=type_hints["logout_urls"])
            check_type(argname="argument prevent_user_existence_errors", value=prevent_user_existence_errors, expected_type=type_hints["prevent_user_existence_errors"])
            check_type(argname="argument read_attributes", value=read_attributes, expected_type=type_hints["read_attributes"])
            check_type(argname="argument refresh_token_validity", value=refresh_token_validity, expected_type=type_hints["refresh_token_validity"])
            check_type(argname="argument supported_identity_providers", value=supported_identity_providers, expected_type=type_hints["supported_identity_providers"])
            check_type(argname="argument token_validity_units", value=token_validity_units, expected_type=type_hints["token_validity_units"])
            check_type(argname="argument write_attributes", value=write_attributes, expected_type=type_hints["write_attributes"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "user_pool_id": user_pool_id,
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
        if access_token_validity is not None:
            self._values["access_token_validity"] = access_token_validity
        if allowed_oauth_flows is not None:
            self._values["allowed_oauth_flows"] = allowed_oauth_flows
        if allowed_oauth_flows_user_pool_client is not None:
            self._values["allowed_oauth_flows_user_pool_client"] = allowed_oauth_flows_user_pool_client
        if allowed_oauth_scopes is not None:
            self._values["allowed_oauth_scopes"] = allowed_oauth_scopes
        if analytics_configuration is not None:
            self._values["analytics_configuration"] = analytics_configuration
        if callback_urls is not None:
            self._values["callback_urls"] = callback_urls
        if default_redirect_uri is not None:
            self._values["default_redirect_uri"] = default_redirect_uri
        if enable_propagate_additional_user_context_data is not None:
            self._values["enable_propagate_additional_user_context_data"] = enable_propagate_additional_user_context_data
        if enable_token_revocation is not None:
            self._values["enable_token_revocation"] = enable_token_revocation
        if explicit_auth_flows is not None:
            self._values["explicit_auth_flows"] = explicit_auth_flows
        if generate_secret is not None:
            self._values["generate_secret"] = generate_secret
        if id is not None:
            self._values["id"] = id
        if id_token_validity is not None:
            self._values["id_token_validity"] = id_token_validity
        if logout_urls is not None:
            self._values["logout_urls"] = logout_urls
        if prevent_user_existence_errors is not None:
            self._values["prevent_user_existence_errors"] = prevent_user_existence_errors
        if read_attributes is not None:
            self._values["read_attributes"] = read_attributes
        if refresh_token_validity is not None:
            self._values["refresh_token_validity"] = refresh_token_validity
        if supported_identity_providers is not None:
            self._values["supported_identity_providers"] = supported_identity_providers
        if token_validity_units is not None:
            self._values["token_validity_units"] = token_validity_units
        if write_attributes is not None:
            self._values["write_attributes"] = write_attributes

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#name CognitoUserPoolClient#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_pool_id CognitoUserPoolClient#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_token_validity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token_validity CognitoUserPoolClient#access_token_validity}.'''
        result = self._values.get("access_token_validity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allowed_oauth_flows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows CognitoUserPoolClient#allowed_oauth_flows}.'''
        result = self._values.get("allowed_oauth_flows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_oauth_flows_user_pool_client(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows_user_pool_client CognitoUserPoolClient#allowed_oauth_flows_user_pool_client}.'''
        result = self._values.get("allowed_oauth_flows_user_pool_client")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def allowed_oauth_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_scopes CognitoUserPoolClient#allowed_oauth_scopes}.'''
        result = self._values.get("allowed_oauth_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def analytics_configuration(
        self,
    ) -> typing.Optional[CognitoUserPoolClientAnalyticsConfiguration]:
        '''analytics_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#analytics_configuration CognitoUserPoolClient#analytics_configuration}
        '''
        result = self._values.get("analytics_configuration")
        return typing.cast(typing.Optional[CognitoUserPoolClientAnalyticsConfiguration], result)

    @builtins.property
    def callback_urls(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#callback_urls CognitoUserPoolClient#callback_urls}.'''
        result = self._values.get("callback_urls")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_redirect_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#default_redirect_uri CognitoUserPoolClient#default_redirect_uri}.'''
        result = self._values.get("default_redirect_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_propagate_additional_user_context_data(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#enable_propagate_additional_user_context_data CognitoUserPoolClient#enable_propagate_additional_user_context_data}.'''
        result = self._values.get("enable_propagate_additional_user_context_data")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_token_revocation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#enable_token_revocation CognitoUserPoolClient#enable_token_revocation}.'''
        result = self._values.get("enable_token_revocation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def explicit_auth_flows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#explicit_auth_flows CognitoUserPoolClient#explicit_auth_flows}.'''
        result = self._values.get("explicit_auth_flows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def generate_secret(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#generate_secret CognitoUserPoolClient#generate_secret}.'''
        result = self._values.get("generate_secret")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id CognitoUserPoolClient#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id_token_validity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token_validity CognitoUserPoolClient#id_token_validity}.'''
        result = self._values.get("id_token_validity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def logout_urls(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#logout_urls CognitoUserPoolClient#logout_urls}.'''
        result = self._values.get("logout_urls")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def prevent_user_existence_errors(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#prevent_user_existence_errors CognitoUserPoolClient#prevent_user_existence_errors}.'''
        result = self._values.get("prevent_user_existence_errors")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#read_attributes CognitoUserPoolClient#read_attributes}.'''
        result = self._values.get("read_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def refresh_token_validity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token_validity CognitoUserPoolClient#refresh_token_validity}.'''
        result = self._values.get("refresh_token_validity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def supported_identity_providers(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#supported_identity_providers CognitoUserPoolClient#supported_identity_providers}.'''
        result = self._values.get("supported_identity_providers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_validity_units(
        self,
    ) -> typing.Optional["CognitoUserPoolClientTokenValidityUnits"]:
        '''token_validity_units block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#token_validity_units CognitoUserPoolClient#token_validity_units}
        '''
        result = self._values.get("token_validity_units")
        return typing.cast(typing.Optional["CognitoUserPoolClientTokenValidityUnits"], result)

    @builtins.property
    def write_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#write_attributes CognitoUserPoolClient#write_attributes}.'''
        result = self._values.get("write_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolClientConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClientTokenValidityUnits",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "id_token": "idToken",
        "refresh_token": "refreshToken",
    },
)
class CognitoUserPoolClientTokenValidityUnits:
    def __init__(
        self,
        *,
        access_token: typing.Optional[builtins.str] = None,
        id_token: typing.Optional[builtins.str] = None,
        refresh_token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token CognitoUserPoolClient#access_token}.
        :param id_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token CognitoUserPoolClient#id_token}.
        :param refresh_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token CognitoUserPoolClient#refresh_token}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolClientTokenValidityUnits.__init__)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument id_token", value=id_token, expected_type=type_hints["id_token"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if id_token is not None:
            self._values["id_token"] = id_token
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def access_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token CognitoUserPoolClient#access_token}.'''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token CognitoUserPoolClient#id_token}.'''
        result = self._values.get("id_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token CognitoUserPoolClient#refresh_token}.'''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolClientTokenValidityUnits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolClientTokenValidityUnitsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClientTokenValidityUnitsOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolClientTokenValidityUnitsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAccessToken")
    def reset_access_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessToken", []))

    @jsii.member(jsii_name="resetIdToken")
    def reset_id_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdToken", []))

    @jsii.member(jsii_name="resetRefreshToken")
    def reset_refresh_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefreshToken", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessTokenInput")
    def access_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idTokenInput")
    def id_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshTokenInput")
    def refresh_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "refreshTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessToken")
    def access_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessToken"))

    @access_token.setter
    def access_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClientTokenValidityUnitsOutputReference, "access_token").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idToken")
    def id_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idToken"))

    @id_token.setter
    def id_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClientTokenValidityUnitsOutputReference, "id_token").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshToken")
    def refresh_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "refreshToken"))

    @refresh_token.setter
    def refresh_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClientTokenValidityUnitsOutputReference, "refresh_token").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "refreshToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolClientTokenValidityUnits]:
        return typing.cast(typing.Optional[CognitoUserPoolClientTokenValidityUnits], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolClientTokenValidityUnits],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolClientTokenValidityUnitsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolConfig",
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
        "account_recovery_setting": "accountRecoverySetting",
        "admin_create_user_config": "adminCreateUserConfig",
        "alias_attributes": "aliasAttributes",
        "auto_verified_attributes": "autoVerifiedAttributes",
        "device_configuration": "deviceConfiguration",
        "email_configuration": "emailConfiguration",
        "email_verification_message": "emailVerificationMessage",
        "email_verification_subject": "emailVerificationSubject",
        "id": "id",
        "lambda_config": "lambdaConfig",
        "mfa_configuration": "mfaConfiguration",
        "password_policy": "passwordPolicy",
        "schema": "schema",
        "sms_authentication_message": "smsAuthenticationMessage",
        "sms_configuration": "smsConfiguration",
        "sms_verification_message": "smsVerificationMessage",
        "software_token_mfa_configuration": "softwareTokenMfaConfiguration",
        "tags": "tags",
        "tags_all": "tagsAll",
        "username_attributes": "usernameAttributes",
        "username_configuration": "usernameConfiguration",
        "user_pool_add_ons": "userPoolAddOns",
        "verification_message_template": "verificationMessageTemplate",
    },
)
class CognitoUserPoolConfig(cdktf.TerraformMetaArguments):
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
        account_recovery_setting: typing.Optional[typing.Union[CognitoUserPoolAccountRecoverySetting, typing.Dict[str, typing.Any]]] = None,
        admin_create_user_config: typing.Optional[typing.Union[CognitoUserPoolAdminCreateUserConfig, typing.Dict[str, typing.Any]]] = None,
        alias_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_verified_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        device_configuration: typing.Optional[typing.Union["CognitoUserPoolDeviceConfiguration", typing.Dict[str, typing.Any]]] = None,
        email_configuration: typing.Optional[typing.Union["CognitoUserPoolEmailConfiguration", typing.Dict[str, typing.Any]]] = None,
        email_verification_message: typing.Optional[builtins.str] = None,
        email_verification_subject: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        lambda_config: typing.Optional[typing.Union["CognitoUserPoolLambdaConfig", typing.Dict[str, typing.Any]]] = None,
        mfa_configuration: typing.Optional[builtins.str] = None,
        password_policy: typing.Optional[typing.Union["CognitoUserPoolPasswordPolicy", typing.Dict[str, typing.Any]]] = None,
        schema: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CognitoUserPoolSchema", typing.Dict[str, typing.Any]]]]] = None,
        sms_authentication_message: typing.Optional[builtins.str] = None,
        sms_configuration: typing.Optional[typing.Union["CognitoUserPoolSmsConfiguration", typing.Dict[str, typing.Any]]] = None,
        sms_verification_message: typing.Optional[builtins.str] = None,
        software_token_mfa_configuration: typing.Optional[typing.Union["CognitoUserPoolSoftwareTokenMfaConfiguration", typing.Dict[str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        username_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        username_configuration: typing.Optional[typing.Union["CognitoUserPoolUsernameConfiguration", typing.Dict[str, typing.Any]]] = None,
        user_pool_add_ons: typing.Optional[typing.Union["CognitoUserPoolUserPoolAddOns", typing.Dict[str, typing.Any]]] = None,
        verification_message_template: typing.Optional[typing.Union["CognitoUserPoolVerificationMessageTemplate", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.
        :param account_recovery_setting: account_recovery_setting block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#account_recovery_setting CognitoUserPool#account_recovery_setting}
        :param admin_create_user_config: admin_create_user_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#admin_create_user_config CognitoUserPool#admin_create_user_config}
        :param alias_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#alias_attributes CognitoUserPool#alias_attributes}.
        :param auto_verified_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#auto_verified_attributes CognitoUserPool#auto_verified_attributes}.
        :param device_configuration: device_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_configuration CognitoUserPool#device_configuration}
        :param email_configuration: email_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_configuration CognitoUserPool#email_configuration}
        :param email_verification_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_message CognitoUserPool#email_verification_message}.
        :param email_verification_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_subject CognitoUserPool#email_verification_subject}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#id CognitoUserPool#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param lambda_config: lambda_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_config CognitoUserPool#lambda_config}
        :param mfa_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#mfa_configuration CognitoUserPool#mfa_configuration}.
        :param password_policy: password_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#password_policy CognitoUserPool#password_policy}
        :param schema: schema block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#schema CognitoUserPool#schema}
        :param sms_authentication_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_authentication_message CognitoUserPool#sms_authentication_message}.
        :param sms_configuration: sms_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_configuration CognitoUserPool#sms_configuration}
        :param sms_verification_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_verification_message CognitoUserPool#sms_verification_message}.
        :param software_token_mfa_configuration: software_token_mfa_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#software_token_mfa_configuration CognitoUserPool#software_token_mfa_configuration}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags CognitoUserPool#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags_all CognitoUserPool#tags_all}.
        :param username_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_attributes CognitoUserPool#username_attributes}.
        :param username_configuration: username_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_configuration CognitoUserPool#username_configuration}
        :param user_pool_add_ons: user_pool_add_ons block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_pool_add_ons CognitoUserPool#user_pool_add_ons}
        :param verification_message_template: verification_message_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verification_message_template CognitoUserPool#verification_message_template}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(account_recovery_setting, dict):
            account_recovery_setting = CognitoUserPoolAccountRecoverySetting(**account_recovery_setting)
        if isinstance(admin_create_user_config, dict):
            admin_create_user_config = CognitoUserPoolAdminCreateUserConfig(**admin_create_user_config)
        if isinstance(device_configuration, dict):
            device_configuration = CognitoUserPoolDeviceConfiguration(**device_configuration)
        if isinstance(email_configuration, dict):
            email_configuration = CognitoUserPoolEmailConfiguration(**email_configuration)
        if isinstance(lambda_config, dict):
            lambda_config = CognitoUserPoolLambdaConfig(**lambda_config)
        if isinstance(password_policy, dict):
            password_policy = CognitoUserPoolPasswordPolicy(**password_policy)
        if isinstance(sms_configuration, dict):
            sms_configuration = CognitoUserPoolSmsConfiguration(**sms_configuration)
        if isinstance(software_token_mfa_configuration, dict):
            software_token_mfa_configuration = CognitoUserPoolSoftwareTokenMfaConfiguration(**software_token_mfa_configuration)
        if isinstance(username_configuration, dict):
            username_configuration = CognitoUserPoolUsernameConfiguration(**username_configuration)
        if isinstance(user_pool_add_ons, dict):
            user_pool_add_ons = CognitoUserPoolUserPoolAddOns(**user_pool_add_ons)
        if isinstance(verification_message_template, dict):
            verification_message_template = CognitoUserPoolVerificationMessageTemplate(**verification_message_template)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument account_recovery_setting", value=account_recovery_setting, expected_type=type_hints["account_recovery_setting"])
            check_type(argname="argument admin_create_user_config", value=admin_create_user_config, expected_type=type_hints["admin_create_user_config"])
            check_type(argname="argument alias_attributes", value=alias_attributes, expected_type=type_hints["alias_attributes"])
            check_type(argname="argument auto_verified_attributes", value=auto_verified_attributes, expected_type=type_hints["auto_verified_attributes"])
            check_type(argname="argument device_configuration", value=device_configuration, expected_type=type_hints["device_configuration"])
            check_type(argname="argument email_configuration", value=email_configuration, expected_type=type_hints["email_configuration"])
            check_type(argname="argument email_verification_message", value=email_verification_message, expected_type=type_hints["email_verification_message"])
            check_type(argname="argument email_verification_subject", value=email_verification_subject, expected_type=type_hints["email_verification_subject"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument lambda_config", value=lambda_config, expected_type=type_hints["lambda_config"])
            check_type(argname="argument mfa_configuration", value=mfa_configuration, expected_type=type_hints["mfa_configuration"])
            check_type(argname="argument password_policy", value=password_policy, expected_type=type_hints["password_policy"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument sms_authentication_message", value=sms_authentication_message, expected_type=type_hints["sms_authentication_message"])
            check_type(argname="argument sms_configuration", value=sms_configuration, expected_type=type_hints["sms_configuration"])
            check_type(argname="argument sms_verification_message", value=sms_verification_message, expected_type=type_hints["sms_verification_message"])
            check_type(argname="argument software_token_mfa_configuration", value=software_token_mfa_configuration, expected_type=type_hints["software_token_mfa_configuration"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
            check_type(argname="argument username_attributes", value=username_attributes, expected_type=type_hints["username_attributes"])
            check_type(argname="argument username_configuration", value=username_configuration, expected_type=type_hints["username_configuration"])
            check_type(argname="argument user_pool_add_ons", value=user_pool_add_ons, expected_type=type_hints["user_pool_add_ons"])
            check_type(argname="argument verification_message_template", value=verification_message_template, expected_type=type_hints["verification_message_template"])
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
        if account_recovery_setting is not None:
            self._values["account_recovery_setting"] = account_recovery_setting
        if admin_create_user_config is not None:
            self._values["admin_create_user_config"] = admin_create_user_config
        if alias_attributes is not None:
            self._values["alias_attributes"] = alias_attributes
        if auto_verified_attributes is not None:
            self._values["auto_verified_attributes"] = auto_verified_attributes
        if device_configuration is not None:
            self._values["device_configuration"] = device_configuration
        if email_configuration is not None:
            self._values["email_configuration"] = email_configuration
        if email_verification_message is not None:
            self._values["email_verification_message"] = email_verification_message
        if email_verification_subject is not None:
            self._values["email_verification_subject"] = email_verification_subject
        if id is not None:
            self._values["id"] = id
        if lambda_config is not None:
            self._values["lambda_config"] = lambda_config
        if mfa_configuration is not None:
            self._values["mfa_configuration"] = mfa_configuration
        if password_policy is not None:
            self._values["password_policy"] = password_policy
        if schema is not None:
            self._values["schema"] = schema
        if sms_authentication_message is not None:
            self._values["sms_authentication_message"] = sms_authentication_message
        if sms_configuration is not None:
            self._values["sms_configuration"] = sms_configuration
        if sms_verification_message is not None:
            self._values["sms_verification_message"] = sms_verification_message
        if software_token_mfa_configuration is not None:
            self._values["software_token_mfa_configuration"] = software_token_mfa_configuration
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if username_attributes is not None:
            self._values["username_attributes"] = username_attributes
        if username_configuration is not None:
            self._values["username_configuration"] = username_configuration
        if user_pool_add_ons is not None:
            self._values["user_pool_add_ons"] = user_pool_add_ons
        if verification_message_template is not None:
            self._values["verification_message_template"] = verification_message_template

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_recovery_setting(
        self,
    ) -> typing.Optional[CognitoUserPoolAccountRecoverySetting]:
        '''account_recovery_setting block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#account_recovery_setting CognitoUserPool#account_recovery_setting}
        '''
        result = self._values.get("account_recovery_setting")
        return typing.cast(typing.Optional[CognitoUserPoolAccountRecoverySetting], result)

    @builtins.property
    def admin_create_user_config(
        self,
    ) -> typing.Optional[CognitoUserPoolAdminCreateUserConfig]:
        '''admin_create_user_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#admin_create_user_config CognitoUserPool#admin_create_user_config}
        '''
        result = self._values.get("admin_create_user_config")
        return typing.cast(typing.Optional[CognitoUserPoolAdminCreateUserConfig], result)

    @builtins.property
    def alias_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#alias_attributes CognitoUserPool#alias_attributes}.'''
        result = self._values.get("alias_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def auto_verified_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#auto_verified_attributes CognitoUserPool#auto_verified_attributes}.'''
        result = self._values.get("auto_verified_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def device_configuration(
        self,
    ) -> typing.Optional["CognitoUserPoolDeviceConfiguration"]:
        '''device_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_configuration CognitoUserPool#device_configuration}
        '''
        result = self._values.get("device_configuration")
        return typing.cast(typing.Optional["CognitoUserPoolDeviceConfiguration"], result)

    @builtins.property
    def email_configuration(
        self,
    ) -> typing.Optional["CognitoUserPoolEmailConfiguration"]:
        '''email_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_configuration CognitoUserPool#email_configuration}
        '''
        result = self._values.get("email_configuration")
        return typing.cast(typing.Optional["CognitoUserPoolEmailConfiguration"], result)

    @builtins.property
    def email_verification_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_message CognitoUserPool#email_verification_message}.'''
        result = self._values.get("email_verification_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_verification_subject(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_subject CognitoUserPool#email_verification_subject}.'''
        result = self._values.get("email_verification_subject")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#id CognitoUserPool#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_config(self) -> typing.Optional["CognitoUserPoolLambdaConfig"]:
        '''lambda_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_config CognitoUserPool#lambda_config}
        '''
        result = self._values.get("lambda_config")
        return typing.cast(typing.Optional["CognitoUserPoolLambdaConfig"], result)

    @builtins.property
    def mfa_configuration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#mfa_configuration CognitoUserPool#mfa_configuration}.'''
        result = self._values.get("mfa_configuration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_policy(self) -> typing.Optional["CognitoUserPoolPasswordPolicy"]:
        '''password_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#password_policy CognitoUserPool#password_policy}
        '''
        result = self._values.get("password_policy")
        return typing.cast(typing.Optional["CognitoUserPoolPasswordPolicy"], result)

    @builtins.property
    def schema(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoUserPoolSchema"]]]:
        '''schema block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#schema CognitoUserPool#schema}
        '''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CognitoUserPoolSchema"]]], result)

    @builtins.property
    def sms_authentication_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_authentication_message CognitoUserPool#sms_authentication_message}.'''
        result = self._values.get("sms_authentication_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sms_configuration(self) -> typing.Optional["CognitoUserPoolSmsConfiguration"]:
        '''sms_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_configuration CognitoUserPool#sms_configuration}
        '''
        result = self._values.get("sms_configuration")
        return typing.cast(typing.Optional["CognitoUserPoolSmsConfiguration"], result)

    @builtins.property
    def sms_verification_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_verification_message CognitoUserPool#sms_verification_message}.'''
        result = self._values.get("sms_verification_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def software_token_mfa_configuration(
        self,
    ) -> typing.Optional["CognitoUserPoolSoftwareTokenMfaConfiguration"]:
        '''software_token_mfa_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#software_token_mfa_configuration CognitoUserPool#software_token_mfa_configuration}
        '''
        result = self._values.get("software_token_mfa_configuration")
        return typing.cast(typing.Optional["CognitoUserPoolSoftwareTokenMfaConfiguration"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags CognitoUserPool#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags_all CognitoUserPool#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def username_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_attributes CognitoUserPool#username_attributes}.'''
        result = self._values.get("username_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def username_configuration(
        self,
    ) -> typing.Optional["CognitoUserPoolUsernameConfiguration"]:
        '''username_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_configuration CognitoUserPool#username_configuration}
        '''
        result = self._values.get("username_configuration")
        return typing.cast(typing.Optional["CognitoUserPoolUsernameConfiguration"], result)

    @builtins.property
    def user_pool_add_ons(self) -> typing.Optional["CognitoUserPoolUserPoolAddOns"]:
        '''user_pool_add_ons block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_pool_add_ons CognitoUserPool#user_pool_add_ons}
        '''
        result = self._values.get("user_pool_add_ons")
        return typing.cast(typing.Optional["CognitoUserPoolUserPoolAddOns"], result)

    @builtins.property
    def verification_message_template(
        self,
    ) -> typing.Optional["CognitoUserPoolVerificationMessageTemplate"]:
        '''verification_message_template block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verification_message_template CognitoUserPool#verification_message_template}
        '''
        result = self._values.get("verification_message_template")
        return typing.cast(typing.Optional["CognitoUserPoolVerificationMessageTemplate"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolDeviceConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "challenge_required_on_new_device": "challengeRequiredOnNewDevice",
        "device_only_remembered_on_user_prompt": "deviceOnlyRememberedOnUserPrompt",
    },
)
class CognitoUserPoolDeviceConfiguration:
    def __init__(
        self,
        *,
        challenge_required_on_new_device: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        device_only_remembered_on_user_prompt: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param challenge_required_on_new_device: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#challenge_required_on_new_device CognitoUserPool#challenge_required_on_new_device}.
        :param device_only_remembered_on_user_prompt: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_only_remembered_on_user_prompt CognitoUserPool#device_only_remembered_on_user_prompt}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolDeviceConfiguration.__init__)
            check_type(argname="argument challenge_required_on_new_device", value=challenge_required_on_new_device, expected_type=type_hints["challenge_required_on_new_device"])
            check_type(argname="argument device_only_remembered_on_user_prompt", value=device_only_remembered_on_user_prompt, expected_type=type_hints["device_only_remembered_on_user_prompt"])
        self._values: typing.Dict[str, typing.Any] = {}
        if challenge_required_on_new_device is not None:
            self._values["challenge_required_on_new_device"] = challenge_required_on_new_device
        if device_only_remembered_on_user_prompt is not None:
            self._values["device_only_remembered_on_user_prompt"] = device_only_remembered_on_user_prompt

    @builtins.property
    def challenge_required_on_new_device(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#challenge_required_on_new_device CognitoUserPool#challenge_required_on_new_device}.'''
        result = self._values.get("challenge_required_on_new_device")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def device_only_remembered_on_user_prompt(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_only_remembered_on_user_prompt CognitoUserPool#device_only_remembered_on_user_prompt}.'''
        result = self._values.get("device_only_remembered_on_user_prompt")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolDeviceConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolDeviceConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolDeviceConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolDeviceConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetChallengeRequiredOnNewDevice")
    def reset_challenge_required_on_new_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChallengeRequiredOnNewDevice", []))

    @jsii.member(jsii_name="resetDeviceOnlyRememberedOnUserPrompt")
    def reset_device_only_remembered_on_user_prompt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceOnlyRememberedOnUserPrompt", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="challengeRequiredOnNewDeviceInput")
    def challenge_required_on_new_device_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "challengeRequiredOnNewDeviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceOnlyRememberedOnUserPromptInput")
    def device_only_remembered_on_user_prompt_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deviceOnlyRememberedOnUserPromptInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="challengeRequiredOnNewDevice")
    def challenge_required_on_new_device(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "challengeRequiredOnNewDevice"))

    @challenge_required_on_new_device.setter
    def challenge_required_on_new_device(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolDeviceConfigurationOutputReference, "challenge_required_on_new_device").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "challengeRequiredOnNewDevice", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceOnlyRememberedOnUserPrompt")
    def device_only_remembered_on_user_prompt(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deviceOnlyRememberedOnUserPrompt"))

    @device_only_remembered_on_user_prompt.setter
    def device_only_remembered_on_user_prompt(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolDeviceConfigurationOutputReference, "device_only_remembered_on_user_prompt").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deviceOnlyRememberedOnUserPrompt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolDeviceConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolDeviceConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolDeviceConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolDeviceConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoUserPoolDomain(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolDomain",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain aws_cognito_user_pool_domain}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        domain: builtins.str,
        user_pool_id: builtins.str,
        certificate_arn: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain aws_cognito_user_pool_domain} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#domain CognitoUserPoolDomain#domain}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#user_pool_id CognitoUserPoolDomain#user_pool_id}.
        :param certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#certificate_arn CognitoUserPoolDomain#certificate_arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#id CognitoUserPoolDomain#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolDomain.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoUserPoolDomainConfig(
            domain=domain,
            user_pool_id=user_pool_id,
            certificate_arn=certificate_arn,
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

    @jsii.member(jsii_name="resetCertificateArn")
    def reset_certificate_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateArn", []))

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
    @jsii.member(jsii_name="awsAccountId")
    def aws_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudfrontDistributionArn")
    def cloudfront_distribution_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudfrontDistributionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateArnInput")
    def certificate_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateArn"))

    @certificate_arn.setter
    def certificate_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolDomain, "certificate_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolDomain, "domain").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolDomain, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolDomain, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolDomainConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "domain": "domain",
        "user_pool_id": "userPoolId",
        "certificate_arn": "certificateArn",
        "id": "id",
    },
)
class CognitoUserPoolDomainConfig(cdktf.TerraformMetaArguments):
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
        domain: builtins.str,
        user_pool_id: builtins.str,
        certificate_arn: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#domain CognitoUserPoolDomain#domain}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#user_pool_id CognitoUserPoolDomain#user_pool_id}.
        :param certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#certificate_arn CognitoUserPoolDomain#certificate_arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#id CognitoUserPoolDomain#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolDomainConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument certificate_arn", value=certificate_arn, expected_type=type_hints["certificate_arn"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
            "user_pool_id": user_pool_id,
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
        if certificate_arn is not None:
            self._values["certificate_arn"] = certificate_arn
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
    def domain(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#domain CognitoUserPoolDomain#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#user_pool_id CognitoUserPoolDomain#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#certificate_arn CognitoUserPoolDomain#certificate_arn}.'''
        result = self._values.get("certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#id CognitoUserPoolDomain#id}.

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
        return "CognitoUserPoolDomainConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolEmailConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "configuration_set": "configurationSet",
        "email_sending_account": "emailSendingAccount",
        "from_email_address": "fromEmailAddress",
        "reply_to_email_address": "replyToEmailAddress",
        "source_arn": "sourceArn",
    },
)
class CognitoUserPoolEmailConfiguration:
    def __init__(
        self,
        *,
        configuration_set: typing.Optional[builtins.str] = None,
        email_sending_account: typing.Optional[builtins.str] = None,
        from_email_address: typing.Optional[builtins.str] = None,
        reply_to_email_address: typing.Optional[builtins.str] = None,
        source_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param configuration_set: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#configuration_set CognitoUserPool#configuration_set}.
        :param email_sending_account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_sending_account CognitoUserPool#email_sending_account}.
        :param from_email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#from_email_address CognitoUserPool#from_email_address}.
        :param reply_to_email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#reply_to_email_address CognitoUserPool#reply_to_email_address}.
        :param source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#source_arn CognitoUserPool#source_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolEmailConfiguration.__init__)
            check_type(argname="argument configuration_set", value=configuration_set, expected_type=type_hints["configuration_set"])
            check_type(argname="argument email_sending_account", value=email_sending_account, expected_type=type_hints["email_sending_account"])
            check_type(argname="argument from_email_address", value=from_email_address, expected_type=type_hints["from_email_address"])
            check_type(argname="argument reply_to_email_address", value=reply_to_email_address, expected_type=type_hints["reply_to_email_address"])
            check_type(argname="argument source_arn", value=source_arn, expected_type=type_hints["source_arn"])
        self._values: typing.Dict[str, typing.Any] = {}
        if configuration_set is not None:
            self._values["configuration_set"] = configuration_set
        if email_sending_account is not None:
            self._values["email_sending_account"] = email_sending_account
        if from_email_address is not None:
            self._values["from_email_address"] = from_email_address
        if reply_to_email_address is not None:
            self._values["reply_to_email_address"] = reply_to_email_address
        if source_arn is not None:
            self._values["source_arn"] = source_arn

    @builtins.property
    def configuration_set(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#configuration_set CognitoUserPool#configuration_set}.'''
        result = self._values.get("configuration_set")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_sending_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_sending_account CognitoUserPool#email_sending_account}.'''
        result = self._values.get("email_sending_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def from_email_address(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#from_email_address CognitoUserPool#from_email_address}.'''
        result = self._values.get("from_email_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def reply_to_email_address(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#reply_to_email_address CognitoUserPool#reply_to_email_address}.'''
        result = self._values.get("reply_to_email_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#source_arn CognitoUserPool#source_arn}.'''
        result = self._values.get("source_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolEmailConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolEmailConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolEmailConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolEmailConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConfigurationSet")
    def reset_configuration_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurationSet", []))

    @jsii.member(jsii_name="resetEmailSendingAccount")
    def reset_email_sending_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSendingAccount", []))

    @jsii.member(jsii_name="resetFromEmailAddress")
    def reset_from_email_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFromEmailAddress", []))

    @jsii.member(jsii_name="resetReplyToEmailAddress")
    def reset_reply_to_email_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplyToEmailAddress", []))

    @jsii.member(jsii_name="resetSourceArn")
    def reset_source_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceArn", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationSetInput")
    def configuration_set_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configurationSetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSendingAccountInput")
    def email_sending_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSendingAccountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromEmailAddressInput")
    def from_email_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromEmailAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replyToEmailAddressInput")
    def reply_to_email_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replyToEmailAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceArnInput")
    def source_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationSet")
    def configuration_set(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationSet"))

    @configuration_set.setter
    def configuration_set(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolEmailConfigurationOutputReference, "configuration_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configurationSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSendingAccount")
    def email_sending_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSendingAccount"))

    @email_sending_account.setter
    def email_sending_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolEmailConfigurationOutputReference, "email_sending_account").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailSendingAccount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromEmailAddress")
    def from_email_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fromEmailAddress"))

    @from_email_address.setter
    def from_email_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolEmailConfigurationOutputReference, "from_email_address").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fromEmailAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replyToEmailAddress")
    def reply_to_email_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replyToEmailAddress"))

    @reply_to_email_address.setter
    def reply_to_email_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolEmailConfigurationOutputReference, "reply_to_email_address").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replyToEmailAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceArn")
    def source_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceArn"))

    @source_arn.setter
    def source_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolEmailConfigurationOutputReference, "source_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolEmailConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolEmailConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolEmailConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolEmailConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfig",
    jsii_struct_bases=[],
    name_mapping={
        "create_auth_challenge": "createAuthChallenge",
        "custom_email_sender": "customEmailSender",
        "custom_message": "customMessage",
        "custom_sms_sender": "customSmsSender",
        "define_auth_challenge": "defineAuthChallenge",
        "kms_key_id": "kmsKeyId",
        "post_authentication": "postAuthentication",
        "post_confirmation": "postConfirmation",
        "pre_authentication": "preAuthentication",
        "pre_sign_up": "preSignUp",
        "pre_token_generation": "preTokenGeneration",
        "user_migration": "userMigration",
        "verify_auth_challenge_response": "verifyAuthChallengeResponse",
    },
)
class CognitoUserPoolLambdaConfig:
    def __init__(
        self,
        *,
        create_auth_challenge: typing.Optional[builtins.str] = None,
        custom_email_sender: typing.Optional[typing.Union["CognitoUserPoolLambdaConfigCustomEmailSender", typing.Dict[str, typing.Any]]] = None,
        custom_message: typing.Optional[builtins.str] = None,
        custom_sms_sender: typing.Optional[typing.Union["CognitoUserPoolLambdaConfigCustomSmsSender", typing.Dict[str, typing.Any]]] = None,
        define_auth_challenge: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        post_authentication: typing.Optional[builtins.str] = None,
        post_confirmation: typing.Optional[builtins.str] = None,
        pre_authentication: typing.Optional[builtins.str] = None,
        pre_sign_up: typing.Optional[builtins.str] = None,
        pre_token_generation: typing.Optional[builtins.str] = None,
        user_migration: typing.Optional[builtins.str] = None,
        verify_auth_challenge_response: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_auth_challenge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#create_auth_challenge CognitoUserPool#create_auth_challenge}.
        :param custom_email_sender: custom_email_sender block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_email_sender CognitoUserPool#custom_email_sender}
        :param custom_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_message CognitoUserPool#custom_message}.
        :param custom_sms_sender: custom_sms_sender block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_sms_sender CognitoUserPool#custom_sms_sender}
        :param define_auth_challenge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#define_auth_challenge CognitoUserPool#define_auth_challenge}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#kms_key_id CognitoUserPool#kms_key_id}.
        :param post_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_authentication CognitoUserPool#post_authentication}.
        :param post_confirmation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_confirmation CognitoUserPool#post_confirmation}.
        :param pre_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_authentication CognitoUserPool#pre_authentication}.
        :param pre_sign_up: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_sign_up CognitoUserPool#pre_sign_up}.
        :param pre_token_generation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_token_generation CognitoUserPool#pre_token_generation}.
        :param user_migration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_migration CognitoUserPool#user_migration}.
        :param verify_auth_challenge_response: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verify_auth_challenge_response CognitoUserPool#verify_auth_challenge_response}.
        '''
        if isinstance(custom_email_sender, dict):
            custom_email_sender = CognitoUserPoolLambdaConfigCustomEmailSender(**custom_email_sender)
        if isinstance(custom_sms_sender, dict):
            custom_sms_sender = CognitoUserPoolLambdaConfigCustomSmsSender(**custom_sms_sender)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolLambdaConfig.__init__)
            check_type(argname="argument create_auth_challenge", value=create_auth_challenge, expected_type=type_hints["create_auth_challenge"])
            check_type(argname="argument custom_email_sender", value=custom_email_sender, expected_type=type_hints["custom_email_sender"])
            check_type(argname="argument custom_message", value=custom_message, expected_type=type_hints["custom_message"])
            check_type(argname="argument custom_sms_sender", value=custom_sms_sender, expected_type=type_hints["custom_sms_sender"])
            check_type(argname="argument define_auth_challenge", value=define_auth_challenge, expected_type=type_hints["define_auth_challenge"])
            check_type(argname="argument kms_key_id", value=kms_key_id, expected_type=type_hints["kms_key_id"])
            check_type(argname="argument post_authentication", value=post_authentication, expected_type=type_hints["post_authentication"])
            check_type(argname="argument post_confirmation", value=post_confirmation, expected_type=type_hints["post_confirmation"])
            check_type(argname="argument pre_authentication", value=pre_authentication, expected_type=type_hints["pre_authentication"])
            check_type(argname="argument pre_sign_up", value=pre_sign_up, expected_type=type_hints["pre_sign_up"])
            check_type(argname="argument pre_token_generation", value=pre_token_generation, expected_type=type_hints["pre_token_generation"])
            check_type(argname="argument user_migration", value=user_migration, expected_type=type_hints["user_migration"])
            check_type(argname="argument verify_auth_challenge_response", value=verify_auth_challenge_response, expected_type=type_hints["verify_auth_challenge_response"])
        self._values: typing.Dict[str, typing.Any] = {}
        if create_auth_challenge is not None:
            self._values["create_auth_challenge"] = create_auth_challenge
        if custom_email_sender is not None:
            self._values["custom_email_sender"] = custom_email_sender
        if custom_message is not None:
            self._values["custom_message"] = custom_message
        if custom_sms_sender is not None:
            self._values["custom_sms_sender"] = custom_sms_sender
        if define_auth_challenge is not None:
            self._values["define_auth_challenge"] = define_auth_challenge
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if post_authentication is not None:
            self._values["post_authentication"] = post_authentication
        if post_confirmation is not None:
            self._values["post_confirmation"] = post_confirmation
        if pre_authentication is not None:
            self._values["pre_authentication"] = pre_authentication
        if pre_sign_up is not None:
            self._values["pre_sign_up"] = pre_sign_up
        if pre_token_generation is not None:
            self._values["pre_token_generation"] = pre_token_generation
        if user_migration is not None:
            self._values["user_migration"] = user_migration
        if verify_auth_challenge_response is not None:
            self._values["verify_auth_challenge_response"] = verify_auth_challenge_response

    @builtins.property
    def create_auth_challenge(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#create_auth_challenge CognitoUserPool#create_auth_challenge}.'''
        result = self._values.get("create_auth_challenge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_email_sender(
        self,
    ) -> typing.Optional["CognitoUserPoolLambdaConfigCustomEmailSender"]:
        '''custom_email_sender block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_email_sender CognitoUserPool#custom_email_sender}
        '''
        result = self._values.get("custom_email_sender")
        return typing.cast(typing.Optional["CognitoUserPoolLambdaConfigCustomEmailSender"], result)

    @builtins.property
    def custom_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_message CognitoUserPool#custom_message}.'''
        result = self._values.get("custom_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_sms_sender(
        self,
    ) -> typing.Optional["CognitoUserPoolLambdaConfigCustomSmsSender"]:
        '''custom_sms_sender block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_sms_sender CognitoUserPool#custom_sms_sender}
        '''
        result = self._values.get("custom_sms_sender")
        return typing.cast(typing.Optional["CognitoUserPoolLambdaConfigCustomSmsSender"], result)

    @builtins.property
    def define_auth_challenge(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#define_auth_challenge CognitoUserPool#define_auth_challenge}.'''
        result = self._values.get("define_auth_challenge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#kms_key_id CognitoUserPool#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_authentication(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_authentication CognitoUserPool#post_authentication}.'''
        result = self._values.get("post_authentication")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_confirmation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_confirmation CognitoUserPool#post_confirmation}.'''
        result = self._values.get("post_confirmation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_authentication(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_authentication CognitoUserPool#pre_authentication}.'''
        result = self._values.get("pre_authentication")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_sign_up(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_sign_up CognitoUserPool#pre_sign_up}.'''
        result = self._values.get("pre_sign_up")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_token_generation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_token_generation CognitoUserPool#pre_token_generation}.'''
        result = self._values.get("pre_token_generation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_migration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_migration CognitoUserPool#user_migration}.'''
        result = self._values.get("user_migration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verify_auth_challenge_response(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verify_auth_challenge_response CognitoUserPool#verify_auth_challenge_response}.'''
        result = self._values.get("verify_auth_challenge_response")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolLambdaConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfigCustomEmailSender",
    jsii_struct_bases=[],
    name_mapping={"lambda_arn": "lambdaArn", "lambda_version": "lambdaVersion"},
)
class CognitoUserPoolLambdaConfigCustomEmailSender:
    def __init__(
        self,
        *,
        lambda_arn: builtins.str,
        lambda_version: builtins.str,
    ) -> None:
        '''
        :param lambda_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.
        :param lambda_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolLambdaConfigCustomEmailSender.__init__)
            check_type(argname="argument lambda_arn", value=lambda_arn, expected_type=type_hints["lambda_arn"])
            check_type(argname="argument lambda_version", value=lambda_version, expected_type=type_hints["lambda_version"])
        self._values: typing.Dict[str, typing.Any] = {
            "lambda_arn": lambda_arn,
            "lambda_version": lambda_version,
        }

    @builtins.property
    def lambda_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.'''
        result = self._values.get("lambda_arn")
        assert result is not None, "Required property 'lambda_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.'''
        result = self._values.get("lambda_version")
        assert result is not None, "Required property 'lambda_version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolLambdaConfigCustomEmailSender(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaArnInput")
    def lambda_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaVersionInput")
    def lambda_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaArn")
    def lambda_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaArn"))

    @lambda_arn.setter
    def lambda_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference, "lambda_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lambdaArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaVersion")
    def lambda_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaVersion"))

    @lambda_version.setter
    def lambda_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference, "lambda_version").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lambdaVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolLambdaConfigCustomEmailSender]:
        return typing.cast(typing.Optional[CognitoUserPoolLambdaConfigCustomEmailSender], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolLambdaConfigCustomEmailSender],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfigCustomSmsSender",
    jsii_struct_bases=[],
    name_mapping={"lambda_arn": "lambdaArn", "lambda_version": "lambdaVersion"},
)
class CognitoUserPoolLambdaConfigCustomSmsSender:
    def __init__(
        self,
        *,
        lambda_arn: builtins.str,
        lambda_version: builtins.str,
    ) -> None:
        '''
        :param lambda_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.
        :param lambda_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolLambdaConfigCustomSmsSender.__init__)
            check_type(argname="argument lambda_arn", value=lambda_arn, expected_type=type_hints["lambda_arn"])
            check_type(argname="argument lambda_version", value=lambda_version, expected_type=type_hints["lambda_version"])
        self._values: typing.Dict[str, typing.Any] = {
            "lambda_arn": lambda_arn,
            "lambda_version": lambda_version,
        }

    @builtins.property
    def lambda_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.'''
        result = self._values.get("lambda_arn")
        assert result is not None, "Required property 'lambda_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.'''
        result = self._values.get("lambda_version")
        assert result is not None, "Required property 'lambda_version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolLambdaConfigCustomSmsSender(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaArnInput")
    def lambda_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaVersionInput")
    def lambda_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaArn")
    def lambda_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaArn"))

    @lambda_arn.setter
    def lambda_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference, "lambda_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lambdaArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaVersion")
    def lambda_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaVersion"))

    @lambda_version.setter
    def lambda_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference, "lambda_version").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lambdaVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolLambdaConfigCustomSmsSender]:
        return typing.cast(typing.Optional[CognitoUserPoolLambdaConfigCustomSmsSender], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolLambdaConfigCustomSmsSender],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoUserPoolLambdaConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfigOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolLambdaConfigOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCustomEmailSender")
    def put_custom_email_sender(
        self,
        *,
        lambda_arn: builtins.str,
        lambda_version: builtins.str,
    ) -> None:
        '''
        :param lambda_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.
        :param lambda_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.
        '''
        value = CognitoUserPoolLambdaConfigCustomEmailSender(
            lambda_arn=lambda_arn, lambda_version=lambda_version
        )

        return typing.cast(None, jsii.invoke(self, "putCustomEmailSender", [value]))

    @jsii.member(jsii_name="putCustomSmsSender")
    def put_custom_sms_sender(
        self,
        *,
        lambda_arn: builtins.str,
        lambda_version: builtins.str,
    ) -> None:
        '''
        :param lambda_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.
        :param lambda_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.
        '''
        value = CognitoUserPoolLambdaConfigCustomSmsSender(
            lambda_arn=lambda_arn, lambda_version=lambda_version
        )

        return typing.cast(None, jsii.invoke(self, "putCustomSmsSender", [value]))

    @jsii.member(jsii_name="resetCreateAuthChallenge")
    def reset_create_auth_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateAuthChallenge", []))

    @jsii.member(jsii_name="resetCustomEmailSender")
    def reset_custom_email_sender(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomEmailSender", []))

    @jsii.member(jsii_name="resetCustomMessage")
    def reset_custom_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomMessage", []))

    @jsii.member(jsii_name="resetCustomSmsSender")
    def reset_custom_sms_sender(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSmsSender", []))

    @jsii.member(jsii_name="resetDefineAuthChallenge")
    def reset_define_auth_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefineAuthChallenge", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetPostAuthentication")
    def reset_post_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostAuthentication", []))

    @jsii.member(jsii_name="resetPostConfirmation")
    def reset_post_confirmation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostConfirmation", []))

    @jsii.member(jsii_name="resetPreAuthentication")
    def reset_pre_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreAuthentication", []))

    @jsii.member(jsii_name="resetPreSignUp")
    def reset_pre_sign_up(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreSignUp", []))

    @jsii.member(jsii_name="resetPreTokenGeneration")
    def reset_pre_token_generation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreTokenGeneration", []))

    @jsii.member(jsii_name="resetUserMigration")
    def reset_user_migration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserMigration", []))

    @jsii.member(jsii_name="resetVerifyAuthChallengeResponse")
    def reset_verify_auth_challenge_response(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerifyAuthChallengeResponse", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customEmailSender")
    def custom_email_sender(
        self,
    ) -> CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference:
        return typing.cast(CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference, jsii.get(self, "customEmailSender"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSmsSender")
    def custom_sms_sender(
        self,
    ) -> CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference:
        return typing.cast(CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference, jsii.get(self, "customSmsSender"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createAuthChallengeInput")
    def create_auth_challenge_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createAuthChallengeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customEmailSenderInput")
    def custom_email_sender_input(
        self,
    ) -> typing.Optional[CognitoUserPoolLambdaConfigCustomEmailSender]:
        return typing.cast(typing.Optional[CognitoUserPoolLambdaConfigCustomEmailSender], jsii.get(self, "customEmailSenderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customMessageInput")
    def custom_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSmsSenderInput")
    def custom_sms_sender_input(
        self,
    ) -> typing.Optional[CognitoUserPoolLambdaConfigCustomSmsSender]:
        return typing.cast(typing.Optional[CognitoUserPoolLambdaConfigCustomSmsSender], jsii.get(self, "customSmsSenderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defineAuthChallengeInput")
    def define_auth_challenge_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defineAuthChallengeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postAuthenticationInput")
    def post_authentication_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postAuthenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postConfirmationInput")
    def post_confirmation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postConfirmationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preAuthenticationInput")
    def pre_authentication_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preAuthenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preSignUpInput")
    def pre_sign_up_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preSignUpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preTokenGenerationInput")
    def pre_token_generation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preTokenGenerationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userMigrationInput")
    def user_migration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userMigrationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifyAuthChallengeResponseInput")
    def verify_auth_challenge_response_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "verifyAuthChallengeResponseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createAuthChallenge")
    def create_auth_challenge(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createAuthChallenge"))

    @create_auth_challenge.setter
    def create_auth_challenge(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "create_auth_challenge").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createAuthChallenge", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customMessage")
    def custom_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customMessage"))

    @custom_message.setter
    def custom_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "custom_message").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defineAuthChallenge")
    def define_auth_challenge(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defineAuthChallenge"))

    @define_auth_challenge.setter
    def define_auth_challenge(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "define_auth_challenge").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defineAuthChallenge", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "kms_key_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postAuthentication")
    def post_authentication(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postAuthentication"))

    @post_authentication.setter
    def post_authentication(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "post_authentication").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postAuthentication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postConfirmation")
    def post_confirmation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postConfirmation"))

    @post_confirmation.setter
    def post_confirmation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "post_confirmation").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postConfirmation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preAuthentication")
    def pre_authentication(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preAuthentication"))

    @pre_authentication.setter
    def pre_authentication(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "pre_authentication").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preAuthentication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preSignUp")
    def pre_sign_up(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preSignUp"))

    @pre_sign_up.setter
    def pre_sign_up(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "pre_sign_up").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preSignUp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preTokenGeneration")
    def pre_token_generation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preTokenGeneration"))

    @pre_token_generation.setter
    def pre_token_generation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "pre_token_generation").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preTokenGeneration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userMigration")
    def user_migration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userMigration"))

    @user_migration.setter
    def user_migration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "user_migration").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userMigration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifyAuthChallengeResponse")
    def verify_auth_challenge_response(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "verifyAuthChallengeResponse"))

    @verify_auth_challenge_response.setter
    def verify_auth_challenge_response(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "verify_auth_challenge_response").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "verifyAuthChallengeResponse", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolLambdaConfig]:
        return typing.cast(typing.Optional[CognitoUserPoolLambdaConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolLambdaConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolLambdaConfigOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolPasswordPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "minimum_length": "minimumLength",
        "require_lowercase": "requireLowercase",
        "require_numbers": "requireNumbers",
        "require_symbols": "requireSymbols",
        "require_uppercase": "requireUppercase",
        "temporary_password_validity_days": "temporaryPasswordValidityDays",
    },
)
class CognitoUserPoolPasswordPolicy:
    def __init__(
        self,
        *,
        minimum_length: typing.Optional[jsii.Number] = None,
        require_lowercase: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_numbers: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_symbols: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_uppercase: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        temporary_password_validity_days: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param minimum_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#minimum_length CognitoUserPool#minimum_length}.
        :param require_lowercase: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_lowercase CognitoUserPool#require_lowercase}.
        :param require_numbers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_numbers CognitoUserPool#require_numbers}.
        :param require_symbols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_symbols CognitoUserPool#require_symbols}.
        :param require_uppercase: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_uppercase CognitoUserPool#require_uppercase}.
        :param temporary_password_validity_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#temporary_password_validity_days CognitoUserPool#temporary_password_validity_days}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolPasswordPolicy.__init__)
            check_type(argname="argument minimum_length", value=minimum_length, expected_type=type_hints["minimum_length"])
            check_type(argname="argument require_lowercase", value=require_lowercase, expected_type=type_hints["require_lowercase"])
            check_type(argname="argument require_numbers", value=require_numbers, expected_type=type_hints["require_numbers"])
            check_type(argname="argument require_symbols", value=require_symbols, expected_type=type_hints["require_symbols"])
            check_type(argname="argument require_uppercase", value=require_uppercase, expected_type=type_hints["require_uppercase"])
            check_type(argname="argument temporary_password_validity_days", value=temporary_password_validity_days, expected_type=type_hints["temporary_password_validity_days"])
        self._values: typing.Dict[str, typing.Any] = {}
        if minimum_length is not None:
            self._values["minimum_length"] = minimum_length
        if require_lowercase is not None:
            self._values["require_lowercase"] = require_lowercase
        if require_numbers is not None:
            self._values["require_numbers"] = require_numbers
        if require_symbols is not None:
            self._values["require_symbols"] = require_symbols
        if require_uppercase is not None:
            self._values["require_uppercase"] = require_uppercase
        if temporary_password_validity_days is not None:
            self._values["temporary_password_validity_days"] = temporary_password_validity_days

    @builtins.property
    def minimum_length(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#minimum_length CognitoUserPool#minimum_length}.'''
        result = self._values.get("minimum_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def require_lowercase(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_lowercase CognitoUserPool#require_lowercase}.'''
        result = self._values.get("require_lowercase")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def require_numbers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_numbers CognitoUserPool#require_numbers}.'''
        result = self._values.get("require_numbers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def require_symbols(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_symbols CognitoUserPool#require_symbols}.'''
        result = self._values.get("require_symbols")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def require_uppercase(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_uppercase CognitoUserPool#require_uppercase}.'''
        result = self._values.get("require_uppercase")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def temporary_password_validity_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#temporary_password_validity_days CognitoUserPool#temporary_password_validity_days}.'''
        result = self._values.get("temporary_password_validity_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolPasswordPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolPasswordPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolPasswordPolicyOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolPasswordPolicyOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMinimumLength")
    def reset_minimum_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumLength", []))

    @jsii.member(jsii_name="resetRequireLowercase")
    def reset_require_lowercase(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireLowercase", []))

    @jsii.member(jsii_name="resetRequireNumbers")
    def reset_require_numbers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireNumbers", []))

    @jsii.member(jsii_name="resetRequireSymbols")
    def reset_require_symbols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireSymbols", []))

    @jsii.member(jsii_name="resetRequireUppercase")
    def reset_require_uppercase(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireUppercase", []))

    @jsii.member(jsii_name="resetTemporaryPasswordValidityDays")
    def reset_temporary_password_validity_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemporaryPasswordValidityDays", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumLengthInput")
    def minimum_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minimumLengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireLowercaseInput")
    def require_lowercase_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireLowercaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireNumbersInput")
    def require_numbers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireNumbersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireSymbolsInput")
    def require_symbols_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireSymbolsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireUppercaseInput")
    def require_uppercase_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireUppercaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="temporaryPasswordValidityDaysInput")
    def temporary_password_validity_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "temporaryPasswordValidityDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumLength")
    def minimum_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minimumLength"))

    @minimum_length.setter
    def minimum_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolPasswordPolicyOutputReference, "minimum_length").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimumLength", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireLowercase")
    def require_lowercase(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireLowercase"))

    @require_lowercase.setter
    def require_lowercase(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolPasswordPolicyOutputReference, "require_lowercase").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireLowercase", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireNumbers")
    def require_numbers(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireNumbers"))

    @require_numbers.setter
    def require_numbers(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolPasswordPolicyOutputReference, "require_numbers").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireNumbers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireSymbols")
    def require_symbols(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireSymbols"))

    @require_symbols.setter
    def require_symbols(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolPasswordPolicyOutputReference, "require_symbols").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireSymbols", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireUppercase")
    def require_uppercase(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireUppercase"))

    @require_uppercase.setter
    def require_uppercase(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolPasswordPolicyOutputReference, "require_uppercase").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireUppercase", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="temporaryPasswordValidityDays")
    def temporary_password_validity_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "temporaryPasswordValidityDays"))

    @temporary_password_validity_days.setter
    def temporary_password_validity_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolPasswordPolicyOutputReference, "temporary_password_validity_days").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "temporaryPasswordValidityDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolPasswordPolicy]:
        return typing.cast(typing.Optional[CognitoUserPoolPasswordPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolPasswordPolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolPasswordPolicyOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchema",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_data_type": "attributeDataType",
        "name": "name",
        "developer_only_attribute": "developerOnlyAttribute",
        "mutable": "mutable",
        "number_attribute_constraints": "numberAttributeConstraints",
        "required": "required",
        "string_attribute_constraints": "stringAttributeConstraints",
    },
)
class CognitoUserPoolSchema:
    def __init__(
        self,
        *,
        attribute_data_type: builtins.str,
        name: builtins.str,
        developer_only_attribute: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        mutable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        number_attribute_constraints: typing.Optional[typing.Union["CognitoUserPoolSchemaNumberAttributeConstraints", typing.Dict[str, typing.Any]]] = None,
        required: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        string_attribute_constraints: typing.Optional[typing.Union["CognitoUserPoolSchemaStringAttributeConstraints", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param attribute_data_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#attribute_data_type CognitoUserPool#attribute_data_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.
        :param developer_only_attribute: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#developer_only_attribute CognitoUserPool#developer_only_attribute}.
        :param mutable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#mutable CognitoUserPool#mutable}.
        :param number_attribute_constraints: number_attribute_constraints block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#number_attribute_constraints CognitoUserPool#number_attribute_constraints}
        :param required: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#required CognitoUserPool#required}.
        :param string_attribute_constraints: string_attribute_constraints block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#string_attribute_constraints CognitoUserPool#string_attribute_constraints}
        '''
        if isinstance(number_attribute_constraints, dict):
            number_attribute_constraints = CognitoUserPoolSchemaNumberAttributeConstraints(**number_attribute_constraints)
        if isinstance(string_attribute_constraints, dict):
            string_attribute_constraints = CognitoUserPoolSchemaStringAttributeConstraints(**string_attribute_constraints)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolSchema.__init__)
            check_type(argname="argument attribute_data_type", value=attribute_data_type, expected_type=type_hints["attribute_data_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument developer_only_attribute", value=developer_only_attribute, expected_type=type_hints["developer_only_attribute"])
            check_type(argname="argument mutable", value=mutable, expected_type=type_hints["mutable"])
            check_type(argname="argument number_attribute_constraints", value=number_attribute_constraints, expected_type=type_hints["number_attribute_constraints"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
            check_type(argname="argument string_attribute_constraints", value=string_attribute_constraints, expected_type=type_hints["string_attribute_constraints"])
        self._values: typing.Dict[str, typing.Any] = {
            "attribute_data_type": attribute_data_type,
            "name": name,
        }
        if developer_only_attribute is not None:
            self._values["developer_only_attribute"] = developer_only_attribute
        if mutable is not None:
            self._values["mutable"] = mutable
        if number_attribute_constraints is not None:
            self._values["number_attribute_constraints"] = number_attribute_constraints
        if required is not None:
            self._values["required"] = required
        if string_attribute_constraints is not None:
            self._values["string_attribute_constraints"] = string_attribute_constraints

    @builtins.property
    def attribute_data_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#attribute_data_type CognitoUserPool#attribute_data_type}.'''
        result = self._values.get("attribute_data_type")
        assert result is not None, "Required property 'attribute_data_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def developer_only_attribute(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#developer_only_attribute CognitoUserPool#developer_only_attribute}.'''
        result = self._values.get("developer_only_attribute")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def mutable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#mutable CognitoUserPool#mutable}.'''
        result = self._values.get("mutable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def number_attribute_constraints(
        self,
    ) -> typing.Optional["CognitoUserPoolSchemaNumberAttributeConstraints"]:
        '''number_attribute_constraints block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#number_attribute_constraints CognitoUserPool#number_attribute_constraints}
        '''
        result = self._values.get("number_attribute_constraints")
        return typing.cast(typing.Optional["CognitoUserPoolSchemaNumberAttributeConstraints"], result)

    @builtins.property
    def required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#required CognitoUserPool#required}.'''
        result = self._values.get("required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def string_attribute_constraints(
        self,
    ) -> typing.Optional["CognitoUserPoolSchemaStringAttributeConstraints"]:
        '''string_attribute_constraints block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#string_attribute_constraints CognitoUserPool#string_attribute_constraints}
        '''
        result = self._values.get("string_attribute_constraints")
        return typing.cast(typing.Optional["CognitoUserPoolSchemaStringAttributeConstraints"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolSchema(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolSchemaList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchemaList",
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
            type_hints = typing.get_type_hints(CognitoUserPoolSchemaList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "CognitoUserPoolSchemaOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolSchemaList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CognitoUserPoolSchemaOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoUserPoolSchema]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoUserPoolSchema]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CognitoUserPoolSchema]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchemaNumberAttributeConstraints",
    jsii_struct_bases=[],
    name_mapping={"max_value": "maxValue", "min_value": "minValue"},
)
class CognitoUserPoolSchemaNumberAttributeConstraints:
    def __init__(
        self,
        *,
        max_value: typing.Optional[builtins.str] = None,
        min_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#max_value CognitoUserPool#max_value}.
        :param min_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#min_value CognitoUserPool#min_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolSchemaNumberAttributeConstraints.__init__)
            check_type(argname="argument max_value", value=max_value, expected_type=type_hints["max_value"])
            check_type(argname="argument min_value", value=min_value, expected_type=type_hints["min_value"])
        self._values: typing.Dict[str, typing.Any] = {}
        if max_value is not None:
            self._values["max_value"] = max_value
        if min_value is not None:
            self._values["min_value"] = min_value

    @builtins.property
    def max_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#max_value CognitoUserPool#max_value}.'''
        result = self._values.get("max_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#min_value CognitoUserPool#min_value}.'''
        result = self._values.get("min_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolSchemaNumberAttributeConstraints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxValue")
    def reset_max_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxValue", []))

    @jsii.member(jsii_name="resetMinValue")
    def reset_min_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxValueInput")
    def max_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minValueInput")
    def min_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxValue")
    def max_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxValue"))

    @max_value.setter
    def max_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference, "max_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minValue")
    def min_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minValue"))

    @min_value.setter
    def min_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference, "min_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolSchemaNumberAttributeConstraints]:
        return typing.cast(typing.Optional[CognitoUserPoolSchemaNumberAttributeConstraints], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolSchemaNumberAttributeConstraints],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoUserPoolSchemaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchemaOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolSchemaOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putNumberAttributeConstraints")
    def put_number_attribute_constraints(
        self,
        *,
        max_value: typing.Optional[builtins.str] = None,
        min_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#max_value CognitoUserPool#max_value}.
        :param min_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#min_value CognitoUserPool#min_value}.
        '''
        value = CognitoUserPoolSchemaNumberAttributeConstraints(
            max_value=max_value, min_value=min_value
        )

        return typing.cast(None, jsii.invoke(self, "putNumberAttributeConstraints", [value]))

    @jsii.member(jsii_name="putStringAttributeConstraints")
    def put_string_attribute_constraints(
        self,
        *,
        max_length: typing.Optional[builtins.str] = None,
        min_length: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#max_length CognitoUserPool#max_length}.
        :param min_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#min_length CognitoUserPool#min_length}.
        '''
        value = CognitoUserPoolSchemaStringAttributeConstraints(
            max_length=max_length, min_length=min_length
        )

        return typing.cast(None, jsii.invoke(self, "putStringAttributeConstraints", [value]))

    @jsii.member(jsii_name="resetDeveloperOnlyAttribute")
    def reset_developer_only_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeveloperOnlyAttribute", []))

    @jsii.member(jsii_name="resetMutable")
    def reset_mutable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMutable", []))

    @jsii.member(jsii_name="resetNumberAttributeConstraints")
    def reset_number_attribute_constraints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberAttributeConstraints", []))

    @jsii.member(jsii_name="resetRequired")
    def reset_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequired", []))

    @jsii.member(jsii_name="resetStringAttributeConstraints")
    def reset_string_attribute_constraints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStringAttributeConstraints", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberAttributeConstraints")
    def number_attribute_constraints(
        self,
    ) -> CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference:
        return typing.cast(CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference, jsii.get(self, "numberAttributeConstraints"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringAttributeConstraints")
    def string_attribute_constraints(
        self,
    ) -> "CognitoUserPoolSchemaStringAttributeConstraintsOutputReference":
        return typing.cast("CognitoUserPoolSchemaStringAttributeConstraintsOutputReference", jsii.get(self, "stringAttributeConstraints"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeDataTypeInput")
    def attribute_data_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeDataTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="developerOnlyAttributeInput")
    def developer_only_attribute_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "developerOnlyAttributeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mutableInput")
    def mutable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "mutableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberAttributeConstraintsInput")
    def number_attribute_constraints_input(
        self,
    ) -> typing.Optional[CognitoUserPoolSchemaNumberAttributeConstraints]:
        return typing.cast(typing.Optional[CognitoUserPoolSchemaNumberAttributeConstraints], jsii.get(self, "numberAttributeConstraintsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requiredInput")
    def required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requiredInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringAttributeConstraintsInput")
    def string_attribute_constraints_input(
        self,
    ) -> typing.Optional["CognitoUserPoolSchemaStringAttributeConstraints"]:
        return typing.cast(typing.Optional["CognitoUserPoolSchemaStringAttributeConstraints"], jsii.get(self, "stringAttributeConstraintsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeDataType")
    def attribute_data_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeDataType"))

    @attribute_data_type.setter
    def attribute_data_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaOutputReference, "attribute_data_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeDataType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="developerOnlyAttribute")
    def developer_only_attribute(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "developerOnlyAttribute"))

    @developer_only_attribute.setter
    def developer_only_attribute(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaOutputReference, "developer_only_attribute").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "developerOnlyAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mutable")
    def mutable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "mutable"))

    @mutable.setter
    def mutable(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaOutputReference, "mutable").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mutable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaOutputReference, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="required")
    def required(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "required"))

    @required.setter
    def required(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaOutputReference, "required").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "required", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[CognitoUserPoolSchema, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[CognitoUserPoolSchema, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[CognitoUserPoolSchema, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchemaStringAttributeConstraints",
    jsii_struct_bases=[],
    name_mapping={"max_length": "maxLength", "min_length": "minLength"},
)
class CognitoUserPoolSchemaStringAttributeConstraints:
    def __init__(
        self,
        *,
        max_length: typing.Optional[builtins.str] = None,
        min_length: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#max_length CognitoUserPool#max_length}.
        :param min_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#min_length CognitoUserPool#min_length}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolSchemaStringAttributeConstraints.__init__)
            check_type(argname="argument max_length", value=max_length, expected_type=type_hints["max_length"])
            check_type(argname="argument min_length", value=min_length, expected_type=type_hints["min_length"])
        self._values: typing.Dict[str, typing.Any] = {}
        if max_length is not None:
            self._values["max_length"] = max_length
        if min_length is not None:
            self._values["min_length"] = min_length

    @builtins.property
    def max_length(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#max_length CognitoUserPool#max_length}.'''
        result = self._values.get("max_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_length(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#min_length CognitoUserPool#min_length}.'''
        result = self._values.get("min_length")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolSchemaStringAttributeConstraints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolSchemaStringAttributeConstraintsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchemaStringAttributeConstraintsOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolSchemaStringAttributeConstraintsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxLength")
    def reset_max_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLength", []))

    @jsii.member(jsii_name="resetMinLength")
    def reset_min_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinLength", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxLengthInput")
    def max_length_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxLengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minLengthInput")
    def min_length_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minLengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxLength")
    def max_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxLength"))

    @max_length.setter
    def max_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaStringAttributeConstraintsOutputReference, "max_length").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLength", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minLength")
    def min_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minLength"))

    @min_length.setter
    def min_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaStringAttributeConstraintsOutputReference, "min_length").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minLength", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolSchemaStringAttributeConstraints]:
        return typing.cast(typing.Optional[CognitoUserPoolSchemaStringAttributeConstraints], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolSchemaStringAttributeConstraints],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSchemaStringAttributeConstraintsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSmsConfiguration",
    jsii_struct_bases=[],
    name_mapping={"external_id": "externalId", "sns_caller_arn": "snsCallerArn"},
)
class CognitoUserPoolSmsConfiguration:
    def __init__(
        self,
        *,
        external_id: builtins.str,
        sns_caller_arn: builtins.str,
    ) -> None:
        '''
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#external_id CognitoUserPool#external_id}.
        :param sns_caller_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sns_caller_arn CognitoUserPool#sns_caller_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolSmsConfiguration.__init__)
            check_type(argname="argument external_id", value=external_id, expected_type=type_hints["external_id"])
            check_type(argname="argument sns_caller_arn", value=sns_caller_arn, expected_type=type_hints["sns_caller_arn"])
        self._values: typing.Dict[str, typing.Any] = {
            "external_id": external_id,
            "sns_caller_arn": sns_caller_arn,
        }

    @builtins.property
    def external_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#external_id CognitoUserPool#external_id}.'''
        result = self._values.get("external_id")
        assert result is not None, "Required property 'external_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sns_caller_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sns_caller_arn CognitoUserPool#sns_caller_arn}.'''
        result = self._values.get("sns_caller_arn")
        assert result is not None, "Required property 'sns_caller_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolSmsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolSmsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSmsConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolSmsConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalIdInput")
    def external_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsCallerArnInput")
    def sns_caller_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsCallerArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @external_id.setter
    def external_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSmsConfigurationOutputReference, "external_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "externalId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsCallerArn")
    def sns_caller_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsCallerArn"))

    @sns_caller_arn.setter
    def sns_caller_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSmsConfigurationOutputReference, "sns_caller_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "snsCallerArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolSmsConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolSmsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolSmsConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSmsConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSoftwareTokenMfaConfiguration",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class CognitoUserPoolSoftwareTokenMfaConfiguration:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#enabled CognitoUserPool#enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolSoftwareTokenMfaConfiguration.__init__)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#enabled CognitoUserPool#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolSoftwareTokenMfaConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference, "enabled").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolSoftwareTokenMfaConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolSoftwareTokenMfaConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolSoftwareTokenMfaConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CognitoUserPoolUiCustomization(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUiCustomization",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization aws_cognito_user_pool_ui_customization}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        user_pool_id: builtins.str,
        client_id: typing.Optional[builtins.str] = None,
        css: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        image_file: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization aws_cognito_user_pool_ui_customization} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#user_pool_id CognitoUserPoolUiCustomization#user_pool_id}.
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#client_id CognitoUserPoolUiCustomization#client_id}.
        :param css: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#css CognitoUserPoolUiCustomization#css}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#id CognitoUserPoolUiCustomization#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#image_file CognitoUserPoolUiCustomization#image_file}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolUiCustomization.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CognitoUserPoolUiCustomizationConfig(
            user_pool_id=user_pool_id,
            client_id=client_id,
            css=css,
            id=id,
            image_file=image_file,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetCss")
    def reset_css(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCss", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetImageFile")
    def reset_image_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageFile", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationDate")
    def creation_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cssVersion")
    def css_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cssVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageUrl")
    def image_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedDate")
    def last_modified_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cssInput")
    def css_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cssInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageFileInput")
    def image_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageFileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolUiCustomization, "client_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="css")
    def css(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "css"))

    @css.setter
    def css(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolUiCustomization, "css").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "css", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolUiCustomization, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageFile")
    def image_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageFile"))

    @image_file.setter
    def image_file(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolUiCustomization, "image_file").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageFile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolUiCustomization, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUiCustomizationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "user_pool_id": "userPoolId",
        "client_id": "clientId",
        "css": "css",
        "id": "id",
        "image_file": "imageFile",
    },
)
class CognitoUserPoolUiCustomizationConfig(cdktf.TerraformMetaArguments):
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
        user_pool_id: builtins.str,
        client_id: typing.Optional[builtins.str] = None,
        css: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        image_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#user_pool_id CognitoUserPoolUiCustomization#user_pool_id}.
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#client_id CognitoUserPoolUiCustomization#client_id}.
        :param css: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#css CognitoUserPoolUiCustomization#css}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#id CognitoUserPoolUiCustomization#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#image_file CognitoUserPoolUiCustomization#image_file}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolUiCustomizationConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument css", value=css, expected_type=type_hints["css"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument image_file", value=image_file, expected_type=type_hints["image_file"])
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool_id": user_pool_id,
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
        if client_id is not None:
            self._values["client_id"] = client_id
        if css is not None:
            self._values["css"] = css
        if id is not None:
            self._values["id"] = id
        if image_file is not None:
            self._values["image_file"] = image_file

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
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#user_pool_id CognitoUserPoolUiCustomization#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#client_id CognitoUserPoolUiCustomization#client_id}.'''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def css(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#css CognitoUserPoolUiCustomization#css}.'''
        result = self._values.get("css")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#id CognitoUserPoolUiCustomization#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_file(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#image_file CognitoUserPoolUiCustomization#image_file}.'''
        result = self._values.get("image_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolUiCustomizationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUserPoolAddOns",
    jsii_struct_bases=[],
    name_mapping={"advanced_security_mode": "advancedSecurityMode"},
)
class CognitoUserPoolUserPoolAddOns:
    def __init__(self, *, advanced_security_mode: builtins.str) -> None:
        '''
        :param advanced_security_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#advanced_security_mode CognitoUserPool#advanced_security_mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolUserPoolAddOns.__init__)
            check_type(argname="argument advanced_security_mode", value=advanced_security_mode, expected_type=type_hints["advanced_security_mode"])
        self._values: typing.Dict[str, typing.Any] = {
            "advanced_security_mode": advanced_security_mode,
        }

    @builtins.property
    def advanced_security_mode(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#advanced_security_mode CognitoUserPool#advanced_security_mode}.'''
        result = self._values.get("advanced_security_mode")
        assert result is not None, "Required property 'advanced_security_mode' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolUserPoolAddOns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolUserPoolAddOnsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUserPoolAddOnsOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolUserPoolAddOnsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="advancedSecurityModeInput")
    def advanced_security_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "advancedSecurityModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="advancedSecurityMode")
    def advanced_security_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "advancedSecurityMode"))

    @advanced_security_mode.setter
    def advanced_security_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolUserPoolAddOnsOutputReference, "advanced_security_mode").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "advancedSecurityMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolUserPoolAddOns]:
        return typing.cast(typing.Optional[CognitoUserPoolUserPoolAddOns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolUserPoolAddOns],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolUserPoolAddOnsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUsernameConfiguration",
    jsii_struct_bases=[],
    name_mapping={"case_sensitive": "caseSensitive"},
)
class CognitoUserPoolUsernameConfiguration:
    def __init__(
        self,
        *,
        case_sensitive: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param case_sensitive: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#case_sensitive CognitoUserPool#case_sensitive}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolUsernameConfiguration.__init__)
            check_type(argname="argument case_sensitive", value=case_sensitive, expected_type=type_hints["case_sensitive"])
        self._values: typing.Dict[str, typing.Any] = {
            "case_sensitive": case_sensitive,
        }

    @builtins.property
    def case_sensitive(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#case_sensitive CognitoUserPool#case_sensitive}.'''
        result = self._values.get("case_sensitive")
        assert result is not None, "Required property 'case_sensitive' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolUsernameConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolUsernameConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUsernameConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolUsernameConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caseSensitiveInput")
    def case_sensitive_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "caseSensitiveInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caseSensitive")
    def case_sensitive(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "caseSensitive"))

    @case_sensitive.setter
    def case_sensitive(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolUsernameConfigurationOutputReference, "case_sensitive").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caseSensitive", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolUsernameConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolUsernameConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolUsernameConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolUsernameConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolVerificationMessageTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "default_email_option": "defaultEmailOption",
        "email_message": "emailMessage",
        "email_message_by_link": "emailMessageByLink",
        "email_subject": "emailSubject",
        "email_subject_by_link": "emailSubjectByLink",
        "sms_message": "smsMessage",
    },
)
class CognitoUserPoolVerificationMessageTemplate:
    def __init__(
        self,
        *,
        default_email_option: typing.Optional[builtins.str] = None,
        email_message: typing.Optional[builtins.str] = None,
        email_message_by_link: typing.Optional[builtins.str] = None,
        email_subject: typing.Optional[builtins.str] = None,
        email_subject_by_link: typing.Optional[builtins.str] = None,
        sms_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_email_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#default_email_option CognitoUserPool#default_email_option}.
        :param email_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.
        :param email_message_by_link: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message_by_link CognitoUserPool#email_message_by_link}.
        :param email_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.
        :param email_subject_by_link: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject_by_link CognitoUserPool#email_subject_by_link}.
        :param sms_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CognitoUserPoolVerificationMessageTemplate.__init__)
            check_type(argname="argument default_email_option", value=default_email_option, expected_type=type_hints["default_email_option"])
            check_type(argname="argument email_message", value=email_message, expected_type=type_hints["email_message"])
            check_type(argname="argument email_message_by_link", value=email_message_by_link, expected_type=type_hints["email_message_by_link"])
            check_type(argname="argument email_subject", value=email_subject, expected_type=type_hints["email_subject"])
            check_type(argname="argument email_subject_by_link", value=email_subject_by_link, expected_type=type_hints["email_subject_by_link"])
            check_type(argname="argument sms_message", value=sms_message, expected_type=type_hints["sms_message"])
        self._values: typing.Dict[str, typing.Any] = {}
        if default_email_option is not None:
            self._values["default_email_option"] = default_email_option
        if email_message is not None:
            self._values["email_message"] = email_message
        if email_message_by_link is not None:
            self._values["email_message_by_link"] = email_message_by_link
        if email_subject is not None:
            self._values["email_subject"] = email_subject
        if email_subject_by_link is not None:
            self._values["email_subject_by_link"] = email_subject_by_link
        if sms_message is not None:
            self._values["sms_message"] = sms_message

    @builtins.property
    def default_email_option(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#default_email_option CognitoUserPool#default_email_option}.'''
        result = self._values.get("default_email_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.'''
        result = self._values.get("email_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_message_by_link(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message_by_link CognitoUserPool#email_message_by_link}.'''
        result = self._values.get("email_message_by_link")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_subject(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.'''
        result = self._values.get("email_subject")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_subject_by_link(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject_by_link CognitoUserPool#email_subject_by_link}.'''
        result = self._values.get("email_subject_by_link")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sms_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.'''
        result = self._values.get("sms_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolVerificationMessageTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolVerificationMessageTemplateOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolVerificationMessageTemplateOutputReference",
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
            type_hints = typing.get_type_hints(CognitoUserPoolVerificationMessageTemplateOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDefaultEmailOption")
    def reset_default_email_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultEmailOption", []))

    @jsii.member(jsii_name="resetEmailMessage")
    def reset_email_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailMessage", []))

    @jsii.member(jsii_name="resetEmailMessageByLink")
    def reset_email_message_by_link(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailMessageByLink", []))

    @jsii.member(jsii_name="resetEmailSubject")
    def reset_email_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSubject", []))

    @jsii.member(jsii_name="resetEmailSubjectByLink")
    def reset_email_subject_by_link(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSubjectByLink", []))

    @jsii.member(jsii_name="resetSmsMessage")
    def reset_sms_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsMessage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultEmailOptionInput")
    def default_email_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultEmailOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessageByLinkInput")
    def email_message_by_link_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailMessageByLinkInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessageInput")
    def email_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubjectByLinkInput")
    def email_subject_by_link_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSubjectByLinkInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubjectInput")
    def email_subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSubjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsMessageInput")
    def sms_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smsMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultEmailOption")
    def default_email_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultEmailOption"))

    @default_email_option.setter
    def default_email_option(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolVerificationMessageTemplateOutputReference, "default_email_option").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultEmailOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessage")
    def email_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailMessage"))

    @email_message.setter
    def email_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolVerificationMessageTemplateOutputReference, "email_message").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessageByLink")
    def email_message_by_link(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailMessageByLink"))

    @email_message_by_link.setter
    def email_message_by_link(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolVerificationMessageTemplateOutputReference, "email_message_by_link").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailMessageByLink", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubject")
    def email_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSubject"))

    @email_subject.setter
    def email_subject(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolVerificationMessageTemplateOutputReference, "email_subject").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailSubject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubjectByLink")
    def email_subject_by_link(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSubjectByLink"))

    @email_subject_by_link.setter
    def email_subject_by_link(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolVerificationMessageTemplateOutputReference, "email_subject_by_link").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailSubjectByLink", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsMessage")
    def sms_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smsMessage"))

    @sms_message.setter
    def sms_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolVerificationMessageTemplateOutputReference, "sms_message").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smsMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolVerificationMessageTemplate]:
        return typing.cast(typing.Optional[CognitoUserPoolVerificationMessageTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolVerificationMessageTemplate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CognitoUserPoolVerificationMessageTemplateOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAwsCognitoUserPoolClient(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClient",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client aws_cognito_user_pool_client}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        client_id: builtins.str,
        user_pool_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client aws_cognito_user_pool_client} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#client_id DataAwsCognitoUserPoolClient#client_id}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#user_pool_id DataAwsCognitoUserPoolClient#user_pool_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#id DataAwsCognitoUserPoolClient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolClient.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsCognitoUserPoolClientConfig(
            client_id=client_id,
            user_pool_id=user_pool_id,
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
    @jsii.member(jsii_name="accessTokenValidity")
    def access_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessTokenValidity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlows")
    def allowed_oauth_flows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOauthFlows"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlowsUserPoolClient")
    def allowed_oauth_flows_user_pool_client(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "allowedOauthFlowsUserPoolClient"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthScopes")
    def allowed_oauth_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOauthScopes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="analyticsConfiguration")
    def analytics_configuration(
        self,
    ) -> "DataAwsCognitoUserPoolClientAnalyticsConfigurationList":
        return typing.cast("DataAwsCognitoUserPoolClientAnalyticsConfigurationList", jsii.get(self, "analyticsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callbackUrls")
    def callback_urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "callbackUrls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRedirectUri")
    def default_redirect_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultRedirectUri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePropagateAdditionalUserContextData")
    def enable_propagate_additional_user_context_data(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "enablePropagateAdditionalUserContextData"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableTokenRevocation")
    def enable_token_revocation(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "enableTokenRevocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="explicitAuthFlows")
    def explicit_auth_flows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "explicitAuthFlows"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generateSecret")
    def generate_secret(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "generateSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idTokenValidity")
    def id_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idTokenValidity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logoutUrls")
    def logout_urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "logoutUrls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preventUserExistenceErrors")
    def prevent_user_existence_errors(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preventUserExistenceErrors"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readAttributes")
    def read_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "readAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshTokenValidity")
    def refresh_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "refreshTokenValidity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedIdentityProviders")
    def supported_identity_providers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedIdentityProviders"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenValidityUnits")
    def token_validity_units(
        self,
    ) -> "DataAwsCognitoUserPoolClientTokenValidityUnitsList":
        return typing.cast("DataAwsCognitoUserPoolClientTokenValidityUnitsList", jsii.get(self, "tokenValidityUnits"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writeAttributes")
    def write_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "writeAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClient, "client_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClient, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClient, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientAnalyticsConfiguration",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsCognitoUserPoolClientAnalyticsConfiguration:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCognitoUserPoolClientAnalyticsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCognitoUserPoolClientAnalyticsConfigurationList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientAnalyticsConfigurationList",
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
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolClientAnalyticsConfigurationList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsCognitoUserPoolClientAnalyticsConfigurationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolClientAnalyticsConfigurationList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsCognitoUserPoolClientAnalyticsConfigurationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClientAnalyticsConfigurationList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClientAnalyticsConfigurationList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClientAnalyticsConfigurationList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsCognitoUserPoolClientAnalyticsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientAnalyticsConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolClientAnalyticsConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataShared")
    def user_data_shared(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "userDataShared"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsCognitoUserPoolClientAnalyticsConfiguration]:
        return typing.cast(typing.Optional[DataAwsCognitoUserPoolClientAnalyticsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsCognitoUserPoolClientAnalyticsConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClientAnalyticsConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "client_id": "clientId",
        "user_pool_id": "userPoolId",
        "id": "id",
    },
)
class DataAwsCognitoUserPoolClientConfig(cdktf.TerraformMetaArguments):
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
        client_id: builtins.str,
        user_pool_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#client_id DataAwsCognitoUserPoolClient#client_id}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#user_pool_id DataAwsCognitoUserPoolClient#user_pool_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#id DataAwsCognitoUserPoolClient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolClientConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "client_id": client_id,
            "user_pool_id": user_pool_id,
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
    def client_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#client_id DataAwsCognitoUserPoolClient#client_id}.'''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#user_pool_id DataAwsCognitoUserPoolClient#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#id DataAwsCognitoUserPoolClient#id}.

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
        return "DataAwsCognitoUserPoolClientConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientTokenValidityUnits",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsCognitoUserPoolClientTokenValidityUnits:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCognitoUserPoolClientTokenValidityUnits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCognitoUserPoolClientTokenValidityUnitsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientTokenValidityUnitsList",
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
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolClientTokenValidityUnitsList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsCognitoUserPoolClientTokenValidityUnitsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolClientTokenValidityUnitsList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsCognitoUserPoolClientTokenValidityUnitsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClientTokenValidityUnitsList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClientTokenValidityUnitsList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClientTokenValidityUnitsList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsCognitoUserPoolClientTokenValidityUnitsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientTokenValidityUnitsOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolClientTokenValidityUnitsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessToken")
    def access_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idToken")
    def id_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshToken")
    def refresh_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "refreshToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsCognitoUserPoolClientTokenValidityUnits]:
        return typing.cast(typing.Optional[DataAwsCognitoUserPoolClientTokenValidityUnits], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsCognitoUserPoolClientTokenValidityUnits],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClientTokenValidityUnitsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAwsCognitoUserPoolClients(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClients",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients aws_cognito_user_pool_clients}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        user_pool_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients aws_cognito_user_pool_clients} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients#user_pool_id DataAwsCognitoUserPoolClients#user_pool_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients#id DataAwsCognitoUserPoolClients#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolClients.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsCognitoUserPoolClientsConfig(
            user_pool_id=user_pool_id,
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
    @jsii.member(jsii_name="clientIds")
    def client_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clientIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientNames")
    def client_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clientNames"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClients, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolClients, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "user_pool_id": "userPoolId",
        "id": "id",
    },
)
class DataAwsCognitoUserPoolClientsConfig(cdktf.TerraformMetaArguments):
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
        user_pool_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients#user_pool_id DataAwsCognitoUserPoolClients#user_pool_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients#id DataAwsCognitoUserPoolClients#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolClientsConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool_id": user_pool_id,
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
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients#user_pool_id DataAwsCognitoUserPoolClients#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients#id DataAwsCognitoUserPoolClients#id}.

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
        return "DataAwsCognitoUserPoolClientsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCognitoUserPoolSigningCertificate(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolSigningCertificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate aws_cognito_user_pool_signing_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        user_pool_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate aws_cognito_user_pool_signing_certificate} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate#user_pool_id DataAwsCognitoUserPoolSigningCertificate#user_pool_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate#id DataAwsCognitoUserPoolSigningCertificate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolSigningCertificate.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsCognitoUserPoolSigningCertificateConfig(
            user_pool_id=user_pool_id,
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
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolSigningCertificate, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPoolSigningCertificate, "user_pool_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolSigningCertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "user_pool_id": "userPoolId",
        "id": "id",
    },
)
class DataAwsCognitoUserPoolSigningCertificateConfig(cdktf.TerraformMetaArguments):
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
        user_pool_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate#user_pool_id DataAwsCognitoUserPoolSigningCertificate#user_pool_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate#id DataAwsCognitoUserPoolSigningCertificate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolSigningCertificateConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool_id": user_pool_id,
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
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate#user_pool_id DataAwsCognitoUserPoolSigningCertificate#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate#id DataAwsCognitoUserPoolSigningCertificate#id}.

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
        return "DataAwsCognitoUserPoolSigningCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCognitoUserPools(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPools",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools aws_cognito_user_pools}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools aws_cognito_user_pools} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools#name DataAwsCognitoUserPools#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools#id DataAwsCognitoUserPools#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCognitoUserPools.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsCognitoUserPoolsConfig(
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
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ids")
    def ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ids"))

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
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPools, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCognitoUserPools, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolsConfig",
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
class DataAwsCognitoUserPoolsConfig(cdktf.TerraformMetaArguments):
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
        '''AWS Cognito.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools#name DataAwsCognitoUserPools#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools#id DataAwsCognitoUserPools#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCognitoUserPoolsConfig.__init__)
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools#name DataAwsCognitoUserPools#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools#id DataAwsCognitoUserPools#id}.

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
        return "DataAwsCognitoUserPoolsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CognitoIdentityPool",
    "CognitoIdentityPoolCognitoIdentityProviders",
    "CognitoIdentityPoolCognitoIdentityProvidersList",
    "CognitoIdentityPoolCognitoIdentityProvidersOutputReference",
    "CognitoIdentityPoolConfig",
    "CognitoIdentityPoolProviderPrincipalTag",
    "CognitoIdentityPoolProviderPrincipalTagConfig",
    "CognitoIdentityPoolRolesAttachment",
    "CognitoIdentityPoolRolesAttachmentConfig",
    "CognitoIdentityPoolRolesAttachmentRoleMapping",
    "CognitoIdentityPoolRolesAttachmentRoleMappingList",
    "CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule",
    "CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleList",
    "CognitoIdentityPoolRolesAttachmentRoleMappingMappingRuleOutputReference",
    "CognitoIdentityPoolRolesAttachmentRoleMappingOutputReference",
    "CognitoIdentityProvider",
    "CognitoIdentityProviderConfig",
    "CognitoResourceServer",
    "CognitoResourceServerConfig",
    "CognitoResourceServerScope",
    "CognitoResourceServerScopeList",
    "CognitoResourceServerScopeOutputReference",
    "CognitoRiskConfiguration",
    "CognitoRiskConfigurationAccountTakeoverRiskConfiguration",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActions",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighAction",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsHighActionOutputReference",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowAction",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsLowActionOutputReference",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumAction",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsMediumActionOutputReference",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationActionsOutputReference",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfiguration",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmail",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationBlockEmailOutputReference",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmail",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationMfaEmailOutputReference",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmail",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationNoActionEmailOutputReference",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationNotifyConfigurationOutputReference",
    "CognitoRiskConfigurationAccountTakeoverRiskConfigurationOutputReference",
    "CognitoRiskConfigurationCompromisedCredentialsRiskConfiguration",
    "CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActions",
    "CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationActionsOutputReference",
    "CognitoRiskConfigurationCompromisedCredentialsRiskConfigurationOutputReference",
    "CognitoRiskConfigurationConfig",
    "CognitoRiskConfigurationRiskExceptionConfiguration",
    "CognitoRiskConfigurationRiskExceptionConfigurationOutputReference",
    "CognitoUser",
    "CognitoUserConfig",
    "CognitoUserGroup",
    "CognitoUserGroupConfig",
    "CognitoUserInGroup",
    "CognitoUserInGroupConfig",
    "CognitoUserPool",
    "CognitoUserPoolAccountRecoverySetting",
    "CognitoUserPoolAccountRecoverySettingOutputReference",
    "CognitoUserPoolAccountRecoverySettingRecoveryMechanism",
    "CognitoUserPoolAccountRecoverySettingRecoveryMechanismList",
    "CognitoUserPoolAccountRecoverySettingRecoveryMechanismOutputReference",
    "CognitoUserPoolAdminCreateUserConfig",
    "CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate",
    "CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference",
    "CognitoUserPoolAdminCreateUserConfigOutputReference",
    "CognitoUserPoolClient",
    "CognitoUserPoolClientAnalyticsConfiguration",
    "CognitoUserPoolClientAnalyticsConfigurationOutputReference",
    "CognitoUserPoolClientConfig",
    "CognitoUserPoolClientTokenValidityUnits",
    "CognitoUserPoolClientTokenValidityUnitsOutputReference",
    "CognitoUserPoolConfig",
    "CognitoUserPoolDeviceConfiguration",
    "CognitoUserPoolDeviceConfigurationOutputReference",
    "CognitoUserPoolDomain",
    "CognitoUserPoolDomainConfig",
    "CognitoUserPoolEmailConfiguration",
    "CognitoUserPoolEmailConfigurationOutputReference",
    "CognitoUserPoolLambdaConfig",
    "CognitoUserPoolLambdaConfigCustomEmailSender",
    "CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference",
    "CognitoUserPoolLambdaConfigCustomSmsSender",
    "CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference",
    "CognitoUserPoolLambdaConfigOutputReference",
    "CognitoUserPoolPasswordPolicy",
    "CognitoUserPoolPasswordPolicyOutputReference",
    "CognitoUserPoolSchema",
    "CognitoUserPoolSchemaList",
    "CognitoUserPoolSchemaNumberAttributeConstraints",
    "CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference",
    "CognitoUserPoolSchemaOutputReference",
    "CognitoUserPoolSchemaStringAttributeConstraints",
    "CognitoUserPoolSchemaStringAttributeConstraintsOutputReference",
    "CognitoUserPoolSmsConfiguration",
    "CognitoUserPoolSmsConfigurationOutputReference",
    "CognitoUserPoolSoftwareTokenMfaConfiguration",
    "CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference",
    "CognitoUserPoolUiCustomization",
    "CognitoUserPoolUiCustomizationConfig",
    "CognitoUserPoolUserPoolAddOns",
    "CognitoUserPoolUserPoolAddOnsOutputReference",
    "CognitoUserPoolUsernameConfiguration",
    "CognitoUserPoolUsernameConfigurationOutputReference",
    "CognitoUserPoolVerificationMessageTemplate",
    "CognitoUserPoolVerificationMessageTemplateOutputReference",
    "DataAwsCognitoUserPoolClient",
    "DataAwsCognitoUserPoolClientAnalyticsConfiguration",
    "DataAwsCognitoUserPoolClientAnalyticsConfigurationList",
    "DataAwsCognitoUserPoolClientAnalyticsConfigurationOutputReference",
    "DataAwsCognitoUserPoolClientConfig",
    "DataAwsCognitoUserPoolClientTokenValidityUnits",
    "DataAwsCognitoUserPoolClientTokenValidityUnitsList",
    "DataAwsCognitoUserPoolClientTokenValidityUnitsOutputReference",
    "DataAwsCognitoUserPoolClients",
    "DataAwsCognitoUserPoolClientsConfig",
    "DataAwsCognitoUserPoolSigningCertificate",
    "DataAwsCognitoUserPoolSigningCertificateConfig",
    "DataAwsCognitoUserPools",
    "DataAwsCognitoUserPoolsConfig",
]

publication.publish()
