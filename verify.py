#!/usr/bin/env python3
"""
逐字比对验证：我们的爻辞数据库 vs ctext.org（中国哲学书电子化计划）
"""
import sys, re, time, json, os
import urllib.request

# NOTE: Requires cast_hexagram.py (HEXAGRAM_MAP, HEXAGRAMS) and yaoci_data.py (YAOCI)
# from the yijing skill scripts. Place those files on your PYTHONPATH to run.
from cast_hexagram import HEXAGRAM_MAP, HEXAGRAMS
from yaoci_data import YAOCI

# ─── ctext.org URL mapping ───
HEX_SLUGS = {
    1:'qian',2:'kun',3:'tun',4:'meng',5:'xu',6:'song',
    7:'shi',8:'bi',9:'xiao-xu',10:'lu',
    11:'tai',12:'pi',13:'tong-ren',14:'da-you',15:'qian1',16:'yu',
    17:'sui',18:'gu',19:'lin',20:'guan',
    21:'shi-he',22:'bi1',23:'bo',24:'fu',25:'wu-wang',26:'da-xu',
    27:'yi',28:'da-guo',29:'kan',30:'li',
    31:'xian',32:'heng',33:'dun',34:'da-zhuang',35:'jin',36:'ming-yi',
    37:'jia-ren',38:'kui',39:'jian',40:'xie',
    41:'sun',42:'yi1',43:'guai',44:'gou',45:'cui',46:'sheng',
    47:'kun1',48:'jing',49:'ge',50:'ding',
    51:'zhen',52:'gen',53:'jian1',54:'gui-mei',55:'feng',56:'lv',
    57:'xun',58:'dui',59:'huan',60:'jie',
    61:'zhong-fu',62:'xiao-guo',63:'ji-ji',64:'wei-ji',
}

# ─── Traditional → Simplified mapping (common chars in Zhouyi) ───
T2S = str.maketrans({
    '龍':'龙','見':'见','終':'终','厲':'厉','躍':'跃','淵':'渊','飛':'飞',
    '貞':'贞','馬':'马','漣':'涟','堅':'坚','習':'习','從':'从','譽':'誉',
    '黃':'黄','戰':'战','幾':'几','錫':'锡','褫':'褫','訟':'讼','歸':'归',
    '邑':'邑','輿':'舆','帥':'帅','開':'开','國':'国','誡':'诫','顯':'显',
    '驅':'驱','發':'发','說':'说','納':'纳','婦':'妇','擊':'击','禦':'御',
    '為':'为','寇':'寇','恆':'恒','來':'来','敬':'敬','復':'复','渝':'渝',
    '長':'长','執':'执','鞶':'鞶','潛':'潜','勸':'劝','觀':'观','臨':'临',
    '養':'养','損':'损','益':'益','決':'决','萃':'萃','無':'无','於':'于',
    '廟':'庙','親':'亲','問':'问','亂':'乱','號':'号','隨':'随','蠱':'蛊',
    '盧':'庐','碩':'硕','遷':'迁','圭':'圭','禽':'禽','遯':'遁','壯':'壮',
    '藩':'藩','羝':'羝','喪':'丧','晉':'晋','愁':'愁','鼠':'鼠','箕':'箕',
    '闈':'闱','睽':'睽','輻':'辐','牽':'牵','揮':'挥','撝':'撝','僕':'仆',
    '資':'资','鑄':'铸','鉉':'铉','鉅':'钜','鼎':'鼎','鑒':'鉴','歸':'归',
    '實':'实','濟':'济','練':'练','鬼':'鬼','繻':'繻','億':'亿','麗':'丽',
    '盤':'盘','窺':'窥','漸':'渐','隴':'陇','陵':'陵','磐':'磐','屨':'屦',
    '膚':'肤','齧':'啮','臘':'腊','噬':'噬','嗑':'嗑','幹':'干','裕':'裕',
    '譽':'誉','靈':'灵','龜':'龟','頤':'颐','躋':'跻','險':'险','窞':'窞',
    '緯':'纬','繫':'系','紱':'绂','棘':'棘','纆':'纆','徽':'徽','蹇':'蹇',
    '碩':'硕','隼':'隼','墉':'墉','鱣':'鳣','狐':'狐','遜':'逊','孚':'孚',
    '萊':'莱','藟':'藟','臲':'臲','卼':'卼','覯':'觏','賁':'贲','皤':'皤',
    '翰':'翰','帶':'带','鶴':'鹤','寇':'寇','陸':'陆','豮':'豮','牿':'牿',
    '輹':'輹','銜':'衔','轅':'辕','轂':'毂','輪':'轮','尾':'尾','茀':'茀',
    '袽':'袽','鰒':'鲋','餗':'餗','鑄':'铸','銑':'铣','釜':'釜','雉':'雉',
    '戶':'户','闚':'窥','闃':'阒','幃':'帏','覿':'觌','蔀':'蔀','沬':'沬',
    '紀':'纪','機':'机','號':'号','翮':'翮','僕':'仆','斧':'斧','巽':'巽',
    '兌':'兑','渙':'涣','節':'节','魴':'鲂','妣':'妣','匹':'匹','鶴':'鹤',
    '靡':'靡','爵':'爵','壺':'壶','樽':'樽','簋':'簋','纓':'缨','約':'约',
    '牖':'牖','幃':'帏','學':'学','類':'类','間':'间','閑':'闲','關':'关',
    '門':'门','庭':'庭','鶴':'鹤','濡':'濡','豕':'豕','載':'载','張':'张',
    '弧':'弧','膢':'膢','遇':'遇','夫':'夫','體':'体','車':'车','徒':'徒',
})

