"""
Dashboard Helper Functions - Zalo Campaign Automation Support

Provides utilities for:
- Message template loading and formatting
- Campaign tracking and history
- Recommendation extraction
- UI helpers
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


# ============================================================================
# MESSAGE TEMPLATES
# ============================================================================

def get_template_by_key(template_key: str) -> Dict[str, str]:
    """Get template by key (CHAMPIONS, POTENTIAL, LOYAL, LOST)"""
    templates = {
        "CHAMPIONS": {
            "subject": "🎁 Exclusive Rewards for VIP Members!",
            "body": """Xin chào {customer_name}!

Chúng tôi rất cảm ơn bạn là một trong những khách hàng trung thành nhất của cửa hàng.

🎉 Đặc biệt dành cho bạn:
- VIP membership & loyalty rewards
- Priority customer service
- Early access to new products

💝 Recommended for you:
{recommendations}

Hãy ghé cửa hàng hoặc nhắn tin để nhận ưu đãi!

Best regards,
Smart Retail Team""",
            "button_text": "Xem ưu đãi"
        },
        "POTENTIAL": {
            "subject": "🌟 Khám phá sản phẩm mới dành cho bạn",
            "body": """Chào {customer_name}!

Chúng tôi có những sản phẩm mới tuyệt vời dành cho bạn.

✨ Gợi ý sản phẩm:
{recommendations}

🎁 Lần đầu tiên mua: Giảm 10%

Truy cập để xem thêm chi tiết!

Thanks,
Smart Retail Team""",
            "button_text": "Xem sản phẩm"
        },
        "LOYAL": {
            "subject": "👋 Chúng tôi nhớ bạn! Quay lại nhé",
            "body": """Chào {customer_name}!

Đã lâu không thấy bạn. Chúng tôi có những điều thú vị dành cho bạn!

🎯 Top products you loved:
{recommendations}

💰 Special offer: 15% off on selected items

Quay lại nhé! Chúng tôi sẽ rất vui.

Warmly,
Smart Retail Team""",
            "button_text": "Mua ngay"
        },
        "LOST": {
            "subject": "🙏 Chúng tôi muốn có bạn trở lại",
            "body": """Chào {customer_name}!

Chúng tôi nhận ra rằng bạn đã không mua hàng từ lâu.

🎊 Nhân dịp này, chúng tôi có:
- 20% discount on all items
- Free shipping
- Special gift with first purchase

🎁 New products you might like:
{recommendations}

Hãy cho chúng tôi một cơ hội!

Sincerely,
Smart Retail Team""",
            "button_text": "Quay lại"
        }
    }
    return templates.get(template_key.upper(), templates["POTENTIAL"])


def format_message(
    template_key: str,
    customer_name: str,
    recommendations: Optional[List[str]] = None
) -> str:
    """
    Format message template with customer data

    Args:
        template_key: CHAMPIONS, POTENTIAL, LOYAL, or LOST
        customer_name: Customer name for personalization
        recommendations: List of product recommendations

    Returns:
        Formatted message body
    """
    if recommendations is None:
        recommendations = ["Sản phẩm 1", "Sản phẩm 2", "Sản phẩm 3"]

    template = get_template_by_key(template_key)

    # Format recommendations as bullet list
    rec_text = "\n".join([f"• {rec}" for rec in recommendations[:5]])

    # Format message
    message = template["body"].format(
        customer_name=customer_name,
        recommendations=rec_text
    )

    return message


# ============================================================================
# PRODUCT RECOMMENDATIONS
# ============================================================================

def extract_recommendations(segment: str) -> List[str]:
    """
    Get recommended products for segment

    Args:
        segment: RFM segment (Champions, Potential, Loyal, Lost)

    Returns:
        List of product names for recommendations
    """
    recommendations = {
        "Champions": [
            "Premium Product A",
            "Exclusive Service B",
            "VIP Bundle C"
        ],
        "Potential": [
            "Popular Product X",
            "Trending Item Y",
            "Special Offer Z"
        ],
        "Loyal": [
            "Your Favorite Category",
            "New Arrivals",
            "Bestsellers"
        ],
        "Lost": [
            "Limited Time Offer",
            "Customer Favorite",
            "Best Seller"
        ]
    }

    return recommendations.get(segment, recommendations["Potential"])


# ============================================================================
# CAMPAIGN TRACKING
# ============================================================================

def get_campaign_summary(stats: List[Dict]) -> Dict:
    """
    Generate summary statistics from campaign stats

    Args:
        stats: Campaign stats from database

    Returns:
        Dictionary with aggregated metrics
    """
    if not stats:
        return {
            "total_campaigns": 0,
            "total_sent": 0,
            "total_success": 0,
            "avg_success_rate": 0.0
        }

    df = pd.DataFrame(stats)

    return {
        "total_campaigns": len(df),
        "total_sent": df['sent_count'].sum(),
        "total_success": df['success_count'].sum(),
        "avg_success_rate": (
            df['success_count'].sum() / df['sent_count'].sum() * 100
            if df['sent_count'].sum() > 0 else 0
        ),
        "by_segment": df.groupby('segment').agg({
            'sent_count': 'sum',
            'success_count': 'sum'
        }).to_dict('index')
    }


# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def format_phone(phone: str) -> str:
    """Format phone number (Vietnamese format)"""
    # Remove non-digits
    phone = ''.join(filter(str.isdigit, phone))

    # Ensure 10 digits (Vietnamese standard)
    if len(phone) == 9:
        phone = "0" + phone

    return phone


def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return timestamp


def format_success_rate(count: float, total: int) -> str:
    """Format success rate as percentage"""
    if total == 0:
        return "0%"
    rate = (count / total) * 100
    return f"{rate:.0f}%"


# ============================================================================
# VALIDATION
# ============================================================================

def validate_segment(segment: str) -> bool:
    """Check if segment is valid"""
    return segment in ["Champions", "Potential", "Loyal", "Lost"]


def validate_customers_list(customers: List[Dict]) -> bool:
    """Validate customer list format"""
    if not customers:
        return False

    required_fields = ['ma_khach_hang', 'ten_khach_hang', 'dien_thoai']
    for customer in customers:
        for field in required_fields:
            if field not in customer:
                return False

    return True


# ============================================================================
# LOGGING HELPERS
# ============================================================================

def log_campaign_start(segment: str, customer_count: int):
    """Log campaign start"""
    logger.info(
        f"campaign_start",
        extra={
            "segment": segment,
            "customer_count": customer_count,
            "timestamp": datetime.now().isoformat()
        }
    )


def log_campaign_result(campaign_id: str, segment: str, result: Dict):
    """Log campaign result"""
    logger.info(
        f"campaign_complete",
        extra={
            "campaign_id": campaign_id,
            "segment": segment,
            "sent": result.get('sent', 0),
            "failed": result.get('failed', 0),
            "success_rate": (
                result.get('sent', 0) / (result.get('sent', 0) + result.get('failed', 0)) * 100
                if (result.get('sent', 0) + result.get('failed', 0)) > 0 else 0
            )
        }
    )


def log_campaign_error(segment: str, error: str):
    """Log campaign error"""
    logger.error(
        f"campaign_error",
        extra={
            "segment": segment,
            "error": str(error)[:200]  # Truncate long errors
        }
    )
