# dapi-python

A client library that talks to the [Dapi](https://dapi.com) [API](https://api.dapi.com).

## Quickstart

### Configure Project

First install the library.

```
$ pip install dapi-python
```

### Configure Library

1. Create a Dapi client instance with your App Secret.

```python
from dapi import DapiClient

client = DapiClient(app_secret="YOUR_APP_SECRET")
```

2. Now you can access any of the functions of the products available on the `DapiClient` instance, `client`, (`data` for example) to call Dapi with your `appSecret`.

```python
from dapi import DapiClient

client = DapiClient(app_secret="YOUR_APP_SECRET")
accounts_resp = client.data.getAccounts("YOUR_ACCESS_TOKEN", "YOUR_USER_SECRET")
```

3. Or, you can use the `handleSDKDapiRequests` function from the `DapiClient` instance inside your endpoint. Our code will basically update the request to add your app's `appSecret`
   to it, and forward the request to Dapi, then return the result.

```python
from dapi import DapiClient

client = DapiClient(app_secret="YOUR_APP_SECRET")

dapi_resp = client.handleSDKDapiRequests()  # inside your endpoint handler
```

## Reference

### !! Dapi API Disclaimer !!

Dapi's api request and response params are in camelCase, so while this library follows PEP8 standard and uses snake_case for all arguments, all responses will be in camelCase.

### BaseResponse

All the responses have the fields described here. Meaning all the responses described below in the document will have following fields besides the ones specific to each response.

| Parameter | Type | Description |
|---|---|---|
| operationID | `str` | Unique ID generated to identify a specific operation. |
| success | `bool` | Returns true if request is successful and false otherwise." |
| status | `str` | The status of the job. <br><br> `done` - Operation Completed. <br> `failed` - Operation Failed. <br> `user_input_required` - Pending User Input. <br> `initialized` - Operation In Progress. <br><br> For further explanation see [Operation Statuses](https://dapi-api.readme.io/docs/operation-statuses). |
| userInputs | `[dict]` | Array of `UserInput` objects, that are needed to complete this operation. <br><br> Specifies the type of further information required from the user before the job can be completed. <br><br> Note: It's only returned if operation status is `user_input_required` |
| type | `str` | Type of error encountered. <br><br> Note: It's only returned if operation status is `failed` |
| msg | `str` | Detailed description of the error. <br><br> Note: It's only returned if operation status is `failed` |

#### UserInput Object

| Parameter | Type | Description |
|---|---|---|
| id | `str` | Type of input required. <br><br> You can read more about user input types on [User Input Types](https://dapi-api.readme.io/docs/user-input-types). |
| query | `str` | Textual description of what is required from the user side. |
| index | `int` | Is used in case more than one user input is requested. <br> Will always be 0 If only one input is requested. |
| answer | `str` | User input that must be submitted. In the response it will always be empty. |

### Methods

#### auth.exchangeToken

Method is used to obtain user's permanent access token by exchanging it with access code received during the user authentication (user login).

##### Note:

You can read more about how to obtain a permanent token on [Obtain an Access Token](https://dapi-api.readme.io/docs/get-an-access-token).

##### Method Description

```python
def exchangeToken(access_code, connection_id) -> dict
```

##### Input Parameters

| Parameter | Type | Description |
|---|---|---|
| **access_code** <br> _REQUIRED_ | `str` | Unique code for a user’s successful login to **Connect**. Returned in the response of **UserLogin**. |
| **connection_id** <br> _REQUIRED_ | `str` | The `connectionID` from a user’s successful log in to **Connect**. |

##### Response

In addition to the fields described in the BaseResponse, it has the following fields, which will only be returned if the status is `done`:

| Parameter | Type | Description |
|---|---|---|
| **accessToken** | `str` | A unique permanent token linked to the user. |

---

#### data.getIdentity

Method is used to retrieve personal details about the user.

##### Method Description

```python
def getIdentity(access_token, user_secret, user_inputs=[], operation_id="") -> dict
```

##### Input Parameters

| Parameter | Type | Description |
|---|---|---|
| **access_token** <br> _REQUIRED_ | `str` | Access Token obtained using the `exchangeToken` method. |
| **user_secret** <br> _REQUIRED_ | `str` | The `userSecret` from a user’s successful log in to **Connect**. |
| **operation_id** <br> _OPTIONAL_ | `str` | The `operationID` from a previous call's response. <br> Required only when resuming a previous call that responded with `user_input_required` status, to provided user inputs. |
| **user_inputs** <br> _OPTIONAL_ | `[dict]` | Array of `UserInput` objects, that are needed to complete this operation. <br> Required only if a previous call responded with `user_input_required` status. <br><br> You can read more about user inputs specification on [Specify User Input](https://dapi-api.readme.io/docs/specify-user-input) |

###### UserInput Object

| Parameter | Type | Description |
|---|---|---|
| id | `str` | Type of input required. <br><br> You can read more about user input types on [User Input Types](https://dapi-api.readme.io/docs/user-input-types). |
| index | `int` | Is used in case more than one user input is requested. <br> Will always be 0 If only one input is requested. |
| answer | `str` | User input that must be submitted. |

##### Response

In addition to the fields described in the BaseResponse, it has the following fields, which will only be returned if the status is `done`:

| Parameter | Type | Description |
|---|---|---|
| identity | `dict` | An object containing the identity data of the user. <br><br> For the exact schema of the `identity` object, see [Identity schema](https://dapi-api.readme.io/docs/get-identity#response). |

---

#### data.getAccounts

Method is used to retrieve list of all the bank accounts registered on the user. The list will contain all types of bank accounts.

##### Method Description

```python
def getAccounts(access_token, user_secret, user_inputs=[], operation_id="") -> dict
```

##### Input Parameters

| Parameter | Type | Description |
|---|---|---|
| **access_token** <br> _REQUIRED_ | `str` | Access Token obtained using the `exchangeToken` method. |
| **user_secret** <br> _REQUIRED_ | `str` | The `userSecret` from a user’s successful log in to **Connect**. |
| **operation_id** <br> _OPTIONAL_ | `str` | The `operationID` from a previous call's response. <br> Required only when resuming a previous call that responded with `user_input_required` status, to provided user inputs. |
| **user_inputs** <br> _OPTIONAL_ | `[dict]` | Array of `UserInput` objects, that are needed to complete this operation. <br> Required only if a previous call responded with `user_input_required` status. <br><br> You can read more about user inputs specification on [Specify User Input](https://dapi-api.readme.io/docs/specify-user-input) |

###### UserInput Object

| Parameter | Type | Description |
|---|---|---|
| id | `str` | Type of input required. <br><br> You can read more about user input types on [User Input Types](https://dapi-api.readme.io/docs/user-input-types). |
| index | `int` | Is used in case more than one user input is requested. <br> Will always be 0 If only one input is requested. |
| answer | `str` | User input that must be submitted. |

##### Response

In addition to the fields described in the BaseResponse, it has the following fields, which will only be returned if the status is `done`:

| Parameter | Type | Description |
|---|---|---|
| accounts | `[dict]` | An array containing the accounts data of the user. <br><br> For the exact schema of the `accounts` array, see [Account schema](https://dapi-api.readme.io/docs/get-accounts#account-schema). |

---

#### data.getBalance

Method is used to retrieve balance on specific bank account of the user.

##### Method Description

```python
def getBalance(access_token, user_secret, account_id, user_inputs=[], operation_id="") -> dict
```

##### Input Parameters

| Parameter | Type | Description |
|---|---|---|
| **account_id** <br> _REQUIRED_ | `str` | The bank account ID which its balance is requested. <br> Retrieved from one of the accounts returned from the `GetAccounts` method. |
| **access_token** <br> _REQUIRED_ | `str` | Access Token obtained using the `exchangeToken` method. |
| **user_secret** <br> _REQUIRED_ | `str` | The `userSecret` from a user’s successful log in to **Connect**. |
| **operation_id** <br> _OPTIONAL_ | `str` | The `operationID` from a previous call's response. <br> Required only when resuming a previous call that responded with `user_input_required` status, to provided user inputs. |
| **user_inputs** <br> _OPTIONAL_ | `[dict]` | Array of `UserInput` objects, that are needed to complete this operation. <br> Required only if a previous call responded with `user_input_required` status. <br><br> You can read more about user inputs specification on [Specify User Input](https://dapi-api.readme.io/docs/specify-user-input) |

###### UserInput Object

| Parameter | Type | Description |
|---|---|---|
| id | `str` | Type of input required. <br><br> You can read more about user input types on [User Input Types](https://dapi-api.readme.io/docs/user-input-types). |
| index | `int` | Is used in case more than one user input is requested. <br> Will always be 0 If only one input is requested. |
| answer | `str` | User input that must be submitted. |

##### Response

In addition to the fields described in the BaseResponse, it has the following fields, which will only be valid if the status is `done`:

| Parameter | Type | Description |
|---|---|---|
| balance | `dict` | An object containing the account's balance information. <br><br> For the exact schema of the `balance` object, see [Balance schema](https://dapi-api.readme.io/docs/get-balance#account-schema). |

---

#### data.getTransactions

Method is used to retrieve transactions that user has performed over a specific period of time from their bank account. The transaction list is unfiltered, meaning the response will contain all the transactions performed by the user (not just the transactions performed using your app).

Date range of the transactions that can be retrieved varies for each bank. The range supported by the users bank is shown in the response parameter `transactionRange` of Get Accounts Metadata endpoint.

##### Method Description

```python
def getTransactions(access_token, user_secret, account_id, from_date, to_date, user_inputs=[], operation_id="") -> dict
```

##### Input Parameters

| Parameter | Type | Description |
|---|---|---|
| **account_id** <br> _REQUIRED_ | `str` | The bank account ID which its transactions are requested. <br> Retrieved from one of the accounts returned from the `getAccounts` method. |
| **from_date** <br> _REQUIRED_ | `str` | The start date of the transactions wanted. <br> It should be in this format `YYYY-MM-DD`. |
| **to_date** <br> _REQUIRED_ | `str` | The end date of the transactions wanted. <br> It should be in this format `YYYY-MM-DD`. |
| **access_token** <br> _REQUIRED_ | `str` | Access Token obtained using the `exchangeToken` method. |
| **user_secret** <br> _REQUIRED_ | `str` | The `userSecret` from a user’s successful log in to **Connect**. |
| **operation_id** <br> _OPTIONAL_ | `str` | The `operationID` from a previous call's response. <br> Required only when resuming a previous call that responded with `user_input_required` status, to provided user inputs. |
| **user_inputs** <br> _OPTIONAL_ | `[dict]` | Array of `UserInput` objects, that are needed to complete this operation. <br> Required only if a previous call responded with `user_input_required` status. <br><br> You can read more about user inputs specification on [Specify User Input](https://dapi-api.readme.io/docs/specify-user-input) |

###### UserInput Object

| Parameter | Type | Description |
|---|---|---|
| id | `str` | Type of input required. <br><br> You can read more about user input types on [User Input Types](https://dapi-api.readme.io/docs/user-input-types). |
| index | `int` | Is used in case more than one user input is requested. <br> Will always be 0 If only one input is requested. |
| answer | `str` | User input that must be submitted. |

##### Response

In addition to the fields described in the BaseResponse, it has the following fields, which will only be valid if the status is `done`:

| Parameter | Type | Description |
|---|---|---|
| transactions | `[dict]` | Array containing the transactional data for the specified account within the specified period. <br><br> For the exact schema of the `transactions` array, see [Transaction schema](https://dapi-api.readme.io/docs/get-transactions#transaction-schema). |

---

#### payment.getBeneficiaries

Method is used to retrieve list of all the beneficiaries already added for a user within a financial institution.

##### Method Description

```python
def getBeneficiaries(access_token, user_secret, user_inputs=[], operation_id="") -> dict
```

##### Input Parameters

| Parameter | Type | Description |
|---|---|---|
| **access_token** <br> _REQUIRED_ | `str` | Access Token obtained using the `exchangeToken` method. |
| **user_secret** <br> _REQUIRED_ | `str` | The `userSecret` from a user’s successful log in to **Connect**. |
| **operation_id** <br> _OPTIONAL_ | `str` | The `operationID` from a previous call's response. <br> Required only when resuming a previous call that responded with `user_input_required` status, to provided user inputs. |
| **user_inputs** <br> _OPTIONAL_ | `[dict]` | Array of `UserInput` objects, that are needed to complete this operation. <br> Required only if a previous call responded with `user_input_required` status. <br><br> You can read more about user inputs specification on [Specify User Input](https://dapi-api.readme.io/docs/specify-user-input) |

###### UserInput Object

| Parameter | Type | Description |
|---|---|---|
| id | `str` | Type of input required. <br><br> You can read more about user input types on [User Input Types](https://dapi-api.readme.io/docs/user-input-types). |
| index | `int` | Is used in case more than one user input is requested. <br> Will always be 0 If only one input is requested. |
| answer | `str` | User input that must be submitted. |

##### Response

In addition to the fields described in the BaseResponse, it has the following fields, which will only be returned if the status is `done`:

| Parameter | Type | Description |
|---|---|---|
| beneficiaries | `[dict]` | An array containing the beneficiary information. <br><br> For the exact schema of the `beneficiaries` array, see [Beneficiary schema](https://dapi-api.readme.io/docs/get-beneficiaries#beneficiaries-schema). |

---

#### payment.createBeneficiary

Method is used to retrieve list of all the beneficiaries already added for a user within a financial institution.

##### Method Description

```python
def createBeneficiary(access_token, user_secret, beneficiary_data, user_inputs=[], operation_id="") -> dict
```

##### Input Parameters

| Parameter | Type | Description |
|---|---|---|
| **beneficiary_data** <br> _REQUIRED_ | `dict` | An object that contains info about the beneficiary that should be added. |
| **access_token** <br> _REQUIRED_ | `str` | Access Token obtained using the `exchangeToken` method. |
| **user_secret** <br> _REQUIRED_ | `str` | The `userSecret` from a user’s successful log in to **Connect**. |
| **operation_id** <br> _OPTIONAL_ | `str` | The `operationID` from a previous call's response. <br> Required only when resuming a previous call that responded with `user_input_required` status, to provided user inputs. |
| **user_inputs** <br> _OPTIONAL_ | `[dict]` | Array of `UserInput` objects, that are needed to complete this operation. <br> Required only if a previous call responded with `user_input_required` status. <br><br> You can read more about user inputs specification on [Specify User Input](https://dapi-api.readme.io/docs/specify-user-input) |

###### UserInput Object

| Parameter | Type | Description |
|---|---|---|
| id | `str` | Type of input required. <br><br> You can read more about user input types on [User Input Types](https://dapi-api.readme.io/docs/user-input-types). |
| index | `int` | Is used in case more than one user input is requested. <br> Will always be 0 If only one input is requested. |
| answer | `str` | User input that must be submitted. |

###### beneficiary_data Object

| Parameter | Type | Description |
|---|---|---|
| **name** <br> _REQUIRED_ | `str` | Name of the beneficiary. |
| **accountNumber** <br> _REQUIRED_ | `str` | Account number of the beneficiary. |
| **iban** <br> _REQUIRED_ | `str` | Beneficiary's IBAN number. |
| **swiftCode** <br> _REQUIRED_ | `str` | Beneficiary's financial institution's SWIFT code. |
| **type** <br> _REQUIRED_ | `str` | Type of beneficiary. <br> For further explanation see [Beneficiary Types](https://dapi-api.readme.io/docs/beneficiary-types). |
| **address** <br> _REQUIRED_ | `dict` | An object containing the address information of the beneficiary. |
| **country** <br> _REQUIRED_ | `str` | Name of the country in all uppercase letters. |
| **branchAddress** <br> _REQUIRED_ | `str` | Address of the financial institution’s specific branch. |
| **branchName** <br> _REQUIRED_ | `str` | Name of the financial institution’s specific branch. |
| **phoneNumber** <br> _OPTIONAL_ | `str` | Beneficiary's phone number. |
| **routingNumber** <br> _OPTIONAL_ | `str` | Beneficiary's Routing number, needed only for US banks accounts. |

###### address Object

| Parameter | Type | Description |
|---|---|---|
| **line1** <br> _REQUIRED_ | `str` | Street name and number. Note: value should not contain any commas or special characters. |
| **line2** <br> _REQUIRED_ | `str` | City name. Note: value should not contain any commas or special characters. |
| **line3** <br> _REQUIRED_ | `str` | Country name. Note: value should not contain any commas or special characters. |

##### Response

Method returns only the fields defined in the BaseResponse.

---

#### payment.createTransfer

Method is used to initiate a new payment from one account to another account.

##### Important

We suggest you use `transferAutoflow` method instead to initiate a payment. `transferAutoflow` abstracts all the validations and processing logic, required to initiate a transaction using `createTransfer` method.

You can read about `transferAutoflow` further in the document.

##### Method Description

```python
def createTransfer(access_token, user_secret, transfer_data, user_inputs=[], operation_id="") -> dict
```

##### Input Parameters

| Parameter | Type | Description |
|---|---|---|
| **transfer_data** <br> _REQUIRED_ | `dict` | An object that contains info about the transfer that should be initiated. |
| **access_token** <br> _REQUIRED_ | `str` | Access Token obtained using the `exchangeToken` method. |
| **user_secret** <br> _REQUIRED_ | `str` | The `userSecret` from a user’s successful log in to **Connect**. |
| **operation_id** <br> _OPTIONAL_ | `str` | The `operationID` from a previous call's response. <br> Required only when resuming a previous call that responded with `user_input_required` status, to provided user inputs. |
| **user_inputs** <br> _OPTIONAL_ | `[dict]` | Array of `UserInput` objects, that are needed to complete this operation. <br> Required only if a previous call responded with `user_input_required` status. <br><br> You can read more about user inputs specification on [Specify User Input](https://dapi-api.readme.io/docs/specify-user-input) |

###### UserInput Object

| Parameter | Type | Description |
|---|---|---|
| id | `str` | Type of input required. <br><br> You can read more about user input types on [User Input Types](https://dapi-api.readme.io/docs/user-input-types). |
| index | `int` | Is used in case more than one user input is requested. <br> Will always be 0 If only one input is requested. |
| answer | `str` | User input that must be submitted. |

###### transfer_data Object

| Parameter | Type | Description |
|---|---|---|
| **senderID** <br> _REQUIRED_ | `str` | The id of the account which the money should be sent from. <br> Retrieved from one of the accounts array returned from the getAccounts method. |
| **amount** <br> _REQUIRED_ | `float` | The amount of money which should be sent. |
| **receiverID** <br> _OPTIONAL_ | `str` | The id of the beneficiary which the money should be sent to. <br> Retrieved from one of the beneficiaries array returned from the getBeneficiaries method. <br> Needed only when creating a transfer from a bank that requires the receiver to be already registered as a beneficiary to perform a transaction. |
| **name** <br> _OPTIONAL_ | `str` | The name of receiver. <br> Needed only when creating a transfer from a bank that handles the creation of beneficiaries on its own, internally, and doesn't require the receiver to be already registered as a beneficiary to perform a transaction. |
| **accountNumber** <br> _OPTIONAL_ | `str` | The Account Number of the receiver's account. <br> Needed only when creating a transfer from a bank that handles the creation of beneficiaries on its own, internally, and doesn't require the receiver to be already registered as a beneficiary to perform a transaction. |
| **iban** <br> _OPTIONAL_ | `str` | The IBAN of the receiver's account. <br> Needed only when creating a transfer from a bank that handles the creation of beneficiaries on its own, internally, and doesn't require the receiver to be already registered as a beneficiary to perform a transaction. |

##### Response

In addition to the fields described in the BaseResponse, it has the following fields, which will only be returned if the status is `done`:

| Parameter | Type | Description |
|---|---|---|
| reference | `str` | Transaction reference string returned by the bank. |

---

#### payment.transferAutoflow

Method is used to initiate a new payment from one account to another account, without having to care nor handle any special cases or scenarios.

##### Method Description

```python
def transferAutoflow(access_token, user_secret, transfer_autoflow_data, user_inputs=[], operation_id="") -> dict
```

##### Input Parameters

| Parameter | Type | Description |
|---|---|---|
| **transfer_autoflow_data** <br> _REQUIRED_ | `dict` | An object that contains info about the transfer that should be initiated, and any other details that's used to automate the operation. |
| **access_token** <br> _REQUIRED_ | `str` | Access Token obtained using the `exchangeToken` method. |
| **user_secret** <br> _REQUIRED_ | `str` | The `userSecret` from a user’s successful log in to **Connect**. |
| **operation_id** <br> _OPTIONAL_ | `str` | The `operationID` from a previous call's response. <br> Required only when resuming a previous call that responded with `user_input_required` status, to provided user inputs. |
| **user_inputs** <br> _OPTIONAL_ | `[dict]` | Array of `UserInput` objects, that are needed to complete this operation. <br> Required only if a previous call responded with `user_input_required` status. <br><br> You can read more about user inputs specification on [Specify User Input](https://dapi-api.readme.io/docs/specify-user-input) |

###### UserInput Object

| Parameter | Type | Description |
|---|---|---|
| id | `str` | Type of input required. <br><br> You can read more about user input types on [User Input Types](https://dapi-api.readme.io/docs/user-input-types). |
| index | `int` | Is used in case more than one user input is requested. <br> Will always be 0 If only one input is requested. |
| answer | `str` | User input that must be submitted. |

###### transfer_autoflow_data Object

| Parameter | Type | Description |
|---|---|---|
| **senderID** <br> _REQUIRED_ | `str` | The id of the account which the money should be sent from. <br> Retrieved from one of the accounts array returned from the getAccounts method. |
| **amount** <br> _REQUIRED_ | `float` | The amount of money which should be sent. |
| **beneficiary** <br> _REQUIRED_ | `dict` | An object that holds the info about the beneficiary which the money should be sent to. |
| **bankID** <br> _REQUIRED_ | `str` | The bankID of the user which is initiating this transfer. |

###### beneficiary Object

| Parameter | Type | Description |
|---|---|---|
| **name** <br> _REQUIRED_ | `str` | Name of the beneficiary. |
| **accountNumber** <br> _REQUIRED_ | `str` | Account number of the beneficiary. |
| **iban** <br> _REQUIRED_ | `str` | Beneficiary's IBAN number. |
| **swiftCode** <br> _REQUIRED_ | `str` | Beneficiary's financial institution's SWIFT code. |
| **address** <br> _REQUIRED_ | `dict` | An object containing the address information of the beneficiary. |
| **country** <br> _REQUIRED_ | `str` | Name of the country in all uppercase letters. |
| **branchAddress** <br> _REQUIRED_ | `str` | Address of the financial institution’s specific branch. |
| **branchName** <br> _REQUIRED_ | `str` | Name of the financial institution’s specific branch. |
| **phoneNumber** <br> _OPTIONAL_ | `str` | Beneficiary's phone number. |
| **routingNumber** <br> _OPTIONAL_ | `str` | Beneficiary's Routing number, needed only for US banks accounts. |

###### address Object

| Parameter | Type | Description |
|---|---|---|
| **line1** <br> _REQUIRED_ | `str` | Street name and number. Note: value should not contain any commas or special characters. |
| **line2** <br> _REQUIRED_ | `str` | City name. Note: value should not contain any commas or special characters. |
| **line3** <br> _REQUIRED_ | `str` | Country name. Note: value should not contain any commas or special characters. |

##### Response

In addition to the fields described in the BaseResponse, it has the following fields, which will only be returned if the status is `done`:

| Parameter | Type | Description |
|---|---|---|
| reference | `str` | Transaction reference string returned by the bank. |

---
