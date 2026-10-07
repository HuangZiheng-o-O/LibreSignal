"""In-Memory Database 四层练习的空白实现。

按下方 Level 1 → 4 的顺序补方法；进入 Level 3 时需要让字段支持 TTL，
进入 Level 4 时再加入备份与恢复。各层题面见同目录 level1.md 至 level4.md。
"""
class InMemoryDatabase:
    def __init__(self):
        pass
    
    # ========== Level 1 Operations ==========
    def set(self,key, field, value):
        pass
    
    def get(self,key, field):
        pass

    def delete(self,key, field):
        pass
    
    # ========== Level 2 Operations ==========
    def scan(self, key):
        pass

    def scan_by_prefix(self, key, prefix):
        pass

    # ========== Level 3 Operations ==========
    def set_at(self, key, field, value, timestamp):
        pass

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        pass

    def delete_at(self, key, field, timestamp):
        pass

    def get_at(self, key, field, timestamp):
        pass

    def scan_at(self, key, timestamp):
        pass

    def scan_by_prefix_at(self, key, prefix, timestamp):
        pass

    # ========== Level 4 Operations ==========
    def backup(self, timestamp):
        pass

    def restore(self, timestamp, timestampToRestore):
        pass
