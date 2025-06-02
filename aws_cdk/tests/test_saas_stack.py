import aws_cdk as cdk
from infra.saas_stack import SaasStack

def test_stack_synthesizes():
    app = cdk.App()
    stack = SaasStack(app, "TestStack")
    template = app.synth().get_stack_by_name("TestStack").template
    assert "Resources" in template
