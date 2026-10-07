# 四套题从哪里开始

每个子文件夹的 `LEVEL_GUIDE.md` 都列出 Level 1 → 4 的新增操作、需要保存的状态，以及对应代码位置。按顺序只读当前层的题面和测试，做完一层再进入下一层。

| 题目 | 逐层指南 | 实现入口 |
| --- | --- | --- |
| Banking | [bank_system/LEVEL_GUIDE.md](bank_system/LEVEL_GUIDE.md) | `bank_system/simulation.py` |
| In-Memory Database | [in_memory_database/LEVEL_GUIDE.md](in_memory_database/LEVEL_GUIDE.md) | `in_memory_database/simulation.py` |
| Cloud Storage | [storage/LEVEL_GUIDE.md](storage/LEVEL_GUIDE.md) | `storage/simulation.py` 是已有的完整实现；可另建练习副本。 |
| Working Hours | [workers/LEVEL_GUIDE.md](workers/LEVEL_GUIDE.md) | `workers/simulation.py` 是已有的完整实现；可另建练习副本。 |

`simulation_solution.py`（Bank、Database）和已有的 `storage/simulation.py`、`workers/simulation.py` 展示的是完成全部层级后的代码。早期层级的方法里也可能出现后续新增的调用；指南会注明何时把它们补回去。
