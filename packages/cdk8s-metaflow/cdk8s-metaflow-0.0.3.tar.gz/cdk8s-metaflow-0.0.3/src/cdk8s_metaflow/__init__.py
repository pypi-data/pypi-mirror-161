'''
# cdk8s-metaflow

Collection of cdk8s constructs for deploying [Metaflow](https://metaflow.org) on Kubernetes.

### Imports

```shell
cdk8s import k8s@1.22.0 -l typescript -o src/imports
cdk8s import github:minio/operator@4.4.22 -l typescript -o src/imports
```
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
from .k8s import (
    Affinity as _Affinity_9d28a7c5,
    EnvFromSource as _EnvFromSource_2b00ef0f,
    IngressTls as _IngressTls_e4c411c9,
    SecurityContext as _SecurityContext_bd8348aa,
    Toleration as _Toleration_0b6f63dc,
)


@jsii.data_type(
    jsii_type="cdk8s-metaflow.AutoscalingOptions",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "max_replicas": "maxReplicas",
        "min_replicas": "minReplicas",
        "target_cpu_utilization_percentage": "targetCPUUtilizationPercentage",
    },
)
class AutoscalingOptions:
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        max_replicas: typing.Optional[jsii.Number] = None,
        min_replicas: typing.Optional[jsii.Number] = None,
        target_cpu_utilization_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: 
        :param max_replicas: 
        :param min_replicas: 
        :param target_cpu_utilization_percentage: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AutoscalingOptions.__init__)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument max_replicas", value=max_replicas, expected_type=type_hints["max_replicas"])
            check_type(argname="argument min_replicas", value=min_replicas, expected_type=type_hints["min_replicas"])
            check_type(argname="argument target_cpu_utilization_percentage", value=target_cpu_utilization_percentage, expected_type=type_hints["target_cpu_utilization_percentage"])
        self._values: typing.Dict[str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if max_replicas is not None:
            self._values["max_replicas"] = max_replicas
        if min_replicas is not None:
            self._values["min_replicas"] = min_replicas
        if target_cpu_utilization_percentage is not None:
            self._values["target_cpu_utilization_percentage"] = target_cpu_utilization_percentage

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def max_replicas(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_replicas(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("min_replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_cpu_utilization_percentage(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("target_cpu_utilization_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.DatabaseAuthOptions",
    jsii_struct_bases=[],
    name_mapping={
        "database": "database",
        "enable_postgres_user": "enablePostgresUser",
        "password": "password",
        "postgres_password": "postgresPassword",
        "replication_password": "replicationPassword",
        "replication_username": "replicationUsername",
        "username": "username",
    },
)
class DatabaseAuthOptions:
    def __init__(
        self,
        *,
        database: typing.Optional[builtins.str] = None,
        enable_postgres_user: typing.Optional[builtins.bool] = None,
        password: typing.Optional[builtins.str] = None,
        postgres_password: typing.Optional[builtins.str] = None,
        replication_password: typing.Optional[builtins.str] = None,
        replication_username: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param database: 
        :param enable_postgres_user: 
        :param password: 
        :param postgres_password: 
        :param replication_password: 
        :param replication_username: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DatabaseAuthOptions.__init__)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument enable_postgres_user", value=enable_postgres_user, expected_type=type_hints["enable_postgres_user"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument postgres_password", value=postgres_password, expected_type=type_hints["postgres_password"])
            check_type(argname="argument replication_password", value=replication_password, expected_type=type_hints["replication_password"])
            check_type(argname="argument replication_username", value=replication_username, expected_type=type_hints["replication_username"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[str, typing.Any] = {}
        if database is not None:
            self._values["database"] = database
        if enable_postgres_user is not None:
            self._values["enable_postgres_user"] = enable_postgres_user
        if password is not None:
            self._values["password"] = password
        if postgres_password is not None:
            self._values["postgres_password"] = postgres_password
        if replication_password is not None:
            self._values["replication_password"] = replication_password
        if replication_username is not None:
            self._values["replication_username"] = replication_username
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def database(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("database")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_postgres_user(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("enable_postgres_user")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgres_password(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("postgres_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_password(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("replication_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_username(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("replication_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseAuthOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.DatabaseMetricsOptions",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class DatabaseMetricsOptions:
    def __init__(self, *, enabled: typing.Optional[builtins.bool] = None) -> None:
        '''
        :param enabled: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DatabaseMetricsOptions.__init__)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseMetricsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.DatabaseReplicationOptions",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "read_replicas": "readReplicas"},
)
class DatabaseReplicationOptions:
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        read_replicas: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: 
        :param read_replicas: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DatabaseReplicationOptions.__init__)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument read_replicas", value=read_replicas, expected_type=type_hints["read_replicas"])
        self._values: typing.Dict[str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if read_replicas is not None:
            self._values["read_replicas"] = read_replicas

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def read_replicas(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("read_replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseReplicationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.DatabaseResourceRequestOptions",
    jsii_struct_bases=[],
    name_mapping={"cpu": "cpu", "memory": "memory"},
)
class DatabaseResourceRequestOptions:
    def __init__(
        self,
        *,
        cpu: typing.Optional[builtins.str] = None,
        memory: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cpu: 
        :param memory: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DatabaseResourceRequestOptions.__init__)
            check_type(argname="argument cpu", value=cpu, expected_type=type_hints["cpu"])
            check_type(argname="argument memory", value=memory, expected_type=type_hints["memory"])
        self._values: typing.Dict[str, typing.Any] = {}
        if cpu is not None:
            self._values["cpu"] = cpu
        if memory is not None:
            self._values["memory"] = memory

    @builtins.property
    def cpu(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memory(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseResourceRequestOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.DatabaseResourcesOptions",
    jsii_struct_bases=[],
    name_mapping={"requests": "requests"},
)
class DatabaseResourcesOptions:
    def __init__(
        self,
        *,
        requests: typing.Optional[typing.Union[DatabaseResourceRequestOptions, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param requests: 

        :stability: experimental
        '''
        if isinstance(requests, dict):
            requests = DatabaseResourceRequestOptions(**requests)
        if __debug__:
            type_hints = typing.get_type_hints(DatabaseResourcesOptions.__init__)
            check_type(argname="argument requests", value=requests, expected_type=type_hints["requests"])
        self._values: typing.Dict[str, typing.Any] = {}
        if requests is not None:
            self._values["requests"] = requests

    @builtins.property
    def requests(self) -> typing.Optional[DatabaseResourceRequestOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("requests")
        return typing.cast(typing.Optional[DatabaseResourceRequestOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseResourcesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.DatabaseVolumePermissionsOptions",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class DatabaseVolumePermissionsOptions:
    def __init__(self, *, enabled: typing.Optional[builtins.bool] = None) -> None:
        '''
        :param enabled: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DatabaseVolumePermissionsOptions.__init__)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseVolumePermissionsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.DbMigrationOptions",
    jsii_struct_bases=[],
    name_mapping={"only_if_db_empty": "onlyIfDbEmpty", "run_on_start": "runOnStart"},
)
class DbMigrationOptions:
    def __init__(
        self,
        *,
        only_if_db_empty: typing.Optional[builtins.bool] = None,
        run_on_start: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param only_if_db_empty: 
        :param run_on_start: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(DbMigrationOptions.__init__)
            check_type(argname="argument only_if_db_empty", value=only_if_db_empty, expected_type=type_hints["only_if_db_empty"])
            check_type(argname="argument run_on_start", value=run_on_start, expected_type=type_hints["run_on_start"])
        self._values: typing.Dict[str, typing.Any] = {}
        if only_if_db_empty is not None:
            self._values["only_if_db_empty"] = only_if_db_empty
        if run_on_start is not None:
            self._values["run_on_start"] = run_on_start

    @builtins.property
    def only_if_db_empty(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("only_if_db_empty")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def run_on_start(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("run_on_start")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbMigrationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.HostOptions",
    jsii_struct_bases=[],
    name_mapping={"host": "host", "paths": "paths"},
)
class HostOptions:
    def __init__(
        self,
        *,
        host: typing.Optional[builtins.str] = None,
        paths: typing.Optional[typing.Sequence[typing.Union["HttpIngressPath", typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param host: 
        :param paths: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(HostOptions.__init__)
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument paths", value=paths, expected_type=type_hints["paths"])
        self._values: typing.Dict[str, typing.Any] = {}
        if host is not None:
            self._values["host"] = host
        if paths is not None:
            self._values["paths"] = paths

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def paths(self) -> typing.Optional[typing.List["HttpIngressPath"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("paths")
        return typing.cast(typing.Optional[typing.List["HttpIngressPath"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HostOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.HttpIngressPath",
    jsii_struct_bases=[],
    name_mapping={"path": "path", "path_type": "pathType"},
)
class HttpIngressPath:
    def __init__(
        self,
        *,
        path: typing.Optional[builtins.str] = None,
        path_type: typing.Optional["HttpIngressPathType"] = None,
    ) -> None:
        '''
        :param path: 
        :param path_type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(HttpIngressPath.__init__)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument path_type", value=path_type, expected_type=type_hints["path_type"])
        self._values: typing.Dict[str, typing.Any] = {}
        if path is not None:
            self._values["path"] = path
        if path_type is not None:
            self._values["path_type"] = path_type

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_type(self) -> typing.Optional["HttpIngressPathType"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("path_type")
        return typing.cast(typing.Optional["HttpIngressPathType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpIngressPath(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s-metaflow.HttpIngressPathType")
class HttpIngressPathType(enum.Enum):
    '''
    :stability: experimental
    '''

    PREFIX = "PREFIX"
    '''
    :stability: experimental
    '''
    EXACT = "EXACT"
    '''
    :stability: experimental
    '''
    IMPLEMENTATION_SPECIFIC = "IMPLEMENTATION_SPECIFIC"
    '''
    :stability: experimental
    '''


@jsii.interface(jsii_type="cdk8s-metaflow.IApiResource")
class IApiResource(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGroup")
    def api_group(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceName")
    def resource_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...


class _IApiResourceProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk8s-metaflow.IApiResource"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGroup")
    def api_group(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceName")
    def resource_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceType"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IApiResource).__jsii_proxy_class__ = lambda : _IApiResourceProxy


@jsii.data_type(
    jsii_type="cdk8s-metaflow.ImageOptions",
    jsii_struct_bases=[],
    name_mapping={
        "pull_policy": "pullPolicy",
        "repository": "repository",
        "tag": "tag",
    },
)
class ImageOptions:
    def __init__(
        self,
        *,
        pull_policy: typing.Optional["ImagePullPolicy"] = None,
        repository: typing.Optional[builtins.str] = None,
        tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pull_policy: 
        :param repository: 
        :param tag: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ImageOptions.__init__)
            check_type(argname="argument pull_policy", value=pull_policy, expected_type=type_hints["pull_policy"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
        self._values: typing.Dict[str, typing.Any] = {}
        if pull_policy is not None:
            self._values["pull_policy"] = pull_policy
        if repository is not None:
            self._values["repository"] = repository
        if tag is not None:
            self._values["tag"] = tag

    @builtins.property
    def pull_policy(self) -> typing.Optional["ImagePullPolicy"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pull_policy")
        return typing.cast(typing.Optional["ImagePullPolicy"], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s-metaflow.ImagePullPolicy")
class ImagePullPolicy(enum.Enum):
    '''
    :stability: experimental
    '''

    ALWAYS = "ALWAYS"
    '''
    :stability: experimental
    '''
    IF_NOT_PRESENT = "IF_NOT_PRESENT"
    '''
    :stability: experimental
    '''
    NEVER = "NEVER"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="cdk8s-metaflow.IngressOptions",
    jsii_struct_bases=[],
    name_mapping={
        "annotations": "annotations",
        "class_name": "className",
        "enabled": "enabled",
        "hosts": "hosts",
        "tls": "tls",
    },
)
class IngressOptions:
    def __init__(
        self,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        class_name: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        hosts: typing.Optional[typing.Sequence[typing.Union[HostOptions, typing.Dict[str, typing.Any]]]] = None,
        tls: typing.Optional[_IngressTls_e4c411c9] = None,
    ) -> None:
        '''
        :param annotations: 
        :param class_name: 
        :param enabled: 
        :param hosts: 
        :param tls: 

        :stability: experimental
        '''
        if isinstance(tls, dict):
            tls = _IngressTls_e4c411c9(**tls)
        if __debug__:
            type_hints = typing.get_type_hints(IngressOptions.__init__)
            check_type(argname="argument annotations", value=annotations, expected_type=type_hints["annotations"])
            check_type(argname="argument class_name", value=class_name, expected_type=type_hints["class_name"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument hosts", value=hosts, expected_type=type_hints["hosts"])
            check_type(argname="argument tls", value=tls, expected_type=type_hints["tls"])
        self._values: typing.Dict[str, typing.Any] = {}
        if annotations is not None:
            self._values["annotations"] = annotations
        if class_name is not None:
            self._values["class_name"] = class_name
        if enabled is not None:
            self._values["enabled"] = enabled
        if hosts is not None:
            self._values["hosts"] = hosts
        if tls is not None:
            self._values["tls"] = tls

    @builtins.property
    def annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def class_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("class_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def hosts(self) -> typing.Optional[typing.List[HostOptions]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("hosts")
        return typing.cast(typing.Optional[typing.List[HostOptions]], result)

    @builtins.property
    def tls(self) -> typing.Optional[_IngressTls_e4c411c9]:
        '''
        :stability: experimental
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional[_IngressTls_e4c411c9], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IngressOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetadataDatabase(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-metaflow.MetadataDatabase",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        chart_version: builtins.str,
        chart_values: typing.Optional[typing.Union["MetadataDatabaseOptions", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param chart_version: 
        :param chart_values: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(MetadataDatabase.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MetadataDatabaseProps(
            chart_version=chart_version, chart_values=chart_values
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk8s-metaflow.MetadataDatabaseOptions",
    jsii_struct_bases=[],
    name_mapping={
        "architecture": "architecture",
        "auth": "auth",
        "host": "host",
        "metrics": "metrics",
        "password": "password",
        "port": "port",
        "replication": "replication",
        "resources": "resources",
        "user": "user",
        "volume_permissions": "volumePermissions",
    },
)
class MetadataDatabaseOptions:
    def __init__(
        self,
        *,
        architecture: typing.Optional[builtins.str] = None,
        auth: typing.Optional[typing.Union[DatabaseAuthOptions, typing.Dict[str, typing.Any]]] = None,
        host: typing.Optional[builtins.str] = None,
        metrics: typing.Optional[typing.Union[DatabaseMetricsOptions, typing.Dict[str, typing.Any]]] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        replication: typing.Optional[typing.Union[DatabaseReplicationOptions, typing.Dict[str, typing.Any]]] = None,
        resources: typing.Optional[typing.Union[DatabaseResourcesOptions, typing.Dict[str, typing.Any]]] = None,
        user: typing.Optional[builtins.str] = None,
        volume_permissions: typing.Optional[typing.Union[DatabaseVolumePermissionsOptions, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param architecture: 
        :param auth: 
        :param host: 
        :param metrics: 
        :param password: 
        :param port: 
        :param replication: 
        :param resources: 
        :param user: 
        :param volume_permissions: 

        :stability: experimental
        '''
        if isinstance(auth, dict):
            auth = DatabaseAuthOptions(**auth)
        if isinstance(metrics, dict):
            metrics = DatabaseMetricsOptions(**metrics)
        if isinstance(replication, dict):
            replication = DatabaseReplicationOptions(**replication)
        if isinstance(resources, dict):
            resources = DatabaseResourcesOptions(**resources)
        if isinstance(volume_permissions, dict):
            volume_permissions = DatabaseVolumePermissionsOptions(**volume_permissions)
        if __debug__:
            type_hints = typing.get_type_hints(MetadataDatabaseOptions.__init__)
            check_type(argname="argument architecture", value=architecture, expected_type=type_hints["architecture"])
            check_type(argname="argument auth", value=auth, expected_type=type_hints["auth"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument metrics", value=metrics, expected_type=type_hints["metrics"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument replication", value=replication, expected_type=type_hints["replication"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
            check_type(argname="argument user", value=user, expected_type=type_hints["user"])
            check_type(argname="argument volume_permissions", value=volume_permissions, expected_type=type_hints["volume_permissions"])
        self._values: typing.Dict[str, typing.Any] = {}
        if architecture is not None:
            self._values["architecture"] = architecture
        if auth is not None:
            self._values["auth"] = auth
        if host is not None:
            self._values["host"] = host
        if metrics is not None:
            self._values["metrics"] = metrics
        if password is not None:
            self._values["password"] = password
        if port is not None:
            self._values["port"] = port
        if replication is not None:
            self._values["replication"] = replication
        if resources is not None:
            self._values["resources"] = resources
        if user is not None:
            self._values["user"] = user
        if volume_permissions is not None:
            self._values["volume_permissions"] = volume_permissions

    @builtins.property
    def architecture(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth(self) -> typing.Optional[DatabaseAuthOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("auth")
        return typing.cast(typing.Optional[DatabaseAuthOptions], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metrics(self) -> typing.Optional[DatabaseMetricsOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("metrics")
        return typing.cast(typing.Optional[DatabaseMetricsOptions], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def replication(self) -> typing.Optional[DatabaseReplicationOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("replication")
        return typing.cast(typing.Optional[DatabaseReplicationOptions], result)

    @builtins.property
    def resources(self) -> typing.Optional[DatabaseResourcesOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[DatabaseResourcesOptions], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def volume_permissions(self) -> typing.Optional[DatabaseVolumePermissionsOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("volume_permissions")
        return typing.cast(typing.Optional[DatabaseVolumePermissionsOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetadataDatabaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.MetadataDatabaseProps",
    jsii_struct_bases=[],
    name_mapping={"chart_version": "chartVersion", "chart_values": "chartValues"},
)
class MetadataDatabaseProps:
    def __init__(
        self,
        *,
        chart_version: builtins.str,
        chart_values: typing.Optional[typing.Union[MetadataDatabaseOptions, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param chart_version: 
        :param chart_values: 

        :stability: experimental
        '''
        if isinstance(chart_values, dict):
            chart_values = MetadataDatabaseOptions(**chart_values)
        if __debug__:
            type_hints = typing.get_type_hints(MetadataDatabaseProps.__init__)
            check_type(argname="argument chart_version", value=chart_version, expected_type=type_hints["chart_version"])
            check_type(argname="argument chart_values", value=chart_values, expected_type=type_hints["chart_values"])
        self._values: typing.Dict[str, typing.Any] = {
            "chart_version": chart_version,
        }
        if chart_values is not None:
            self._values["chart_values"] = chart_values

    @builtins.property
    def chart_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("chart_version")
        assert result is not None, "Required property 'chart_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def chart_values(self) -> typing.Optional[MetadataDatabaseOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("chart_values")
        return typing.cast(typing.Optional[MetadataDatabaseOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetadataDatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetaflowService(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-metaflow.MetaflowService",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        chart_version: builtins.str,
        chart_values: typing.Optional[typing.Union["MetaflowServiceOptions", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param chart_version: 
        :param chart_values: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(MetaflowService.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MetaflowServiceProps(
            chart_version=chart_version, chart_values=chart_values
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk8s-metaflow.MetaflowServiceOptions",
    jsii_struct_bases=[],
    name_mapping={
        "affinity": "affinity",
        "autoscaling": "autoscaling",
        "db_migrations": "dbMigrations",
        "env_from": "envFrom",
        "fullname_override": "fullnameOverride",
        "image": "image",
        "image_pull_secrets": "imagePullSecrets",
        "ingress": "ingress",
        "metadatadb": "metadatadb",
        "name_override": "nameOverride",
        "node_selector": "nodeSelector",
        "pod_annotations": "podAnnotations",
        "pod_security_context": "podSecurityContext",
        "replica_count": "replicaCount",
        "resources": "resources",
        "security_context": "securityContext",
        "service": "service",
        "service_account": "serviceAccount",
        "tolerations": "tolerations",
    },
)
class MetaflowServiceOptions:
    def __init__(
        self,
        *,
        affinity: typing.Optional[_Affinity_9d28a7c5] = None,
        autoscaling: typing.Optional[typing.Union[AutoscalingOptions, typing.Dict[str, typing.Any]]] = None,
        db_migrations: typing.Optional[typing.Union[DbMigrationOptions, typing.Dict[str, typing.Any]]] = None,
        env_from: typing.Optional[typing.Sequence[_EnvFromSource_2b00ef0f]] = None,
        fullname_override: typing.Optional[builtins.str] = None,
        image: typing.Optional[typing.Union[ImageOptions, typing.Dict[str, typing.Any]]] = None,
        image_pull_secrets: typing.Optional[typing.Sequence[builtins.str]] = None,
        ingress: typing.Optional[typing.Union[IngressOptions, typing.Dict[str, typing.Any]]] = None,
        metadatadb: typing.Optional[typing.Union[MetadataDatabaseOptions, typing.Dict[str, typing.Any]]] = None,
        name_override: typing.Optional[builtins.str] = None,
        node_selector: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        pod_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        pod_security_context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        replica_count: typing.Optional[jsii.Number] = None,
        resources: typing.Optional[typing.Sequence[IApiResource]] = None,
        security_context: typing.Optional[_SecurityContext_bd8348aa] = None,
        service: typing.Optional[typing.Union["ServiceOptions", typing.Dict[str, typing.Any]]] = None,
        service_account: typing.Optional[typing.Union["ServiceAccountOptions", typing.Dict[str, typing.Any]]] = None,
        tolerations: typing.Optional[typing.Sequence[_Toleration_0b6f63dc]] = None,
    ) -> None:
        '''
        :param affinity: 
        :param autoscaling: 
        :param db_migrations: 
        :param env_from: 
        :param fullname_override: 
        :param image: 
        :param image_pull_secrets: 
        :param ingress: 
        :param metadatadb: 
        :param name_override: 
        :param node_selector: 
        :param pod_annotations: 
        :param pod_security_context: 
        :param replica_count: 
        :param resources: 
        :param security_context: 
        :param service: 
        :param service_account: 
        :param tolerations: 

        :stability: experimental
        '''
        if isinstance(affinity, dict):
            affinity = _Affinity_9d28a7c5(**affinity)
        if isinstance(autoscaling, dict):
            autoscaling = AutoscalingOptions(**autoscaling)
        if isinstance(db_migrations, dict):
            db_migrations = DbMigrationOptions(**db_migrations)
        if isinstance(image, dict):
            image = ImageOptions(**image)
        if isinstance(ingress, dict):
            ingress = IngressOptions(**ingress)
        if isinstance(metadatadb, dict):
            metadatadb = MetadataDatabaseOptions(**metadatadb)
        if isinstance(security_context, dict):
            security_context = _SecurityContext_bd8348aa(**security_context)
        if isinstance(service, dict):
            service = ServiceOptions(**service)
        if isinstance(service_account, dict):
            service_account = ServiceAccountOptions(**service_account)
        if __debug__:
            type_hints = typing.get_type_hints(MetaflowServiceOptions.__init__)
            check_type(argname="argument affinity", value=affinity, expected_type=type_hints["affinity"])
            check_type(argname="argument autoscaling", value=autoscaling, expected_type=type_hints["autoscaling"])
            check_type(argname="argument db_migrations", value=db_migrations, expected_type=type_hints["db_migrations"])
            check_type(argname="argument env_from", value=env_from, expected_type=type_hints["env_from"])
            check_type(argname="argument fullname_override", value=fullname_override, expected_type=type_hints["fullname_override"])
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument image_pull_secrets", value=image_pull_secrets, expected_type=type_hints["image_pull_secrets"])
            check_type(argname="argument ingress", value=ingress, expected_type=type_hints["ingress"])
            check_type(argname="argument metadatadb", value=metadatadb, expected_type=type_hints["metadatadb"])
            check_type(argname="argument name_override", value=name_override, expected_type=type_hints["name_override"])
            check_type(argname="argument node_selector", value=node_selector, expected_type=type_hints["node_selector"])
            check_type(argname="argument pod_annotations", value=pod_annotations, expected_type=type_hints["pod_annotations"])
            check_type(argname="argument pod_security_context", value=pod_security_context, expected_type=type_hints["pod_security_context"])
            check_type(argname="argument replica_count", value=replica_count, expected_type=type_hints["replica_count"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
            check_type(argname="argument security_context", value=security_context, expected_type=type_hints["security_context"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument service_account", value=service_account, expected_type=type_hints["service_account"])
            check_type(argname="argument tolerations", value=tolerations, expected_type=type_hints["tolerations"])
        self._values: typing.Dict[str, typing.Any] = {}
        if affinity is not None:
            self._values["affinity"] = affinity
        if autoscaling is not None:
            self._values["autoscaling"] = autoscaling
        if db_migrations is not None:
            self._values["db_migrations"] = db_migrations
        if env_from is not None:
            self._values["env_from"] = env_from
        if fullname_override is not None:
            self._values["fullname_override"] = fullname_override
        if image is not None:
            self._values["image"] = image
        if image_pull_secrets is not None:
            self._values["image_pull_secrets"] = image_pull_secrets
        if ingress is not None:
            self._values["ingress"] = ingress
        if metadatadb is not None:
            self._values["metadatadb"] = metadatadb
        if name_override is not None:
            self._values["name_override"] = name_override
        if node_selector is not None:
            self._values["node_selector"] = node_selector
        if pod_annotations is not None:
            self._values["pod_annotations"] = pod_annotations
        if pod_security_context is not None:
            self._values["pod_security_context"] = pod_security_context
        if replica_count is not None:
            self._values["replica_count"] = replica_count
        if resources is not None:
            self._values["resources"] = resources
        if security_context is not None:
            self._values["security_context"] = security_context
        if service is not None:
            self._values["service"] = service
        if service_account is not None:
            self._values["service_account"] = service_account
        if tolerations is not None:
            self._values["tolerations"] = tolerations

    @builtins.property
    def affinity(self) -> typing.Optional[_Affinity_9d28a7c5]:
        '''
        :stability: experimental
        '''
        result = self._values.get("affinity")
        return typing.cast(typing.Optional[_Affinity_9d28a7c5], result)

    @builtins.property
    def autoscaling(self) -> typing.Optional[AutoscalingOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("autoscaling")
        return typing.cast(typing.Optional[AutoscalingOptions], result)

    @builtins.property
    def db_migrations(self) -> typing.Optional[DbMigrationOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("db_migrations")
        return typing.cast(typing.Optional[DbMigrationOptions], result)

    @builtins.property
    def env_from(self) -> typing.Optional[typing.List[_EnvFromSource_2b00ef0f]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("env_from")
        return typing.cast(typing.Optional[typing.List[_EnvFromSource_2b00ef0f]], result)

    @builtins.property
    def fullname_override(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("fullname_override")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image(self) -> typing.Optional[ImageOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[ImageOptions], result)

    @builtins.property
    def image_pull_secrets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("image_pull_secrets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ingress(self) -> typing.Optional[IngressOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ingress")
        return typing.cast(typing.Optional[IngressOptions], result)

    @builtins.property
    def metadatadb(self) -> typing.Optional[MetadataDatabaseOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("metadatadb")
        return typing.cast(typing.Optional[MetadataDatabaseOptions], result)

    @builtins.property
    def name_override(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name_override")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("node_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def pod_annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pod_annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def pod_security_context(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pod_security_context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def replica_count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("replica_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def resources(self) -> typing.Optional[typing.List[IApiResource]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.List[IApiResource]], result)

    @builtins.property
    def security_context(self) -> typing.Optional[_SecurityContext_bd8348aa]:
        '''
        :stability: experimental
        '''
        result = self._values.get("security_context")
        return typing.cast(typing.Optional[_SecurityContext_bd8348aa], result)

    @builtins.property
    def service(self) -> typing.Optional["ServiceOptions"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional["ServiceOptions"], result)

    @builtins.property
    def service_account(self) -> typing.Optional["ServiceAccountOptions"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional["ServiceAccountOptions"], result)

    @builtins.property
    def tolerations(self) -> typing.Optional[typing.List[_Toleration_0b6f63dc]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("tolerations")
        return typing.cast(typing.Optional[typing.List[_Toleration_0b6f63dc]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetaflowServiceOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.MetaflowServiceProps",
    jsii_struct_bases=[],
    name_mapping={"chart_version": "chartVersion", "chart_values": "chartValues"},
)
class MetaflowServiceProps:
    def __init__(
        self,
        *,
        chart_version: builtins.str,
        chart_values: typing.Optional[typing.Union[MetaflowServiceOptions, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param chart_version: 
        :param chart_values: 

        :stability: experimental
        '''
        if isinstance(chart_values, dict):
            chart_values = MetaflowServiceOptions(**chart_values)
        if __debug__:
            type_hints = typing.get_type_hints(MetaflowServiceProps.__init__)
            check_type(argname="argument chart_version", value=chart_version, expected_type=type_hints["chart_version"])
            check_type(argname="argument chart_values", value=chart_values, expected_type=type_hints["chart_values"])
        self._values: typing.Dict[str, typing.Any] = {
            "chart_version": chart_version,
        }
        if chart_values is not None:
            self._values["chart_values"] = chart_values

    @builtins.property
    def chart_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("chart_version")
        assert result is not None, "Required property 'chart_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def chart_values(self) -> typing.Optional[MetaflowServiceOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("chart_values")
        return typing.cast(typing.Optional[MetaflowServiceOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetaflowServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetaflowUI(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-metaflow.MetaflowUI",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        chart_version: builtins.str,
        chart_values: typing.Optional[typing.Union["MetaflowUIOptions", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param chart_version: 
        :param chart_values: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(MetaflowUI.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MetaflowUIProps(chart_version=chart_version, chart_values=chart_values)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk8s-metaflow.MetaflowUIOptions",
    jsii_struct_bases=[],
    name_mapping={
        "env": "env",
        "metaflow_datastore_sysroot_s3": "metaflowDatastoreSysrootS3",
        "affinity": "affinity",
        "autoscaling": "autoscaling",
        "env_from": "envFrom",
        "fullname_override": "fullnameOverride",
        "image": "image",
        "image_pull_secrets": "imagePullSecrets",
        "ingress": "ingress",
        "metadatadb": "metadatadb",
        "name_override": "nameOverride",
        "node_selector": "nodeSelector",
        "pod_annotations": "podAnnotations",
        "pod_security_context": "podSecurityContext",
        "replica_count": "replicaCount",
        "resources": "resources",
        "security_context": "securityContext",
        "service": "service",
        "service_account": "serviceAccount",
        "service_static": "serviceStatic",
        "tolerations": "tolerations",
        "ui_image": "uiImage",
    },
)
class MetaflowUIOptions:
    def __init__(
        self,
        *,
        env: typing.Mapping[builtins.str, builtins.str],
        metaflow_datastore_sysroot_s3: builtins.str,
        affinity: typing.Optional[_Affinity_9d28a7c5] = None,
        autoscaling: typing.Optional[typing.Union[AutoscalingOptions, typing.Dict[str, typing.Any]]] = None,
        env_from: typing.Optional[typing.Sequence[_EnvFromSource_2b00ef0f]] = None,
        fullname_override: typing.Optional[builtins.str] = None,
        image: typing.Optional[typing.Union[ImageOptions, typing.Dict[str, typing.Any]]] = None,
        image_pull_secrets: typing.Optional[typing.Sequence[builtins.str]] = None,
        ingress: typing.Optional[typing.Union[IngressOptions, typing.Dict[str, typing.Any]]] = None,
        metadatadb: typing.Optional[typing.Union[MetadataDatabaseOptions, typing.Dict[str, typing.Any]]] = None,
        name_override: typing.Optional[builtins.str] = None,
        node_selector: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        pod_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        pod_security_context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        replica_count: typing.Optional[jsii.Number] = None,
        resources: typing.Optional[typing.Sequence[IApiResource]] = None,
        security_context: typing.Optional[_SecurityContext_bd8348aa] = None,
        service: typing.Optional[typing.Union["ServiceOptions", typing.Dict[str, typing.Any]]] = None,
        service_account: typing.Optional[typing.Union["ServiceAccountOptions", typing.Dict[str, typing.Any]]] = None,
        service_static: typing.Optional[typing.Union["ServiceOptions", typing.Dict[str, typing.Any]]] = None,
        tolerations: typing.Optional[typing.Sequence[_Toleration_0b6f63dc]] = None,
        ui_image: typing.Optional[typing.Union[ImageOptions, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param env: 
        :param metaflow_datastore_sysroot_s3: 
        :param affinity: 
        :param autoscaling: 
        :param env_from: 
        :param fullname_override: 
        :param image: 
        :param image_pull_secrets: 
        :param ingress: 
        :param metadatadb: 
        :param name_override: 
        :param node_selector: 
        :param pod_annotations: 
        :param pod_security_context: 
        :param replica_count: 
        :param resources: 
        :param security_context: 
        :param service: 
        :param service_account: 
        :param service_static: 
        :param tolerations: 
        :param ui_image: 

        :stability: experimental
        '''
        if isinstance(affinity, dict):
            affinity = _Affinity_9d28a7c5(**affinity)
        if isinstance(autoscaling, dict):
            autoscaling = AutoscalingOptions(**autoscaling)
        if isinstance(image, dict):
            image = ImageOptions(**image)
        if isinstance(ingress, dict):
            ingress = IngressOptions(**ingress)
        if isinstance(metadatadb, dict):
            metadatadb = MetadataDatabaseOptions(**metadatadb)
        if isinstance(security_context, dict):
            security_context = _SecurityContext_bd8348aa(**security_context)
        if isinstance(service, dict):
            service = ServiceOptions(**service)
        if isinstance(service_account, dict):
            service_account = ServiceAccountOptions(**service_account)
        if isinstance(service_static, dict):
            service_static = ServiceOptions(**service_static)
        if isinstance(ui_image, dict):
            ui_image = ImageOptions(**ui_image)
        if __debug__:
            type_hints = typing.get_type_hints(MetaflowUIOptions.__init__)
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument metaflow_datastore_sysroot_s3", value=metaflow_datastore_sysroot_s3, expected_type=type_hints["metaflow_datastore_sysroot_s3"])
            check_type(argname="argument affinity", value=affinity, expected_type=type_hints["affinity"])
            check_type(argname="argument autoscaling", value=autoscaling, expected_type=type_hints["autoscaling"])
            check_type(argname="argument env_from", value=env_from, expected_type=type_hints["env_from"])
            check_type(argname="argument fullname_override", value=fullname_override, expected_type=type_hints["fullname_override"])
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument image_pull_secrets", value=image_pull_secrets, expected_type=type_hints["image_pull_secrets"])
            check_type(argname="argument ingress", value=ingress, expected_type=type_hints["ingress"])
            check_type(argname="argument metadatadb", value=metadatadb, expected_type=type_hints["metadatadb"])
            check_type(argname="argument name_override", value=name_override, expected_type=type_hints["name_override"])
            check_type(argname="argument node_selector", value=node_selector, expected_type=type_hints["node_selector"])
            check_type(argname="argument pod_annotations", value=pod_annotations, expected_type=type_hints["pod_annotations"])
            check_type(argname="argument pod_security_context", value=pod_security_context, expected_type=type_hints["pod_security_context"])
            check_type(argname="argument replica_count", value=replica_count, expected_type=type_hints["replica_count"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
            check_type(argname="argument security_context", value=security_context, expected_type=type_hints["security_context"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument service_account", value=service_account, expected_type=type_hints["service_account"])
            check_type(argname="argument service_static", value=service_static, expected_type=type_hints["service_static"])
            check_type(argname="argument tolerations", value=tolerations, expected_type=type_hints["tolerations"])
            check_type(argname="argument ui_image", value=ui_image, expected_type=type_hints["ui_image"])
        self._values: typing.Dict[str, typing.Any] = {
            "env": env,
            "metaflow_datastore_sysroot_s3": metaflow_datastore_sysroot_s3,
        }
        if affinity is not None:
            self._values["affinity"] = affinity
        if autoscaling is not None:
            self._values["autoscaling"] = autoscaling
        if env_from is not None:
            self._values["env_from"] = env_from
        if fullname_override is not None:
            self._values["fullname_override"] = fullname_override
        if image is not None:
            self._values["image"] = image
        if image_pull_secrets is not None:
            self._values["image_pull_secrets"] = image_pull_secrets
        if ingress is not None:
            self._values["ingress"] = ingress
        if metadatadb is not None:
            self._values["metadatadb"] = metadatadb
        if name_override is not None:
            self._values["name_override"] = name_override
        if node_selector is not None:
            self._values["node_selector"] = node_selector
        if pod_annotations is not None:
            self._values["pod_annotations"] = pod_annotations
        if pod_security_context is not None:
            self._values["pod_security_context"] = pod_security_context
        if replica_count is not None:
            self._values["replica_count"] = replica_count
        if resources is not None:
            self._values["resources"] = resources
        if security_context is not None:
            self._values["security_context"] = security_context
        if service is not None:
            self._values["service"] = service
        if service_account is not None:
            self._values["service_account"] = service_account
        if service_static is not None:
            self._values["service_static"] = service_static
        if tolerations is not None:
            self._values["tolerations"] = tolerations
        if ui_image is not None:
            self._values["ui_image"] = ui_image

    @builtins.property
    def env(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("env")
        assert result is not None, "Required property 'env' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def metaflow_datastore_sysroot_s3(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("metaflow_datastore_sysroot_s3")
        assert result is not None, "Required property 'metaflow_datastore_sysroot_s3' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def affinity(self) -> typing.Optional[_Affinity_9d28a7c5]:
        '''
        :stability: experimental
        '''
        result = self._values.get("affinity")
        return typing.cast(typing.Optional[_Affinity_9d28a7c5], result)

    @builtins.property
    def autoscaling(self) -> typing.Optional[AutoscalingOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("autoscaling")
        return typing.cast(typing.Optional[AutoscalingOptions], result)

    @builtins.property
    def env_from(self) -> typing.Optional[typing.List[_EnvFromSource_2b00ef0f]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("env_from")
        return typing.cast(typing.Optional[typing.List[_EnvFromSource_2b00ef0f]], result)

    @builtins.property
    def fullname_override(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("fullname_override")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image(self) -> typing.Optional[ImageOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[ImageOptions], result)

    @builtins.property
    def image_pull_secrets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("image_pull_secrets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ingress(self) -> typing.Optional[IngressOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ingress")
        return typing.cast(typing.Optional[IngressOptions], result)

    @builtins.property
    def metadatadb(self) -> typing.Optional[MetadataDatabaseOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("metadatadb")
        return typing.cast(typing.Optional[MetadataDatabaseOptions], result)

    @builtins.property
    def name_override(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name_override")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("node_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def pod_annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pod_annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def pod_security_context(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pod_security_context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def replica_count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("replica_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def resources(self) -> typing.Optional[typing.List[IApiResource]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.List[IApiResource]], result)

    @builtins.property
    def security_context(self) -> typing.Optional[_SecurityContext_bd8348aa]:
        '''
        :stability: experimental
        '''
        result = self._values.get("security_context")
        return typing.cast(typing.Optional[_SecurityContext_bd8348aa], result)

    @builtins.property
    def service(self) -> typing.Optional["ServiceOptions"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional["ServiceOptions"], result)

    @builtins.property
    def service_account(self) -> typing.Optional["ServiceAccountOptions"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional["ServiceAccountOptions"], result)

    @builtins.property
    def service_static(self) -> typing.Optional["ServiceOptions"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("service_static")
        return typing.cast(typing.Optional["ServiceOptions"], result)

    @builtins.property
    def tolerations(self) -> typing.Optional[typing.List[_Toleration_0b6f63dc]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("tolerations")
        return typing.cast(typing.Optional[typing.List[_Toleration_0b6f63dc]], result)

    @builtins.property
    def ui_image(self) -> typing.Optional[ImageOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ui_image")
        return typing.cast(typing.Optional[ImageOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetaflowUIOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.MetaflowUIProps",
    jsii_struct_bases=[],
    name_mapping={"chart_version": "chartVersion", "chart_values": "chartValues"},
)
class MetaflowUIProps:
    def __init__(
        self,
        *,
        chart_version: builtins.str,
        chart_values: typing.Optional[typing.Union[MetaflowUIOptions, typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param chart_version: 
        :param chart_values: 

        :stability: experimental
        '''
        if isinstance(chart_values, dict):
            chart_values = MetaflowUIOptions(**chart_values)
        if __debug__:
            type_hints = typing.get_type_hints(MetaflowUIProps.__init__)
            check_type(argname="argument chart_version", value=chart_version, expected_type=type_hints["chart_version"])
            check_type(argname="argument chart_values", value=chart_values, expected_type=type_hints["chart_values"])
        self._values: typing.Dict[str, typing.Any] = {
            "chart_version": chart_version,
        }
        if chart_values is not None:
            self._values["chart_values"] = chart_values

    @builtins.property
    def chart_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("chart_version")
        assert result is not None, "Required property 'chart_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def chart_values(self) -> typing.Optional[MetaflowUIOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("chart_values")
        return typing.cast(typing.Optional[MetaflowUIOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetaflowUIProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.ServiceAccountOptions",
    jsii_struct_bases=[],
    name_mapping={"annotations": "annotations", "create": "create", "name": "name"},
)
class ServiceAccountOptions:
    def __init__(
        self,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        create: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param annotations: 
        :param create: 
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ServiceAccountOptions.__init__)
            check_type(argname="argument annotations", value=annotations, expected_type=type_hints["annotations"])
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[str, typing.Any] = {}
        if annotations is not None:
            self._values["annotations"] = annotations
        if create is not None:
            self._values["create"] = create
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def create(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceAccountOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.ServiceOptions",
    jsii_struct_bases=[],
    name_mapping={"annotations": "annotations", "port": "port", "type": "type"},
)
class ServiceOptions:
    def __init__(
        self,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        port: typing.Optional[jsii.Number] = None,
        type: typing.Optional["ServiceType"] = None,
    ) -> None:
        '''
        :param annotations: 
        :param port: 
        :param type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ServiceOptions.__init__)
            check_type(argname="argument annotations", value=annotations, expected_type=type_hints["annotations"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[str, typing.Any] = {}
        if annotations is not None:
            self._values["annotations"] = annotations
        if port is not None:
            self._values["port"] = port
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type(self) -> typing.Optional["ServiceType"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["ServiceType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s-metaflow.ServiceType")
class ServiceType(enum.Enum):
    '''
    :stability: experimental
    '''

    CLUSTER_IP = "CLUSTER_IP"
    '''
    :stability: experimental
    '''
    NODE_PORT = "NODE_PORT"
    '''
    :stability: experimental
    '''
    LOAD_BALANCER = "LOAD_BALANCER"
    '''
    :stability: experimental
    '''
    EXTERNAL_NAME = "EXTERNAL_NAME"
    '''
    :stability: experimental
    '''


__all__ = [
    "AutoscalingOptions",
    "DatabaseAuthOptions",
    "DatabaseMetricsOptions",
    "DatabaseReplicationOptions",
    "DatabaseResourceRequestOptions",
    "DatabaseResourcesOptions",
    "DatabaseVolumePermissionsOptions",
    "DbMigrationOptions",
    "HostOptions",
    "HttpIngressPath",
    "HttpIngressPathType",
    "IApiResource",
    "ImageOptions",
    "ImagePullPolicy",
    "IngressOptions",
    "MetadataDatabase",
    "MetadataDatabaseOptions",
    "MetadataDatabaseProps",
    "MetaflowService",
    "MetaflowServiceOptions",
    "MetaflowServiceProps",
    "MetaflowUI",
    "MetaflowUIOptions",
    "MetaflowUIProps",
    "ServiceAccountOptions",
    "ServiceOptions",
    "ServiceType",
    "k8s",
    "minio",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import k8s
from . import minio
