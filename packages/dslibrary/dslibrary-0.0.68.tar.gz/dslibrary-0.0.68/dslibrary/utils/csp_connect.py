
def connect_to_csp(service: str, for_write: bool=True, **kwargs):
    """
    Connect to various CSP services.
    :param service:         Name of a service on some CSP.
    :param for_write:       Ignored for the time being.
    :param kwargs:          Credentials and other options.
    :return: A native CSP connector, i.e. a boto3 client.
    """
    if service in ("s3", "sagemaker", "lambda"):
        import boto3
        access = {}
        for i, o in {
            "key": "aws_access_key_id", "secret": "aws_secret_access_key",
            "access_key": "aws_access_key_id", "secret_key": "aws_secret_access_key",
            "aws_access_key_id": "aws_access_key_id", "aws_secret_access_key": "aws_secret_access_key",
            "region": "region_name", "region_name": "region_name"
        }.items():
            if i in kwargs:
                access[o] = kwargs[i]
        return boto3.client(service, **access)

