'''
# AWS Lambda Layer with the NPM dependency proxy-agent

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

This module exports a single class called `NodeProxyAgentLayer` which is a `lambda.Layer` that bundles the NPM dependency [`proxy-agent`](https://www.npmjs.com/package/proxy-agent).

> * proxy-agent Version: 5.0.0

Usage:

```python
from aws_cdk.lambda_layer_node_proxy_agent import NodeProxyAgentLayer
import aws_cdk.aws_lambda as lambda_

# fn: lambda.Function

fn.add_layers(NodeProxyAgentLayer(self, "NodeProxyAgentLayer"))
```

[`proxy-agent`](https://www.npmjs.com/package/proxy-agent) will be installed under `/nodejs/node_modules`.
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

import aws_cdk.aws_lambda
import constructs


class NodeProxyAgentLayer(
    aws_cdk.aws_lambda.LayerVersion,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/lambda-layer-node-proxy-agent.NodeProxyAgentLayer",
):
    '''An AWS Lambda layer that includes the NPM dependency ``proxy-agent``.

    :exampleMetadata: infused

    Example::

        from aws_cdk.lambda_layer_node_proxy_agent import NodeProxyAgentLayer
        import aws_cdk.aws_lambda as lambda_
        
        # fn: lambda.Function
        
        fn.add_layers(NodeProxyAgentLayer(self, "NodeProxyAgentLayer"))
    '''

    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(NodeProxyAgentLayer.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])


__all__ = [
    "NodeProxyAgentLayer",
]

publication.publish()
