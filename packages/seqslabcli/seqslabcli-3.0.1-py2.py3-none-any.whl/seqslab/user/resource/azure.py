from seqslab.auth.commands import BaseAuth
from seqslab.exceptions import exception_handler
from seqslab.user import API_HOSTNAME

from .base import BaseResource

"""
Copyright (C) 2022, Atgenomix Incorporated.

All Rights Reserved.

This program is an unpublished copyrighted work which is proprietary to
Atgenomix Incorporated and contains confidential information that is not to
be reproduced or disclosed to any other person or entity without prior
written consent from Atgenomix, Inc. in each and every instance.

Unauthorized reproduction of this program as well as unauthorized
preparation of derivative works based upon the program or distribution of
copies by sale, rental, lease or lending are violations of federal copyright
laws and state trade secret laws, punishable by civil and criminal penalties.
"""


class AzureResource(BaseResource):
    """
    Azure Compute services provides computation resource in Azure cloud.
    """

    CONSENT_URL = 'https://login.microsoftonline.com/{tenant}/adminconsent?' \
                  'state={user_id}/azure/&client_id=b10403db-7700-42c2-996e-116578438579&' \
                  'redirect_uri={host}/auth/v3/permissions/azure/ '

    def __init__(self):
        super().__init__()

    @exception_handler
    def admin_consent(self):
        if self.is_global_admin():
            token = BaseAuth.get_token().get('attrs')
            return AzureResource.CONSENT_URL.format(tenant=token.get('tid'),
                                                    user_id=token.get('user_id'),
                                                    host=f"https://{API_HOSTNAME}")
        else:
            raise PermissionError('Only user with Global administrator role is allowed to conduct admin consent')
