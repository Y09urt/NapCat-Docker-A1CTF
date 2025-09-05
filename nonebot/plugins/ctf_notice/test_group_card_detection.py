#!/usr/bin/env python3
"""
群卡片广告检测功能测试
"""

import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ad_detector import detect_advertisement, detect_group_card_advertisement

def test_group_card_detection():
    """测试群卡片检测功能"""
    
    print("=" * 60)
    print("🧪 群卡片广告检测功能测试")
    print("=" * 60)
    
    # 测试用的群卡片数据
    test_messages = [
        # 完整的群卡片JSON格式 - 应该被检测为广告
        '[CQ:json,data={"app":"com.tencent.contact.lua","desc":"","view":"contact","ver":"0.0.0.1","prompt":"推荐群聊: 2025级大一新生通知群","config":{"autosize":true,"ctime":1693234567,"token":"xxxx"},"meta":{"contact":{"action":"","scene":"","tag":"群聊推荐"}}}]',
        
        # 另一种群卡片格式 - 应该被检测为广告
        '[CQ:json,data={"app":"com.tencent.structmsg","desc":"","view":"contact","ver":"1.0.0.1","prompt":"邀请你加入群聊: 大一新生答疑群","config":{"autosize":true},"meta":{"contact":{"action":"add_group","group_id":"123456789","group_name":"大一新生答疑群"}}}]',
        
        # 直接的JSON数据 - 应该被检测为广告
        '{"app":"com.tencent.contact.lua","prompt":"推荐群聊: 新生军训通知群","view":"contact","ver":"0.0.0.1","meta":{"contact":{"group_name":"新生军训通知群"}}}',
        
        # 正常的群卡片（非新生相关） - 风险较低
        '[CQ:json,data={"app":"com.tencent.contact.lua","desc":"","view":"contact","ver":"0.0.0.1","prompt":"推荐群聊: 编程学习交流群","config":{"autosize":true},"meta":{"contact":{"group_name":"编程学习交流群"}}}]',
        
        # 普通文本广告 - 应该被检测为广告
        '⚠️ 紧急通知！！！新生群即将解散，务必进群：123456789，错过重要通知后果自负！',
        
        # 正常文本消息 - 不应该被检测为广告
        '大家好，这是一条正常的群聊消息，讨论学习内容。'
    ]
    
    test_descriptions = [
        "新生通知群卡片（高风险）",
        "新生答疑群卡片（高风险）", 
        "军训通知群JSON（高风险）",
        "编程学习群卡片（低风险）",
        "普通文本广告（高风险）",
        "正常群聊消息（无风险）"
    ]
    
    for i, (message, description) in enumerate(zip(test_messages, test_descriptions)):
        print(f"\n🔍 测试 {i+1}: {description}")
        print("-" * 40)
        
        # 执行检测
        is_ad, result = detect_advertisement(message)
        
        # 显示检测结果
        print(f"📄 消息内容: {message[:80]}{'...' if len(message) > 80 else ''}")
        print(f"🎯 检测结果: {'🚨 疑似广告' if is_ad else '✅ 正常消息'}")
        print(f"📊 置信度: {result['confidence']:.2f}")
        
        if result.get('is_group_card'):
            print("📱 消息类型: 群聊邀请卡片")
            card_info = result.get('card_info', {})
            if card_info.get('group_name'):
                print(f"🎯 推广群聊: {card_info['group_name']}")
        else:
            print("📱 消息类型: 普通文本")
        
        if result['reasons']:
            print(f"🔍 检测原因:")
            for reason in result['reasons']:
                print(f"  • {reason}")
        
        # 显示关键词匹配（如果有）
        if 'keyword_matches' in result:
            matches = result['keyword_matches']
            if any(matches.values()):
                print(f"🔑 关键词匹配:")
                if matches.get('high_risk'):
                    print(f"  • 高风险: {', '.join(matches['high_risk'])}")
                if matches.get('medium_risk'):
                    print(f"  • 中风险: {', '.join(matches['medium_risk'])}")
                if matches.get('urgency'):
                    print(f"  • 紧迫性: {', '.join(matches['urgency'])}")
                if matches.get('group_numbers'):
                    print(f"  • 群号: {', '.join(matches['group_numbers'])}")

def test_group_card_only():
    """专门测试群卡片检测函数"""
    
    print("\n" + "=" * 60)
    print("🧪 群卡片专项检测测试")
    print("=" * 60)
    
    test_cases = [
        # CQ码格式的群卡片
        '[CQ:json,data={"app":"com.tencent.contact.lua","prompt":"推荐群聊: 2025级新生通知群"}]',
        
        # 纯JSON格式
        '{"app":"com.tencent.contact.lua","prompt":"邀请你加入群聊: 大一新生群"}',
        
        # 非群卡片消息
        '这是一条普通的文本消息，不包含群卡片',
        
        # 包含群卡片标识但JSON格式错误
        '[CQ:json,data={"app":"com.tencent.contact.lua","prompt":"推荐群聊: 编程学习群"',
    ]
    
    for i, message in enumerate(test_cases):
        print(f"\n🔍 群卡片测试 {i+1}:")
        print("-" * 30)
        print(f"📄 消息: {message[:60]}{'...' if len(message) > 60 else ''}")
        
        is_ad, result = detect_group_card_advertisement(message)
        
        print(f"📱 是否群卡片: {'✅' if result['is_group_card'] else '❌'}")
        print(f"🚨 是否广告: {'✅' if is_ad else '❌'}")
        print(f"📊 置信度: {result['confidence']:.2f}")
        
        if result['reasons']:
            print(f"🔍 原因: {', '.join(result['reasons'])}")

if __name__ == "__main__":
    try:
        test_group_card_detection()
        test_group_card_only()
        
        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
