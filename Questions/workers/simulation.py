"""Working Hours 四层练习的完整实现；命令分支按 Level 1 → 4 排列。

原仓库只有 level1.md 至 level3.md。这里的 Level 4 双倍工资是额外扩展，
不是原仓库提供的第四层题面。独立练习时先做打卡与累计时间，再逐层
加入排名、延迟晋升/历史薪资、双倍工资区间。
"""


def solution(queries):
    workers = {}  # Level 1：员工状态；Level 2/3 再扩充字段
    double_paid = []  # Level 4：合并后的全局双倍工资区间 [l, r)
    ans = []

    # Level 4 辅助逻辑：合并区间，保证同一时间最多只按双倍计薪。
    def add_double(l, r):
        """加入双倍工资区间，并合并重叠/相邻区间，避免重复翻倍。"""
        nonlocal double_paid
        merged = []
        for a, b in sorted(double_paid + [(l, r)]):
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b))
            else:
                merged.append((a, b))
        double_paid = merged

    def double_overlap(l, r):
        """返回 [l, r) 中落在双倍工资区间内的总时长。"""
        total = 0
        for a, b in double_paid:
            if b <= l:
                continue
            if a >= r:
                break
            total += min(r, b) - max(l, a)
        return total

    for q in queries:
        op = q[0].upper().replace(" ", "_")

        # Level 1：登记员工、进出办公室、查询已完成的工作时长。
        if op == "ADD_WORKER":
            wid, pos, pay = q[1], q[2], int(q[3])
            if wid in workers:
                ans.append("false")
                continue
            workers[wid] = {
                "pos": pos, "pay": pay,
                "entry": None,          # (进入时间, 当次薪资)
                "pending": None,        # Level 3：(新职位, 新薪资, 生效门槛时间)
                "sessions": [],         # Level 3：已完成工作段 (start, end, pay)
                "total": 0,             # 全部历史已完成时长
                "pos_time": 0,          # Level 2：当前职位下的已完成时长
            }
            ans.append("true")

        elif op == "REGISTER":
            wid, t = q[1], int(q[2])
            if wid not in workers:
                ans.append("invalid_request")
                continue

            w = workers[wid]
            if w["entry"] is None:       # 进入办公室
                # Level 3 补入：晋升到达门槛后，在下一次入场时才生效。
                p = w["pending"]
                if p is not None and t >= p[2]:
                    w["pos"], w["pay"] = p[0], p[1]
                    w["pos_time"] = 0
                    w["pending"] = None
                w["entry"] = (t, w["pay"])
            else:                         # 离开办公室，形成完整工作段
                start, pay = w["entry"]
                duration = t - start
                w["sessions"].append((start, t, pay))
                w["total"] += duration
                w["pos_time"] += duration
                w["entry"] = None
            ans.append("registered")

        elif op == "GET":
            w = workers.get(q[1])
            ans.append("" if w is None else str(w["total"]))

        # Level 2：只排名当前职位相同的员工。
        elif op == "TOP_N_WORKERS":
            n, pos = int(q[1]), q[2]
            rows = [(wid, w["pos_time"]) for wid, w in workers.items()
                    if w["pos"] == pos]
            rows.sort(key=lambda x: (-x[1], x[0]))
            ans.append(", ".join(f"{wid}({t})" for wid, t in rows[:n]))

        # Level 3：登记延迟晋升，并按历史工作段计算薪资。
        elif op == "PROMOTE":
            wid, new_pos = q[1], q[2]
            new_pay, start = int(q[3]), int(q[4])
            w = workers.get(wid)
            if w is None or w["pending"] is not None:
                ans.append("invalid_request")
            else:
                w["pending"] = (new_pos, new_pay, start)
                ans.append("success")

        elif op == "CALC_SALARY":
            wid, left, right = q[1], int(q[2]), int(q[3])
            w = workers.get(wid)
            if w is None:
                ans.append("")
                continue

            salary = 0
            for start, end, pay in w["sessions"]:
                l, r = max(start, left), min(end, right)
                if l < r:
                    duration = r - l
                    # Level 4 补入：双倍区间的交集再额外支付一份工资。
                    salary += (duration + double_overlap(l, r)) * pay
            ans.append(str(salary))

        # Level 4 扩展：全局设置双倍工资区间。
        elif op in ("SET_DOUBLE_PAID", "DOUBLE_PAY"):
            add_double(int(q[1]), int(q[2]))
            ans.append("")

    return ans
