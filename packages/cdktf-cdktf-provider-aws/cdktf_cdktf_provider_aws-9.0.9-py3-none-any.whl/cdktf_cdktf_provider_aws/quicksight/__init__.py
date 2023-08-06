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


class QuicksightDataSource(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSource",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source aws_quicksight_data_source}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        data_source_id: builtins.str,
        name: builtins.str,
        parameters: typing.Union["QuicksightDataSourceParameters", typing.Dict[str, typing.Any]],
        type: builtins.str,
        aws_account_id: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union["QuicksightDataSourceCredentials", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        permission: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["QuicksightDataSourcePermission", typing.Dict[str, typing.Any]]]]] = None,
        ssl_properties: typing.Optional[typing.Union["QuicksightDataSourceSslProperties", typing.Dict[str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc_connection_properties: typing.Optional[typing.Union["QuicksightDataSourceVpcConnectionProperties", typing.Dict[str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source aws_quicksight_data_source} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param data_source_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#data_source_id QuicksightDataSource#data_source_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#name QuicksightDataSource#name}.
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#parameters QuicksightDataSource#parameters}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#type QuicksightDataSource#type}.
        :param aws_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aws_account_id QuicksightDataSource#aws_account_id}.
        :param credentials: credentials block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#credentials QuicksightDataSource#credentials}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#id QuicksightDataSource#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param permission: permission block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#permission QuicksightDataSource#permission}
        :param ssl_properties: ssl_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#ssl_properties QuicksightDataSource#ssl_properties}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#tags QuicksightDataSource#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#tags_all QuicksightDataSource#tags_all}.
        :param vpc_connection_properties: vpc_connection_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#vpc_connection_properties QuicksightDataSource#vpc_connection_properties}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSource.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = QuicksightDataSourceConfig(
            data_source_id=data_source_id,
            name=name,
            parameters=parameters,
            type=type,
            aws_account_id=aws_account_id,
            credentials=credentials,
            id=id,
            permission=permission,
            ssl_properties=ssl_properties,
            tags=tags,
            tags_all=tags_all,
            vpc_connection_properties=vpc_connection_properties,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putCredentials")
    def put_credentials(
        self,
        *,
        copy_source_arn: typing.Optional[builtins.str] = None,
        credential_pair: typing.Optional[typing.Union["QuicksightDataSourceCredentialsCredentialPair", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param copy_source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#copy_source_arn QuicksightDataSource#copy_source_arn}.
        :param credential_pair: credential_pair block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#credential_pair QuicksightDataSource#credential_pair}
        '''
        value = QuicksightDataSourceCredentials(
            copy_source_arn=copy_source_arn, credential_pair=credential_pair
        )

        return typing.cast(None, jsii.invoke(self, "putCredentials", [value]))

    @jsii.member(jsii_name="putParameters")
    def put_parameters(
        self,
        *,
        amazon_elasticsearch: typing.Optional[typing.Union["QuicksightDataSourceParametersAmazonElasticsearch", typing.Dict[str, typing.Any]]] = None,
        athena: typing.Optional[typing.Union["QuicksightDataSourceParametersAthena", typing.Dict[str, typing.Any]]] = None,
        aurora: typing.Optional[typing.Union["QuicksightDataSourceParametersAurora", typing.Dict[str, typing.Any]]] = None,
        aurora_postgresql: typing.Optional[typing.Union["QuicksightDataSourceParametersAuroraPostgresql", typing.Dict[str, typing.Any]]] = None,
        aws_iot_analytics: typing.Optional[typing.Union["QuicksightDataSourceParametersAwsIotAnalytics", typing.Dict[str, typing.Any]]] = None,
        jira: typing.Optional[typing.Union["QuicksightDataSourceParametersJira", typing.Dict[str, typing.Any]]] = None,
        maria_db: typing.Optional[typing.Union["QuicksightDataSourceParametersMariaDb", typing.Dict[str, typing.Any]]] = None,
        mysql: typing.Optional[typing.Union["QuicksightDataSourceParametersMysql", typing.Dict[str, typing.Any]]] = None,
        oracle: typing.Optional[typing.Union["QuicksightDataSourceParametersOracle", typing.Dict[str, typing.Any]]] = None,
        postgresql: typing.Optional[typing.Union["QuicksightDataSourceParametersPostgresql", typing.Dict[str, typing.Any]]] = None,
        presto: typing.Optional[typing.Union["QuicksightDataSourceParametersPresto", typing.Dict[str, typing.Any]]] = None,
        rds: typing.Optional[typing.Union["QuicksightDataSourceParametersRds", typing.Dict[str, typing.Any]]] = None,
        redshift: typing.Optional[typing.Union["QuicksightDataSourceParametersRedshift", typing.Dict[str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union["QuicksightDataSourceParametersS3", typing.Dict[str, typing.Any]]] = None,
        service_now: typing.Optional[typing.Union["QuicksightDataSourceParametersServiceNow", typing.Dict[str, typing.Any]]] = None,
        snowflake: typing.Optional[typing.Union["QuicksightDataSourceParametersSnowflake", typing.Dict[str, typing.Any]]] = None,
        spark: typing.Optional[typing.Union["QuicksightDataSourceParametersSpark", typing.Dict[str, typing.Any]]] = None,
        sql_server: typing.Optional[typing.Union["QuicksightDataSourceParametersSqlServer", typing.Dict[str, typing.Any]]] = None,
        teradata: typing.Optional[typing.Union["QuicksightDataSourceParametersTeradata", typing.Dict[str, typing.Any]]] = None,
        twitter: typing.Optional[typing.Union["QuicksightDataSourceParametersTwitter", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param amazon_elasticsearch: amazon_elasticsearch block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#amazon_elasticsearch QuicksightDataSource#amazon_elasticsearch}
        :param athena: athena block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#athena QuicksightDataSource#athena}
        :param aurora: aurora block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aurora QuicksightDataSource#aurora}
        :param aurora_postgresql: aurora_postgresql block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aurora_postgresql QuicksightDataSource#aurora_postgresql}
        :param aws_iot_analytics: aws_iot_analytics block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aws_iot_analytics QuicksightDataSource#aws_iot_analytics}
        :param jira: jira block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#jira QuicksightDataSource#jira}
        :param maria_db: maria_db block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#maria_db QuicksightDataSource#maria_db}
        :param mysql: mysql block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#mysql QuicksightDataSource#mysql}
        :param oracle: oracle block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#oracle QuicksightDataSource#oracle}
        :param postgresql: postgresql block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#postgresql QuicksightDataSource#postgresql}
        :param presto: presto block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#presto QuicksightDataSource#presto}
        :param rds: rds block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#rds QuicksightDataSource#rds}
        :param redshift: redshift block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#redshift QuicksightDataSource#redshift}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#s3 QuicksightDataSource#s3}
        :param service_now: service_now block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#service_now QuicksightDataSource#service_now}
        :param snowflake: snowflake block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#snowflake QuicksightDataSource#snowflake}
        :param spark: spark block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#spark QuicksightDataSource#spark}
        :param sql_server: sql_server block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#sql_server QuicksightDataSource#sql_server}
        :param teradata: teradata block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#teradata QuicksightDataSource#teradata}
        :param twitter: twitter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#twitter QuicksightDataSource#twitter}
        '''
        value = QuicksightDataSourceParameters(
            amazon_elasticsearch=amazon_elasticsearch,
            athena=athena,
            aurora=aurora,
            aurora_postgresql=aurora_postgresql,
            aws_iot_analytics=aws_iot_analytics,
            jira=jira,
            maria_db=maria_db,
            mysql=mysql,
            oracle=oracle,
            postgresql=postgresql,
            presto=presto,
            rds=rds,
            redshift=redshift,
            s3=s3,
            service_now=service_now,
            snowflake=snowflake,
            spark=spark,
            sql_server=sql_server,
            teradata=teradata,
            twitter=twitter,
        )

        return typing.cast(None, jsii.invoke(self, "putParameters", [value]))

    @jsii.member(jsii_name="putPermission")
    def put_permission(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["QuicksightDataSourcePermission", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSource.put_permission)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPermission", [value]))

    @jsii.member(jsii_name="putSslProperties")
    def put_ssl_properties(
        self,
        *,
        disable_ssl: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param disable_ssl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#disable_ssl QuicksightDataSource#disable_ssl}.
        '''
        value = QuicksightDataSourceSslProperties(disable_ssl=disable_ssl)

        return typing.cast(None, jsii.invoke(self, "putSslProperties", [value]))

    @jsii.member(jsii_name="putVpcConnectionProperties")
    def put_vpc_connection_properties(
        self,
        *,
        vpc_connection_arn: builtins.str,
    ) -> None:
        '''
        :param vpc_connection_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#vpc_connection_arn QuicksightDataSource#vpc_connection_arn}.
        '''
        value = QuicksightDataSourceVpcConnectionProperties(
            vpc_connection_arn=vpc_connection_arn
        )

        return typing.cast(None, jsii.invoke(self, "putVpcConnectionProperties", [value]))

    @jsii.member(jsii_name="resetAwsAccountId")
    def reset_aws_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccountId", []))

    @jsii.member(jsii_name="resetCredentials")
    def reset_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCredentials", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPermission")
    def reset_permission(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermission", []))

    @jsii.member(jsii_name="resetSslProperties")
    def reset_ssl_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslProperties", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetVpcConnectionProperties")
    def reset_vpc_connection_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcConnectionProperties", []))

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
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> "QuicksightDataSourceCredentialsOutputReference":
        return typing.cast("QuicksightDataSourceCredentialsOutputReference", jsii.get(self, "credentials"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "QuicksightDataSourceParametersOutputReference":
        return typing.cast("QuicksightDataSourceParametersOutputReference", jsii.get(self, "parameters"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permission")
    def permission(self) -> "QuicksightDataSourcePermissionList":
        return typing.cast("QuicksightDataSourcePermissionList", jsii.get(self, "permission"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslProperties")
    def ssl_properties(self) -> "QuicksightDataSourceSslPropertiesOutputReference":
        return typing.cast("QuicksightDataSourceSslPropertiesOutputReference", jsii.get(self, "sslProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConnectionProperties")
    def vpc_connection_properties(
        self,
    ) -> "QuicksightDataSourceVpcConnectionPropertiesOutputReference":
        return typing.cast("QuicksightDataSourceVpcConnectionPropertiesOutputReference", jsii.get(self, "vpcConnectionProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsAccountIdInput")
    def aws_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentialsInput")
    def credentials_input(self) -> typing.Optional["QuicksightDataSourceCredentials"]:
        return typing.cast(typing.Optional["QuicksightDataSourceCredentials"], jsii.get(self, "credentialsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSourceIdInput")
    def data_source_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSourceIdInput"))

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
    def parameters_input(self) -> typing.Optional["QuicksightDataSourceParameters"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParameters"], jsii.get(self, "parametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionInput")
    def permission_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["QuicksightDataSourcePermission"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["QuicksightDataSourcePermission"]]], jsii.get(self, "permissionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslPropertiesInput")
    def ssl_properties_input(
        self,
    ) -> typing.Optional["QuicksightDataSourceSslProperties"]:
        return typing.cast(typing.Optional["QuicksightDataSourceSslProperties"], jsii.get(self, "sslPropertiesInput"))

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
    @jsii.member(jsii_name="vpcConnectionPropertiesInput")
    def vpc_connection_properties_input(
        self,
    ) -> typing.Optional["QuicksightDataSourceVpcConnectionProperties"]:
        return typing.cast(typing.Optional["QuicksightDataSourceVpcConnectionProperties"], jsii.get(self, "vpcConnectionPropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsAccountId")
    def aws_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccountId"))

    @aws_account_id.setter
    def aws_account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSource, "aws_account_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSourceId")
    def data_source_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSourceId"))

    @data_source_id.setter
    def data_source_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSource, "data_source_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSourceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSource, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSource, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSource, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSource, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSource, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "data_source_id": "dataSourceId",
        "name": "name",
        "parameters": "parameters",
        "type": "type",
        "aws_account_id": "awsAccountId",
        "credentials": "credentials",
        "id": "id",
        "permission": "permission",
        "ssl_properties": "sslProperties",
        "tags": "tags",
        "tags_all": "tagsAll",
        "vpc_connection_properties": "vpcConnectionProperties",
    },
)
class QuicksightDataSourceConfig(cdktf.TerraformMetaArguments):
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
        data_source_id: builtins.str,
        name: builtins.str,
        parameters: typing.Union["QuicksightDataSourceParameters", typing.Dict[str, typing.Any]],
        type: builtins.str,
        aws_account_id: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[typing.Union["QuicksightDataSourceCredentials", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        permission: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["QuicksightDataSourcePermission", typing.Dict[str, typing.Any]]]]] = None,
        ssl_properties: typing.Optional[typing.Union["QuicksightDataSourceSslProperties", typing.Dict[str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc_connection_properties: typing.Optional[typing.Union["QuicksightDataSourceVpcConnectionProperties", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''AWS QuickSight.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param data_source_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#data_source_id QuicksightDataSource#data_source_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#name QuicksightDataSource#name}.
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#parameters QuicksightDataSource#parameters}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#type QuicksightDataSource#type}.
        :param aws_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aws_account_id QuicksightDataSource#aws_account_id}.
        :param credentials: credentials block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#credentials QuicksightDataSource#credentials}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#id QuicksightDataSource#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param permission: permission block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#permission QuicksightDataSource#permission}
        :param ssl_properties: ssl_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#ssl_properties QuicksightDataSource#ssl_properties}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#tags QuicksightDataSource#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#tags_all QuicksightDataSource#tags_all}.
        :param vpc_connection_properties: vpc_connection_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#vpc_connection_properties QuicksightDataSource#vpc_connection_properties}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(parameters, dict):
            parameters = QuicksightDataSourceParameters(**parameters)
        if isinstance(credentials, dict):
            credentials = QuicksightDataSourceCredentials(**credentials)
        if isinstance(ssl_properties, dict):
            ssl_properties = QuicksightDataSourceSslProperties(**ssl_properties)
        if isinstance(vpc_connection_properties, dict):
            vpc_connection_properties = QuicksightDataSourceVpcConnectionProperties(**vpc_connection_properties)
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument data_source_id", value=data_source_id, expected_type=type_hints["data_source_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument aws_account_id", value=aws_account_id, expected_type=type_hints["aws_account_id"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
            check_type(argname="argument ssl_properties", value=ssl_properties, expected_type=type_hints["ssl_properties"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
            check_type(argname="argument vpc_connection_properties", value=vpc_connection_properties, expected_type=type_hints["vpc_connection_properties"])
        self._values: typing.Dict[str, typing.Any] = {
            "data_source_id": data_source_id,
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
        if aws_account_id is not None:
            self._values["aws_account_id"] = aws_account_id
        if credentials is not None:
            self._values["credentials"] = credentials
        if id is not None:
            self._values["id"] = id
        if permission is not None:
            self._values["permission"] = permission
        if ssl_properties is not None:
            self._values["ssl_properties"] = ssl_properties
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if vpc_connection_properties is not None:
            self._values["vpc_connection_properties"] = vpc_connection_properties

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
    def data_source_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#data_source_id QuicksightDataSource#data_source_id}.'''
        result = self._values.get("data_source_id")
        assert result is not None, "Required property 'data_source_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#name QuicksightDataSource#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters(self) -> "QuicksightDataSourceParameters":
        '''parameters block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#parameters QuicksightDataSource#parameters}
        '''
        result = self._values.get("parameters")
        assert result is not None, "Required property 'parameters' is missing"
        return typing.cast("QuicksightDataSourceParameters", result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#type QuicksightDataSource#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aws_account_id QuicksightDataSource#aws_account_id}.'''
        result = self._values.get("aws_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(self) -> typing.Optional["QuicksightDataSourceCredentials"]:
        '''credentials block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#credentials QuicksightDataSource#credentials}
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional["QuicksightDataSourceCredentials"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#id QuicksightDataSource#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permission(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["QuicksightDataSourcePermission"]]]:
        '''permission block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#permission QuicksightDataSource#permission}
        '''
        result = self._values.get("permission")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["QuicksightDataSourcePermission"]]], result)

    @builtins.property
    def ssl_properties(self) -> typing.Optional["QuicksightDataSourceSslProperties"]:
        '''ssl_properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#ssl_properties QuicksightDataSource#ssl_properties}
        '''
        result = self._values.get("ssl_properties")
        return typing.cast(typing.Optional["QuicksightDataSourceSslProperties"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#tags QuicksightDataSource#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#tags_all QuicksightDataSource#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def vpc_connection_properties(
        self,
    ) -> typing.Optional["QuicksightDataSourceVpcConnectionProperties"]:
        '''vpc_connection_properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#vpc_connection_properties QuicksightDataSource#vpc_connection_properties}
        '''
        result = self._values.get("vpc_connection_properties")
        return typing.cast(typing.Optional["QuicksightDataSourceVpcConnectionProperties"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceCredentials",
    jsii_struct_bases=[],
    name_mapping={
        "copy_source_arn": "copySourceArn",
        "credential_pair": "credentialPair",
    },
)
class QuicksightDataSourceCredentials:
    def __init__(
        self,
        *,
        copy_source_arn: typing.Optional[builtins.str] = None,
        credential_pair: typing.Optional[typing.Union["QuicksightDataSourceCredentialsCredentialPair", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param copy_source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#copy_source_arn QuicksightDataSource#copy_source_arn}.
        :param credential_pair: credential_pair block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#credential_pair QuicksightDataSource#credential_pair}
        '''
        if isinstance(credential_pair, dict):
            credential_pair = QuicksightDataSourceCredentialsCredentialPair(**credential_pair)
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceCredentials.__init__)
            check_type(argname="argument copy_source_arn", value=copy_source_arn, expected_type=type_hints["copy_source_arn"])
            check_type(argname="argument credential_pair", value=credential_pair, expected_type=type_hints["credential_pair"])
        self._values: typing.Dict[str, typing.Any] = {}
        if copy_source_arn is not None:
            self._values["copy_source_arn"] = copy_source_arn
        if credential_pair is not None:
            self._values["credential_pair"] = credential_pair

    @builtins.property
    def copy_source_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#copy_source_arn QuicksightDataSource#copy_source_arn}.'''
        result = self._values.get("copy_source_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credential_pair(
        self,
    ) -> typing.Optional["QuicksightDataSourceCredentialsCredentialPair"]:
        '''credential_pair block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#credential_pair QuicksightDataSource#credential_pair}
        '''
        result = self._values.get("credential_pair")
        return typing.cast(typing.Optional["QuicksightDataSourceCredentialsCredentialPair"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceCredentials(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceCredentialsCredentialPair",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class QuicksightDataSourceCredentialsCredentialPair:
    def __init__(self, *, password: builtins.str, username: builtins.str) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#password QuicksightDataSource#password}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#username QuicksightDataSource#username}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceCredentialsCredentialPair.__init__)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#password QuicksightDataSource#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#username QuicksightDataSource#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceCredentialsCredentialPair(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceCredentialsCredentialPairOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceCredentialsCredentialPairOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceCredentialsCredentialPairOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceCredentialsCredentialPairOutputReference, "password").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceCredentialsCredentialPairOutputReference, "username").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QuicksightDataSourceCredentialsCredentialPair]:
        return typing.cast(typing.Optional[QuicksightDataSourceCredentialsCredentialPair], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceCredentialsCredentialPair],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceCredentialsCredentialPairOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class QuicksightDataSourceCredentialsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceCredentialsOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceCredentialsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCredentialPair")
    def put_credential_pair(
        self,
        *,
        password: builtins.str,
        username: builtins.str,
    ) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#password QuicksightDataSource#password}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#username QuicksightDataSource#username}.
        '''
        value = QuicksightDataSourceCredentialsCredentialPair(
            password=password, username=username
        )

        return typing.cast(None, jsii.invoke(self, "putCredentialPair", [value]))

    @jsii.member(jsii_name="resetCopySourceArn")
    def reset_copy_source_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopySourceArn", []))

    @jsii.member(jsii_name="resetCredentialPair")
    def reset_credential_pair(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCredentialPair", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentialPair")
    def credential_pair(
        self,
    ) -> QuicksightDataSourceCredentialsCredentialPairOutputReference:
        return typing.cast(QuicksightDataSourceCredentialsCredentialPairOutputReference, jsii.get(self, "credentialPair"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copySourceArnInput")
    def copy_source_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copySourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentialPairInput")
    def credential_pair_input(
        self,
    ) -> typing.Optional[QuicksightDataSourceCredentialsCredentialPair]:
        return typing.cast(typing.Optional[QuicksightDataSourceCredentialsCredentialPair], jsii.get(self, "credentialPairInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copySourceArn")
    def copy_source_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copySourceArn"))

    @copy_source_arn.setter
    def copy_source_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceCredentialsOutputReference, "copy_source_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "copySourceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceCredentials]:
        return typing.cast(typing.Optional[QuicksightDataSourceCredentials], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceCredentials],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceCredentialsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParameters",
    jsii_struct_bases=[],
    name_mapping={
        "amazon_elasticsearch": "amazonElasticsearch",
        "athena": "athena",
        "aurora": "aurora",
        "aurora_postgresql": "auroraPostgresql",
        "aws_iot_analytics": "awsIotAnalytics",
        "jira": "jira",
        "maria_db": "mariaDb",
        "mysql": "mysql",
        "oracle": "oracle",
        "postgresql": "postgresql",
        "presto": "presto",
        "rds": "rds",
        "redshift": "redshift",
        "s3": "s3",
        "service_now": "serviceNow",
        "snowflake": "snowflake",
        "spark": "spark",
        "sql_server": "sqlServer",
        "teradata": "teradata",
        "twitter": "twitter",
    },
)
class QuicksightDataSourceParameters:
    def __init__(
        self,
        *,
        amazon_elasticsearch: typing.Optional[typing.Union["QuicksightDataSourceParametersAmazonElasticsearch", typing.Dict[str, typing.Any]]] = None,
        athena: typing.Optional[typing.Union["QuicksightDataSourceParametersAthena", typing.Dict[str, typing.Any]]] = None,
        aurora: typing.Optional[typing.Union["QuicksightDataSourceParametersAurora", typing.Dict[str, typing.Any]]] = None,
        aurora_postgresql: typing.Optional[typing.Union["QuicksightDataSourceParametersAuroraPostgresql", typing.Dict[str, typing.Any]]] = None,
        aws_iot_analytics: typing.Optional[typing.Union["QuicksightDataSourceParametersAwsIotAnalytics", typing.Dict[str, typing.Any]]] = None,
        jira: typing.Optional[typing.Union["QuicksightDataSourceParametersJira", typing.Dict[str, typing.Any]]] = None,
        maria_db: typing.Optional[typing.Union["QuicksightDataSourceParametersMariaDb", typing.Dict[str, typing.Any]]] = None,
        mysql: typing.Optional[typing.Union["QuicksightDataSourceParametersMysql", typing.Dict[str, typing.Any]]] = None,
        oracle: typing.Optional[typing.Union["QuicksightDataSourceParametersOracle", typing.Dict[str, typing.Any]]] = None,
        postgresql: typing.Optional[typing.Union["QuicksightDataSourceParametersPostgresql", typing.Dict[str, typing.Any]]] = None,
        presto: typing.Optional[typing.Union["QuicksightDataSourceParametersPresto", typing.Dict[str, typing.Any]]] = None,
        rds: typing.Optional[typing.Union["QuicksightDataSourceParametersRds", typing.Dict[str, typing.Any]]] = None,
        redshift: typing.Optional[typing.Union["QuicksightDataSourceParametersRedshift", typing.Dict[str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union["QuicksightDataSourceParametersS3", typing.Dict[str, typing.Any]]] = None,
        service_now: typing.Optional[typing.Union["QuicksightDataSourceParametersServiceNow", typing.Dict[str, typing.Any]]] = None,
        snowflake: typing.Optional[typing.Union["QuicksightDataSourceParametersSnowflake", typing.Dict[str, typing.Any]]] = None,
        spark: typing.Optional[typing.Union["QuicksightDataSourceParametersSpark", typing.Dict[str, typing.Any]]] = None,
        sql_server: typing.Optional[typing.Union["QuicksightDataSourceParametersSqlServer", typing.Dict[str, typing.Any]]] = None,
        teradata: typing.Optional[typing.Union["QuicksightDataSourceParametersTeradata", typing.Dict[str, typing.Any]]] = None,
        twitter: typing.Optional[typing.Union["QuicksightDataSourceParametersTwitter", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param amazon_elasticsearch: amazon_elasticsearch block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#amazon_elasticsearch QuicksightDataSource#amazon_elasticsearch}
        :param athena: athena block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#athena QuicksightDataSource#athena}
        :param aurora: aurora block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aurora QuicksightDataSource#aurora}
        :param aurora_postgresql: aurora_postgresql block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aurora_postgresql QuicksightDataSource#aurora_postgresql}
        :param aws_iot_analytics: aws_iot_analytics block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aws_iot_analytics QuicksightDataSource#aws_iot_analytics}
        :param jira: jira block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#jira QuicksightDataSource#jira}
        :param maria_db: maria_db block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#maria_db QuicksightDataSource#maria_db}
        :param mysql: mysql block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#mysql QuicksightDataSource#mysql}
        :param oracle: oracle block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#oracle QuicksightDataSource#oracle}
        :param postgresql: postgresql block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#postgresql QuicksightDataSource#postgresql}
        :param presto: presto block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#presto QuicksightDataSource#presto}
        :param rds: rds block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#rds QuicksightDataSource#rds}
        :param redshift: redshift block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#redshift QuicksightDataSource#redshift}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#s3 QuicksightDataSource#s3}
        :param service_now: service_now block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#service_now QuicksightDataSource#service_now}
        :param snowflake: snowflake block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#snowflake QuicksightDataSource#snowflake}
        :param spark: spark block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#spark QuicksightDataSource#spark}
        :param sql_server: sql_server block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#sql_server QuicksightDataSource#sql_server}
        :param teradata: teradata block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#teradata QuicksightDataSource#teradata}
        :param twitter: twitter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#twitter QuicksightDataSource#twitter}
        '''
        if isinstance(amazon_elasticsearch, dict):
            amazon_elasticsearch = QuicksightDataSourceParametersAmazonElasticsearch(**amazon_elasticsearch)
        if isinstance(athena, dict):
            athena = QuicksightDataSourceParametersAthena(**athena)
        if isinstance(aurora, dict):
            aurora = QuicksightDataSourceParametersAurora(**aurora)
        if isinstance(aurora_postgresql, dict):
            aurora_postgresql = QuicksightDataSourceParametersAuroraPostgresql(**aurora_postgresql)
        if isinstance(aws_iot_analytics, dict):
            aws_iot_analytics = QuicksightDataSourceParametersAwsIotAnalytics(**aws_iot_analytics)
        if isinstance(jira, dict):
            jira = QuicksightDataSourceParametersJira(**jira)
        if isinstance(maria_db, dict):
            maria_db = QuicksightDataSourceParametersMariaDb(**maria_db)
        if isinstance(mysql, dict):
            mysql = QuicksightDataSourceParametersMysql(**mysql)
        if isinstance(oracle, dict):
            oracle = QuicksightDataSourceParametersOracle(**oracle)
        if isinstance(postgresql, dict):
            postgresql = QuicksightDataSourceParametersPostgresql(**postgresql)
        if isinstance(presto, dict):
            presto = QuicksightDataSourceParametersPresto(**presto)
        if isinstance(rds, dict):
            rds = QuicksightDataSourceParametersRds(**rds)
        if isinstance(redshift, dict):
            redshift = QuicksightDataSourceParametersRedshift(**redshift)
        if isinstance(s3, dict):
            s3 = QuicksightDataSourceParametersS3(**s3)
        if isinstance(service_now, dict):
            service_now = QuicksightDataSourceParametersServiceNow(**service_now)
        if isinstance(snowflake, dict):
            snowflake = QuicksightDataSourceParametersSnowflake(**snowflake)
        if isinstance(spark, dict):
            spark = QuicksightDataSourceParametersSpark(**spark)
        if isinstance(sql_server, dict):
            sql_server = QuicksightDataSourceParametersSqlServer(**sql_server)
        if isinstance(teradata, dict):
            teradata = QuicksightDataSourceParametersTeradata(**teradata)
        if isinstance(twitter, dict):
            twitter = QuicksightDataSourceParametersTwitter(**twitter)
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParameters.__init__)
            check_type(argname="argument amazon_elasticsearch", value=amazon_elasticsearch, expected_type=type_hints["amazon_elasticsearch"])
            check_type(argname="argument athena", value=athena, expected_type=type_hints["athena"])
            check_type(argname="argument aurora", value=aurora, expected_type=type_hints["aurora"])
            check_type(argname="argument aurora_postgresql", value=aurora_postgresql, expected_type=type_hints["aurora_postgresql"])
            check_type(argname="argument aws_iot_analytics", value=aws_iot_analytics, expected_type=type_hints["aws_iot_analytics"])
            check_type(argname="argument jira", value=jira, expected_type=type_hints["jira"])
            check_type(argname="argument maria_db", value=maria_db, expected_type=type_hints["maria_db"])
            check_type(argname="argument mysql", value=mysql, expected_type=type_hints["mysql"])
            check_type(argname="argument oracle", value=oracle, expected_type=type_hints["oracle"])
            check_type(argname="argument postgresql", value=postgresql, expected_type=type_hints["postgresql"])
            check_type(argname="argument presto", value=presto, expected_type=type_hints["presto"])
            check_type(argname="argument rds", value=rds, expected_type=type_hints["rds"])
            check_type(argname="argument redshift", value=redshift, expected_type=type_hints["redshift"])
            check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
            check_type(argname="argument service_now", value=service_now, expected_type=type_hints["service_now"])
            check_type(argname="argument snowflake", value=snowflake, expected_type=type_hints["snowflake"])
            check_type(argname="argument spark", value=spark, expected_type=type_hints["spark"])
            check_type(argname="argument sql_server", value=sql_server, expected_type=type_hints["sql_server"])
            check_type(argname="argument teradata", value=teradata, expected_type=type_hints["teradata"])
            check_type(argname="argument twitter", value=twitter, expected_type=type_hints["twitter"])
        self._values: typing.Dict[str, typing.Any] = {}
        if amazon_elasticsearch is not None:
            self._values["amazon_elasticsearch"] = amazon_elasticsearch
        if athena is not None:
            self._values["athena"] = athena
        if aurora is not None:
            self._values["aurora"] = aurora
        if aurora_postgresql is not None:
            self._values["aurora_postgresql"] = aurora_postgresql
        if aws_iot_analytics is not None:
            self._values["aws_iot_analytics"] = aws_iot_analytics
        if jira is not None:
            self._values["jira"] = jira
        if maria_db is not None:
            self._values["maria_db"] = maria_db
        if mysql is not None:
            self._values["mysql"] = mysql
        if oracle is not None:
            self._values["oracle"] = oracle
        if postgresql is not None:
            self._values["postgresql"] = postgresql
        if presto is not None:
            self._values["presto"] = presto
        if rds is not None:
            self._values["rds"] = rds
        if redshift is not None:
            self._values["redshift"] = redshift
        if s3 is not None:
            self._values["s3"] = s3
        if service_now is not None:
            self._values["service_now"] = service_now
        if snowflake is not None:
            self._values["snowflake"] = snowflake
        if spark is not None:
            self._values["spark"] = spark
        if sql_server is not None:
            self._values["sql_server"] = sql_server
        if teradata is not None:
            self._values["teradata"] = teradata
        if twitter is not None:
            self._values["twitter"] = twitter

    @builtins.property
    def amazon_elasticsearch(
        self,
    ) -> typing.Optional["QuicksightDataSourceParametersAmazonElasticsearch"]:
        '''amazon_elasticsearch block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#amazon_elasticsearch QuicksightDataSource#amazon_elasticsearch}
        '''
        result = self._values.get("amazon_elasticsearch")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersAmazonElasticsearch"], result)

    @builtins.property
    def athena(self) -> typing.Optional["QuicksightDataSourceParametersAthena"]:
        '''athena block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#athena QuicksightDataSource#athena}
        '''
        result = self._values.get("athena")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersAthena"], result)

    @builtins.property
    def aurora(self) -> typing.Optional["QuicksightDataSourceParametersAurora"]:
        '''aurora block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aurora QuicksightDataSource#aurora}
        '''
        result = self._values.get("aurora")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersAurora"], result)

    @builtins.property
    def aurora_postgresql(
        self,
    ) -> typing.Optional["QuicksightDataSourceParametersAuroraPostgresql"]:
        '''aurora_postgresql block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aurora_postgresql QuicksightDataSource#aurora_postgresql}
        '''
        result = self._values.get("aurora_postgresql")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersAuroraPostgresql"], result)

    @builtins.property
    def aws_iot_analytics(
        self,
    ) -> typing.Optional["QuicksightDataSourceParametersAwsIotAnalytics"]:
        '''aws_iot_analytics block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#aws_iot_analytics QuicksightDataSource#aws_iot_analytics}
        '''
        result = self._values.get("aws_iot_analytics")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersAwsIotAnalytics"], result)

    @builtins.property
    def jira(self) -> typing.Optional["QuicksightDataSourceParametersJira"]:
        '''jira block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#jira QuicksightDataSource#jira}
        '''
        result = self._values.get("jira")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersJira"], result)

    @builtins.property
    def maria_db(self) -> typing.Optional["QuicksightDataSourceParametersMariaDb"]:
        '''maria_db block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#maria_db QuicksightDataSource#maria_db}
        '''
        result = self._values.get("maria_db")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersMariaDb"], result)

    @builtins.property
    def mysql(self) -> typing.Optional["QuicksightDataSourceParametersMysql"]:
        '''mysql block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#mysql QuicksightDataSource#mysql}
        '''
        result = self._values.get("mysql")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersMysql"], result)

    @builtins.property
    def oracle(self) -> typing.Optional["QuicksightDataSourceParametersOracle"]:
        '''oracle block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#oracle QuicksightDataSource#oracle}
        '''
        result = self._values.get("oracle")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersOracle"], result)

    @builtins.property
    def postgresql(self) -> typing.Optional["QuicksightDataSourceParametersPostgresql"]:
        '''postgresql block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#postgresql QuicksightDataSource#postgresql}
        '''
        result = self._values.get("postgresql")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersPostgresql"], result)

    @builtins.property
    def presto(self) -> typing.Optional["QuicksightDataSourceParametersPresto"]:
        '''presto block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#presto QuicksightDataSource#presto}
        '''
        result = self._values.get("presto")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersPresto"], result)

    @builtins.property
    def rds(self) -> typing.Optional["QuicksightDataSourceParametersRds"]:
        '''rds block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#rds QuicksightDataSource#rds}
        '''
        result = self._values.get("rds")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersRds"], result)

    @builtins.property
    def redshift(self) -> typing.Optional["QuicksightDataSourceParametersRedshift"]:
        '''redshift block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#redshift QuicksightDataSource#redshift}
        '''
        result = self._values.get("redshift")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersRedshift"], result)

    @builtins.property
    def s3(self) -> typing.Optional["QuicksightDataSourceParametersS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#s3 QuicksightDataSource#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersS3"], result)

    @builtins.property
    def service_now(
        self,
    ) -> typing.Optional["QuicksightDataSourceParametersServiceNow"]:
        '''service_now block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#service_now QuicksightDataSource#service_now}
        '''
        result = self._values.get("service_now")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersServiceNow"], result)

    @builtins.property
    def snowflake(self) -> typing.Optional["QuicksightDataSourceParametersSnowflake"]:
        '''snowflake block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#snowflake QuicksightDataSource#snowflake}
        '''
        result = self._values.get("snowflake")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersSnowflake"], result)

    @builtins.property
    def spark(self) -> typing.Optional["QuicksightDataSourceParametersSpark"]:
        '''spark block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#spark QuicksightDataSource#spark}
        '''
        result = self._values.get("spark")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersSpark"], result)

    @builtins.property
    def sql_server(self) -> typing.Optional["QuicksightDataSourceParametersSqlServer"]:
        '''sql_server block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#sql_server QuicksightDataSource#sql_server}
        '''
        result = self._values.get("sql_server")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersSqlServer"], result)

    @builtins.property
    def teradata(self) -> typing.Optional["QuicksightDataSourceParametersTeradata"]:
        '''teradata block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#teradata QuicksightDataSource#teradata}
        '''
        result = self._values.get("teradata")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersTeradata"], result)

    @builtins.property
    def twitter(self) -> typing.Optional["QuicksightDataSourceParametersTwitter"]:
        '''twitter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#twitter QuicksightDataSource#twitter}
        '''
        result = self._values.get("twitter")
        return typing.cast(typing.Optional["QuicksightDataSourceParametersTwitter"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersAmazonElasticsearch",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain"},
)
class QuicksightDataSourceParametersAmazonElasticsearch:
    def __init__(self, *, domain: builtins.str) -> None:
        '''
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#domain QuicksightDataSource#domain}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersAmazonElasticsearch.__init__)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
        }

    @builtins.property
    def domain(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#domain QuicksightDataSource#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersAmazonElasticsearch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersAmazonElasticsearchOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersAmazonElasticsearchOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersAmazonElasticsearchOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAmazonElasticsearchOutputReference, "domain").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersAmazonElasticsearch]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersAmazonElasticsearch], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersAmazonElasticsearch],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAmazonElasticsearchOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersAthena",
    jsii_struct_bases=[],
    name_mapping={"work_group": "workGroup"},
)
class QuicksightDataSourceParametersAthena:
    def __init__(self, *, work_group: typing.Optional[builtins.str] = None) -> None:
        '''
        :param work_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#work_group QuicksightDataSource#work_group}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersAthena.__init__)
            check_type(argname="argument work_group", value=work_group, expected_type=type_hints["work_group"])
        self._values: typing.Dict[str, typing.Any] = {}
        if work_group is not None:
            self._values["work_group"] = work_group

    @builtins.property
    def work_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#work_group QuicksightDataSource#work_group}.'''
        result = self._values.get("work_group")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersAthena(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersAthenaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersAthenaOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersAthenaOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetWorkGroup")
    def reset_work_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkGroup", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workGroupInput")
    def work_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workGroup")
    def work_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workGroup"))

    @work_group.setter
    def work_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAthenaOutputReference, "work_group").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersAthena]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersAthena], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersAthena],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAthenaOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersAurora",
    jsii_struct_bases=[],
    name_mapping={"database": "database", "host": "host", "port": "port"},
)
class QuicksightDataSourceParametersAurora:
    def __init__(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersAurora.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "host": host,
            "port": port,
        }

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersAurora(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersAuroraOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersAuroraOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersAuroraOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAuroraOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAuroraOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAuroraOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersAurora]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersAurora], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersAurora],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAuroraOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersAuroraPostgresql",
    jsii_struct_bases=[],
    name_mapping={"database": "database", "host": "host", "port": "port"},
)
class QuicksightDataSourceParametersAuroraPostgresql:
    def __init__(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersAuroraPostgresql.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "host": host,
            "port": port,
        }

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersAuroraPostgresql(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersAuroraPostgresqlOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersAuroraPostgresqlOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersAuroraPostgresqlOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAuroraPostgresqlOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAuroraPostgresqlOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAuroraPostgresqlOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersAuroraPostgresql]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersAuroraPostgresql], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersAuroraPostgresql],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAuroraPostgresqlOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersAwsIotAnalytics",
    jsii_struct_bases=[],
    name_mapping={"data_set_name": "dataSetName"},
)
class QuicksightDataSourceParametersAwsIotAnalytics:
    def __init__(self, *, data_set_name: builtins.str) -> None:
        '''
        :param data_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#data_set_name QuicksightDataSource#data_set_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersAwsIotAnalytics.__init__)
            check_type(argname="argument data_set_name", value=data_set_name, expected_type=type_hints["data_set_name"])
        self._values: typing.Dict[str, typing.Any] = {
            "data_set_name": data_set_name,
        }

    @builtins.property
    def data_set_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#data_set_name QuicksightDataSource#data_set_name}.'''
        result = self._values.get("data_set_name")
        assert result is not None, "Required property 'data_set_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersAwsIotAnalytics(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersAwsIotAnalyticsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersAwsIotAnalyticsOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersAwsIotAnalyticsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSetNameInput")
    def data_set_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSetName")
    def data_set_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSetName"))

    @data_set_name.setter
    def data_set_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAwsIotAnalyticsOutputReference, "data_set_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSetName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersAwsIotAnalytics]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersAwsIotAnalytics], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersAwsIotAnalytics],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersAwsIotAnalyticsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersJira",
    jsii_struct_bases=[],
    name_mapping={"site_base_url": "siteBaseUrl"},
)
class QuicksightDataSourceParametersJira:
    def __init__(self, *, site_base_url: builtins.str) -> None:
        '''
        :param site_base_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#site_base_url QuicksightDataSource#site_base_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersJira.__init__)
            check_type(argname="argument site_base_url", value=site_base_url, expected_type=type_hints["site_base_url"])
        self._values: typing.Dict[str, typing.Any] = {
            "site_base_url": site_base_url,
        }

    @builtins.property
    def site_base_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#site_base_url QuicksightDataSource#site_base_url}.'''
        result = self._values.get("site_base_url")
        assert result is not None, "Required property 'site_base_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersJira(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersJiraOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersJiraOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersJiraOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="siteBaseUrlInput")
    def site_base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "siteBaseUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="siteBaseUrl")
    def site_base_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "siteBaseUrl"))

    @site_base_url.setter
    def site_base_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersJiraOutputReference, "site_base_url").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "siteBaseUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersJira]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersJira], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersJira],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersJiraOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersMariaDb",
    jsii_struct_bases=[],
    name_mapping={"database": "database", "host": "host", "port": "port"},
)
class QuicksightDataSourceParametersMariaDb:
    def __init__(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersMariaDb.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "host": host,
            "port": port,
        }

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersMariaDb(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersMariaDbOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersMariaDbOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersMariaDbOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersMariaDbOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersMariaDbOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersMariaDbOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersMariaDb]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersMariaDb], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersMariaDb],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersMariaDbOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersMysql",
    jsii_struct_bases=[],
    name_mapping={"database": "database", "host": "host", "port": "port"},
)
class QuicksightDataSourceParametersMysql:
    def __init__(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersMysql.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "host": host,
            "port": port,
        }

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersMysql(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersMysqlOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersMysqlOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersMysqlOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersMysqlOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersMysqlOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersMysqlOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersMysql]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersMysql], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersMysql],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersMysqlOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersOracle",
    jsii_struct_bases=[],
    name_mapping={"database": "database", "host": "host", "port": "port"},
)
class QuicksightDataSourceParametersOracle:
    def __init__(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersOracle.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "host": host,
            "port": port,
        }

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersOracle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersOracleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersOracleOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersOracleOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersOracleOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersOracleOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersOracleOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersOracle]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersOracle], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersOracle],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersOracleOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class QuicksightDataSourceParametersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAmazonElasticsearch")
    def put_amazon_elasticsearch(self, *, domain: builtins.str) -> None:
        '''
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#domain QuicksightDataSource#domain}.
        '''
        value = QuicksightDataSourceParametersAmazonElasticsearch(domain=domain)

        return typing.cast(None, jsii.invoke(self, "putAmazonElasticsearch", [value]))

    @jsii.member(jsii_name="putAthena")
    def put_athena(self, *, work_group: typing.Optional[builtins.str] = None) -> None:
        '''
        :param work_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#work_group QuicksightDataSource#work_group}.
        '''
        value = QuicksightDataSourceParametersAthena(work_group=work_group)

        return typing.cast(None, jsii.invoke(self, "putAthena", [value]))

    @jsii.member(jsii_name="putAurora")
    def put_aurora(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersAurora(
            database=database, host=host, port=port
        )

        return typing.cast(None, jsii.invoke(self, "putAurora", [value]))

    @jsii.member(jsii_name="putAuroraPostgresql")
    def put_aurora_postgresql(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersAuroraPostgresql(
            database=database, host=host, port=port
        )

        return typing.cast(None, jsii.invoke(self, "putAuroraPostgresql", [value]))

    @jsii.member(jsii_name="putAwsIotAnalytics")
    def put_aws_iot_analytics(self, *, data_set_name: builtins.str) -> None:
        '''
        :param data_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#data_set_name QuicksightDataSource#data_set_name}.
        '''
        value = QuicksightDataSourceParametersAwsIotAnalytics(
            data_set_name=data_set_name
        )

        return typing.cast(None, jsii.invoke(self, "putAwsIotAnalytics", [value]))

    @jsii.member(jsii_name="putJira")
    def put_jira(self, *, site_base_url: builtins.str) -> None:
        '''
        :param site_base_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#site_base_url QuicksightDataSource#site_base_url}.
        '''
        value = QuicksightDataSourceParametersJira(site_base_url=site_base_url)

        return typing.cast(None, jsii.invoke(self, "putJira", [value]))

    @jsii.member(jsii_name="putMariaDb")
    def put_maria_db(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersMariaDb(
            database=database, host=host, port=port
        )

        return typing.cast(None, jsii.invoke(self, "putMariaDb", [value]))

    @jsii.member(jsii_name="putMysql")
    def put_mysql(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersMysql(
            database=database, host=host, port=port
        )

        return typing.cast(None, jsii.invoke(self, "putMysql", [value]))

    @jsii.member(jsii_name="putOracle")
    def put_oracle(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersOracle(
            database=database, host=host, port=port
        )

        return typing.cast(None, jsii.invoke(self, "putOracle", [value]))

    @jsii.member(jsii_name="putPostgresql")
    def put_postgresql(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersPostgresql(
            database=database, host=host, port=port
        )

        return typing.cast(None, jsii.invoke(self, "putPostgresql", [value]))

    @jsii.member(jsii_name="putPresto")
    def put_presto(
        self,
        *,
        catalog: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param catalog: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#catalog QuicksightDataSource#catalog}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersPresto(
            catalog=catalog, host=host, port=port
        )

        return typing.cast(None, jsii.invoke(self, "putPresto", [value]))

    @jsii.member(jsii_name="putRds")
    def put_rds(self, *, database: builtins.str, instance_id: builtins.str) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#instance_id QuicksightDataSource#instance_id}.
        '''
        value = QuicksightDataSourceParametersRds(
            database=database, instance_id=instance_id
        )

        return typing.cast(None, jsii.invoke(self, "putRds", [value]))

    @jsii.member(jsii_name="putRedshift")
    def put_redshift(
        self,
        *,
        database: builtins.str,
        cluster_id: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#cluster_id QuicksightDataSource#cluster_id}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersRedshift(
            database=database, cluster_id=cluster_id, host=host, port=port
        )

        return typing.cast(None, jsii.invoke(self, "putRedshift", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        manifest_file_location: typing.Union["QuicksightDataSourceParametersS3ManifestFileLocation", typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param manifest_file_location: manifest_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#manifest_file_location QuicksightDataSource#manifest_file_location}
        '''
        value = QuicksightDataSourceParametersS3(
            manifest_file_location=manifest_file_location
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="putServiceNow")
    def put_service_now(self, *, site_base_url: builtins.str) -> None:
        '''
        :param site_base_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#site_base_url QuicksightDataSource#site_base_url}.
        '''
        value = QuicksightDataSourceParametersServiceNow(site_base_url=site_base_url)

        return typing.cast(None, jsii.invoke(self, "putServiceNow", [value]))

    @jsii.member(jsii_name="putSnowflake")
    def put_snowflake(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        warehouse: builtins.str,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param warehouse: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#warehouse QuicksightDataSource#warehouse}.
        '''
        value = QuicksightDataSourceParametersSnowflake(
            database=database, host=host, warehouse=warehouse
        )

        return typing.cast(None, jsii.invoke(self, "putSnowflake", [value]))

    @jsii.member(jsii_name="putSpark")
    def put_spark(self, *, host: builtins.str, port: jsii.Number) -> None:
        '''
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersSpark(host=host, port=port)

        return typing.cast(None, jsii.invoke(self, "putSpark", [value]))

    @jsii.member(jsii_name="putSqlServer")
    def put_sql_server(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersSqlServer(
            database=database, host=host, port=port
        )

        return typing.cast(None, jsii.invoke(self, "putSqlServer", [value]))

    @jsii.member(jsii_name="putTeradata")
    def put_teradata(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        value = QuicksightDataSourceParametersTeradata(
            database=database, host=host, port=port
        )

        return typing.cast(None, jsii.invoke(self, "putTeradata", [value]))

    @jsii.member(jsii_name="putTwitter")
    def put_twitter(self, *, max_rows: jsii.Number, query: builtins.str) -> None:
        '''
        :param max_rows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#max_rows QuicksightDataSource#max_rows}.
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#query QuicksightDataSource#query}.
        '''
        value = QuicksightDataSourceParametersTwitter(max_rows=max_rows, query=query)

        return typing.cast(None, jsii.invoke(self, "putTwitter", [value]))

    @jsii.member(jsii_name="resetAmazonElasticsearch")
    def reset_amazon_elasticsearch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAmazonElasticsearch", []))

    @jsii.member(jsii_name="resetAthena")
    def reset_athena(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAthena", []))

    @jsii.member(jsii_name="resetAurora")
    def reset_aurora(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAurora", []))

    @jsii.member(jsii_name="resetAuroraPostgresql")
    def reset_aurora_postgresql(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuroraPostgresql", []))

    @jsii.member(jsii_name="resetAwsIotAnalytics")
    def reset_aws_iot_analytics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsIotAnalytics", []))

    @jsii.member(jsii_name="resetJira")
    def reset_jira(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJira", []))

    @jsii.member(jsii_name="resetMariaDb")
    def reset_maria_db(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMariaDb", []))

    @jsii.member(jsii_name="resetMysql")
    def reset_mysql(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMysql", []))

    @jsii.member(jsii_name="resetOracle")
    def reset_oracle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracle", []))

    @jsii.member(jsii_name="resetPostgresql")
    def reset_postgresql(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostgresql", []))

    @jsii.member(jsii_name="resetPresto")
    def reset_presto(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPresto", []))

    @jsii.member(jsii_name="resetRds")
    def reset_rds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRds", []))

    @jsii.member(jsii_name="resetRedshift")
    def reset_redshift(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedshift", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @jsii.member(jsii_name="resetServiceNow")
    def reset_service_now(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceNow", []))

    @jsii.member(jsii_name="resetSnowflake")
    def reset_snowflake(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnowflake", []))

    @jsii.member(jsii_name="resetSpark")
    def reset_spark(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpark", []))

    @jsii.member(jsii_name="resetSqlServer")
    def reset_sql_server(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlServer", []))

    @jsii.member(jsii_name="resetTeradata")
    def reset_teradata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeradata", []))

    @jsii.member(jsii_name="resetTwitter")
    def reset_twitter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTwitter", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amazonElasticsearch")
    def amazon_elasticsearch(
        self,
    ) -> QuicksightDataSourceParametersAmazonElasticsearchOutputReference:
        return typing.cast(QuicksightDataSourceParametersAmazonElasticsearchOutputReference, jsii.get(self, "amazonElasticsearch"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="athena")
    def athena(self) -> QuicksightDataSourceParametersAthenaOutputReference:
        return typing.cast(QuicksightDataSourceParametersAthenaOutputReference, jsii.get(self, "athena"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aurora")
    def aurora(self) -> QuicksightDataSourceParametersAuroraOutputReference:
        return typing.cast(QuicksightDataSourceParametersAuroraOutputReference, jsii.get(self, "aurora"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auroraPostgresql")
    def aurora_postgresql(
        self,
    ) -> QuicksightDataSourceParametersAuroraPostgresqlOutputReference:
        return typing.cast(QuicksightDataSourceParametersAuroraPostgresqlOutputReference, jsii.get(self, "auroraPostgresql"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsIotAnalytics")
    def aws_iot_analytics(
        self,
    ) -> QuicksightDataSourceParametersAwsIotAnalyticsOutputReference:
        return typing.cast(QuicksightDataSourceParametersAwsIotAnalyticsOutputReference, jsii.get(self, "awsIotAnalytics"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jira")
    def jira(self) -> QuicksightDataSourceParametersJiraOutputReference:
        return typing.cast(QuicksightDataSourceParametersJiraOutputReference, jsii.get(self, "jira"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mariaDb")
    def maria_db(self) -> QuicksightDataSourceParametersMariaDbOutputReference:
        return typing.cast(QuicksightDataSourceParametersMariaDbOutputReference, jsii.get(self, "mariaDb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mysql")
    def mysql(self) -> QuicksightDataSourceParametersMysqlOutputReference:
        return typing.cast(QuicksightDataSourceParametersMysqlOutputReference, jsii.get(self, "mysql"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oracle")
    def oracle(self) -> QuicksightDataSourceParametersOracleOutputReference:
        return typing.cast(QuicksightDataSourceParametersOracleOutputReference, jsii.get(self, "oracle"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postgresql")
    def postgresql(self) -> "QuicksightDataSourceParametersPostgresqlOutputReference":
        return typing.cast("QuicksightDataSourceParametersPostgresqlOutputReference", jsii.get(self, "postgresql"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="presto")
    def presto(self) -> "QuicksightDataSourceParametersPrestoOutputReference":
        return typing.cast("QuicksightDataSourceParametersPrestoOutputReference", jsii.get(self, "presto"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rds")
    def rds(self) -> "QuicksightDataSourceParametersRdsOutputReference":
        return typing.cast("QuicksightDataSourceParametersRdsOutputReference", jsii.get(self, "rds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redshift")
    def redshift(self) -> "QuicksightDataSourceParametersRedshiftOutputReference":
        return typing.cast("QuicksightDataSourceParametersRedshiftOutputReference", jsii.get(self, "redshift"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "QuicksightDataSourceParametersS3OutputReference":
        return typing.cast("QuicksightDataSourceParametersS3OutputReference", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceNow")
    def service_now(self) -> "QuicksightDataSourceParametersServiceNowOutputReference":
        return typing.cast("QuicksightDataSourceParametersServiceNowOutputReference", jsii.get(self, "serviceNow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snowflake")
    def snowflake(self) -> "QuicksightDataSourceParametersSnowflakeOutputReference":
        return typing.cast("QuicksightDataSourceParametersSnowflakeOutputReference", jsii.get(self, "snowflake"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spark")
    def spark(self) -> "QuicksightDataSourceParametersSparkOutputReference":
        return typing.cast("QuicksightDataSourceParametersSparkOutputReference", jsii.get(self, "spark"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqlServer")
    def sql_server(self) -> "QuicksightDataSourceParametersSqlServerOutputReference":
        return typing.cast("QuicksightDataSourceParametersSqlServerOutputReference", jsii.get(self, "sqlServer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teradata")
    def teradata(self) -> "QuicksightDataSourceParametersTeradataOutputReference":
        return typing.cast("QuicksightDataSourceParametersTeradataOutputReference", jsii.get(self, "teradata"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="twitter")
    def twitter(self) -> "QuicksightDataSourceParametersTwitterOutputReference":
        return typing.cast("QuicksightDataSourceParametersTwitterOutputReference", jsii.get(self, "twitter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amazonElasticsearchInput")
    def amazon_elasticsearch_input(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersAmazonElasticsearch]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersAmazonElasticsearch], jsii.get(self, "amazonElasticsearchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="athenaInput")
    def athena_input(self) -> typing.Optional[QuicksightDataSourceParametersAthena]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersAthena], jsii.get(self, "athenaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auroraInput")
    def aurora_input(self) -> typing.Optional[QuicksightDataSourceParametersAurora]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersAurora], jsii.get(self, "auroraInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auroraPostgresqlInput")
    def aurora_postgresql_input(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersAuroraPostgresql]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersAuroraPostgresql], jsii.get(self, "auroraPostgresqlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsIotAnalyticsInput")
    def aws_iot_analytics_input(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersAwsIotAnalytics]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersAwsIotAnalytics], jsii.get(self, "awsIotAnalyticsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jiraInput")
    def jira_input(self) -> typing.Optional[QuicksightDataSourceParametersJira]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersJira], jsii.get(self, "jiraInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mariaDbInput")
    def maria_db_input(self) -> typing.Optional[QuicksightDataSourceParametersMariaDb]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersMariaDb], jsii.get(self, "mariaDbInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mysqlInput")
    def mysql_input(self) -> typing.Optional[QuicksightDataSourceParametersMysql]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersMysql], jsii.get(self, "mysqlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oracleInput")
    def oracle_input(self) -> typing.Optional[QuicksightDataSourceParametersOracle]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersOracle], jsii.get(self, "oracleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postgresqlInput")
    def postgresql_input(
        self,
    ) -> typing.Optional["QuicksightDataSourceParametersPostgresql"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersPostgresql"], jsii.get(self, "postgresqlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prestoInput")
    def presto_input(self) -> typing.Optional["QuicksightDataSourceParametersPresto"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersPresto"], jsii.get(self, "prestoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rdsInput")
    def rds_input(self) -> typing.Optional["QuicksightDataSourceParametersRds"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersRds"], jsii.get(self, "rdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redshiftInput")
    def redshift_input(
        self,
    ) -> typing.Optional["QuicksightDataSourceParametersRedshift"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersRedshift"], jsii.get(self, "redshiftInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Input")
    def s3_input(self) -> typing.Optional["QuicksightDataSourceParametersS3"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersS3"], jsii.get(self, "s3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceNowInput")
    def service_now_input(
        self,
    ) -> typing.Optional["QuicksightDataSourceParametersServiceNow"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersServiceNow"], jsii.get(self, "serviceNowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snowflakeInput")
    def snowflake_input(
        self,
    ) -> typing.Optional["QuicksightDataSourceParametersSnowflake"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersSnowflake"], jsii.get(self, "snowflakeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sparkInput")
    def spark_input(self) -> typing.Optional["QuicksightDataSourceParametersSpark"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersSpark"], jsii.get(self, "sparkInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqlServerInput")
    def sql_server_input(
        self,
    ) -> typing.Optional["QuicksightDataSourceParametersSqlServer"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersSqlServer"], jsii.get(self, "sqlServerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="teradataInput")
    def teradata_input(
        self,
    ) -> typing.Optional["QuicksightDataSourceParametersTeradata"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersTeradata"], jsii.get(self, "teradataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="twitterInput")
    def twitter_input(self) -> typing.Optional["QuicksightDataSourceParametersTwitter"]:
        return typing.cast(typing.Optional["QuicksightDataSourceParametersTwitter"], jsii.get(self, "twitterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParameters]:
        return typing.cast(typing.Optional[QuicksightDataSourceParameters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParameters],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersPostgresql",
    jsii_struct_bases=[],
    name_mapping={"database": "database", "host": "host", "port": "port"},
)
class QuicksightDataSourceParametersPostgresql:
    def __init__(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersPostgresql.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "host": host,
            "port": port,
        }

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersPostgresql(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersPostgresqlOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersPostgresqlOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersPostgresqlOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersPostgresqlOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersPostgresqlOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersPostgresqlOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersPostgresql]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersPostgresql], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersPostgresql],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersPostgresqlOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersPresto",
    jsii_struct_bases=[],
    name_mapping={"catalog": "catalog", "host": "host", "port": "port"},
)
class QuicksightDataSourceParametersPresto:
    def __init__(
        self,
        *,
        catalog: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param catalog: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#catalog QuicksightDataSource#catalog}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersPresto.__init__)
            check_type(argname="argument catalog", value=catalog, expected_type=type_hints["catalog"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "catalog": catalog,
            "host": host,
            "port": port,
        }

    @builtins.property
    def catalog(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#catalog QuicksightDataSource#catalog}.'''
        result = self._values.get("catalog")
        assert result is not None, "Required property 'catalog' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersPresto(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersPrestoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersPrestoOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersPrestoOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="catalogInput")
    def catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="catalog")
    def catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalog"))

    @catalog.setter
    def catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersPrestoOutputReference, "catalog").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalog", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersPrestoOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersPrestoOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersPresto]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersPresto], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersPresto],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersPrestoOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersRds",
    jsii_struct_bases=[],
    name_mapping={"database": "database", "instance_id": "instanceId"},
)
class QuicksightDataSourceParametersRds:
    def __init__(self, *, database: builtins.str, instance_id: builtins.str) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#instance_id QuicksightDataSource#instance_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersRds.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument instance_id", value=instance_id, expected_type=type_hints["instance_id"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "instance_id": instance_id,
        }

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#instance_id QuicksightDataSource#instance_id}.'''
        result = self._values.get("instance_id")
        assert result is not None, "Required property 'instance_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersRds(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersRdsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersRdsOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersRdsOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdInput")
    def instance_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersRdsOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @instance_id.setter
    def instance_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersRdsOutputReference, "instance_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersRds]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersRds], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersRds],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersRdsOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersRedshift",
    jsii_struct_bases=[],
    name_mapping={
        "database": "database",
        "cluster_id": "clusterId",
        "host": "host",
        "port": "port",
    },
)
class QuicksightDataSourceParametersRedshift:
    def __init__(
        self,
        *,
        database: builtins.str,
        cluster_id: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#cluster_id QuicksightDataSource#cluster_id}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersRedshift.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
        }
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if host is not None:
            self._values["host"] = host
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#cluster_id QuicksightDataSource#cluster_id}.'''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersRedshift(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersRedshiftOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersRedshiftOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersRedshiftOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetClusterId")
    def reset_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterId", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersRedshiftOutputReference, "cluster_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersRedshiftOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersRedshiftOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersRedshiftOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersRedshift]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersRedshift], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersRedshift],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersRedshiftOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersS3",
    jsii_struct_bases=[],
    name_mapping={"manifest_file_location": "manifestFileLocation"},
)
class QuicksightDataSourceParametersS3:
    def __init__(
        self,
        *,
        manifest_file_location: typing.Union["QuicksightDataSourceParametersS3ManifestFileLocation", typing.Dict[str, typing.Any]],
    ) -> None:
        '''
        :param manifest_file_location: manifest_file_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#manifest_file_location QuicksightDataSource#manifest_file_location}
        '''
        if isinstance(manifest_file_location, dict):
            manifest_file_location = QuicksightDataSourceParametersS3ManifestFileLocation(**manifest_file_location)
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersS3.__init__)
            check_type(argname="argument manifest_file_location", value=manifest_file_location, expected_type=type_hints["manifest_file_location"])
        self._values: typing.Dict[str, typing.Any] = {
            "manifest_file_location": manifest_file_location,
        }

    @builtins.property
    def manifest_file_location(
        self,
    ) -> "QuicksightDataSourceParametersS3ManifestFileLocation":
        '''manifest_file_location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#manifest_file_location QuicksightDataSource#manifest_file_location}
        '''
        result = self._values.get("manifest_file_location")
        assert result is not None, "Required property 'manifest_file_location' is missing"
        return typing.cast("QuicksightDataSourceParametersS3ManifestFileLocation", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersS3ManifestFileLocation",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "key": "key"},
)
class QuicksightDataSourceParametersS3ManifestFileLocation:
    def __init__(self, *, bucket: builtins.str, key: builtins.str) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#bucket QuicksightDataSource#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#key QuicksightDataSource#key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersS3ManifestFileLocation.__init__)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "key": key,
        }

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#bucket QuicksightDataSource#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#key QuicksightDataSource#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersS3ManifestFileLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersS3ManifestFileLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersS3ManifestFileLocationOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersS3ManifestFileLocationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersS3ManifestFileLocationOutputReference, "bucket").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersS3ManifestFileLocationOutputReference, "key").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersS3ManifestFileLocation]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersS3ManifestFileLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersS3ManifestFileLocation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersS3ManifestFileLocationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class QuicksightDataSourceParametersS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersS3OutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersS3OutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putManifestFileLocation")
    def put_manifest_file_location(
        self,
        *,
        bucket: builtins.str,
        key: builtins.str,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#bucket QuicksightDataSource#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#key QuicksightDataSource#key}.
        '''
        value = QuicksightDataSourceParametersS3ManifestFileLocation(
            bucket=bucket, key=key
        )

        return typing.cast(None, jsii.invoke(self, "putManifestFileLocation", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manifestFileLocation")
    def manifest_file_location(
        self,
    ) -> QuicksightDataSourceParametersS3ManifestFileLocationOutputReference:
        return typing.cast(QuicksightDataSourceParametersS3ManifestFileLocationOutputReference, jsii.get(self, "manifestFileLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manifestFileLocationInput")
    def manifest_file_location_input(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersS3ManifestFileLocation]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersS3ManifestFileLocation], jsii.get(self, "manifestFileLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersS3]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersS3],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersS3OutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersServiceNow",
    jsii_struct_bases=[],
    name_mapping={"site_base_url": "siteBaseUrl"},
)
class QuicksightDataSourceParametersServiceNow:
    def __init__(self, *, site_base_url: builtins.str) -> None:
        '''
        :param site_base_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#site_base_url QuicksightDataSource#site_base_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersServiceNow.__init__)
            check_type(argname="argument site_base_url", value=site_base_url, expected_type=type_hints["site_base_url"])
        self._values: typing.Dict[str, typing.Any] = {
            "site_base_url": site_base_url,
        }

    @builtins.property
    def site_base_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#site_base_url QuicksightDataSource#site_base_url}.'''
        result = self._values.get("site_base_url")
        assert result is not None, "Required property 'site_base_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersServiceNow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersServiceNowOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersServiceNowOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersServiceNowOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="siteBaseUrlInput")
    def site_base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "siteBaseUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="siteBaseUrl")
    def site_base_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "siteBaseUrl"))

    @site_base_url.setter
    def site_base_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersServiceNowOutputReference, "site_base_url").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "siteBaseUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersServiceNow]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersServiceNow], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersServiceNow],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersServiceNowOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersSnowflake",
    jsii_struct_bases=[],
    name_mapping={"database": "database", "host": "host", "warehouse": "warehouse"},
)
class QuicksightDataSourceParametersSnowflake:
    def __init__(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        warehouse: builtins.str,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param warehouse: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#warehouse QuicksightDataSource#warehouse}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersSnowflake.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument warehouse", value=warehouse, expected_type=type_hints["warehouse"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "host": host,
            "warehouse": warehouse,
        }

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def warehouse(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#warehouse QuicksightDataSource#warehouse}.'''
        result = self._values.get("warehouse")
        assert result is not None, "Required property 'warehouse' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersSnowflake(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersSnowflakeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersSnowflakeOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersSnowflakeOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="warehouseInput")
    def warehouse_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warehouseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSnowflakeOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSnowflakeOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="warehouse")
    def warehouse(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "warehouse"))

    @warehouse.setter
    def warehouse(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSnowflakeOutputReference, "warehouse").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warehouse", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersSnowflake]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersSnowflake], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersSnowflake],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSnowflakeOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersSpark",
    jsii_struct_bases=[],
    name_mapping={"host": "host", "port": "port"},
)
class QuicksightDataSourceParametersSpark:
    def __init__(self, *, host: builtins.str, port: jsii.Number) -> None:
        '''
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersSpark.__init__)
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "host": host,
            "port": port,
        }

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersSpark(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersSparkOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersSparkOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersSparkOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSparkOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSparkOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersSpark]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersSpark], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersSpark],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSparkOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersSqlServer",
    jsii_struct_bases=[],
    name_mapping={"database": "database", "host": "host", "port": "port"},
)
class QuicksightDataSourceParametersSqlServer:
    def __init__(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersSqlServer.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "host": host,
            "port": port,
        }

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersSqlServer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersSqlServerOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersSqlServerOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersSqlServerOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSqlServerOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSqlServerOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSqlServerOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QuicksightDataSourceParametersSqlServer]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersSqlServer], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersSqlServer],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersSqlServerOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersTeradata",
    jsii_struct_bases=[],
    name_mapping={"database": "database", "host": "host", "port": "port"},
)
class QuicksightDataSourceParametersTeradata:
    def __init__(
        self,
        *,
        database: builtins.str,
        host: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.
        :param host: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersTeradata.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "host": host,
            "port": port,
        }

    @builtins.property
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#database QuicksightDataSource#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#host QuicksightDataSource#host}.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#port QuicksightDataSource#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersTeradata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersTeradataOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersTeradataOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersTeradataOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersTeradataOutputReference, "database").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersTeradataOutputReference, "host").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersTeradataOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersTeradata]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersTeradata], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersTeradata],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersTeradataOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersTwitter",
    jsii_struct_bases=[],
    name_mapping={"max_rows": "maxRows", "query": "query"},
)
class QuicksightDataSourceParametersTwitter:
    def __init__(self, *, max_rows: jsii.Number, query: builtins.str) -> None:
        '''
        :param max_rows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#max_rows QuicksightDataSource#max_rows}.
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#query QuicksightDataSource#query}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersTwitter.__init__)
            check_type(argname="argument max_rows", value=max_rows, expected_type=type_hints["max_rows"])
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
        self._values: typing.Dict[str, typing.Any] = {
            "max_rows": max_rows,
            "query": query,
        }

    @builtins.property
    def max_rows(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#max_rows QuicksightDataSource#max_rows}.'''
        result = self._values.get("max_rows")
        assert result is not None, "Required property 'max_rows' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#query QuicksightDataSource#query}.'''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceParametersTwitter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceParametersTwitterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceParametersTwitterOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceParametersTwitterOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRowsInput")
    def max_rows_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRowsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryInput")
    def query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRows")
    def max_rows(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxRows"))

    @max_rows.setter
    def max_rows(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersTwitterOutputReference, "max_rows").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRows", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="query")
    def query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "query"))

    @query.setter
    def query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersTwitterOutputReference, "query").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "query", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceParametersTwitter]:
        return typing.cast(typing.Optional[QuicksightDataSourceParametersTwitter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceParametersTwitter],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceParametersTwitterOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourcePermission",
    jsii_struct_bases=[],
    name_mapping={"actions": "actions", "principal": "principal"},
)
class QuicksightDataSourcePermission:
    def __init__(
        self,
        *,
        actions: typing.Sequence[builtins.str],
        principal: builtins.str,
    ) -> None:
        '''
        :param actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#actions QuicksightDataSource#actions}.
        :param principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#principal QuicksightDataSource#principal}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourcePermission.__init__)
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
        self._values: typing.Dict[str, typing.Any] = {
            "actions": actions,
            "principal": principal,
        }

    @builtins.property
    def actions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#actions QuicksightDataSource#actions}.'''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def principal(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#principal QuicksightDataSource#principal}.'''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourcePermission(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourcePermissionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourcePermissionList",
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
            type_hints = typing.get_type_hints(QuicksightDataSourcePermissionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "QuicksightDataSourcePermissionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourcePermissionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("QuicksightDataSourcePermissionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourcePermissionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourcePermissionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourcePermissionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[QuicksightDataSourcePermission]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[QuicksightDataSourcePermission]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[QuicksightDataSourcePermission]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourcePermissionList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class QuicksightDataSourcePermissionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourcePermissionOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourcePermissionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionsInput")
    def actions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "actionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principalInput")
    def principal_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "principalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "actions"))

    @actions.setter
    def actions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourcePermissionOutputReference, "actions").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principal")
    def principal(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "principal"))

    @principal.setter
    def principal(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourcePermissionOutputReference, "principal").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "principal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[QuicksightDataSourcePermission, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[QuicksightDataSourcePermission, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[QuicksightDataSourcePermission, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourcePermissionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceSslProperties",
    jsii_struct_bases=[],
    name_mapping={"disable_ssl": "disableSsl"},
)
class QuicksightDataSourceSslProperties:
    def __init__(
        self,
        *,
        disable_ssl: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param disable_ssl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#disable_ssl QuicksightDataSource#disable_ssl}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceSslProperties.__init__)
            check_type(argname="argument disable_ssl", value=disable_ssl, expected_type=type_hints["disable_ssl"])
        self._values: typing.Dict[str, typing.Any] = {
            "disable_ssl": disable_ssl,
        }

    @builtins.property
    def disable_ssl(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#disable_ssl QuicksightDataSource#disable_ssl}.'''
        result = self._values.get("disable_ssl")
        assert result is not None, "Required property 'disable_ssl' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceSslProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceSslPropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceSslPropertiesOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceSslPropertiesOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableSslInput")
    def disable_ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "disableSslInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableSsl")
    def disable_ssl(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "disableSsl"))

    @disable_ssl.setter
    def disable_ssl(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceSslPropertiesOutputReference, "disable_ssl").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableSsl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[QuicksightDataSourceSslProperties]:
        return typing.cast(typing.Optional[QuicksightDataSourceSslProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceSslProperties],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceSslPropertiesOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceVpcConnectionProperties",
    jsii_struct_bases=[],
    name_mapping={"vpc_connection_arn": "vpcConnectionArn"},
)
class QuicksightDataSourceVpcConnectionProperties:
    def __init__(self, *, vpc_connection_arn: builtins.str) -> None:
        '''
        :param vpc_connection_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#vpc_connection_arn QuicksightDataSource#vpc_connection_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightDataSourceVpcConnectionProperties.__init__)
            check_type(argname="argument vpc_connection_arn", value=vpc_connection_arn, expected_type=type_hints["vpc_connection_arn"])
        self._values: typing.Dict[str, typing.Any] = {
            "vpc_connection_arn": vpc_connection_arn,
        }

    @builtins.property
    def vpc_connection_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_data_source#vpc_connection_arn QuicksightDataSource#vpc_connection_arn}.'''
        result = self._values.get("vpc_connection_arn")
        assert result is not None, "Required property 'vpc_connection_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightDataSourceVpcConnectionProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightDataSourceVpcConnectionPropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightDataSourceVpcConnectionPropertiesOutputReference",
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
            type_hints = typing.get_type_hints(QuicksightDataSourceVpcConnectionPropertiesOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConnectionArnInput")
    def vpc_connection_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcConnectionArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConnectionArn")
    def vpc_connection_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcConnectionArn"))

    @vpc_connection_arn.setter
    def vpc_connection_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceVpcConnectionPropertiesOutputReference, "vpc_connection_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcConnectionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[QuicksightDataSourceVpcConnectionProperties]:
        return typing.cast(typing.Optional[QuicksightDataSourceVpcConnectionProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[QuicksightDataSourceVpcConnectionProperties],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightDataSourceVpcConnectionPropertiesOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class QuicksightGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group aws_quicksight_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        group_name: builtins.str,
        aws_account_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group aws_quicksight_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#group_name QuicksightGroup#group_name}.
        :param aws_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#aws_account_id QuicksightGroup#aws_account_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#description QuicksightGroup#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#id QuicksightGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#namespace QuicksightGroup#namespace}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightGroup.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = QuicksightGroupConfig(
            group_name=group_name,
            aws_account_id=aws_account_id,
            description=description,
            id=id,
            namespace=namespace,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetAwsAccountId")
    def reset_aws_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccountId", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

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
    @jsii.member(jsii_name="awsAccountIdInput")
    def aws_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupNameInput")
    def group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsAccountId")
    def aws_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccountId"))

    @aws_account_id.setter
    def aws_account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightGroup, "aws_account_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightGroup, "description").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupName"))

    @group_name.setter
    def group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightGroup, "group_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightGroup, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightGroup, "namespace").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightGroupConfig",
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
        "aws_account_id": "awsAccountId",
        "description": "description",
        "id": "id",
        "namespace": "namespace",
    },
)
class QuicksightGroupConfig(cdktf.TerraformMetaArguments):
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
        aws_account_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS QuickSight.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#group_name QuicksightGroup#group_name}.
        :param aws_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#aws_account_id QuicksightGroup#aws_account_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#description QuicksightGroup#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#id QuicksightGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#namespace QuicksightGroup#namespace}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightGroupConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument group_name", value=group_name, expected_type=type_hints["group_name"])
            check_type(argname="argument aws_account_id", value=aws_account_id, expected_type=type_hints["aws_account_id"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
        self._values: typing.Dict[str, typing.Any] = {
            "group_name": group_name,
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
        if aws_account_id is not None:
            self._values["aws_account_id"] = aws_account_id
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#group_name QuicksightGroup#group_name}.'''
        result = self._values.get("group_name")
        assert result is not None, "Required property 'group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#aws_account_id QuicksightGroup#aws_account_id}.'''
        result = self._values.get("aws_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#description QuicksightGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#id QuicksightGroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group#namespace QuicksightGroup#namespace}.'''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightGroupMembership(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightGroupMembership",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership aws_quicksight_group_membership}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        group_name: builtins.str,
        member_name: builtins.str,
        aws_account_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership aws_quicksight_group_membership} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#group_name QuicksightGroupMembership#group_name}.
        :param member_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#member_name QuicksightGroupMembership#member_name}.
        :param aws_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#aws_account_id QuicksightGroupMembership#aws_account_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#id QuicksightGroupMembership#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#namespace QuicksightGroupMembership#namespace}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightGroupMembership.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = QuicksightGroupMembershipConfig(
            group_name=group_name,
            member_name=member_name,
            aws_account_id=aws_account_id,
            id=id,
            namespace=namespace,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetAwsAccountId")
    def reset_aws_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccountId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

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
    @jsii.member(jsii_name="awsAccountIdInput")
    def aws_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupNameInput")
    def group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memberNameInput")
    def member_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "memberNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsAccountId")
    def aws_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccountId"))

    @aws_account_id.setter
    def aws_account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightGroupMembership, "aws_account_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupName"))

    @group_name.setter
    def group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightGroupMembership, "group_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightGroupMembership, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memberName")
    def member_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "memberName"))

    @member_name.setter
    def member_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightGroupMembership, "member_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memberName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightGroupMembership, "namespace").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightGroupMembershipConfig",
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
        "member_name": "memberName",
        "aws_account_id": "awsAccountId",
        "id": "id",
        "namespace": "namespace",
    },
)
class QuicksightGroupMembershipConfig(cdktf.TerraformMetaArguments):
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
        member_name: builtins.str,
        aws_account_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS QuickSight.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#group_name QuicksightGroupMembership#group_name}.
        :param member_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#member_name QuicksightGroupMembership#member_name}.
        :param aws_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#aws_account_id QuicksightGroupMembership#aws_account_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#id QuicksightGroupMembership#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#namespace QuicksightGroupMembership#namespace}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightGroupMembershipConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument group_name", value=group_name, expected_type=type_hints["group_name"])
            check_type(argname="argument member_name", value=member_name, expected_type=type_hints["member_name"])
            check_type(argname="argument aws_account_id", value=aws_account_id, expected_type=type_hints["aws_account_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
        self._values: typing.Dict[str, typing.Any] = {
            "group_name": group_name,
            "member_name": member_name,
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
        if aws_account_id is not None:
            self._values["aws_account_id"] = aws_account_id
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#group_name QuicksightGroupMembership#group_name}.'''
        result = self._values.get("group_name")
        assert result is not None, "Required property 'group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def member_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#member_name QuicksightGroupMembership#member_name}.'''
        result = self._values.get("member_name")
        assert result is not None, "Required property 'member_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#aws_account_id QuicksightGroupMembership#aws_account_id}.'''
        result = self._values.get("aws_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#id QuicksightGroupMembership#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_group_membership#namespace QuicksightGroupMembership#namespace}.'''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightGroupMembershipConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class QuicksightUser(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user aws_quicksight_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        email: builtins.str,
        identity_type: builtins.str,
        user_role: builtins.str,
        aws_account_id: typing.Optional[builtins.str] = None,
        iam_arn: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        session_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user aws_quicksight_user} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#email QuicksightUser#email}.
        :param identity_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#identity_type QuicksightUser#identity_type}.
        :param user_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#user_role QuicksightUser#user_role}.
        :param aws_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#aws_account_id QuicksightUser#aws_account_id}.
        :param iam_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#iam_arn QuicksightUser#iam_arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#id QuicksightUser#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#namespace QuicksightUser#namespace}.
        :param session_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#session_name QuicksightUser#session_name}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#user_name QuicksightUser#user_name}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightUser.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = QuicksightUserConfig(
            email=email,
            identity_type=identity_type,
            user_role=user_role,
            aws_account_id=aws_account_id,
            iam_arn=iam_arn,
            id=id,
            namespace=namespace,
            session_name=session_name,
            user_name=user_name,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetAwsAccountId")
    def reset_aws_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccountId", []))

    @jsii.member(jsii_name="resetIamArn")
    def reset_iam_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamArn", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetSessionName")
    def reset_session_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionName", []))

    @jsii.member(jsii_name="resetUserName")
    def reset_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserName", []))

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
    @jsii.member(jsii_name="awsAccountIdInput")
    def aws_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamArnInput")
    def iam_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityTypeInput")
    def identity_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionNameInput")
    def session_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userRoleInput")
    def user_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsAccountId")
    def aws_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccountId"))

    @aws_account_id.setter
    def aws_account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightUser, "aws_account_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightUser, "email").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamArn")
    def iam_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamArn"))

    @iam_arn.setter
    def iam_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightUser, "iam_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightUser, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityType")
    def identity_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityType"))

    @identity_type.setter
    def identity_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightUser, "identity_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightUser, "namespace").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionName")
    def session_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionName"))

    @session_name.setter
    def session_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightUser, "session_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightUser, "user_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userRole")
    def user_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userRole"))

    @user_role.setter
    def user_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(QuicksightUser, "user_role").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userRole", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.quicksight.QuicksightUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "email": "email",
        "identity_type": "identityType",
        "user_role": "userRole",
        "aws_account_id": "awsAccountId",
        "iam_arn": "iamArn",
        "id": "id",
        "namespace": "namespace",
        "session_name": "sessionName",
        "user_name": "userName",
    },
)
class QuicksightUserConfig(cdktf.TerraformMetaArguments):
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
        email: builtins.str,
        identity_type: builtins.str,
        user_role: builtins.str,
        aws_account_id: typing.Optional[builtins.str] = None,
        iam_arn: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        session_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS QuickSight.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#email QuicksightUser#email}.
        :param identity_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#identity_type QuicksightUser#identity_type}.
        :param user_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#user_role QuicksightUser#user_role}.
        :param aws_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#aws_account_id QuicksightUser#aws_account_id}.
        :param iam_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#iam_arn QuicksightUser#iam_arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#id QuicksightUser#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#namespace QuicksightUser#namespace}.
        :param session_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#session_name QuicksightUser#session_name}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#user_name QuicksightUser#user_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(QuicksightUserConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument identity_type", value=identity_type, expected_type=type_hints["identity_type"])
            check_type(argname="argument user_role", value=user_role, expected_type=type_hints["user_role"])
            check_type(argname="argument aws_account_id", value=aws_account_id, expected_type=type_hints["aws_account_id"])
            check_type(argname="argument iam_arn", value=iam_arn, expected_type=type_hints["iam_arn"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument session_name", value=session_name, expected_type=type_hints["session_name"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
            "identity_type": identity_type,
            "user_role": user_role,
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
        if aws_account_id is not None:
            self._values["aws_account_id"] = aws_account_id
        if iam_arn is not None:
            self._values["iam_arn"] = iam_arn
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
        if session_name is not None:
            self._values["session_name"] = session_name
        if user_name is not None:
            self._values["user_name"] = user_name

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
    def email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#email QuicksightUser#email}.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#identity_type QuicksightUser#identity_type}.'''
        result = self._values.get("identity_type")
        assert result is not None, "Required property 'identity_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#user_role QuicksightUser#user_role}.'''
        result = self._values.get("user_role")
        assert result is not None, "Required property 'user_role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#aws_account_id QuicksightUser#aws_account_id}.'''
        result = self._values.get("aws_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#iam_arn QuicksightUser#iam_arn}.'''
        result = self._values.get("iam_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#id QuicksightUser#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#namespace QuicksightUser#namespace}.'''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#session_name QuicksightUser#session_name}.'''
        result = self._values.get("session_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/quicksight_user#user_name QuicksightUser#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuicksightUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "QuicksightDataSource",
    "QuicksightDataSourceConfig",
    "QuicksightDataSourceCredentials",
    "QuicksightDataSourceCredentialsCredentialPair",
    "QuicksightDataSourceCredentialsCredentialPairOutputReference",
    "QuicksightDataSourceCredentialsOutputReference",
    "QuicksightDataSourceParameters",
    "QuicksightDataSourceParametersAmazonElasticsearch",
    "QuicksightDataSourceParametersAmazonElasticsearchOutputReference",
    "QuicksightDataSourceParametersAthena",
    "QuicksightDataSourceParametersAthenaOutputReference",
    "QuicksightDataSourceParametersAurora",
    "QuicksightDataSourceParametersAuroraOutputReference",
    "QuicksightDataSourceParametersAuroraPostgresql",
    "QuicksightDataSourceParametersAuroraPostgresqlOutputReference",
    "QuicksightDataSourceParametersAwsIotAnalytics",
    "QuicksightDataSourceParametersAwsIotAnalyticsOutputReference",
    "QuicksightDataSourceParametersJira",
    "QuicksightDataSourceParametersJiraOutputReference",
    "QuicksightDataSourceParametersMariaDb",
    "QuicksightDataSourceParametersMariaDbOutputReference",
    "QuicksightDataSourceParametersMysql",
    "QuicksightDataSourceParametersMysqlOutputReference",
    "QuicksightDataSourceParametersOracle",
    "QuicksightDataSourceParametersOracleOutputReference",
    "QuicksightDataSourceParametersOutputReference",
    "QuicksightDataSourceParametersPostgresql",
    "QuicksightDataSourceParametersPostgresqlOutputReference",
    "QuicksightDataSourceParametersPresto",
    "QuicksightDataSourceParametersPrestoOutputReference",
    "QuicksightDataSourceParametersRds",
    "QuicksightDataSourceParametersRdsOutputReference",
    "QuicksightDataSourceParametersRedshift",
    "QuicksightDataSourceParametersRedshiftOutputReference",
    "QuicksightDataSourceParametersS3",
    "QuicksightDataSourceParametersS3ManifestFileLocation",
    "QuicksightDataSourceParametersS3ManifestFileLocationOutputReference",
    "QuicksightDataSourceParametersS3OutputReference",
    "QuicksightDataSourceParametersServiceNow",
    "QuicksightDataSourceParametersServiceNowOutputReference",
    "QuicksightDataSourceParametersSnowflake",
    "QuicksightDataSourceParametersSnowflakeOutputReference",
    "QuicksightDataSourceParametersSpark",
    "QuicksightDataSourceParametersSparkOutputReference",
    "QuicksightDataSourceParametersSqlServer",
    "QuicksightDataSourceParametersSqlServerOutputReference",
    "QuicksightDataSourceParametersTeradata",
    "QuicksightDataSourceParametersTeradataOutputReference",
    "QuicksightDataSourceParametersTwitter",
    "QuicksightDataSourceParametersTwitterOutputReference",
    "QuicksightDataSourcePermission",
    "QuicksightDataSourcePermissionList",
    "QuicksightDataSourcePermissionOutputReference",
    "QuicksightDataSourceSslProperties",
    "QuicksightDataSourceSslPropertiesOutputReference",
    "QuicksightDataSourceVpcConnectionProperties",
    "QuicksightDataSourceVpcConnectionPropertiesOutputReference",
    "QuicksightGroup",
    "QuicksightGroupConfig",
    "QuicksightGroupMembership",
    "QuicksightGroupMembershipConfig",
    "QuicksightUser",
    "QuicksightUserConfig",
]

publication.publish()
