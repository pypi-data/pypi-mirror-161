import datetime as dt

import humanize
import requests

ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"

def getBlockTimestamp(apiKey, blockId):
    action = "eth_getBlockByNumber"
    url = f"{ETHERSCAN_BASE_URL}?module=proxy&action={action}&tag={blockId}&boolean=true&apikey={apiKey}"
    res = requests.get(url)
    block = res.json()
    blockTimestamp = block['result']['timestamp']
    blockTimeDecimal = float(int(blockTimestamp[2:], 16))
    blockDate = dt.datetime.utcfromtimestamp(blockTimeDecimal)

    preciseDelta = humanize.precisedelta(dt.datetime.now() - blockDate, minimum_unit='minutes')

    return f"{preciseDelta} ago"
