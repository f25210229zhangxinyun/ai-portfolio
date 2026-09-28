import csv
import os

# 数据文件路径：桌面下data文件夹中的生词表.csv
DATA = os.path.join("data", "生词表.csv")

# ①读取csv生词表
def load_words(path=DATA):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

# ②筛选指定HSK等级词汇，默认筛选HSK4
def filter_by_level(words, level="4"):
    return [w for w in words
            if str(w["HSK等级"]) == str(level)]

# ③统计各类词性出现数量
def count_by_pos(words):
    pos_dict = {}
    for w in words:
        pos_dict[w["词性"]] = pos_dict.get(w["词性"], 0) + 1
    return pos_dict

# ④生成练习题，输出到桌面练习.txt
def gen_exercises(words, out="练习.txt"):
    with open(out, "w", encoding="utf-8") as f:
        for w in words:
            f.write(f'用“{w["词汇"]}”造一个句子。（{w["词性"]}）\n')


if __name__ == "__main__":
    all_words = load_words()
    hsk4_words = filter_by_level(all_words, "4")
    pos_result = count_by_pos(hsk4_words)

    print(f"总词汇：{len(all_words)}个，其中HSK4词汇 {len(hsk4_words)} 个")
    print("词性分布：", pos_result)

    gen_exercises(hsk4_words)
    print("✅已生成：练习.txt")