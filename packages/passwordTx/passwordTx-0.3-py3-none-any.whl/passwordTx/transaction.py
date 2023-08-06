import getpass
import os
from typing import Union
from web3 import Web3, contract
import time

from passwordTx.utils import create_key, encrypt_key, read_private_key, read_fpath


class PasswordTx:
    """ how to use?
    1. setting process
    ````python
    web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    passwordTx = passwordTx("user1", web3)
    > new Password : *****
    > PRIVATE KEY : *******
    ````

    2. send Tx
    ````python
    erc20 = web3.eth.contract(
        address=TOKEN_ADDRESS,
        abi=[
                {
                    'inputs': [{'internalType': 'address', 'name': 'amount', 'type': 'address'},
                               {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}],
                    'name': 'transfer',
                    'outputs': [],
                    'stateMutability': 'nonpayable',
                    'type': 'function'
                }
            ]
    )

    // password prompt will appear
    with PasswordTx("OPERATOR", web3) as tx:
        tx.send(
            erc20.functions.transfer(TO, AMOUNT)
        )
    ````

    """
    web3 = None
    __username = None
    __address = None
    __key = None
    __wait = None
    __verbose = True

    def __init__(self, username, web3: Web3, wait=2, verbose=True):
        """ create Instance

        :param username: private keys are managed independently for each username
        :param web3: instance of web3.py:Web3, Web3(Web3.HTTPProvider(JSON_RPC_URL))
        :param wait: idle time(seconds) after sending transaction
        :param verbose: if true, print all. if not, no print
        """
        if not isinstance(username, str) and username == '':
            raise ValueError("INVALID USERNAME")
        self.__username = username
        self.web3 = web3
        self.__wait = wait
        self.__verbose = verbose
        self.register()

    def register(self):
        """register private key & password
        """
        if os.path.exists(read_fpath(self.__username)):
            return
        password = getpass.getpass("NEW PASSWORD :")
        key = create_key(password)
        private_key = getpass.getpass("PRIVATE KEY : ")
        encrypt_key(self.__username, key, private_key)

    def update(self):
        """ update password
        """
        private_key = read_private_key(self.__username)
        address = self.web3.eth.account.from_key(private_key).address
        if self.__verbose:
            print(f"connect to address(${address})")
        password = getpass.getpass("NEW PASSWORD :")
        key = create_key(password)
        encrypt_key(self.__username, key, private_key)

    def destroy(self):
        """ destroy private key & password
        """
        fpath = read_fpath(self.__username)
        if not os.path.exists(fpath):
            raise ValueError("Not Exist key")
        read_private_key(self.__username)
        os.remove(fpath)

    def __enter__(self):
        """ check password verification & get temp private key
        """
        if not os.path.exists(read_fpath(self.__username)):
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

    def send(self, func: Union[contract.ContractFunction, str], value=None):
        if not self.__key:
            raise ValueError("verify password first")

        to = None
        if isinstance(func, str):
            # case: sending eth
            if not value:
                raise ValueError("value must be set")
            to = self.web3.toChecksumAddress(func)
        else:
            to = func.address

        if self.__verbose:
            if isinstance(func, contract.ContractFunction):
                print(f"CALL: {func.fn_name}{func.arguments} \nTO: {to}")
            else:
                print(f"SEND ETHER: {value}  \nTO: {to}")

        if isinstance(func, contract.ContractFunction):
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
        else:
            gasPrice = self.web3.eth.generate_gas_price()
            tx = {
                "nonce": self.web3.eth.getTransactionCount(self.__address),
                "gasPrice": gasPrice if gasPrice else self.web3.toWei('250', 'gwei'),
                "gas": 21000,
                "to": to,
                "value": value
            }

        signed_tx = self.web3.eth.account.signTransaction(tx, self.__key)
        self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        time.sleep(self.__wait)

        self.web3.eth.get_transaction_receipt(signed_tx.hash)

        if self.__verbose:
            print("RESULT : success\n")

    def __exit__(self, type, value, traceback):
        # destroy key after exit
        self.__address = None
        self.__key = None