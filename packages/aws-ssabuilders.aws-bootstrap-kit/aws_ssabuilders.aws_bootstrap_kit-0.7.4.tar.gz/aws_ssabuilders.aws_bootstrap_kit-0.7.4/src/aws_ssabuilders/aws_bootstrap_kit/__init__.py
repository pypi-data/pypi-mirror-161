'''
# AWS Bootstrap Kit main package

Expose a set of stacks and constructs to help you get started properly on AWS.

## Usage

1. install

   ```
   npm install aws-bootstrap-kit
   ```
2. Check the [Examples](https://github.com/aws-samples/aws-bootstrap-kit-examples) and [API Doc](./API.md) for more details

## Contributing

Check [CONTRIBUTING.md](/source/aws-bootstrap-kit/CONTRIBUTING.md)
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk
import aws_cdk.aws_iam
import aws_cdk.aws_route53
import constructs


class Account(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-bootstrap-kit.Account",
):
    '''An AWS Account.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        account_props: "IAccountProps",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account_props: -
        '''
        jsii.create(self.__class__, self, [scope, id, account_props])

    @jsii.member(jsii_name="registerAsDelegatedAdministrator")
    def register_as_delegated_administrator(
        self,
        account_id: builtins.str,
        service_principal: builtins.str,
    ) -> None:
        '''
        :param account_id: -
        :param service_principal: -
        '''
        return typing.cast(None, jsii.invoke(self, "registerAsDelegatedAdministrator", [account_id, service_principal]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountName")
    def account_name(self) -> builtins.str:
        '''Constructor.'''
        return typing.cast(builtins.str, jsii.get(self, "accountName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountStageName")
    def account_stage_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountStageName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountStageOrder")
    def account_stage_order(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accountStageOrder"))


@jsii.data_type(
    jsii_type="aws-bootstrap-kit.AccountSpec",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "email": "email",
        "existing_account_id": "existingAccountId",
        "hosted_services": "hostedServices",
        "removal_policy": "removalPolicy",
        "stage_name": "stageName",
        "stage_order": "stageOrder",
        "type": "type",
    },
)
class AccountSpec:
    def __init__(
        self,
        *,
        name: builtins.str,
        email: typing.Optional[builtins.str] = None,
        existing_account_id: typing.Optional[builtins.str] = None,
        hosted_services: typing.Optional[typing.Sequence[builtins.str]] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        stage_name: typing.Optional[builtins.str] = None,
        stage_order: typing.Optional[jsii.Number] = None,
        type: typing.Optional["AccountType"] = None,
    ) -> None:
        '''AWS Account input details.

        :param name: The name of the AWS account.
        :param email: The email associated to the AWS account.
        :param existing_account_id: The (optional) id of the account to reuse, instead of creating a new account.
        :param hosted_services: List of your services that will be hosted in this account. Set it to [ALL] if you don't plan to have dedicated account for each service.
        :param removal_policy: RemovalPolicy of the account (wether it must be retained or destroyed). See https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html#aws-attribute-deletionpolicy-options. As an account cannot be deleted, RETAIN is the default value. If you choose DESTROY instead (default behavior of CloudFormation), the stack deletion will fail and you will have to manually remove the account from the organization before retrying to delete the stack: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_remove.html Note that existing accounts (when using ``existingAccountId``) are retained whatever the removalPolicy is. Default: RemovalPolicy.RETAIN
        :param stage_name: The (optional) Stage name to be used in CI/CD pipeline.
        :param stage_order: The (optional) Stage deployment order.
        :param type: The account type.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if email is not None:
            self._values["email"] = email
        if existing_account_id is not None:
            self._values["existing_account_id"] = existing_account_id
        if hosted_services is not None:
            self._values["hosted_services"] = hosted_services
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if stage_name is not None:
            self._values["stage_name"] = stage_name
        if stage_order is not None:
            self._values["stage_order"] = stage_order
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the AWS account.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''The email associated to the AWS account.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existing_account_id(self) -> typing.Optional[builtins.str]:
        '''The (optional) id of the account to reuse, instead of creating a new account.'''
        result = self._values.get("existing_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hosted_services(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of your services that will be hosted in this account.

        Set it to [ALL] if you don't plan to have dedicated account for each service.
        '''
        result = self._values.get("hosted_services")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''RemovalPolicy of the account (wether it must be retained or destroyed). See https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html#aws-attribute-deletionpolicy-options.

        As an account cannot be deleted, RETAIN is the default value.

        If you choose DESTROY instead (default behavior of CloudFormation), the stack deletion will fail and
        you will have to manually remove the account from the organization before retrying to delete the stack:
        https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_remove.html

        Note that existing accounts (when using ``existingAccountId``) are retained whatever the removalPolicy is.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''The (optional) Stage name to be used in CI/CD pipeline.'''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage_order(self) -> typing.Optional[jsii.Number]:
        '''The (optional) Stage deployment order.'''
        result = self._values.get("stage_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type(self) -> typing.Optional["AccountType"]:
        '''The account type.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional["AccountType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="aws-bootstrap-kit.AccountType")
class AccountType(enum.Enum):
    '''The type of the AWS account.'''

    CICD = "CICD"
    '''The account used to deploy CI/CD pipelines (See `here <https://cs.github.com/?scopeName=bk&scope=repo%3Aawslabs%2Faws-bootstrap-kit&q=AccountType.CICD>`_ for internal usage).'''
    STAGE = "STAGE"
    '''Accounts which will be used to deploy Stage environments (staging/prod ...). (See `here <https://cs.github.com/?scopeName=bk&scope=repo%3Aawslabs%2Faws-bootstrap-kit&q=AccountType.STAGE>`_ for internal usage).'''
    PLAYGROUND = "PLAYGROUND"
    '''Sandbox accounts dedicated to developers work.'''


class AwsOrganizationsStack(
    aws_cdk.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-bootstrap-kit.AwsOrganizationsStack",
):
    '''A Stack creating the Software Development Life Cycle (SDLC) Organization.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        email: builtins.str,
        nested_ou: typing.Sequence["OUSpec"],
        existing_root_hosted_zone_id: typing.Optional[builtins.str] = None,
        force_email_verification: typing.Optional[builtins.bool] = None,
        root_hosted_zone_dns_name: typing.Optional[builtins.str] = None,
        third_party_provider_dns_used: typing.Optional[builtins.bool] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[aws_cdk.Environment] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[aws_cdk.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param email: (experimental) Email address of the Root account.
        :param nested_ou: (experimental) Specification of the sub Organizational Unit.
        :param existing_root_hosted_zone_id: (experimental) The (optional) existing root hosted zone id to use instead of creating one.
        :param force_email_verification: (experimental) Enable Email Verification Process.
        :param root_hosted_zone_dns_name: (experimental) The main DNS domain name to manage.
        :param third_party_provider_dns_used: (experimental) A boolean used to decide if domain should be requested through this delpoyment or if already registered through a third party.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        props = AwsOrganizationsStackProps(
            email=email,
            nested_ou=nested_ou,
            existing_root_hosted_zone_id=existing_root_hosted_zone_id,
            force_email_verification=force_email_verification,
            root_hosted_zone_dns_name=root_hosted_zone_dns_name,
            third_party_provider_dns_used=third_party_provider_dns_used,
            analytics_reporting=analytics_reporting,
            description=description,
            env=env,
            stack_name=stack_name,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootDns")
    def root_dns(self) -> typing.Optional["RootDns"]:
        return typing.cast(typing.Optional["RootDns"], jsii.get(self, "rootDns"))


@jsii.data_type(
    jsii_type="aws-bootstrap-kit.AwsOrganizationsStackProps",
    jsii_struct_bases=[aws_cdk.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "description": "description",
        "env": "env",
        "stack_name": "stackName",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "email": "email",
        "nested_ou": "nestedOU",
        "existing_root_hosted_zone_id": "existingRootHostedZoneId",
        "force_email_verification": "forceEmailVerification",
        "root_hosted_zone_dns_name": "rootHostedZoneDNSName",
        "third_party_provider_dns_used": "thirdPartyProviderDNSUsed",
    },
)
class AwsOrganizationsStackProps(aws_cdk.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[aws_cdk.Environment] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[aws_cdk.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        email: builtins.str,
        nested_ou: typing.Sequence["OUSpec"],
        existing_root_hosted_zone_id: typing.Optional[builtins.str] = None,
        force_email_verification: typing.Optional[builtins.bool] = None,
        root_hosted_zone_dns_name: typing.Optional[builtins.str] = None,
        third_party_provider_dns_used: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for AWS SDLC Organizations Stack.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param email: (experimental) Email address of the Root account.
        :param nested_ou: (experimental) Specification of the sub Organizational Unit.
        :param existing_root_hosted_zone_id: (experimental) The (optional) existing root hosted zone id to use instead of creating one.
        :param force_email_verification: (experimental) Enable Email Verification Process.
        :param root_hosted_zone_dns_name: (experimental) The main DNS domain name to manage.
        :param third_party_provider_dns_used: (experimental) A boolean used to decide if domain should be requested through this delpoyment or if already registered through a third party.

        :stability: experimental
        '''
        if isinstance(env, dict):
            env = aws_cdk.Environment(**env)
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
            "nested_ou": nested_ou,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if existing_root_hosted_zone_id is not None:
            self._values["existing_root_hosted_zone_id"] = existing_root_hosted_zone_id
        if force_email_verification is not None:
            self._values["force_email_verification"] = force_email_verification
        if root_hosted_zone_dns_name is not None:
            self._values["root_hosted_zone_dns_name"] = root_hosted_zone_dns_name
        if third_party_provider_dns_used is not None:
            self._values["third_party_provider_dns_used"] = third_party_provider_dns_used

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[aws_cdk.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[aws_cdk.Environment], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[aws_cdk.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        :default:

        - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag
        is set, ``LegacyStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[aws_cdk.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def email(self) -> builtins.str:
        '''(experimental) Email address of the Root account.

        :stability: experimental
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def nested_ou(self) -> typing.List["OUSpec"]:
        '''(experimental) Specification of the sub Organizational Unit.

        :stability: experimental
        '''
        result = self._values.get("nested_ou")
        assert result is not None, "Required property 'nested_ou' is missing"
        return typing.cast(typing.List["OUSpec"], result)

    @builtins.property
    def existing_root_hosted_zone_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The (optional) existing root hosted zone id to use instead of creating one.

        :stability: experimental
        '''
        result = self._values.get("existing_root_hosted_zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_email_verification(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable Email Verification Process.

        :stability: experimental
        '''
        result = self._values.get("force_email_verification")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def root_hosted_zone_dns_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The main DNS domain name to manage.

        :stability: experimental
        '''
        result = self._values.get("root_hosted_zone_dns_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def third_party_provider_dns_used(self) -> typing.Optional[builtins.bool]:
        '''(experimental) A boolean used to decide if domain should be requested through this delpoyment or if already registered through a third party.

        :stability: experimental
        '''
        result = self._values.get("third_party_provider_dns_used")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsOrganizationsStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CrossAccountDNSDelegator(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-bootstrap-kit.CrossAccountDNSDelegator",
):
    '''TODO: propose this to fix https://github.com/aws/aws-cdk/issues/8776 High-level construct that creates: 1. A public hosted zone in the current account 2. A record name in the hosted zone id of target account.

    Usage:
    Create a role with the following permission:
    {
    "Sid": "VisualEditor0",
    "Effect": "Allow",
    "Action": [
    "route53:GetHostedZone",
    "route53:ChangeResourceRecordSets"
    ],
    "Resource": "arn:aws:route53:::hostedzone/ZXXXXXXXXX"
    }

    Then use the construct like this:

    const crossAccountDNSDelegatorProps: ICrossAccountDNSDelegatorProps = {
    targetAccount: '1234567890',
    targetRoleToAssume: 'DelegateRecordUpdateRoleInThatAccount',
    targetHostedZoneId: 'ZXXXXXXXXX',
    zoneName: 'subdomain.mydomain.com',
    };

    new CrossAccountDNSDelegator(this, 'CrossAccountDNSDelegatorStack', crossAccountDNSDelegatorProps);
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: "ICrossAccountDNSDelegatorProps",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> aws_cdk.aws_route53.HostedZone:
        return typing.cast(aws_cdk.aws_route53.HostedZone, jsii.get(self, "hostedZone"))


@jsii.interface(jsii_type="aws-bootstrap-kit.IAccountProps")
class IAccountProps(typing_extensions.Protocol):
    '''Properties of an AWS account.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        '''The email to use to create the AWS account.'''
        ...

    @email.setter
    def email(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the AWS Account.'''
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedServices")
    def hosted_services(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of your services that will be hosted in this account.

        Set it to [ALL] if you don't plan to have dedicated account for each service.
        '''
        ...

    @hosted_services.setter
    def hosted_services(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> typing.Optional[builtins.str]:
        '''The AWS account Id.'''
        ...

    @id.setter
    def id(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentOrganizationalUnitId")
    def parent_organizational_unit_id(self) -> typing.Optional[builtins.str]:
        '''The potential Organizational Unit Id the account should be placed in.'''
        ...

    @parent_organizational_unit_id.setter
    def parent_organizational_unit_id(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentOrganizationalUnitName")
    def parent_organizational_unit_name(self) -> typing.Optional[builtins.str]:
        '''The potential Organizational Unit Name the account should be placed in.'''
        ...

    @parent_organizational_unit_name.setter
    def parent_organizational_unit_name(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="removalPolicy")
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''RemovalPolicy of the account.

        See https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html#aws-attribute-deletionpolicy-options

        :default: RemovalPolicy.RETAIN
        '''
        ...

    @removal_policy.setter
    def removal_policy(self, value: typing.Optional[aws_cdk.RemovalPolicy]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''The (optional) Stage name to be used in CI/CD pipeline.'''
        ...

    @stage_name.setter
    def stage_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageOrder")
    def stage_order(self) -> typing.Optional[jsii.Number]:
        '''The (optional) Stage deployment order.'''
        ...

    @stage_order.setter
    def stage_order(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[AccountType]:
        '''The account type.'''
        ...

    @type.setter
    def type(self, value: typing.Optional[AccountType]) -> None:
        ...


class _IAccountPropsProxy:
    '''Properties of an AWS account.'''

    __jsii_type__: typing.ClassVar[str] = "aws-bootstrap-kit.IAccountProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        '''The email to use to create the AWS account.'''
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        jsii.set(self, "email", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the AWS Account.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedServices")
    def hosted_services(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of your services that will be hosted in this account.

        Set it to [ALL] if you don't plan to have dedicated account for each service.
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "hostedServices"))

    @hosted_services.setter
    def hosted_services(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "hostedServices", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> typing.Optional[builtins.str]:
        '''The AWS account Id.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "id"))

    @id.setter
    def id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentOrganizationalUnitId")
    def parent_organizational_unit_id(self) -> typing.Optional[builtins.str]:
        '''The potential Organizational Unit Id the account should be placed in.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentOrganizationalUnitId"))

    @parent_organizational_unit_id.setter
    def parent_organizational_unit_id(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "parentOrganizationalUnitId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentOrganizationalUnitName")
    def parent_organizational_unit_name(self) -> typing.Optional[builtins.str]:
        '''The potential Organizational Unit Name the account should be placed in.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentOrganizationalUnitName"))

    @parent_organizational_unit_name.setter
    def parent_organizational_unit_name(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "parentOrganizationalUnitName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="removalPolicy")
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''RemovalPolicy of the account.

        See https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html#aws-attribute-deletionpolicy-options

        :default: RemovalPolicy.RETAIN
        '''
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], jsii.get(self, "removalPolicy"))

    @removal_policy.setter
    def removal_policy(self, value: typing.Optional[aws_cdk.RemovalPolicy]) -> None:
        jsii.set(self, "removalPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''The (optional) Stage name to be used in CI/CD pipeline.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stageName"))

    @stage_name.setter
    def stage_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "stageName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageOrder")
    def stage_order(self) -> typing.Optional[jsii.Number]:
        '''The (optional) Stage deployment order.'''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "stageOrder"))

    @stage_order.setter
    def stage_order(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "stageOrder", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[AccountType]:
        '''The account type.'''
        return typing.cast(typing.Optional[AccountType], jsii.get(self, "type"))

    @type.setter
    def type(self, value: typing.Optional[AccountType]) -> None:
        jsii.set(self, "type", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAccountProps).__jsii_proxy_class__ = lambda : _IAccountPropsProxy


@jsii.interface(jsii_type="aws-bootstrap-kit.ICrossAccountDNSDelegatorProps")
class ICrossAccountDNSDelegatorProps(typing_extensions.Protocol):
    '''Properties to create delegated subzone of a zone hosted in a different account.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> builtins.str:
        '''The sub zone name to be created.'''
        ...

    @zone_name.setter
    def zone_name(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetAccount")
    def target_account(self) -> typing.Optional[builtins.str]:
        '''The Account hosting the parent zone Optional since can be resolved if the system has been setup with aws-bootstrap-kit.'''
        ...

    @target_account.setter
    def target_account(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetHostedZoneId")
    def target_hosted_zone_id(self) -> typing.Optional[builtins.str]:
        '''The parent zone Id to add the sub zone delegation NS record to Optional since can be resolved if the system has been setup with aws-bootstrap-kit.'''
        ...

    @target_hosted_zone_id.setter
    def target_hosted_zone_id(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetRoleToAssume")
    def target_role_to_assume(self) -> typing.Optional[builtins.str]:
        '''The role to Assume in the parent zone's account which has permissions to update the parent zone Optional since can be resolved if the system has been setup with aws-bootstrap-kit.'''
        ...

    @target_role_to_assume.setter
    def target_role_to_assume(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _ICrossAccountDNSDelegatorPropsProxy:
    '''Properties to create delegated subzone of a zone hosted in a different account.'''

    __jsii_type__: typing.ClassVar[str] = "aws-bootstrap-kit.ICrossAccountDNSDelegatorProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> builtins.str:
        '''The sub zone name to be created.'''
        return typing.cast(builtins.str, jsii.get(self, "zoneName"))

    @zone_name.setter
    def zone_name(self, value: builtins.str) -> None:
        jsii.set(self, "zoneName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetAccount")
    def target_account(self) -> typing.Optional[builtins.str]:
        '''The Account hosting the parent zone Optional since can be resolved if the system has been setup with aws-bootstrap-kit.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetAccount"))

    @target_account.setter
    def target_account(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "targetAccount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetHostedZoneId")
    def target_hosted_zone_id(self) -> typing.Optional[builtins.str]:
        '''The parent zone Id to add the sub zone delegation NS record to Optional since can be resolved if the system has been setup with aws-bootstrap-kit.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetHostedZoneId"))

    @target_hosted_zone_id.setter
    def target_hosted_zone_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "targetHostedZoneId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetRoleToAssume")
    def target_role_to_assume(self) -> typing.Optional[builtins.str]:
        '''The role to Assume in the parent zone's account which has permissions to update the parent zone Optional since can be resolved if the system has been setup with aws-bootstrap-kit.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetRoleToAssume"))

    @target_role_to_assume.setter
    def target_role_to_assume(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "targetRoleToAssume", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICrossAccountDNSDelegatorProps).__jsii_proxy_class__ = lambda : _ICrossAccountDNSDelegatorPropsProxy


@jsii.data_type(
    jsii_type="aws-bootstrap-kit.OUSpec",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "accounts": "accounts", "nested_ou": "nestedOU"},
)
class OUSpec:
    def __init__(
        self,
        *,
        name: builtins.str,
        accounts: typing.Optional[typing.Sequence[AccountSpec]] = None,
        nested_ou: typing.Optional[typing.Sequence["OUSpec"]] = None,
    ) -> None:
        '''Organizational Unit Input details.

        :param name: Name of the Organizational Unit.
        :param accounts: Accounts' specification inside in this Organizational Unit.
        :param nested_ou: Specification of sub Organizational Unit.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if accounts is not None:
            self._values["accounts"] = accounts
        if nested_ou is not None:
            self._values["nested_ou"] = nested_ou

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the Organizational Unit.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def accounts(self) -> typing.Optional[typing.List[AccountSpec]]:
        '''Accounts' specification inside in this Organizational Unit.'''
        result = self._values.get("accounts")
        return typing.cast(typing.Optional[typing.List[AccountSpec]], result)

    @builtins.property
    def nested_ou(self) -> typing.Optional[typing.List["OUSpec"]]:
        '''Specification of sub Organizational Unit.'''
        result = self._values.get("nested_ou")
        return typing.cast(typing.Optional[typing.List["OUSpec"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OUSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RootDns(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-bootstrap-kit.RootDns",
):
    '''A class creating the main hosted zone and a role assumable by stages account to be able to set sub domain delegation.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        root_hosted_zone_dns_name: builtins.str,
        stages_accounts: typing.Sequence[Account],
        existing_root_hosted_zone_id: typing.Optional[builtins.str] = None,
        third_party_provider_dns_used: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param root_hosted_zone_dns_name: The top level domain name.
        :param stages_accounts: The stages Accounts taht will need their subzone delegation.
        :param existing_root_hosted_zone_id: The (optional) existing root hosted zone id to use instead of creating one.
        :param third_party_provider_dns_used: A boolean indicating if Domain name has already been registered to a third party or if you want this contruct to create it (the latter is not yet supported).
        '''
        props = RootDnsProps(
            root_hosted_zone_dns_name=root_hosted_zone_dns_name,
            stages_accounts=stages_accounts,
            existing_root_hosted_zone_id=existing_root_hosted_zone_id,
            third_party_provider_dns_used=third_party_provider_dns_used,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createDNSAutoUpdateRole")
    def create_dns_auto_update_role(
        self,
        account: Account,
        stage_sub_zone: aws_cdk.aws_route53.HostedZone,
    ) -> aws_cdk.aws_iam.Role:
        '''
        :param account: -
        :param stage_sub_zone: -
        '''
        return typing.cast(aws_cdk.aws_iam.Role, jsii.invoke(self, "createDNSAutoUpdateRole", [account, stage_sub_zone]))

    @jsii.member(jsii_name="createRootHostedZone")
    def create_root_hosted_zone(
        self,
        *,
        root_hosted_zone_dns_name: builtins.str,
        stages_accounts: typing.Sequence[Account],
        existing_root_hosted_zone_id: typing.Optional[builtins.str] = None,
        third_party_provider_dns_used: typing.Optional[builtins.bool] = None,
    ) -> aws_cdk.aws_route53.IHostedZone:
        '''
        :param root_hosted_zone_dns_name: The top level domain name.
        :param stages_accounts: The stages Accounts taht will need their subzone delegation.
        :param existing_root_hosted_zone_id: The (optional) existing root hosted zone id to use instead of creating one.
        :param third_party_provider_dns_used: A boolean indicating if Domain name has already been registered to a third party or if you want this contruct to create it (the latter is not yet supported).
        '''
        props = RootDnsProps(
            root_hosted_zone_dns_name=root_hosted_zone_dns_name,
            stages_accounts=stages_accounts,
            existing_root_hosted_zone_id=existing_root_hosted_zone_id,
            third_party_provider_dns_used=third_party_provider_dns_used,
        )

        return typing.cast(aws_cdk.aws_route53.IHostedZone, jsii.invoke(self, "createRootHostedZone", [props]))

    @jsii.member(jsii_name="createStageSubZone")
    def create_stage_sub_zone(
        self,
        account: Account,
        root_hosted_zone_dns_name: builtins.str,
    ) -> aws_cdk.aws_route53.HostedZone:
        '''
        :param account: -
        :param root_hosted_zone_dns_name: -
        '''
        return typing.cast(aws_cdk.aws_route53.HostedZone, jsii.invoke(self, "createStageSubZone", [account, root_hosted_zone_dns_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootHostedZone")
    def root_hosted_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        return typing.cast(aws_cdk.aws_route53.IHostedZone, jsii.get(self, "rootHostedZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stagesHostedZones")
    def stages_hosted_zones(self) -> typing.List[aws_cdk.aws_route53.HostedZone]:
        return typing.cast(typing.List[aws_cdk.aws_route53.HostedZone], jsii.get(self, "stagesHostedZones"))


@jsii.data_type(
    jsii_type="aws-bootstrap-kit.RootDnsProps",
    jsii_struct_bases=[],
    name_mapping={
        "root_hosted_zone_dns_name": "rootHostedZoneDNSName",
        "stages_accounts": "stagesAccounts",
        "existing_root_hosted_zone_id": "existingRootHostedZoneId",
        "third_party_provider_dns_used": "thirdPartyProviderDNSUsed",
    },
)
class RootDnsProps:
    def __init__(
        self,
        *,
        root_hosted_zone_dns_name: builtins.str,
        stages_accounts: typing.Sequence[Account],
        existing_root_hosted_zone_id: typing.Optional[builtins.str] = None,
        third_party_provider_dns_used: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for RootDns.

        :param root_hosted_zone_dns_name: The top level domain name.
        :param stages_accounts: The stages Accounts taht will need their subzone delegation.
        :param existing_root_hosted_zone_id: The (optional) existing root hosted zone id to use instead of creating one.
        :param third_party_provider_dns_used: A boolean indicating if Domain name has already been registered to a third party or if you want this contruct to create it (the latter is not yet supported).
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "root_hosted_zone_dns_name": root_hosted_zone_dns_name,
            "stages_accounts": stages_accounts,
        }
        if existing_root_hosted_zone_id is not None:
            self._values["existing_root_hosted_zone_id"] = existing_root_hosted_zone_id
        if third_party_provider_dns_used is not None:
            self._values["third_party_provider_dns_used"] = third_party_provider_dns_used

    @builtins.property
    def root_hosted_zone_dns_name(self) -> builtins.str:
        '''The top level domain name.'''
        result = self._values.get("root_hosted_zone_dns_name")
        assert result is not None, "Required property 'root_hosted_zone_dns_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stages_accounts(self) -> typing.List[Account]:
        '''The stages Accounts taht will need their subzone delegation.'''
        result = self._values.get("stages_accounts")
        assert result is not None, "Required property 'stages_accounts' is missing"
        return typing.cast(typing.List[Account], result)

    @builtins.property
    def existing_root_hosted_zone_id(self) -> typing.Optional[builtins.str]:
        '''The (optional) existing root hosted zone id to use instead of creating one.'''
        result = self._values.get("existing_root_hosted_zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def third_party_provider_dns_used(self) -> typing.Optional[builtins.bool]:
        '''A boolean indicating if Domain name has already been registered to a third party or if you want this contruct to create it (the latter is not yet supported).'''
        result = self._values.get("third_party_provider_dns_used")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RootDnsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecureRootUser(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-bootstrap-kit.SecureRootUser",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        notification_email: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param notification_email: -
        '''
        jsii.create(self.__class__, self, [scope, id, notification_email])


class ValidateEmail(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-bootstrap-kit.ValidateEmail",
):
    '''Email Validation.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        email: builtins.str,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''Constructor.

        :param scope: The parent Construct instantiating this construct.
        :param id: This instance name.
        :param email: Email address of the Root account.
        :param timeout: -
        '''
        props = ValidateEmailProps(email=email, timeout=timeout)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="aws-bootstrap-kit.ValidateEmailProps",
    jsii_struct_bases=[],
    name_mapping={"email": "email", "timeout": "timeout"},
)
class ValidateEmailProps:
    def __init__(
        self,
        *,
        email: builtins.str,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''Properties of ValidateEmail.

        :param email: Email address of the Root account.
        :param timeout: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
        }
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def email(self) -> builtins.str:
        '''Email address of the Root account.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ValidateEmailProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Account",
    "AccountSpec",
    "AccountType",
    "AwsOrganizationsStack",
    "AwsOrganizationsStackProps",
    "CrossAccountDNSDelegator",
    "IAccountProps",
    "ICrossAccountDNSDelegatorProps",
    "OUSpec",
    "RootDns",
    "RootDnsProps",
    "SecureRootUser",
    "ValidateEmail",
    "ValidateEmailProps",
]

publication.publish()
