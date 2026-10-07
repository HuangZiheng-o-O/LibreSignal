# Working Hours：Level 1 → 4

仓库原有 `level1.md`、`level2.md`、`level3.md`；**没有 `level4.md`**。`simulation.py` 中的 Level 4 双倍工资是额外扩展，不能把它当作此仓库提供的正式第四层题面。

| 层级 | 本层新增命令 | 先保存什么状态 | 对旧代码做什么 |
| --- | --- | --- | --- |
| **Level 1** | `ADD_WORKER`、`REGISTER`、`GET` | 员工、当前入场时间、已完成工作时长 | `REGISTER` 在入场/离场间切换；未离场的一段不计入 `GET`。 |
| **Level 2** | `TOP_N_WORKERS` | 当前职位下的已完成时长 `pos_time` | 只选当前职位相同的员工；按时长降序、员工 ID 升序排序。 |
| **Level 3** | `PROMOTE`、`CALC_SALARY` | 待生效晋升 `pending`、每段工作的起止时间及当时薪资 `sessions` | 晋升到达门槛时间后，须等下一次入场才生效；薪资按历史工作段与查询区间的交集计算。 |
| **Level 4（扩展）** | `SET_DOUBLE_PAID`（实现也接受 `DOUBLE_PAY`） | 合并后的双倍工资时间段 `double_paid` | 计算薪资时增加落在双倍区间内的那部分工资；重叠区间只加倍一次。 |

最终版的 Level 1 员工记录里已有 `pending`、`sessions` 等后续状态。独立练习时先完成入场/离场与累计时长，到 Level 3 再保存每段工作的历史薪资。

此目录目前没有独立测试文件；Level 1–3 可以对照原题面的例子。Level 4 请当作补充练习，不要与原仓库题面混同。
