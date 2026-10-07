"""四级银行题的最终版实现；下方的公开方法按 Level 1 → 4 排列。

建议按这个顺序自己动手，而不是从上到下照抄最终版：
1. Level 1：只需 accounts 和每个账户的 balance；实现开户、存款、转账。
2. Level 2：给账户加 outgoing；成功转账时累加转出金额，再实现排行榜。
3. Level 3：加支付 ID、支付状态和返现队列；实现 pay、get_payment_status。
   这时才把 _process_cashbacks 放到所有公开方法开头，保证到期返现先执行。
4. Level 4：加余额 history 与合并指针 parent；实现 merge_accounts、get_balance。
   这时才在余额变化处补 _record，并让返现与支付查询沿 parent 找到保留账户。

因此，Level 1 方法里出现的 _process_cashbacks 和 _record 是后来升级时加回去的，
不是做 Level 1 时就需要预先写好的代码。
"""

from bisect import bisect_right
import heapq


DAY = 86_400_000  # Level 3：24 小时，题目中的时间戳单位为毫秒


class _Account:
    """单个账户的状态；parent 用于追踪账户合并后的最终归属。"""

    __slots__ = ("account_id", "created_at", "balance", "outgoing", "history", "parent")

    def __init__(self, account_id: str, created_at: int):
        self.account_id = account_id
        self.created_at = created_at  # Level 4：判断历史查询时账户是否已存在
        self.balance = 0              # Level 1：当前余额
        self.outgoing = 0             # Level 2：累计转出和付款金额
        # (时间戳, 当次操作后的余额)，按时间递增；创建时余额为 0。
        self.history = [(created_at, 0)]  # Level 4：历史余额
        self.parent = self                # Level 4：合并后指向保留账户


