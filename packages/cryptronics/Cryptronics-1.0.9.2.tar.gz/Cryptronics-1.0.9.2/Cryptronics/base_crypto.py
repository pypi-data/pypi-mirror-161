import requests


class Crypto(object):

    def __init__(
        self,
        octopus_api_key: str = None,
        crypto_api_key: str = None,
        eth_api_key: str = None,
        bnb_api_key: str = None
    ) -> None:
        # api keys
        self.OCTOPUS_API_KEY = octopus_api_key
        self.CRYPTO_API_KEY = crypto_api_key
        self.ETH_API_KEY = eth_api_key
        self.BNB_API_KEY = bnb_api_key

        # api url's
        self.OCTOPUS_URL = 'https://octopusapisoftware.com/api-tron'
        self.CRYPTO_URL = 'https://cryptocurrencyapi.net/api'
        self.ETH_URL = 'https://etherapi.net/api/v2'
        self.BNB_URL = 'https://bnbapi.net/api'

        # tokens supported
        self.SUPPORTED_TOKENS = {
            'cryptocurrency': ('btc', 'dash', 'doge', 'ltc', 'bch'),
            'octopus':        ('usdt'),
            'ethapi':         ('eth'),
            'bnbapi':         ('bnb')
        }

    def send(
        self,
        token: str,
        to_address: str,
        amount: float,
        tag: str = None,
        mix: bool = False
    ) -> dict:
        """Send tokens from main address to specified address

        Args:
            token (str): token to send (BTC, ETH etc.)
            to_address (str): address for which tokens need to be sended
            amount (float): amount of tokens to send
            tag (str, optional): to locate operation in API service.

        Raises:
            ValueError: if token isn't specified
            ValueError: if to_address isn't specified
            ValueError: if amount isn't specified
            ValueError: if token doesn't supported

        Returns:
            dict: response from API service

        """
        if not token:
            raise ValueError("'token' is required argument")
        if not to_address:
            raise ValueError("'to_address' is required argument")
        if not amount:
            raise ValueError("'amount' is required argument")
        if not self.is_token_supported(token):
            raise ValueError(f"Token {token} is not supported")

        key, url, api = self.get_key_and_url(token)
        if not mix:
            data = requests.get(
                f'{url}/{"send.html?" if api=="octopus" else ".send?"}'
                f'key={key}'
                f'&address={to_address}'
                f'&token={token}'
                f'&amount={amount}'
                f'&tag={tag}'
            )
            response = data.json()
        else:
            response = self.send_via_mixer(to_address, token, amount, tag)

        return response

    def create_wallet(
        self,
        token: str,
        tag: str
    ) -> dict:
        """Create new wallet for specified token in blockchain network

        Args:
            token (str): token for which wallet will be created
            tag (str): tag to identify wallet in API service

        Raises:
            ValueError: if token isn't specified

        Returns:
            dict: response from API service
        """
        if not token:
            raise ValueError("'token' is required argument")

        key, url, api = self.get_key_and_url(token)
        if api == 'octopus':
            response = requests.get(
                f'{url}/give.html?'
                f'key={key}&'
                f'tag={tag}&'
                f'token={token}'
            )
        elif api in ('eth', 'bnb'):
            response = requests.get(
                f'{url}/.give?'
                f'key={key}&'
            )
        elif api in ('cryptocurrency'):
            response = requests.get(
                f'{url}/.give?'
                f'key={key}&'
                f'tag={tag}&'
                f'currrency={token.upper()}'
            )
        return response.json()

    def get_key_and_url(
        self,
        token: str
    ) -> list:
        """private function to get key and url for specified token

        Args:
            token (str): token for which url and key will be returned

        Raises:
            ValueError: if tokens isn't specified
            ValueError: if can't find key for this token

        Returns:
            list: api key and api url
        """
        if not token:
            raise ValueError("'token' is required argument")
        key = None

        if token.lower() in self.SUPPORTED_TOKENS['octopus']:
            key, url, api = [self.OCTOPUS_API_KEY, self.OCTOPUS_URL, 'octopus']
        if token.lower() in self.SUPPORTED_TOKENS['cryptocurrency']:
            key, url, api = [self.CRYPTO_API_KEY, self.CRYPTO_URL, 'crypto']
        if token.lower() in self.SUPPORTED_TOKENS['ethapi']:
            key, url, api = [self.ETH_API_KEY, self.ETH_URL, 'eth']
        if token.lower() in self.SUPPORTED_TOKENS['bnbapi']:
            key, url, api = [self.BNB_API_KEY, self.BNB_URL, 'bnb']

        if key:
            return [key, url, api]
        else:
            raise ValueError(f"cannot find api key for token: '{token}'")

    def is_token_supported(
        self,
        token: str
    ) -> bool:
        if not token:
            raise ValueError("'token' is required argument")

        for _, tokens in self.SUPPORTED_TOKENS.items():
            if token in tokens:
                return True

        return False

    def generate_wallets(
        self,
        tokens: list[str],
        tag: str,
    ) -> list:
        """Generate multiple wallets

        Args:
            tokens (list[str]): list of tokens to generate wallets for
            tag (str): unique tag to define wallet in API service.
            For example, it cancontain user id in your database

        Returns:
            list: list of objects
            {
                "wallet":"<wallet_address>",
                "token":"<wallet_token>"
            }
        """
        if not tokens:
            return ValueError("'tokens' is required argument")
        if not tag:
            return ValueError("'tag' is required value")

        wallets = []

        for token in tokens:
            if not self.is_token_supported(token):
                return ValueError(f"Token {token} is not supported")

            wallet = self.create_wallet(token, f"{tag}-{token}")
            wallets.append(
                {
                    "wallet": wallet['result'],
                    "token": token
                }
            )

        return wallets

    def send_via_mixer(
        self,
        to_address: str,
        token: str,
        amount,
        tag: str = None
    ):
        return {'success': False}
