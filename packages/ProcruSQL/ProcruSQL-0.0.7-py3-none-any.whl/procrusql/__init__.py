import argparse
import logging
import sys

import psycopg2
from psycopg2 import sql
from psycopg2 import extras

from . import parser

log = logging.getLogger(__name__)
log_action = log.getChild("action")
log_check = log.getChild("check")
log_state = log.getChild("state")

class Node:
    def __init__(self, name, depends):
        self.name = name
        self.depends = depends
        self.ok = False
        self.ready = False

    def __repr__(self):
        return f"{type(self)}({self.name}{' ready' if self.ready else ''}{' ok' if self.ok else ''})"

    def is_ready(self):
        # XXX - Naive O(n²) algorithm
        if self.ready:
            return True
        for d in self.depends:
            found = False
            for w in want:
                if w.name == d:
                    if not w.ok:
                        log_state.info("%s depends on %s which is not yet ok", self.name, d)
                        return False
                    found = True
                    break
            if not found:
                raise RuntimeError(f"Dependency {d} of {self.name} doesn't exist")
        log_state.info("%s is now ready", self.name)
        self.ready = True
        return True

    def set_order(self):
        global order
        order += 1
        self.order = order

class HaveData(Node):
    def __init__(self, name, depends, table, key, extra):
        super().__init__(name, depends)
        self.table = table
        self.key = key
        self.extra = extra

    def check(self):
        log_check.info("Checking %s", self.name)
        csr = db.cursor(cursor_factory=extras.DictCursor)
        key_checks = [
            sql.SQL(" = ").join([ sql.Identifier(x), sql.Placeholder() ])
            for x in self.key.keys()
        ]
        key_check = sql.SQL(" and ").join(key_checks)
        q = sql.SQL(
                "select * from {table} where {key_check}"
            ).format(
                table=sql.Identifier(self.table),
                key_check=key_check
            )
        key_values = [v.resolve() if isinstance(v, Ref) else v for v in self.key.values()]
        csr.execute(q, key_values)
        self.result = csr.fetchall()
        log_check.info("Got %d rows", len(self.result))
        if self.result:
            extra_columns = list(self.extra.keys())
            for c in extra_columns:
                if self.result[0][c] != self.extra[c]:
                    log_action.info("Updating %s: %s <- %s", key_values, c, self.extra[c])
                    q = sql.SQL(
                        "update {table} set {column}={placeholder} where {key_check}"
                    ).format(
                        table=sql.Identifier(self.table),
                        column=sql.Identifier(c),
                        placeholder=sql.Placeholder(),
                        key_check=key_check,
                    )
                    csr.execute(q, [self.extra[c]] + key_values)
                    self.result[0][c] = self.extra[c]
            self.set_order()
            self.ok = True
            log_state.info("%s is now ok", self.name)
            return
        else:
            extra_values = [v.resolve() if isinstance(v, Ref) else v for v in self.extra.values()]
            columns = list(self.key.keys()) + list(self.extra.keys())
            values = key_values + extra_values
            q = sql.SQL(
                    "insert into {table}({columns}) values({placeholders}) returning *"
                ).format(
                    table=sql.Identifier(self.table),
                    columns=sql.SQL(", ").join([sql.Identifier(x) for x in columns]),
                    placeholders=sql.SQL(", ").join([sql.Placeholder() for x in columns]),
                )
            log_action.info("Inserting data")
            csr.execute(q, values)
            self.result = csr.fetchall()
            log_action.info("Got %d rows", len(self.result))
            if self.result:
                self.set_order()
                self.ok = True
                log_state.info("%s is now ok", self.name)
                return
            # We shouldn't get here. Either the insert succeeded, or it raised an
            # exception. Success with 0 rows should not happen.
        raise RuntimeError("Unreachable code reached")

class HaveInit(Node):
    def __init__(self, name, depends, table, query):
        super().__init__(name, depends)
        self.table = table
        self.query = query

    def check(self):
        log_check.info("Checking %s", self.name)

        for w in want:
            if isinstance(w, HaveTable) and w.table == self.table:
                if not w.ok:
                    log_check.error("%s not yet ok", w.name)
                    raise RuntimeError(f"Cannot insert into table {w.table} from {w.name} which is not yet ok. Please add a dependency")
                if w.new:
                    log_action.info("Executing %s", self.query)
                    csr = db.cursor(cursor_factory=extras.DictCursor)
                    csr.execute(self.query)
                    self.result = csr.fetchall()
                    log_action.info("Got %d rows", len(self.result))
                    self.set_order()
                else:
                    log_check.info("Table %s already exists", w.table)
                self.ok = True
                log_state.info("%s is now ok", self.name)
                break
        else:
            raise RuntimeError(f"Cannot find a rule which creates table {self.table}")


class HaveTable(Node):

    def __init__(self, name, depends, table, schema="public"):
        super().__init__(name, depends)
        self.table = table
        self.schema = "public"

    def check(self):
        log_check.info("Checking %s", self.name)
        csr = db.cursor(cursor_factory=extras.DictCursor)
        csr.execute(
                """
                select * from information_schema.tables
                where table_schema = %s and table_name = %s
                """,
                (self.schema, self.table,))
        r = csr.fetchall()
        if len(r) == 1:
            # Table exists, all ok
            self.set_order()
            self.ok = True
            self.new = False
            log_state.info("%s is now ok", self.name)
            return
        if len(r) > 1:
            raise RuntimeError(f"Found {len(r)} tables with schema {self.schema} and name {self.table}")

        # Create table
        # (Yes, we can actually create a table with 0 columns)
        log_action.info("Creating table %s.%s", self.schema, self.table)
        q = sql.SQL("create table {schema}.{table}()").format(
                schema=sql.Identifier(self.schema),
                table=sql.Identifier(self.table)
            )
        csr.execute(q)
        self.set_order()
        self.ok = True
        self.new = True
        log_state.info("%s is now ok", self.name)

    pass

