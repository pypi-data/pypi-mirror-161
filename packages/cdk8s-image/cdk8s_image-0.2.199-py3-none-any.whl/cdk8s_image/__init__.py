'''
# cdk8s-image

An `Image` construct which takes care of building & pushing docker images that
can be used in [CDK8s](https://github.com/awslabs/cdk8s) apps.

The following example will build the docker image from `Dockerfile` under the
`my-app` directory, push it to a local registry and then define a Kubernetes
deployment that deploys containers that run this image.

```python
const image = new Image(this, 'image', {
  dir: `${__dirname}/my-app`,
  registry: 'localhost:5000'
});

new Deployment(this, 'deployment', {
  containers: [ new Container({ image: image.url }) ],
});
```

## Contributions

All contributions are celebrated.

## License

Licensed under [Apache 2.0](./LICENSE).
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
    jsii_type="cdk8s-image.BuildArg",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class BuildArg:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''Build arg to pass to the docker build.

        :param name: the name of the build arg.
        :param value: the value of the build arg.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(BuildArg.__init__)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''the name of the build arg.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''the value of the build arg.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildArg(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Image(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-image.Image",
):
    '''Represents a docker image built during synthesis from a context directory (``dir``) with a ``Dockerfile``.

    The image will be built using ``docker build`` and then pushed through ``docker push``. The URL of the pushed image can be accessed through ``image.url``.

    If you push to a registry other than docker hub, you can specify the registry
    URL through the ``registry`` option.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        dir: builtins.str,
        build_args: typing.Optional[typing.Sequence[typing.Union[BuildArg, typing.Dict[str, typing.Any]]]] = None,
        file: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
        tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param dir: The docker build context directory (where ``Dockerfile`` is).
        :param build_args: List of build args to pass to the build action.
        :param file: Path to Dockerfile.
        :param name: Name for the image. Docker convention is {registry_name}/{name}:{tag} Visit https://docs.docker.com/engine/reference/commandline/tag/ for more information Default: - auto-generated name
        :param platform: Set to specify the target platform for the build output, (for example, linux/amd64, linux/arm64, or darwin/amd64).
        :param registry: The registry URL to use. This will be used as the prefix for the image name. For example, if you have a local registry listening on port 500, you can set this to ``localhost:5000``. Default: "docker.io/library"
        :param tag: Tag for the image. Docker convention is {registry_name}/{name}:{tag} Visit https://docs.docker.com/engine/reference/commandline/tag/ for more information Default: "latest"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Image.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ImageProps(
            dir=dir,
            build_args=build_args,
            file=file,
            name=name,
            platform=platform,
            registry=registry,
            tag=tag,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''The image URL to use in order to pull this instance of the image.'''
        return typing.cast(builtins.str, jsii.get(self, "url"))


@jsii.data_type(
    jsii_type="cdk8s-image.ImageProps",
    jsii_struct_bases=[],
    name_mapping={
        "dir": "dir",
        "build_args": "buildArgs",
        "file": "file",
        "name": "name",
        "platform": "platform",
        "registry": "registry",
        "tag": "tag",
    },
)
class ImageProps:
    def __init__(
        self,
        *,
        dir: builtins.str,
        build_args: typing.Optional[typing.Sequence[typing.Union[BuildArg, typing.Dict[str, typing.Any]]]] = None,
        file: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
        tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Props for ``Image``.

        :param dir: The docker build context directory (where ``Dockerfile`` is).
        :param build_args: List of build args to pass to the build action.
        :param file: Path to Dockerfile.
        :param name: Name for the image. Docker convention is {registry_name}/{name}:{tag} Visit https://docs.docker.com/engine/reference/commandline/tag/ for more information Default: - auto-generated name
        :param platform: Set to specify the target platform for the build output, (for example, linux/amd64, linux/arm64, or darwin/amd64).
        :param registry: The registry URL to use. This will be used as the prefix for the image name. For example, if you have a local registry listening on port 500, you can set this to ``localhost:5000``. Default: "docker.io/library"
        :param tag: Tag for the image. Docker convention is {registry_name}/{name}:{tag} Visit https://docs.docker.com/engine/reference/commandline/tag/ for more information Default: "latest"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ImageProps.__init__)
            check_type(argname="argument dir", value=dir, expected_type=type_hints["dir"])
            check_type(argname="argument build_args", value=build_args, expected_type=type_hints["build_args"])
            check_type(argname="argument file", value=file, expected_type=type_hints["file"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument platform", value=platform, expected_type=type_hints["platform"])
            check_type(argname="argument registry", value=registry, expected_type=type_hints["registry"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
        self._values: typing.Dict[str, typing.Any] = {
            "dir": dir,
        }
        if build_args is not None:
            self._values["build_args"] = build_args
        if file is not None:
            self._values["file"] = file
        if name is not None:
            self._values["name"] = name
        if platform is not None:
            self._values["platform"] = platform
        if registry is not None:
            self._values["registry"] = registry
        if tag is not None:
            self._values["tag"] = tag

    @builtins.property
    def dir(self) -> builtins.str:
        '''The docker build context directory (where ``Dockerfile`` is).'''
        result = self._values.get("dir")
        assert result is not None, "Required property 'dir' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_args(self) -> typing.Optional[typing.List[BuildArg]]:
        '''List of build args to pass to the build action.'''
        result = self._values.get("build_args")
        return typing.cast(typing.Optional[typing.List[BuildArg]], result)

    @builtins.property
    def file(self) -> typing.Optional[builtins.str]:
        '''Path to Dockerfile.'''
        result = self._values.get("file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name for the image.

        Docker convention is {registry_name}/{name}:{tag}
        Visit https://docs.docker.com/engine/reference/commandline/tag/ for more information

        :default: - auto-generated name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def platform(self) -> typing.Optional[builtins.str]:
        '''Set to specify the target platform for the build output, (for example, linux/amd64, linux/arm64, or darwin/amd64).'''
        result = self._values.get("platform")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry(self) -> typing.Optional[builtins.str]:
        '''The registry URL to use.

        This will be used as the prefix for the image name.

        For example, if you have a local registry listening on port 500, you can set this to ``localhost:5000``.

        :default: "docker.io/library"
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag(self) -> typing.Optional[builtins.str]:
        '''Tag for the image.

        Docker convention is {registry_name}/{name}:{tag}
        Visit https://docs.docker.com/engine/reference/commandline/tag/ for more information

        :default: "latest"
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BuildArg",
    "Image",
    "ImageProps",
]

publication.publish()
