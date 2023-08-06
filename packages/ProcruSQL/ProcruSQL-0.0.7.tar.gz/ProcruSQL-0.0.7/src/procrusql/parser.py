#!/usr/bin/python3
import logging
import re
import sys
from pprint import pprint

import psycopg2

import procrusql

class RuleFile:
    def __init__(self, filename):
        with open(filename) as f:
            self.text = f.read()

class Failure:
    def __init__(self, message, position, parse_state):
        self.message = message
        self.position = position
        self.parse_state = parse_state

class ParseState:

    def __init__(self, text, position=0):
        self.text = text
        self.position = position
        self.child_failure = None

    def clone(self):
        ps = ParseState(self.text, self.position)
        return ps

    @property
    def rest(self):
        return self.text[self.position:]

    def printerror(self):
        if not self.child_failure:
            return
        position = self.child_failure.position
        message = self.child_failure.message
        linesbefore = self.text[:position].split("\n")
        linesafter = self.text[position:].split("\n")
        good = "\x1B[40;32m"
        bad = "\x1B[40;31m"
        reset = "\x1B[0m"
        s = reset + message + "\n"
        lines = []
        for ln in range(max(len(linesbefore) - 3, 0), len(linesbefore)):
            # XXX - join
            lines.append(reset + f"{ln+1:4}: " + good + linesbefore[ln] + reset)
        s += "\n".join(lines)
        s += bad + linesafter[0] + reset
        print(s)

        if  self.child_failure.parse_state:
            self.child_failure.parse_state.printerror()

    def skip_whitespace_and_comments(self):
        self.match(r"(\s+|#.*)*")

    def match(self, regexp):
        if m := re.match(regexp, self.text[self.position:]):
            self.position += len(m.group(0))
        return m

    def match_newlines(self):
        self.match(r"(\s+|#.*)*\n")

    def record_child_failure(self, ps_child, msg):
        if not self.child_failure or  ps_child.position > self.child_failure.position:
            self.child_failure = Failure(position=ps_child.position, message=msg, parse_state=ps_child)

def parse_ruleset(ps):
    ps2 = ps.clone()
    ps2.ast = []
    while ps2.rest:
        ps3 = parse_table_rule(ps2) or  \
              parse_column_rule(ps2) or \
              parse_data_rule(ps2) or   \
              parse_index_rule(ps2)
        if ps3:
            ps2.ast.append(ps3.ast)
            ps2.position = ps3.position
        else:
            ps.record_child_failure(ps2, "expected one of: table rule, column rule, data rule")
            return
    return ps2

def parse_table_rule(ps):
    ps2 = ps.clone()
    ps2.skip_whitespace_and_comments()
    if not ps2.match(r"table\b"):
        ps.record_child_failure(ps2, "expected “table”")
        return
    ps2.skip_whitespace_and_comments()
    ps3 = parse_table_name(ps2)
    if not ps3:
        ps.record_child_failure(ps2, "expected table name")
        return

    ps2.ast = procrusql.HaveTable(rulename(), [], ps3.ast[0])
    ps2.position = ps3.position
    return ps2

def parse_column_rule(ps):
    ps2 = ps.clone()
    ps2.ast = []
    ps2.skip_whitespace_and_comments()
    if not ps2.match(r"column\b"):
        ps.record_child_failure(ps2, "expected “column”")
        return

    # The table name should be omitted if this is part of a table declaration.
    # I haven't decided if I want to make that optional in this rule or write a
    # different rule. Probably the latter. If the former, I may have to change
    # the syntax to avoid ambiguity.
    ps3 = parse_table_name(ps2)
    if not ps3:
        ps.record_child_failure(ps2, "expected table name")
        return
    table_name = ps3.ast[0]
    ps2.position = ps3.position

    ps3 = parse_column_name(ps2)
    if not ps3:
        ps.record_child_failure(ps2, "expected column name")
        return
    column_name = ps3.ast[0]
    ps2.position = ps3.position

    ps3 = parse_column_definition(ps2)
    if not ps3:
        ps.record_child_failure(ps2, "expected column definition")
        return
    column_definition = ps3.ast[0]
    ps2.position = ps3.position

    ps2.ast = procrusql.HaveColumn(rulename(), [], table_name, column_name, column_definition)

    ps2.match_newlines()

    return ps2

