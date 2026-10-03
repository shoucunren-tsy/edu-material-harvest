# -*- coding: utf-8 -*-
"""高校公开资料采集 · 自检

改动脚本后跑一遍，全 PASS（SKIP 不算失败）才算无回退。

    python scripts/selftest.py            # 全部（含可移植 grep 断言）
    python scripts/selftest.py --no-net   # 离线模式（跳过任何联网断言）

三类结果：
    PASS  通过
    SKIP  本机缺依赖（不算失败；如没装解压器只是跳过 find_7z 的存在性检查）
    FAIL  真失败（要修）

设计原则：**缺依赖要 SKIP，不要 FAIL**——别人机器上没 7z 不该判 skill 坏。
"""
import os
import re
import sys
import argparse
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C   # noqa: E402  （导入即完成 stdout utf-8 重配置）
import env           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)

PASS, SKIP, FAIL = [], [], []


def t(name, cond):
    (PASS if cond else FAIL).append(name)


def skip(name, why):
    SKIP.append("%s（%s）" % (name, why))


def _raises_dep(fn):
    try:
        fn()
    except env.DepError:
        return True
    except Exception:
        return False
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-net", action="store_true", help="离线：跳过联网断言")
    a = ap.parse_args()

    # ---------------- 编码 ----------------
    t("decode_gbk", C.decode("培养方案（2025版）".encode("gbk")) == "培养方案（2025版）")
    t("decode_utf8", C.decode("培养方案".encode("utf-8")) == "培养方案")

    # ---------------- 魔数 ----------------
    d = tempfile.mkdtemp()
    samples = {"pdf": b"%PDF-1.7", "docx": b"PK\x03\x04", "rar": b"Rar!\x1a\x07\x00",
               "doc": b"\xd0\xcf\x11\xe0\xa1\xb1", "zip": b"PK\x03\x04"}
    for ext, head in samples.items():
        p = os.path.join(d, "s." + ext)
        open(p, "wb").write(head + b"\x00" * 100)
        t("magic_" + ext, C.magic_ok(p, ext))
    p = os.path.join(d, "fake.pdf")
    open(p, "wb").write(b"<!DOCTYPE html>" + b"\x00" * 100)
    t("magic_reject_html", C.magic_ok(p, "pdf") is False)
    p = os.path.join(d, "small.pdf")
    open(p, "wb").write(b"%PDF-1.7")
    t("valid_small_false", C.valid(p, "pdf") is False)

    # ---------------- 命名 ----------------
    r = C.safe_name('a/b\\c:d*e?f"g<h>i|j')
    t("safe_name_clean", all(ch not in r for ch in '/\\:*?"<>|'))
    t("safe_name_illegal_to_underscore", C.safe_name("***") == "___")
    t("safe_name_empty", C.safe_name("") == "unnamed")
    t("ascii_url_ok", C.ascii_path_url("https://x.edu.cn/a/b.pdf"))
    t("ascii_url_bad", C.ascii_path_url("https://x.edu.cn/a/专业.pdf") is False)
    t("url_quote", "%E4%B8%93%E4%B8%9A" in C.url_quote("https://x.edu.cn/a/专业.pdf"))
    t("url_quote_keep_slash", "/a/" in C.url_quote("https://x.edu.cn/a/专业.pdf"))

    # ---------------- env 契约（缺失=SKIP，不当 FAIL）----------------
    z = env.find_7z()
    if z is None:
        skip("find_7z_exists", "本机无解压器")
        t("require_7z_raises", _raises_dep(env.require_7z))
    else:
        t("find_7z_exists", os.path.exists(z[0]))
        t("find_7z_flavor", z[1] in ("7z", "bandizip"))

    cu = env.find_curl()
    if cu is None:
        skip("find_curl_exists", "本机无 curl")
        t("require_curl_raises", _raises_dep(env.require_curl))
    else:
        t("find_curl_exists", os.path.exists(cu))

    ps = env.find_powershell()
    t("find_powershell_none_or_exists", ps is None or os.path.exists(ps))

    # ---------------- 回收站契约（缺 PowerShell 时隔离，不静默丢）----------------
    import shutil as _sh
    _real = env.find_powershell
    try:
        env.find_powershell = lambda: None      # 假装无 PowerShell
        qdir = os.path.join(d, "recycle_q")
        victim = os.path.join(d, "victim.txt")
        open(victim, "w").write("x")
        C.recycle(victim, tmp=qdir)
        moved = (not os.path.exists(victim)) and os.path.exists(os.path.join(qdir, "victim.txt"))
        t("recycle_quarantine_when_no_ps", moved)   # 文件移位，不是永久删
    finally:
        env.find_powershell = _real

    # ---------------- 可移植断言：全库无本机专属/写死日期 ----------------
    FORBID_ALL = ["D:\\Software", "D:/Software", "trae-data", "01_Python", "2026-10-03"]
    # scripts/*.py 里还不许写死校名（示例表在 references/ 里才允许出现）
    FORBID_CODE = FORBID_ALL + ["清华大学", "北京大学", "北京工业大学"]
    scanned = 0
    for root, _dirs, files in os.walk(SKILL_DIR):
        if "__pycache__" in root:
            continue
        for fn in files:
            if not fn.endswith((".py", ".md", ".json", ".txt")):
                continue
            if fn == "selftest.py":      # 本文件带着上面这些反面词字面量，跳过自扫描
                continue
            fp = os.path.join(root, fn)
            try:
                s = open(fp, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            scanned += 1
            is_own_code = (fn.endswith(".py") and os.path.dirname(fp) == HERE)
            rules = FORBID_CODE if is_own_code else FORBID_ALL
            for bad in rules:
                t("portable_no_%s_in_%s" % (bad.strip(":/\\"), fn),
                  bad not in s)
    t("portable_scanned_some", scanned > 8)

    # ---------------- 结果 ----------------
    print("PASS", len(PASS))
    if SKIP:
        print("SKIP", len(SKIP))
        for s in SKIP:
            print("   -", s)
    print("FAIL", len(FAIL))
    for f in FAIL:
        print("   x", f)
    print("RESULT:", "OK" if not FAIL else "HAS FAILURES")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
