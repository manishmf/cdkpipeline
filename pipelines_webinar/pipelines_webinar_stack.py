from os import path

from aws_cdk import core,aws_iam,aws_lambda
import aws_cdk.aws_lambda as lmb
import aws_cdk.aws_apigateway as apigw
import aws_cdk.aws_codedeploy as codedeploy
import aws_cdk.aws_cloudwatch as cloudwatch

class PipelinesWebinarStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        this_dir = path.dirname(__file__)

        #handler = lmb.Function(self, 'Handler',
        #    runtime=lmb.Runtime.PYTHON_3_8,
        #    handler='handler.handler',
        #    code=lmb.Code.from_asset(path.join(this_dir, 'lambda')))
        lambda_role = aws_iam.Role(scope=self, id='cdk-lambda-role',
                                assumed_by =aws_iam.ServicePrincipal('lambda.amazonaws.com'),
                                role_name='cdk-lambda-role',
                                managed_policies=[
                                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                                    'service-role/AWSLambdaVPCAccessExecutionRole'),
                                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                                    'service-role/AWSLambdaBasicExecutionRole')
                                ])
        cdk_lambda =aws_lambda.Function(
            self, 'cdk-r4p-lambda',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            function_name='cdk-r4p-lambda',
            description='Lambda function deployed using AWS CDK Python',
            code=aws_lambda.Code.asset('./lambda'),
            handler='slack_alerts.lambda_handler',
            role=lambda_role,
        )

        alias = aws_lambda.Alias(self, 'HandlerAlias',
            alias_name='Current',
            version=cdk_lambda.current_version)

        gw = apigw.LambdaRestApi(self, 'Gateway',
            description='Endpoint for a simple Lambda-powered web service',
            handler=alias)

        failure_alarm = cloudwatch.Alarm(self, 'FailureAlarm',
            metric=cloudwatch.Metric(
                metric_name='5XXError',
                namespace='AWS/ApiGateway',
                dimensions={
                    'ApiName': 'Gateway',
                },
                statistic='Sum',
                period=core.Duration.minutes(1)),
            threshold=1,
            evaluation_periods=1)

        codedeploy.LambdaDeploymentGroup(self, 'DeploymentGroup',
            alias=alias,
            deployment_config=codedeploy.LambdaDeploymentConfig.CANARY_10_PERCENT_10_MINUTES,
            alarms=[failure_alarm])

        self.url_output = core.CfnOutput(self, 'Url',
            value=gw.url)