class Simulation:
    def __init__(self):
        # Level 1：先只有 accounts；合并后的 ID 在 Level 4 才会删除。
        self.accounts: dict[str, _Account] = {}
        # Level 3：付款状态；Level 4 时保留原账户引用以追踪合并后的归属。
        self.payments: dict[str, tuple[_Account, str]] = {}
        # 最小堆元素：(返现到期时间, 支付序号, 原账户, 返现金额, 支付 ID)。
        # 支付序号打破同一到期时间的平局，避免堆比较 _Account 对象。
        self.cashbacks: list[tuple[int, int, _Account, int, str]] = []  # Level 3
        self.payment_count = 0  # Level 3：生成 payment1、payment2 等 ID

    # Level 1：开户、存款、转账
    def create_account(self, timestamp: int, account_id: str) -> bool:
        # Level 3 升级时补入：处理截至当前时间已到期的返现。
        self._process_cashbacks(timestamp)
        if account_id in self.accounts:
            return False
        self.accounts[account_id] = _Account(account_id, timestamp)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._process_cashbacks(timestamp)
        account = self.accounts.get(account_id)
        if account is None:
            return None
        account.balance += amount
        # Level 4 升级时补入：供 get_balance 查询历史余额。
        self._record(account, timestamp)
        return account.balance

    def transfer(self, timestamp: int, source_account_id: str,
                 target_account_id: str, amount: int) -> int | None:
        """成功时返回转出账户余额；条件不满足时不执行转账。"""
        self._process_cashbacks(timestamp)
        source = self.accounts.get(source_account_id)
        target = self.accounts.get(target_account_id)
        if source is None or target is None or source is target or source.balance < amount:
            return None

        source.balance -= amount
        target.balance += amount
        # Level 2 升级时补入：只统计转出账户的支出。
        source.outgoing += amount
        self._record(source, timestamp)
        self._record(target, timestamp)
        return source.balance

    # Level 2：统计累计支出并排序
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        """按累计支出降序排列；并列时按账户 ID 升序排列。"""
        self._process_cashbacks(timestamp)
        ranked = sorted(self.accounts.values(), key=lambda a: (-a.outgoing, a.account_id))
        return [f"{a.account_id}({a.outgoing})" for a in ranked[:n]]

    # Level 3：支付、定时返现、支付状态
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        """立即扣款，排入 24 小时后的 2% 返现，并返回新支付 ID。"""
        self._process_cashbacks(timestamp)
        account = self.accounts.get(account_id)
        if account is None or account.balance < amount:
            return None

        account.balance -= amount
        account.outgoing += amount
        self._record(account, timestamp)

        self.payment_count += 1
        payment_id = f"payment{self.payment_count}"
        due = timestamp + DAY
        # 整数除法向下取整；即使返现金额为 0，也保留支付状态流转。
        cashback = amount * 2 // 100
        self.payments[payment_id] = (account, "IN_PROGRESS")
        heapq.heappush(self.cashbacks, (due, self.payment_count, account, cashback, payment_id))
        return payment_id

    def get_payment_status(self, timestamp: int, account_id: str,
                           payment: str) -> str | None:
        """只有支付所属的当前有效账户可以查询其状态。"""
        self._process_cashbacks(timestamp)
        account = self.accounts.get(account_id)
        info = self.payments.get(payment)
        if account is None or info is None:
            return None

        owner, status = info
        # 原付款账户已被合并时，_find(owner) 会指向保留账户。
        return status if self._find(owner) is account else None

    # Level 4：账户合并与历史余额
    def merge_accounts(self, timestamp: int, account_id_1: str,
                       account_id_2: str) -> bool:
        """将第二个账户并入第一个；第二个账户 ID 此后不再可用。"""
        self._process_cashbacks(timestamp)
        if account_id_1 == account_id_2:
            return False

        first = self.accounts.get(account_id_1)
        second = self.accounts.get(account_id_2)
        if first is None or second is None:
            return False

        # 合并当前余额和支出；历史轨迹也合并，供后续 get_balance 查询。
        first.balance += second.balance
        first.outgoing += second.outgoing
        first.history = self._merge_history(first.history, second.history)
        # 保留对象引用：待返现和支付记录仍可能指向 second。
        second.parent = first
        del self.accounts[account_id_2]
        return True

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        """查询不晚于 time_at 的最近一次余额；账户不存在时返回 None。"""
        self._process_cashbacks(timestamp)
        account = self.accounts.get(account_id)
        if account is None or time_at < account.created_at:
            return None

        # 二分定位最后一个时间戳 <= time_at 的历史记录。
        i = bisect_right(account.history, (time_at, float("inf"))) - 1
        return account.history[i][1] if i >= 0 else None

    # Level 3 辅助方法：每次公开操作前处理已到期返现。
    def _process_cashbacks(self, timestamp: int) -> None:
        """先结算截至当前操作时间已到期的返现。"""
        while self.cashbacks and self.cashbacks[0][0] <= timestamp:
            due, _, owner, amount, payment_id = heapq.heappop(self.cashbacks)
            # 付款后账户可能被合并；返现应进入最终保留的账户。
            account = self._find(owner)
            account.balance += amount
            # 历史中记录真实的返现到期时间，而不是触发结算的查询时间。
            self._record(account, due)
            self.payments[payment_id] = (owner, "CASHBACK_RECEIVED")

    # Level 4 辅助方法：合并账户并维护可查询的历史。
    def _find(self, account: _Account) -> _Account:
        """沿 parent 找到合并后的有效账户，并压缩查找路径。"""
        if account.parent is not account:
            account.parent = self._find(account.parent)
        return account.parent

    @staticmethod
    def _record(account: _Account, timestamp: int) -> None:
        """记录操作后的余额；同一时间戳发生多次变动时只保留最终值。"""
        if account.history and account.history[-1][0] == timestamp:
            account.history[-1] = (timestamp, account.balance)
        else:
            account.history.append((timestamp, account.balance))

    @staticmethod
    def _merge_history(a: list[tuple[int, int]], b: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """合并两条余额轨迹，得到每个变动时刻的两账户余额之和。"""
        i = j = 0
        # ba、bb 是遍历到当前时刻时，各账户最近一次记录的余额。
        ba = bb = 0
        merged = []
        while i < len(a) or j < len(b):
            ta = a[i][0] if i < len(a) else float("inf")
            tb = b[j][0] if j < len(b) else float("inf")
            t = min(ta, tb)
            if ta == t:
                ba = a[i][1]
                i += 1
            if tb == t:
                bb = b[j][1]
                j += 1
            merged.append((t, ba + bb))
        return merged
