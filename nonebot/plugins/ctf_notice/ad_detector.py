"""
广告检测模块
"""
import re
from typing import Dict, List, Tuple
from nonebot import logger

from .config import AD_DETECTION_CONFIG

def detect_advertisement(message: str) -> Tuple[bool, Dict]:
    """
    检测消息是否为广告
    
    Args:
        message: 要检测的消息内容
        
    Returns:
        Tuple[bool, Dict]: (是否为广告, 检测详情)
    """
    message_lower = message.lower()
    detection_result = {
        "is_ad": False,
        "confidence": 0.0,
        "reasons": [],
        "keyword_matches": {
            "high_risk": [],
            "medium_risk": [],
            "urgency": [],
            "disclaimer": [],
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
    
    # 检测免责声明关键词
    disclaimer_count = 0
    for keyword in AD_DETECTION_CONFIG["disclaimer_keywords"]:
        if keyword.lower() in message_lower:
            disclaimer_count += 1
            detection_result["keyword_matches"]["disclaimer"].append(keyword)
    
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
    
    # 免责声明 + 其他特征判定
    if disclaimer_count >= threshold.get("disclaimer_count", 1):
        detection_result["confidence"] += 0.4
        detection_result["reasons"].append(f"包含{disclaimer_count}个免责声明关键词")
        
        # 免责声明 + 中风险词汇
        if medium_risk_count >= 2:  # 降低阈值
            detection_result["is_ad"] = True
            detection_result["confidence"] += 0.3
            detection_result["reasons"].append(f"免责声明+{medium_risk_count}个中风险关键词")
    
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

def log_ad_detection(message: str, detection_result: Dict, user_id: str = None):
    """记录广告检测结果"""
    if detection_result["is_ad"]:
        logger.warning(f"🚨 检测到广告消息 | 置信度: {detection_result['confidence']:.2f}")
        logger.warning(f"📝 检测原因: {', '.join(detection_result['reasons'])}")
        if user_id:
            logger.warning(f"👤 发送者: {user_id}")
        logger.warning(f"📄 消息内容: {message[:100]}...")
    else:
        logger.info(f"✅ 消息检测通过 | 置信度: {detection_result['confidence']:.2f}")

def get_ad_detection_summary() -> str:
    """获取广告检测配置摘要"""
    config = AD_DETECTION_CONFIG
    return f"""🛡️ 广告检测配置摘要:
    
📋 检测规则:
• 高风险关键词: {len(config['high_risk_keywords'])} 个
• 中风险关键词: {len(config['medium_risk_keywords'])} 个  
• 紧迫性关键词: {len(config['urgency_keywords'])} 个
• 群号模式检测: 启用

⚖️ 判定阈值:
• 高风险词汇: {config['detection_threshold']['high_risk_count']} 个触发
• 中风险词汇: {config['detection_threshold']['medium_risk_count']} 个触发
• 紧迫性词汇: {config['detection_threshold']['urgency_count']} 个触发

🎯 检测策略:
• 单个高风险词汇 → 直接判定为广告
• 群号 + 多个中/低风险词汇 → 判定为广告
• 多个感叹号 + 其他特征 → 提高可疑度"""
