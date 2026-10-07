# In-Memory Database：Level 1 → 4

题面依次是 `level1.md`、`level2.md`、`level3.md`、`level4.md`。从空白的 `simulation.py` 开始写；`simulation_solution.py` 的方法已有 Level 标记，供做完后复盘。

| 层级 | 本层新增操作 | 先保存什么状态 | 对旧代码做什么 |
| --- | --- | --- | --- |
| **Level 1** | `set`、`get`、`delete` | `data[key][field] = value` | 删除最后一个字段时可以清理空记录。 |
| **Level 2** | `scan`、`scan_by_prefix` | 继续使用二级字典 | 按字段名字典序输出 `field(value)`；前缀查询先筛选再排序。 |
| **Level 3** | `set_at`、`set_at_with_ttl`、`get_at`、`delete_at`、`scan_at`、`scan_by_prefix_at` | 字段扩展为 `(value, expire_at)` | 所有带时间的读、删、扫描都检查存活；TTL 有效区间为 `[timestamp, timestamp + ttl)`。 |
| **Level 4** | `backup`、`restore` | 备份时间和独立快照 | 备份只收录当时有效的字段，并保存**剩余 TTL**；恢复时用恢复时间重新计算到期时间。 |

最终版从一开始就用 `(value, expire_at)`，这是为了兼容 Level 3。独立练习时，Level 1 可以先只存 `value`，到 Level 3 再重构。

```bash
pytest Questions/in_memory_database/test_in_memory_database.py::TestLevel1 -v
```

通过后依次运行 `TestLevel2`、`TestLevel3`、`TestLevel4`。
