def save_markdown(surah_title, surah_num, intro, sections):
    safe     = re.sub(r'[^\w\u0600-\u06FF]', '_', surah_title)[:40]
    filename = f"{surah_num:03d}_{safe}.md"
    filepath = os.path.join(OUT_DIR, filename)

    lines        = [
        f"# {surah_title}\n\n",
        f"> المصدر: {BASE}/tafseer/{surah_num}\n\n",
        "---\n\n",
    ]
    all_footnotes = []   # ← تُجمع هنا كل حواشي الملف
    global_fn     = 1

    def renum(text, fns):
        nonlocal global_fn
        local_map = {}
        for fn in fns:
            m = re.match(r'\[\^(\d+)\]:', fn)
            if m:
                local_map[m.group(1)] = str(global_fn)
                global_fn += 1
        for loc, gbl in local_map.items():
            text = re.sub(rf'\[\^{re.escape(loc)}\](?!\d)', f'[^{gbl}]', text)
        new_fns = []
        for fn in fns:
            m = re.match(r'\[\^(\d+)\]:(.*)', fn, re.DOTALL)
            if m:
                new_fns.append(
                    f"[^{local_map.get(m.group(1), m.group(1))}]:{m.group(2)}"
                )
        return text, new_fns

    # تعريف السورة
    if intro.get("text"):
        lines.append("## تعريف السورة\n\n")
        text, fns = renum(intro["text"], intro.get("footnotes", []))
        lines.append(f"{text}\n\n")
        all_footnotes.extend(fns)   # ← تأجيل، لا كتابة فورية
        lines.append("---\n\n")

    # المقاطع
    for sec in sections:
        lines.append(f"## {sec['title']}\n\n")
        lines.append(f"> {sec['url']}\n\n")
        if sec.get("text"):
            text, fns = renum(sec["text"], sec.get("footnotes", []))
            lines.append(f"{text}\n\n")
            all_footnotes.extend(fns)   # ← تأجيل
        lines.append("---\n\n")

    # ✅ كل الحواشي في نهاية الملف مرة واحدة
    if all_footnotes:
        lines.append("\n")
        for fn in all_footnotes:
            lines.append(f"{fn}\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

    total = len(intro.get("text", "")) + sum(len(s.get("text", "")) for s in sections)
    print(f"    ✔ {filepath}  |  {len(sections)} مقطع  |  ~{total//1024} KB  |  {len(all_footnotes)} حاشية")
    return filepath