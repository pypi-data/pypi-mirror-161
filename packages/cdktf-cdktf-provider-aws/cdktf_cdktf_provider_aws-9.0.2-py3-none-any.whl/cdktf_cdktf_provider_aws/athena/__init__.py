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


class AthenaDataCatalog(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaDataCatalog",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog aws_athena_data_catalog}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        description: builtins.str,
        name: builtins.str,
        parameters: typing.Mapping[builtins.str, builtins.str],
        type: builtins.str,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog aws_athena_data_catalog} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#description AthenaDataCatalog#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#name AthenaDataCatalog#name}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#parameters AthenaDataCatalog#parameters}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#type AthenaDataCatalog#type}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#id AthenaDataCatalog#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#tags AthenaDataCatalog#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#tags_all AthenaDataCatalog#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AthenaDataCatalog.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AthenaDataCatalogConfig(
            description=description,
            name=name,
            parameters=parameters,
            type=type,
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
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "parametersInput"))

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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDataCatalog, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDataCatalog, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDataCatalog, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDataCatalog, "parameters").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDataCatalog, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDataCatalog, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDataCatalog, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaDataCatalogConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "description": "description",
        "name": "name",
        "parameters": "parameters",
        "type": "type",
        "id": "id",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class AthenaDataCatalogConfig(cdktf.TerraformMetaArguments):
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
        description: builtins.str,
        name: builtins.str,
        parameters: typing.Mapping[builtins.str, builtins.str],
        type: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''Amazon Athena.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#description AthenaDataCatalog#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#name AthenaDataCatalog#name}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#parameters AthenaDataCatalog#parameters}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#type AthenaDataCatalog#type}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#id AthenaDataCatalog#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#tags AthenaDataCatalog#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#tags_all AthenaDataCatalog#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(AthenaDataCatalogConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "name": name,
            "parameters": parameters,
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
    def description(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#description AthenaDataCatalog#description}.'''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#name AthenaDataCatalog#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#parameters AthenaDataCatalog#parameters}.'''
        result = self._values.get("parameters")
        assert result is not None, "Required property 'parameters' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#type AthenaDataCatalog#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#id AthenaDataCatalog#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#tags AthenaDataCatalog#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_data_catalog#tags_all AthenaDataCatalog#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaDataCatalogConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaDatabase(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaDatabase",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/athena_database aws_athena_database}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        acl_configuration: typing.Optional[typing.Union["AthenaDatabaseAclConfiguration", typing.Dict[str, typing.Any]]] = None,
        bucket: typing.Optional[builtins.str] = None,
        comment: typing.Optional[builtins.str] = None,
        encryption_configuration: typing.Optional[typing.Union["AthenaDatabaseEncryptionConfiguration", typing.Dict[str, typing.Any]]] = None,
        expected_bucket_owner: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/athena_database aws_athena_database} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#name AthenaDatabase#name}.
        :param acl_configuration: acl_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#acl_configuration AthenaDatabase#acl_configuration}
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#bucket AthenaDatabase#bucket}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#comment AthenaDatabase#comment}.
        :param encryption_configuration: encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_configuration AthenaDatabase#encryption_configuration}
        :param expected_bucket_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#expected_bucket_owner AthenaDatabase#expected_bucket_owner}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#force_destroy AthenaDatabase#force_destroy}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#id AthenaDatabase#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#properties AthenaDatabase#properties}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AthenaDatabase.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AthenaDatabaseConfig(
            name=name,
            acl_configuration=acl_configuration,
            bucket=bucket,
            comment=comment,
            encryption_configuration=encryption_configuration,
            expected_bucket_owner=expected_bucket_owner,
            force_destroy=force_destroy,
            id=id,
            properties=properties,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putAclConfiguration")
    def put_acl_configuration(self, *, s3_acl_option: builtins.str) -> None:
        '''
        :param s3_acl_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#s3_acl_option AthenaDatabase#s3_acl_option}.
        '''
        value = AthenaDatabaseAclConfiguration(s3_acl_option=s3_acl_option)

        return typing.cast(None, jsii.invoke(self, "putAclConfiguration", [value]))

    @jsii.member(jsii_name="putEncryptionConfiguration")
    def put_encryption_configuration(
        self,
        *,
        encryption_option: builtins.str,
        kms_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_option AthenaDatabase#encryption_option}.
        :param kms_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#kms_key AthenaDatabase#kms_key}.
        '''
        value = AthenaDatabaseEncryptionConfiguration(
            encryption_option=encryption_option, kms_key=kms_key
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionConfiguration", [value]))

    @jsii.member(jsii_name="resetAclConfiguration")
    def reset_acl_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAclConfiguration", []))

    @jsii.member(jsii_name="resetBucket")
    def reset_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucket", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetEncryptionConfiguration")
    def reset_encryption_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionConfiguration", []))

    @jsii.member(jsii_name="resetExpectedBucketOwner")
    def reset_expected_bucket_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpectedBucketOwner", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclConfiguration")
    def acl_configuration(self) -> "AthenaDatabaseAclConfigurationOutputReference":
        return typing.cast("AthenaDatabaseAclConfigurationOutputReference", jsii.get(self, "aclConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfiguration")
    def encryption_configuration(
        self,
    ) -> "AthenaDatabaseEncryptionConfigurationOutputReference":
        return typing.cast("AthenaDatabaseEncryptionConfigurationOutputReference", jsii.get(self, "encryptionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclConfigurationInput")
    def acl_configuration_input(
        self,
    ) -> typing.Optional["AthenaDatabaseAclConfiguration"]:
        return typing.cast(typing.Optional["AthenaDatabaseAclConfiguration"], jsii.get(self, "aclConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfigurationInput")
    def encryption_configuration_input(
        self,
    ) -> typing.Optional["AthenaDatabaseEncryptionConfiguration"]:
        return typing.cast(typing.Optional["AthenaDatabaseEncryptionConfiguration"], jsii.get(self, "encryptionConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expectedBucketOwnerInput")
    def expected_bucket_owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expectedBucketOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "propertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabase, "bucket").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabase, "comment").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expectedBucketOwner")
    def expected_bucket_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expectedBucketOwner"))

    @expected_bucket_owner.setter
    def expected_bucket_owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabase, "expected_bucket_owner").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expectedBucketOwner", value)

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
            type_hints = typing.get_type_hints(getattr(AthenaDatabase, "force_destroy").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceDestroy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabase, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabase, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="properties")
    def properties(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "properties"))

    @properties.setter
    def properties(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabase, "properties").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "properties", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaDatabaseAclConfiguration",
    jsii_struct_bases=[],
    name_mapping={"s3_acl_option": "s3AclOption"},
)
class AthenaDatabaseAclConfiguration:
    def __init__(self, *, s3_acl_option: builtins.str) -> None:
        '''
        :param s3_acl_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#s3_acl_option AthenaDatabase#s3_acl_option}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AthenaDatabaseAclConfiguration.__init__)
            check_type(argname="argument s3_acl_option", value=s3_acl_option, expected_type=type_hints["s3_acl_option"])
        self._values: typing.Dict[str, typing.Any] = {
            "s3_acl_option": s3_acl_option,
        }

    @builtins.property
    def s3_acl_option(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#s3_acl_option AthenaDatabase#s3_acl_option}.'''
        result = self._values.get("s3_acl_option")
        assert result is not None, "Required property 's3_acl_option' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaDatabaseAclConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaDatabaseAclConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaDatabaseAclConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(AthenaDatabaseAclConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3AclOptionInput")
    def s3_acl_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3AclOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3AclOption")
    def s3_acl_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3AclOption"))

    @s3_acl_option.setter
    def s3_acl_option(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabaseAclConfigurationOutputReference, "s3_acl_option").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3AclOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AthenaDatabaseAclConfiguration]:
        return typing.cast(typing.Optional[AthenaDatabaseAclConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaDatabaseAclConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabaseAclConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaDatabaseConfig",
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
        "acl_configuration": "aclConfiguration",
        "bucket": "bucket",
        "comment": "comment",
        "encryption_configuration": "encryptionConfiguration",
        "expected_bucket_owner": "expectedBucketOwner",
        "force_destroy": "forceDestroy",
        "id": "id",
        "properties": "properties",
    },
)
class AthenaDatabaseConfig(cdktf.TerraformMetaArguments):
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
        acl_configuration: typing.Optional[typing.Union[AthenaDatabaseAclConfiguration, typing.Dict[str, typing.Any]]] = None,
        bucket: typing.Optional[builtins.str] = None,
        comment: typing.Optional[builtins.str] = None,
        encryption_configuration: typing.Optional[typing.Union["AthenaDatabaseEncryptionConfiguration", typing.Dict[str, typing.Any]]] = None,
        expected_bucket_owner: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''Amazon Athena.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#name AthenaDatabase#name}.
        :param acl_configuration: acl_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#acl_configuration AthenaDatabase#acl_configuration}
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#bucket AthenaDatabase#bucket}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#comment AthenaDatabase#comment}.
        :param encryption_configuration: encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_configuration AthenaDatabase#encryption_configuration}
        :param expected_bucket_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#expected_bucket_owner AthenaDatabase#expected_bucket_owner}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#force_destroy AthenaDatabase#force_destroy}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#id AthenaDatabase#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#properties AthenaDatabase#properties}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(acl_configuration, dict):
            acl_configuration = AthenaDatabaseAclConfiguration(**acl_configuration)
        if isinstance(encryption_configuration, dict):
            encryption_configuration = AthenaDatabaseEncryptionConfiguration(**encryption_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(AthenaDatabaseConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument acl_configuration", value=acl_configuration, expected_type=type_hints["acl_configuration"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument encryption_configuration", value=encryption_configuration, expected_type=type_hints["encryption_configuration"])
            check_type(argname="argument expected_bucket_owner", value=expected_bucket_owner, expected_type=type_hints["expected_bucket_owner"])
            check_type(argname="argument force_destroy", value=force_destroy, expected_type=type_hints["force_destroy"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
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
        if acl_configuration is not None:
            self._values["acl_configuration"] = acl_configuration
        if bucket is not None:
            self._values["bucket"] = bucket
        if comment is not None:
            self._values["comment"] = comment
        if encryption_configuration is not None:
            self._values["encryption_configuration"] = encryption_configuration
        if expected_bucket_owner is not None:
            self._values["expected_bucket_owner"] = expected_bucket_owner
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if id is not None:
            self._values["id"] = id
        if properties is not None:
            self._values["properties"] = properties

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#name AthenaDatabase#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def acl_configuration(self) -> typing.Optional[AthenaDatabaseAclConfiguration]:
        '''acl_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#acl_configuration AthenaDatabase#acl_configuration}
        '''
        result = self._values.get("acl_configuration")
        return typing.cast(typing.Optional[AthenaDatabaseAclConfiguration], result)

    @builtins.property
    def bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#bucket AthenaDatabase#bucket}.'''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#comment AthenaDatabase#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_configuration(
        self,
    ) -> typing.Optional["AthenaDatabaseEncryptionConfiguration"]:
        '''encryption_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_configuration AthenaDatabase#encryption_configuration}
        '''
        result = self._values.get("encryption_configuration")
        return typing.cast(typing.Optional["AthenaDatabaseEncryptionConfiguration"], result)

    @builtins.property
    def expected_bucket_owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#expected_bucket_owner AthenaDatabase#expected_bucket_owner}.'''
        result = self._values.get("expected_bucket_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#force_destroy AthenaDatabase#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#id AthenaDatabase#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#properties AthenaDatabase#properties}.'''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaDatabaseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaDatabaseEncryptionConfiguration",
    jsii_struct_bases=[],
    name_mapping={"encryption_option": "encryptionOption", "kms_key": "kmsKey"},
)
class AthenaDatabaseEncryptionConfiguration:
    def __init__(
        self,
        *,
        encryption_option: builtins.str,
        kms_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_option AthenaDatabase#encryption_option}.
        :param kms_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#kms_key AthenaDatabase#kms_key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AthenaDatabaseEncryptionConfiguration.__init__)
            check_type(argname="argument encryption_option", value=encryption_option, expected_type=type_hints["encryption_option"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
        self._values: typing.Dict[str, typing.Any] = {
            "encryption_option": encryption_option,
        }
        if kms_key is not None:
            self._values["kms_key"] = kms_key

    @builtins.property
    def encryption_option(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_option AthenaDatabase#encryption_option}.'''
        result = self._values.get("encryption_option")
        assert result is not None, "Required property 'encryption_option' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#kms_key AthenaDatabase#kms_key}.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaDatabaseEncryptionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaDatabaseEncryptionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaDatabaseEncryptionConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(AthenaDatabaseEncryptionConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionOptionInput")
    def encryption_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionOption")
    def encryption_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionOption"))

    @encryption_option.setter
    def encryption_option(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabaseEncryptionConfigurationOutputReference, "encryption_option").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabaseEncryptionConfigurationOutputReference, "kms_key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AthenaDatabaseEncryptionConfiguration]:
        return typing.cast(typing.Optional[AthenaDatabaseEncryptionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaDatabaseEncryptionConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaDatabaseEncryptionConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AthenaNamedQuery(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaNamedQuery",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query aws_athena_named_query}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        database: builtins.str,
        name: builtins.str,
        query: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        workgroup: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query aws_athena_named_query} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#database AthenaNamedQuery#database}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#name AthenaNamedQuery#name}.
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#query AthenaNamedQuery#query}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#description AthenaNamedQuery#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#id AthenaNamedQuery#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param workgroup: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#workgroup AthenaNamedQuery#workgroup}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AthenaNamedQuery.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AthenaNamedQueryConfig(
            database=database,
            name=name,
            query=query,
            description=description,
            id=id,
            workgroup=workgroup,
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

    @jsii.member(jsii_name="resetWorkgroup")
    def reset_workgroup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkgroup", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

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
    @jsii.member(jsii_name="queryInput")
    def query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workgroupInput")
    def workgroup_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workgroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaNamedQuery, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaNamedQuery, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaNamedQuery, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaNamedQuery, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="query")
    def query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "query"))

    @query.setter
    def query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaNamedQuery, "query").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "query", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workgroup")
    def workgroup(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workgroup"))

    @workgroup.setter
    def workgroup(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaNamedQuery, "workgroup").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workgroup", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaNamedQueryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "database": "database",
        "name": "name",
        "query": "query",
        "description": "description",
        "id": "id",
        "workgroup": "workgroup",
    },
)
class AthenaNamedQueryConfig(cdktf.TerraformMetaArguments):
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
        database: builtins.str,
        name: builtins.str,
        query: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        workgroup: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Amazon Athena.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#database AthenaNamedQuery#database}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#name AthenaNamedQuery#name}.
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#query AthenaNamedQuery#query}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#description AthenaNamedQuery#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#id AthenaNamedQuery#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param workgroup: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#workgroup AthenaNamedQuery#workgroup}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(AthenaNamedQueryConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument workgroup", value=workgroup, expected_type=type_hints["workgroup"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "name": name,
            "query": query,
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
        if workgroup is not None:
            self._values["workgroup"] = workgroup

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
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#database AthenaNamedQuery#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#name AthenaNamedQuery#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#query AthenaNamedQuery#query}.'''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#description AthenaNamedQuery#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#id AthenaNamedQuery#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workgroup(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#workgroup AthenaNamedQuery#workgroup}.'''
        result = self._values.get("workgroup")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaNamedQueryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaWorkgroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup aws_athena_workgroup}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        configuration: typing.Optional[typing.Union["AthenaWorkgroupConfiguration", typing.Dict[str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup aws_athena_workgroup} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#name AthenaWorkgroup#name}.
        :param configuration: configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#configuration AthenaWorkgroup#configuration}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#description AthenaWorkgroup#description}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#force_destroy AthenaWorkgroup#force_destroy}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#id AthenaWorkgroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#state AthenaWorkgroup#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags AthenaWorkgroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags_all AthenaWorkgroup#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AthenaWorkgroup.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AthenaWorkgroupConfig(
            name=name,
            configuration=configuration,
            description=description,
            force_destroy=force_destroy,
            id=id,
            state=state,
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

    @jsii.member(jsii_name="putConfiguration")
    def put_configuration(
        self,
        *,
        bytes_scanned_cutoff_per_query: typing.Optional[jsii.Number] = None,
        enforce_workgroup_configuration: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        engine_version: typing.Optional[typing.Union["AthenaWorkgroupConfigurationEngineVersion", typing.Dict[str, typing.Any]]] = None,
        publish_cloudwatch_metrics_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        requester_pays_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        result_configuration: typing.Optional[typing.Union["AthenaWorkgroupConfigurationResultConfiguration", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bytes_scanned_cutoff_per_query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#bytes_scanned_cutoff_per_query AthenaWorkgroup#bytes_scanned_cutoff_per_query}.
        :param enforce_workgroup_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#enforce_workgroup_configuration AthenaWorkgroup#enforce_workgroup_configuration}.
        :param engine_version: engine_version block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#engine_version AthenaWorkgroup#engine_version}
        :param publish_cloudwatch_metrics_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#publish_cloudwatch_metrics_enabled AthenaWorkgroup#publish_cloudwatch_metrics_enabled}.
        :param requester_pays_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#requester_pays_enabled AthenaWorkgroup#requester_pays_enabled}.
        :param result_configuration: result_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#result_configuration AthenaWorkgroup#result_configuration}
        '''
        value = AthenaWorkgroupConfiguration(
            bytes_scanned_cutoff_per_query=bytes_scanned_cutoff_per_query,
            enforce_workgroup_configuration=enforce_workgroup_configuration,
            engine_version=engine_version,
            publish_cloudwatch_metrics_enabled=publish_cloudwatch_metrics_enabled,
            requester_pays_enabled=requester_pays_enabled,
            result_configuration=result_configuration,
        )

        return typing.cast(None, jsii.invoke(self, "putConfiguration", [value]))

    @jsii.member(jsii_name="resetConfiguration")
    def reset_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfiguration", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

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
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> "AthenaWorkgroupConfigurationOutputReference":
        return typing.cast("AthenaWorkgroupConfigurationOutputReference", jsii.get(self, "configuration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInput")
    def configuration_input(self) -> typing.Optional["AthenaWorkgroupConfiguration"]:
        return typing.cast(typing.Optional["AthenaWorkgroupConfiguration"], jsii.get(self, "configurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

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
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroup, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

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
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroup, "force_destroy").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceDestroy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroup, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroup, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroup, "state").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroup, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroup, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfig",
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
        "configuration": "configuration",
        "description": "description",
        "force_destroy": "forceDestroy",
        "id": "id",
        "state": "state",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class AthenaWorkgroupConfig(cdktf.TerraformMetaArguments):
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
        configuration: typing.Optional[typing.Union["AthenaWorkgroupConfiguration", typing.Dict[str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''Amazon Athena.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#name AthenaWorkgroup#name}.
        :param configuration: configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#configuration AthenaWorkgroup#configuration}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#description AthenaWorkgroup#description}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#force_destroy AthenaWorkgroup#force_destroy}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#id AthenaWorkgroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#state AthenaWorkgroup#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags AthenaWorkgroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags_all AthenaWorkgroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(configuration, dict):
            configuration = AthenaWorkgroupConfiguration(**configuration)
        if __debug__:
            type_hints = typing.get_type_hints(AthenaWorkgroupConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument force_destroy", value=force_destroy, expected_type=type_hints["force_destroy"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
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
        if configuration is not None:
            self._values["configuration"] = configuration
        if description is not None:
            self._values["description"] = description
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if id is not None:
            self._values["id"] = id
        if state is not None:
            self._values["state"] = state
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#name AthenaWorkgroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def configuration(self) -> typing.Optional["AthenaWorkgroupConfiguration"]:
        '''configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#configuration AthenaWorkgroup#configuration}
        '''
        result = self._values.get("configuration")
        return typing.cast(typing.Optional["AthenaWorkgroupConfiguration"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#description AthenaWorkgroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#force_destroy AthenaWorkgroup#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#id AthenaWorkgroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#state AthenaWorkgroup#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags AthenaWorkgroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags_all AthenaWorkgroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "bytes_scanned_cutoff_per_query": "bytesScannedCutoffPerQuery",
        "enforce_workgroup_configuration": "enforceWorkgroupConfiguration",
        "engine_version": "engineVersion",
        "publish_cloudwatch_metrics_enabled": "publishCloudwatchMetricsEnabled",
        "requester_pays_enabled": "requesterPaysEnabled",
        "result_configuration": "resultConfiguration",
    },
)
class AthenaWorkgroupConfiguration:
    def __init__(
        self,
        *,
        bytes_scanned_cutoff_per_query: typing.Optional[jsii.Number] = None,
        enforce_workgroup_configuration: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        engine_version: typing.Optional[typing.Union["AthenaWorkgroupConfigurationEngineVersion", typing.Dict[str, typing.Any]]] = None,
        publish_cloudwatch_metrics_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        requester_pays_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        result_configuration: typing.Optional[typing.Union["AthenaWorkgroupConfigurationResultConfiguration", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bytes_scanned_cutoff_per_query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#bytes_scanned_cutoff_per_query AthenaWorkgroup#bytes_scanned_cutoff_per_query}.
        :param enforce_workgroup_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#enforce_workgroup_configuration AthenaWorkgroup#enforce_workgroup_configuration}.
        :param engine_version: engine_version block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#engine_version AthenaWorkgroup#engine_version}
        :param publish_cloudwatch_metrics_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#publish_cloudwatch_metrics_enabled AthenaWorkgroup#publish_cloudwatch_metrics_enabled}.
        :param requester_pays_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#requester_pays_enabled AthenaWorkgroup#requester_pays_enabled}.
        :param result_configuration: result_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#result_configuration AthenaWorkgroup#result_configuration}
        '''
        if isinstance(engine_version, dict):
            engine_version = AthenaWorkgroupConfigurationEngineVersion(**engine_version)
        if isinstance(result_configuration, dict):
            result_configuration = AthenaWorkgroupConfigurationResultConfiguration(**result_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(AthenaWorkgroupConfiguration.__init__)
            check_type(argname="argument bytes_scanned_cutoff_per_query", value=bytes_scanned_cutoff_per_query, expected_type=type_hints["bytes_scanned_cutoff_per_query"])
            check_type(argname="argument enforce_workgroup_configuration", value=enforce_workgroup_configuration, expected_type=type_hints["enforce_workgroup_configuration"])
            check_type(argname="argument engine_version", value=engine_version, expected_type=type_hints["engine_version"])
            check_type(argname="argument publish_cloudwatch_metrics_enabled", value=publish_cloudwatch_metrics_enabled, expected_type=type_hints["publish_cloudwatch_metrics_enabled"])
            check_type(argname="argument requester_pays_enabled", value=requester_pays_enabled, expected_type=type_hints["requester_pays_enabled"])
            check_type(argname="argument result_configuration", value=result_configuration, expected_type=type_hints["result_configuration"])
        self._values: typing.Dict[str, typing.Any] = {}
        if bytes_scanned_cutoff_per_query is not None:
            self._values["bytes_scanned_cutoff_per_query"] = bytes_scanned_cutoff_per_query
        if enforce_workgroup_configuration is not None:
            self._values["enforce_workgroup_configuration"] = enforce_workgroup_configuration
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if publish_cloudwatch_metrics_enabled is not None:
            self._values["publish_cloudwatch_metrics_enabled"] = publish_cloudwatch_metrics_enabled
        if requester_pays_enabled is not None:
            self._values["requester_pays_enabled"] = requester_pays_enabled
        if result_configuration is not None:
            self._values["result_configuration"] = result_configuration

    @builtins.property
    def bytes_scanned_cutoff_per_query(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#bytes_scanned_cutoff_per_query AthenaWorkgroup#bytes_scanned_cutoff_per_query}.'''
        result = self._values.get("bytes_scanned_cutoff_per_query")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enforce_workgroup_configuration(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#enforce_workgroup_configuration AthenaWorkgroup#enforce_workgroup_configuration}.'''
        result = self._values.get("enforce_workgroup_configuration")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def engine_version(
        self,
    ) -> typing.Optional["AthenaWorkgroupConfigurationEngineVersion"]:
        '''engine_version block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#engine_version AthenaWorkgroup#engine_version}
        '''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional["AthenaWorkgroupConfigurationEngineVersion"], result)

    @builtins.property
    def publish_cloudwatch_metrics_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#publish_cloudwatch_metrics_enabled AthenaWorkgroup#publish_cloudwatch_metrics_enabled}.'''
        result = self._values.get("publish_cloudwatch_metrics_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def requester_pays_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#requester_pays_enabled AthenaWorkgroup#requester_pays_enabled}.'''
        result = self._values.get("requester_pays_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def result_configuration(
        self,
    ) -> typing.Optional["AthenaWorkgroupConfigurationResultConfiguration"]:
        '''result_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#result_configuration AthenaWorkgroup#result_configuration}
        '''
        result = self._values.get("result_configuration")
        return typing.cast(typing.Optional["AthenaWorkgroupConfigurationResultConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationEngineVersion",
    jsii_struct_bases=[],
    name_mapping={"selected_engine_version": "selectedEngineVersion"},
)
class AthenaWorkgroupConfigurationEngineVersion:
    def __init__(
        self,
        *,
        selected_engine_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param selected_engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#selected_engine_version AthenaWorkgroup#selected_engine_version}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AthenaWorkgroupConfigurationEngineVersion.__init__)
            check_type(argname="argument selected_engine_version", value=selected_engine_version, expected_type=type_hints["selected_engine_version"])
        self._values: typing.Dict[str, typing.Any] = {}
        if selected_engine_version is not None:
            self._values["selected_engine_version"] = selected_engine_version

    @builtins.property
    def selected_engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#selected_engine_version AthenaWorkgroup#selected_engine_version}.'''
        result = self._values.get("selected_engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfigurationEngineVersion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaWorkgroupConfigurationEngineVersionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationEngineVersionOutputReference",
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
            type_hints = typing.get_type_hints(AthenaWorkgroupConfigurationEngineVersionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSelectedEngineVersion")
    def reset_selected_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelectedEngineVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="effectiveEngineVersion")
    def effective_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "effectiveEngineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectedEngineVersionInput")
    def selected_engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "selectedEngineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectedEngineVersion")
    def selected_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "selectedEngineVersion"))

    @selected_engine_version.setter
    def selected_engine_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationEngineVersionOutputReference, "selected_engine_version").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "selectedEngineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationEngineVersion]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationEngineVersion], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaWorkgroupConfigurationEngineVersion],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationEngineVersionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AthenaWorkgroupConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(AthenaWorkgroupConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEngineVersion")
    def put_engine_version(
        self,
        *,
        selected_engine_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param selected_engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#selected_engine_version AthenaWorkgroup#selected_engine_version}.
        '''
        value = AthenaWorkgroupConfigurationEngineVersion(
            selected_engine_version=selected_engine_version
        )

        return typing.cast(None, jsii.invoke(self, "putEngineVersion", [value]))

    @jsii.member(jsii_name="putResultConfiguration")
    def put_result_configuration(
        self,
        *,
        acl_configuration: typing.Optional[typing.Union["AthenaWorkgroupConfigurationResultConfigurationAclConfiguration", typing.Dict[str, typing.Any]]] = None,
        encryption_configuration: typing.Optional[typing.Union["AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration", typing.Dict[str, typing.Any]]] = None,
        expected_bucket_owner: typing.Optional[builtins.str] = None,
        output_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param acl_configuration: acl_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#acl_configuration AthenaWorkgroup#acl_configuration}
        :param encryption_configuration: encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_configuration AthenaWorkgroup#encryption_configuration}
        :param expected_bucket_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#expected_bucket_owner AthenaWorkgroup#expected_bucket_owner}.
        :param output_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#output_location AthenaWorkgroup#output_location}.
        '''
        value = AthenaWorkgroupConfigurationResultConfiguration(
            acl_configuration=acl_configuration,
            encryption_configuration=encryption_configuration,
            expected_bucket_owner=expected_bucket_owner,
            output_location=output_location,
        )

        return typing.cast(None, jsii.invoke(self, "putResultConfiguration", [value]))

    @jsii.member(jsii_name="resetBytesScannedCutoffPerQuery")
    def reset_bytes_scanned_cutoff_per_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBytesScannedCutoffPerQuery", []))

    @jsii.member(jsii_name="resetEnforceWorkgroupConfiguration")
    def reset_enforce_workgroup_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceWorkgroupConfiguration", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetPublishCloudwatchMetricsEnabled")
    def reset_publish_cloudwatch_metrics_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublishCloudwatchMetricsEnabled", []))

    @jsii.member(jsii_name="resetRequesterPaysEnabled")
    def reset_requester_pays_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequesterPaysEnabled", []))

    @jsii.member(jsii_name="resetResultConfiguration")
    def reset_result_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResultConfiguration", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(
        self,
    ) -> AthenaWorkgroupConfigurationEngineVersionOutputReference:
        return typing.cast(AthenaWorkgroupConfigurationEngineVersionOutputReference, jsii.get(self, "engineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resultConfiguration")
    def result_configuration(
        self,
    ) -> "AthenaWorkgroupConfigurationResultConfigurationOutputReference":
        return typing.cast("AthenaWorkgroupConfigurationResultConfigurationOutputReference", jsii.get(self, "resultConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bytesScannedCutoffPerQueryInput")
    def bytes_scanned_cutoff_per_query_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bytesScannedCutoffPerQueryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enforceWorkgroupConfigurationInput")
    def enforce_workgroup_configuration_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enforceWorkgroupConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionInput")
    def engine_version_input(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationEngineVersion]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationEngineVersion], jsii.get(self, "engineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishCloudwatchMetricsEnabledInput")
    def publish_cloudwatch_metrics_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publishCloudwatchMetricsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requesterPaysEnabledInput")
    def requester_pays_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requesterPaysEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resultConfigurationInput")
    def result_configuration_input(
        self,
    ) -> typing.Optional["AthenaWorkgroupConfigurationResultConfiguration"]:
        return typing.cast(typing.Optional["AthenaWorkgroupConfigurationResultConfiguration"], jsii.get(self, "resultConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bytesScannedCutoffPerQuery")
    def bytes_scanned_cutoff_per_query(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bytesScannedCutoffPerQuery"))

    @bytes_scanned_cutoff_per_query.setter
    def bytes_scanned_cutoff_per_query(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationOutputReference, "bytes_scanned_cutoff_per_query").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bytesScannedCutoffPerQuery", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enforceWorkgroupConfiguration")
    def enforce_workgroup_configuration(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enforceWorkgroupConfiguration"))

    @enforce_workgroup_configuration.setter
    def enforce_workgroup_configuration(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationOutputReference, "enforce_workgroup_configuration").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforceWorkgroupConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishCloudwatchMetricsEnabled")
    def publish_cloudwatch_metrics_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "publishCloudwatchMetricsEnabled"))

    @publish_cloudwatch_metrics_enabled.setter
    def publish_cloudwatch_metrics_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationOutputReference, "publish_cloudwatch_metrics_enabled").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publishCloudwatchMetricsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requesterPaysEnabled")
    def requester_pays_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requesterPaysEnabled"))

    @requester_pays_enabled.setter
    def requester_pays_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationOutputReference, "requester_pays_enabled").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requesterPaysEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AthenaWorkgroupConfiguration]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaWorkgroupConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationResultConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "acl_configuration": "aclConfiguration",
        "encryption_configuration": "encryptionConfiguration",
        "expected_bucket_owner": "expectedBucketOwner",
        "output_location": "outputLocation",
    },
)
class AthenaWorkgroupConfigurationResultConfiguration:
    def __init__(
        self,
        *,
        acl_configuration: typing.Optional[typing.Union["AthenaWorkgroupConfigurationResultConfigurationAclConfiguration", typing.Dict[str, typing.Any]]] = None,
        encryption_configuration: typing.Optional[typing.Union["AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration", typing.Dict[str, typing.Any]]] = None,
        expected_bucket_owner: typing.Optional[builtins.str] = None,
        output_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param acl_configuration: acl_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#acl_configuration AthenaWorkgroup#acl_configuration}
        :param encryption_configuration: encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_configuration AthenaWorkgroup#encryption_configuration}
        :param expected_bucket_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#expected_bucket_owner AthenaWorkgroup#expected_bucket_owner}.
        :param output_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#output_location AthenaWorkgroup#output_location}.
        '''
        if isinstance(acl_configuration, dict):
            acl_configuration = AthenaWorkgroupConfigurationResultConfigurationAclConfiguration(**acl_configuration)
        if isinstance(encryption_configuration, dict):
            encryption_configuration = AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration(**encryption_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(AthenaWorkgroupConfigurationResultConfiguration.__init__)
            check_type(argname="argument acl_configuration", value=acl_configuration, expected_type=type_hints["acl_configuration"])
            check_type(argname="argument encryption_configuration", value=encryption_configuration, expected_type=type_hints["encryption_configuration"])
            check_type(argname="argument expected_bucket_owner", value=expected_bucket_owner, expected_type=type_hints["expected_bucket_owner"])
            check_type(argname="argument output_location", value=output_location, expected_type=type_hints["output_location"])
        self._values: typing.Dict[str, typing.Any] = {}
        if acl_configuration is not None:
            self._values["acl_configuration"] = acl_configuration
        if encryption_configuration is not None:
            self._values["encryption_configuration"] = encryption_configuration
        if expected_bucket_owner is not None:
            self._values["expected_bucket_owner"] = expected_bucket_owner
        if output_location is not None:
            self._values["output_location"] = output_location

    @builtins.property
    def acl_configuration(
        self,
    ) -> typing.Optional["AthenaWorkgroupConfigurationResultConfigurationAclConfiguration"]:
        '''acl_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#acl_configuration AthenaWorkgroup#acl_configuration}
        '''
        result = self._values.get("acl_configuration")
        return typing.cast(typing.Optional["AthenaWorkgroupConfigurationResultConfigurationAclConfiguration"], result)

    @builtins.property
    def encryption_configuration(
        self,
    ) -> typing.Optional["AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration"]:
        '''encryption_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_configuration AthenaWorkgroup#encryption_configuration}
        '''
        result = self._values.get("encryption_configuration")
        return typing.cast(typing.Optional["AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration"], result)

    @builtins.property
    def expected_bucket_owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#expected_bucket_owner AthenaWorkgroup#expected_bucket_owner}.'''
        result = self._values.get("expected_bucket_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#output_location AthenaWorkgroup#output_location}.'''
        result = self._values.get("output_location")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfigurationResultConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationResultConfigurationAclConfiguration",
    jsii_struct_bases=[],
    name_mapping={"s3_acl_option": "s3AclOption"},
)
class AthenaWorkgroupConfigurationResultConfigurationAclConfiguration:
    def __init__(self, *, s3_acl_option: builtins.str) -> None:
        '''
        :param s3_acl_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#s3_acl_option AthenaWorkgroup#s3_acl_option}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AthenaWorkgroupConfigurationResultConfigurationAclConfiguration.__init__)
            check_type(argname="argument s3_acl_option", value=s3_acl_option, expected_type=type_hints["s3_acl_option"])
        self._values: typing.Dict[str, typing.Any] = {
            "s3_acl_option": s3_acl_option,
        }

    @builtins.property
    def s3_acl_option(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#s3_acl_option AthenaWorkgroup#s3_acl_option}.'''
        result = self._values.get("s3_acl_option")
        assert result is not None, "Required property 's3_acl_option' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfigurationResultConfigurationAclConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaWorkgroupConfigurationResultConfigurationAclConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationResultConfigurationAclConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(AthenaWorkgroupConfigurationResultConfigurationAclConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3AclOptionInput")
    def s3_acl_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3AclOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3AclOption")
    def s3_acl_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3AclOption"))

    @s3_acl_option.setter
    def s3_acl_option(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationResultConfigurationAclConfigurationOutputReference, "s3_acl_option").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3AclOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationResultConfigurationAclConfiguration]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationResultConfigurationAclConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaWorkgroupConfigurationResultConfigurationAclConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationResultConfigurationAclConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration",
    jsii_struct_bases=[],
    name_mapping={"encryption_option": "encryptionOption", "kms_key_arn": "kmsKeyArn"},
)
class AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration:
    def __init__(
        self,
        *,
        encryption_option: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_option AthenaWorkgroup#encryption_option}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#kms_key_arn AthenaWorkgroup#kms_key_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration.__init__)
            check_type(argname="argument encryption_option", value=encryption_option, expected_type=type_hints["encryption_option"])
            check_type(argname="argument kms_key_arn", value=kms_key_arn, expected_type=type_hints["kms_key_arn"])
        self._values: typing.Dict[str, typing.Any] = {}
        if encryption_option is not None:
            self._values["encryption_option"] = encryption_option
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn

    @builtins.property
    def encryption_option(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_option AthenaWorkgroup#encryption_option}.'''
        result = self._values.get("encryption_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#kms_key_arn AthenaWorkgroup#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEncryptionOption")
    def reset_encryption_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionOption", []))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionOptionInput")
    def encryption_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionOption")
    def encryption_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionOption"))

    @encryption_option.setter
    def encryption_option(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference, "encryption_option").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference, "kms_key_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AthenaWorkgroupConfigurationResultConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationResultConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(AthenaWorkgroupConfigurationResultConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAclConfiguration")
    def put_acl_configuration(self, *, s3_acl_option: builtins.str) -> None:
        '''
        :param s3_acl_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#s3_acl_option AthenaWorkgroup#s3_acl_option}.
        '''
        value = AthenaWorkgroupConfigurationResultConfigurationAclConfiguration(
            s3_acl_option=s3_acl_option
        )

        return typing.cast(None, jsii.invoke(self, "putAclConfiguration", [value]))

    @jsii.member(jsii_name="putEncryptionConfiguration")
    def put_encryption_configuration(
        self,
        *,
        encryption_option: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_option AthenaWorkgroup#encryption_option}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#kms_key_arn AthenaWorkgroup#kms_key_arn}.
        '''
        value = AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration(
            encryption_option=encryption_option, kms_key_arn=kms_key_arn
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionConfiguration", [value]))

    @jsii.member(jsii_name="resetAclConfiguration")
    def reset_acl_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAclConfiguration", []))

    @jsii.member(jsii_name="resetEncryptionConfiguration")
    def reset_encryption_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionConfiguration", []))

    @jsii.member(jsii_name="resetExpectedBucketOwner")
    def reset_expected_bucket_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpectedBucketOwner", []))

    @jsii.member(jsii_name="resetOutputLocation")
    def reset_output_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputLocation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclConfiguration")
    def acl_configuration(
        self,
    ) -> AthenaWorkgroupConfigurationResultConfigurationAclConfigurationOutputReference:
        return typing.cast(AthenaWorkgroupConfigurationResultConfigurationAclConfigurationOutputReference, jsii.get(self, "aclConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfiguration")
    def encryption_configuration(
        self,
    ) -> AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference:
        return typing.cast(AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference, jsii.get(self, "encryptionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclConfigurationInput")
    def acl_configuration_input(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationResultConfigurationAclConfiguration]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationResultConfigurationAclConfiguration], jsii.get(self, "aclConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfigurationInput")
    def encryption_configuration_input(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration], jsii.get(self, "encryptionConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expectedBucketOwnerInput")
    def expected_bucket_owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expectedBucketOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputLocationInput")
    def output_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expectedBucketOwner")
    def expected_bucket_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expectedBucketOwner"))

    @expected_bucket_owner.setter
    def expected_bucket_owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationResultConfigurationOutputReference, "expected_bucket_owner").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expectedBucketOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputLocation")
    def output_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputLocation"))

    @output_location.setter
    def output_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationResultConfigurationOutputReference, "output_location").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationResultConfiguration]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationResultConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaWorkgroupConfigurationResultConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AthenaWorkgroupConfigurationResultConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "AthenaDataCatalog",
    "AthenaDataCatalogConfig",
    "AthenaDatabase",
    "AthenaDatabaseAclConfiguration",
    "AthenaDatabaseAclConfigurationOutputReference",
    "AthenaDatabaseConfig",
    "AthenaDatabaseEncryptionConfiguration",
    "AthenaDatabaseEncryptionConfigurationOutputReference",
    "AthenaNamedQuery",
    "AthenaNamedQueryConfig",
    "AthenaWorkgroup",
    "AthenaWorkgroupConfig",
    "AthenaWorkgroupConfiguration",
    "AthenaWorkgroupConfigurationEngineVersion",
    "AthenaWorkgroupConfigurationEngineVersionOutputReference",
    "AthenaWorkgroupConfigurationOutputReference",
    "AthenaWorkgroupConfigurationResultConfiguration",
    "AthenaWorkgroupConfigurationResultConfigurationAclConfiguration",
    "AthenaWorkgroupConfigurationResultConfigurationAclConfigurationOutputReference",
    "AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration",
    "AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference",
    "AthenaWorkgroupConfigurationResultConfigurationOutputReference",
]

publication.publish()
