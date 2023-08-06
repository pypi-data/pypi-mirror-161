# snowtrace-python


![GitHub](https://img.shields.io/github/license/EmperorMew/snowtrace-python)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-385/)



A minimal, yet complete, Python API for [snowtrace.io](https://snowtrace.io/). 

All standard and pro endpoints are provided. Kovan, Rinkeby and Ropsten testnets are also supported.

Available on [PyPI](https://pypi.org/project/snowtrace-python/). Powered by [snowtrace.io APIs](https://snowtrace.io/apis#misc).


___


## Endpoints

The following endpoints are provided:

<details><summary>Accounts <a href="https://snowtrace.io/apis#accounts">(source)</a></summary>
<p>

* `get_avax_balance`
* `get_avax_balance_multiple`
* `get_normal_txs_by_address`
* `get_normal_txs_by_address_paginated`
* `get_internal_txs_by_address`
* `get_internal_txs_by_address_paginated`
* `get_internal_txs_by_txhash`
* `get_internal_txs_by_block_range_paginated`
* `get_erc20_token_transfer_events_by_address`
* `get_erc20_token_transfer_events_by_contract_address_paginated`
* `get_erc20_token_transfer_events_by_address_and_contract_paginated`
* `get_erc721_token_transfer_events_by_address`
* `get_erc721_token_transfer_events_by_contract_address_paginated`
* `get_erc721_token_transfer_events_by_address_and_contract_paginated`
* `get_mined_blocks_by_address`
* `get_mined_blocks_by_address_paginated`

</details>

<details><summary>Contracts <a href="https://snowtrace.io/apis#contracts">(source)</a></summary>
<p>
  
* `get_contract_abi`
* `get_contract_source_code`

</details>

</details>

<details><summary>Transactions <a href="https://snowtrace.io/apis#transactions">(source)</a></summary>
<p>
  
* `get_contract_execution_status`
* `get_tx_receipt_status`

</details>

<details><summary>Blocks <a href="https://snowtrace.io/apis#blocks">(source)</a></summary>
<p>
  
* `get_block_reward_by_block_number`
* `get_est_block_countdown_time_by_block_number`
* `get_block_number_by_timestamp`

</details>

<details><summary>GETH/Parity Proxy <a href="https://snowtrace.io/apis#proxy">(source)</a></summary>
<p>

* `get_proxy_block_number`
* `get_proxy_block_by_number`
* `get_proxy_uncle_by_block_number_and_index`
* `get_proxy_block_transaction_count_by_number`
* `get_proxy_transaction_by_hash`
* `get_proxy_transaction_by_block_number_and_index`
* `get_proxy_transaction_count`
* `get_proxy_transaction_receipt`
* `get_proxy_call`
* `get_proxy_code_at`
* `get_proxy_storage_position_at`
* `get_proxy_gas_price`
* `get_proxy_est_gas`

</details>

<details><summary>Tokens <a href="https://snowtrace.io/apis#tokens">(source)</a></summary>
<p>
  
* `get_total_supply_by_contract_address`
* `get_acc_balance_by_token_and_contract_address`

</details>

<details><summary>Gas Tracker <a href="https://snowtrace.io/apis#gastracker">(source)</a></summary>
<p>
  
* `get_est_confirmation_time`
* `get_gas_oracle`

</details>

<details><summary>Stats <a href="https://snowtrace.io/apis#stats">(source)</a></summary>
<p>
  
* `get_total_avax_supply`
* `get_avax_last_price`
* `get_avax_nodes_size`

</details>

<details><summary>Pro (PRO API key needed) <a href="https://snowtrace.io/apis#APIpro">(source)</a></summary>
<p>

* `get_hist_avax_balance_for_address_by_block_no`
* `get_daily_average_block_size`
* `get_daily_block_count_and_rewards`
* `get_daily_block_rewards`
* `get_daily_average_block_time`
* `get_daily_uncle_block_count_and_rewards`
* `get_hist_erc20_token_total_supply_by_contract_address_and_block_no`
* `get_hist_erc20_token_account_balance_for_token_contract_address_by_block_no`
* `get_token_info_by_contract_address`
* `get_daily_average_gas_limit`
* `get_avax_daily_total_gas_used`
* `get_avax_daily_average_gas_price`
* `get_avax_daily_network_tx_fee`
* `get_daily_new_address_count`
* `get_daily_network_utilization`
* `get_daily_average_network_hash_rate`
* `get_daily_tx_count`
* `get_daily_average_network_difficulty`
* `get_avax_hist_daily_market_cap`
* `get_avax_hist_price`

</details>

*If you think that a newly-added method is missing, kindly open an [issue](https://github.com/EmperorMew/snowtrace-python/issues) as a feature request and I will do my best to add it.*

## Installation

Before proceeding, you should register an account on [snowtrace.io](https://snowtrace.io/) and [generate a personal API key](https://snowtrace.io/myapikey) to use. 

If you wish to have access to the PRO endpoints, you should obtain elevated privileges via snowtrace's subscription service.

Install from source:

``` bash
pip install git+https://github.com/EmperorMew/snowtrace-python.git
```

Alternatively, install from [PyPI](https://pypi.org/project/snowtrace-python/):

```bash
pip install snowtrace-python
```

## Unit tests

In `bash`, test that everything looks OK on your end using your `YOUR_API_KEY` (without quotation marks) before proceeding:

``` bash
bash run_tests.sh YOUR_API_KEY
````

This will regenerate the logs under `logs/` with the most recent results and the timestamp of the execution.

The tests also include the PRO endpoints so if your key is not PRO, the correspondings tests are expected to fail.

## Usage

In `python`, create a client with your personal [snowtrace.io](https://snowtrace.io/) API key:

``` python
from snowtrace import Snowtrace
avax = Snowtrace(YOUR_API_KEY) # key in quotation marks
```

Then you can call all available methods, e.g.:

``` python
avax.get_avax_balance(address="0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121a")

> '40891631566070000000000'
```
You can also choose one of the other testnets:
``` python
avax = Snowtrace(YOUR_API_KEY, net="ropsten") # net name is case-insensitive, default is main
```

## Examples

Examples (arguments and results) for all methods may be found as JSON files [here](https://github.com/EmperorMew/snowtrace-python/tree/master/logs).  For example, if you want to use the method `get_block_number_by_timestamp`, you can find the supported arguments and the format of its output in its respective [JSON file](logs/standard/get_block_number_by_timestamp.json):

``` json
{
  "method": "get_block_number_by_timestamp",
  "module": "blocks",
  "kwargs": {
    "timestamp": "1578638524",
    "closest": "before"
  },
  "log_timestamp": "2020-10-28-12:34:44",
  "res": "9251482"
}
```

where `kwargs` refer to the required named arguments and `res` refers to the expected result if you were to run:

``` python
avax.get_block_number_by_timestamp(timestamp="1578638524", closest="before")

> '9251482'
```

**Disclaimer**: Those examples blindly use the arguments originally showcased [here](https://api.snowtrace.io/apis) and the selected wallets/contracts do not reflect any personal preference. You should refer to the same source for additional information regarding specific argument values.

## Issues

For problems regarding installing or using the package please open an [issue](https://github.com/EmperorMew/snowtrace-python/issues). Kindly avoid disclosing potentially sensitive information such as your API keys or your wallet addresses.

## Cite

Kotsias, P. C., EmperorMew/snowtrace-python. *https://github.com/EmperorMew/snowtrace-python (2020)*. doi:10.5281/zenodo.4306855

or in ```bibtex```:

```bibtex
@misc{Kotsias2020,
  author = {Kotsias, P.C.},
  title = {EmperorMew/snowtrace-python},
  year = {2020},
  publisher = {Zenodo},
  url = {https://github.com/EmperorMew/snowtrace-python},
  doi = {10.5281/zenodo.4306855}
}
```

Feel free to leave a :star: if you found this package useful.

___

 Powered by [snowtrace.io APIs](https://snowtrace.io/apis).
