'''
---


### ✨ Have you heard of <a href="https://github.com/cdklabs/cdk-monitoring-constructs">cdk-monitoring-constructs</a>? ✨</span>

Watchful on steroids. Check it out! 🔝

---


# cdk-watchful

> Watching your CDK back since 2019

Watchful is an [AWS CDK](https://github.com/awslabs/aws-cdk) construct library that makes it easy
to monitor CDK apps. It automatically synthesizes alarms and dashboards for supported AWS resources.

```python
import { Watchful } from 'cdk-watchful'

const wf = new Watchful(this, 'watchful');
wf.watchDynamoTable('My Cute Little Table', myTable);
wf.watchLambdaFunction('My Function', myFunction);
wf.watchApiGateway('My REST API', myRestApi);
```

And...

![](https://raw.githubusercontent.com/eladb/cdk-watchful/master/example/sample.png)

## Initialize

To get started, just define a `Watchful` construct in your CDK app.
You can initialize using an email address, SQS ARN or both:

```python
import { Watchful } from 'cdk-watchful'
import * as sns from 'aws-cdk-lib/aws-sns';
import * as sqs from 'aws-cdk-lib/aws-sqs';

const alarmSqs = sqs.Queue.fromQueueArn(this, 'AlarmQueue', 'arn:aws:sqs:us-east-1:444455556666:alarm-queue')
const alarmSns = sns.Topic.fromTopicArn(this, 'AlarmTopic', 'arn:aws:sns:us-east-2:444455556666:MyTopic');

const wf = new Watchful(this, 'watchful', {
  alarmEmail: 'your@email.com',
  alarmSqs,
  alarmSns,
  alarmActionArns: [ 'arn:aws:sqs:us-east-1:444455556666:alarm-queue' ]
});
```

## Add Resources

Watchful manages a central dashboard and configures default alarming for:

* Amazon DynamoDB: `watchful.watchDynamoTable`
* AWS Lambda: `watchful.watchLambdaFunction`
* Amazon API Gateway: `watchful.watchApiGateway`
* [Request yours](https://github.com/eladb/cdk-watchful/issues/new)

## Watching Scopes

Watchful can also watch complete CDK construct scopes. It will automatically
discover all watchable resources within that scope (recursively), add them
to your dashboard and configure alarms for them.

```python
wf.watchScope(storageLayer);
```

## Example

See a more complete [example](https://github.com/eladb/cdk-watchful/blob/master/example/index.ts).

## Contributing

Contributions of all kinds are welcome and celebrated. Raise an issue, submit a PR, do the right thing.

To set up a dev environment:

1. Clone this repo
2. `yarn`

Development workflow (change code and run tests automatically):

```shell
yarn test:watch
```

Build (like CI):

```shell
yarn build
```

And then publish as a PR.

## License

[Apache 2.0](https://github.com/eladb/cdk-watchful/blob/master/LICENSE)
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
import aws_cdk.aws_apigateway
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_dynamodb
import aws_cdk.aws_ecs
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_lambda
import aws_cdk.aws_rds
import aws_cdk.aws_sns
import aws_cdk.aws_sqs
import aws_cdk.aws_stepfunctions
import constructs


@jsii.interface(jsii_type="cdk-watchful.IWatchful")
class IWatchful(typing_extensions.Protocol):
    @jsii.member(jsii_name="addAlarm")
    def add_alarm(self, alarm: aws_cdk.aws_cloudwatch.IAlarm) -> None:
        '''
        :param alarm: -
        '''
        ...

    @jsii.member(jsii_name="addSection")
    def add_section(
        self,
        title: builtins.str,
        *,
        links: typing.Optional[typing.Sequence[typing.Union["QuickLink", typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param title: -
        :param links: 
        '''
        ...

    @jsii.member(jsii_name="addWidgets")
    def add_widgets(self, *widgets: aws_cdk.aws_cloudwatch.IWidget) -> None:
        '''
        :param widgets: -
        '''
        ...


