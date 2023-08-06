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


class BatchComputeEnvironment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment aws_batch_compute_environment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        type: builtins.str,
        compute_environment_name: typing.Optional[builtins.str] = None,
        compute_environment_name_prefix: typing.Optional[builtins.str] = None,
        compute_resources: typing.Optional[typing.Union["BatchComputeEnvironmentComputeResources", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        service_role: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment aws_batch_compute_environment} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.
        :param compute_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name BatchComputeEnvironment#compute_environment_name}.
        :param compute_environment_name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name_prefix BatchComputeEnvironment#compute_environment_name_prefix}.
        :param compute_resources: compute_resources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_resources BatchComputeEnvironment#compute_resources}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#id BatchComputeEnvironment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param service_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#service_role BatchComputeEnvironment#service_role}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#state BatchComputeEnvironment#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags_all BatchComputeEnvironment#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchComputeEnvironment.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = BatchComputeEnvironmentConfig(
            type=type,
            compute_environment_name=compute_environment_name,
            compute_environment_name_prefix=compute_environment_name_prefix,
            compute_resources=compute_resources,
            id=id,
            service_role=service_role,
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

    @jsii.member(jsii_name="putComputeResources")
    def put_compute_resources(
        self,
        *,
        max_vcpus: jsii.Number,
        security_group_ids: typing.Sequence[builtins.str],
        subnets: typing.Sequence[builtins.str],
        type: builtins.str,
        allocation_strategy: typing.Optional[builtins.str] = None,
        bid_percentage: typing.Optional[jsii.Number] = None,
        desired_vcpus: typing.Optional[jsii.Number] = None,
        ec2_configuration: typing.Optional[typing.Union["BatchComputeEnvironmentComputeResourcesEc2Configuration", typing.Dict[str, typing.Any]]] = None,
        ec2_key_pair: typing.Optional[builtins.str] = None,
        image_id: typing.Optional[builtins.str] = None,
        instance_role: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[typing.Sequence[builtins.str]] = None,
        launch_template: typing.Optional[typing.Union["BatchComputeEnvironmentComputeResourcesLaunchTemplate", typing.Dict[str, typing.Any]]] = None,
        min_vcpus: typing.Optional[jsii.Number] = None,
        spot_iam_fleet_role: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param max_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#max_vcpus BatchComputeEnvironment#max_vcpus}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#security_group_ids BatchComputeEnvironment#security_group_ids}.
        :param subnets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#subnets BatchComputeEnvironment#subnets}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.
        :param allocation_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#allocation_strategy BatchComputeEnvironment#allocation_strategy}.
        :param bid_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#bid_percentage BatchComputeEnvironment#bid_percentage}.
        :param desired_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#desired_vcpus BatchComputeEnvironment#desired_vcpus}.
        :param ec2_configuration: ec2_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_configuration BatchComputeEnvironment#ec2_configuration}
        :param ec2_key_pair: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_key_pair BatchComputeEnvironment#ec2_key_pair}.
        :param image_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id BatchComputeEnvironment#image_id}.
        :param instance_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_role BatchComputeEnvironment#instance_role}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_type BatchComputeEnvironment#instance_type}.
        :param launch_template: launch_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template BatchComputeEnvironment#launch_template}
        :param min_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#min_vcpus BatchComputeEnvironment#min_vcpus}.
        :param spot_iam_fleet_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#spot_iam_fleet_role BatchComputeEnvironment#spot_iam_fleet_role}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.
        '''
        value = BatchComputeEnvironmentComputeResources(
            max_vcpus=max_vcpus,
            security_group_ids=security_group_ids,
            subnets=subnets,
            type=type,
            allocation_strategy=allocation_strategy,
            bid_percentage=bid_percentage,
            desired_vcpus=desired_vcpus,
            ec2_configuration=ec2_configuration,
            ec2_key_pair=ec2_key_pair,
            image_id=image_id,
            instance_role=instance_role,
            instance_type=instance_type,
            launch_template=launch_template,
            min_vcpus=min_vcpus,
            spot_iam_fleet_role=spot_iam_fleet_role,
            tags=tags,
        )

        return typing.cast(None, jsii.invoke(self, "putComputeResources", [value]))

    @jsii.member(jsii_name="resetComputeEnvironmentName")
    def reset_compute_environment_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputeEnvironmentName", []))

    @jsii.member(jsii_name="resetComputeEnvironmentNamePrefix")
    def reset_compute_environment_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputeEnvironmentNamePrefix", []))

    @jsii.member(jsii_name="resetComputeResources")
    def reset_compute_resources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputeResources", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetServiceRole")
    def reset_service_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceRole", []))

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
    @jsii.member(jsii_name="computeResources")
    def compute_resources(
        self,
    ) -> "BatchComputeEnvironmentComputeResourcesOutputReference":
        return typing.cast("BatchComputeEnvironmentComputeResourcesOutputReference", jsii.get(self, "computeResources"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecsClusterArn")
    def ecs_cluster_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ecsClusterArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusReason")
    def status_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentNameInput")
    def compute_environment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computeEnvironmentNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentNamePrefixInput")
    def compute_environment_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computeEnvironmentNamePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeResourcesInput")
    def compute_resources_input(
        self,
    ) -> typing.Optional["BatchComputeEnvironmentComputeResources"]:
        return typing.cast(typing.Optional["BatchComputeEnvironmentComputeResources"], jsii.get(self, "computeResourcesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleInput")
    def service_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceRoleInput"))

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
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentName"))

    @compute_environment_name.setter
    def compute_environment_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironment, "compute_environment_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "computeEnvironmentName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentNamePrefix")
    def compute_environment_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentNamePrefix"))

    @compute_environment_name_prefix.setter
    def compute_environment_name_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironment, "compute_environment_name_prefix").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "computeEnvironmentNamePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironment, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @service_role.setter
    def service_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironment, "service_role").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironment, "state").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironment, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironment, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironment, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResources",
    jsii_struct_bases=[],
    name_mapping={
        "max_vcpus": "maxVcpus",
        "security_group_ids": "securityGroupIds",
        "subnets": "subnets",
        "type": "type",
        "allocation_strategy": "allocationStrategy",
        "bid_percentage": "bidPercentage",
        "desired_vcpus": "desiredVcpus",
        "ec2_configuration": "ec2Configuration",
        "ec2_key_pair": "ec2KeyPair",
        "image_id": "imageId",
        "instance_role": "instanceRole",
        "instance_type": "instanceType",
        "launch_template": "launchTemplate",
        "min_vcpus": "minVcpus",
        "spot_iam_fleet_role": "spotIamFleetRole",
        "tags": "tags",
    },
)
class BatchComputeEnvironmentComputeResources:
    def __init__(
        self,
        *,
        max_vcpus: jsii.Number,
        security_group_ids: typing.Sequence[builtins.str],
        subnets: typing.Sequence[builtins.str],
        type: builtins.str,
        allocation_strategy: typing.Optional[builtins.str] = None,
        bid_percentage: typing.Optional[jsii.Number] = None,
        desired_vcpus: typing.Optional[jsii.Number] = None,
        ec2_configuration: typing.Optional[typing.Union["BatchComputeEnvironmentComputeResourcesEc2Configuration", typing.Dict[str, typing.Any]]] = None,
        ec2_key_pair: typing.Optional[builtins.str] = None,
        image_id: typing.Optional[builtins.str] = None,
        instance_role: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[typing.Sequence[builtins.str]] = None,
        launch_template: typing.Optional[typing.Union["BatchComputeEnvironmentComputeResourcesLaunchTemplate", typing.Dict[str, typing.Any]]] = None,
        min_vcpus: typing.Optional[jsii.Number] = None,
        spot_iam_fleet_role: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param max_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#max_vcpus BatchComputeEnvironment#max_vcpus}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#security_group_ids BatchComputeEnvironment#security_group_ids}.
        :param subnets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#subnets BatchComputeEnvironment#subnets}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.
        :param allocation_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#allocation_strategy BatchComputeEnvironment#allocation_strategy}.
        :param bid_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#bid_percentage BatchComputeEnvironment#bid_percentage}.
        :param desired_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#desired_vcpus BatchComputeEnvironment#desired_vcpus}.
        :param ec2_configuration: ec2_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_configuration BatchComputeEnvironment#ec2_configuration}
        :param ec2_key_pair: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_key_pair BatchComputeEnvironment#ec2_key_pair}.
        :param image_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id BatchComputeEnvironment#image_id}.
        :param instance_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_role BatchComputeEnvironment#instance_role}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_type BatchComputeEnvironment#instance_type}.
        :param launch_template: launch_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template BatchComputeEnvironment#launch_template}
        :param min_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#min_vcpus BatchComputeEnvironment#min_vcpus}.
        :param spot_iam_fleet_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#spot_iam_fleet_role BatchComputeEnvironment#spot_iam_fleet_role}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.
        '''
        if isinstance(ec2_configuration, dict):
            ec2_configuration = BatchComputeEnvironmentComputeResourcesEc2Configuration(**ec2_configuration)
        if isinstance(launch_template, dict):
            launch_template = BatchComputeEnvironmentComputeResourcesLaunchTemplate(**launch_template)
        if __debug__:
            type_hints = typing.get_type_hints(BatchComputeEnvironmentComputeResources.__init__)
            check_type(argname="argument max_vcpus", value=max_vcpus, expected_type=type_hints["max_vcpus"])
            check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument allocation_strategy", value=allocation_strategy, expected_type=type_hints["allocation_strategy"])
            check_type(argname="argument bid_percentage", value=bid_percentage, expected_type=type_hints["bid_percentage"])
            check_type(argname="argument desired_vcpus", value=desired_vcpus, expected_type=type_hints["desired_vcpus"])
            check_type(argname="argument ec2_configuration", value=ec2_configuration, expected_type=type_hints["ec2_configuration"])
            check_type(argname="argument ec2_key_pair", value=ec2_key_pair, expected_type=type_hints["ec2_key_pair"])
            check_type(argname="argument image_id", value=image_id, expected_type=type_hints["image_id"])
            check_type(argname="argument instance_role", value=instance_role, expected_type=type_hints["instance_role"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument launch_template", value=launch_template, expected_type=type_hints["launch_template"])
            check_type(argname="argument min_vcpus", value=min_vcpus, expected_type=type_hints["min_vcpus"])
            check_type(argname="argument spot_iam_fleet_role", value=spot_iam_fleet_role, expected_type=type_hints["spot_iam_fleet_role"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[str, typing.Any] = {
            "max_vcpus": max_vcpus,
            "security_group_ids": security_group_ids,
            "subnets": subnets,
            "type": type,
        }
        if allocation_strategy is not None:
            self._values["allocation_strategy"] = allocation_strategy
        if bid_percentage is not None:
            self._values["bid_percentage"] = bid_percentage
        if desired_vcpus is not None:
            self._values["desired_vcpus"] = desired_vcpus
        if ec2_configuration is not None:
            self._values["ec2_configuration"] = ec2_configuration
        if ec2_key_pair is not None:
            self._values["ec2_key_pair"] = ec2_key_pair
        if image_id is not None:
            self._values["image_id"] = image_id
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if launch_template is not None:
            self._values["launch_template"] = launch_template
        if min_vcpus is not None:
            self._values["min_vcpus"] = min_vcpus
        if spot_iam_fleet_role is not None:
            self._values["spot_iam_fleet_role"] = spot_iam_fleet_role
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def max_vcpus(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#max_vcpus BatchComputeEnvironment#max_vcpus}.'''
        result = self._values.get("max_vcpus")
        assert result is not None, "Required property 'max_vcpus' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def security_group_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#security_group_ids BatchComputeEnvironment#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        assert result is not None, "Required property 'security_group_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subnets(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#subnets BatchComputeEnvironment#subnets}.'''
        result = self._values.get("subnets")
        assert result is not None, "Required property 'subnets' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allocation_strategy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#allocation_strategy BatchComputeEnvironment#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bid_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#bid_percentage BatchComputeEnvironment#bid_percentage}.'''
        result = self._values.get("bid_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def desired_vcpus(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#desired_vcpus BatchComputeEnvironment#desired_vcpus}.'''
        result = self._values.get("desired_vcpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ec2_configuration(
        self,
    ) -> typing.Optional["BatchComputeEnvironmentComputeResourcesEc2Configuration"]:
        '''ec2_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_configuration BatchComputeEnvironment#ec2_configuration}
        '''
        result = self._values.get("ec2_configuration")
        return typing.cast(typing.Optional["BatchComputeEnvironmentComputeResourcesEc2Configuration"], result)

    @builtins.property
    def ec2_key_pair(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_key_pair BatchComputeEnvironment#ec2_key_pair}.'''
        result = self._values.get("ec2_key_pair")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id BatchComputeEnvironment#image_id}.'''
        result = self._values.get("image_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_role BatchComputeEnvironment#instance_role}.'''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_type BatchComputeEnvironment#instance_type}.'''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def launch_template(
        self,
    ) -> typing.Optional["BatchComputeEnvironmentComputeResourcesLaunchTemplate"]:
        '''launch_template block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template BatchComputeEnvironment#launch_template}
        '''
        result = self._values.get("launch_template")
        return typing.cast(typing.Optional["BatchComputeEnvironmentComputeResourcesLaunchTemplate"], result)

    @builtins.property
    def min_vcpus(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#min_vcpus BatchComputeEnvironment#min_vcpus}.'''
        result = self._values.get("min_vcpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def spot_iam_fleet_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#spot_iam_fleet_role BatchComputeEnvironment#spot_iam_fleet_role}.'''
        result = self._values.get("spot_iam_fleet_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchComputeEnvironmentComputeResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResourcesEc2Configuration",
    jsii_struct_bases=[],
    name_mapping={"image_id_override": "imageIdOverride", "image_type": "imageType"},
)
class BatchComputeEnvironmentComputeResourcesEc2Configuration:
    def __init__(
        self,
        *,
        image_id_override: typing.Optional[builtins.str] = None,
        image_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image_id_override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id_override BatchComputeEnvironment#image_id_override}.
        :param image_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_type BatchComputeEnvironment#image_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchComputeEnvironmentComputeResourcesEc2Configuration.__init__)
            check_type(argname="argument image_id_override", value=image_id_override, expected_type=type_hints["image_id_override"])
            check_type(argname="argument image_type", value=image_type, expected_type=type_hints["image_type"])
        self._values: typing.Dict[str, typing.Any] = {}
        if image_id_override is not None:
            self._values["image_id_override"] = image_id_override
        if image_type is not None:
            self._values["image_type"] = image_type

    @builtins.property
    def image_id_override(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id_override BatchComputeEnvironment#image_id_override}.'''
        result = self._values.get("image_id_override")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_type BatchComputeEnvironment#image_type}.'''
        result = self._values.get("image_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchComputeEnvironmentComputeResourcesEc2Configuration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetImageIdOverride")
    def reset_image_id_override(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageIdOverride", []))

    @jsii.member(jsii_name="resetImageType")
    def reset_image_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageIdOverrideInput")
    def image_id_override_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageIdOverrideInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTypeInput")
    def image_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageIdOverride")
    def image_id_override(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageIdOverride"))

    @image_id_override.setter
    def image_id_override(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference, "image_id_override").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageIdOverride", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageType")
    def image_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageType"))

    @image_type.setter
    def image_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference, "image_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResourcesEc2Configuration]:
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResourcesEc2Configuration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BatchComputeEnvironmentComputeResourcesEc2Configuration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResourcesLaunchTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "launch_template_id": "launchTemplateId",
        "launch_template_name": "launchTemplateName",
        "version": "version",
    },
)
class BatchComputeEnvironmentComputeResourcesLaunchTemplate:
    def __init__(
        self,
        *,
        launch_template_id: typing.Optional[builtins.str] = None,
        launch_template_name: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param launch_template_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_id BatchComputeEnvironment#launch_template_id}.
        :param launch_template_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_name BatchComputeEnvironment#launch_template_name}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#version BatchComputeEnvironment#version}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchComputeEnvironmentComputeResourcesLaunchTemplate.__init__)
            check_type(argname="argument launch_template_id", value=launch_template_id, expected_type=type_hints["launch_template_id"])
            check_type(argname="argument launch_template_name", value=launch_template_name, expected_type=type_hints["launch_template_name"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[str, typing.Any] = {}
        if launch_template_id is not None:
            self._values["launch_template_id"] = launch_template_id
        if launch_template_name is not None:
            self._values["launch_template_name"] = launch_template_name
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def launch_template_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_id BatchComputeEnvironment#launch_template_id}.'''
        result = self._values.get("launch_template_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def launch_template_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_name BatchComputeEnvironment#launch_template_name}.'''
        result = self._values.get("launch_template_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#version BatchComputeEnvironment#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchComputeEnvironmentComputeResourcesLaunchTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference",
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
            type_hints = typing.get_type_hints(BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLaunchTemplateId")
    def reset_launch_template_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchTemplateId", []))

    @jsii.member(jsii_name="resetLaunchTemplateName")
    def reset_launch_template_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchTemplateName", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateIdInput")
    def launch_template_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "launchTemplateIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateNameInput")
    def launch_template_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "launchTemplateNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateId")
    def launch_template_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "launchTemplateId"))

    @launch_template_id.setter
    def launch_template_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference, "launch_template_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "launchTemplateId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateName")
    def launch_template_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "launchTemplateName"))

    @launch_template_name.setter
    def launch_template_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference, "launch_template_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "launchTemplateName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference, "version").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResourcesLaunchTemplate]:
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResourcesLaunchTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BatchComputeEnvironmentComputeResourcesLaunchTemplate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class BatchComputeEnvironmentComputeResourcesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResourcesOutputReference",
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
            type_hints = typing.get_type_hints(BatchComputeEnvironmentComputeResourcesOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEc2Configuration")
    def put_ec2_configuration(
        self,
        *,
        image_id_override: typing.Optional[builtins.str] = None,
        image_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image_id_override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id_override BatchComputeEnvironment#image_id_override}.
        :param image_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_type BatchComputeEnvironment#image_type}.
        '''
        value = BatchComputeEnvironmentComputeResourcesEc2Configuration(
            image_id_override=image_id_override, image_type=image_type
        )

        return typing.cast(None, jsii.invoke(self, "putEc2Configuration", [value]))

    @jsii.member(jsii_name="putLaunchTemplate")
    def put_launch_template(
        self,
        *,
        launch_template_id: typing.Optional[builtins.str] = None,
        launch_template_name: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param launch_template_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_id BatchComputeEnvironment#launch_template_id}.
        :param launch_template_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_name BatchComputeEnvironment#launch_template_name}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#version BatchComputeEnvironment#version}.
        '''
        value = BatchComputeEnvironmentComputeResourcesLaunchTemplate(
            launch_template_id=launch_template_id,
            launch_template_name=launch_template_name,
            version=version,
        )

        return typing.cast(None, jsii.invoke(self, "putLaunchTemplate", [value]))

    @jsii.member(jsii_name="resetAllocationStrategy")
    def reset_allocation_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllocationStrategy", []))

    @jsii.member(jsii_name="resetBidPercentage")
    def reset_bid_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBidPercentage", []))

    @jsii.member(jsii_name="resetDesiredVcpus")
    def reset_desired_vcpus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDesiredVcpus", []))

    @jsii.member(jsii_name="resetEc2Configuration")
    def reset_ec2_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2Configuration", []))

    @jsii.member(jsii_name="resetEc2KeyPair")
    def reset_ec2_key_pair(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2KeyPair", []))

    @jsii.member(jsii_name="resetImageId")
    def reset_image_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageId", []))

    @jsii.member(jsii_name="resetInstanceRole")
    def reset_instance_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceRole", []))

    @jsii.member(jsii_name="resetInstanceType")
    def reset_instance_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceType", []))

    @jsii.member(jsii_name="resetLaunchTemplate")
    def reset_launch_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchTemplate", []))

    @jsii.member(jsii_name="resetMinVcpus")
    def reset_min_vcpus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinVcpus", []))

    @jsii.member(jsii_name="resetSpotIamFleetRole")
    def reset_spot_iam_fleet_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotIamFleetRole", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2Configuration")
    def ec2_configuration(
        self,
    ) -> BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference:
        return typing.cast(BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference, jsii.get(self, "ec2Configuration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplate")
    def launch_template(
        self,
    ) -> BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference:
        return typing.cast(BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference, jsii.get(self, "launchTemplate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocationStrategyInput")
    def allocation_strategy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allocationStrategyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bidPercentageInput")
    def bid_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bidPercentageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="desiredVcpusInput")
    def desired_vcpus_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "desiredVcpusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2ConfigurationInput")
    def ec2_configuration_input(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResourcesEc2Configuration]:
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResourcesEc2Configuration], jsii.get(self, "ec2ConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2KeyPairInput")
    def ec2_key_pair_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ec2KeyPairInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageIdInput")
    def image_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRoleInput")
    def instance_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeInput")
    def instance_type_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "instanceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateInput")
    def launch_template_input(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResourcesLaunchTemplate]:
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResourcesLaunchTemplate], jsii.get(self, "launchTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxVcpusInput")
    def max_vcpus_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxVcpusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minVcpusInput")
    def min_vcpus_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minVcpusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotIamFleetRoleInput")
    def spot_iam_fleet_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotIamFleetRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetsInput")
    def subnets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocationStrategy")
    def allocation_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allocationStrategy"))

    @allocation_strategy.setter
    def allocation_strategy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "allocation_strategy").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allocationStrategy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bidPercentage")
    def bid_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bidPercentage"))

    @bid_percentage.setter
    def bid_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "bid_percentage").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bidPercentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="desiredVcpus")
    def desired_vcpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "desiredVcpus"))

    @desired_vcpus.setter
    def desired_vcpus(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "desired_vcpus").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "desiredVcpus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2KeyPair")
    def ec2_key_pair(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ec2KeyPair"))

    @ec2_key_pair.setter
    def ec2_key_pair(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "ec2_key_pair").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ec2KeyPair", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @image_id.setter
    def image_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "image_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRole")
    def instance_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceRole"))

    @instance_role.setter
    def instance_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "instance_role").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "instance_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxVcpus")
    def max_vcpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVcpus"))

    @max_vcpus.setter
    def max_vcpus(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "max_vcpus").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVcpus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minVcpus")
    def min_vcpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minVcpus"))

    @min_vcpus.setter
    def min_vcpus(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "min_vcpus").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minVcpus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "security_group_ids").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotIamFleetRole")
    def spot_iam_fleet_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotIamFleetRole"))

    @spot_iam_fleet_role.setter
    def spot_iam_fleet_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "spot_iam_fleet_role").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotIamFleetRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnets")
    def subnets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnets"))

    @subnets.setter
    def subnets(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "subnets").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResources]:
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResources], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BatchComputeEnvironmentComputeResources],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchComputeEnvironmentComputeResourcesOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "type": "type",
        "compute_environment_name": "computeEnvironmentName",
        "compute_environment_name_prefix": "computeEnvironmentNamePrefix",
        "compute_resources": "computeResources",
        "id": "id",
        "service_role": "serviceRole",
        "state": "state",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class BatchComputeEnvironmentConfig(cdktf.TerraformMetaArguments):
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
        type: builtins.str,
        compute_environment_name: typing.Optional[builtins.str] = None,
        compute_environment_name_prefix: typing.Optional[builtins.str] = None,
        compute_resources: typing.Optional[typing.Union[BatchComputeEnvironmentComputeResources, typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        service_role: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Batch.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.
        :param compute_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name BatchComputeEnvironment#compute_environment_name}.
        :param compute_environment_name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name_prefix BatchComputeEnvironment#compute_environment_name_prefix}.
        :param compute_resources: compute_resources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_resources BatchComputeEnvironment#compute_resources}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#id BatchComputeEnvironment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param service_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#service_role BatchComputeEnvironment#service_role}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#state BatchComputeEnvironment#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags_all BatchComputeEnvironment#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(compute_resources, dict):
            compute_resources = BatchComputeEnvironmentComputeResources(**compute_resources)
        if __debug__:
            type_hints = typing.get_type_hints(BatchComputeEnvironmentConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument compute_environment_name", value=compute_environment_name, expected_type=type_hints["compute_environment_name"])
            check_type(argname="argument compute_environment_name_prefix", value=compute_environment_name_prefix, expected_type=type_hints["compute_environment_name_prefix"])
            check_type(argname="argument compute_resources", value=compute_resources, expected_type=type_hints["compute_resources"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument service_role", value=service_role, expected_type=type_hints["service_role"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
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
        if compute_environment_name is not None:
            self._values["compute_environment_name"] = compute_environment_name
        if compute_environment_name_prefix is not None:
            self._values["compute_environment_name_prefix"] = compute_environment_name_prefix
        if compute_resources is not None:
            self._values["compute_resources"] = compute_resources
        if id is not None:
            self._values["id"] = id
        if service_role is not None:
            self._values["service_role"] = service_role
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
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compute_environment_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name BatchComputeEnvironment#compute_environment_name}.'''
        result = self._values.get("compute_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compute_environment_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name_prefix BatchComputeEnvironment#compute_environment_name_prefix}.'''
        result = self._values.get("compute_environment_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compute_resources(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResources]:
        '''compute_resources block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_resources BatchComputeEnvironment#compute_resources}
        '''
        result = self._values.get("compute_resources")
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResources], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#id BatchComputeEnvironment#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#service_role BatchComputeEnvironment#service_role}.'''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#state BatchComputeEnvironment#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags_all BatchComputeEnvironment#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchComputeEnvironmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchJobDefinition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition aws_batch_job_definition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        type: builtins.str,
        container_properties: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        platform_capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        propagate_tags: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        retry_strategy: typing.Optional[typing.Union["BatchJobDefinitionRetryStrategy", typing.Dict[str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeout: typing.Optional[typing.Union["BatchJobDefinitionTimeout", typing.Dict[str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition aws_batch_job_definition} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#name BatchJobDefinition#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#type BatchJobDefinition#type}.
        :param container_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#container_properties BatchJobDefinition#container_properties}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#id BatchJobDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#parameters BatchJobDefinition#parameters}.
        :param platform_capabilities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#platform_capabilities BatchJobDefinition#platform_capabilities}.
        :param propagate_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#propagate_tags BatchJobDefinition#propagate_tags}.
        :param retry_strategy: retry_strategy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#retry_strategy BatchJobDefinition#retry_strategy}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags BatchJobDefinition#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags_all BatchJobDefinition#tags_all}.
        :param timeout: timeout block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#timeout BatchJobDefinition#timeout}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchJobDefinition.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = BatchJobDefinitionConfig(
            name=name,
            type=type,
            container_properties=container_properties,
            id=id,
            parameters=parameters,
            platform_capabilities=platform_capabilities,
            propagate_tags=propagate_tags,
            retry_strategy=retry_strategy,
            tags=tags,
            tags_all=tags_all,
            timeout=timeout,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putRetryStrategy")
    def put_retry_strategy(
        self,
        *,
        attempts: typing.Optional[jsii.Number] = None,
        evaluate_on_exit: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["BatchJobDefinitionRetryStrategyEvaluateOnExit", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempts BatchJobDefinition#attempts}.
        :param evaluate_on_exit: evaluate_on_exit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#evaluate_on_exit BatchJobDefinition#evaluate_on_exit}
        '''
        value = BatchJobDefinitionRetryStrategy(
            attempts=attempts, evaluate_on_exit=evaluate_on_exit
        )

        return typing.cast(None, jsii.invoke(self, "putRetryStrategy", [value]))

    @jsii.member(jsii_name="putTimeout")
    def put_timeout(
        self,
        *,
        attempt_duration_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param attempt_duration_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempt_duration_seconds BatchJobDefinition#attempt_duration_seconds}.
        '''
        value = BatchJobDefinitionTimeout(
            attempt_duration_seconds=attempt_duration_seconds
        )

        return typing.cast(None, jsii.invoke(self, "putTimeout", [value]))

    @jsii.member(jsii_name="resetContainerProperties")
    def reset_container_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContainerProperties", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @jsii.member(jsii_name="resetPlatformCapabilities")
    def reset_platform_capabilities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlatformCapabilities", []))

    @jsii.member(jsii_name="resetPropagateTags")
    def reset_propagate_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPropagateTags", []))

    @jsii.member(jsii_name="resetRetryStrategy")
    def reset_retry_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryStrategy", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

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
    @jsii.member(jsii_name="retryStrategy")
    def retry_strategy(self) -> "BatchJobDefinitionRetryStrategyOutputReference":
        return typing.cast("BatchJobDefinitionRetryStrategyOutputReference", jsii.get(self, "retryStrategy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revision")
    def revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "revision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> "BatchJobDefinitionTimeoutOutputReference":
        return typing.cast("BatchJobDefinitionTimeoutOutputReference", jsii.get(self, "timeout"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerPropertiesInput")
    def container_properties_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerPropertiesInput"))

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
    @jsii.member(jsii_name="platformCapabilitiesInput")
    def platform_capabilities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "platformCapabilitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propagateTagsInput")
    def propagate_tags_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "propagateTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryStrategyInput")
    def retry_strategy_input(
        self,
    ) -> typing.Optional["BatchJobDefinitionRetryStrategy"]:
        return typing.cast(typing.Optional["BatchJobDefinitionRetryStrategy"], jsii.get(self, "retryStrategyInput"))

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
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional["BatchJobDefinitionTimeout"]:
        return typing.cast(typing.Optional["BatchJobDefinitionTimeout"], jsii.get(self, "timeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerProperties")
    def container_properties(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerProperties"))

    @container_properties.setter
    def container_properties(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinition, "container_properties").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "containerProperties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinition, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinition, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinition, "parameters").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformCapabilities")
    def platform_capabilities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "platformCapabilities"))

    @platform_capabilities.setter
    def platform_capabilities(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinition, "platform_capabilities").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "platformCapabilities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propagateTags")
    def propagate_tags(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "propagateTags"))

    @propagate_tags.setter
    def propagate_tags(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinition, "propagate_tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "propagateTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinition, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinition, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinition, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionConfig",
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
        "type": "type",
        "container_properties": "containerProperties",
        "id": "id",
        "parameters": "parameters",
        "platform_capabilities": "platformCapabilities",
        "propagate_tags": "propagateTags",
        "retry_strategy": "retryStrategy",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeout": "timeout",
    },
)
class BatchJobDefinitionConfig(cdktf.TerraformMetaArguments):
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
        type: builtins.str,
        container_properties: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        platform_capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        propagate_tags: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        retry_strategy: typing.Optional[typing.Union["BatchJobDefinitionRetryStrategy", typing.Dict[str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeout: typing.Optional[typing.Union["BatchJobDefinitionTimeout", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''AWS Batch.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#name BatchJobDefinition#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#type BatchJobDefinition#type}.
        :param container_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#container_properties BatchJobDefinition#container_properties}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#id BatchJobDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#parameters BatchJobDefinition#parameters}.
        :param platform_capabilities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#platform_capabilities BatchJobDefinition#platform_capabilities}.
        :param propagate_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#propagate_tags BatchJobDefinition#propagate_tags}.
        :param retry_strategy: retry_strategy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#retry_strategy BatchJobDefinition#retry_strategy}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags BatchJobDefinition#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags_all BatchJobDefinition#tags_all}.
        :param timeout: timeout block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#timeout BatchJobDefinition#timeout}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(retry_strategy, dict):
            retry_strategy = BatchJobDefinitionRetryStrategy(**retry_strategy)
        if isinstance(timeout, dict):
            timeout = BatchJobDefinitionTimeout(**timeout)
        if __debug__:
            type_hints = typing.get_type_hints(BatchJobDefinitionConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument container_properties", value=container_properties, expected_type=type_hints["container_properties"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument platform_capabilities", value=platform_capabilities, expected_type=type_hints["platform_capabilities"])
            check_type(argname="argument propagate_tags", value=propagate_tags, expected_type=type_hints["propagate_tags"])
            check_type(argname="argument retry_strategy", value=retry_strategy, expected_type=type_hints["retry_strategy"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[str, typing.Any] = {
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
        if container_properties is not None:
            self._values["container_properties"] = container_properties
        if id is not None:
            self._values["id"] = id
        if parameters is not None:
            self._values["parameters"] = parameters
        if platform_capabilities is not None:
            self._values["platform_capabilities"] = platform_capabilities
        if propagate_tags is not None:
            self._values["propagate_tags"] = propagate_tags
        if retry_strategy is not None:
            self._values["retry_strategy"] = retry_strategy
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeout is not None:
            self._values["timeout"] = timeout

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#name BatchJobDefinition#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#type BatchJobDefinition#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def container_properties(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#container_properties BatchJobDefinition#container_properties}.'''
        result = self._values.get("container_properties")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#id BatchJobDefinition#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#parameters BatchJobDefinition#parameters}.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def platform_capabilities(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#platform_capabilities BatchJobDefinition#platform_capabilities}.'''
        result = self._values.get("platform_capabilities")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def propagate_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#propagate_tags BatchJobDefinition#propagate_tags}.'''
        result = self._values.get("propagate_tags")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def retry_strategy(self) -> typing.Optional["BatchJobDefinitionRetryStrategy"]:
        '''retry_strategy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#retry_strategy BatchJobDefinition#retry_strategy}
        '''
        result = self._values.get("retry_strategy")
        return typing.cast(typing.Optional["BatchJobDefinitionRetryStrategy"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags BatchJobDefinition#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags_all BatchJobDefinition#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def timeout(self) -> typing.Optional["BatchJobDefinitionTimeout"]:
        '''timeout block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#timeout BatchJobDefinition#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional["BatchJobDefinitionTimeout"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchJobDefinitionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionRetryStrategy",
    jsii_struct_bases=[],
    name_mapping={"attempts": "attempts", "evaluate_on_exit": "evaluateOnExit"},
)
class BatchJobDefinitionRetryStrategy:
    def __init__(
        self,
        *,
        attempts: typing.Optional[jsii.Number] = None,
        evaluate_on_exit: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["BatchJobDefinitionRetryStrategyEvaluateOnExit", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempts BatchJobDefinition#attempts}.
        :param evaluate_on_exit: evaluate_on_exit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#evaluate_on_exit BatchJobDefinition#evaluate_on_exit}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchJobDefinitionRetryStrategy.__init__)
            check_type(argname="argument attempts", value=attempts, expected_type=type_hints["attempts"])
            check_type(argname="argument evaluate_on_exit", value=evaluate_on_exit, expected_type=type_hints["evaluate_on_exit"])
        self._values: typing.Dict[str, typing.Any] = {}
        if attempts is not None:
            self._values["attempts"] = attempts
        if evaluate_on_exit is not None:
            self._values["evaluate_on_exit"] = evaluate_on_exit

    @builtins.property
    def attempts(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempts BatchJobDefinition#attempts}.'''
        result = self._values.get("attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def evaluate_on_exit(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["BatchJobDefinitionRetryStrategyEvaluateOnExit"]]]:
        '''evaluate_on_exit block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#evaluate_on_exit BatchJobDefinition#evaluate_on_exit}
        '''
        result = self._values.get("evaluate_on_exit")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["BatchJobDefinitionRetryStrategyEvaluateOnExit"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchJobDefinitionRetryStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionRetryStrategyEvaluateOnExit",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "on_exit_code": "onExitCode",
        "on_reason": "onReason",
        "on_status_reason": "onStatusReason",
    },
)
class BatchJobDefinitionRetryStrategyEvaluateOnExit:
    def __init__(
        self,
        *,
        action: builtins.str,
        on_exit_code: typing.Optional[builtins.str] = None,
        on_reason: typing.Optional[builtins.str] = None,
        on_status_reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#action BatchJobDefinition#action}.
        :param on_exit_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_exit_code BatchJobDefinition#on_exit_code}.
        :param on_reason: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_reason BatchJobDefinition#on_reason}.
        :param on_status_reason: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_status_reason BatchJobDefinition#on_status_reason}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchJobDefinitionRetryStrategyEvaluateOnExit.__init__)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument on_exit_code", value=on_exit_code, expected_type=type_hints["on_exit_code"])
            check_type(argname="argument on_reason", value=on_reason, expected_type=type_hints["on_reason"])
            check_type(argname="argument on_status_reason", value=on_status_reason, expected_type=type_hints["on_status_reason"])
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
        }
        if on_exit_code is not None:
            self._values["on_exit_code"] = on_exit_code
        if on_reason is not None:
            self._values["on_reason"] = on_reason
        if on_status_reason is not None:
            self._values["on_status_reason"] = on_status_reason

    @builtins.property
    def action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#action BatchJobDefinition#action}.'''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def on_exit_code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_exit_code BatchJobDefinition#on_exit_code}.'''
        result = self._values.get("on_exit_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_reason(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_reason BatchJobDefinition#on_reason}.'''
        result = self._values.get("on_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_status_reason(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_status_reason BatchJobDefinition#on_status_reason}.'''
        result = self._values.get("on_status_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchJobDefinitionRetryStrategyEvaluateOnExit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchJobDefinitionRetryStrategyEvaluateOnExitList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionRetryStrategyEvaluateOnExitList",
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
            type_hints = typing.get_type_hints(BatchJobDefinitionRetryStrategyEvaluateOnExitList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchJobDefinitionRetryStrategyEvaluateOnExitList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyEvaluateOnExitList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyEvaluateOnExitList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyEvaluateOnExitList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[BatchJobDefinitionRetryStrategyEvaluateOnExit]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[BatchJobDefinitionRetryStrategyEvaluateOnExit]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[BatchJobDefinitionRetryStrategyEvaluateOnExit]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyEvaluateOnExitList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference",
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
            type_hints = typing.get_type_hints(BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetOnExitCode")
    def reset_on_exit_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnExitCode", []))

    @jsii.member(jsii_name="resetOnReason")
    def reset_on_reason(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnReason", []))

    @jsii.member(jsii_name="resetOnStatusReason")
    def reset_on_status_reason(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnStatusReason", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onExitCodeInput")
    def on_exit_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onExitCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onReasonInput")
    def on_reason_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onReasonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onStatusReasonInput")
    def on_status_reason_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onStatusReasonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference, "action").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onExitCode")
    def on_exit_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onExitCode"))

    @on_exit_code.setter
    def on_exit_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference, "on_exit_code").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onExitCode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onReason")
    def on_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onReason"))

    @on_reason.setter
    def on_reason(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference, "on_reason").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onReason", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onStatusReason")
    def on_status_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onStatusReason"))

    @on_status_reason.setter
    def on_status_reason(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference, "on_status_reason").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onStatusReason", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[BatchJobDefinitionRetryStrategyEvaluateOnExit, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[BatchJobDefinitionRetryStrategyEvaluateOnExit, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[BatchJobDefinitionRetryStrategyEvaluateOnExit, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class BatchJobDefinitionRetryStrategyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionRetryStrategyOutputReference",
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
            type_hints = typing.get_type_hints(BatchJobDefinitionRetryStrategyOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEvaluateOnExit")
    def put_evaluate_on_exit(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union[BatchJobDefinitionRetryStrategyEvaluateOnExit, typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchJobDefinitionRetryStrategyOutputReference.put_evaluate_on_exit)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEvaluateOnExit", [value]))

    @jsii.member(jsii_name="resetAttempts")
    def reset_attempts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttempts", []))

    @jsii.member(jsii_name="resetEvaluateOnExit")
    def reset_evaluate_on_exit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvaluateOnExit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluateOnExit")
    def evaluate_on_exit(self) -> BatchJobDefinitionRetryStrategyEvaluateOnExitList:
        return typing.cast(BatchJobDefinitionRetryStrategyEvaluateOnExitList, jsii.get(self, "evaluateOnExit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attemptsInput")
    def attempts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "attemptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluateOnExitInput")
    def evaluate_on_exit_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[BatchJobDefinitionRetryStrategyEvaluateOnExit]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[BatchJobDefinitionRetryStrategyEvaluateOnExit]]], jsii.get(self, "evaluateOnExitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attempts")
    def attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "attempts"))

    @attempts.setter
    def attempts(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyOutputReference, "attempts").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attempts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BatchJobDefinitionRetryStrategy]:
        return typing.cast(typing.Optional[BatchJobDefinitionRetryStrategy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BatchJobDefinitionRetryStrategy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionRetryStrategyOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionTimeout",
    jsii_struct_bases=[],
    name_mapping={"attempt_duration_seconds": "attemptDurationSeconds"},
)
class BatchJobDefinitionTimeout:
    def __init__(
        self,
        *,
        attempt_duration_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param attempt_duration_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempt_duration_seconds BatchJobDefinition#attempt_duration_seconds}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchJobDefinitionTimeout.__init__)
            check_type(argname="argument attempt_duration_seconds", value=attempt_duration_seconds, expected_type=type_hints["attempt_duration_seconds"])
        self._values: typing.Dict[str, typing.Any] = {}
        if attempt_duration_seconds is not None:
            self._values["attempt_duration_seconds"] = attempt_duration_seconds

    @builtins.property
    def attempt_duration_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempt_duration_seconds BatchJobDefinition#attempt_duration_seconds}.'''
        result = self._values.get("attempt_duration_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchJobDefinitionTimeout(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchJobDefinitionTimeoutOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionTimeoutOutputReference",
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
            type_hints = typing.get_type_hints(BatchJobDefinitionTimeoutOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAttemptDurationSeconds")
    def reset_attempt_duration_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttemptDurationSeconds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attemptDurationSecondsInput")
    def attempt_duration_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "attemptDurationSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attemptDurationSeconds")
    def attempt_duration_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "attemptDurationSeconds"))

    @attempt_duration_seconds.setter
    def attempt_duration_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionTimeoutOutputReference, "attempt_duration_seconds").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attemptDurationSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BatchJobDefinitionTimeout]:
        return typing.cast(typing.Optional[BatchJobDefinitionTimeout], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[BatchJobDefinitionTimeout]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobDefinitionTimeoutOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class BatchJobQueue(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchJobQueue",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue aws_batch_job_queue}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        compute_environments: typing.Sequence[builtins.str],
        name: builtins.str,
        priority: jsii.Number,
        state: builtins.str,
        id: typing.Optional[builtins.str] = None,
        scheduling_policy_arn: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue aws_batch_job_queue} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param compute_environments: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#compute_environments BatchJobQueue#compute_environments}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#name BatchJobQueue#name}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#priority BatchJobQueue#priority}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#state BatchJobQueue#state}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#id BatchJobQueue#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param scheduling_policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#scheduling_policy_arn BatchJobQueue#scheduling_policy_arn}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags BatchJobQueue#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags_all BatchJobQueue#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchJobQueue.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = BatchJobQueueConfig(
            compute_environments=compute_environments,
            name=name,
            priority=priority,
            state=state,
            id=id,
            scheduling_policy_arn=scheduling_policy_arn,
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

    @jsii.member(jsii_name="resetSchedulingPolicyArn")
    def reset_scheduling_policy_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedulingPolicyArn", []))

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
    @jsii.member(jsii_name="computeEnvironmentsInput")
    def compute_environments_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "computeEnvironmentsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedulingPolicyArnInput")
    def scheduling_policy_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schedulingPolicyArnInput"))

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
    @jsii.member(jsii_name="computeEnvironments")
    def compute_environments(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "computeEnvironments"))

    @compute_environments.setter
    def compute_environments(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobQueue, "compute_environments").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "computeEnvironments", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobQueue, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobQueue, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobQueue, "priority").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedulingPolicyArn")
    def scheduling_policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schedulingPolicyArn"))

    @scheduling_policy_arn.setter
    def scheduling_policy_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobQueue, "scheduling_policy_arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schedulingPolicyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobQueue, "state").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobQueue, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchJobQueue, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchJobQueueConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "compute_environments": "computeEnvironments",
        "name": "name",
        "priority": "priority",
        "state": "state",
        "id": "id",
        "scheduling_policy_arn": "schedulingPolicyArn",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class BatchJobQueueConfig(cdktf.TerraformMetaArguments):
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
        compute_environments: typing.Sequence[builtins.str],
        name: builtins.str,
        priority: jsii.Number,
        state: builtins.str,
        id: typing.Optional[builtins.str] = None,
        scheduling_policy_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Batch.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param compute_environments: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#compute_environments BatchJobQueue#compute_environments}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#name BatchJobQueue#name}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#priority BatchJobQueue#priority}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#state BatchJobQueue#state}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#id BatchJobQueue#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param scheduling_policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#scheduling_policy_arn BatchJobQueue#scheduling_policy_arn}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags BatchJobQueue#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags_all BatchJobQueue#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(BatchJobQueueConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument compute_environments", value=compute_environments, expected_type=type_hints["compute_environments"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument scheduling_policy_arn", value=scheduling_policy_arn, expected_type=type_hints["scheduling_policy_arn"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tags_all", value=tags_all, expected_type=type_hints["tags_all"])
        self._values: typing.Dict[str, typing.Any] = {
            "compute_environments": compute_environments,
            "name": name,
            "priority": priority,
            "state": state,
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
        if scheduling_policy_arn is not None:
            self._values["scheduling_policy_arn"] = scheduling_policy_arn
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
    def compute_environments(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#compute_environments BatchJobQueue#compute_environments}.'''
        result = self._values.get("compute_environments")
        assert result is not None, "Required property 'compute_environments' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#name BatchJobQueue#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#priority BatchJobQueue#priority}.'''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def state(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#state BatchJobQueue#state}.'''
        result = self._values.get("state")
        assert result is not None, "Required property 'state' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#id BatchJobQueue#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scheduling_policy_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#scheduling_policy_arn BatchJobQueue#scheduling_policy_arn}.'''
        result = self._values.get("scheduling_policy_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags BatchJobQueue#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags_all BatchJobQueue#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchJobQueueConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchSchedulingPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy aws_batch_scheduling_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        fair_share_policy: typing.Optional[typing.Union["BatchSchedulingPolicyFairSharePolicy", typing.Dict[str, typing.Any]]] = None,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy aws_batch_scheduling_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#name BatchSchedulingPolicy#name}.
        :param fair_share_policy: fair_share_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#fair_share_policy BatchSchedulingPolicy#fair_share_policy}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#id BatchSchedulingPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags BatchSchedulingPolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags_all BatchSchedulingPolicy#tags_all}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchSchedulingPolicy.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = BatchSchedulingPolicyConfig(
            name=name,
            fair_share_policy=fair_share_policy,
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

    @jsii.member(jsii_name="putFairSharePolicy")
    def put_fair_share_policy(
        self,
        *,
        compute_reservation: typing.Optional[jsii.Number] = None,
        share_decay_seconds: typing.Optional[jsii.Number] = None,
        share_distribution: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["BatchSchedulingPolicyFairSharePolicyShareDistribution", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param compute_reservation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#compute_reservation BatchSchedulingPolicy#compute_reservation}.
        :param share_decay_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_decay_seconds BatchSchedulingPolicy#share_decay_seconds}.
        :param share_distribution: share_distribution block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_distribution BatchSchedulingPolicy#share_distribution}
        '''
        value = BatchSchedulingPolicyFairSharePolicy(
            compute_reservation=compute_reservation,
            share_decay_seconds=share_decay_seconds,
            share_distribution=share_distribution,
        )

        return typing.cast(None, jsii.invoke(self, "putFairSharePolicy", [value]))

    @jsii.member(jsii_name="resetFairSharePolicy")
    def reset_fair_share_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFairSharePolicy", []))

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
    @jsii.member(jsii_name="fairSharePolicy")
    def fair_share_policy(
        self,
    ) -> "BatchSchedulingPolicyFairSharePolicyOutputReference":
        return typing.cast("BatchSchedulingPolicyFairSharePolicyOutputReference", jsii.get(self, "fairSharePolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fairSharePolicyInput")
    def fair_share_policy_input(
        self,
    ) -> typing.Optional["BatchSchedulingPolicyFairSharePolicy"]:
        return typing.cast(typing.Optional["BatchSchedulingPolicyFairSharePolicy"], jsii.get(self, "fairSharePolicyInput"))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicy, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicy, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicy, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicy, "tags_all").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicyConfig",
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
        "fair_share_policy": "fairSharePolicy",
        "id": "id",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class BatchSchedulingPolicyConfig(cdktf.TerraformMetaArguments):
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
        fair_share_policy: typing.Optional[typing.Union["BatchSchedulingPolicyFairSharePolicy", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Batch.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#name BatchSchedulingPolicy#name}.
        :param fair_share_policy: fair_share_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#fair_share_policy BatchSchedulingPolicy#fair_share_policy}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#id BatchSchedulingPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags BatchSchedulingPolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags_all BatchSchedulingPolicy#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(fair_share_policy, dict):
            fair_share_policy = BatchSchedulingPolicyFairSharePolicy(**fair_share_policy)
        if __debug__:
            type_hints = typing.get_type_hints(BatchSchedulingPolicyConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument fair_share_policy", value=fair_share_policy, expected_type=type_hints["fair_share_policy"])
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
        if fair_share_policy is not None:
            self._values["fair_share_policy"] = fair_share_policy
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#name BatchSchedulingPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def fair_share_policy(
        self,
    ) -> typing.Optional["BatchSchedulingPolicyFairSharePolicy"]:
        '''fair_share_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#fair_share_policy BatchSchedulingPolicy#fair_share_policy}
        '''
        result = self._values.get("fair_share_policy")
        return typing.cast(typing.Optional["BatchSchedulingPolicyFairSharePolicy"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#id BatchSchedulingPolicy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags BatchSchedulingPolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags_all BatchSchedulingPolicy#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchSchedulingPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicyFairSharePolicy",
    jsii_struct_bases=[],
    name_mapping={
        "compute_reservation": "computeReservation",
        "share_decay_seconds": "shareDecaySeconds",
        "share_distribution": "shareDistribution",
    },
)
class BatchSchedulingPolicyFairSharePolicy:
    def __init__(
        self,
        *,
        compute_reservation: typing.Optional[jsii.Number] = None,
        share_decay_seconds: typing.Optional[jsii.Number] = None,
        share_distribution: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["BatchSchedulingPolicyFairSharePolicyShareDistribution", typing.Dict[str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param compute_reservation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#compute_reservation BatchSchedulingPolicy#compute_reservation}.
        :param share_decay_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_decay_seconds BatchSchedulingPolicy#share_decay_seconds}.
        :param share_distribution: share_distribution block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_distribution BatchSchedulingPolicy#share_distribution}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchSchedulingPolicyFairSharePolicy.__init__)
            check_type(argname="argument compute_reservation", value=compute_reservation, expected_type=type_hints["compute_reservation"])
            check_type(argname="argument share_decay_seconds", value=share_decay_seconds, expected_type=type_hints["share_decay_seconds"])
            check_type(argname="argument share_distribution", value=share_distribution, expected_type=type_hints["share_distribution"])
        self._values: typing.Dict[str, typing.Any] = {}
        if compute_reservation is not None:
            self._values["compute_reservation"] = compute_reservation
        if share_decay_seconds is not None:
            self._values["share_decay_seconds"] = share_decay_seconds
        if share_distribution is not None:
            self._values["share_distribution"] = share_distribution

    @builtins.property
    def compute_reservation(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#compute_reservation BatchSchedulingPolicy#compute_reservation}.'''
        result = self._values.get("compute_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def share_decay_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_decay_seconds BatchSchedulingPolicy#share_decay_seconds}.'''
        result = self._values.get("share_decay_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def share_distribution(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"]]]:
        '''share_distribution block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_distribution BatchSchedulingPolicy#share_distribution}
        '''
        result = self._values.get("share_distribution")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchSchedulingPolicyFairSharePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchSchedulingPolicyFairSharePolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicyFairSharePolicyOutputReference",
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
            type_hints = typing.get_type_hints(BatchSchedulingPolicyFairSharePolicyOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putShareDistribution")
    def put_share_distribution(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["BatchSchedulingPolicyFairSharePolicyShareDistribution", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchSchedulingPolicyFairSharePolicyOutputReference.put_share_distribution)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putShareDistribution", [value]))

    @jsii.member(jsii_name="resetComputeReservation")
    def reset_compute_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputeReservation", []))

    @jsii.member(jsii_name="resetShareDecaySeconds")
    def reset_share_decay_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShareDecaySeconds", []))

    @jsii.member(jsii_name="resetShareDistribution")
    def reset_share_distribution(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShareDistribution", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDistribution")
    def share_distribution(
        self,
    ) -> "BatchSchedulingPolicyFairSharePolicyShareDistributionList":
        return typing.cast("BatchSchedulingPolicyFairSharePolicyShareDistributionList", jsii.get(self, "shareDistribution"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeReservationInput")
    def compute_reservation_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "computeReservationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDecaySecondsInput")
    def share_decay_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "shareDecaySecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDistributionInput")
    def share_distribution_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"]]], jsii.get(self, "shareDistributionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeReservation")
    def compute_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "computeReservation"))

    @compute_reservation.setter
    def compute_reservation(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicyFairSharePolicyOutputReference, "compute_reservation").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "computeReservation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDecaySeconds")
    def share_decay_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shareDecaySeconds"))

    @share_decay_seconds.setter
    def share_decay_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicyFairSharePolicyOutputReference, "share_decay_seconds").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shareDecaySeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BatchSchedulingPolicyFairSharePolicy]:
        return typing.cast(typing.Optional[BatchSchedulingPolicyFairSharePolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BatchSchedulingPolicyFairSharePolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicyFairSharePolicyOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicyFairSharePolicyShareDistribution",
    jsii_struct_bases=[],
    name_mapping={
        "share_identifier": "shareIdentifier",
        "weight_factor": "weightFactor",
    },
)
class BatchSchedulingPolicyFairSharePolicyShareDistribution:
    def __init__(
        self,
        *,
        share_identifier: builtins.str,
        weight_factor: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param share_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_identifier BatchSchedulingPolicy#share_identifier}.
        :param weight_factor: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#weight_factor BatchSchedulingPolicy#weight_factor}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchSchedulingPolicyFairSharePolicyShareDistribution.__init__)
            check_type(argname="argument share_identifier", value=share_identifier, expected_type=type_hints["share_identifier"])
            check_type(argname="argument weight_factor", value=weight_factor, expected_type=type_hints["weight_factor"])
        self._values: typing.Dict[str, typing.Any] = {
            "share_identifier": share_identifier,
        }
        if weight_factor is not None:
            self._values["weight_factor"] = weight_factor

    @builtins.property
    def share_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_identifier BatchSchedulingPolicy#share_identifier}.'''
        result = self._values.get("share_identifier")
        assert result is not None, "Required property 'share_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def weight_factor(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#weight_factor BatchSchedulingPolicy#weight_factor}.'''
        result = self._values.get("weight_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchSchedulingPolicyFairSharePolicyShareDistribution(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchSchedulingPolicyFairSharePolicyShareDistributionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicyFairSharePolicyShareDistributionList",
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
            type_hints = typing.get_type_hints(BatchSchedulingPolicyFairSharePolicyShareDistributionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "BatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BatchSchedulingPolicyFairSharePolicyShareDistributionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("BatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicyFairSharePolicyShareDistributionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicyFairSharePolicyShareDistributionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicyFairSharePolicyShareDistributionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[BatchSchedulingPolicyFairSharePolicyShareDistribution]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[BatchSchedulingPolicyFairSharePolicyShareDistribution]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[BatchSchedulingPolicyFairSharePolicyShareDistribution]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicyFairSharePolicyShareDistributionList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class BatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference",
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
            type_hints = typing.get_type_hints(BatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetWeightFactor")
    def reset_weight_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeightFactor", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareIdentifierInput")
    def share_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "shareIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weightFactorInput")
    def weight_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "weightFactorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareIdentifier")
    def share_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shareIdentifier"))

    @share_identifier.setter
    def share_identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference, "share_identifier").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shareIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weightFactor")
    def weight_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weightFactor"))

    @weight_factor.setter
    def weight_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference, "weight_factor").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "weightFactor", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[BatchSchedulingPolicyFairSharePolicyShareDistribution, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[BatchSchedulingPolicyFairSharePolicyShareDistribution, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[BatchSchedulingPolicyFairSharePolicyShareDistribution, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(BatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAwsBatchComputeEnvironment(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchComputeEnvironment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment aws_batch_compute_environment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        compute_environment_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment aws_batch_compute_environment} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param compute_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#compute_environment_name DataAwsBatchComputeEnvironment#compute_environment_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#id DataAwsBatchComputeEnvironment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#tags DataAwsBatchComputeEnvironment#tags}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsBatchComputeEnvironment.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsBatchComputeEnvironmentConfig(
            compute_environment_name=compute_environment_name,
            id=id,
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

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecsClusterArn")
    def ecs_cluster_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ecsClusterArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusReason")
    def status_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentNameInput")
    def compute_environment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computeEnvironmentNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentName"))

    @compute_environment_name.setter
    def compute_environment_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchComputeEnvironment, "compute_environment_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "computeEnvironmentName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchComputeEnvironment, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchComputeEnvironment, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchComputeEnvironmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "compute_environment_name": "computeEnvironmentName",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsBatchComputeEnvironmentConfig(cdktf.TerraformMetaArguments):
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
        compute_environment_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Batch.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param compute_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#compute_environment_name DataAwsBatchComputeEnvironment#compute_environment_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#id DataAwsBatchComputeEnvironment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#tags DataAwsBatchComputeEnvironment#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsBatchComputeEnvironmentConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument compute_environment_name", value=compute_environment_name, expected_type=type_hints["compute_environment_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[str, typing.Any] = {
            "compute_environment_name": compute_environment_name,
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
    def compute_environment_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#compute_environment_name DataAwsBatchComputeEnvironment#compute_environment_name}.'''
        result = self._values.get("compute_environment_name")
        assert result is not None, "Required property 'compute_environment_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#id DataAwsBatchComputeEnvironment#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#tags DataAwsBatchComputeEnvironment#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBatchComputeEnvironmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBatchJobQueue(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchJobQueue",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue aws_batch_job_queue}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue aws_batch_job_queue} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#name DataAwsBatchJobQueue#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#id DataAwsBatchJobQueue#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#tags DataAwsBatchJobQueue#tags}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsBatchJobQueue.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsBatchJobQueueConfig(
            name=name,
            id=id,
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

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentOrder")
    def compute_environment_order(
        self,
    ) -> "DataAwsBatchJobQueueComputeEnvironmentOrderList":
        return typing.cast("DataAwsBatchJobQueueComputeEnvironmentOrderList", jsii.get(self, "computeEnvironmentOrder"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedulingPolicyArn")
    def scheduling_policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schedulingPolicyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusReason")
    def status_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusReason"))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchJobQueue, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchJobQueue, "name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchJobQueue, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchJobQueueComputeEnvironmentOrder",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsBatchJobQueueComputeEnvironmentOrder:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBatchJobQueueComputeEnvironmentOrder(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBatchJobQueueComputeEnvironmentOrderList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchJobQueueComputeEnvironmentOrderList",
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
            type_hints = typing.get_type_hints(DataAwsBatchJobQueueComputeEnvironmentOrderList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsBatchJobQueueComputeEnvironmentOrderOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsBatchJobQueueComputeEnvironmentOrderList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsBatchJobQueueComputeEnvironmentOrderOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchJobQueueComputeEnvironmentOrderList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsBatchJobQueueComputeEnvironmentOrderList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsBatchJobQueueComputeEnvironmentOrderList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsBatchJobQueueComputeEnvironmentOrderOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchJobQueueComputeEnvironmentOrderOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsBatchJobQueueComputeEnvironmentOrderOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironment")
    def compute_environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="order")
    def order(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "order"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsBatchJobQueueComputeEnvironmentOrder]:
        return typing.cast(typing.Optional[DataAwsBatchJobQueueComputeEnvironmentOrder], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsBatchJobQueueComputeEnvironmentOrder],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchJobQueueComputeEnvironmentOrderOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchJobQueueConfig",
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
        "tags": "tags",
    },
)
class DataAwsBatchJobQueueConfig(cdktf.TerraformMetaArguments):
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
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Batch.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#name DataAwsBatchJobQueue#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#id DataAwsBatchJobQueue#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#tags DataAwsBatchJobQueue#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsBatchJobQueueConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#name DataAwsBatchJobQueue#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#id DataAwsBatchJobQueue#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#tags DataAwsBatchJobQueue#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBatchJobQueueConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBatchSchedulingPolicy(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy aws_batch_scheduling_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy aws_batch_scheduling_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#arn DataAwsBatchSchedulingPolicy#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#id DataAwsBatchSchedulingPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#tags DataAwsBatchSchedulingPolicy#tags}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsBatchSchedulingPolicy.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAwsBatchSchedulingPolicyConfig(
            arn=arn,
            id=id,
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

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="fairSharePolicy")
    def fair_share_policy(self) -> "DataAwsBatchSchedulingPolicyFairSharePolicyList":
        return typing.cast("DataAwsBatchSchedulingPolicyFairSharePolicyList", jsii.get(self, "fairSharePolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

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
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicy, "arn").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicy, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicy, "tags").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicyConfig",
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
        "tags": "tags",
    },
)
class DataAwsBatchSchedulingPolicyConfig(cdktf.TerraformMetaArguments):
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
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Batch.

        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#arn DataAwsBatchSchedulingPolicy#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#id DataAwsBatchSchedulingPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#tags DataAwsBatchSchedulingPolicy#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsBatchSchedulingPolicyConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#arn DataAwsBatchSchedulingPolicy#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#id DataAwsBatchSchedulingPolicy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#tags DataAwsBatchSchedulingPolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBatchSchedulingPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicyFairSharePolicy",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsBatchSchedulingPolicyFairSharePolicy:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBatchSchedulingPolicyFairSharePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBatchSchedulingPolicyFairSharePolicyList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicyFairSharePolicyList",
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
            type_hints = typing.get_type_hints(DataAwsBatchSchedulingPolicyFairSharePolicyList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsBatchSchedulingPolicyFairSharePolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsBatchSchedulingPolicyFairSharePolicyList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsBatchSchedulingPolicyFairSharePolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicyFairSharePolicyList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicyFairSharePolicyList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicyFairSharePolicyList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsBatchSchedulingPolicyFairSharePolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicyFairSharePolicyOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsBatchSchedulingPolicyFairSharePolicyOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeReservation")
    def compute_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "computeReservation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDecaySeconds")
    def share_decay_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shareDecaySeconds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDistribution")
    def share_distribution(
        self,
    ) -> "DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionList":
        return typing.cast("DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionList", jsii.get(self, "shareDistribution"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsBatchSchedulingPolicyFairSharePolicy]:
        return typing.cast(typing.Optional[DataAwsBatchSchedulingPolicyFairSharePolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsBatchSchedulingPolicyFairSharePolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicyFairSharePolicyOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicyFairSharePolicyShareDistribution",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsBatchSchedulingPolicyFairSharePolicyShareDistribution:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBatchSchedulingPolicyFairSharePolicyShareDistribution(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionList",
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
            type_hints = typing.get_type_hints(DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference",
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
            type_hints = typing.get_type_hints(DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareIdentifier")
    def share_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shareIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weightFactor")
    def weight_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weightFactor"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsBatchSchedulingPolicyFairSharePolicyShareDistribution]:
        return typing.cast(typing.Optional[DataAwsBatchSchedulingPolicyFairSharePolicyShareDistribution], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsBatchSchedulingPolicyFairSharePolicyShareDistribution],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "BatchComputeEnvironment",
    "BatchComputeEnvironmentComputeResources",
    "BatchComputeEnvironmentComputeResourcesEc2Configuration",
    "BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference",
    "BatchComputeEnvironmentComputeResourcesLaunchTemplate",
    "BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference",
    "BatchComputeEnvironmentComputeResourcesOutputReference",
    "BatchComputeEnvironmentConfig",
    "BatchJobDefinition",
    "BatchJobDefinitionConfig",
    "BatchJobDefinitionRetryStrategy",
    "BatchJobDefinitionRetryStrategyEvaluateOnExit",
    "BatchJobDefinitionRetryStrategyEvaluateOnExitList",
    "BatchJobDefinitionRetryStrategyEvaluateOnExitOutputReference",
    "BatchJobDefinitionRetryStrategyOutputReference",
    "BatchJobDefinitionTimeout",
    "BatchJobDefinitionTimeoutOutputReference",
    "BatchJobQueue",
    "BatchJobQueueConfig",
    "BatchSchedulingPolicy",
    "BatchSchedulingPolicyConfig",
    "BatchSchedulingPolicyFairSharePolicy",
    "BatchSchedulingPolicyFairSharePolicyOutputReference",
    "BatchSchedulingPolicyFairSharePolicyShareDistribution",
    "BatchSchedulingPolicyFairSharePolicyShareDistributionList",
    "BatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference",
    "DataAwsBatchComputeEnvironment",
    "DataAwsBatchComputeEnvironmentConfig",
    "DataAwsBatchJobQueue",
    "DataAwsBatchJobQueueComputeEnvironmentOrder",
    "DataAwsBatchJobQueueComputeEnvironmentOrderList",
    "DataAwsBatchJobQueueComputeEnvironmentOrderOutputReference",
    "DataAwsBatchJobQueueConfig",
    "DataAwsBatchSchedulingPolicy",
    "DataAwsBatchSchedulingPolicyConfig",
    "DataAwsBatchSchedulingPolicyFairSharePolicy",
    "DataAwsBatchSchedulingPolicyFairSharePolicyList",
    "DataAwsBatchSchedulingPolicyFairSharePolicyOutputReference",
    "DataAwsBatchSchedulingPolicyFairSharePolicyShareDistribution",
    "DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionList",
    "DataAwsBatchSchedulingPolicyFairSharePolicyShareDistributionOutputReference",
]

publication.publish()
