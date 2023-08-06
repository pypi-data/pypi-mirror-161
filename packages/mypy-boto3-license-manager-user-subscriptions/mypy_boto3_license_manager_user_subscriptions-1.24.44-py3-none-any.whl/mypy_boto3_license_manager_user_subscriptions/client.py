"""
Type annotations for license-manager-user-subscriptions service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_license_manager_user_subscriptions.client import LicenseManagerUserSubscriptionsClient

    session = Session()
    client: LicenseManagerUserSubscriptionsClient = session.client("license-manager-user-subscriptions")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .paginator import (
    ListIdentityProvidersPaginator,
    ListInstancesPaginator,
    ListProductSubscriptionsPaginator,
    ListUserAssociationsPaginator,
)
from .type_defs import (
    AssociateUserResponseTypeDef,
    DeregisterIdentityProviderResponseTypeDef,
    DisassociateUserResponseTypeDef,
    FilterTypeDef,
    IdentityProviderTypeDef,
    ListIdentityProvidersResponseTypeDef,
    ListInstancesResponseTypeDef,
    ListProductSubscriptionsResponseTypeDef,
    ListUserAssociationsResponseTypeDef,
    RegisterIdentityProviderResponseTypeDef,
    StartProductSubscriptionResponseTypeDef,
    StopProductSubscriptionResponseTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("LicenseManagerUserSubscriptionsClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class LicenseManagerUserSubscriptionsClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        LicenseManagerUserSubscriptionsClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#exceptions)
        """

    def associate_user(
        self,
        *,
        IdentityProvider: IdentityProviderTypeDef,
        InstanceId: str,
        Username: str,
        Domain: str = ...
    ) -> AssociateUserResponseTypeDef:
        """
        Associates the user to an EC2 instance to utilize user-based subscriptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.associate_user)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#associate_user)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#can_paginate)
        """

    def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.close)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#close)
        """

    def deregister_identity_provider(
        self, *, IdentityProvider: IdentityProviderTypeDef, Product: str
    ) -> DeregisterIdentityProviderResponseTypeDef:
        """
        Deregisters the identity provider from providing user-based subscriptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.deregister_identity_provider)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#deregister_identity_provider)
        """

    def disassociate_user(
        self,
        *,
        IdentityProvider: IdentityProviderTypeDef,
        InstanceId: str,
        Username: str,
        Domain: str = ...
    ) -> DisassociateUserResponseTypeDef:
        """
        Disassociates the user from an EC2 instance providing user-based subscriptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.disassociate_user)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#disassociate_user)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#generate_presigned_url)
        """

    def list_identity_providers(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListIdentityProvidersResponseTypeDef:
        """
        Lists the identity providers for user-based subscriptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.list_identity_providers)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#list_identity_providers)
        """

    def list_instances(
        self, *, Filters: Sequence[FilterTypeDef] = ..., MaxResults: int = ..., NextToken: str = ...
    ) -> ListInstancesResponseTypeDef:
        """
        Lists the EC2 instances providing user-based subscriptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.list_instances)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#list_instances)
        """

    def list_product_subscriptions(
        self,
        *,
        IdentityProvider: IdentityProviderTypeDef,
        Product: str,
        Filters: Sequence[FilterTypeDef] = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListProductSubscriptionsResponseTypeDef:
        """
        Lists the user-based subscription products available from an identity provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.list_product_subscriptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#list_product_subscriptions)
        """

    def list_user_associations(
        self,
        *,
        IdentityProvider: IdentityProviderTypeDef,
        InstanceId: str,
        Filters: Sequence[FilterTypeDef] = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListUserAssociationsResponseTypeDef:
        """
        Lists user associations for an identity provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.list_user_associations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#list_user_associations)
        """

    def register_identity_provider(
        self, *, IdentityProvider: IdentityProviderTypeDef, Product: str
    ) -> RegisterIdentityProviderResponseTypeDef:
        """
        Registers an identity provider for user-based subscriptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.register_identity_provider)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#register_identity_provider)
        """

    def start_product_subscription(
        self,
        *,
        IdentityProvider: IdentityProviderTypeDef,
        Product: str,
        Username: str,
        Domain: str = ...
    ) -> StartProductSubscriptionResponseTypeDef:
        """
        Starts a product subscription for a user with the specified identity provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.start_product_subscription)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#start_product_subscription)
        """

    def stop_product_subscription(
        self,
        *,
        IdentityProvider: IdentityProviderTypeDef,
        Product: str,
        Username: str,
        Domain: str = ...
    ) -> StopProductSubscriptionResponseTypeDef:
        """
        Stops a product subscription for a user with the specified identity provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.stop_product_subscription)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#stop_product_subscription)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_identity_providers"]
    ) -> ListIdentityProvidersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_instances"]) -> ListInstancesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_product_subscriptions"]
    ) -> ListProductSubscriptionsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_user_associations"]
    ) -> ListUserAssociationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/license-manager-user-subscriptions.html#LicenseManagerUserSubscriptions.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_license_manager_user_subscriptions/client/#get_paginator)
        """
