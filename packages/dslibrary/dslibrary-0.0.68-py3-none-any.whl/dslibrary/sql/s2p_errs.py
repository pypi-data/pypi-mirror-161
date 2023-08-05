"""
Interpret sql-to-pandas errors.
"""
import re
import sys
import traceback

from dslibrary import DSLibraryDataFormatException

PTN_TITLE = re.compile(r'^(.*?)\s+Traceback \(most recent call last\)$')
PTN_LEVEL = re.compile(r'^([^\n]+) in ([^\n]+)\n(.*)$', re.DOTALL)
PTN_DETAIL_W_TRACE = re.compile(r'^([^\n]+)\n\nOriginal error is below:\n----.*$', re.DOTALL)
PTN_ANOTHER = re.compile(r'\nDuring handling of the above exception, another exception occurred:\n')
PTN_REF_LINE = re.compile(r'^-+>\s*(\d+)\s+(.*)$')


def parse_ipykernel_traceback(lines: list):
    """
    Tracebacks are returned in a 'sort of visual' console format.  Here we attempt to turn it into a reasonably
    machine-interpretable format.
    """
    if not lines:
        return
    out = {"error": "", "levels": [], "detail": ""}
    current = out
    for line in lines:
        if line.startswith("------------"):
            continue
        m = PTN_TITLE.match(line)
        if m is not None:
            current["error"] = m.group(1)
            continue
        if PTN_ANOTHER.match(line) is not None:
            next = current["cause"] = {"error": "", "levels": [], "detail": ""}
            current = next
            continue
        m = PTN_DETAIL_W_TRACE.match(line)
        if m is not None:
            current["detail"] += m.group(1).strip() + "\n"
            continue
        level = _parse_tb_level(line)
        if level:
            current["levels"].append(level)
            continue
        current["detail"] += line.replace("\\n", "\n").strip() + "\n"
    return out


def _parse_tb_level(line: str):
    m = PTN_LEVEL.match(line)
    if m is not None:
        ref_line = list(filter(lambda l: l.startswith("-"), m.group(3).split("\n")))
        mref = PTN_REF_LINE.match(ref_line[0]) if ref_line else None
        return {
            "file": m.group(1),
            "method": m.group(2),
            "line": int(mref.group(1)) if mref is not None else None,
            "code": mref.group(2) if mref is not None else None
        }


def ipykernel_exc_to_json(exc_info=None) -> dict:
    """
    Convert an in-scope exception into a format that corresponds to what ipykernel returns, after its traceback is parsed by
    parse_ipykernel_traceback().
    """
    err_type, err_value, err_traceback = (exc_info or sys.exc_info())
    tb = traceback.extract_tb(err_traceback)
    return {
        "ename": err_type.__name__,
        "evalue": str(err_value),
        "traceback": {
            "error": err_type.__name__,
            "detail": str(err_value),
            "levels": [
                {"file": level.filename, "method": level.name, "line": level.lineno, "code": level.line or ""}
                for level in tb
            ]
        }
    }


def interpret_s2p_errors(err: dict):
    """
    Detect common SQL errors and add their description into a traceback.
    """
    _detect_datatype_conflict(err)


def _detect_datatype_conflict(err: dict):
    if err["ename"] not in {"ValueError", "TypeError"}:
        return
    if err["evalue"].startswith("Metadata inference failed in"):
        # dask
        pass
    elif "not supported between instances of " in err["evalue"]:
        # pandas
        pass
    else:
        return
    err["interpretation"] = \
        "The data types in the requested operation are not compatible.\n" \
        "You may need to clean one or more columns in order that they consistently contain the intended data type.\n"\
        "Reported error was: %s" % err["traceback"]["detail"].strip()


def translate_pandas_dask_exceptions(exc):
    """
    Recognize some exceptions and provide more helpful information/codes.
    """
    if isinstance(exc, UnicodeDecodeError):
        return DSLibraryDataFormatException(f"Encoding problem in file, reason={exc.reason}, offset={exc.start}, encoding={exc.encoding}")
    s_exc = str(exc)
    if "Error tokenizing data." in s_exc or ("Expected " in s_exc and "fields in line " in s_exc):
        return DSLibraryDataFormatException(f"CSV problem: {s_exc}")
    if isinstance(exc, ValueError) and ("Trailing data" in s_exc or "Expected object" in s_exc or "No ':'" in s_exc):
        return DSLibraryDataFormatException(f"JSON problem: {s_exc}")
    if isinstance(exc, ValueError):
        return DSLibraryDataFormatException(f"Data format problem: {s_exc}")
    return exc
