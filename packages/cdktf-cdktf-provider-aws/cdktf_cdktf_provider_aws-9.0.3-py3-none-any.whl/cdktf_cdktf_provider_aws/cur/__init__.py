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


class CurReportDefinition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cur.CurReportDefinition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition aws_cur_report_definition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        additional_schema_elements: typing.Sequence[builtins.str],
        compression: builtins.str,
        format: builtins.str,
        report_name: builtins.str,
        s3_bucket: builtins.str,
        s3_region: builtins.str,
        time_unit: builtins.str,
        additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        report_versioning: typing.Optional[builtins.str] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition aws_cur_report_definition} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param additional_schema_elements: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#additional_schema_elements CurReportDefinition#additional_schema_elements}.
        :param compression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#compression CurReportDefinition#compression}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#format CurReportDefinition#format}.
        :param report_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#report_name CurReportDefinition#report_name}.
        :param s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#s3_bucket CurReportDefinition#s3_bucket}.
        :param s3_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#s3_region CurReportDefinition#s3_region}.
        :param time_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#time_unit CurReportDefinition#time_unit}.
        :param additional_artifacts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#additional_artifacts CurReportDefinition#additional_artifacts}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#id CurReportDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param refresh_closed_reports: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#refresh_closed_reports CurReportDefinition#refresh_closed_reports}.
        :param report_versioning: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#report_versioning CurReportDefinition#report_versioning}.
        :param s3_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#s3_prefix CurReportDefinition#s3_prefix}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CurReportDefinition.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CurReportDefinitionConfig(
            additional_schema_elements=additional_schema_elements,
            compression=compression,
            format=format,
            report_name=report_name,
            s3_bucket=s3_bucket,
            s3_region=s3_region,
            time_unit=time_unit,
            additional_artifacts=additional_artifacts,
            id=id,
            refresh_closed_reports=refresh_closed_reports,
            report_versioning=report_versioning,
            s3_prefix=s3_prefix,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetAdditionalArtifacts")
    def reset_additional_artifacts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalArtifacts", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRefreshClosedReports")
    def reset_refresh_closed_reports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefreshClosedReports", []))

    @jsii.member(jsii_name="resetReportVersioning")
    def reset_report_versioning(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReportVersioning", []))

    @jsii.member(jsii_name="resetS3Prefix")
    def reset_s3_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Prefix", []))

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
    @jsii.member(jsii_name="additionalArtifactsInput")
    def additional_artifacts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "additionalArtifactsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalSchemaElementsInput")
    def additional_schema_elements_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "additionalSchemaElementsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compressionInput")
    def compression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "compressionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshClosedReportsInput")
    def refresh_closed_reports_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "refreshClosedReportsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportNameInput")
    def report_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportVersioningInput")
    def report_versioning_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportVersioningInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketInput")
    def s3_bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3BucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3PrefixInput")
    def s3_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3PrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3RegionInput")
    def s3_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3RegionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeUnitInput")
    def time_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalArtifacts")
    def additional_artifacts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "additionalArtifacts"))

    @additional_artifacts.setter
    def additional_artifacts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "additional_artifacts").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "additionalArtifacts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalSchemaElements")
    def additional_schema_elements(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "additionalSchemaElements"))

    @additional_schema_elements.setter
    def additional_schema_elements(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "additional_schema_elements").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "additionalSchemaElements", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compression")
    def compression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compression"))

    @compression.setter
    def compression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "compression").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "compression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "format").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "format", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshClosedReports")
    def refresh_closed_reports(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "refreshClosedReports"))

    @refresh_closed_reports.setter
    def refresh_closed_reports(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "refresh_closed_reports").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "refreshClosedReports", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportName")
    def report_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportName"))

    @report_name.setter
    def report_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "report_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportVersioning")
    def report_versioning(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportVersioning"))

    @report_versioning.setter
    def report_versioning(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "report_versioning").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportVersioning", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Bucket"))

    @s3_bucket.setter
    def s3_bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "s3_bucket").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3Bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Prefix")
    def s3_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Prefix"))

    @s3_prefix.setter
    def s3_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "s3_prefix").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3Prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Region")
    def s3_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Region"))

    @s3_region.setter
    def s3_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "s3_region").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3Region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeUnit")
    def time_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeUnit"))

    @time_unit.setter
    def time_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CurReportDefinition, "time_unit").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeUnit", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cur.CurReportDefinitionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "additional_schema_elements": "additionalSchemaElements",
        "compression": "compression",
        "format": "format",
        "report_name": "reportName",
        "s3_bucket": "s3Bucket",
        "s3_region": "s3Region",
        "time_unit": "timeUnit",
        "additional_artifacts": "additionalArtifacts",
        "id": "id",
        "refresh_closed_reports": "refreshClosedReports",
        "report_versioning": "reportVersioning",
        "s3_prefix": "s3Prefix",
    },
)
class CurReportDefinitionConfig(cdktf.TerraformMetaArguments):
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
        additional_schema_elements: typing.Sequence[builtins.str],
        compression: builtins.str,
        format: builtins.str,
        report_name: builtins.str,
        s3_bucket: builtins.str,
        s3_region: builtins.str,
        time_unit: builtins.str,
        additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        refresh_closed_reports: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        report_versioning: typing.Optional[builtins.str] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cost and Usage Report.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param additional_schema_elements: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#additional_schema_elements CurReportDefinition#additional_schema_elements}.
        :param compression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#compression CurReportDefinition#compression}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#format CurReportDefinition#format}.
        :param report_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#report_name CurReportDefinition#report_name}.
        :param s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#s3_bucket CurReportDefinition#s3_bucket}.
        :param s3_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#s3_region CurReportDefinition#s3_region}.
        :param time_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#time_unit CurReportDefinition#time_unit}.
        :param additional_artifacts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#additional_artifacts CurReportDefinition#additional_artifacts}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#id CurReportDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param refresh_closed_reports: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#refresh_closed_reports CurReportDefinition#refresh_closed_reports}.
        :param report_versioning: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#report_versioning CurReportDefinition#report_versioning}.
        :param s3_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#s3_prefix CurReportDefinition#s3_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(CurReportDefinitionConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument additional_schema_elements", value=additional_schema_elements, expected_type=type_hints["additional_schema_elements"])
            check_type(argname="argument compression", value=compression, expected_type=type_hints["compression"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument report_name", value=report_name, expected_type=type_hints["report_name"])
            check_type(argname="argument s3_bucket", value=s3_bucket, expected_type=type_hints["s3_bucket"])
            check_type(argname="argument s3_region", value=s3_region, expected_type=type_hints["s3_region"])
            check_type(argname="argument time_unit", value=time_unit, expected_type=type_hints["time_unit"])
            check_type(argname="argument additional_artifacts", value=additional_artifacts, expected_type=type_hints["additional_artifacts"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument refresh_closed_reports", value=refresh_closed_reports, expected_type=type_hints["refresh_closed_reports"])
            check_type(argname="argument report_versioning", value=report_versioning, expected_type=type_hints["report_versioning"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
        self._values: typing.Dict[str, typing.Any] = {
            "additional_schema_elements": additional_schema_elements,
            "compression": compression,
            "format": format,
            "report_name": report_name,
            "s3_bucket": s3_bucket,
            "s3_region": s3_region,
            "time_unit": time_unit,
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
        if additional_artifacts is not None:
            self._values["additional_artifacts"] = additional_artifacts
        if id is not None:
            self._values["id"] = id
        if refresh_closed_reports is not None:
            self._values["refresh_closed_reports"] = refresh_closed_reports
        if report_versioning is not None:
            self._values["report_versioning"] = report_versioning
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix

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
    def additional_schema_elements(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#additional_schema_elements CurReportDefinition#additional_schema_elements}.'''
        result = self._values.get("additional_schema_elements")
        assert result is not None, "Required property 'additional_schema_elements' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def compression(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#compression CurReportDefinition#compression}.'''
        result = self._values.get("compression")
        assert result is not None, "Required property 'compression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def format(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#format CurReportDefinition#format}.'''
        result = self._values.get("format")
        assert result is not None, "Required property 'format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def report_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#report_name CurReportDefinition#report_name}.'''
        result = self._values.get("report_name")
        assert result is not None, "Required property 'report_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#s3_bucket CurReportDefinition#s3_bucket}.'''
        result = self._values.get("s3_bucket")
        assert result is not None, "Required property 's3_bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#s3_region CurReportDefinition#s3_region}.'''
        result = self._values.get("s3_region")
        assert result is not None, "Required property 's3_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def time_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#time_unit CurReportDefinition#time_unit}.'''
        result = self._values.get("time_unit")
        assert result is not None, "Required property 'time_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_artifacts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#additional_artifacts CurReportDefinition#additional_artifacts}.'''
        result = self._values.get("additional_artifacts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#id CurReportDefinition#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def refresh_closed_reports(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#refresh_closed_reports CurReportDefinition#refresh_closed_reports}.'''
        result = self._values.get("refresh_closed_reports")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def report_versioning(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#report_versioning CurReportDefinition#report_versioning}.'''
        result = self._values.get("report_versioning")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cur_report_definition#s3_prefix CurReportDefinition#s3_prefix}.'''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CurReportDefinitionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCurReportDefinition(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cur.DataAwsCurReportDefinition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cur_report_definition aws_cur_report_definition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        report_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cur_report_definition aws_cur_report_definition} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param report_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cur_report_definition#report_name DataAwsCurReportDefinition#report_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cur_report_definition#id DataAwsCurReportDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCurReportDefinition.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsCurReportDefinitionConfig(
            report_name=report_name,
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
    @jsii.member(jsii_name="additionalArtifacts")
    def additional_artifacts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "additionalArtifacts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalSchemaElements")
    def additional_schema_elements(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "additionalSchemaElements"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compression")
    def compression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compression"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshClosedReports")
    def refresh_closed_reports(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "refreshClosedReports"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportVersioning")
    def report_versioning(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportVersioning"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Prefix")
    def s3_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Prefix"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Region")
    def s3_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeUnit")
    def time_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeUnit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportNameInput")
    def report_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCurReportDefinition, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportName")
    def report_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportName"))

    @report_name.setter
    def report_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsCurReportDefinition, "report_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cur.DataAwsCurReportDefinitionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "report_name": "reportName",
        "id": "id",
    },
)
class DataAwsCurReportDefinitionConfig(cdktf.TerraformMetaArguments):
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
        report_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cost and Usage Report.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param report_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cur_report_definition#report_name DataAwsCurReportDefinition#report_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cur_report_definition#id DataAwsCurReportDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsCurReportDefinitionConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument report_name", value=report_name, expected_type=type_hints["report_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "report_name": report_name,
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
    def report_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cur_report_definition#report_name DataAwsCurReportDefinition#report_name}.'''
        result = self._values.get("report_name")
        assert result is not None, "Required property 'report_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cur_report_definition#id DataAwsCurReportDefinition#id}.

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
        return "DataAwsCurReportDefinitionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CurReportDefinition",
    "CurReportDefinitionConfig",
    "DataAwsCurReportDefinition",
    "DataAwsCurReportDefinitionConfig",
]

publication.publish()
