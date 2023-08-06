import base64
import keyring
import logging


class VaultTools(object):
    headers = {'content-type': 'application/json'}

    def __init__(self, env, encode):
        self.env = env
        self.encode = encode
        self.logger = logging.getLogger(__name__)

    def set_password(self, usr, pwd):
        env = self.env
        user_notencoded = usr
        # set windows vault

        if self.encode:
            # if we choose to encode
            env = base64.b64encode(self.env.encode("utf-8")).decode("utf-8")
            usr = base64.b64encode(usr.encode("utf-8")).decode("utf-8")
            pwd = base64.b64encode((pwd.encode("utf-8"))).decode("utf-8")
        try:
            keyring.set_password(env, usr, pwd)
        except Exception as ex:
            self.logger.error("Error setting vault password: {0}".format(ex))

    def get_pwd(self, usr):
        env = self.env
        if self.encode:
            env = base64.b64encode(env.encode("utf-8")).decode("utf-8")
            usr = base64.b64encode(usr.encode("utf-8")).decode("utf-8")
        try:
            vault_pwd = keyring.get_password(env, usr)
            if self.encode:
                vault_pwd = base64.b64decode(vault_pwd).decode("utf-8")

        except Exception as ex:
            self.logger.error("Error getting Password from Windows Vaults: {0}".format(ex))
            return None
        return vault_pwd
