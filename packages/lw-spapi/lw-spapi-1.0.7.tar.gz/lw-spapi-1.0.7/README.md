# SPAPI

## Amazon Selling-Partner API

A wrapper to access **Amazon's Selling Partner API** with an easy-to-use interface.

### Installation
```
python setup.py install
```

---
### Usage

``` shell script
export SPAPI_REDIS_URL='redis://[[username]:[password]]@localhost:6379/0'
```

```
from spapi.base.client import AmazonSpApi

# getReports API
def get_reports(self, next_token=None):
    url = 'https://sellingpartnerapi-na.amazon.com/reports/2021-06-30/reports'
    kwargs = {
        'headers': {
            'User-Agent': 'Mancang/V0.1 (Language=Python/3.7.1; Platform=Docker)',
            'Content-Type': 'application/json'
        },
        'params': {
            'reportTypes': 'GET_FBA_MYI_ALL_INVENTORY_DATA',
            'createdSince': '2021-07-01T00:00:00Z',
        },
        'region': 'us-east-1',
        # 'proxies': ['http://localhost:7890']
    }

    if next_token:
        kwargs['params'] = {'nextToken': next_token}

    AmazonSpApi(credentials=self.credentials).request('GET', url, **kwargs)
```
---

### Documentation

Documentation is available [here]()
