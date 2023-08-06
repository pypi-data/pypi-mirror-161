'''
# cdk-create-ami

![Experimental](https://img.shields.io/badge/experimental-important.svg?style=for-the-badge)

An AWS Cloud Development Kit (AWS CDK) construct library that allows you to build an [Amazon EC2](https://aws.amazon.com/ec2/) instance and create an [Amazon Machine Image](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html) from that instance.

## Background

From [Creating an AMI](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html#creating-an-ami):

> You can launch an instance from an existing AMI, customize the instance (for example, [install software](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/install-software.html) on the instance), and then save this updated configuration as a custom AMI. Instances launched from this new custom AMI include the customizations that you made when you created the AMI.

This CDK Construct will assist in you creating that AMI for later use.

## Installing

To add to your AWS CDK package.json file:

```
yarn add cdk-create-ami
```

## How It Works

To create an image:

```python
import * as ami from 'cdk-create-ami';
```

```python
const amiImage = new ami.CreateAMI(this, 'amiImage', {
  instanceId: baseInstance.instanceId,
  deleteAmi: true,
  deleteInstance: true,
  blockDeviceMappings: [
    {
      deviceName: '/dev/sdh',
      ebs: {
        volumeSize: 20,
        volumeType: ami.VolumeType.GP3,
        deleteOnTermination: true,
      },
    },
  ],
  tagSpecifications: [
    {
      resourceType: ami.ResourceType.IMAGE,
      tags: [{ key: 'TagKey', value: 'TagValue' }],
    },
  ],
});
```

This will take an already created [Instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Instances.html) and convert it to an AMI. This process involves stopping the Instance and then creating the AMI. Besides typical AMI creation options regarding [block device mappings](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html) and [tags](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Tags.html), the AMI can be created with two options:

```python
      deleteAmi: true,
      deleteInstance: true,
```

* deleteAmi: When the CDK is destroyed, if this is set to `True`, the AMI will be deleted. Otherwise, the AMI will be retained.
* deleteInstance: When the CDK is deployed, if this is set to `True`, the base image will be deleted. Otherwise, the instance will be retained in a `Stopped` state.

## Example

The associated exmaple includes two Stacks that can be created.

* AMIExample - Deploys Instance and creates AMI from Instance
* InstanceExample - Deploys Instance from previously created AMI

### AMI Example

```
cd example
yarn ami
```

This will deploy an Instance and create an AMI from the created Instance.

#### Creating the Instance

```python
const vpc = new VPC(this, 'VPC');
const baseInstance = new BaseInstance(this, 'Instance', {
  vpc: vpc.vpc,
  securityGroup: vpc.securityGroup,
  ec2Role: vpc.ec2Role,
});
```

The example will create a VPC and Instance to be used to create the AMI. This instance contains a [cloud-init script](example/resources/base_install.sh):

```bash
HOMEDIR=/home/ec2-user
yum update -y
yum install net-tools -y
yum install wget -y

TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
LOCAL_HOSTNAME=$( curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/public-hostname )
INSTANCE_ID=$( curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/instance-id )

echo "AMI Hostname: $LOCAL_HOSTNAME" >> /home/ec2-user/config.txt
echo "AMI InstanceId: $INSTANCE_ID" >> /home/ec2-user/config.txt
```

This will result in a file: `/home/ec2-user/config.txt` that contains the base instance information. This file will be retained in the AMI.

```
AMI Hostname: ec2-54-152-127-245.compute-1.amazonaws.com
AMI InstanceId: i-002aeb6cdde92c9b5
```

#### SSM

The AMI information will be stored in AWS Systems Manager - Parameter Store

![SSM](images/SSM.png)

### Instance Example

Once the AMI has been created, that AMI can be used to create a new Instance that has been pre-configured.

```bash
yarn instance imageId=IMAGEID
```

The IMAGEID to be used is provided as output from the AMI Example Stack.

This AMI Image ID is retrieved by the CDK:

```python
const customAmi = new ec2.GenericSSMParameterImage(
  '/createAMI/' + props.imageId,
  ec2.OperatingSystemType.LINUX,
);
```

This AMI Image ID is used to create the new Instance:

```python
const ec2Instance = new ec2.Instance(this, 'Instance', {
  vpc: props.vpc,
  instanceType: ec2.InstanceType.of(
    ec2.InstanceClass.T4G,
    ec2.InstanceSize.MEDIUM,
  ),
  machineImage: customAmi,
  // More Instance configuration here
});
```

This instance contains a [cloud-init script](example/resources/new_install.sh):

```bash
HOMEDIR=/home/ec2-user

TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
LOCAL_HOSTNAME=$( curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/public-hostname )
INSTANCE_ID=$( curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/instance-id )

echo "New Instance Hostname: $LOCAL_HOSTNAME" >> /home/ec2-user/config.txt
echo "New Instance InstanceId: $INSTANCE_ID" >> /home/ec2-user/config.txt
```

Because the Instance used to create the AMI has already updated and installed packages, these do not need to be run again. Instead, the new Instance Hostname and InstanceId will be copied to the existing `/home/ec2-user/config.txt` file.

```text
AMI Hostname: ec2-54-152-127-245.compute-1.amazonaws.com
AMI InstanceId: i-002aeb6cdde92c9b5
New Instance Hostname: ec2-54-242-5-47.compute-1.amazonaws.com
New Instance InstanceId: i-0e67014a77d5d1995
```

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## License

This project is licensed under the Apache-2.0 License.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import constructs


@jsii.data_type(
    jsii_type="cdk-create-ami.BlockDeviceMapping",
    jsii_struct_bases=[],
    name_mapping={
        "device_name": "deviceName",
        "ebs": "ebs",
        "no_device": "noDevice",
        "virtual_name": "virtualName",
    },
)
class BlockDeviceMapping:
    def __init__(
        self,
        *,
        device_name: typing.Optional[builtins.str] = None,
        ebs: typing.Optional[typing.Union["Ebs", typing.Dict[str, typing.Any]]] = None,
        no_device: typing.Optional[builtins.str] = None,
        virtual_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param device_name: 
        :param ebs: 
        :param no_device: 
        :param virtual_name: 
        '''
        if isinstance(ebs, dict):
            ebs = Ebs(**ebs)
        if __debug__:
            type_hints = typing.get_type_hints(BlockDeviceMapping.__init__)
            check_type(argname="argument device_name", value=device_name, expected_type=type_hints["device_name"])
            check_type(argname="argument ebs", value=ebs, expected_type=type_hints["ebs"])
            check_type(argname="argument no_device", value=no_device, expected_type=type_hints["no_device"])
            check_type(argname="argument virtual_name", value=virtual_name, expected_type=type_hints["virtual_name"])
        self._values: typing.Dict[str, typing.Any] = {}
        if device_name is not None:
            self._values["device_name"] = device_name
        if ebs is not None:
            self._values["ebs"] = ebs
        if no_device is not None:
            self._values["no_device"] = no_device
        if virtual_name is not None:
            self._values["virtual_name"] = virtual_name

    @builtins.property
    def device_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("device_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs(self) -> typing.Optional["Ebs"]:
        result = self._values.get("ebs")
        return typing.cast(typing.Optional["Ebs"], result)

    @builtins.property
    def no_device(self) -> typing.Optional[builtins.str]:
        result = self._values.get("no_device")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def virtual_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("virtual_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BlockDeviceMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CreateAMI(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-create-ami.CreateAMI",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        instance_id: builtins.str,
        block_device_mappings: typing.Optional[typing.Sequence[typing.Union[BlockDeviceMapping, typing.Dict[str, typing.Any]]]] = None,
        delete_ami: typing.Optional[builtins.bool] = None,
        delete_instance: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tag_specifications: typing.Optional[typing.Sequence[typing.Union["TagSpecification", typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_id: 
        :param block_device_mappings: 
        :param delete_ami: 
        :param delete_instance: 
        :param description: 
        :param name: 
        :param tag_specifications: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CreateAMI.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CreateAMIProps(
            instance_id=instance_id,
            block_device_mappings=block_device_mappings,
            delete_ami=delete_ami,
            delete_instance=delete_instance,
            description=description,
            name=name,
            tag_specifications=tag_specifications,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageName"))


@jsii.data_type(
    jsii_type="cdk-create-ami.CreateAMIProps",
    jsii_struct_bases=[],
    name_mapping={
        "instance_id": "instanceId",
        "block_device_mappings": "blockDeviceMappings",
        "delete_ami": "deleteAmi",
        "delete_instance": "deleteInstance",
        "description": "description",
        "name": "name",
        "tag_specifications": "tagSpecifications",
    },
)
class CreateAMIProps:
    def __init__(
        self,
        *,
        instance_id: builtins.str,
        block_device_mappings: typing.Optional[typing.Sequence[typing.Union[BlockDeviceMapping, typing.Dict[str, typing.Any]]]] = None,
        delete_ami: typing.Optional[builtins.bool] = None,
        delete_instance: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tag_specifications: typing.Optional[typing.Sequence[typing.Union["TagSpecification", typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param instance_id: 
        :param block_device_mappings: 
        :param delete_ami: 
        :param delete_instance: 
        :param description: 
        :param name: 
        :param tag_specifications: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CreateAMIProps.__init__)
            check_type(argname="argument instance_id", value=instance_id, expected_type=type_hints["instance_id"])
            check_type(argname="argument block_device_mappings", value=block_device_mappings, expected_type=type_hints["block_device_mappings"])
            check_type(argname="argument delete_ami", value=delete_ami, expected_type=type_hints["delete_ami"])
            check_type(argname="argument delete_instance", value=delete_instance, expected_type=type_hints["delete_instance"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument tag_specifications", value=tag_specifications, expected_type=type_hints["tag_specifications"])
        self._values: typing.Dict[str, typing.Any] = {
            "instance_id": instance_id,
        }
        if block_device_mappings is not None:
            self._values["block_device_mappings"] = block_device_mappings
        if delete_ami is not None:
            self._values["delete_ami"] = delete_ami
        if delete_instance is not None:
            self._values["delete_instance"] = delete_instance
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if tag_specifications is not None:
            self._values["tag_specifications"] = tag_specifications

    @builtins.property
    def instance_id(self) -> builtins.str:
        result = self._values.get("instance_id")
        assert result is not None, "Required property 'instance_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def block_device_mappings(self) -> typing.Optional[typing.List[BlockDeviceMapping]]:
        result = self._values.get("block_device_mappings")
        return typing.cast(typing.Optional[typing.List[BlockDeviceMapping]], result)

    @builtins.property
    def delete_ami(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("delete_ami")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def delete_instance(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("delete_instance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_specifications(self) -> typing.Optional[typing.List["TagSpecification"]]:
        result = self._values.get("tag_specifications")
        return typing.cast(typing.Optional[typing.List["TagSpecification"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateAMIProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-create-ami.Ebs",
    jsii_struct_bases=[],
    name_mapping={
        "delete_on_termination": "deleteOnTermination",
        "encrypted": "encrypted",
        "iops": "iops",
        "kms_key_id": "kmsKeyId",
        "outpost_arn": "outpostArn",
        "snapshot_id": "snapshotId",
        "throughput": "throughput",
        "volume_size": "volumeSize",
        "volume_type": "volumeType",
    },
)
class Ebs:
    def __init__(
        self,
        *,
        delete_on_termination: typing.Optional[builtins.bool] = None,
        encrypted: typing.Optional[builtins.bool] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        outpost_arn: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        throughput: typing.Optional[jsii.Number] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional["VolumeType"] = None,
    ) -> None:
        '''
        :param delete_on_termination: 
        :param encrypted: 
        :param iops: 
        :param kms_key_id: 
        :param outpost_arn: 
        :param snapshot_id: 
        :param throughput: 
        :param volume_size: 
        :param volume_type: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Ebs.__init__)
            check_type(argname="argument delete_on_termination", value=delete_on_termination, expected_type=type_hints["delete_on_termination"])
            check_type(argname="argument encrypted", value=encrypted, expected_type=type_hints["encrypted"])
            check_type(argname="argument iops", value=iops, expected_type=type_hints["iops"])
            check_type(argname="argument kms_key_id", value=kms_key_id, expected_type=type_hints["kms_key_id"])
            check_type(argname="argument outpost_arn", value=outpost_arn, expected_type=type_hints["outpost_arn"])
            check_type(argname="argument snapshot_id", value=snapshot_id, expected_type=type_hints["snapshot_id"])
            check_type(argname="argument throughput", value=throughput, expected_type=type_hints["throughput"])
            check_type(argname="argument volume_size", value=volume_size, expected_type=type_hints["volume_size"])
            check_type(argname="argument volume_type", value=volume_type, expected_type=type_hints["volume_type"])
        self._values: typing.Dict[str, typing.Any] = {}
        if delete_on_termination is not None:
            self._values["delete_on_termination"] = delete_on_termination
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if outpost_arn is not None:
            self._values["outpost_arn"] = outpost_arn
        if snapshot_id is not None:
            self._values["snapshot_id"] = snapshot_id
        if throughput is not None:
            self._values["throughput"] = throughput
        if volume_size is not None:
            self._values["volume_size"] = volume_size
        if volume_type is not None:
            self._values["volume_type"] = volume_type

    @builtins.property
    def delete_on_termination(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("delete_on_termination")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encrypted(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def outpost_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("outpost_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def throughput(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_type(self) -> typing.Optional["VolumeType"]:
        result = self._values.get("volume_type")
        return typing.cast(typing.Optional["VolumeType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Ebs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-create-ami.ResourceType")
class ResourceType(enum.Enum):
    IMAGE = "IMAGE"
    SNAPSHOT = "SNAPSHOT"


@jsii.data_type(
    jsii_type="cdk-create-ami.TagSpecification",
    jsii_struct_bases=[],
    name_mapping={"resource_type": "resourceType", "tags": "tags"},
)
class TagSpecification:
    def __init__(
        self,
        *,
        resource_type: typing.Optional[ResourceType] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["Tags", typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param resource_type: 
        :param tags: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TagSpecification.__init__)
            check_type(argname="argument resource_type", value=resource_type, expected_type=type_hints["resource_type"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[str, typing.Any] = {}
        if resource_type is not None:
            self._values["resource_type"] = resource_type
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def resource_type(self) -> typing.Optional[ResourceType]:
        result = self._values.get("resource_type")
        return typing.cast(typing.Optional[ResourceType], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List["Tags"]]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List["Tags"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TagSpecification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-create-ami.Tags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class Tags:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: 
        :param value: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Tags.__init__)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Tags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-create-ami.VolumeType")
class VolumeType(enum.Enum):
    STANDARD = "STANDARD"
    IO1 = "IO1"
    IO2 = "IO2"
    GP2 = "GP2"
    SC1 = "SC1"
    ST1 = "ST1"
    GP3 = "GP3"


__all__ = [
    "BlockDeviceMapping",
    "CreateAMI",
    "CreateAMIProps",
    "Ebs",
    "ResourceType",
    "TagSpecification",
    "Tags",
    "VolumeType",
]

publication.publish()
