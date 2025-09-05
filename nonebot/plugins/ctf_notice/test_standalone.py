#!/usr/bin/env python3
"""
群卡片广告检测功能独立测试
不依赖nonebot环境
"""

import re
import json
from typing import Dict, List, Tuple

# 配置 (从config.py复制)
AD_DETECTION_CONFIG = {
    "auto_delete": True,
    "delete_threshold": 0.7,
    "warning_threshold": 0.5,
    "high_risk_keywords": [
        "广告泛滥", "即将解散", "作废", "紧急通知！！！", 
        "务必进群", "后果自负", "最后一次提醒", "抓紧进群",
        "已报备，管理勿撤回", "导员让转发", "错过重要通知后果自负"
    ],
    "group_number_pattern": r"\b\d{8,12}\b",
    "medium_risk_keywords": [
        "转移", "新群", "官方群", "通知群", "新生群",
        "军训通知", "新生宿舍", "开学时间", "转换专业",
        "十点前", "抓紧时间", "统计人数", "签到信息"
    ],
    "urgency_keywords": [
        "紧急", "立即", "马上", "抓紧", "务必", 
        "最后", "截止", "过期", "后果自负"
    ],
    "detection_threshold": {
        "high_risk_count": 1,
        "medium_risk_count": 3,
        "urgency_count": 2,
        "has_group_number": True
    },
    "group_card_detection": {
        "card_app_identifiers": [
            "com.tencent.contact.lua",
            "com.tencent.structmsg"
        ],
        "card_prompt_patterns": [
            r"推荐群聊[：:]\s*(.+)",
            r"邀请你加入群聊[：:]\s*(.+)",
            r"群聊推荐[：:]\s*(.+)",
            r"加入群聊[：:]\s*(.+)"
        ],
        "card_high_risk_keywords": [
            "新生", "大一", "新生群", "新生通知群", "通知群", "答疑群",
            "班级群", "学院群", "校群", "军训通知", "开学通知", "转专业群",
            "2025级", "大一新生", "新生宿舍", "新生军训"
        ],
        "card_instant_ad_patterns": [
            r"2025级.*新生.*群",
            r"新生.*通知.*群", 
            r"军训.*通知.*群",
            r"大一.*新生.*群",
            r"新生.*答疑.*群"
        ],
        "card_detection_threshold": 0.6,
        "card_delete_threshold": 0.6
    }
}

def detect_group_card_advertisement(message: str) -> Tuple[bool, Dict]:
    """检测群卡片邀请是否为广告"""
    detection_result = {
        "is_group_card": False,
        "is_ad": False,
        "confidence": 0.0,
        "reasons": [],
        "card_info": {}
    }
    
    card_config = AD_DETECTION_CONFIG.get("group_card_detection", {})
    
    # 检查是否包含群卡片相关内容
    if not any(indicator in message for indicator in ["[CQ:json", "com.tencent.contact", "com.tencent.structmsg"]):
        return False, detection_result
    
    # 检测是否为群卡片消息
    card_data = None
    
    # 方法1: 检测CQ码中的json参数  
    cq_json_match = re.search(r'\[CQ:json,data=({.*})\]', message)
    if cq_json_match:
        try:
            card_data = json.loads(cq_json_match.group(1))
            detection_result["is_group_card"] = True
        except json.JSONDecodeError:
            pass
    
    # 方法2: 尝试解析整个消息作为JSON
    if not card_data and message.strip().startswith('{') and message.strip().endswith('}'):
        try:
            card_data = json.loads(message.strip())
            detection_result["is_group_card"] = True
        except json.JSONDecodeError:
            pass
    
    if not card_data:
        return False, detection_result

    # 检查是否为群卡片类型
    app_name = card_data.get("app", "")
    if app_name not in card_config.get("card_app_identifiers", []):
        return False, detection_result
    
    detection_result["card_info"]["app"] = app_name
    detection_result["reasons"].append(f"群卡片类型: {app_name}")
    detection_result["confidence"] += 0.3
    
    # 提取群卡片信息
    prompt = card_data.get("prompt", "")
    detection_result["card_info"]["prompt"] = prompt
    
    # 分析prompt中的群信息
    group_name = prompt
    for pattern in card_config.get("card_prompt_patterns", []):
        match = re.search(pattern, prompt)
        if match:
            group_name = match.group(1).strip()
            detection_result["reasons"].append(f"匹配提示模式: {pattern.split('(')[0]}")
            detection_result["confidence"] += 0.25
            break
    
    detection_result["card_info"]["group_name"] = group_name
    
    # 检测直接判定为广告的模式
    for pattern in card_config.get("card_instant_ad_patterns", []):
        if re.search(pattern, prompt, re.IGNORECASE) or re.search(pattern, group_name, re.IGNORECASE):
            detection_result["is_ad"] = True
            detection_result["confidence"] = 0.95
            detection_result["reasons"].append(f"即时广告模式: {pattern}")
            return True, detection_result
    
    # 检测高风险关键词
    matched_keywords = []
    
    for keyword in card_config.get("card_high_risk_keywords", []):
        if keyword.lower() in prompt.lower() or keyword.lower() in group_name.lower():
            detection_result["confidence"] += 0.15
            matched_keywords.append(keyword)
    
    if matched_keywords:
        detection_result["reasons"].append(f"包含{len(matched_keywords)}个高风险关键词: {matched_keywords[:3]}")
    
    # 应用群卡片检测阈值
    card_threshold = card_config.get("card_detection_threshold", 0.6)
    if detection_result["confidence"] >= card_threshold:
        detection_result["is_ad"] = True
        detection_result["reasons"].append(f"置信度达到群卡片阈值({card_threshold})")
    
    # 确保置信度不超过1.0
    detection_result["confidence"] = min(detection_result["confidence"], 1.0)
    
    return detection_result["is_ad"], detection_result

