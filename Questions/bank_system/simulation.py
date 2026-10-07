"""从 Level 1 开始逐层实现；每层只补当前新增的操作和状态。

方法名按 Level 1 → 4 排列。具体要求见同目录 level1.md 至 level4.md；
做完当前层后再运行对应的 TestLevel1、TestLevel2、TestLevel3、TestLevel4。
"""

class Simulation:

    def __init__(self):
        pass

    # Level 1：开户、存款、转账。起步只需要账户和余额。
    def create_account(self, timestamp: int, account_id: str) -> bool | None:
        pass

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        pass

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        pass

    # Level 2：记录累计支出，按支出降序 / ID 升序排列。
    def top_spenders(self, timestamp: int, n: int) -> list[str] | None:
        pass

    # Level 3：支付、24 小时后返现、支付状态；将到期返现处理补进旧方法。
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        pass

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        pass

    # Level 4：合并账户、保留历史余额；将历史记录补进旧方法。
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool | None:
        pass

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        pass
