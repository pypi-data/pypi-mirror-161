'''
# Terraform CDK archive Provider ~> 2.2

This repo builds and publishes the Terraform archive Provider bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-archive](https://www.npmjs.com/package/@cdktf/provider-archive).

`npm install @cdktf/provider-archive`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-archive](https://pypi.org/project/cdktf-cdktf-provider-archive).

`pipenv install cdktf-cdktf-provider-archive`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Archive](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Archive).

`dotnet add package HashiCorp.Cdktf.Providers.Archive`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-archive](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-archive).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-archive</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/hashicorp/cdktf-provider-archive-go`](https://github.com/hashicorp/cdktf-provider-archive-go) package.

`go get github.com/hashicorp/cdktf-provider-archive-go/archive`

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)
You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-archive).

## Versioning

This project is explicitly not tracking the Terraform archive Provider version 1:1. In fact, it always tracks `latest` of `~> 2.2` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform archive Provider](https://github.com/terraform-providers/terraform-provider-archive)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [terraform cdk](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### projen

This is mostly based on [projen](https://github.com/eladb/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on projen

There's a custom [project builder](https://github.com/hashicorp/cdktf-provider-project) which encapsulate the common settings for all `cdktf` providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [Repository Manager](https://github.com/hashicorp/cdktf-repository-manager/)
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

import cdktf
import constructs


class ArchiveProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-archive.ArchiveProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/archive archive}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/archive archive} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive#alias ArchiveProvider#alias}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ArchiveProvider.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ArchiveProviderConfig(alias=alias)

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(ArchiveProvider, "alias").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-archive.ArchiveProviderConfig",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias"},
)
class ArchiveProviderConfig:
    def __init__(self, *, alias: typing.Optional[builtins.str] = None) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive#alias ArchiveProvider#alias}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ArchiveProviderConfig.__init__)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive#alias ArchiveProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ArchiveProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataArchiveFile(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-archive.DataArchiveFile",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/archive/d/file archive_file}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        output_path: builtins.str,
        type: builtins.str,
        excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        output_file_mode: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["DataArchiveFileSource", typing.Dict[str, typing.Any]]]]] = None,
        source_content: typing.Optional[builtins.str] = None,
        source_content_filename: typing.Optional[builtins.str] = None,
        source_dir: typing.Optional[builtins.str] = None,
        source_file: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/archive/d/file archive_file} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param output_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_path DataArchiveFile#output_path}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#type DataArchiveFile#type}.
        :param excludes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#excludes DataArchiveFile#excludes}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#id DataArchiveFile#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param output_file_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_file_mode DataArchiveFile#output_file_mode}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source DataArchiveFile#source}
        :param source_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content DataArchiveFile#source_content}.
        :param source_content_filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content_filename DataArchiveFile#source_content_filename}.
        :param source_dir: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_dir DataArchiveFile#source_dir}.
        :param source_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_file DataArchiveFile#source_file}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataArchiveFile.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataArchiveFileConfig(
            output_path=output_path,
            type=type,
            excludes=excludes,
            id=id,
            output_file_mode=output_file_mode,
            source=source,
            source_content=source_content,
            source_content_filename=source_content_filename,
            source_dir=source_dir,
            source_file=source_file,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putSource")
    def put_source(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["DataArchiveFileSource", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataArchiveFile.put_source)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="resetExcludes")
    def reset_excludes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludes", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOutputFileMode")
    def reset_output_file_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputFileMode", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetSourceContent")
    def reset_source_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceContent", []))

    @jsii.member(jsii_name="resetSourceContentFilename")
    def reset_source_content_filename(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceContentFilename", []))

    @jsii.member(jsii_name="resetSourceDir")
    def reset_source_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceDir", []))

    @jsii.member(jsii_name="resetSourceFile")
    def reset_source_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFile", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputBase64Sha256")
    def output_base64_sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputBase64Sha256"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputMd5")
    def output_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputMd5"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputSha")
    def output_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputSize")
    def output_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "outputSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> "DataArchiveFileSourceList":
        return typing.cast("DataArchiveFileSourceList", jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludesInput")
    def excludes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFileModeInput")
    def output_file_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputFileModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputPathInput")
    def output_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentFilenameInput")
    def source_content_filename_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceContentFilenameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentInput")
    def source_content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceContentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDirInput")
    def source_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceDirInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileInput")
    def source_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataArchiveFileSource"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataArchiveFileSource"]]], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludes")
    def excludes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludes"))

    @excludes.setter
    def excludes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFile, "excludes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFile, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFileMode")
    def output_file_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputFileMode"))

    @output_file_mode.setter
    def output_file_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFile, "output_file_mode").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputFileMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputPath")
    def output_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputPath"))

    @output_path.setter
    def output_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFile, "output_path").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContent")
    def source_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceContent"))

    @source_content.setter
    def source_content(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFile, "source_content").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceContent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentFilename")
    def source_content_filename(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceContentFilename"))

    @source_content_filename.setter
    def source_content_filename(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFile, "source_content_filename").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceContentFilename", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDir")
    def source_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceDir"))

    @source_dir.setter
    def source_dir(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFile, "source_dir").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceDir", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFile")
    def source_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFile"))

    @source_file.setter
    def source_file(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFile, "source_file").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFile, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-archive.DataArchiveFileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "output_path": "outputPath",
        "type": "type",
        "excludes": "excludes",
        "id": "id",
        "output_file_mode": "outputFileMode",
        "source": "source",
        "source_content": "sourceContent",
        "source_content_filename": "sourceContentFilename",
        "source_dir": "sourceDir",
        "source_file": "sourceFile",
    },
)
class DataArchiveFileConfig(cdktf.TerraformMetaArguments):
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
        output_path: builtins.str,
        type: builtins.str,
        excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        output_file_mode: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["DataArchiveFileSource", typing.Dict[str, typing.Any]]]]] = None,
        source_content: typing.Optional[builtins.str] = None,
        source_content_filename: typing.Optional[builtins.str] = None,
        source_dir: typing.Optional[builtins.str] = None,
        source_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param output_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_path DataArchiveFile#output_path}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#type DataArchiveFile#type}.
        :param excludes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#excludes DataArchiveFile#excludes}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#id DataArchiveFile#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param output_file_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_file_mode DataArchiveFile#output_file_mode}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source DataArchiveFile#source}
        :param source_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content DataArchiveFile#source_content}.
        :param source_content_filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content_filename DataArchiveFile#source_content_filename}.
        :param source_dir: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_dir DataArchiveFile#source_dir}.
        :param source_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_file DataArchiveFile#source_file}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(DataArchiveFileConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument excludes", value=excludes, expected_type=type_hints["excludes"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument output_file_mode", value=output_file_mode, expected_type=type_hints["output_file_mode"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument source_content", value=source_content, expected_type=type_hints["source_content"])
            check_type(argname="argument source_content_filename", value=source_content_filename, expected_type=type_hints["source_content_filename"])
            check_type(argname="argument source_dir", value=source_dir, expected_type=type_hints["source_dir"])
            check_type(argname="argument source_file", value=source_file, expected_type=type_hints["source_file"])
        self._values: typing.Dict[str, typing.Any] = {
            "output_path": output_path,
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
        if excludes is not None:
            self._values["excludes"] = excludes
        if id is not None:
            self._values["id"] = id
        if output_file_mode is not None:
            self._values["output_file_mode"] = output_file_mode
        if source is not None:
            self._values["source"] = source
        if source_content is not None:
            self._values["source_content"] = source_content
        if source_content_filename is not None:
            self._values["source_content_filename"] = source_content_filename
        if source_dir is not None:
            self._values["source_dir"] = source_dir
        if source_file is not None:
            self._values["source_file"] = source_file

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
    def output_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_path DataArchiveFile#output_path}.'''
        result = self._values.get("output_path")
        assert result is not None, "Required property 'output_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#type DataArchiveFile#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def excludes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#excludes DataArchiveFile#excludes}.'''
        result = self._values.get("excludes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#id DataArchiveFile#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_file_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_file_mode DataArchiveFile#output_file_mode}.'''
        result = self._values.get("output_file_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataArchiveFileSource"]]]:
        '''source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source DataArchiveFile#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataArchiveFileSource"]]], result)

    @builtins.property
    def source_content(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content DataArchiveFile#source_content}.'''
        result = self._values.get("source_content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_content_filename(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content_filename DataArchiveFile#source_content_filename}.'''
        result = self._values.get("source_content_filename")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_dir(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_dir DataArchiveFile#source_dir}.'''
        result = self._values.get("source_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_file DataArchiveFile#source_file}.'''
        result = self._values.get("source_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataArchiveFileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-archive.DataArchiveFileSource",
    jsii_struct_bases=[],
    name_mapping={"content": "content", "filename": "filename"},
)
class DataArchiveFileSource:
    def __init__(self, *, content: builtins.str, filename: builtins.str) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#content DataArchiveFile#content}.
        :param filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#filename DataArchiveFile#filename}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataArchiveFileSource.__init__)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument filename", value=filename, expected_type=type_hints["filename"])
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "filename": filename,
        }

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#content DataArchiveFile#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filename(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#filename DataArchiveFile#filename}.'''
        result = self._values.get("filename")
        assert result is not None, "Required property 'filename' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataArchiveFileSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataArchiveFileSourceList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-archive.DataArchiveFileSourceList",
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
            type_hints = typing.get_type_hints(DataArchiveFileSourceList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataArchiveFileSourceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DataArchiveFileSourceList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataArchiveFileSourceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFileSourceList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(DataArchiveFileSourceList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(DataArchiveFileSourceList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataArchiveFileSource]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataArchiveFileSource]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataArchiveFileSource]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFileSourceList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataArchiveFileSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-archive.DataArchiveFileSourceOutputReference",
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
            type_hints = typing.get_type_hints(DataArchiveFileSourceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentInput")
    def content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filenameInput")
    def filename_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filenameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @content.setter
    def content(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFileSourceOutputReference, "content").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "content", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filename")
    def filename(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filename"))

    @filename.setter
    def filename(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFileSourceOutputReference, "filename").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "filename", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, DataArchiveFileSource]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, DataArchiveFileSource]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, DataArchiveFileSource]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(DataArchiveFileSourceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class File(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-archive.File",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/archive/r/file archive_file}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        output_path: builtins.str,
        type: builtins.str,
        excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        output_file_mode: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Union[typing.Sequence[typing.Union["FileSource", typing.Dict[str, typing.Any]]], cdktf.IResolvable]] = None,
        source_content: typing.Optional[builtins.str] = None,
        source_content_filename: typing.Optional[builtins.str] = None,
        source_dir: typing.Optional[builtins.str] = None,
        source_file: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/archive/r/file archive_file} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param output_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_path File#output_path}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#type File#type}.
        :param excludes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#excludes File#excludes}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#id File#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param output_file_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_file_mode File#output_file_mode}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source File#source}
        :param source_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content File#source_content}.
        :param source_content_filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content_filename File#source_content_filename}.
        :param source_dir: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_dir File#source_dir}.
        :param source_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_file File#source_file}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(File.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = FileConfig(
            output_path=output_path,
            type=type,
            excludes=excludes,
            id=id,
            output_file_mode=output_file_mode,
            source=source,
            source_content=source_content,
            source_content_filename=source_content_filename,
            source_dir=source_dir,
            source_file=source_file,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putSource")
    def put_source(
        self,
        value: typing.Union[typing.Sequence[typing.Union["FileSource", typing.Dict[str, typing.Any]]], cdktf.IResolvable],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(File.put_source)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="resetExcludes")
    def reset_excludes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludes", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOutputFileMode")
    def reset_output_file_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputFileMode", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetSourceContent")
    def reset_source_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceContent", []))

    @jsii.member(jsii_name="resetSourceContentFilename")
    def reset_source_content_filename(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceContentFilename", []))

    @jsii.member(jsii_name="resetSourceDir")
    def reset_source_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceDir", []))

    @jsii.member(jsii_name="resetSourceFile")
    def reset_source_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFile", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputBase64Sha256")
    def output_base64_sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputBase64Sha256"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputMd5")
    def output_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputMd5"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputSha")
    def output_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputSize")
    def output_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "outputSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> "FileSourceList":
        return typing.cast("FileSourceList", jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludesInput")
    def excludes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFileModeInput")
    def output_file_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputFileModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputPathInput")
    def output_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentFilenameInput")
    def source_content_filename_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceContentFilenameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentInput")
    def source_content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceContentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDirInput")
    def source_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceDirInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileInput")
    def source_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(
        self,
    ) -> typing.Optional[typing.Union[typing.List["FileSource"], cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[typing.List["FileSource"], cdktf.IResolvable]], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludes")
    def excludes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludes"))

    @excludes.setter
    def excludes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(File, "excludes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(File, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFileMode")
    def output_file_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputFileMode"))

    @output_file_mode.setter
    def output_file_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(File, "output_file_mode").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputFileMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputPath")
    def output_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputPath"))

    @output_path.setter
    def output_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(File, "output_path").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContent")
    def source_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceContent"))

    @source_content.setter
    def source_content(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(File, "source_content").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceContent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentFilename")
    def source_content_filename(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceContentFilename"))

    @source_content_filename.setter
    def source_content_filename(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(File, "source_content_filename").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceContentFilename", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDir")
    def source_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceDir"))

    @source_dir.setter
    def source_dir(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(File, "source_dir").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceDir", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFile")
    def source_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFile"))

    @source_file.setter
    def source_file(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(File, "source_file").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(File, "type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-archive.FileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "output_path": "outputPath",
        "type": "type",
        "excludes": "excludes",
        "id": "id",
        "output_file_mode": "outputFileMode",
        "source": "source",
        "source_content": "sourceContent",
        "source_content_filename": "sourceContentFilename",
        "source_dir": "sourceDir",
        "source_file": "sourceFile",
    },
)
class FileConfig(cdktf.TerraformMetaArguments):
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
        output_path: builtins.str,
        type: builtins.str,
        excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        output_file_mode: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Union[typing.Sequence[typing.Union["FileSource", typing.Dict[str, typing.Any]]], cdktf.IResolvable]] = None,
        source_content: typing.Optional[builtins.str] = None,
        source_content_filename: typing.Optional[builtins.str] = None,
        source_dir: typing.Optional[builtins.str] = None,
        source_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param output_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_path File#output_path}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#type File#type}.
        :param excludes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#excludes File#excludes}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#id File#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param output_file_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_file_mode File#output_file_mode}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source File#source}
        :param source_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content File#source_content}.
        :param source_content_filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content_filename File#source_content_filename}.
        :param source_dir: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_dir File#source_dir}.
        :param source_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_file File#source_file}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(FileConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument excludes", value=excludes, expected_type=type_hints["excludes"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument output_file_mode", value=output_file_mode, expected_type=type_hints["output_file_mode"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument source_content", value=source_content, expected_type=type_hints["source_content"])
            check_type(argname="argument source_content_filename", value=source_content_filename, expected_type=type_hints["source_content_filename"])
            check_type(argname="argument source_dir", value=source_dir, expected_type=type_hints["source_dir"])
            check_type(argname="argument source_file", value=source_file, expected_type=type_hints["source_file"])
        self._values: typing.Dict[str, typing.Any] = {
            "output_path": output_path,
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
        if excludes is not None:
            self._values["excludes"] = excludes
        if id is not None:
            self._values["id"] = id
        if output_file_mode is not None:
            self._values["output_file_mode"] = output_file_mode
        if source is not None:
            self._values["source"] = source
        if source_content is not None:
            self._values["source_content"] = source_content
        if source_content_filename is not None:
            self._values["source_content_filename"] = source_content_filename
        if source_dir is not None:
            self._values["source_dir"] = source_dir
        if source_file is not None:
            self._values["source_file"] = source_file

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
    def output_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_path File#output_path}.'''
        result = self._values.get("output_path")
        assert result is not None, "Required property 'output_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#type File#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def excludes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#excludes File#excludes}.'''
        result = self._values.get("excludes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#id File#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_file_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_file_mode File#output_file_mode}.'''
        result = self._values.get("output_file_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(
        self,
    ) -> typing.Optional[typing.Union[typing.List["FileSource"], cdktf.IResolvable]]:
        '''source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source File#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[typing.Union[typing.List["FileSource"], cdktf.IResolvable]], result)

    @builtins.property
    def source_content(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content File#source_content}.'''
        result = self._values.get("source_content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_content_filename(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content_filename File#source_content_filename}.'''
        result = self._values.get("source_content_filename")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_dir(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_dir File#source_dir}.'''
        result = self._values.get("source_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_file File#source_file}.'''
        result = self._values.get("source_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-archive.FileSource",
    jsii_struct_bases=[],
    name_mapping={"content": "content", "filename": "filename"},
)
class FileSource:
    def __init__(self, *, content: builtins.str, filename: builtins.str) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#content File#content}.
        :param filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#filename File#filename}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(FileSource.__init__)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument filename", value=filename, expected_type=type_hints["filename"])
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "filename": filename,
        }

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#content File#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filename(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#filename File#filename}.'''
        result = self._values.get("filename")
        assert result is not None, "Required property 'filename' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FileSourceList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-archive.FileSourceList",
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
            type_hints = typing.get_type_hints(FileSourceList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "FileSourceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(FileSourceList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("FileSourceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(FileSourceList, "_terraform_attribute").fset)
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
            type_hints = typing.get_type_hints(getattr(FileSourceList, "_terraform_resource").fset)
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
            type_hints = typing.get_type_hints(getattr(FileSourceList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[typing.List[FileSource], cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[typing.List[FileSource], cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[typing.List[FileSource], cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(FileSourceList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class FileSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-archive.FileSourceOutputReference",
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
            type_hints = typing.get_type_hints(FileSourceOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentInput")
    def content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filenameInput")
    def filename_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filenameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @content.setter
    def content(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(FileSourceOutputReference, "content").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "content", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filename")
    def filename(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filename"))

    @filename.setter
    def filename(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(FileSourceOutputReference, "filename").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "filename", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[FileSource, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[FileSource, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[FileSource, cdktf.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(FileSourceOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "ArchiveProvider",
    "ArchiveProviderConfig",
    "DataArchiveFile",
    "DataArchiveFileConfig",
    "DataArchiveFileSource",
    "DataArchiveFileSourceList",
    "DataArchiveFileSourceOutputReference",
    "File",
    "FileConfig",
    "FileSource",
    "FileSourceList",
    "FileSourceOutputReference",
]

publication.publish()