def parse_data_rule(ps):
    ps2 = ps.clone()
    ps2.skip_whitespace_and_comments()
    if not ps2.match(r"data\b"):
        ps.record_child_failure(ps2, "expected “data”")
        return

    ps3 = parse_table_name(ps2)
    if not ps3:
        ps.record_child_failure(ps2, "expected table name")
        return
    table_name = ps3.ast[0]
    ps2.position = ps3.position

    if ps3 := parse_dict(ps2):
        key_data = ps3.ast
        ps2.position = ps3.position

        ps3 = parse_dict(ps2)
        if not ps3:
            ps.record_child_failure(ps2, "expected extra data definition")
            return
        extra_data = ps3.ast
        ps2.position = ps3.position

        ps3 = parse_label(ps2)
        if ps3:
            label = ps3.ast
            ps2.position = ps3.position
        else:
            label = rulename()

        ps2.ast = procrusql.HaveData(label, [], table_name, key_data, extra_data)

        ps2.match_newlines()
    elif ps3 := parse_init_query(ps2):
        # We have a bit of a problem here: The query extends to the end of the
        # line so there is no room for a label. I really don't want to parse
        # SQL here.
        label = rulename()
        ps2.position = ps3.position
        ps2.ast = procrusql.HaveInit(label, [], table_name, ps3.ast)

        ps2.match_newlines()
    else:
        ps.record_child_failure(ps2, "expected key data definition or insert query")
        return

    return ps2

def parse_index_rule(ps):
    ps2 = ps.clone()
    ps2.skip_whitespace_and_comments()
    m = ps2.match(r"(unique)? index\b")
    if not m:
        ps.record_child_failure(ps2, "expected “(unique) index”")
        return
    index_type = m.group(0)

    ps3 = parse_index_name(ps2)
    if not ps3:
        ps.record_child_failure(ps2, "expected index name")
        return
    index_name = ps3.ast[0]
    ps2.position = ps3.position
    if not ps2.match(r"\s+on\b"):
        ps.record_child_failure(ps2, "expected “on”")
        return

    ps3 = parse_table_name(ps2)
    if not ps3:
        ps.record_child_failure(ps2, "expected table name")
        return
    table_name = ps3.ast[0]
    ps2.position = ps3.position

    m = ps2.match(r"\s*(using\b|\([\w, ]+\))[^>\n]*")
    if not m:
        ps.record_child_failure(ps2, "expected “using” or column list")
    index_definition = m.group(0)

    ps3 = parse_label(ps2)
    if ps3:
        label = ps3.ast
        ps2.position = ps3.position
    else:
        label = rulename()

    ps2.ast = procrusql.HaveIndex(label, [], table_name, index_name, index_type, index_definition)

    ps2.match_newlines()

    return ps2



def parse_table_name(ps):
    # For now this matches only simple names, not schema-qualified names or
    # quoted names.
    ps2 = ps.clone()
    ps2.ast = []
    ps2.skip_whitespace_and_comments()
    if ps2.rest[0].isalpha():
        m = ps2.match(r"\w+") # always succeeds since we already checked the first character
        ps2.ast.append(m.group(0))
    else:
        ps.record_child_failure(ps2, "expected table name")
    return ps2

def parse_column_name(ps):
    # For now this matches only simple names, not quoted names.
    # Also, this is an exact duplicate of parse_table_name, but they will
    # probably diverge, so I duplicated it.
    ps2 = ps.clone()
    ps2.ast = []
    ps2.skip_whitespace_and_comments()
    if ps2.rest[0].isalpha():
        m = ps2.match(r"\w+") # always succeeds since we already checked the first character
        ps2.ast.append(m.group(0))
        return ps2
    else:
        ps.record_child_failure(ps2, "expected column name")
        return

