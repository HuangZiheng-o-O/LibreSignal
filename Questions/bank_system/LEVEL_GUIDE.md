# Banking：Level 1 → 4

题面依次是 `level1.md`、`level2.md`、`level3.md`、`level4.md`。从空白的 `simulation.py` 开始写；`simulation_solution.py` 是最终版参考代码，公开方法已按 Level 排列。

| 层级 | 本层新增操作 | 先保存什么状态 | 对旧代码做什么 |
| --- | --- | --- | --- |
| **Level 1** | `create_account`、`deposit`、`transfer` | `accounts`：账户 ID → 当前余额 | 转账前检查两个账户、不能转给自己、余额足够。此时不用实现返现或历史。 |
| **Level 2** | `top_spenders` | 每个账户的累计支出 `outgoing` | 成功转账时累加转出金额；排行按 `(-outgoing, account_id)` 排序。 |
| **Level 3** | `pay`、`get_payment_status` | 支付序号、支付状态、按到期时间排列的返现队列 | 成功支付也计入 `outgoing`；在**每个公开操作前**处理已到期返现。 |
| **Level 4** | `merge_accounts`、`get_balance` | 账户创建时间、余额历史、合并后的账户归属 | 所有余额变动都记录历史；合并余额与支出，让旧账户的待返现和支付归属新账户。 |

最容易看混的一点：最终版 Level 1 方法中调用的 `_process_cashbacks` 是 **Level 3 回填**，`_record` 是 **Level 4 回填**。做 Level 1 时不需要先写它们。

从仓库根目录运行某层测试：

```bash
pytest Questions/bank_system/test_bank_system.py::TestLevel1 -v
```

通过后把 `TestLevel1` 改为 `TestLevel2`、`TestLevel3`、`TestLevel4`。
