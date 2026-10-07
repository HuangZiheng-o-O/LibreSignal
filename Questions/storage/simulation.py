"""Cloud Storage 四层题的完整实现；命令分支按 Level 1 → 4 排列。

Level 1：文件增、查、删。Level 2：前缀筛选和排行榜。
Level 3：用户、所有权、容量与合并。Level 4：备份和恢复。
下面的 files 元组包含 owner，且早期操作会维护容量，这是 Level 3 升级后
补回旧代码的逻辑；独立做 Level 1 时先用 文件名 → 大小 即可。
"""


def solution(queries):
    ADMIN = "admin"

    files = {}      # Level 1；Level 3 扩展为 文件名 -> (大小, 所有者)
    remain = {}     # Level 3：普通用户 -> 剩余容量
    backups = {}    # Level 4：用户 -> {文件名: 大小}

    # Level 3 辅助逻辑：确认用户存在，并维护所有权与容量。
    def user_exists(user):
        return user == ADMIN or user in remain

    def add_file(owner, name, size):
        # 全局文件名唯一；admin 容量无限
        if name in files or not user_exists(owner):
            return False
        if owner != ADMIN:
            if remain[owner] < size:
                return False
            remain[owner] -= size
        files[name] = (size, owner)
        return True

    # Level 1 删除文件；返还用户容量是 Level 3 才补入的行为。
    def delete_file(name):
        # 删除普通用户文件时返还容量
        item = files.pop(name, None)
        if item is None:
            return None
        size, owner = item
        if owner != ADMIN:
            remain[owner] += size
        return size

    ans = []

    for q in queries:
        op = q[0]

        # Level 1：文件增、查、删。
        if op == "ADD_FILE":
            ans.append("true" if add_file(ADMIN, q[1], int(q[2])) else "false")

        elif op == "GET_FILE_SIZE":
            item = files.get(q[1])
            ans.append(str(item[0]) if item else "")

        elif op == "DELETE_FILE":
            size = delete_file(q[1])
            ans.append("" if size is None else str(size))

        # Level 2：按前缀找文件，先按大小降序，再按名字升序。
        elif op == "GET_N_LARGEST":
            prefix = q[1]
            candidates = [
                (name, size)
                for name, (size, _) in files.items()
                if name.startswith(prefix)
            ]
            if not candidates:
                ans.append("")
                continue

            n = int(q[2])
            candidates.sort(key=lambda x: (-x[1], x[0]))
            ans.append(", ".join(
                f"{name}({size})" for name, size in candidates[:n]
            ))

        # Level 3：用户、容量、文件所有权和用户合并。
        elif op == "ADD_USER":
            user, capacity = q[1], int(q[2])
            if user_exists(user):
                ans.append("false")
            else:
                remain[user] = capacity
                ans.append("true")

        elif op == "ADD_FILE_BY":
            user, name, size = q[1], q[2], int(q[3])
            # admin 添加文件按题意使用 ADD_FILE
            if user not in remain or not add_file(user, name, size):
                ans.append("")
            else:
                ans.append(str(remain[user]))

        elif op == "MERGE_USER":
            u1, u2 = q[1], q[2]
            if u1 == u2 or u1 not in remain or u2 not in remain:
                ans.append("")
                continue

            # 转移所有权；两人的剩余容量直接相加
            for name, (size, owner) in files.items():
                if owner == u2:
                    files[name] = (size, u1)

            remain[u1] += remain.pop(u2)
            backups.pop(u2, None)  # Level 4 补入：被合并用户的备份同时删除
            ans.append(str(remain[u1]))

        # Level 4：保存用户快照，并从最近的快照恢复。
        elif op == "BACKUP_USER":
            user = q[1]
            if not user_exists(user):
                ans.append("")
                continue

            backups[user] = {
                name: size
                for name, (size, owner) in files.items()
                if owner == user
            }
            ans.append(str(len(backups[user])))

        elif op == "RESTORE_USER":
            user = q[1]
            if not user_exists(user):
                ans.append("")
                continue

            # 先清空该用户当前文件
            for name in [
                name for name, (_, owner) in files.items()
                if owner == user
            ]:
                delete_file(name)

            # 再恢复最近备份；同名文件被别人占用时跳过
            restored = 0
            for name, size in backups.get(user, {}).items():
                if name in files:
                    continue
                if add_file(user, name, size):
                    restored += 1

            ans.append(str(restored))

    return ans
