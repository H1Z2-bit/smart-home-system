from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCE_SQL = ROOT_DIR.parent / "smart_home.sql"
SQL_DIR = ROOT_DIR / "sql"


def main() -> None:
    sql = SOURCE_SQL.read_text(encoding="utf-8")
    first_insert = sql.index("INSERT INTO")
    schema_part = sql[:first_insert].rstrip()
    data_part = sql[first_insert:].strip()
    data_part = data_part.replace("SET FOREIGN_KEY_CHECKS = 1;", "").strip()

    tables = [
        line.split("`")[1]
        for line in schema_part.splitlines()
        if line.startswith("DROP TABLE IF EXISTS `")
    ]

    SQL_DIR.mkdir(parents=True, exist_ok=True)
    (SQL_DIR / "init_schema.sql").write_text(
        schema_part + "\n\nSET FOREIGN_KEY_CHECKS = 1;\n",
        encoding="utf-8",
    )
    (SQL_DIR / "init_data.sql").write_text(
        header("Smart Home demo data") + "\n"
        "USE `smart_home`;\n\n"
        "SET NAMES utf8mb4;\n"
        "SET FOREIGN_KEY_CHECKS = 0;\n\n"
        + data_part
        + "\n\nSET FOREIGN_KEY_CHECKS = 1;\n",
        encoding="utf-8",
    )
    (SQL_DIR / "reset_demo_data.sql").write_text(
        header("Reset Smart Home demo data") + "\n"
        "USE `smart_home`;\n\n"
        "SET NAMES utf8mb4;\n"
        "SET FOREIGN_KEY_CHECKS = 0;\n\n"
        + "\n".join(f"DELETE FROM `{table}`;" for table in tables)
        + "\n\n"
        + "\n".join(f"ALTER TABLE `{table}` AUTO_INCREMENT = 1;" for table in reversed(tables))
        + "\n\n"
        + data_part
        + "\n\nSET FOREIGN_KEY_CHECKS = 1;\n",
        encoding="utf-8",
    )
    print("Generated sql/init_schema.sql")
    print("Generated sql/init_data.sql")
    print("Generated sql/reset_demo_data.sql")


def header(title: str) -> str:
    return f"/*\n {title}\n Generated from smart_home.sql.\n*/"


if __name__ == "__main__":
    main()