class _IWatchfulProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-watchful.IWatchful"

    @jsii.member(jsii_name="addAlarm")
    def add_alarm(self, alarm: aws_cdk.aws_cloudwatch.IAlarm) -> None:
        '''
        :param alarm: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(IWatchful.add_alarm)
            check_type(argname="argument alarm", value=alarm, expected_type=type_hints["alarm"])
        return typing.cast(None, jsii.invoke(self, "addAlarm", [alarm]))

    @jsii.member(jsii_name="addSection")
    def add_section(
        self,
        title: builtins.str,
        *,
        links: typing.Optional[typing.Sequence[typing.Union["QuickLink", typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param title: -
        :param links: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(IWatchful.add_section)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
        options = SectionOptions(links=links)

        return typing.cast(None, jsii.invoke(self, "addSection", [title, options]))

    @jsii.member(jsii_name="addWidgets")
    def add_widgets(self, *widgets: aws_cdk.aws_cloudwatch.IWidget) -> None:
        '''
        :param widgets: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(IWatchful.add_widgets)
            check_type(argname="argument widgets", value=widgets, expected_type=typing.Tuple[type_hints["widgets"], ...])
        return typing.cast(None, jsii.invoke(self, "addWidgets", [*widgets]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWatchful).__jsii_proxy_class__ = lambda : _IWatchfulProxy


@jsii.data_type(
    jsii_type="cdk-watchful.QuickLink",
    jsii_struct_bases=[],
    name_mapping={"title": "title", "url": "url"},
)
class QuickLink:
    def __init__(self, *, title: builtins.str, url: builtins.str) -> None:
        '''
        :param title: 
        :param url: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(QuickLink.__init__)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        self._values: typing.Dict[str, typing.Any] = {
            "title": title,
            "url": url,
        }

    @builtins.property
    def title(self) -> builtins.str:
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuickLink(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-watchful.SectionOptions",
    jsii_struct_bases=[],
    name_mapping={"links": "links"},
)
class SectionOptions:
    def __init__(
        self,
        *,
        links: typing.Optional[typing.Sequence[typing.Union[QuickLink, typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param links: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(SectionOptions.__init__)
            check_type(argname="argument links", value=links, expected_type=type_hints["links"])
        self._values: typing.Dict[str, typing.Any] = {}
        if links is not None:
            self._values["links"] = links

    @builtins.property
    def links(self) -> typing.Optional[typing.List[QuickLink]]:
        result = self._values.get("links")
        return typing.cast(typing.Optional[typing.List[QuickLink]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SectionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WatchApiGateway(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-watchful.WatchApiGateway",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        rest_api: aws_cdk.aws_apigateway.RestApi,
        title: builtins.str,
        watchful: IWatchful,
        cache_graph: typing.Optional[builtins.bool] = None,
        server_error_threshold: typing.Optional[jsii.Number] = None,
        watched_operations: typing.Optional[typing.Sequence[typing.Union["WatchedOperation", typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param rest_api: The API Gateway REST API that is being watched.
        :param title: The title of this section.
        :param watchful: The Watchful instance to add widgets into.
        :param cache_graph: Include a dashboard graph for caching metrics. Default: false
        :param server_error_threshold: Alarm when 5XX errors reach this threshold over 5 minutes. Default: 1 any 5xx HTTP response will trigger the alarm
        :param watched_operations: A list of operations to monitor separately. Default: - only API-level monitoring is added.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchApiGateway.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WatchApiGatewayProps(
            rest_api=rest_api,
            title=title,
            watchful=watchful,
            cache_graph=cache_graph,
            server_error_threshold=server_error_threshold,
            watched_operations=watched_operations,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-watchful.WatchApiGatewayOptions",
    jsii_struct_bases=[],
    name_mapping={
        "cache_graph": "cacheGraph",
        "server_error_threshold": "serverErrorThreshold",
        "watched_operations": "watchedOperations",
    },
)
class WatchApiGatewayOptions:
    def __init__(
        self,
        *,
        cache_graph: typing.Optional[builtins.bool] = None,
        server_error_threshold: typing.Optional[jsii.Number] = None,
        watched_operations: typing.Optional[typing.Sequence[typing.Union["WatchedOperation", typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param cache_graph: Include a dashboard graph for caching metrics. Default: false
        :param server_error_threshold: Alarm when 5XX errors reach this threshold over 5 minutes. Default: 1 any 5xx HTTP response will trigger the alarm
        :param watched_operations: A list of operations to monitor separately. Default: - only API-level monitoring is added.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchApiGatewayOptions.__init__)
            check_type(argname="argument cache_graph", value=cache_graph, expected_type=type_hints["cache_graph"])
            check_type(argname="argument server_error_threshold", value=server_error_threshold, expected_type=type_hints["server_error_threshold"])
            check_type(argname="argument watched_operations", value=watched_operations, expected_type=type_hints["watched_operations"])
        self._values: typing.Dict[str, typing.Any] = {}
        if cache_graph is not None:
            self._values["cache_graph"] = cache_graph
        if server_error_threshold is not None:
            self._values["server_error_threshold"] = server_error_threshold
        if watched_operations is not None:
            self._values["watched_operations"] = watched_operations

    @builtins.property
    def cache_graph(self) -> typing.Optional[builtins.bool]:
        '''Include a dashboard graph for caching metrics.

        :default: false
        '''
        result = self._values.get("cache_graph")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def server_error_threshold(self) -> typing.Optional[jsii.Number]:
        '''Alarm when 5XX errors reach this threshold over 5 minutes.

        :default: 1 any 5xx HTTP response will trigger the alarm
        '''
        result = self._values.get("server_error_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def watched_operations(self) -> typing.Optional[typing.List["WatchedOperation"]]:
        '''A list of operations to monitor separately.

        :default: - only API-level monitoring is added.
        '''
        result = self._values.get("watched_operations")
        return typing.cast(typing.Optional[typing.List["WatchedOperation"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchApiGatewayOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-watchful.WatchApiGatewayProps",
    jsii_struct_bases=[WatchApiGatewayOptions],
    name_mapping={
        "cache_graph": "cacheGraph",
        "server_error_threshold": "serverErrorThreshold",
        "watched_operations": "watchedOperations",
        "rest_api": "restApi",
        "title": "title",
        "watchful": "watchful",
    },
)
class WatchApiGatewayProps(WatchApiGatewayOptions):
    def __init__(
        self,
        *,
        cache_graph: typing.Optional[builtins.bool] = None,
        server_error_threshold: typing.Optional[jsii.Number] = None,
        watched_operations: typing.Optional[typing.Sequence[typing.Union["WatchedOperation", typing.Dict[str, typing.Any]]]] = None,
        rest_api: aws_cdk.aws_apigateway.RestApi,
        title: builtins.str,
        watchful: IWatchful,
    ) -> None:
        '''
        :param cache_graph: Include a dashboard graph for caching metrics. Default: false
        :param server_error_threshold: Alarm when 5XX errors reach this threshold over 5 minutes. Default: 1 any 5xx HTTP response will trigger the alarm
        :param watched_operations: A list of operations to monitor separately. Default: - only API-level monitoring is added.
        :param rest_api: The API Gateway REST API that is being watched.
        :param title: The title of this section.
        :param watchful: The Watchful instance to add widgets into.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchApiGatewayProps.__init__)
            check_type(argname="argument cache_graph", value=cache_graph, expected_type=type_hints["cache_graph"])
            check_type(argname="argument server_error_threshold", value=server_error_threshold, expected_type=type_hints["server_error_threshold"])
            check_type(argname="argument watched_operations", value=watched_operations, expected_type=type_hints["watched_operations"])
            check_type(argname="argument rest_api", value=rest_api, expected_type=type_hints["rest_api"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument watchful", value=watchful, expected_type=type_hints["watchful"])
        self._values: typing.Dict[str, typing.Any] = {
            "rest_api": rest_api,
            "title": title,
            "watchful": watchful,
        }
        if cache_graph is not None:
            self._values["cache_graph"] = cache_graph
        if server_error_threshold is not None:
            self._values["server_error_threshold"] = server_error_threshold
        if watched_operations is not None:
            self._values["watched_operations"] = watched_operations

    @builtins.property
    def cache_graph(self) -> typing.Optional[builtins.bool]:
        '''Include a dashboard graph for caching metrics.

        :default: false
        '''
        result = self._values.get("cache_graph")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def server_error_threshold(self) -> typing.Optional[jsii.Number]:
        '''Alarm when 5XX errors reach this threshold over 5 minutes.

        :default: 1 any 5xx HTTP response will trigger the alarm
        '''
        result = self._values.get("server_error_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def watched_operations(self) -> typing.Optional[typing.List["WatchedOperation"]]:
        '''A list of operations to monitor separately.

        :default: - only API-level monitoring is added.
        '''
        result = self._values.get("watched_operations")
        return typing.cast(typing.Optional[typing.List["WatchedOperation"]], result)

    @builtins.property
    def rest_api(self) -> aws_cdk.aws_apigateway.RestApi:
        '''The API Gateway REST API that is being watched.'''
        result = self._values.get("rest_api")
        assert result is not None, "Required property 'rest_api' is missing"
        return typing.cast(aws_cdk.aws_apigateway.RestApi, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''The title of this section.'''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def watchful(self) -> IWatchful:
        '''The Watchful instance to add widgets into.'''
        result = self._values.get("watchful")
        assert result is not None, "Required property 'watchful' is missing"
        return typing.cast(IWatchful, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchApiGatewayProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WatchDynamoTable(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-watchful.WatchDynamoTable",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        table: aws_cdk.aws_dynamodb.Table,
        title: builtins.str,
        watchful: IWatchful,
        read_capacity_threshold_percent: typing.Optional[jsii.Number] = None,
        write_capacity_threshold_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param table: 
        :param title: 
        :param watchful: 
        :param read_capacity_threshold_percent: Threshold for read capacity alarm (percentage). Default: 80
        :param write_capacity_threshold_percent: Threshold for read capacity alarm (percentage). Default: 80
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchDynamoTable.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WatchDynamoTableProps(
            table=table,
            title=title,
            watchful=watchful,
            read_capacity_threshold_percent=read_capacity_threshold_percent,
            write_capacity_threshold_percent=write_capacity_threshold_percent,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-watchful.WatchDynamoTableOptions",
    jsii_struct_bases=[],
    name_mapping={
        "read_capacity_threshold_percent": "readCapacityThresholdPercent",
        "write_capacity_threshold_percent": "writeCapacityThresholdPercent",
    },
)
class WatchDynamoTableOptions:
    def __init__(
        self,
        *,
        read_capacity_threshold_percent: typing.Optional[jsii.Number] = None,
        write_capacity_threshold_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param read_capacity_threshold_percent: Threshold for read capacity alarm (percentage). Default: 80
        :param write_capacity_threshold_percent: Threshold for read capacity alarm (percentage). Default: 80
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchDynamoTableOptions.__init__)
            check_type(argname="argument read_capacity_threshold_percent", value=read_capacity_threshold_percent, expected_type=type_hints["read_capacity_threshold_percent"])
            check_type(argname="argument write_capacity_threshold_percent", value=write_capacity_threshold_percent, expected_type=type_hints["write_capacity_threshold_percent"])
        self._values: typing.Dict[str, typing.Any] = {}
        if read_capacity_threshold_percent is not None:
            self._values["read_capacity_threshold_percent"] = read_capacity_threshold_percent
        if write_capacity_threshold_percent is not None:
            self._values["write_capacity_threshold_percent"] = write_capacity_threshold_percent

    @builtins.property
    def read_capacity_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for read capacity alarm (percentage).

        :default: 80
        '''
        result = self._values.get("read_capacity_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def write_capacity_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for read capacity alarm (percentage).

        :default: 80
        '''
        result = self._values.get("write_capacity_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchDynamoTableOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-watchful.WatchDynamoTableProps",
    jsii_struct_bases=[WatchDynamoTableOptions],
    name_mapping={
        "read_capacity_threshold_percent": "readCapacityThresholdPercent",
        "write_capacity_threshold_percent": "writeCapacityThresholdPercent",
        "table": "table",
        "title": "title",
        "watchful": "watchful",
    },
)
class WatchDynamoTableProps(WatchDynamoTableOptions):
    def __init__(
        self,
        *,
        read_capacity_threshold_percent: typing.Optional[jsii.Number] = None,
        write_capacity_threshold_percent: typing.Optional[jsii.Number] = None,
        table: aws_cdk.aws_dynamodb.Table,
        title: builtins.str,
        watchful: IWatchful,
    ) -> None:
        '''
        :param read_capacity_threshold_percent: Threshold for read capacity alarm (percentage). Default: 80
        :param write_capacity_threshold_percent: Threshold for read capacity alarm (percentage). Default: 80
        :param table: 
        :param title: 
        :param watchful: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchDynamoTableProps.__init__)
            check_type(argname="argument read_capacity_threshold_percent", value=read_capacity_threshold_percent, expected_type=type_hints["read_capacity_threshold_percent"])
            check_type(argname="argument write_capacity_threshold_percent", value=write_capacity_threshold_percent, expected_type=type_hints["write_capacity_threshold_percent"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument watchful", value=watchful, expected_type=type_hints["watchful"])
        self._values: typing.Dict[str, typing.Any] = {
            "table": table,
            "title": title,
            "watchful": watchful,
        }
        if read_capacity_threshold_percent is not None:
            self._values["read_capacity_threshold_percent"] = read_capacity_threshold_percent
        if write_capacity_threshold_percent is not None:
            self._values["write_capacity_threshold_percent"] = write_capacity_threshold_percent

    @builtins.property
    def read_capacity_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for read capacity alarm (percentage).

        :default: 80
        '''
        result = self._values.get("read_capacity_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def write_capacity_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for read capacity alarm (percentage).

        :default: 80
        '''
        result = self._values.get("write_capacity_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def table(self) -> aws_cdk.aws_dynamodb.Table:
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(aws_cdk.aws_dynamodb.Table, result)

    @builtins.property
    def title(self) -> builtins.str:
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def watchful(self) -> IWatchful:
        result = self._values.get("watchful")
        assert result is not None, "Required property 'watchful' is missing"
        return typing.cast(IWatchful, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchDynamoTableProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WatchEcsService(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-watchful.WatchEcsService",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        target_group: aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup,
        title: builtins.str,
        watchful: IWatchful,
        ec2_service: typing.Optional[aws_cdk.aws_ecs.Ec2Service] = None,
        fargate_service: typing.Optional[aws_cdk.aws_ecs.FargateService] = None,
        cpu_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        memory_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        requests_error_rate_threshold: typing.Optional[jsii.Number] = None,
        requests_threshold: typing.Optional[jsii.Number] = None,
        target_response_time_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param target_group: 
        :param title: 
        :param watchful: 
        :param ec2_service: 
        :param fargate_service: 
        :param cpu_maximum_threshold_percent: Threshold for the Cpu Maximum utilization. Default: 80
        :param memory_maximum_threshold_percent: Threshold for the Memory Maximum utilization. Default: - 0.
        :param requests_error_rate_threshold: Threshold for the Number of Request Errors. Default: - 0.
        :param requests_threshold: Threshold for the Number of Requests. Default: - 0.
        :param target_response_time_threshold: Threshold for the Target Response Time. Default: - 0.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchEcsService.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WatchEcsServiceProps(
            target_group=target_group,
            title=title,
            watchful=watchful,
            ec2_service=ec2_service,
            fargate_service=fargate_service,
            cpu_maximum_threshold_percent=cpu_maximum_threshold_percent,
            memory_maximum_threshold_percent=memory_maximum_threshold_percent,
            requests_error_rate_threshold=requests_error_rate_threshold,
            requests_threshold=requests_threshold,
            target_response_time_threshold=target_response_time_threshold,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-watchful.WatchEcsServiceOptions",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_maximum_threshold_percent": "cpuMaximumThresholdPercent",
        "memory_maximum_threshold_percent": "memoryMaximumThresholdPercent",
        "requests_error_rate_threshold": "requestsErrorRateThreshold",
        "requests_threshold": "requestsThreshold",
        "target_response_time_threshold": "targetResponseTimeThreshold",
    },
)
class WatchEcsServiceOptions:
    def __init__(
        self,
        *,
        cpu_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        memory_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        requests_error_rate_threshold: typing.Optional[jsii.Number] = None,
        requests_threshold: typing.Optional[jsii.Number] = None,
        target_response_time_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_maximum_threshold_percent: Threshold for the Cpu Maximum utilization. Default: 80
        :param memory_maximum_threshold_percent: Threshold for the Memory Maximum utilization. Default: - 0.
        :param requests_error_rate_threshold: Threshold for the Number of Request Errors. Default: - 0.
        :param requests_threshold: Threshold for the Number of Requests. Default: - 0.
        :param target_response_time_threshold: Threshold for the Target Response Time. Default: - 0.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchEcsServiceOptions.__init__)
            check_type(argname="argument cpu_maximum_threshold_percent", value=cpu_maximum_threshold_percent, expected_type=type_hints["cpu_maximum_threshold_percent"])
            check_type(argname="argument memory_maximum_threshold_percent", value=memory_maximum_threshold_percent, expected_type=type_hints["memory_maximum_threshold_percent"])
            check_type(argname="argument requests_error_rate_threshold", value=requests_error_rate_threshold, expected_type=type_hints["requests_error_rate_threshold"])
            check_type(argname="argument requests_threshold", value=requests_threshold, expected_type=type_hints["requests_threshold"])
            check_type(argname="argument target_response_time_threshold", value=target_response_time_threshold, expected_type=type_hints["target_response_time_threshold"])
        self._values: typing.Dict[str, typing.Any] = {}
        if cpu_maximum_threshold_percent is not None:
            self._values["cpu_maximum_threshold_percent"] = cpu_maximum_threshold_percent
        if memory_maximum_threshold_percent is not None:
            self._values["memory_maximum_threshold_percent"] = memory_maximum_threshold_percent
        if requests_error_rate_threshold is not None:
            self._values["requests_error_rate_threshold"] = requests_error_rate_threshold
        if requests_threshold is not None:
            self._values["requests_threshold"] = requests_threshold
        if target_response_time_threshold is not None:
            self._values["target_response_time_threshold"] = target_response_time_threshold

    @builtins.property
    def cpu_maximum_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Cpu Maximum utilization.

        :default: 80
        '''
        result = self._values.get("cpu_maximum_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_maximum_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Memory Maximum utilization.

        :default:

        -
        0.
        '''
        result = self._values.get("memory_maximum_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def requests_error_rate_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Number of Request Errors.

        :default:

        -
        0.
        '''
        result = self._values.get("requests_error_rate_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def requests_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Number of Requests.

        :default:

        -
        0.
        '''
        result = self._values.get("requests_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_response_time_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Target Response Time.

        :default:

        -
        0.
        '''
        result = self._values.get("target_response_time_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchEcsServiceOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-watchful.WatchEcsServiceProps",
    jsii_struct_bases=[WatchEcsServiceOptions],
    name_mapping={
        "cpu_maximum_threshold_percent": "cpuMaximumThresholdPercent",
        "memory_maximum_threshold_percent": "memoryMaximumThresholdPercent",
        "requests_error_rate_threshold": "requestsErrorRateThreshold",
        "requests_threshold": "requestsThreshold",
        "target_response_time_threshold": "targetResponseTimeThreshold",
        "target_group": "targetGroup",
        "title": "title",
        "watchful": "watchful",
        "ec2_service": "ec2Service",
        "fargate_service": "fargateService",
    },
)
class WatchEcsServiceProps(WatchEcsServiceOptions):
    def __init__(
        self,
        *,
        cpu_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        memory_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        requests_error_rate_threshold: typing.Optional[jsii.Number] = None,
        requests_threshold: typing.Optional[jsii.Number] = None,
        target_response_time_threshold: typing.Optional[jsii.Number] = None,
        target_group: aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup,
        title: builtins.str,
        watchful: IWatchful,
        ec2_service: typing.Optional[aws_cdk.aws_ecs.Ec2Service] = None,
        fargate_service: typing.Optional[aws_cdk.aws_ecs.FargateService] = None,
    ) -> None:
        '''
        :param cpu_maximum_threshold_percent: Threshold for the Cpu Maximum utilization. Default: 80
        :param memory_maximum_threshold_percent: Threshold for the Memory Maximum utilization. Default: - 0.
        :param requests_error_rate_threshold: Threshold for the Number of Request Errors. Default: - 0.
        :param requests_threshold: Threshold for the Number of Requests. Default: - 0.
        :param target_response_time_threshold: Threshold for the Target Response Time. Default: - 0.
        :param target_group: 
        :param title: 
        :param watchful: 
        :param ec2_service: 
        :param fargate_service: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchEcsServiceProps.__init__)
            check_type(argname="argument cpu_maximum_threshold_percent", value=cpu_maximum_threshold_percent, expected_type=type_hints["cpu_maximum_threshold_percent"])
            check_type(argname="argument memory_maximum_threshold_percent", value=memory_maximum_threshold_percent, expected_type=type_hints["memory_maximum_threshold_percent"])
            check_type(argname="argument requests_error_rate_threshold", value=requests_error_rate_threshold, expected_type=type_hints["requests_error_rate_threshold"])
            check_type(argname="argument requests_threshold", value=requests_threshold, expected_type=type_hints["requests_threshold"])
            check_type(argname="argument target_response_time_threshold", value=target_response_time_threshold, expected_type=type_hints["target_response_time_threshold"])
            check_type(argname="argument target_group", value=target_group, expected_type=type_hints["target_group"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument watchful", value=watchful, expected_type=type_hints["watchful"])
            check_type(argname="argument ec2_service", value=ec2_service, expected_type=type_hints["ec2_service"])
            check_type(argname="argument fargate_service", value=fargate_service, expected_type=type_hints["fargate_service"])
        self._values: typing.Dict[str, typing.Any] = {
            "target_group": target_group,
            "title": title,
            "watchful": watchful,
        }
        if cpu_maximum_threshold_percent is not None:
            self._values["cpu_maximum_threshold_percent"] = cpu_maximum_threshold_percent
        if memory_maximum_threshold_percent is not None:
            self._values["memory_maximum_threshold_percent"] = memory_maximum_threshold_percent
        if requests_error_rate_threshold is not None:
            self._values["requests_error_rate_threshold"] = requests_error_rate_threshold
        if requests_threshold is not None:
            self._values["requests_threshold"] = requests_threshold
        if target_response_time_threshold is not None:
            self._values["target_response_time_threshold"] = target_response_time_threshold
        if ec2_service is not None:
            self._values["ec2_service"] = ec2_service
        if fargate_service is not None:
            self._values["fargate_service"] = fargate_service

    @builtins.property
    def cpu_maximum_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Cpu Maximum utilization.

        :default: 80
        '''
        result = self._values.get("cpu_maximum_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_maximum_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Memory Maximum utilization.

        :default:

        -
        0.
        '''
        result = self._values.get("memory_maximum_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def requests_error_rate_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Number of Request Errors.

        :default:

        -
        0.
        '''
        result = self._values.get("requests_error_rate_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def requests_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Number of Requests.

        :default:

        -
        0.
        '''
        result = self._values.get("requests_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_response_time_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Target Response Time.

        :default:

        -
        0.
        '''
        result = self._values.get("target_response_time_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_group(self) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup:
        result = self._values.get("target_group")
        assert result is not None, "Required property 'target_group' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup, result)

    @builtins.property
    def title(self) -> builtins.str:
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def watchful(self) -> IWatchful:
        result = self._values.get("watchful")
        assert result is not None, "Required property 'watchful' is missing"
        return typing.cast(IWatchful, result)

    @builtins.property
    def ec2_service(self) -> typing.Optional[aws_cdk.aws_ecs.Ec2Service]:
        result = self._values.get("ec2_service")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.Ec2Service], result)

    @builtins.property
    def fargate_service(self) -> typing.Optional[aws_cdk.aws_ecs.FargateService]:
        result = self._values.get("fargate_service")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.FargateService], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchEcsServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WatchLambdaFunction(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-watchful.WatchLambdaFunction",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        fn: aws_cdk.aws_lambda.Function,
        title: builtins.str,
        watchful: IWatchful,
        duration_threshold_percent: typing.Optional[jsii.Number] = None,
        errors_per_minute_threshold: typing.Optional[jsii.Number] = None,
        throttles_per_minute_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param fn: 
        :param title: 
        :param watchful: 
        :param duration_threshold_percent: Threshold for the duration alarm as percentage of the function's timeout value. If this is set to 50%, the alarm will be set when p99 latency of the function exceeds 50% of the function's timeout setting. Default: 80
        :param errors_per_minute_threshold: Number of allowed errors per minute. If there are more errors than that, an alarm will trigger. Default: 0
        :param throttles_per_minute_threshold: Number of allowed throttles per minute. Default: 0
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchLambdaFunction.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WatchLambdaFunctionProps(
            fn=fn,
            title=title,
            watchful=watchful,
            duration_threshold_percent=duration_threshold_percent,
            errors_per_minute_threshold=errors_per_minute_threshold,
            throttles_per_minute_threshold=throttles_per_minute_threshold,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-watchful.WatchLambdaFunctionOptions",
    jsii_struct_bases=[],
    name_mapping={
        "duration_threshold_percent": "durationThresholdPercent",
        "errors_per_minute_threshold": "errorsPerMinuteThreshold",
        "throttles_per_minute_threshold": "throttlesPerMinuteThreshold",
    },
)
class WatchLambdaFunctionOptions:
    def __init__(
        self,
        *,
        duration_threshold_percent: typing.Optional[jsii.Number] = None,
        errors_per_minute_threshold: typing.Optional[jsii.Number] = None,
        throttles_per_minute_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param duration_threshold_percent: Threshold for the duration alarm as percentage of the function's timeout value. If this is set to 50%, the alarm will be set when p99 latency of the function exceeds 50% of the function's timeout setting. Default: 80
        :param errors_per_minute_threshold: Number of allowed errors per minute. If there are more errors than that, an alarm will trigger. Default: 0
        :param throttles_per_minute_threshold: Number of allowed throttles per minute. Default: 0
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchLambdaFunctionOptions.__init__)
            check_type(argname="argument duration_threshold_percent", value=duration_threshold_percent, expected_type=type_hints["duration_threshold_percent"])
            check_type(argname="argument errors_per_minute_threshold", value=errors_per_minute_threshold, expected_type=type_hints["errors_per_minute_threshold"])
            check_type(argname="argument throttles_per_minute_threshold", value=throttles_per_minute_threshold, expected_type=type_hints["throttles_per_minute_threshold"])
        self._values: typing.Dict[str, typing.Any] = {}
        if duration_threshold_percent is not None:
            self._values["duration_threshold_percent"] = duration_threshold_percent
        if errors_per_minute_threshold is not None:
            self._values["errors_per_minute_threshold"] = errors_per_minute_threshold
        if throttles_per_minute_threshold is not None:
            self._values["throttles_per_minute_threshold"] = throttles_per_minute_threshold

    @builtins.property
    def duration_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the duration alarm as percentage of the function's timeout value.

        If this is set to 50%, the alarm will be set when p99 latency of the
        function exceeds 50% of the function's timeout setting.

        :default: 80
        '''
        result = self._values.get("duration_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def errors_per_minute_threshold(self) -> typing.Optional[jsii.Number]:
        '''Number of allowed errors per minute.

        If there are more errors than that, an alarm will trigger.

        :default: 0
        '''
        result = self._values.get("errors_per_minute_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def throttles_per_minute_threshold(self) -> typing.Optional[jsii.Number]:
        '''Number of allowed throttles per minute.

        :default: 0
        '''
        result = self._values.get("throttles_per_minute_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchLambdaFunctionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-watchful.WatchLambdaFunctionProps",
    jsii_struct_bases=[WatchLambdaFunctionOptions],
    name_mapping={
        "duration_threshold_percent": "durationThresholdPercent",
        "errors_per_minute_threshold": "errorsPerMinuteThreshold",
        "throttles_per_minute_threshold": "throttlesPerMinuteThreshold",
        "fn": "fn",
        "title": "title",
        "watchful": "watchful",
    },
)
class WatchLambdaFunctionProps(WatchLambdaFunctionOptions):
    def __init__(
        self,
        *,
        duration_threshold_percent: typing.Optional[jsii.Number] = None,
        errors_per_minute_threshold: typing.Optional[jsii.Number] = None,
        throttles_per_minute_threshold: typing.Optional[jsii.Number] = None,
        fn: aws_cdk.aws_lambda.Function,
        title: builtins.str,
        watchful: IWatchful,
    ) -> None:
        '''
        :param duration_threshold_percent: Threshold for the duration alarm as percentage of the function's timeout value. If this is set to 50%, the alarm will be set when p99 latency of the function exceeds 50% of the function's timeout setting. Default: 80
        :param errors_per_minute_threshold: Number of allowed errors per minute. If there are more errors than that, an alarm will trigger. Default: 0
        :param throttles_per_minute_threshold: Number of allowed throttles per minute. Default: 0
        :param fn: 
        :param title: 
        :param watchful: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchLambdaFunctionProps.__init__)
            check_type(argname="argument duration_threshold_percent", value=duration_threshold_percent, expected_type=type_hints["duration_threshold_percent"])
            check_type(argname="argument errors_per_minute_threshold", value=errors_per_minute_threshold, expected_type=type_hints["errors_per_minute_threshold"])
            check_type(argname="argument throttles_per_minute_threshold", value=throttles_per_minute_threshold, expected_type=type_hints["throttles_per_minute_threshold"])
            check_type(argname="argument fn", value=fn, expected_type=type_hints["fn"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument watchful", value=watchful, expected_type=type_hints["watchful"])
        self._values: typing.Dict[str, typing.Any] = {
            "fn": fn,
            "title": title,
            "watchful": watchful,
        }
        if duration_threshold_percent is not None:
            self._values["duration_threshold_percent"] = duration_threshold_percent
        if errors_per_minute_threshold is not None:
            self._values["errors_per_minute_threshold"] = errors_per_minute_threshold
        if throttles_per_minute_threshold is not None:
            self._values["throttles_per_minute_threshold"] = throttles_per_minute_threshold

    @builtins.property
    def duration_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the duration alarm as percentage of the function's timeout value.

        If this is set to 50%, the alarm will be set when p99 latency of the
        function exceeds 50% of the function's timeout setting.

        :default: 80
        '''
        result = self._values.get("duration_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def errors_per_minute_threshold(self) -> typing.Optional[jsii.Number]:
        '''Number of allowed errors per minute.

        If there are more errors than that, an alarm will trigger.

        :default: 0
        '''
        result = self._values.get("errors_per_minute_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def throttles_per_minute_threshold(self) -> typing.Optional[jsii.Number]:
        '''Number of allowed throttles per minute.

        :default: 0
        '''
        result = self._values.get("throttles_per_minute_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fn(self) -> aws_cdk.aws_lambda.Function:
        result = self._values.get("fn")
        assert result is not None, "Required property 'fn' is missing"
        return typing.cast(aws_cdk.aws_lambda.Function, result)

    @builtins.property
    def title(self) -> builtins.str:
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def watchful(self) -> IWatchful:
        result = self._values.get("watchful")
        assert result is not None, "Required property 'watchful' is missing"
        return typing.cast(IWatchful, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchLambdaFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WatchRdsAurora(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-watchful.WatchRdsAurora",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_rds.DatabaseCluster,
        title: builtins.str,
        watchful: IWatchful,
        cpu_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        db_buffer_cache_minimum_threshold: typing.Optional[jsii.Number] = None,
        db_connections_maximum_threshold: typing.Optional[jsii.Number] = None,
        db_replica_lag_maximum_threshold: typing.Optional[jsii.Number] = None,
        db_throughput_maximum_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        :param title: 
        :param watchful: 
        :param cpu_maximum_threshold_percent: Threshold for the Cpu Maximum utilization. Default: 80
        :param db_buffer_cache_minimum_threshold: Threshold for the Minimum Db Buffer Cache. Default: - 0.
        :param db_connections_maximum_threshold: Threshold for the Maximum Db Connections. Default: - 0.
        :param db_replica_lag_maximum_threshold: Threshold for the Maximum Db ReplicaLag. Default: - 0.
        :param db_throughput_maximum_threshold: Threshold for the Maximum Db Throughput. Default: - 0.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchRdsAurora.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WatchRdsAuroraProps(
            cluster=cluster,
            title=title,
            watchful=watchful,
            cpu_maximum_threshold_percent=cpu_maximum_threshold_percent,
            db_buffer_cache_minimum_threshold=db_buffer_cache_minimum_threshold,
            db_connections_maximum_threshold=db_connections_maximum_threshold,
            db_replica_lag_maximum_threshold=db_replica_lag_maximum_threshold,
            db_throughput_maximum_threshold=db_throughput_maximum_threshold,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-watchful.WatchRdsAuroraOptions",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_maximum_threshold_percent": "cpuMaximumThresholdPercent",
        "db_buffer_cache_minimum_threshold": "dbBufferCacheMinimumThreshold",
        "db_connections_maximum_threshold": "dbConnectionsMaximumThreshold",
        "db_replica_lag_maximum_threshold": "dbReplicaLagMaximumThreshold",
        "db_throughput_maximum_threshold": "dbThroughputMaximumThreshold",
    },
)
class WatchRdsAuroraOptions:
    def __init__(
        self,
        *,
        cpu_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        db_buffer_cache_minimum_threshold: typing.Optional[jsii.Number] = None,
        db_connections_maximum_threshold: typing.Optional[jsii.Number] = None,
        db_replica_lag_maximum_threshold: typing.Optional[jsii.Number] = None,
        db_throughput_maximum_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_maximum_threshold_percent: Threshold for the Cpu Maximum utilization. Default: 80
        :param db_buffer_cache_minimum_threshold: Threshold for the Minimum Db Buffer Cache. Default: - 0.
        :param db_connections_maximum_threshold: Threshold for the Maximum Db Connections. Default: - 0.
        :param db_replica_lag_maximum_threshold: Threshold for the Maximum Db ReplicaLag. Default: - 0.
        :param db_throughput_maximum_threshold: Threshold for the Maximum Db Throughput. Default: - 0.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchRdsAuroraOptions.__init__)
            check_type(argname="argument cpu_maximum_threshold_percent", value=cpu_maximum_threshold_percent, expected_type=type_hints["cpu_maximum_threshold_percent"])
            check_type(argname="argument db_buffer_cache_minimum_threshold", value=db_buffer_cache_minimum_threshold, expected_type=type_hints["db_buffer_cache_minimum_threshold"])
            check_type(argname="argument db_connections_maximum_threshold", value=db_connections_maximum_threshold, expected_type=type_hints["db_connections_maximum_threshold"])
            check_type(argname="argument db_replica_lag_maximum_threshold", value=db_replica_lag_maximum_threshold, expected_type=type_hints["db_replica_lag_maximum_threshold"])
            check_type(argname="argument db_throughput_maximum_threshold", value=db_throughput_maximum_threshold, expected_type=type_hints["db_throughput_maximum_threshold"])
        self._values: typing.Dict[str, typing.Any] = {}
        if cpu_maximum_threshold_percent is not None:
            self._values["cpu_maximum_threshold_percent"] = cpu_maximum_threshold_percent
        if db_buffer_cache_minimum_threshold is not None:
            self._values["db_buffer_cache_minimum_threshold"] = db_buffer_cache_minimum_threshold
        if db_connections_maximum_threshold is not None:
            self._values["db_connections_maximum_threshold"] = db_connections_maximum_threshold
        if db_replica_lag_maximum_threshold is not None:
            self._values["db_replica_lag_maximum_threshold"] = db_replica_lag_maximum_threshold
        if db_throughput_maximum_threshold is not None:
            self._values["db_throughput_maximum_threshold"] = db_throughput_maximum_threshold

    @builtins.property
    def cpu_maximum_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Cpu Maximum utilization.

        :default: 80
        '''
        result = self._values.get("cpu_maximum_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def db_buffer_cache_minimum_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Minimum Db Buffer Cache.

        :default:

        -
        0.
        '''
        result = self._values.get("db_buffer_cache_minimum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def db_connections_maximum_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Maximum Db Connections.

        :default:

        -
        0.
        '''
        result = self._values.get("db_connections_maximum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def db_replica_lag_maximum_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Maximum Db ReplicaLag.

        :default:

        -
        0.
        '''
        result = self._values.get("db_replica_lag_maximum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def db_throughput_maximum_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Maximum Db Throughput.

        :default:

        -
        0.
        '''
        result = self._values.get("db_throughput_maximum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchRdsAuroraOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-watchful.WatchRdsAuroraProps",
    jsii_struct_bases=[WatchRdsAuroraOptions],
    name_mapping={
        "cpu_maximum_threshold_percent": "cpuMaximumThresholdPercent",
        "db_buffer_cache_minimum_threshold": "dbBufferCacheMinimumThreshold",
        "db_connections_maximum_threshold": "dbConnectionsMaximumThreshold",
        "db_replica_lag_maximum_threshold": "dbReplicaLagMaximumThreshold",
        "db_throughput_maximum_threshold": "dbThroughputMaximumThreshold",
        "cluster": "cluster",
        "title": "title",
        "watchful": "watchful",
    },
)
class WatchRdsAuroraProps(WatchRdsAuroraOptions):
    def __init__(
        self,
        *,
        cpu_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        db_buffer_cache_minimum_threshold: typing.Optional[jsii.Number] = None,
        db_connections_maximum_threshold: typing.Optional[jsii.Number] = None,
        db_replica_lag_maximum_threshold: typing.Optional[jsii.Number] = None,
        db_throughput_maximum_threshold: typing.Optional[jsii.Number] = None,
        cluster: aws_cdk.aws_rds.DatabaseCluster,
        title: builtins.str,
        watchful: IWatchful,
    ) -> None:
        '''
        :param cpu_maximum_threshold_percent: Threshold for the Cpu Maximum utilization. Default: 80
        :param db_buffer_cache_minimum_threshold: Threshold for the Minimum Db Buffer Cache. Default: - 0.
        :param db_connections_maximum_threshold: Threshold for the Maximum Db Connections. Default: - 0.
        :param db_replica_lag_maximum_threshold: Threshold for the Maximum Db ReplicaLag. Default: - 0.
        :param db_throughput_maximum_threshold: Threshold for the Maximum Db Throughput. Default: - 0.
        :param cluster: 
        :param title: 
        :param watchful: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchRdsAuroraProps.__init__)
            check_type(argname="argument cpu_maximum_threshold_percent", value=cpu_maximum_threshold_percent, expected_type=type_hints["cpu_maximum_threshold_percent"])
            check_type(argname="argument db_buffer_cache_minimum_threshold", value=db_buffer_cache_minimum_threshold, expected_type=type_hints["db_buffer_cache_minimum_threshold"])
            check_type(argname="argument db_connections_maximum_threshold", value=db_connections_maximum_threshold, expected_type=type_hints["db_connections_maximum_threshold"])
            check_type(argname="argument db_replica_lag_maximum_threshold", value=db_replica_lag_maximum_threshold, expected_type=type_hints["db_replica_lag_maximum_threshold"])
            check_type(argname="argument db_throughput_maximum_threshold", value=db_throughput_maximum_threshold, expected_type=type_hints["db_throughput_maximum_threshold"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument watchful", value=watchful, expected_type=type_hints["watchful"])
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "title": title,
            "watchful": watchful,
        }
        if cpu_maximum_threshold_percent is not None:
            self._values["cpu_maximum_threshold_percent"] = cpu_maximum_threshold_percent
        if db_buffer_cache_minimum_threshold is not None:
            self._values["db_buffer_cache_minimum_threshold"] = db_buffer_cache_minimum_threshold
        if db_connections_maximum_threshold is not None:
            self._values["db_connections_maximum_threshold"] = db_connections_maximum_threshold
        if db_replica_lag_maximum_threshold is not None:
            self._values["db_replica_lag_maximum_threshold"] = db_replica_lag_maximum_threshold
        if db_throughput_maximum_threshold is not None:
            self._values["db_throughput_maximum_threshold"] = db_throughput_maximum_threshold

    @builtins.property
    def cpu_maximum_threshold_percent(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Cpu Maximum utilization.

        :default: 80
        '''
        result = self._values.get("cpu_maximum_threshold_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def db_buffer_cache_minimum_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Minimum Db Buffer Cache.

        :default:

        -
        0.
        '''
        result = self._values.get("db_buffer_cache_minimum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def db_connections_maximum_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Maximum Db Connections.

        :default:

        -
        0.
        '''
        result = self._values.get("db_connections_maximum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def db_replica_lag_maximum_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Maximum Db ReplicaLag.

        :default:

        -
        0.
        '''
        result = self._values.get("db_replica_lag_maximum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def db_throughput_maximum_threshold(self) -> typing.Optional[jsii.Number]:
        '''Threshold for the Maximum Db Throughput.

        :default:

        -
        0.
        '''
        result = self._values.get("db_throughput_maximum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cluster(self) -> aws_cdk.aws_rds.DatabaseCluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_rds.DatabaseCluster, result)

    @builtins.property
    def title(self) -> builtins.str:
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def watchful(self) -> IWatchful:
        result = self._values.get("watchful")
        assert result is not None, "Required property 'watchful' is missing"
        return typing.cast(IWatchful, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchRdsAuroraProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WatchStateMachine(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-watchful.WatchStateMachine",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        state_machine: aws_cdk.aws_stepfunctions.StateMachine,
        title: builtins.str,
        watchful: IWatchful,
        metric_failed_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param state_machine: 
        :param title: 
        :param watchful: 
        :param metric_failed_threshold: Alarm when execution failures reach this threshold over 1 minute. Default: 1 any execution failure will trigger the alarm
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchStateMachine.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WatchStateMachineProps(
            state_machine=state_machine,
            title=title,
            watchful=watchful,
            metric_failed_threshold=metric_failed_threshold,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-watchful.WatchStateMachineOptions",
    jsii_struct_bases=[],
    name_mapping={"metric_failed_threshold": "metricFailedThreshold"},
)
class WatchStateMachineOptions:
    def __init__(
        self,
        *,
        metric_failed_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param metric_failed_threshold: Alarm when execution failures reach this threshold over 1 minute. Default: 1 any execution failure will trigger the alarm
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchStateMachineOptions.__init__)
            check_type(argname="argument metric_failed_threshold", value=metric_failed_threshold, expected_type=type_hints["metric_failed_threshold"])
        self._values: typing.Dict[str, typing.Any] = {}
        if metric_failed_threshold is not None:
            self._values["metric_failed_threshold"] = metric_failed_threshold

    @builtins.property
    def metric_failed_threshold(self) -> typing.Optional[jsii.Number]:
        '''Alarm when execution failures reach this threshold over 1 minute.

        :default: 1 any execution failure will trigger the alarm
        '''
        result = self._values.get("metric_failed_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchStateMachineOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-watchful.WatchStateMachineProps",
    jsii_struct_bases=[WatchStateMachineOptions],
    name_mapping={
        "metric_failed_threshold": "metricFailedThreshold",
        "state_machine": "stateMachine",
        "title": "title",
        "watchful": "watchful",
    },
)
class WatchStateMachineProps(WatchStateMachineOptions):
    def __init__(
        self,
        *,
        metric_failed_threshold: typing.Optional[jsii.Number] = None,
        state_machine: aws_cdk.aws_stepfunctions.StateMachine,
        title: builtins.str,
        watchful: IWatchful,
    ) -> None:
        '''
        :param metric_failed_threshold: Alarm when execution failures reach this threshold over 1 minute. Default: 1 any execution failure will trigger the alarm
        :param state_machine: 
        :param title: 
        :param watchful: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchStateMachineProps.__init__)
            check_type(argname="argument metric_failed_threshold", value=metric_failed_threshold, expected_type=type_hints["metric_failed_threshold"])
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument watchful", value=watchful, expected_type=type_hints["watchful"])
        self._values: typing.Dict[str, typing.Any] = {
            "state_machine": state_machine,
            "title": title,
            "watchful": watchful,
        }
        if metric_failed_threshold is not None:
            self._values["metric_failed_threshold"] = metric_failed_threshold

    @builtins.property
    def metric_failed_threshold(self) -> typing.Optional[jsii.Number]:
        '''Alarm when execution failures reach this threshold over 1 minute.

        :default: 1 any execution failure will trigger the alarm
        '''
        result = self._values.get("metric_failed_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state_machine(self) -> aws_cdk.aws_stepfunctions.StateMachine:
        result = self._values.get("state_machine")
        assert result is not None, "Required property 'state_machine' is missing"
        return typing.cast(aws_cdk.aws_stepfunctions.StateMachine, result)

    @builtins.property
    def title(self) -> builtins.str:
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def watchful(self) -> IWatchful:
        result = self._values.get("watchful")
        assert result is not None, "Required property 'watchful' is missing"
        return typing.cast(IWatchful, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchStateMachineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-watchful.WatchedOperation",
    jsii_struct_bases=[],
    name_mapping={"http_method": "httpMethod", "resource_path": "resourcePath"},
)
class WatchedOperation:
    def __init__(
        self,
        *,
        http_method: builtins.str,
        resource_path: builtins.str,
    ) -> None:
        '''An operation (path and method) worth monitoring.

        :param http_method: The HTTP method for the operation (GET, POST, ...).
        :param resource_path: The REST API path for this operation (/, /resource/{id}, ...).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchedOperation.__init__)
            check_type(argname="argument http_method", value=http_method, expected_type=type_hints["http_method"])
            check_type(argname="argument resource_path", value=resource_path, expected_type=type_hints["resource_path"])
        self._values: typing.Dict[str, typing.Any] = {
            "http_method": http_method,
            "resource_path": resource_path,
        }

    @builtins.property
    def http_method(self) -> builtins.str:
        '''The HTTP method for the operation (GET, POST, ...).'''
        result = self._values.get("http_method")
        assert result is not None, "Required property 'http_method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_path(self) -> builtins.str:
        '''The REST API path for this operation (/, /resource/{id}, ...).'''
        result = self._values.get("resource_path")
        assert result is not None, "Required property 'resource_path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchedOperation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IWatchful)
class Watchful(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-watchful.Watchful",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alarm_action_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        alarm_actions: typing.Optional[typing.Sequence[aws_cdk.aws_cloudwatch.IAlarmAction]] = None,
        alarm_email: typing.Optional[builtins.str] = None,
        alarm_sns: typing.Optional[aws_cdk.aws_sns.ITopic] = None,
        alarm_sqs: typing.Optional[aws_cdk.aws_sqs.IQueue] = None,
        dashboard: typing.Optional[builtins.bool] = None,
        dashboard_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alarm_action_arns: ARNs of actions to perform when alarms go off. These actions are in addition to email/sqs/sns. Default: [] You can use ``alarmActions`` instead as a strongly-typed alternative.
        :param alarm_actions: CloudWatch alarm actions to perform when alarms go off. These actions are in addition to email/sqs/sns.
        :param alarm_email: Email address to send alarms to. Default: - alarms are not sent to an email recipient.
        :param alarm_sns: SNS topic to send alarms to. Default: - alarms are not sent to an SNS Topic.
        :param alarm_sqs: SQS queue to send alarms to. Default: - alarms are not sent to an SQS queue.
        :param dashboard: Whether to generate CloudWatch dashboards. Default: true
        :param dashboard_name: The name of the CloudWatch dashboard generated by Watchful. Default: - auto-generated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WatchfulProps(
            alarm_action_arns=alarm_action_arns,
            alarm_actions=alarm_actions,
            alarm_email=alarm_email,
            alarm_sns=alarm_sns,
            alarm_sqs=alarm_sqs,
            dashboard=dashboard,
            dashboard_name=dashboard_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addAlarm")
    def add_alarm(self, alarm: aws_cdk.aws_cloudwatch.IAlarm) -> None:
        '''
        :param alarm: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.add_alarm)
            check_type(argname="argument alarm", value=alarm, expected_type=type_hints["alarm"])
        return typing.cast(None, jsii.invoke(self, "addAlarm", [alarm]))

    @jsii.member(jsii_name="addSection")
    def add_section(
        self,
        title: builtins.str,
        *,
        links: typing.Optional[typing.Sequence[typing.Union[QuickLink, typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param title: -
        :param links: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.add_section)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
        options = SectionOptions(links=links)

        return typing.cast(None, jsii.invoke(self, "addSection", [title, options]))

    @jsii.member(jsii_name="addWidgets")
    def add_widgets(self, *widgets: aws_cdk.aws_cloudwatch.IWidget) -> None:
        '''
        :param widgets: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.add_widgets)
            check_type(argname="argument widgets", value=widgets, expected_type=typing.Tuple[type_hints["widgets"], ...])
        return typing.cast(None, jsii.invoke(self, "addWidgets", [*widgets]))

    @jsii.member(jsii_name="watchApiGateway")
    def watch_api_gateway(
        self,
        title: builtins.str,
        rest_api: aws_cdk.aws_apigateway.RestApi,
        *,
        cache_graph: typing.Optional[builtins.bool] = None,
        server_error_threshold: typing.Optional[jsii.Number] = None,
        watched_operations: typing.Optional[typing.Sequence[typing.Union[WatchedOperation, typing.Dict[str, typing.Any]]]] = None,
    ) -> WatchApiGateway:
        '''
        :param title: -
        :param rest_api: -
        :param cache_graph: Include a dashboard graph for caching metrics. Default: false
        :param server_error_threshold: Alarm when 5XX errors reach this threshold over 5 minutes. Default: 1 any 5xx HTTP response will trigger the alarm
        :param watched_operations: A list of operations to monitor separately. Default: - only API-level monitoring is added.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.watch_api_gateway)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument rest_api", value=rest_api, expected_type=type_hints["rest_api"])
        options = WatchApiGatewayOptions(
            cache_graph=cache_graph,
            server_error_threshold=server_error_threshold,
            watched_operations=watched_operations,
        )

        return typing.cast(WatchApiGateway, jsii.invoke(self, "watchApiGateway", [title, rest_api, options]))

    @jsii.member(jsii_name="watchDynamoTable")
    def watch_dynamo_table(
        self,
        title: builtins.str,
        table: aws_cdk.aws_dynamodb.Table,
        *,
        read_capacity_threshold_percent: typing.Optional[jsii.Number] = None,
        write_capacity_threshold_percent: typing.Optional[jsii.Number] = None,
    ) -> WatchDynamoTable:
        '''
        :param title: -
        :param table: -
        :param read_capacity_threshold_percent: Threshold for read capacity alarm (percentage). Default: 80
        :param write_capacity_threshold_percent: Threshold for read capacity alarm (percentage). Default: 80
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.watch_dynamo_table)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
        options = WatchDynamoTableOptions(
            read_capacity_threshold_percent=read_capacity_threshold_percent,
            write_capacity_threshold_percent=write_capacity_threshold_percent,
        )

        return typing.cast(WatchDynamoTable, jsii.invoke(self, "watchDynamoTable", [title, table, options]))

    @jsii.member(jsii_name="watchEc2Ecs")
    def watch_ec2_ecs(
        self,
        title: builtins.str,
        ec2_service: aws_cdk.aws_ecs.Ec2Service,
        target_group: aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup,
        *,
        cpu_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        memory_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        requests_error_rate_threshold: typing.Optional[jsii.Number] = None,
        requests_threshold: typing.Optional[jsii.Number] = None,
        target_response_time_threshold: typing.Optional[jsii.Number] = None,
    ) -> WatchEcsService:
        '''
        :param title: -
        :param ec2_service: -
        :param target_group: -
        :param cpu_maximum_threshold_percent: Threshold for the Cpu Maximum utilization. Default: 80
        :param memory_maximum_threshold_percent: Threshold for the Memory Maximum utilization. Default: - 0.
        :param requests_error_rate_threshold: Threshold for the Number of Request Errors. Default: - 0.
        :param requests_threshold: Threshold for the Number of Requests. Default: - 0.
        :param target_response_time_threshold: Threshold for the Target Response Time. Default: - 0.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.watch_ec2_ecs)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument ec2_service", value=ec2_service, expected_type=type_hints["ec2_service"])
            check_type(argname="argument target_group", value=target_group, expected_type=type_hints["target_group"])
        options = WatchEcsServiceOptions(
            cpu_maximum_threshold_percent=cpu_maximum_threshold_percent,
            memory_maximum_threshold_percent=memory_maximum_threshold_percent,
            requests_error_rate_threshold=requests_error_rate_threshold,
            requests_threshold=requests_threshold,
            target_response_time_threshold=target_response_time_threshold,
        )

        return typing.cast(WatchEcsService, jsii.invoke(self, "watchEc2Ecs", [title, ec2_service, target_group, options]))

    @jsii.member(jsii_name="watchFargateEcs")
    def watch_fargate_ecs(
        self,
        title: builtins.str,
        fargate_service: aws_cdk.aws_ecs.FargateService,
        target_group: aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup,
        *,
        cpu_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        memory_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        requests_error_rate_threshold: typing.Optional[jsii.Number] = None,
        requests_threshold: typing.Optional[jsii.Number] = None,
        target_response_time_threshold: typing.Optional[jsii.Number] = None,
    ) -> WatchEcsService:
        '''
        :param title: -
        :param fargate_service: -
        :param target_group: -
        :param cpu_maximum_threshold_percent: Threshold for the Cpu Maximum utilization. Default: 80
        :param memory_maximum_threshold_percent: Threshold for the Memory Maximum utilization. Default: - 0.
        :param requests_error_rate_threshold: Threshold for the Number of Request Errors. Default: - 0.
        :param requests_threshold: Threshold for the Number of Requests. Default: - 0.
        :param target_response_time_threshold: Threshold for the Target Response Time. Default: - 0.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.watch_fargate_ecs)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument fargate_service", value=fargate_service, expected_type=type_hints["fargate_service"])
            check_type(argname="argument target_group", value=target_group, expected_type=type_hints["target_group"])
        options = WatchEcsServiceOptions(
            cpu_maximum_threshold_percent=cpu_maximum_threshold_percent,
            memory_maximum_threshold_percent=memory_maximum_threshold_percent,
            requests_error_rate_threshold=requests_error_rate_threshold,
            requests_threshold=requests_threshold,
            target_response_time_threshold=target_response_time_threshold,
        )

        return typing.cast(WatchEcsService, jsii.invoke(self, "watchFargateEcs", [title, fargate_service, target_group, options]))

    @jsii.member(jsii_name="watchLambdaFunction")
    def watch_lambda_function(
        self,
        title: builtins.str,
        fn: aws_cdk.aws_lambda.Function,
        *,
        duration_threshold_percent: typing.Optional[jsii.Number] = None,
        errors_per_minute_threshold: typing.Optional[jsii.Number] = None,
        throttles_per_minute_threshold: typing.Optional[jsii.Number] = None,
    ) -> WatchLambdaFunction:
        '''
        :param title: -
        :param fn: -
        :param duration_threshold_percent: Threshold for the duration alarm as percentage of the function's timeout value. If this is set to 50%, the alarm will be set when p99 latency of the function exceeds 50% of the function's timeout setting. Default: 80
        :param errors_per_minute_threshold: Number of allowed errors per minute. If there are more errors than that, an alarm will trigger. Default: 0
        :param throttles_per_minute_threshold: Number of allowed throttles per minute. Default: 0
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.watch_lambda_function)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument fn", value=fn, expected_type=type_hints["fn"])
        options = WatchLambdaFunctionOptions(
            duration_threshold_percent=duration_threshold_percent,
            errors_per_minute_threshold=errors_per_minute_threshold,
            throttles_per_minute_threshold=throttles_per_minute_threshold,
        )

        return typing.cast(WatchLambdaFunction, jsii.invoke(self, "watchLambdaFunction", [title, fn, options]))

    @jsii.member(jsii_name="watchRdsAuroraCluster")
    def watch_rds_aurora_cluster(
        self,
        title: builtins.str,
        cluster: aws_cdk.aws_rds.DatabaseCluster,
        *,
        cpu_maximum_threshold_percent: typing.Optional[jsii.Number] = None,
        db_buffer_cache_minimum_threshold: typing.Optional[jsii.Number] = None,
        db_connections_maximum_threshold: typing.Optional[jsii.Number] = None,
        db_replica_lag_maximum_threshold: typing.Optional[jsii.Number] = None,
        db_throughput_maximum_threshold: typing.Optional[jsii.Number] = None,
    ) -> WatchRdsAurora:
        '''
        :param title: -
        :param cluster: -
        :param cpu_maximum_threshold_percent: Threshold for the Cpu Maximum utilization. Default: 80
        :param db_buffer_cache_minimum_threshold: Threshold for the Minimum Db Buffer Cache. Default: - 0.
        :param db_connections_maximum_threshold: Threshold for the Maximum Db Connections. Default: - 0.
        :param db_replica_lag_maximum_threshold: Threshold for the Maximum Db ReplicaLag. Default: - 0.
        :param db_throughput_maximum_threshold: Threshold for the Maximum Db Throughput. Default: - 0.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.watch_rds_aurora_cluster)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        options = WatchRdsAuroraOptions(
            cpu_maximum_threshold_percent=cpu_maximum_threshold_percent,
            db_buffer_cache_minimum_threshold=db_buffer_cache_minimum_threshold,
            db_connections_maximum_threshold=db_connections_maximum_threshold,
            db_replica_lag_maximum_threshold=db_replica_lag_maximum_threshold,
            db_throughput_maximum_threshold=db_throughput_maximum_threshold,
        )

        return typing.cast(WatchRdsAurora, jsii.invoke(self, "watchRdsAuroraCluster", [title, cluster, options]))

    @jsii.member(jsii_name="watchScope")
    def watch_scope(
        self,
        scope: constructs.Construct,
        *,
        api_gateway: typing.Optional[builtins.bool] = None,
        dynamodb: typing.Optional[builtins.bool] = None,
        ec2ecs: typing.Optional[builtins.bool] = None,
        fargateecs: typing.Optional[builtins.bool] = None,
        lambda_: typing.Optional[builtins.bool] = None,
        rdsaurora: typing.Optional[builtins.bool] = None,
        state_machine: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param api_gateway: Automatically watch API Gateway APIs in the scope. Default: true
        :param dynamodb: Automatically watch all Amazon DynamoDB tables in the scope. Default: true
        :param ec2ecs: Automatically watch ApplicationLoadBalanced EC2 Ecs Services in the scope (using ECS Pattern). Default: true
        :param fargateecs: Automatically watch ApplicationLoadBalanced Fargate Ecs Services in the scope (using ECS Pattern). Default: true
        :param lambda_: Automatically watch AWS Lambda functions in the scope. Default: true
        :param rdsaurora: Automatically watch RDS Aurora clusters in the scope. Default: true
        :param state_machine: Automatically watch AWS state machines in the scope. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.watch_scope)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        options = WatchfulAspectProps(
            api_gateway=api_gateway,
            dynamodb=dynamodb,
            ec2ecs=ec2ecs,
            fargateecs=fargateecs,
            lambda_=lambda_,
            rdsaurora=rdsaurora,
            state_machine=state_machine,
        )

        return typing.cast(None, jsii.invoke(self, "watchScope", [scope, options]))

    @jsii.member(jsii_name="watchStateMachine")
    def watch_state_machine(
        self,
        title: builtins.str,
        state_machine: aws_cdk.aws_stepfunctions.StateMachine,
        *,
        metric_failed_threshold: typing.Optional[jsii.Number] = None,
    ) -> WatchStateMachine:
        '''
        :param title: -
        :param state_machine: -
        :param metric_failed_threshold: Alarm when execution failures reach this threshold over 1 minute. Default: 1 any execution failure will trigger the alarm
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Watchful.watch_state_machine)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
        options = WatchStateMachineOptions(
            metric_failed_threshold=metric_failed_threshold
        )

        return typing.cast(WatchStateMachine, jsii.invoke(self, "watchStateMachine", [title, state_machine, options]))


@jsii.implements(aws_cdk.IAspect)
class WatchfulAspect(metaclass=jsii.JSIIMeta, jsii_type="cdk-watchful.WatchfulAspect"):
    '''A CDK aspect that can automatically watch all resources within a scope.'''

    def __init__(
        self,
        watchful: Watchful,
        *,
        api_gateway: typing.Optional[builtins.bool] = None,
        dynamodb: typing.Optional[builtins.bool] = None,
        ec2ecs: typing.Optional[builtins.bool] = None,
        fargateecs: typing.Optional[builtins.bool] = None,
        lambda_: typing.Optional[builtins.bool] = None,
        rdsaurora: typing.Optional[builtins.bool] = None,
        state_machine: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Defines a watchful aspect.

        :param watchful: The watchful to add those resources to.
        :param api_gateway: Automatically watch API Gateway APIs in the scope. Default: true
        :param dynamodb: Automatically watch all Amazon DynamoDB tables in the scope. Default: true
        :param ec2ecs: Automatically watch ApplicationLoadBalanced EC2 Ecs Services in the scope (using ECS Pattern). Default: true
        :param fargateecs: Automatically watch ApplicationLoadBalanced Fargate Ecs Services in the scope (using ECS Pattern). Default: true
        :param lambda_: Automatically watch AWS Lambda functions in the scope. Default: true
        :param rdsaurora: Automatically watch RDS Aurora clusters in the scope. Default: true
        :param state_machine: Automatically watch AWS state machines in the scope. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchfulAspect.__init__)
            check_type(argname="argument watchful", value=watchful, expected_type=type_hints["watchful"])
        props = WatchfulAspectProps(
            api_gateway=api_gateway,
            dynamodb=dynamodb,
            ec2ecs=ec2ecs,
            fargateecs=fargateecs,
            lambda_=lambda_,
            rdsaurora=rdsaurora,
            state_machine=state_machine,
        )

        jsii.create(self.__class__, self, [watchful, props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: constructs.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchfulAspect.visit)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))


@jsii.data_type(
    jsii_type="cdk-watchful.WatchfulAspectProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_gateway": "apiGateway",
        "dynamodb": "dynamodb",
        "ec2ecs": "ec2ecs",
        "fargateecs": "fargateecs",
        "lambda_": "lambda",
        "rdsaurora": "rdsaurora",
        "state_machine": "stateMachine",
    },
)
class WatchfulAspectProps:
    def __init__(
        self,
        *,
        api_gateway: typing.Optional[builtins.bool] = None,
        dynamodb: typing.Optional[builtins.bool] = None,
        ec2ecs: typing.Optional[builtins.bool] = None,
        fargateecs: typing.Optional[builtins.bool] = None,
        lambda_: typing.Optional[builtins.bool] = None,
        rdsaurora: typing.Optional[builtins.bool] = None,
        state_machine: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param api_gateway: Automatically watch API Gateway APIs in the scope. Default: true
        :param dynamodb: Automatically watch all Amazon DynamoDB tables in the scope. Default: true
        :param ec2ecs: Automatically watch ApplicationLoadBalanced EC2 Ecs Services in the scope (using ECS Pattern). Default: true
        :param fargateecs: Automatically watch ApplicationLoadBalanced Fargate Ecs Services in the scope (using ECS Pattern). Default: true
        :param lambda_: Automatically watch AWS Lambda functions in the scope. Default: true
        :param rdsaurora: Automatically watch RDS Aurora clusters in the scope. Default: true
        :param state_machine: Automatically watch AWS state machines in the scope. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchfulAspectProps.__init__)
            check_type(argname="argument api_gateway", value=api_gateway, expected_type=type_hints["api_gateway"])
            check_type(argname="argument dynamodb", value=dynamodb, expected_type=type_hints["dynamodb"])
            check_type(argname="argument ec2ecs", value=ec2ecs, expected_type=type_hints["ec2ecs"])
            check_type(argname="argument fargateecs", value=fargateecs, expected_type=type_hints["fargateecs"])
            check_type(argname="argument lambda_", value=lambda_, expected_type=type_hints["lambda_"])
            check_type(argname="argument rdsaurora", value=rdsaurora, expected_type=type_hints["rdsaurora"])
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
        self._values: typing.Dict[str, typing.Any] = {}
        if api_gateway is not None:
            self._values["api_gateway"] = api_gateway
        if dynamodb is not None:
            self._values["dynamodb"] = dynamodb
        if ec2ecs is not None:
            self._values["ec2ecs"] = ec2ecs
        if fargateecs is not None:
            self._values["fargateecs"] = fargateecs
        if lambda_ is not None:
            self._values["lambda_"] = lambda_
        if rdsaurora is not None:
            self._values["rdsaurora"] = rdsaurora
        if state_machine is not None:
            self._values["state_machine"] = state_machine

    @builtins.property
    def api_gateway(self) -> typing.Optional[builtins.bool]:
        '''Automatically watch API Gateway APIs in the scope.

        :default: true
        '''
        result = self._values.get("api_gateway")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dynamodb(self) -> typing.Optional[builtins.bool]:
        '''Automatically watch all Amazon DynamoDB tables in the scope.

        :default: true
        '''
        result = self._values.get("dynamodb")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ec2ecs(self) -> typing.Optional[builtins.bool]:
        '''Automatically watch ApplicationLoadBalanced EC2 Ecs Services in the scope (using ECS Pattern).

        :default: true
        '''
        result = self._values.get("ec2ecs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def fargateecs(self) -> typing.Optional[builtins.bool]:
        '''Automatically watch ApplicationLoadBalanced Fargate Ecs Services in the scope (using ECS Pattern).

        :default: true
        '''
        result = self._values.get("fargateecs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lambda_(self) -> typing.Optional[builtins.bool]:
        '''Automatically watch AWS Lambda functions in the scope.

        :default: true
        '''
        result = self._values.get("lambda_")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def rdsaurora(self) -> typing.Optional[builtins.bool]:
        '''Automatically watch RDS Aurora clusters in the scope.

        :default: true
        '''
        result = self._values.get("rdsaurora")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def state_machine(self) -> typing.Optional[builtins.bool]:
        '''Automatically watch AWS state machines in the scope.

        :default: true
        '''
        result = self._values.get("state_machine")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchfulAspectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-watchful.WatchfulProps",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_action_arns": "alarmActionArns",
        "alarm_actions": "alarmActions",
        "alarm_email": "alarmEmail",
        "alarm_sns": "alarmSns",
        "alarm_sqs": "alarmSqs",
        "dashboard": "dashboard",
        "dashboard_name": "dashboardName",
    },
)
class WatchfulProps:
    def __init__(
        self,
        *,
        alarm_action_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        alarm_actions: typing.Optional[typing.Sequence[aws_cdk.aws_cloudwatch.IAlarmAction]] = None,
        alarm_email: typing.Optional[builtins.str] = None,
        alarm_sns: typing.Optional[aws_cdk.aws_sns.ITopic] = None,
        alarm_sqs: typing.Optional[aws_cdk.aws_sqs.IQueue] = None,
        dashboard: typing.Optional[builtins.bool] = None,
        dashboard_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alarm_action_arns: ARNs of actions to perform when alarms go off. These actions are in addition to email/sqs/sns. Default: [] You can use ``alarmActions`` instead as a strongly-typed alternative.
        :param alarm_actions: CloudWatch alarm actions to perform when alarms go off. These actions are in addition to email/sqs/sns.
        :param alarm_email: Email address to send alarms to. Default: - alarms are not sent to an email recipient.
        :param alarm_sns: SNS topic to send alarms to. Default: - alarms are not sent to an SNS Topic.
        :param alarm_sqs: SQS queue to send alarms to. Default: - alarms are not sent to an SQS queue.
        :param dashboard: Whether to generate CloudWatch dashboards. Default: true
        :param dashboard_name: The name of the CloudWatch dashboard generated by Watchful. Default: - auto-generated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(WatchfulProps.__init__)
            check_type(argname="argument alarm_action_arns", value=alarm_action_arns, expected_type=type_hints["alarm_action_arns"])
            check_type(argname="argument alarm_actions", value=alarm_actions, expected_type=type_hints["alarm_actions"])
            check_type(argname="argument alarm_email", value=alarm_email, expected_type=type_hints["alarm_email"])
            check_type(argname="argument alarm_sns", value=alarm_sns, expected_type=type_hints["alarm_sns"])
            check_type(argname="argument alarm_sqs", value=alarm_sqs, expected_type=type_hints["alarm_sqs"])
            check_type(argname="argument dashboard", value=dashboard, expected_type=type_hints["dashboard"])
            check_type(argname="argument dashboard_name", value=dashboard_name, expected_type=type_hints["dashboard_name"])
        self._values: typing.Dict[str, typing.Any] = {}
        if alarm_action_arns is not None:
            self._values["alarm_action_arns"] = alarm_action_arns
        if alarm_actions is not None:
            self._values["alarm_actions"] = alarm_actions
        if alarm_email is not None:
            self._values["alarm_email"] = alarm_email
        if alarm_sns is not None:
            self._values["alarm_sns"] = alarm_sns
        if alarm_sqs is not None:
            self._values["alarm_sqs"] = alarm_sqs
        if dashboard is not None:
            self._values["dashboard"] = dashboard
        if dashboard_name is not None:
            self._values["dashboard_name"] = dashboard_name

    @builtins.property
    def alarm_action_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''ARNs of actions to perform when alarms go off.

        These actions are in
        addition to email/sqs/sns.

        :default:

        []

        You can use ``alarmActions`` instead as a strongly-typed alternative.
        '''
        result = self._values.get("alarm_action_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def alarm_actions(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudwatch.IAlarmAction]]:
        '''CloudWatch alarm actions to perform when alarms go off.

        These actions are
        in addition to email/sqs/sns.
        '''
        result = self._values.get("alarm_actions")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudwatch.IAlarmAction]], result)

    @builtins.property
    def alarm_email(self) -> typing.Optional[builtins.str]:
        '''Email address to send alarms to.

        :default: - alarms are not sent to an email recipient.
        '''
        result = self._values.get("alarm_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alarm_sns(self) -> typing.Optional[aws_cdk.aws_sns.ITopic]:
        '''SNS topic to send alarms to.

        :default: - alarms are not sent to an SNS Topic.
        '''
        result = self._values.get("alarm_sns")
        return typing.cast(typing.Optional[aws_cdk.aws_sns.ITopic], result)

    @builtins.property
    def alarm_sqs(self) -> typing.Optional[aws_cdk.aws_sqs.IQueue]:
        '''SQS queue to send alarms to.

        :default: - alarms are not sent to an SQS queue.
        '''
        result = self._values.get("alarm_sqs")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.IQueue], result)

    @builtins.property
    def dashboard(self) -> typing.Optional[builtins.bool]:
        '''Whether to generate CloudWatch dashboards.

        :default: true
        '''
        result = self._values.get("dashboard")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dashboard_name(self) -> typing.Optional[builtins.str]:
        '''The name of the CloudWatch dashboard generated by Watchful.

        :default: - auto-generated
        '''
        result = self._values.get("dashboard_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchfulProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IWatchful",
    "QuickLink",
    "SectionOptions",
    "WatchApiGateway",
    "WatchApiGatewayOptions",
    "WatchApiGatewayProps",
    "WatchDynamoTable",
    "WatchDynamoTableOptions",
    "WatchDynamoTableProps",
    "WatchEcsService",
    "WatchEcsServiceOptions",
    "WatchEcsServiceProps",
    "WatchLambdaFunction",
    "WatchLambdaFunctionOptions",
    "WatchLambdaFunctionProps",
    "WatchRdsAurora",
    "WatchRdsAuroraOptions",
    "WatchRdsAuroraProps",
    "WatchStateMachine",
    "WatchStateMachineOptions",
    "WatchStateMachineProps",
    "WatchedOperation",
    "Watchful",
    "WatchfulAspect",
    "WatchfulAspectProps",
    "WatchfulProps",
]

publication.publish()
