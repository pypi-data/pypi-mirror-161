'''
[![GitHub](https://img.shields.io/github/license/pepperize/cdk-dynamodb-backup?style=flat-square)](https://github.com/pepperize/cdk-dynamodb-backup/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@pepperize/cdk-dynamodb-backup?style=flat-square)](https://www.npmjs.com/package/@pepperize/cdk-dynamodb-backup)
[![PyPI](https://img.shields.io/pypi/v/pepperize.cdk-dynamodb-backup?style=flat-square)](https://pypi.org/project/pepperize.cdk-dynamodb-backup/)
[![Nuget](https://img.shields.io/nuget/v/Pepperize.CDK.DynamodbBackup?style=flat-square)](https://www.nuget.org/packages/Pepperize.CDK.DynamodbBackup/)
[![Sonatype Nexus (Releases)](https://img.shields.io/nexus/r/com.pepperize/cdk-dynamodb-backup?server=https%3A%2F%2Fs01.oss.sonatype.org%2F&style=flat-square)](https://s01.oss.sonatype.org/content/repositories/releases/com/pepperize/cdk-dynamodb-backup/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pepperize/cdk-dynamodb-backup/release/main?label=release&style=flat-square)](https://github.com/pepperize/cdk-dynamodb-backup/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/pepperize/cdk-dynamodb-backup?sort=semver&style=flat-square)](https://github.com/pepperize/cdk-dynamodb-backup/releases)
[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod&style=flat-square)](https://gitpod.io/#https://github.com/pepperize/cdk-dynamodb-backup)

# CDK DynamoDB Backup & Restore

Backup and restore AWS DynamoDB Table with AWS Data Pipeline.

## Install

### TypeScript

```shell
npm install @pepperize/cdk-dynamodb-backup
```

or

```shell
yarn add @pepperize/cdk-dynamodb-backup
```

### Python

```shell
pip install pepperize.cdk-dynamodb-backup
```

### C# / .Net

```
dotnet add package Pepperize.CDK.DynamodbBackup
```

### Java

```xml
<dependency>
  <groupId>com.pepperize</groupId>
  <artifactId>cdk-dynamodb-backup</artifactId>
  <version>${cdkDynamodbBackup.version}</version>
</dependency>
```

## Usage

See [API.md](https://github.com/pepperize/cdk-dynamodb-backup/blob/main/API.md).

### Backup

Export data from AWS DynamoDB to AWS S3

```python
const table = new aws_dynamodb.Table(stack, "Table", {
  partitionKey: { name: "id", type: dynamodb.AttributeType.STRING },
});
const bucket = new aws_s3.Bucket(stack, "Bucket", {});

// When
new DataPipelineBackup(stack, "Account", {
  table: table,
  backupBucket: bucket,
});
```

See [Exporting Data From DynamoDB to Amazon S3](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBPipeline.html#DataPipelineExportImport.Exporting)

### Restore

Import data from AWS S3 into AWS DynamoDB

```python
const table = new aws_dynamodb.Table(stack, "Table", {
  partitionKey: { name: "id", type: dynamodb.AttributeType.STRING },
});
const bucket = new aws_s3.Bucket(stack, "Bucket", {});

// When
new DataPipelineRestore(stack, "Restore", {
  table: table,
  restoreBucket: bucket,
  restoreFolder: "/prefix/to/folder/with/manifest",
});
```

See [Importing Data From Amazon S3 to DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBPipeline.html#DataPipelineExportImport.Importing)
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

import aws_cdk
import aws_cdk.aws_dynamodb
import aws_cdk.aws_iam
import aws_cdk.aws_s3
import constructs


@jsii.implements(aws_cdk.ITaggable)
class DataPipelineBackup(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-dynamodb-backup.DataPipelineBackup",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        backup_bucket: aws_cdk.aws_s3.IBucket,
        table: aws_cdk.aws_dynamodb.ITable,
        dynamo_db_throughput_ratio: typing.Optional[jsii.Number] = None,
        logs_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param backup_bucket: 
        :param table: 
        :param dynamo_db_throughput_ratio: 
        :param logs_bucket: 
        :param pipeline_name: 
        :param schedule: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataPipelineBackup.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataPipelineBackupProps(
            backup_bucket=backup_bucket,
            table=table,
            dynamo_db_throughput_ratio=dynamo_db_throughput_ratio,
            logs_bucket=logs_bucket,
            pipeline_name=pipeline_name,
            schedule=schedule,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(self) -> aws_cdk.aws_iam.CfnInstanceProfile:
        '''The instance profile of the emr cluster resources.'''
        return typing.cast(aws_cdk.aws_iam.CfnInstanceProfile, jsii.get(self, "instanceProfile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceRole")
    def resource_role(self) -> aws_cdk.aws_iam.IRole:
        '''The role used by the emr cluster resources.'''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "resourceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        '''The role used by datapipelines service.'''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.TagManager:
        '''TagManager to set, remove and format tags.'''
        return typing.cast(aws_cdk.TagManager, jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-dynamodb-backup.DataPipelineBackupOptions",
    jsii_struct_bases=[],
    name_mapping={
        "dynamo_db_throughput_ratio": "dynamoDbThroughputRatio",
        "logs_bucket": "logsBucket",
        "pipeline_name": "pipelineName",
        "schedule": "schedule",
    },
)
class DataPipelineBackupOptions:
    def __init__(
        self,
        *,
        dynamo_db_throughput_ratio: typing.Optional[jsii.Number] = None,
        logs_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param dynamo_db_throughput_ratio: 
        :param logs_bucket: 
        :param pipeline_name: 
        :param schedule: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataPipelineBackupOptions.__init__)
            check_type(argname="argument dynamo_db_throughput_ratio", value=dynamo_db_throughput_ratio, expected_type=type_hints["dynamo_db_throughput_ratio"])
            check_type(argname="argument logs_bucket", value=logs_bucket, expected_type=type_hints["logs_bucket"])
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        self._values: typing.Dict[str, typing.Any] = {}
        if dynamo_db_throughput_ratio is not None:
            self._values["dynamo_db_throughput_ratio"] = dynamo_db_throughput_ratio
        if logs_bucket is not None:
            self._values["logs_bucket"] = logs_bucket
        if pipeline_name is not None:
            self._values["pipeline_name"] = pipeline_name
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def dynamo_db_throughput_ratio(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("dynamo_db_throughput_ratio")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def logs_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        result = self._values.get("logs_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def pipeline_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("pipeline_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schedule(self) -> typing.Optional[aws_cdk.Duration]:
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPipelineBackupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-dynamodb-backup.DataPipelineBackupProps",
    jsii_struct_bases=[DataPipelineBackupOptions],
    name_mapping={
        "dynamo_db_throughput_ratio": "dynamoDbThroughputRatio",
        "logs_bucket": "logsBucket",
        "pipeline_name": "pipelineName",
        "schedule": "schedule",
        "backup_bucket": "backupBucket",
        "table": "table",
    },
)
class DataPipelineBackupProps(DataPipelineBackupOptions):
    def __init__(
        self,
        *,
        dynamo_db_throughput_ratio: typing.Optional[jsii.Number] = None,
        logs_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[aws_cdk.Duration] = None,
        backup_bucket: aws_cdk.aws_s3.IBucket,
        table: aws_cdk.aws_dynamodb.ITable,
    ) -> None:
        '''
        :param dynamo_db_throughput_ratio: 
        :param logs_bucket: 
        :param pipeline_name: 
        :param schedule: 
        :param backup_bucket: 
        :param table: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataPipelineBackupProps.__init__)
            check_type(argname="argument dynamo_db_throughput_ratio", value=dynamo_db_throughput_ratio, expected_type=type_hints["dynamo_db_throughput_ratio"])
            check_type(argname="argument logs_bucket", value=logs_bucket, expected_type=type_hints["logs_bucket"])
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument backup_bucket", value=backup_bucket, expected_type=type_hints["backup_bucket"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
        self._values: typing.Dict[str, typing.Any] = {
            "backup_bucket": backup_bucket,
            "table": table,
        }
        if dynamo_db_throughput_ratio is not None:
            self._values["dynamo_db_throughput_ratio"] = dynamo_db_throughput_ratio
        if logs_bucket is not None:
            self._values["logs_bucket"] = logs_bucket
        if pipeline_name is not None:
            self._values["pipeline_name"] = pipeline_name
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def dynamo_db_throughput_ratio(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("dynamo_db_throughput_ratio")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def logs_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        result = self._values.get("logs_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def pipeline_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("pipeline_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schedule(self) -> typing.Optional[aws_cdk.Duration]:
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def backup_bucket(self) -> aws_cdk.aws_s3.IBucket:
        result = self._values.get("backup_bucket")
        assert result is not None, "Required property 'backup_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(aws_cdk.aws_dynamodb.ITable, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPipelineBackupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.ITaggable)
class DataPipelineRestore(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-dynamodb-backup.DataPipelineRestore",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        restore_bucket: aws_cdk.aws_s3.IBucket,
        restore_folder: builtins.str,
        table: aws_cdk.aws_dynamodb.ITable,
        dynamo_db_throughput_ratio: typing.Optional[jsii.Number] = None,
        logs_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param restore_bucket: 
        :param restore_folder: 
        :param table: 
        :param dynamo_db_throughput_ratio: 
        :param logs_bucket: 
        :param pipeline_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataPipelineRestore.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataPipelineRestoreProps(
            restore_bucket=restore_bucket,
            restore_folder=restore_folder,
            table=table,
            dynamo_db_throughput_ratio=dynamo_db_throughput_ratio,
            logs_bucket=logs_bucket,
            pipeline_name=pipeline_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(self) -> aws_cdk.aws_iam.CfnInstanceProfile:
        '''The instance profile of the emr cluster resources.'''
        return typing.cast(aws_cdk.aws_iam.CfnInstanceProfile, jsii.get(self, "instanceProfile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceRole")
    def resource_role(self) -> aws_cdk.aws_iam.IRole:
        '''The role used by the emr cluster resources.'''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "resourceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        '''The role used by datapipelines service.'''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.TagManager:
        '''TagManager to set, remove and format tags.'''
        return typing.cast(aws_cdk.TagManager, jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-dynamodb-backup.DataPipelineRestoreOptions",
    jsii_struct_bases=[],
    name_mapping={
        "dynamo_db_throughput_ratio": "dynamoDbThroughputRatio",
        "logs_bucket": "logsBucket",
        "pipeline_name": "pipelineName",
    },
)
class DataPipelineRestoreOptions:
    def __init__(
        self,
        *,
        dynamo_db_throughput_ratio: typing.Optional[jsii.Number] = None,
        logs_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dynamo_db_throughput_ratio: 
        :param logs_bucket: 
        :param pipeline_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataPipelineRestoreOptions.__init__)
            check_type(argname="argument dynamo_db_throughput_ratio", value=dynamo_db_throughput_ratio, expected_type=type_hints["dynamo_db_throughput_ratio"])
            check_type(argname="argument logs_bucket", value=logs_bucket, expected_type=type_hints["logs_bucket"])
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
        self._values: typing.Dict[str, typing.Any] = {}
        if dynamo_db_throughput_ratio is not None:
            self._values["dynamo_db_throughput_ratio"] = dynamo_db_throughput_ratio
        if logs_bucket is not None:
            self._values["logs_bucket"] = logs_bucket
        if pipeline_name is not None:
            self._values["pipeline_name"] = pipeline_name

    @builtins.property
    def dynamo_db_throughput_ratio(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("dynamo_db_throughput_ratio")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def logs_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        result = self._values.get("logs_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def pipeline_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("pipeline_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPipelineRestoreOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-dynamodb-backup.DataPipelineRestoreProps",
    jsii_struct_bases=[DataPipelineRestoreOptions],
    name_mapping={
        "dynamo_db_throughput_ratio": "dynamoDbThroughputRatio",
        "logs_bucket": "logsBucket",
        "pipeline_name": "pipelineName",
        "restore_bucket": "restoreBucket",
        "restore_folder": "restoreFolder",
        "table": "table",
    },
)
class DataPipelineRestoreProps(DataPipelineRestoreOptions):
    def __init__(
        self,
        *,
        dynamo_db_throughput_ratio: typing.Optional[jsii.Number] = None,
        logs_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        restore_bucket: aws_cdk.aws_s3.IBucket,
        restore_folder: builtins.str,
        table: aws_cdk.aws_dynamodb.ITable,
    ) -> None:
        '''
        :param dynamo_db_throughput_ratio: 
        :param logs_bucket: 
        :param pipeline_name: 
        :param restore_bucket: 
        :param restore_folder: 
        :param table: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataPipelineRestoreProps.__init__)
            check_type(argname="argument dynamo_db_throughput_ratio", value=dynamo_db_throughput_ratio, expected_type=type_hints["dynamo_db_throughput_ratio"])
            check_type(argname="argument logs_bucket", value=logs_bucket, expected_type=type_hints["logs_bucket"])
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
            check_type(argname="argument restore_bucket", value=restore_bucket, expected_type=type_hints["restore_bucket"])
            check_type(argname="argument restore_folder", value=restore_folder, expected_type=type_hints["restore_folder"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
        self._values: typing.Dict[str, typing.Any] = {
            "restore_bucket": restore_bucket,
            "restore_folder": restore_folder,
            "table": table,
        }
        if dynamo_db_throughput_ratio is not None:
            self._values["dynamo_db_throughput_ratio"] = dynamo_db_throughput_ratio
        if logs_bucket is not None:
            self._values["logs_bucket"] = logs_bucket
        if pipeline_name is not None:
            self._values["pipeline_name"] = pipeline_name

    @builtins.property
    def dynamo_db_throughput_ratio(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("dynamo_db_throughput_ratio")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def logs_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        result = self._values.get("logs_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def pipeline_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("pipeline_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restore_bucket(self) -> aws_cdk.aws_s3.IBucket:
        result = self._values.get("restore_bucket")
        assert result is not None, "Required property 'restore_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def restore_folder(self) -> builtins.str:
        result = self._values.get("restore_folder")
        assert result is not None, "Required property 'restore_folder' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(aws_cdk.aws_dynamodb.ITable, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPipelineRestoreProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataPipelineBackup",
    "DataPipelineBackupOptions",
    "DataPipelineBackupProps",
    "DataPipelineRestore",
    "DataPipelineRestoreOptions",
    "DataPipelineRestoreProps",
]

publication.publish()
