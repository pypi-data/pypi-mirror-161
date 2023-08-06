import getpass
import base64
import os
from web3 import Web3
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import time

ROOT_DIR = os.path.join(os.path.expanduser('~'), ".password_tx")
os.makedirs(ROOT_DIR, exist_ok=True)


def create_key(password):
    """ create fernet key from password
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"\xa1\xce'\xfe\xd6\x9d\x80\xd0/\xe9\n\x11\x12\xe8'\x91",
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))


def encrypt_key(username, key, private_key):
    """ encrypt & save privateKey to ROOT_DIR
    """
    fernet = Fernet(key)
    with open(os.path.join(ROOT_DIR, username), "wb") as f:
        f.write(fernet.encrypt(private_key.encode('utf-8')))


def decrypt_key(key, username):
    """ read & decrpyt privateKey from ROOT_DIR
    """
    fernet = Fernet(key)
    with open(os.path.join(ROOT_DIR, username), "rb") as f:
        return fernet.decrypt(f.read()).decode('utf-8')


def read_private_key(username):
    """ read private key with password
    """
    password = getpass.getpass("PASSWORD :")
    try:
        key = create_key(password)
        return decrypt_key(key, username)
    except Exception as e:
        raise ValueError("WRONG PASSWORD")


class PasswordTx:
    web3 = None
    __username = None
    __address = None
    __key = None
    __wait = None
    __verbose = True

    def __init__(self, username, web3: Web3, wait=2, verbose=True):
        self.__username = username
        self.web3 = web3
        self.__wait = wait
        self.__verbose = verbose

    def register(self):
        """register private key & password
        """
        if not os.path.exists(os.path.join(ROOT_DIR, self.__username)):
            password = getpass.getpass("NEW PASSWORD :")
            key = create_key(password)
            private_key = getpass.getpass("PRIVATE KEY : ")
        else:
            private_key = read_private_key(self.__username)
            password = getpass.getpass("NEW PASSWORD :")
            key = create_key(password)
        encrypt_key(self.__username, key, private_key)

    def destroy(self):
        """ destroy private key & password
        """
        fpath = os.path.join(ROOT_DIR, self.__username)
        if not os.path.exists(fpath):
            raise ValueError("Not Exist key")
        private_key = read_private_key(self.__username)
        os.remove(fpath)

    def __enter__(self):
        """ check password verification & get temp private key
        """
        if not os.path.exists(os.path.join(ROOT_DIR, self.__username)):
            raise ValueError(f"Not Registered User...{self.__username}")

        self.__key = read_private_key(self.__username)
        self.__address = self.web3.eth.account.from_key(self.__key).address

        if self.__verbose:
            print(f"connect to address(${self.__address})")
        return self

    def address(self):
        """ get user's address
        """
        if self.__address:
            return self.__address
        else:
            raise ValueError("verify password first")

    def send(self, func, value=None):
        if not self.__key:
            raise ValueError("verify password first")

        if self.__verbose:
            print(f"CALL: {func.fn_name}{func.arguments} \nTO: {func.address}")

        if value:
            tx = func.buildTransaction({
                "from": self.__address,
                "value": value,
                "nonce": self.web3.eth.getTransactionCount(self.__address)
            })
        else:
            tx = func.buildTransaction({
                "from": self.__address,
                "nonce": self.web3.eth.getTransactionCount(self.__address)
            })

        signed_tx = self.web3.eth.account.signTransaction(tx, self.__key)
        self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        time.sleep(self.__wait)

        if self.__verbose:
            print("RESULT : success\n")

    def __exit__(self, type, value, traceback):
        # destroy key after exit
        self.__address = None
        self.__key = None