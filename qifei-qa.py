#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""祈飞结算原型 —— 自动质检脚本

用法：  python3 qifei-qa.py            # 全部场景
        python3 qifei-qa.py add rule   # 只跑指定场景

检查项：
  1) 静态：每个弹窗 div 嵌套深度归零、.actions 是 .modal 的直接子元素、ID 无重复、<script> 语法
  2) 运行时：逐个打开弹窗，量取模态框 / 底部操作区的位置关系，输出报告 + 截图
截图目录：/tmp/qifei-qa/*.png
"""
import io, os, re, subprocess, sys, json, shutil

HTML = "/Users/yechangmian/Documents/AI work/qifei-settlement-demo.html"
OUT = "/tmp/qifei-qa"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

SCEN = {
    "list":     ("祈飞结算商品维护 - 列表", "location.hash='#product';if(window.goPage)goPage('product');"),
    "expand":   ("商品行展开历史记录", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){var b=document.querySelector('#rows [data-expand]');if(b)b.click()},250)"),
    "add":      ("新增商品（未选商品）", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){$('#add').click()},150)"),
    "picked":   ("新增商品（已选商品）", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){$('#add').click();$('#pid').value='782654319876';$('#searchProduct').click();setTimeout(function(){var p=document.querySelector('[data-select]');if(p)p.click()},250)},150)"),
    "pickedoff":("新增商品（不参与结算）", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){$('#add').click();$('#pid').value='782654319876';$('#searchProduct').click();setTimeout(function(){var p=document.querySelector('[data-select]');if(p)p.click();setTimeout(function(){var t=document.querySelector('#nType input[value=off]');if(t)t.click()},200)},250)},150)"),
    "addrule":  ("主行新增结算规则", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){var b=document.querySelector('#rows [data-addrule]');if(b)b.click()},250)"),
    "rule":     ("编辑结算规则", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){var b=document.querySelector('[data-redit]');if(b)b.click()},150)"),
    "imp":      ("批量导入", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){$('#imp').click()},150)"),
    "dr":       ("新增变更（独立弹窗）", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){$('#drHistory').click();setTimeout(function(){$('#drChangeBtn').click()},200)},150)"),
    "drhist":   ("通用佣金率历史变更记录", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){$('#drHistory').click()},150)"),
    "drsave":   ("变更保存后重开历史记录", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){$('#drHistory').click();setTimeout(function(){$('#drChangeBtn').click();setTimeout(function(){document.getElementById('drStart').value='2026-10-08';document.getElementById('drLive').value='19';document.getElementById('drVideo').value='19';document.getElementById('drCard').value='19';$('#drSave').click()},200)},200)},150)"),
    "range":    ("时间段查询（组合选择器）", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){$('#rangeBtn').click();setTimeout(function(){$('#rgs').value='2026-09-10';$('#rge').value='2026-10-12';document.getElementById('rpOk').click()},150)},200)"),
    "rangeprev":("时间段-上月预设", "location.hash='#product';if(window.goPage)goPage('product');setTimeout(function(){$('#rangeBtn').click();setTimeout(function(){document.querySelector('#rangePop [data-rp=prev]').click();document.getElementById('rpOk').click()},150)},200)"),
    "dpfilter": ("达播-商品筛选（关键词）", "location.hash='#daboo';if(window.goPage)goPage('daboo');setTimeout(function(){var i=document.getElementById('dpq');i.value='儿童成长';i.dispatchEvent(new Event('input',{bubbles:true}));setTimeout(function(){var b=document.querySelector('#drows [data-expand]');if(b)b.click()},250)},250)"),
    "dpfilternone":("达播-商品筛选（无结果）", "location.hash='#daboo';if(window.goPage)goPage('daboo');setTimeout(function(){var i=document.getElementById('dpq');i.value='不存在的商品';i.dispatchEvent(new Event('input',{bubbles:true}))},250)"),
    "dexpand":  ("展开达人行", "location.hash='#daboo';if(window.goPage)goPage('daboo');setTimeout(function(){var b=document.querySelector('[data-expand]');if(b)b.click()},250)"),
    "daboo":    ("祈飞达播结算维护 - 列表", "location.hash='#daboo';if(window.goPage)goPage('daboo');"),
    "dadd":     ("新增达人带货", "location.hash='#daboo';if(window.goPage)goPage('daboo');setTimeout(function(){$('#dadd').click()},150)"),
    "dedit":    ("编辑达人带货", "location.hash='#daboo';if(window.goPage)goPage('daboo');setTimeout(function(){var b=document.querySelector('[data-goods]');if(b)b.click()},200)"),
    "dscope":   ("编辑达人带货（全店范围）", "location.hash='#daboo';if(window.goPage)goPage('daboo');setTimeout(function(){var b=document.querySelector('[data-goods=abu_2233]');if(b)b.click()},200)"),
    "store":    ("店铺档案（达人结算范围设置）", "location.hash='#store';if(window.goPage)goPage('store');"),
    "dpart":    ("达人结算范围（指定不结算·双tab）", "location.hash='#store';if(window.goPage)goPage('store');setTimeout(function(){document.querySelector('#storePartMode input[value=deny]').click();setTimeout(function(){if(window.goPage)goPage('daboo')},120)},150)"),
    "dallow":   ("达人结算范围（指定达人结算）", "location.hash='#store';if(window.goPage)goPage('store');setTimeout(function(){document.querySelector('#storePartMode input[value=allow]').click();setTimeout(function(){if(window.goPage)goPage('daboo')},120)},150)"),
    "dofftab":  ("不结算达人页签（第二张表）", "location.hash='#store';if(window.goPage)goPage('store');setTimeout(function(){document.querySelector('#storePartMode input[value=deny]').click();setTimeout(function(){if(window.goPage)goPage('daboo');document.querySelector('#dTab2 [data-t2=off]').click()},120)},150)"),
    "doffadd":  ("新增不结算达人", "location.hash='#store';if(window.goPage)goPage('store');setTimeout(function(){document.querySelector('#storePartMode input[value=deny]').click();setTimeout(function(){if(window.goPage)goPage('daboo');document.querySelector('#dTab2 [data-t2=off]').click();setTimeout(function(){document.getElementById('daddOff').click()},120)},120)},150)"),
    "dtgen":    ("达人通用佣金率-历史变更记录", "location.hash='#daboo';if(window.goPage)goPage('daboo');setTimeout(function(){document.getElementById('dtHistory').click()},250)"),
    "dtedit":   ("达人通用佣金率-新增变更", "location.hash='#daboo';if(window.goPage)goPage('daboo');setTimeout(function(){document.getElementById('dtHistory').click();setTimeout(function(){document.getElementById('dtChangeBtn').click()},250)},250)"),
    "dexpandall":("展开达人行（全店）", "location.hash='#daboo';if(window.goPage)goPage('daboo');setTimeout(function(){var b=document.querySelector('[data-expand=abu_2233]');if(b)b.click()},250)"),
    "brand":    ("特殊品牌结算", "location.hash='#brand';if(window.goPage)goPage('brand');"),
    "list1280": ("列表（1280 窄屏）", "location.hash='#product';if(window.goPage)goPage('product');", "1280,800"),
}

INJECT = """
<script>
(function(){
  var errs=[]; window.onerror=function(m){errs.push(String(m))};
  function R(e){var r=e.getBoundingClientRect();return {t:Math.round(r.top),b:Math.round(r.bottom),l:Math.round(r.left),r:Math.round(r.right),w:Math.round(r.width),h:Math.round(r.height)}}
  function report(){
    var out=[], ms=document.querySelectorAll('.mask.show');
    out.push('visible='+ms.length);
    ms.forEach(function(m){
      var md=m.querySelector('.modal'), ac=md?md.querySelector('.actions'):null;
      if(!md){out.push(m.id+':NO_MODAL');return}
      var mr=R(md), ar=ac?R(ac):null, nm=m.id||'?';
      var part=[nm+' '+mr.w+'x'+mr.h];
      part.push('actionsParent='+(ac?(ac.parentElement.classList.contains('modal')?'ok':'BAD'):'MISSING'));
      part.push('inBox='+(ar?((ar.b<=mr.b+1&&ar.t>=mr.t&&ar.r<=mr.r+1&&ar.l>=mr.l-1)?'ok':'BAD ['+ar.t+'~'+ar.b+' vs '+mr.t+'~'+mr.b+']'):'none'));
      part.push('vfit='+((mr.t>=-1&&mr.b<=window.innerHeight+1)?'ok':'BAD('+mr.b+'>'+window.innerHeight+')'));
      part.push('hfit='+((mr.l>=-1&&mr.r<=window.innerWidth+1)?'ok':'BAD('+mr.w+')'));
      part.push('ovfX='+(md.scrollWidth>md.clientWidth+1?'BAD':'ok'));
      var fm=md.querySelector('.form');
      if(fm)part.push('formScroll='+(fm.scrollHeight>fm.clientHeight+1?('Y '+fm.clientHeight+'/'+fm.scrollHeight):'n'));
      out.push(part.join(' '));
    });
    out.push('docOverflow='+(document.documentElement.scrollWidth>window.innerWidth+1?'BAD('+document.documentElement.scrollWidth+'>'+window.innerWidth+')':'ok'));
    out.push('err='+(errs.length?errs.join(';'):'无'));
    document.title='QA:: '+out.join(' || ');
  }
  setTimeout(function(){
    try{ __SC__ }catch(e){ errs.push('SC:'+e.message) }
    setTimeout(report,700);
  },500);
})();
</script>
"""


def static_checks(src):
    msgs, ok = [], True
    ids = re.findall(r'<div class="mask" id="([^"]+)"', src)
    for mid in ids:
        i = src.index('<div class="mask" id="%s">' % mid)
        nxt = src.find('<div class="mask"', i + 10)
        j = nxt if nxt > 0 else src.find("</body>")
        seg = src[i:j]
        depth, act = 0, []
        for m in re.finditer(r'<div\b[^>]*>|</div>', seg):
            if m.group(0).startswith("</"):
                depth -= 1
            else:
                depth += 1
                if 'class="actions"' in m.group(0):
                    act.append(depth)
        if depth != 0:
            ok = False
            msgs.append("✗ %s 嵌套未闭合（余 %d）" % (mid, depth))
        if act != [3]:
            ok = False
            msgs.append("✗ %s .actions 层级异常 %s（应为 [3]=.modal 子元素）" % (mid, act))
    # 重复 id
    allids = re.findall(r'\bid="([^"]+)"', src)
    dup = sorted({x for x in allids if allids.count(x) > 1})
    if dup:
        ok = False
        msgs.append("✗ 重复 id: " + ", ".join(dup))
    return ok, msgs


def run_chrome(path, shot, budget=3500, size="1440,900"):
    ud = "/tmp/cdq-" + str(os.getpid()) + "-" + str(abs(hash(path)) % 9999)
    base = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--force-device-scale-factor=1",
            "--window-size=" + size, "--user-data-dir=" + ud,
            "--virtual-time-budget=" + str(budget)]
    dom = subprocess.run(base + ["--dump-dom", "file://" + path],
                         capture_output=True, text=True, timeout=90).stdout
    subprocess.run(base + ["--screenshot=" + shot, "file://" + path],
                   capture_output=True, text=True, timeout=90)
    shutil.rmtree(ud, ignore_errors=True)
    m = re.search(r"<title>(.*?)</title>", dom, re.S)
    return (m.group(1).strip() if m else "(no title)")


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    src = io.open(HTML, encoding="utf-8").read()
    os.makedirs(OUT, exist_ok=True)

    print("=" * 78)
    print("① 静态结构检查")
    ok, msgs = static_checks(src)
    print("  结果：", "通过 ✅" if ok else "不通过 ❌")
    for m in msgs:
        print("   ", m)

    # <script> 语法
    scripts = re.findall(r"<script>(.*?)</script>", src, re.S)
    js = "\n;\n".join(scripts)
    io.open("/tmp/qifei-qa/all.js", "w", encoding="utf-8").write(js)
    node = "/Users/yechangmian/.workbuddy/binaries/node/versions/22.22.2-6/bin/node"
    r = subprocess.run([node, "--check", "/tmp/qifei-qa/all.js"], capture_output=True, text=True)
    print("  JS 语法：", "通过 ✅" if r.returncode == 0 else "失败 ❌ " + r.stderr[:400])

    print("=" * 78)
    print("② 运行时检查（逐个打开弹窗）")
    bad = 0
    for k, spec in SCEN.items():
        if only and k not in only:
            continue
        label, code = spec[0], spec[1]
        size = spec[2] if len(spec) > 2 else "1440,900"
        tmp = "/tmp/qifei-qa/%s.html" % k
        io.open(tmp, "w", encoding="utf-8").write(
            src.replace("</body>", INJECT.replace("__SC__", code) + "\n</body>"))
        shot = "/tmp/qifei-qa/%s.png" % k
        title = run_chrome(tmp, shot, size=size)
        flag = "✅" if ("BAD" not in title and "err=无" in title) else "❌"
        if flag == "❌":
            bad += 1
        print("  %s %-22s %s" % (flag, k, label))
        print("      " + title.replace("QA:: ", ""))
        print("      截图 " + shot)
    print("=" * 78)
    print("汇总：结构 %s；运行时异常场景 %d 个" % ("OK" if ok else "FAIL", bad))
    return 0 if ok and bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
