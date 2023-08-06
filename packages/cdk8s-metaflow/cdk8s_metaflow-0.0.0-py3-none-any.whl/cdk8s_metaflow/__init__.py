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

import cdk8s_plus_22
import constructs


@jsii.data_type(
    jsii_type="cdk8s-metaflow.IngressOptions",
    jsii_struct_bases=[],
    name_mapping={"host_name": "hostName"},
)
class IngressOptions:
    def __init__(self, *, host_name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param host_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(IngressOptions.__init__)
            check_type(argname="argument host_name", value=host_name, expected_type=type_hints["host_name"])
        self._values: typing.Dict[str, typing.Any] = {}
        if host_name is not None:
            self._values["host_name"] = host_name

    @builtins.property
    def host_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("host_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IngressOptions(%s)" % ", ".join(
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
        image: typing.Optional[builtins.str] = None,
        ingress_enabled: typing.Optional[builtins.bool] = None,
        ingress_options: typing.Optional[typing.Union[IngressOptions, typing.Dict[str, typing.Any]]] = None,
        metadata_service_port: typing.Optional[jsii.Number] = None,
        postgres_enabled: typing.Optional[builtins.bool] = None,
        postgres_options: typing.Optional[typing.Union["PostgresOptions", typing.Dict[str, typing.Any]]] = None,
        service_account_name: typing.Optional[builtins.str] = None,
        service_name: typing.Optional[builtins.str] = None,
        upgrades_service_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param image: 
        :param ingress_enabled: 
        :param ingress_options: 
        :param metadata_service_port: 
        :param postgres_enabled: 
        :param postgres_options: 
        :param service_account_name: 
        :param service_name: 
        :param upgrades_service_port: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(MetaflowService.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MetaflowServiceProps(
            image=image,
            ingress_enabled=ingress_enabled,
            ingress_options=ingress_options,
            metadata_service_port=metadata_service_port,
            postgres_enabled=postgres_enabled,
            postgres_options=postgres_options,
            service_account_name=service_account_name,
            service_name=service_name,
            upgrades_service_port=upgrades_service_port,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> cdk8s_plus_22.Deployment:
        '''
        :stability: experimental
        '''
        return typing.cast(cdk8s_plus_22.Deployment, jsii.get(self, "deployment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> cdk8s_plus_22.Service:
        '''
        :stability: experimental
        '''
        return typing.cast(cdk8s_plus_22.Service, jsii.get(self, "service"))


@jsii.data_type(
    jsii_type="cdk8s-metaflow.MetaflowServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "image": "image",
        "ingress_enabled": "ingressEnabled",
        "ingress_options": "ingressOptions",
        "metadata_service_port": "metadataServicePort",
        "postgres_enabled": "postgresEnabled",
        "postgres_options": "postgresOptions",
        "service_account_name": "serviceAccountName",
        "service_name": "serviceName",
        "upgrades_service_port": "upgradesServicePort",
    },
)
class MetaflowServiceProps:
    def __init__(
        self,
        *,
        image: typing.Optional[builtins.str] = None,
        ingress_enabled: typing.Optional[builtins.bool] = None,
        ingress_options: typing.Optional[typing.Union[IngressOptions, typing.Dict[str, typing.Any]]] = None,
        metadata_service_port: typing.Optional[jsii.Number] = None,
        postgres_enabled: typing.Optional[builtins.bool] = None,
        postgres_options: typing.Optional[typing.Union["PostgresOptions", typing.Dict[str, typing.Any]]] = None,
        service_account_name: typing.Optional[builtins.str] = None,
        service_name: typing.Optional[builtins.str] = None,
        upgrades_service_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param image: 
        :param ingress_enabled: 
        :param ingress_options: 
        :param metadata_service_port: 
        :param postgres_enabled: 
        :param postgres_options: 
        :param service_account_name: 
        :param service_name: 
        :param upgrades_service_port: 

        :stability: experimental
        '''
        if isinstance(ingress_options, dict):
            ingress_options = IngressOptions(**ingress_options)
        if isinstance(postgres_options, dict):
            postgres_options = PostgresOptions(**postgres_options)
        if __debug__:
            type_hints = typing.get_type_hints(MetaflowServiceProps.__init__)
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument ingress_enabled", value=ingress_enabled, expected_type=type_hints["ingress_enabled"])
            check_type(argname="argument ingress_options", value=ingress_options, expected_type=type_hints["ingress_options"])
            check_type(argname="argument metadata_service_port", value=metadata_service_port, expected_type=type_hints["metadata_service_port"])
            check_type(argname="argument postgres_enabled", value=postgres_enabled, expected_type=type_hints["postgres_enabled"])
            check_type(argname="argument postgres_options", value=postgres_options, expected_type=type_hints["postgres_options"])
            check_type(argname="argument service_account_name", value=service_account_name, expected_type=type_hints["service_account_name"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument upgrades_service_port", value=upgrades_service_port, expected_type=type_hints["upgrades_service_port"])
        self._values: typing.Dict[str, typing.Any] = {}
        if image is not None:
            self._values["image"] = image
        if ingress_enabled is not None:
            self._values["ingress_enabled"] = ingress_enabled
        if ingress_options is not None:
            self._values["ingress_options"] = ingress_options
        if metadata_service_port is not None:
            self._values["metadata_service_port"] = metadata_service_port
        if postgres_enabled is not None:
            self._values["postgres_enabled"] = postgres_enabled
        if postgres_options is not None:
            self._values["postgres_options"] = postgres_options
        if service_account_name is not None:
            self._values["service_account_name"] = service_account_name
        if service_name is not None:
            self._values["service_name"] = service_name
        if upgrades_service_port is not None:
            self._values["upgrades_service_port"] = upgrades_service_port

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ingress_enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ingress_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ingress_options(self) -> typing.Optional[IngressOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ingress_options")
        return typing.cast(typing.Optional[IngressOptions], result)

    @builtins.property
    def metadata_service_port(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("metadata_service_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def postgres_enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("postgres_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def postgres_options(self) -> typing.Optional["PostgresOptions"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("postgres_options")
        return typing.cast(typing.Optional["PostgresOptions"], result)

    @builtins.property
    def service_account_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("service_account_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def upgrades_service_port(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("upgrades_service_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetaflowServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-metaflow.PostgresOptions",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "database_password": "databasePassword",
        "database_user": "databaseUser",
    },
)
class PostgresOptions:
    def __init__(
        self,
        *,
        database_name: typing.Optional[builtins.str] = None,
        database_password: typing.Optional[builtins.str] = None,
        database_user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param database_name: 
        :param database_password: 
        :param database_user: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(PostgresOptions.__init__)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument database_password", value=database_password, expected_type=type_hints["database_password"])
            check_type(argname="argument database_user", value=database_user, expected_type=type_hints["database_user"])
        self._values: typing.Dict[str, typing.Any] = {}
        if database_name is not None:
            self._values["database_name"] = database_name
        if database_password is not None:
            self._values["database_password"] = database_password
        if database_user is not None:
            self._values["database_user"] = database_user

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_password(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_user(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_user")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PostgresOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IngressOptions",
    "MetaflowService",
    "MetaflowServiceProps",
    "PostgresOptions",
    "k8s",
    "minio",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import k8s
from . import minio