class HaveColumn(Node):
    # hjp=> alter table service add id serial primary key;
    # ALTER TABLE
    # hjp=> alter table service add type text;
    # ALTER TABLE
    # ...
    def __init__(self, name, depends, table, column, definition, schema="public"):
        super().__init__(name, depends)
        self.table = table
        self.column = column
        self.definition = definition
        self.schema = "public"

    def check(self):
        log_check.info("Checking %s", self.name)
        csr = db.cursor(cursor_factory=extras.DictCursor)
        # For now just check if column exists. Checking the type etc. will be implemented later
        csr.execute(
                """
                select * from information_schema.columns
                where table_schema = %s and table_name = %s and column_name = %s
                """,
                (self.schema, self.table, self.column, ))
        r = csr.fetchall()
        if len(r) == 1:
            # Column exists, all ok
            self.set_order()
            self.ok = True
            log_state.info("%s is now ok", self.name)
            return
        if len(r) > 1:
            raise RuntimeError(f"Found {len(r)} columns with nam {self.columnr} in {self.schema}.{self.table}")

        # Create column
        log_action.info("Adding column %s to table %s.%s", self.column, self.schema, self.table)
        q = sql.SQL("alter table {schema}.{table} add {column} {definition}").format(
                schema=sql.Identifier(self.schema),
                table=sql.Identifier(self.table),
                column=sql.Identifier(self.column),
                definition=sql.SQL(self.definition),
            )
        csr.execute(q)
        self.set_order()
        self.ok = True
        log_state.info("%s is now ok", self.name)

class HaveUniqueConstraint(Node):
    # hjp=> alter table service add unique (type, feature);
    # ALTER TABLE
    pass

class HaveIndex(Node):
    def __init__(self, name, depends, table, index, type, definition, schema="public"):
        super().__init__(name, depends)
        self.table = table
        self.index = index
        self.type = type
        self.definition = definition
        self.schema = schema

    def check(self):
        log_check.info("Checking %s", self.name)
        csr = db.cursor(cursor_factory=extras.DictCursor)
        # For now just check if index exists. Checking the type etc. will be implemented later
        csr.execute(
                """
                select * from pg_indexes
                where schemaname = %s and tablename = %s and indexname = %s
                """,
                (self.schema, self.table, self.index, ))
        r = csr.fetchall()
        if len(r) == 1:
            # Index exists, all ok
            self.set_order()
            self.ok = True
            log_state.info("%s is now ok", self.name)
            return
        if len(r) > 1:
            raise RuntimeError(f"Found {len(r)} indexes with name {self.index} on {self.schema}.{self.table}")

        # Create index
        log_action.info("Adding index %s to table %s.%s", self.index, self.schema, self.table)
        q = sql.SQL("create {type} {index} on {schema}.{table} {definition}").format(
                type=sql.SQL(self.type),
                schema=sql.Identifier(self.schema),
                table=sql.Identifier(self.table),
                index=sql.Identifier(self.index),
                definition=sql.SQL(self.definition),
            )
        csr.execute(q)
        self.set_order()
        self.ok = True
        log_state.info("%s is now ok", self.name)


def findnode(name):
    for w in want:
        if w.name == name:
            return w

class Ref:
    def __init__(self, datanode, row, column):
        self.datanode = datanode
        self.row = row
        self.column = column

    def resolve(self):
        datanode = findnode(self.datanode)
        if not datanode.ok:
            # XXX - We might try to resolve this, but for now the user is responsible to declare the dependency explicitely
            raise RuntimeError(f"Cannot get data from {datanode.name} which is not yet ok. Please add a dependency")
        return datanode.result[self.row][self.column]


def fit(_db, _want):
    global db, want, order
    db = _db
    want = _want
    order = 0
    while True:
        progress = False
        not_ok = 0
        for w in want:
            if not w.ok:
                if w.is_ready():
                    w.check()
                    progress = True
                else:
                    not_ok += 1
        if not_ok == 0:
            break
        if not progress:
            raise RuntimeError(f"Didn't make any progress in this round, but {not_ok} requirements are still not ok")
        log_state.info("%d requirements are not yet ok", not_ok)

    db.commit()
    log_state.info("Done")

def dump_dot():
    print("digraph {")
    for w in want:
        print(f"\t{w.name} [shape=rect]")
        for d in w.depends:
            print(f"\t{d} -> {w.name} [constraint=false]")
    in_order = [w.name for w in sorted(want, key=lambda x: x.order)]
    for i in range(1, len(in_order)):
        print(f"\t{in_order[i-1]} -> {in_order[i]} [style=dashed]")
    print("}")

def main():
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s %(lineno)d | %(message)s", level=logging.DEBUG)
    ap = argparse.ArgumentParser()
    ap.add_argument("--dbname")
    ap.add_argument("--dbuser")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    db = psycopg2.connect(dbname=args.dbname, user=args.dbuser)

    rules = []
    for f in args.files:
        with open(f) as rf:
            text = rf.read()
        ps = parser.ParseState(text)

        ps2 = parser.parse_ruleset(ps)

        if not ps2:
            ps.printerror()
            sys.exit(1)
        rules.extend(ps2.ast)

    fit(db, rules)

