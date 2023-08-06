import environ

env = environ.Env()
environ.Env.read_env("/etc/seqslab/cli_apps.env")

name = "roles"

__all__ = [

]

__version__ = "v3"

PRIVATE_NAME = env.str("PRIVATE_NAME", "api")
API_HOSTNAME = f"{PRIVATE_NAME}.seqslab.net"
