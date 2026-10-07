"""四级 In-Memory Database 题的一个实现。

一条记录由 key 标识，里面可以有多个 field。每个 field 保存 (value, expire_at)：
expire_at 为 None 时永不过期，否则从该时间戳起视为已过期。
备份保存的是剩余 TTL，恢复时再按新的时间戳计算过期时间。
"""


class InMemoryDatabase:
    def __init__(self):
        # 二级字典：先用 key 找记录，再用 field 找该字段的值和过期时间。
        self.data = {}
        # 每次备份都保留一份独立快照；同一时间可以有多个备份。
        # snapshot[key][field] = (value, remaining_ttl)。
        self.backups = []

    @staticmethod
    def _alive(item, timestamp):
        """检查字段在指定时刻是否有效；到达 expire_at 时就已过期。"""
        return item is not None and (item[1] is None or int(timestamp) < item[1])

    @staticmethod
    def _format(fields):
        """把 (field, value) 排序并格式化为 field(value) 列表。"""
        return ", ".join(f"{field}({value})" for field, value in sorted(fields))

    # ========== Level 1 ==========
    def set(self, key, field, value):
        """写入字段；不带时间参数的写入没有 TTL。"""
        self.data.setdefault(key, {})[field] = (value, None)
        return ""

    def get(self, key, field):
        item = self.data.get(key, {}).get(field)
        return item[0] if item is not None else ""

    def delete(self, key, field):
        """删除存在的字段；最后一个字段删掉后，一并删除空记录。"""
        record = self.data.get(key)
        if record is None or field not in record:
            return "false"
        del record[field]
        if not record:
            del self.data[key]
        return "true"

    # ========== Level 2 ==========
    def scan(self, key):
        """列出记录的全部字段；由 _format 统一处理排序和输出格式。"""
        record = self.data.get(key, {})
        return self._format((field, item[0]) for field, item in record.items())

    def scan_by_prefix(self, key, prefix):
        """只列出字段名以 prefix 开头的字段。"""
        record = self.data.get(key, {})
        return self._format(
            (field, item[0]) for field, item in record.items()
            if field.startswith(prefix)
        )

    # ========== Level 3 ==========
    def set_at(self, key, field, value, timestamp):
        # 覆盖旧字段时，也覆盖旧的 TTL；因此 expire_at 重新变为 None。
        self.data.setdefault(key, {})[field] = (value, None)
        return ""

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        """字段在 [timestamp, timestamp + ttl) 内有效。"""
        timestamp, ttl = int(timestamp), int(ttl)
        self.data.setdefault(key, {})[field] = (value, timestamp + ttl)
        return ""

    def delete_at(self, key, field, timestamp):
        """只删除此刻仍有效的字段；已过期字段按不存在处理。"""
        record = self.data.get(key)
        item = None if record is None else record.get(field)
        if not self._alive(item, timestamp):
            return "false"
        return self.delete(key, field)

    def get_at(self, key, field, timestamp):
        """读取字段当前值；不存在或已过期时返回空字符串。"""
        item = self.data.get(key, {}).get(field)
        return item[0] if self._alive(item, timestamp) else ""

    def scan_at(self, key, timestamp):
        return self._scan_at(key, "", timestamp)

    def scan_by_prefix_at(self, key, prefix, timestamp):
        return self._scan_at(key, prefix, timestamp)

    def _scan_at(self, key, prefix, timestamp):
        """给两种时间查询共用的筛选逻辑：匹配前缀且尚未过期。"""
        record = self.data.get(key, {})
        return self._format(
            (field, item[0]) for field, item in record.items()
            if field.startswith(prefix) and self._alive(item, timestamp)
        )

    # ========== Level 4 ==========
    def backup(self, timestamp):
        """只保存此刻仍有有效字段的记录，返回这类记录的数量。"""
        timestamp = int(timestamp)
        snapshot = {}

        for key, record in self.data.items():
            saved = {}
            for field, item in record.items():
                if self._alive(item, timestamp):
                    value, expire_at = item
                    # 保存剩余寿命，不保存绝对过期时间。例如 t=10 时还剩 5，
                    # 若在 t=100 恢复，新过期时间应为 105。
                    remaining = None if expire_at is None else expire_at - timestamp
                    saved[field] = (value, remaining)
            if saved:
                snapshot[key] = saved

        self.backups.append((timestamp, snapshot))
        return str(len(snapshot))

    def restore(self, timestamp, timestampToRestore):
        """取目标时间之前最近的备份，并将剩余 TTL 接到恢复时间上。"""
        timestamp, target = int(timestamp), int(timestampToRestore)

        # 备份按调用顺序保存；倒序遇到的第一个合格备份就是最近备份。
        for backup_time, snapshot in reversed(self.backups):
            if backup_time <= target:
                # 重建字典，避免后续写入修改原始备份；永久字段仍用 None。
                self.data = {
                    key: {
                        field: (value, None if remaining is None else timestamp + remaining)
                        for field, (value, remaining) in record.items()
                    }
                    for key, record in snapshot.items()
                }
                return ""

        # 题目保证一定存在可恢复的备份；保留兜底以维持返回约定
        return ""
