'''
# Terraform CDK time Provider ~> 0.7

This repo builds and publishes the Terraform time Provider bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-time](https://www.npmjs.com/package/@cdktf/provider-time).

`npm install @cdktf/provider-time`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-time](https://pypi.org/project/cdktf-cdktf-provider-time).

`pipenv install cdktf-cdktf-provider-time`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Time](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Time).

`dotnet add package HashiCorp.Cdktf.Providers.Time`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-time](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-time).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-time</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/hashicorp/cdktf-provider-time-go`](https://github.com/hashicorp/cdktf-provider-time-go) package.

`go get github.com/hashicorp/cdktf-provider-time-go/time`

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)
You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-time).

## Versioning

This project is explicitly not tracking the Terraform time Provider version 1:1. In fact, it always tracks `latest` of `~> 0.7` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform time Provider](https://github.com/terraform-providers/terraform-provider-time)
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


class Offset(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-time.Offset",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/time/r/offset time_offset}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        base_rfc3339: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        offset_days: typing.Optional[jsii.Number] = None,
        offset_hours: typing.Optional[jsii.Number] = None,
        offset_minutes: typing.Optional[jsii.Number] = None,
        offset_months: typing.Optional[jsii.Number] = None,
        offset_seconds: typing.Optional[jsii.Number] = None,
        offset_years: typing.Optional[jsii.Number] = None,
        triggers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/time/r/offset time_offset} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param base_rfc3339: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#base_rfc3339 Offset#base_rfc3339}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#id Offset#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param offset_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_days Offset#offset_days}.
        :param offset_hours: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_hours Offset#offset_hours}.
        :param offset_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_minutes Offset#offset_minutes}.
        :param offset_months: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_months Offset#offset_months}.
        :param offset_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_seconds Offset#offset_seconds}.
        :param offset_years: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_years Offset#offset_years}.
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#triggers Offset#triggers}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Offset.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OffsetConfig(
            base_rfc3339=base_rfc3339,
            id=id,
            offset_days=offset_days,
            offset_hours=offset_hours,
            offset_minutes=offset_minutes,
            offset_months=offset_months,
            offset_seconds=offset_seconds,
            offset_years=offset_years,
            triggers=triggers,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetBaseRfc3339")
    def reset_base_rfc3339(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseRfc3339", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOffsetDays")
    def reset_offset_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOffsetDays", []))

    @jsii.member(jsii_name="resetOffsetHours")
    def reset_offset_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOffsetHours", []))

    @jsii.member(jsii_name="resetOffsetMinutes")
    def reset_offset_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOffsetMinutes", []))

    @jsii.member(jsii_name="resetOffsetMonths")
    def reset_offset_months(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOffsetMonths", []))

    @jsii.member(jsii_name="resetOffsetSeconds")
    def reset_offset_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOffsetSeconds", []))

    @jsii.member(jsii_name="resetOffsetYears")
    def reset_offset_years(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOffsetYears", []))

    @jsii.member(jsii_name="resetTriggers")
    def reset_triggers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggers", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="day")
    def day(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "day"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hour")
    def hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hour"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minute")
    def minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="month")
    def month(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "month"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rfc3339")
    def rfc3339(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rfc3339"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="second")
    def second(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "second"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unix")
    def unix(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unix"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="year")
    def year(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "year"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRfc3339Input")
    def base_rfc3339_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseRfc3339Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetDaysInput")
    def offset_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "offsetDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetHoursInput")
    def offset_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "offsetHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetMinutesInput")
    def offset_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "offsetMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetMonthsInput")
    def offset_months_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "offsetMonthsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetSecondsInput")
    def offset_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "offsetSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetYearsInput")
    def offset_years_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "offsetYearsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggersInput")
    def triggers_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "triggersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="baseRfc3339")
    def base_rfc3339(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseRfc3339"))

    @base_rfc3339.setter
    def base_rfc3339(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Offset, "base_rfc3339").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseRfc3339", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Offset, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetDays")
    def offset_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "offsetDays"))

    @offset_days.setter
    def offset_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Offset, "offset_days").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "offsetDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetHours")
    def offset_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "offsetHours"))

    @offset_hours.setter
    def offset_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Offset, "offset_hours").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "offsetHours", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetMinutes")
    def offset_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "offsetMinutes"))

    @offset_minutes.setter
    def offset_minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Offset, "offset_minutes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "offsetMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetMonths")
    def offset_months(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "offsetMonths"))

    @offset_months.setter
    def offset_months(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Offset, "offset_months").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "offsetMonths", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetSeconds")
    def offset_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "offsetSeconds"))

    @offset_seconds.setter
    def offset_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Offset, "offset_seconds").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "offsetSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offsetYears")
    def offset_years(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "offsetYears"))

    @offset_years.setter
    def offset_years(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Offset, "offset_years").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "offsetYears", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggers")
    def triggers(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "triggers"))

    @triggers.setter
    def triggers(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Offset, "triggers").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggers", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-time.OffsetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "base_rfc3339": "baseRfc3339",
        "id": "id",
        "offset_days": "offsetDays",
        "offset_hours": "offsetHours",
        "offset_minutes": "offsetMinutes",
        "offset_months": "offsetMonths",
        "offset_seconds": "offsetSeconds",
        "offset_years": "offsetYears",
        "triggers": "triggers",
    },
)
class OffsetConfig(cdktf.TerraformMetaArguments):
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
        base_rfc3339: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        offset_days: typing.Optional[jsii.Number] = None,
        offset_hours: typing.Optional[jsii.Number] = None,
        offset_minutes: typing.Optional[jsii.Number] = None,
        offset_months: typing.Optional[jsii.Number] = None,
        offset_seconds: typing.Optional[jsii.Number] = None,
        offset_years: typing.Optional[jsii.Number] = None,
        triggers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param base_rfc3339: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#base_rfc3339 Offset#base_rfc3339}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#id Offset#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param offset_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_days Offset#offset_days}.
        :param offset_hours: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_hours Offset#offset_hours}.
        :param offset_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_minutes Offset#offset_minutes}.
        :param offset_months: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_months Offset#offset_months}.
        :param offset_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_seconds Offset#offset_seconds}.
        :param offset_years: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_years Offset#offset_years}.
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#triggers Offset#triggers}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(OffsetConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument base_rfc3339", value=base_rfc3339, expected_type=type_hints["base_rfc3339"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument offset_days", value=offset_days, expected_type=type_hints["offset_days"])
            check_type(argname="argument offset_hours", value=offset_hours, expected_type=type_hints["offset_hours"])
            check_type(argname="argument offset_minutes", value=offset_minutes, expected_type=type_hints["offset_minutes"])
            check_type(argname="argument offset_months", value=offset_months, expected_type=type_hints["offset_months"])
            check_type(argname="argument offset_seconds", value=offset_seconds, expected_type=type_hints["offset_seconds"])
            check_type(argname="argument offset_years", value=offset_years, expected_type=type_hints["offset_years"])
            check_type(argname="argument triggers", value=triggers, expected_type=type_hints["triggers"])
        self._values: typing.Dict[str, typing.Any] = {}
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
        if base_rfc3339 is not None:
            self._values["base_rfc3339"] = base_rfc3339
        if id is not None:
            self._values["id"] = id
        if offset_days is not None:
            self._values["offset_days"] = offset_days
        if offset_hours is not None:
            self._values["offset_hours"] = offset_hours
        if offset_minutes is not None:
            self._values["offset_minutes"] = offset_minutes
        if offset_months is not None:
            self._values["offset_months"] = offset_months
        if offset_seconds is not None:
            self._values["offset_seconds"] = offset_seconds
        if offset_years is not None:
            self._values["offset_years"] = offset_years
        if triggers is not None:
            self._values["triggers"] = triggers

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
    def base_rfc3339(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#base_rfc3339 Offset#base_rfc3339}.'''
        result = self._values.get("base_rfc3339")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#id Offset#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def offset_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_days Offset#offset_days}.'''
        result = self._values.get("offset_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offset_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_hours Offset#offset_hours}.'''
        result = self._values.get("offset_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offset_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_minutes Offset#offset_minutes}.'''
        result = self._values.get("offset_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offset_months(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_months Offset#offset_months}.'''
        result = self._values.get("offset_months")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offset_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_seconds Offset#offset_seconds}.'''
        result = self._values.get("offset_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offset_years(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#offset_years Offset#offset_years}.'''
        result = self._values.get("offset_years")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def triggers(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/offset#triggers Offset#triggers}.'''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OffsetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Rotating(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-time.Rotating",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/time/r/rotating time_rotating}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        rfc3339: typing.Optional[builtins.str] = None,
        rotation_days: typing.Optional[jsii.Number] = None,
        rotation_hours: typing.Optional[jsii.Number] = None,
        rotation_minutes: typing.Optional[jsii.Number] = None,
        rotation_months: typing.Optional[jsii.Number] = None,
        rotation_rfc3339: typing.Optional[builtins.str] = None,
        rotation_years: typing.Optional[jsii.Number] = None,
        triggers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/time/r/rotating time_rotating} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#id Rotating#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rfc3339: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rfc3339 Rotating#rfc3339}.
        :param rotation_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_days Rotating#rotation_days}.
        :param rotation_hours: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_hours Rotating#rotation_hours}.
        :param rotation_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_minutes Rotating#rotation_minutes}.
        :param rotation_months: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_months Rotating#rotation_months}.
        :param rotation_rfc3339: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_rfc3339 Rotating#rotation_rfc3339}.
        :param rotation_years: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_years Rotating#rotation_years}.
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#triggers Rotating#triggers}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Rotating.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RotatingConfig(
            id=id,
            rfc3339=rfc3339,
            rotation_days=rotation_days,
            rotation_hours=rotation_hours,
            rotation_minutes=rotation_minutes,
            rotation_months=rotation_months,
            rotation_rfc3339=rotation_rfc3339,
            rotation_years=rotation_years,
            triggers=triggers,
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

    @jsii.member(jsii_name="resetRfc3339")
    def reset_rfc3339(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRfc3339", []))

    @jsii.member(jsii_name="resetRotationDays")
    def reset_rotation_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationDays", []))

    @jsii.member(jsii_name="resetRotationHours")
    def reset_rotation_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationHours", []))

    @jsii.member(jsii_name="resetRotationMinutes")
    def reset_rotation_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationMinutes", []))

    @jsii.member(jsii_name="resetRotationMonths")
    def reset_rotation_months(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationMonths", []))

    @jsii.member(jsii_name="resetRotationRfc3339")
    def reset_rotation_rfc3339(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationRfc3339", []))

    @jsii.member(jsii_name="resetRotationYears")
    def reset_rotation_years(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationYears", []))

    @jsii.member(jsii_name="resetTriggers")
    def reset_triggers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggers", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="day")
    def day(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "day"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hour")
    def hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hour"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minute")
    def minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="month")
    def month(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "month"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="second")
    def second(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "second"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unix")
    def unix(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unix"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="year")
    def year(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "year"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rfc3339Input")
    def rfc3339_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rfc3339Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationDaysInput")
    def rotation_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationHoursInput")
    def rotation_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationMinutesInput")
    def rotation_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationMonthsInput")
    def rotation_months_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationMonthsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationRfc3339Input")
    def rotation_rfc3339_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotationRfc3339Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationYearsInput")
    def rotation_years_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationYearsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggersInput")
    def triggers_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "triggersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Rotating, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rfc3339")
    def rfc3339(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rfc3339"))

    @rfc3339.setter
    def rfc3339(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Rotating, "rfc3339").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rfc3339", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationDays")
    def rotation_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationDays"))

    @rotation_days.setter
    def rotation_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Rotating, "rotation_days").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationHours")
    def rotation_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationHours"))

    @rotation_hours.setter
    def rotation_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Rotating, "rotation_hours").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationHours", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationMinutes")
    def rotation_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationMinutes"))

    @rotation_minutes.setter
    def rotation_minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Rotating, "rotation_minutes").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationMonths")
    def rotation_months(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationMonths"))

    @rotation_months.setter
    def rotation_months(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Rotating, "rotation_months").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationMonths", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationRfc3339")
    def rotation_rfc3339(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationRfc3339"))

    @rotation_rfc3339.setter
    def rotation_rfc3339(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Rotating, "rotation_rfc3339").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationRfc3339", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rotationYears")
    def rotation_years(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationYears"))

    @rotation_years.setter
    def rotation_years(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Rotating, "rotation_years").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationYears", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggers")
    def triggers(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "triggers"))

    @triggers.setter
    def triggers(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Rotating, "triggers").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggers", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-time.RotatingConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "id": "id",
        "rfc3339": "rfc3339",
        "rotation_days": "rotationDays",
        "rotation_hours": "rotationHours",
        "rotation_minutes": "rotationMinutes",
        "rotation_months": "rotationMonths",
        "rotation_rfc3339": "rotationRfc3339",
        "rotation_years": "rotationYears",
        "triggers": "triggers",
    },
)
class RotatingConfig(cdktf.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        rfc3339: typing.Optional[builtins.str] = None,
        rotation_days: typing.Optional[jsii.Number] = None,
        rotation_hours: typing.Optional[jsii.Number] = None,
        rotation_minutes: typing.Optional[jsii.Number] = None,
        rotation_months: typing.Optional[jsii.Number] = None,
        rotation_rfc3339: typing.Optional[builtins.str] = None,
        rotation_years: typing.Optional[jsii.Number] = None,
        triggers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#id Rotating#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rfc3339: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rfc3339 Rotating#rfc3339}.
        :param rotation_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_days Rotating#rotation_days}.
        :param rotation_hours: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_hours Rotating#rotation_hours}.
        :param rotation_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_minutes Rotating#rotation_minutes}.
        :param rotation_months: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_months Rotating#rotation_months}.
        :param rotation_rfc3339: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_rfc3339 Rotating#rotation_rfc3339}.
        :param rotation_years: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_years Rotating#rotation_years}.
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#triggers Rotating#triggers}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(RotatingConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument rfc3339", value=rfc3339, expected_type=type_hints["rfc3339"])
            check_type(argname="argument rotation_days", value=rotation_days, expected_type=type_hints["rotation_days"])
            check_type(argname="argument rotation_hours", value=rotation_hours, expected_type=type_hints["rotation_hours"])
            check_type(argname="argument rotation_minutes", value=rotation_minutes, expected_type=type_hints["rotation_minutes"])
            check_type(argname="argument rotation_months", value=rotation_months, expected_type=type_hints["rotation_months"])
            check_type(argname="argument rotation_rfc3339", value=rotation_rfc3339, expected_type=type_hints["rotation_rfc3339"])
            check_type(argname="argument rotation_years", value=rotation_years, expected_type=type_hints["rotation_years"])
            check_type(argname="argument triggers", value=triggers, expected_type=type_hints["triggers"])
        self._values: typing.Dict[str, typing.Any] = {}
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
        if rfc3339 is not None:
            self._values["rfc3339"] = rfc3339
        if rotation_days is not None:
            self._values["rotation_days"] = rotation_days
        if rotation_hours is not None:
            self._values["rotation_hours"] = rotation_hours
        if rotation_minutes is not None:
            self._values["rotation_minutes"] = rotation_minutes
        if rotation_months is not None:
            self._values["rotation_months"] = rotation_months
        if rotation_rfc3339 is not None:
            self._values["rotation_rfc3339"] = rotation_rfc3339
        if rotation_years is not None:
            self._values["rotation_years"] = rotation_years
        if triggers is not None:
            self._values["triggers"] = triggers

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
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#id Rotating#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rfc3339(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rfc3339 Rotating#rfc3339}.'''
        result = self._values.get("rfc3339")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_days Rotating#rotation_days}.'''
        result = self._values.get("rotation_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_hours Rotating#rotation_hours}.'''
        result = self._values.get("rotation_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_minutes Rotating#rotation_minutes}.'''
        result = self._values.get("rotation_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_months(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_months Rotating#rotation_months}.'''
        result = self._values.get("rotation_months")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_rfc3339(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_rfc3339 Rotating#rotation_rfc3339}.'''
        result = self._values.get("rotation_rfc3339")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_years(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#rotation_years Rotating#rotation_years}.'''
        result = self._values.get("rotation_years")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def triggers(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/rotating#triggers Rotating#triggers}.'''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RotatingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Sleep(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-time.Sleep",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/time/r/sleep time_sleep}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        create_duration: typing.Optional[builtins.str] = None,
        destroy_duration: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        triggers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/time/r/sleep time_sleep} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param create_duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#create_duration Sleep#create_duration}.
        :param destroy_duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#destroy_duration Sleep#destroy_duration}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#id Sleep#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#triggers Sleep#triggers}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Sleep.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = SleepConfig(
            create_duration=create_duration,
            destroy_duration=destroy_duration,
            id=id,
            triggers=triggers,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetCreateDuration")
    def reset_create_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateDuration", []))

    @jsii.member(jsii_name="resetDestroyDuration")
    def reset_destroy_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestroyDuration", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTriggers")
    def reset_triggers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggers", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createDurationInput")
    def create_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createDurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destroyDurationInput")
    def destroy_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destroyDurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggersInput")
    def triggers_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "triggersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createDuration")
    def create_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createDuration"))

    @create_duration.setter
    def create_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Sleep, "create_duration").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createDuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destroyDuration")
    def destroy_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destroyDuration"))

    @destroy_duration.setter
    def destroy_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Sleep, "destroy_duration").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destroyDuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Sleep, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggers")
    def triggers(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "triggers"))

    @triggers.setter
    def triggers(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Sleep, "triggers").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggers", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-time.SleepConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "create_duration": "createDuration",
        "destroy_duration": "destroyDuration",
        "id": "id",
        "triggers": "triggers",
    },
)
class SleepConfig(cdktf.TerraformMetaArguments):
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
        create_duration: typing.Optional[builtins.str] = None,
        destroy_duration: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        triggers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param create_duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#create_duration Sleep#create_duration}.
        :param destroy_duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#destroy_duration Sleep#destroy_duration}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#id Sleep#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#triggers Sleep#triggers}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(SleepConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument create_duration", value=create_duration, expected_type=type_hints["create_duration"])
            check_type(argname="argument destroy_duration", value=destroy_duration, expected_type=type_hints["destroy_duration"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument triggers", value=triggers, expected_type=type_hints["triggers"])
        self._values: typing.Dict[str, typing.Any] = {}
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
        if create_duration is not None:
            self._values["create_duration"] = create_duration
        if destroy_duration is not None:
            self._values["destroy_duration"] = destroy_duration
        if id is not None:
            self._values["id"] = id
        if triggers is not None:
            self._values["triggers"] = triggers

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
    def create_duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#create_duration Sleep#create_duration}.'''
        result = self._values.get("create_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destroy_duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#destroy_duration Sleep#destroy_duration}.'''
        result = self._values.get("destroy_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#id Sleep#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def triggers(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/sleep#triggers Sleep#triggers}.'''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SleepConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Static(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-time.Static",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/time/r/static time_static}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        rfc3339: typing.Optional[builtins.str] = None,
        triggers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/time/r/static time_static} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/static#id Static#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rfc3339: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/static#rfc3339 Static#rfc3339}.
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/static#triggers Static#triggers}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Static.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = StaticConfig(
            id=id,
            rfc3339=rfc3339,
            triggers=triggers,
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

    @jsii.member(jsii_name="resetRfc3339")
    def reset_rfc3339(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRfc3339", []))

    @jsii.member(jsii_name="resetTriggers")
    def reset_triggers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggers", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="day")
    def day(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "day"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hour")
    def hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hour"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minute")
    def minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="month")
    def month(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "month"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="second")
    def second(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "second"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unix")
    def unix(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unix"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="year")
    def year(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "year"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rfc3339Input")
    def rfc3339_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rfc3339Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggersInput")
    def triggers_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "triggersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Static, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rfc3339")
    def rfc3339(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rfc3339"))

    @rfc3339.setter
    def rfc3339(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Static, "rfc3339").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rfc3339", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggers")
    def triggers(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "triggers"))

    @triggers.setter
    def triggers(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Static, "triggers").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggers", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-time.StaticConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "id": "id",
        "rfc3339": "rfc3339",
        "triggers": "triggers",
    },
)
class StaticConfig(cdktf.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        rfc3339: typing.Optional[builtins.str] = None,
        triggers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/static#id Static#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rfc3339: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/static#rfc3339 Static#rfc3339}.
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/static#triggers Static#triggers}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(StaticConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument rfc3339", value=rfc3339, expected_type=type_hints["rfc3339"])
            check_type(argname="argument triggers", value=triggers, expected_type=type_hints["triggers"])
        self._values: typing.Dict[str, typing.Any] = {}
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
        if rfc3339 is not None:
            self._values["rfc3339"] = rfc3339
        if triggers is not None:
            self._values["triggers"] = triggers

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
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/static#id Static#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rfc3339(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/static#rfc3339 Static#rfc3339}.'''
        result = self._values.get("rfc3339")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def triggers(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time/r/static#triggers Static#triggers}.'''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaticConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TimeProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-time.TimeProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/time time}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/time time} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time#alias TimeProvider#alias}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TimeProvider.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = TimeProviderConfig(alias=alias)

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
            type_hints = typing.get_type_hints(getattr(TimeProvider, "alias").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-time.TimeProviderConfig",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias"},
)
class TimeProviderConfig:
    def __init__(self, *, alias: typing.Optional[builtins.str] = None) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time#alias TimeProvider#alias}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(TimeProviderConfig.__init__)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/time#alias TimeProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimeProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Offset",
    "OffsetConfig",
    "Rotating",
    "RotatingConfig",
    "Sleep",
    "SleepConfig",
    "Static",
    "StaticConfig",
    "TimeProvider",
    "TimeProviderConfig",
]

publication.publish()
