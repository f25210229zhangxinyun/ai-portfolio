import csv
import os
from collections import defaultdict  # 作业1新增导入

# 获取当前py文件所在文件夹（关键！解决找不到文件的问题）
BASE_DIR = os.path.dirname(__file__)
DATA = os.path.join(BASE_DIR, "data", "生词表.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "练习.txt")

# 读取csv生词表
def load_words(path=DATA):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

# 筛选指定HSK等级词汇，默认筛选HSK4
def filter_by_level(words, level="4"):
    return [w for w in words if str(w["HSK等级"]) == str(level)]

# 统计各类词性出现数量【作业1：修改为defaultdict版本】
def count_by_pos(words):
    pos_dict = defaultdict(int)
    for w in words:
        pos = w["词性"]
        pos_dict[pos] += 1
    return dict(pos_dict)

# 【作业2新增】按词性分组词汇
def group_by_pos(words):
    group = defaultdict(list)
    for w in words:
        group[w["词性"]].append(w)
    return group

# 生成练习题【更新：按词性分组输出，文件固定输出到py同目录】
def gen_exercises(words, out_path=OUTPUT_FILE):
    pos_groups = group_by_pos(words)
    with open(out_path, "w", encoding="utf-8") as f:
        # 循环每一个词性分组
        for pos, word_list in pos_groups.items():
            f.write(f"=====【{pos}】=====\n")
            for w in word_list:
                f.write(f'用“{w["词汇"]}”造一个句子。（{w["词性"]}）\n')

if __name__ == "__main__":
    print("当前脚本所在目录：", BASE_DIR)
    all_words = load_words()
    hsk4_words = filter_by_level(all_words, "4")
    pos_result = count_by_pos(hsk4_words)
    gen_exercises(hsk4_words)
    print(f"总词汇：{len(all_words)}个，其中HSK4词汇 {len(hsk4_words)} 个")
    print("词性分布：", pos_result)
    print(f"✅练习文件已经生成在这里：{OUTPUT_FILE}")