def t2s(text):
    """Traditional Chinese to Simplified Chinese"""
    return text.translate(T2S)

def normalize(text):
    """Remove all punctuation and whitespace for pure character comparison"""
    # Remove common Chinese and Western punctuation
    text = re.sub(r'[，。；：、！？「」『』（）\[\]【】""''…—\-,\.;:!\?\s\u3000]', '', text)
    return text

def extract_yaoci_from_html(html_text, hex_num):
    """Extract yaoci from ctext.org HTML page"""
    # ctext.org puts the text in <td> elements within tables
    # The classical text lines contain the yao positions

    results = {}

    # Look for lines containing yao position markers
    yao_patterns = [
        (r'初[九六]', '初'),
        (r'[九六]二', '二'),
        (r'[九六]三', '三'),
        (r'[九六]四', '四'),
        (r'[九六]五', '五'),
        (r'上[九六]', '上'),
        (r'用[九六]', '用'),
    ]

    # Extract text content, removing HTML tags
    text = re.sub(r'<[^>]+>', '\n', html_text)
    text = re.sub(r'&[a-zA-Z]+;', '', text)

    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line or len(line) < 4:
            continue

        # Check for yao markers
        for pattern, label in yao_patterns:
            match = re.match(r'^(' + pattern + r'[，：\s]*.+?)$', line)
            if match:
                full_text = match.group(1).strip()
                # Extract the key
                key_match = re.match(r'^(初[九六]|[九六][二三四五]|上[九六]|用[九六])', full_text)
                if key_match:
                    key = key_match.group(1)
                    if key not in results:  # Take first occurrence
                        results[key] = full_text

    return results

def fetch_page(hex_num):
    """Fetch ctext.org page for a hexagram"""
    slug = HEX_SLUGS[hex_num]
    url = f'https://ctext.org/book-of-changes/{slug}'
    cache_file = f'/tmp/ctext_cache_{hex_num}.html'

    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(html)
        return html
    except Exception as e:
        return None

def get_our_yao_key(pos, is_yang):
    prefix = '九' if is_yang else '六'
    if pos == 1: return '初' + prefix
    elif pos == 6: return '上' + prefix
    else:
        nums = {2:'二',3:'三',4:'四',5:'五'}
        return prefix + nums[pos]

# ─── Main verification ───
num_to_bin = {}
for b, n in HEXAGRAM_MAP.items():
    num_to_bin[n] = b

total_checked = 0
total_match = 0
total_mismatch = 0
total_fetch_fail = 0
mismatches = []

print("═══ 易经元数据库逐字验证 ═══")
print(f"数据源A：识典古籍（简体） → yaoci_data.py")
print(f"数据源B：ctext.org 中国哲学书电子化计划（繁体→简体）")
print(f"方法：去标点后逐字比对")
print("=" * 60)
print()

