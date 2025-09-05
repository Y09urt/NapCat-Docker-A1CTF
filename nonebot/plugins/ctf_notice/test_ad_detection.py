"""
测试广告检测功能
"""

# 导入检测函数
import sys
import os
sys.path.append(os.path.dirname(__file__))

from ad_detector import detect_advertisement, log_ad_detection, get_ad_detection_summary

def test_message(msg_desc, message):
    """测试单条消息"""
    print(f"\n📝 测试: {msg_desc}")
    print(f"� 消息: {message}")
    print("-" * 60)
    
    # 执行检测
    is_ad, result = detect_advertisement(message)
    
    print(f"🎯 检测结果: {'🚨 广告' if is_ad else '✅ 正常'}")
    print(f"📊 置信度: {result['confidence']:.2f}")
    if result['reasons']:
        print(f"📋 检测原因: {', '.join(result['reasons'])}")
    
    print("🔍 关键词匹配详情:")
    for category, matches in result['keyword_matches'].items():
        if matches:
            print(f"  • {category}: {matches}")
    
    return is_ad, result

# 测试用例
test_cases = [
    ("用户提供的广告消息", "还没加新生通知群的同学抓紧加一下❗无广，正规校群！（新生答疑、入学生会、加社团、转专业、军训事宜，重要通知事项等）"),
    ("带群号的广告", "抓紧加新生群 123456789 无广告正规校群！军训通知转专业等"),
    ("正常消息测试", "今天的CTF比赛很有趣，大家一起来参加吧！"),
    ("边界测试", "新生请注意，学校有重要通知"),
    ("高风险词汇测试", "紧急通知！！！务必进群，后果自负！"),
]

print("🧪 广告检测功能测试")
print("=" * 80)

# 显示配置摘要
print(get_ad_detection_summary())
print("=" * 80)

# 执行测试
for desc, message in test_cases:
    test_message(desc, message)

print("\n" + "=" * 80)
print("✅ 所有测试完成")
