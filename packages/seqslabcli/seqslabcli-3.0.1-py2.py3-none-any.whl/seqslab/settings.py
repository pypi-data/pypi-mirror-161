from os.path import dirname, join

JWT_ALGORITHM = "HS256"
JWT_VERIFYING_KEY = "!de(^y-+=vqh6ky$gq8-_n%7ulrf@qha@1_rn1*7gv(^=_di^="

DRS_STORAGE_BACKENDS = {
    "azure": "seqslab.drs.storage.azure.BlobStorage",
}

WES_RESOURCE_BACKEND = {
    "azure": "seqslab.wes.resource.base.BaseResource",
}

TRS_RESOURCE_BACKEND = {
    "azure": "seqslab.trs.resource.azure.AzureResource",
}

WORKSPACE_RESOURCE_BACKEND = {
    "azure": "seqslab.workspace.resource.azure.AzureResource",
}

DRS_REGISTER_BACKENDS = {
    "azure": "seqslab.drs.api.azure.AzureDRSregister",
}

TRS_REGISTER_BACKEND = {
    "azure": "seqslab.trs.register.azure.AzureTRSregister",
}

ROLE_RESOURCE_BACKEND = {
    "azure": "seqslab.role.resource.azure.AzureResource",
}

USER_RESOURCE_BACKEND = {
    "azure": "seqslab.user.resource.azure.AzureResource",
}