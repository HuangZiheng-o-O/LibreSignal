class InMemoryDatabase:
    def __init__(self):
        # data[key][field] = (value, expire_at)，expire_at=None 表示永不过期
        self.data = {}
        # backups = [(backup_time, snapshot)]；snapshot 中保存的是“剩余 TTL”
        self.backups = []

    @staticmethod
    def _alive(item, timestamp):
        """字段在 timestamp 时是否仍有效；TTL 区间为 [start, expire_at)。"""
        return item is not None and (item[1] is None or int(timestamp) < item[1])

    @staticmethod
    def _format(fields):
        """按字段名字典序输出。"""
        return ", ".join(f"{field}({value})" for field, value in sorted(fields))

    # ========== Level 1 ==========
    def set(self, key, field, value):
        self.data.setdefault(key, {})[field] = (value, None)
        return ""

    def get(self, key, field):
        item = self.data.get(key, {}).get(field)
        return item[0] if item is not None else ""

    def delete(self, key, field):
        record = self.data.get(key)
        if record is None or field not in record:
            return "false"
        del record[field]
        if not record:
            del self.data[key]
        return "true"

    # ========== Level 2 ==========
    def scan(self, key):
        record = self.data.get(key, {})
        return self._format((field, item[0]) for field, item in record.items())

    def scan_by_prefix(self, key, prefix):
        record = self.data.get(key, {})
        return self._format(
            (field, item[0]) for field, item in record.items()
            if field.startswith(prefix)
        )

    # ========== Level 3 ==========
    def set_at(self, key, field, value, timestamp):
        # 无 TTL 的写入会清除该字段原有的过期时间
        self.data.setdefault(key, {})[field] = (value, None)
        return ""

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        timestamp, ttl = int(timestamp), int(ttl)
        self.data.setdefault(key, {})[field] = (value, timestamp + ttl)
        return ""

    def delete_at(self, key, field, timestamp):
        record = self.data.get(key)
        item = None if record is None else record.get(field)
        if not self._alive(item, timestamp):
            return "false"
        return self.delete(key, field)

    def get_at(self, key, field, timestamp):
        item = self.data.get(key, {}).get(field)
        return item[0] if self._alive(item, timestamp) else ""

    def scan_at(self, key, timestamp):
        return self._scan_at(key, "", timestamp)

    def scan_by_prefix_at(self, key, prefix, timestamp):
        return self._scan_at(key, prefix, timestamp)

    def _scan_at(self, key, prefix, timestamp):
        record = self.data.get(key, {})
        return self._format(
            (field, item[0]) for field, item in record.items()
            if field.startswith(prefix) and self._alive(item, timestamp)
        )

    # ========== Level 4 ==========
    def backup(self, timestamp):
        timestamp = int(timestamp)
        snapshot = {}

        for key, record in self.data.items():
            saved = {}
            for field, item in record.items():
                if self._alive(item, timestamp):
                    value, expire_at = item
                    # 保存剩余 TTL，恢复时再以恢复时间为起点重算
                    remaining = None if expire_at is None else expire_at - timestamp
                    saved[field] = (value, remaining)
            if saved:
                snapshot[key] = saved

        self.backups.append((timestamp, snapshot))
        return str(len(snapshot))

    def restore(self, timestamp, timestampToRestore):
        timestamp, target = int(timestamp), int(timestampToRestore)

        # 时间单调递增，倒序找到 target 时刻之前（含该时刻）的最近备份
        for backup_time, snapshot in reversed(self.backups):
            if backup_time <= target:
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
