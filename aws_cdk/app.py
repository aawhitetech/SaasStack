#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infra.saas_stack import SaasStack


app = cdk.App()
SaasStack(app, "SaasStack", env=cdk.Environment(account="123456789012", region="us-east-1"))
app.synth()