def parse_index_name(ps):
    # this is an exact duplicate of parse_table_name and parse_column_name, but they will
    # probably diverge, so I duplicated it. I probably should define a
    # parse_identifier and redefine them in terms of it.
    ps2 = ps.clone()
    ps2.ast = []
    ps2.skip_whitespace_and_comments()
    if ps2.rest[0].isalpha():
        m = ps2.match(r"\w+") # always succeeds since we already checked the first character
        ps2.ast.append(m.group(0))
        return ps2
    else:
        ps.record_child_failure(ps2, "expected index name")
        return

def parse_column_definition(ps):
    ps2 = ps.clone()
    ps2.ast = []
    ps2.skip_whitespace_and_comments()
    sqltypes = (
        "int", "integer", "serial",
        "boolean",
        "text", "character varying",
        "date", "timestamp with time zone", "timestamptz"
    )
    pattern = "(" + "|".join(sqltypes) + ")" + r"([ \t]+default .*)?([ \t]+not null)?([ \t]+(primary key|unique|references \w+))?\b"
    m = ps2.match(pattern)
    if not m:
        ps.record_child_failure(ps2, "expected column definition")
        return
    ps2.ast.append(m.group(0))
    return ps2

def parse_dict(ps):
    ps2 = ps.clone()
    d = {}
    ps2.skip_whitespace_and_comments()
    if not ps2.match(r"{"):
        ps.record_child_failure(ps2, "expected “{”")
        return
    while True:
        ps2.skip_whitespace_and_comments()
        if ps2.match(r'}'):
            break

        m = ps2.match(r'\w+|"([^"]+)"')
        if not m:
            ps.record_child_failure(ps2, "expected column name")
            return
        # XXX - unquote properly
        if m.group(1):
            k = m.group(1)
        else:
            k = m.group(0)

        ps2.skip_whitespace_and_comments()
        if not ps2.match(":"):
            ps.record_child_failure(ps2, "expected “:”")
            return
        ps2.skip_whitespace_and_comments()
        if m := ps2.match(r'[0-9]+'):
            v = int(m.group(0))
        elif m := ps2.match(r'"([^"]*)"'):
            # XXX - process backslash escapes
            v = m.group(1)
        elif m := ps2.match(r'[tT]rue'):
            v = True
        elif m := ps2.match(r'[fF]alse'):
            v = False
        elif m := ps2.match(r'None|null|NULL'):
            v = None
        elif m := ps2.match(r'@(\w+)/(\d+)/(\w+)'):
            v = procrusql.Ref(m.group(1), int(m.group(2)), m.group(3))
        else:
            ps.record_child_failure(ps2, "expected value")
            return

        d[k] = v

        ps2.skip_whitespace_and_comments()
        comma_found = ps2.match(r',')
        ps2.skip_whitespace_and_comments()
        if ps2.match(r'}'):
            break
        if not comma_found:
            ps.record_child_failure(ps2, "expected comma or close brace")
            return
    ps2.ast = d
    return ps2

def parse_init_query(ps):
    ps2 = ps.clone()
    ps2.skip_whitespace_and_comments()
    if m := ps2.match(r'(?i:with|insert)\b.*'):
        ps2.ast = m.group(0)
        return ps2
    else:
        ps.record_child_failure(ps2, "expected insert query")
        return

def parse_label(ps):
    ps2 = ps.clone()
    if m := ps2.match(r"\s*>>\s*(\w+)"):
        ps2.ast = m.group(1)
        return ps2
    else:
        ps.record_child_failure(ps2, "expected label definition")
        return

rulenum = 0
def rulename():
    global rulenum
    rulenum += 1
    return f"__rule_{rulenum}"