def detect_advertisement(message: str) -> Tuple[bool, Dict]:
    """检测消息是否为广告（包括普通文本和群卡片）"""
    # 首先尝试群卡片检测
    is_group_card_ad, group_card_result = detect_group_card_advertisement(message)
    
    if group_card_result["is_group_card"]:
        # 如果是群卡片，直接返回群卡片检测结果
        return is_group_card_ad, group_card_result
    
    # 如果不是群卡片，执行常规文本广告检测
    message_lower = message.lower()
    detection_result = {
        "is_ad": False,
        "confidence": 0.0,
        "reasons": [],
        "keyword_matches": {
            "high_risk": [],
            "medium_risk": [],
            "urgency": [],
            "group_numbers": []
        }
    }
    
    # 检测高风险关键词
    high_risk_count = 0
    for keyword in AD_DETECTION_CONFIG["high_risk_keywords"]:
        if keyword.lower() in message_lower:
            high_risk_count += 1
            detection_result["keyword_matches"]["high_risk"].append(keyword)
    
    # 检测群号模式
    group_pattern = AD_DETECTION_CONFIG["group_number_pattern"]
    group_numbers = re.findall(group_pattern, message)
    if group_numbers:
        detection_result["keyword_matches"]["group_numbers"] = group_numbers
    
    # 检测中风险关键词
    medium_risk_count = 0
    for keyword in AD_DETECTION_CONFIG["medium_risk_keywords"]:
        if keyword.lower() in message_lower:
            medium_risk_count += 1
            detection_result["keyword_matches"]["medium_risk"].append(keyword)
    
    # 检测紧迫性关键词
    urgency_count = 0
    for keyword in AD_DETECTION_CONFIG["urgency_keywords"]:
        if keyword.lower() in message_lower:
            urgency_count += 1
            detection_result["keyword_matches"]["urgency"].append(keyword)
    
    # 判定逻辑
    threshold = AD_DETECTION_CONFIG["detection_threshold"]
    
    # 高风险词汇判定
    if high_risk_count >= threshold["high_risk_count"]:
        detection_result["is_ad"] = True
        detection_result["confidence"] += 0.8
        detection_result["reasons"].append(f"包含{high_risk_count}个高风险关键词")
    
    # 群号 + 其他条件判定
    if group_numbers:
        base_score = 0.3
        detection_result["confidence"] += base_score
        detection_result["reasons"].append(f"包含{len(group_numbers)}个疑似群号")
        
        # 群号 + 中风险词汇
        if medium_risk_count >= threshold["medium_risk_count"]:
            detection_result["is_ad"] = True
            detection_result["confidence"] += 0.4
            detection_result["reasons"].append(f"群号+{medium_risk_count}个中风险关键词")
        
        # 群号 + 紧迫性词汇
        if urgency_count >= threshold["urgency_count"]:
            detection_result["is_ad"] = True
            detection_result["confidence"] += 0.3
            detection_result["reasons"].append(f"群号+{urgency_count}个紧迫性关键词")
    
    # 多个感叹号判定（广告常见特征）
    exclamation_count = message.count('！') + message.count('!')
    if exclamation_count >= 6:
        detection_result["confidence"] += 0.2
        detection_result["reasons"].append(f"包含{exclamation_count}个感叹号")
        
        if detection_result["confidence"] >= 0.6:
            detection_result["is_ad"] = True
    
    # 确保置信度不超过1.0
    detection_result["confidence"] = min(detection_result["confidence"], 1.0)
    
    return detection_result["is_ad"], detection_result

def test_integration():
    """集成测试"""
    
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

if __name__ == "__main__":
    try:
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