for n in range(1, 65):
    hex_name = HEXAGRAMS[n]['name']
    binary = num_to_bin[n]
    our_yaoci = YAOCI.get(n, {}).get('yaoci', {})

    # Fetch ctext page
    html = fetch_page(n)
    if not html:
        print(f"  ✗ 第{n:02d}卦 {hex_name}: 抓取失败")
        total_fetch_fail += 1
        continue

    # Extract ctext yaoci
    ctext_yaoci = extract_yaoci_from_html(html, n)

    if not ctext_yaoci:
        print(f"  ? 第{n:02d}卦 {hex_name}: 未能解析ctext页面")
        total_fetch_fail += 1
        continue

    hex_ok = True
    hex_details = []

    # Compare each yao
    for pos in range(1, 7):
        is_yang = binary[pos-1] == '1'
        key = get_our_yao_key(pos, is_yang)

        our_text = our_yaoci.get(key, '')
        # Strip position prefix from our text
        our_body = our_text
        if our_text.startswith(key):
            our_body = our_text[len(key):].lstrip('，,： ')

        ctext_text = ctext_yaoci.get(key, '')
        if ctext_text.startswith(key):
            ctext_text = ctext_text[len(key):].lstrip('，,：: ')

        # Convert traditional to simplified
        ctext_simplified = t2s(ctext_text)

        # Normalize (remove punctuation) for comparison
        our_norm = normalize(our_body)
        ct_norm = normalize(ctext_simplified)

        total_checked += 1

        if our_norm == ct_norm:
            total_match += 1
        else:
            total_mismatch += 1
            hex_ok = False
            hex_details.append(f"    {key}: 不一致")
            hex_details.append(f"      我们: {our_norm}")
            hex_details.append(f"      ctext: {ct_norm}")
            # Find specific character differences
            diffs = []
            max_len = max(len(our_norm), len(ct_norm))
            for i in range(max_len):
                a = our_norm[i] if i < len(our_norm) else '∅'
                b = ct_norm[i] if i < len(ct_norm) else '∅'
                if a != b:
                    diffs.append(f"第{i}字 '{a}'↔'{b}'")
            if diffs:
                hex_details.append(f"      差异: {', '.join(diffs[:5])}")

    # Check specials
    for skey in ['用九', '用六']:
        if skey in our_yaoci:
            our_text = our_yaoci[skey]
            if our_text.startswith(skey):
                our_text = our_text[len(skey):].lstrip('，,： ')
            ctext_text = ctext_yaoci.get(skey, '')
            if ctext_text.startswith(skey):
                ctext_text = ctext_text[len(skey):].lstrip('，,：: ')
            ctext_simplified = t2s(ctext_text)
            our_norm = normalize(our_text)
            ct_norm = normalize(ctext_simplified)
            total_checked += 1
            if our_norm == ct_norm:
                total_match += 1
            else:
                total_mismatch += 1
                hex_ok = False
                hex_details.append(f"    {skey}: 不一致")
                hex_details.append(f"      我们: {our_norm}")
                hex_details.append(f"      ctext: {ct_norm}")

    if hex_ok:
        print(f"  ✓ 第{n:02d}卦 {hex_name}: 全部一致 ({len(ctext_yaoci)}条)")
    else:
        print(f"  ✗ 第{n:02d}卦 {hex_name}: 有差异")
        for d in hex_details:
            print(d)
        mismatches.append(n)

    time.sleep(0.3)  # Be nice to the server

print()
print("═══ 验证结果 ═══")
print(f"  检验条数: {total_checked}")
print(f"  完全一致: {total_match}")
print(f"  有差异:   {total_mismatch}")
print(f"  抓取失败: {total_fetch_fail}")
print(f"  一致率:   {total_match/total_checked*100:.1f}%" if total_checked > 0 else "")
if mismatches:
    print(f"  有差异的卦: {[HEXAGRAMS[n]['name'] for n in mismatches]}")
print()
if total_mismatch == 0 and total_fetch_fail == 0:
    print("  ★ 结论：386条爻辞与ctext.org逐字完全一致（去标点后）")
elif total_mismatch > 0:
    print(f"  ★ 结论：{total_mismatch}条存在文字差异，需逐条核查")
    print("    注意：差异可能来自版本不同（王弼注 vs 其他版本），不一定是错误")
