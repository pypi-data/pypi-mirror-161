import requests
from dotmap import DotMap
from exceptions import AuthorizationError, InvoiceError, TransferError, GetMeError, Error


class CryptoPay:
    def __init__(self, token: str) -> None:
        self.token = token
        self.url = " https://testnet-pay.crypt.bot/api/"
        self.headers = {
            "Crypto-Pay-API-Token": self.token,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"}
        self.BTC, self.TON, self.ETH, self.USDT, self.USDC, self.BUSD = "BTC", "TON", "ETH", "USDT", "USDC", "BUSD"

    def get_me(self) -> object:
        """
        Use this method to test your app's authentication token. Requires no parameters. On success, returns basic information about an app.

        :Return:

        - app_id: Application ID.
        - name: Application Name.
        - payment_processing_bot_username: The username of the bot for payment.
        """

        params = {"Host": "pay.crypt.bot"}

        response = requests.get(
            self.url+"getMe", headers=self.headers, data=params).json()

        if response["ok"] == True:
            data = response["result"]
            me = DotMap()
            me.app_id = data["app_id"]
            me.name = data["name"]
            me.payment_processing_bot_username = data["payment_processing_bot_username"]
            return me
        else:
            error = response["error"]
            status = error["code"]
            if status == 401:
                raise AuthorizationError(
                    "Check the correctness of your token.")
            else:
                raise GetMeError(f"Unknown error: {error['name']}")

    def create_invoice(self,
                       asset: str,
                       amount: str,
                       description: str = None,
                       hidden_message: str = None,
                       paid_btn_name: str = None,
                       paid_btn_url: str = None,
                       payload: str = None,
                       allow_comments: bool = True,
                       allow_anonymous: bool = True,
                       expires_in: int = None) -> object:
        """
        Use this method to create a new invoice. On success, returns an object of the created invoice.

        :param asset: Currency code. Supported assets: "BTC", "TON", "ETH", "USDT", "USDC" and "BUSD".
        :param amount: Amount of the invoice in float. For example: "125.50" 
        :param description: Optional. Description for the invoice. User will see this description when they pay the invoice. Up to 1024 characters.
        :param hidden_message: Optional. Text of the message that will be shown to a user after the invoice is paid. Up to 2048 characters.
        :param paid_btn_name: Optional. Name of the button that will be shown to a user after the invoice is paid.
            Supported names: 
            - "viewItem" – “View Item”
            - "openChannel" – “View Channel”
            - "openBot" – “Open Bot”
            - "callback" – “Return”

        :param paid_btn_url: Optional. Required if paid_btn_name is used. URL to be opened when the button is pressed. You can set any success link (for example, a link to your bot). Starts with https or http.
        :param payload: Optional. Any data you want to attach to the invoice (for example, user ID, payment ID, ect). Up to 4kb.
        :param allow_comments: Optional. Allow a user to add a comment to the payment. Default is true.
        :param allow_anonymous: Optional. Allow a user to pay the invoice anonymously. Default is true.
        :param expires_in: Optional. You can set a payment time limit for the invoice in seconds. Values between 1-2678400 are accepted.

        :Return:

        - invoice_id: Unique ID for this invoice.
        - status: Status of the invoice, can be either “active”, “paid” or “expired”.
        - hash: Hash of the invoice.
        - asset: Currency code. Currently, can be “BTC”, “TON”, “ETH”, “USDT”, “USDC” or “BUSD”.
        - amount: Amount of the invoice.
        - pay_url: URL should be presented to the user to pay the invoice.
        - created_at: Date the invoice was created in ISO 8601 format.
        - allow_comments: True, if the user can add comment to the payment.
        - allow_anonymous: True, if the user can pay the invoice anonymously.
        - expiration_date: Date the invoice expires in Unix time.
        """

        params = {
            "Host": "pay.crypt.bot",
            "asset": asset,
            "amount": amount,
            "allow_comments": allow_comments,
            "allow_anonymous": allow_anonymous}

        if description is not None:
            params["description"] = description
        if hidden_message is not None:
            params["hidden_message"] = hidden_message
        if paid_btn_name is not None:
            params["paid_btn_name"] = paid_btn_name
        if paid_btn_url is not None:
            params["paid_btn_url"] = paid_btn_url
        if payload is not None:
            params["payload"] = payload
        if expires_in is not None:
            params["expires_in"] = expires_in

        response = requests.get(
            self.url+"createInvoice", headers=self.headers, params=params).json()

        if response["ok"] == True:
            data = dict(response["result"])
            invoice = DotMap()
            invoice.invoice_id = data.get("invoice_id")
            invoice.status = data.get("status")
            invoice.hash = data.get("hash")
            invoice.asset = data.get("asset")
            invoice.amount = data.get("amount")
            invoice.pay_url = data.get("pay_url")
            invoice.created_at = data.get("created_at")
            invoice.allow_comments = data.get("allow_comments")
            invoice.allow_anonymous = data.get("allow_anonymous")
            invoice.expiration_date = data.get("expiration_date")
            return invoice
        else:
            error = response["error"]
            status = error["code"]
            if status == 401:
                raise AuthorizationError(
                    "Check the correctness of your token.")
            else:
                raise InvoiceError(f"Unknown error: {error['name']}")

    def transfer(self,
                 user_id: int,
                 asset: str,
                 amount: str,
                 spend_id: str,
                 comment: str = None,
                 disable_send_notification: bool = False) -> dict:
        """
        Use this method to send coins from your app's balance to a user. On success, returns object of completed transfer.

        :param user_id: Telegram user ID. User must have previously used @CryptoBot (@CryptoTestnetBot for testnet).
        :param asset: Currency code. Supported assets: “BTC”, “TON”, “ETH”, “USDT”, “USDC” and “BUSD”.
        :param amount: Amount of the transfer in float. The minimum and maximum amounts for each of the support asset roughly correspond to the limit of 1-25000 USD. Use get_exchange_rates() to convert amounts. For example: "125.50"
        :param spend_id: Unique ID to make your request idempotent and ensure that only one of the transfers with the same spend_id is accepted from your app. This parameter is useful when the transfer should be retried (i.e. request timeout, connection reset, 500 HTTP status, etc). Up to 64 symbols.
        :param comment: Optional. Comment for the transfer. Users will see this comment when they receive a notification about the transfer. Up to 1024 symbols.
        :param disable_send_notification: Optional. Pass true if the user should not receive a notification about the transfer.Default is false.

        :Return:

        - transfer_id: Unique ID for this transfer.
        - user_id: Telegram user ID the transfer was sent to.
        - asset: Currency code. Currently, can be “BTC”, “TON”, “ETH”, “USDT”, “USDC” or “BUSD”.
        - amount: Amount of the transfer.
        - status: Status of the transfer, can be “completed”.
        - completed_at: Date the transfer was completed in ISO 8601 format.
        - comment: Comment for this transfer.
        """

        params = {
            "Host": "pay.crypt.bot",
            "user_id": user_id,
            "asset": asset,
            "amount": amount,
            "spend_id": spend_id,
            "disable_send_notification": disable_send_notification}

        if comment is not None:
            params["comment"] = comment

        response = requests.get(self.url+"transfer",
                                headers=self.headers, params=params).json()
        if response["ok"] == True:
            data = dict(response["result"])
            obj = DotMap()
            obj.transfer_id = data.get("transfer_id")
            obj.user_id = data.get("user_id")
            obj.asset = data.get("asset")
            obj.amount = data.get("amount")
            obj.status = data.get("status")
            obj.completed_at = data.get("completed_at")
            obj.comment = data.get("comment")
        else:
            error = response["error"]
            status = error["code"]
            if status == 401:
                raise AuthorizationError(
                    "Check the correctness of your token.")
            else:
                raise TransferError(f"Unknown error: {error['name']}")

    def get_invoices(self,
                     asset: str = None,
                     invoice_ids: list = None,
                     status: str = None,
                     offset: int = 0,
                     count: int = 100) -> list:
        """
        Use this method to get invoices of your app. On success, returns array of invoices.

        :param asset: Optional. Currency codes separated by comma. Supported assets: “BTC”, “TON”, “ETH” (testnet only), “USDT”, “USDC” and “BUSD”. Defaults to all assets.
        :param invoice_ids: Optional. Invoice IDs separated by comma.
        :param status: Optional. Status of invoices to be returned. Available statuses: “active” and “paid”. Defaults to all statuses.
        :param offset: Optional. Offset needed to return a specific subset of invoices. Default is 0.
        :param count: Optional. Number of invoices to be returned. Values between 1-1000 are accepted. Default is 100.

        :Return:

        Returns a list of invoices in the form of dictionaries.
        Each dictionary in the list has the following values:
        - invoice_id: Unique ID for this invoice.
        - status: Status of the invoice, can be either “active”, “paid” or “expired”.
        - hash: Hash of the invoice.
        - asset: Currency code. Currently, can be “BTC”, “TON”, “ETH”, “USDT”, “USDC” or “BUSD”.
        - amount: Amount of the invoice.
        - pay_url: URL should be presented to the user to pay the invoice.
        - created_at: Date the invoice was created in ISO 8601 format.
        - allow_comments: True, if the user can add comment to the payment.
        - allow_anonymous: True, if the user can pay the invoice anonymously.
        """

        params = {"Host": "pay.crypt.bot"}

        if asset is not None:
            params["asset"] = asset
        if invoice_ids is not None:
            params["invoice_ids"] = invoice_ids
        if status is not None:
            params["status"] = status
        if offset != 0:
            params["offset"] = offset
        if count != 100:
            params["count"] = count

        response = requests.get(self.url+"getInvoices",
                                headers=self.headers, params=params).json()

        if response["ok"] == True:
            return response["result"]["items"]
        else:
            error = response["error"]
            status = error["code"]
            if status == 401:
                raise AuthorizationError(
                    "Check the correctness of your token.")
            else:
                raise InvoiceError(f"Unknown error: {error['name']}")

    def get_balance(self) -> list:
        """
        Use this method to get a balance of your app. Returns array of assets.

        :Return:

        Returns a list of assets in the form of dictionaries.
        Each dictionary in the list has the following values:
        - currency_code: Currency code. Currently, can be “BTC”, “TON”, “ETH”, “USDT”, “USDC” or “BUSD”.
        - available: Account balance.
        """

        params = {"Host": "pay.crypt.bot"}

        response = requests.get(self.url+"getBalance",
                                headers=self.headers, params=params).json()

        if response["ok"] == True:
            return response["result"]
        else:
            error = response["error"]
            status = error["code"]
            if status == 401:
                raise AuthorizationError(
                    "Check the correctness of your token.")
            else:
                raise InvoiceError(f"Unknown error: {error['name']}")

    def get_exchange_rates(self) -> list:
        """
        Use this method to get exchange rates of supported currencies. Returns array of currencies.

        Return:

        Returns a list containing dictionaries. Each dictionary has the following meanings:
        - is_valid: True, if the course is valid.
        - source: Currency code. Currently, can be “BTC”, “TON”, “ETH”, “USDT”, “USDC” or “BUSD”.
        - target: The code of the fiat currency. Currently it can be "RUB", "USD", "EUR", "BYN", "UAH", "KZT".
        - rate: The exchange rate in relation to the fiat currency. Type: float.
        """

        params = {"Host": "pay.crypt.bot"}

        response = requests.get(
            self.url+"getExchangeRates", headers=self.headers, params=params).json()

        if response["ok"] == True:
            return response["result"]
        else:
            error = response["error"]
            status = error["code"]
            if status == 401:
                raise AuthorizationError(
                    "Check the correctness of your token.")
            else:
                raise Error(f"Unknown error: {error['name']}")

    def get_currencies(self) -> list:
        """
        Use this method to get a list of supported currencies. Returns array of currencies.

        Return:

        Returns a list containing dictionaries. Each dictionary has the following meanings:
        - is_blockchain: True, if the blockchain.
        - is_stablecoin: True, if the stablecoin.
        - is_fiat: True, if the fiat currency.
        - name: Currency name.
        - code: Currency code.
        - url: Link to the official website. There is no fiat currency.
        - decimals: Tell me what it means. Write in the telegram @vlad_eat.
        """

        params = {"Host": "pay.crypt.bot"}

        response = requests.get(self.url+"getCurrencies",
                                headers=self.headers, params=params).json()

        if response["ok"] == True:
            return response["result"]
        else:
            return response["error"]
