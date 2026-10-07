# Cloud Storage：Level 1 → 4

题面依次是 `level1.md`、`level2.md`、`level3.md`、`level4.md`。`simulation.py` 是已有的完整实现，文件内已按操作标注层级。若要盲练，请先另建副本，避免直接看最终版。

| 层级 | 本层新增命令 | 先保存什么状态 | 对旧代码做什么 |
| --- | --- | --- | --- |
| **Level 1** | `ADD_FILE`、`GET_FILE_SIZE`、`DELETE_FILE` | `files`：文件名 → 大小 | 同名文件不能重复添加；删除返回原大小。 |
| **Level 2** | `GET_N_LARGEST` | 继续使用 `files` | 先按前缀筛选，再按大小降序、文件名字典序升序排序。 |
| **Level 3** | `ADD_USER`、`ADD_FILE_BY`、`MERGE_USER` | 文件所有者、用户剩余容量 `remain` | 添加/删除用户文件时更新容量；合并时转移所有权与剩余容量。`admin` 添加文件不受配额限制。 |
| **Level 4** | `BACKUP_USER`、`RESTORE_USER` | 每个用户独立的文件快照 `backups` | 恢复时先清除该用户当前文件，再恢复未被别人占用的备份文件；合并被删除用户时也删除其备份。 |

最终版 Level 1 的 `add_file`、`delete_file` 同时处理 Level 3 才引入的所有权与容量。独立实现 Level 1 时可以先只保存大小，到 Level 3 再把文件数据扩展为 `(size, owner)`。

此目录目前没有独立测试文件；请以四层题面的例子核对返回值和边界条件。
