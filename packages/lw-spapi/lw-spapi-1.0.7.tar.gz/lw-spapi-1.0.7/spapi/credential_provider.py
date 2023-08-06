class MissingCredentials(Exception):
    """
    Credentials are missing, see the error output to find possible causes
    """
    pass


class Config(object):
    def __init__(self, lwa_app_id, lwa_client_secret, aws_access_key, aws_secret_key, role_arn, refresh_token=None):
        self.refresh_token = refresh_token
        self.lwa_app_id = lwa_app_id
        self.lwa_client_secret = lwa_client_secret
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.role_arn = role_arn

        missing = self._check()
        if len(missing):
            raise MissingCredentials('The following configuration parameters are missing: %s' % missing)

    def _check(self):
        errors = []
        for k, v in self.__dict__.items():
            if not v and k != 'refresh_token':
                errors.append(k)
        return errors


class CredentialProvider(object):
    def __init__(self, credentials: dict):
        self.credentials = Config(**credentials)
