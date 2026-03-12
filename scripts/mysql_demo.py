"""
MySQL（或任意 database_url）连接与表操作 demo。

使用方式（项目根目录）：
  export DATABASE_URL="mysql+pymysql://用户:密码@host:端口/库名"
  python -m scripts.mysql_demo

不设置 DATABASE_URL 时使用默认 SQLite（./data/app.db）。
"""
import os
import sys

# 保证项目根在 path 中，便于直接 python scripts/mysql_demo.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    from dotenv import load_dotenv
    load_dotenv()

    from app.domain import models  # noqa: F401  先注册表到 Base.metadata
    from app.db import init_db, dispose_db
    from app.db.session import get_session
    from app.domain.repositories.example_repo import ExampleRepo

    # 1. 打印当前连接 URL（隐藏密码）
    url = os.environ.get("DATABASE_URL", "sqlite:///./data/app.db")
    if "@" in url and ":" in url:
        parts = url.split("@", 1)
        if len(parts) == 2:
            user_part = parts[0].split("//", 1)[-1]
            if ":" in user_part:
                user = user_part.split(":")[0]
                safe = f"{url.split('//')[0]}//{user}:***@{parts[1]}"
            else:
                safe = url
        else:
            safe = url
    else:
        safe = url
    print("database_url:", safe)

    # 2. 建表
    init_db()
    print("init_db() done.")

    # 3. 写一条
    with get_session() as session:
        obj = ExampleRepo.create(session, title="MySQL Demo", content="第一条示例")
        print("created:", obj.id, obj.title)

    # 4. 读列表
    with get_session() as session:
        items = ExampleRepo.list_all(session, limit=5)
        print("list_all:", [(e.id, e.title) for e in items])

    # 5. 释放连接
    dispose_db()
    print("dispose_db() done.")


if __name__ == "__main__":
    main()
