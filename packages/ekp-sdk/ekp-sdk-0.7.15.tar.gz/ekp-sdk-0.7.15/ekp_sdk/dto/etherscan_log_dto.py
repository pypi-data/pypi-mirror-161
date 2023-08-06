from typing import List, TypedDict


class EtherscanLogDto(TypedDict, total=False):
    '''
    :example
    {
        "address": "0xe561479bebee0e606c19bb1973fc4761613e3c42",
        "topics": [
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "0x000000000000000000000000730e2065b9daee84c3003c05bf6d2b3a08e55667",
            "0x000000000000000000000000d7d19938eae260d7f0e0a4c36e665ff4cf4b7acc"
        ],
        "data": "0x000000000000000000000000000000000000000000000000076cd96f53f24b0a",
        "blockNumber": "0x4c3326",
        "timeStamp": "0x602e9ef1",
        "gasPrice": "0x2540be400",
        "gasUsed": "0x1b0f2",
        "logIndex": "0xf7",
        "transactionHash": "0x73844fcfc6beab2e973a897c9573f4d79811b12213ce263045a203e0d3cea90e",
        "transactionIndex": "0xb9"
    }
    '''

    address: str
    topics: List[str]
    data: str
    blockNumber: str
    timeStamp: str
    gasPrice: str
    gasUsed: str
    logIndex: str
    transactionHash: str
    transactionIndex: str
