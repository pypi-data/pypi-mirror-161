
# 差异 查看修改内容
import difflib


def dff_text(a, b):
    """
    统计计算文本的 差异


    :param a: # 原始文本
    :param b: # 新文本
    :return:
    """
    #     a = "qabxcd"
    #     b = "abycdf"
    s = difflib.SequenceMatcher(None, a, b)

    text = []
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        # print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(
        #     tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2]))

        if tag == 'equal':
            text.append(a[i1:i2])
        elif tag == 'replace':
            text.append(f"<span class='del {tag}'>{a[i1:i2]}</span><span class='add {tag}'>{b[j1:j2]}</span>")
        elif tag == 'delete':
            text.append(f"<span class='del {tag}'>{a[i1:i2]}</span>")
        elif tag == 'insert':
            text.append(f"<span class='add {tag}'>{b[j1:j2]}</span>")
        else:
            pass
    # print("".join(text))
    return "".join(text)
