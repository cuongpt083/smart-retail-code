"""
Zalo Messaging Integration - Send campaigns and recommendations

Handles:
- Authentication with Zalo API
- Message templates for each RFM segment
- Sending product recommendations & campaigns
- Message tracking & delivery status
- Campaign analytics
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import sqlite3

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SegmentType(Enum):
    """RFM Segment types"""
    CHAMPIONS = "Champions"
    POTENTIAL = "Potential"
    LOYAL = "Loyal"
    LOST = "Lost"


class ZaloMessenger:
    """Zalo API client for sending messages and campaigns"""

    BASE_URL = "https://openapi.zalo.me/v2.0"

    def __init__(
        self,
        access_token: str,
        db_path: str = "retail.db"
    ):
        """
        Initialize Zalo messenger

        Args:
            access_token: Your Zalo OA access token
            db_path: SQLite database for tracking
        """
        self.access_token = access_token
        self.db_path = db_path
        self.headers = {
            "access_token": access_token,
            "Content-Type": "application/json",
        }

        # Message templates for each segment
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Dict]:
        """Load message templates for each segment"""
        return {
            SegmentType.CHAMPIONS.value: {
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
            SegmentType.POTENTIAL.value: {
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
            SegmentType.LOYAL.value: {
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
            SegmentType.LOST.value: {
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

    # ========================================================================
    # SEND MESSAGE
    # ========================================================================

    def send_message(
        self,
        customer_id: str,
        customer_phone: str,
        message: str,
        message_type: str = "text"
    ) -> Dict:
        """
        Send a message to customer via Zalo

        Args:
            customer_id: Customer ID
            customer_phone: Customer phone number
            message: Message text
            message_type: "text", "template", or "image"

        Returns:
            Response dict with message_id, status, etc
        """
        try:
            payload = {
                "phone": customer_phone,
                "message": message,
                "type": message_type,
            }

            response = requests.post(
                f"{self.BASE_URL}/message/sendtext",
                headers=self.headers,
                json=payload,
                timeout=10
            )

            response.raise_for_status()
            result = response.json()

            if result.get("error") == 0:
                logger.info(f"Message sent to {customer_phone}")
                return {
                    "success": True,
                    "message_id": result.get("data", {}).get("message_id"),
                    "customer_id": customer_id,
                    "phone": customer_phone,
                    "sent_at": datetime.now().isoformat(),
                }
            else:
                logger.error(f"Zalo error: {result.get('message')}")
                return {
                    "success": False,
                    "error": result.get("message"),
                }

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    # ========================================================================
    # SEGMENT CAMPAIGNS
    # ========================================================================

    def send_segment_campaign(
        self,
        segment: SegmentType,
        customers: List[Dict],
        recommendations: Optional[List[str]] = None
    ) -> Dict:
        """
        Send campaign message to all customers in a segment

        Args:
            segment: RFM segment type
            customers: List of customer dicts with id, name, dien_thoai
            recommendations: Product recommendations for the segment

        Returns:
            Campaign result with sent count, failures, etc
        """
        template = self.templates.get(segment.value)
        if not template:
            return {"success": False, "error": f"Unknown segment: {segment}"}

        results = {
            "segment": segment.value,
            "sent": 0,
            "failed": 0,
            "errors": [],
            "message_ids": [],
        }

        rec_str = self._format_recommendations(recommendations)

        for customer in customers:
            try:
                # Format message
                body = template["body"].format(
                    customer_name=customer.get("ten_khach_hang", "Friend"),
                    recommendations=rec_str
                )

                # Send message
                response = self.send_message(
                    customer_id=customer.get("ma_khach_hang"),
                    customer_phone=customer.get("dien_thoai"),
                    message=body
                )

                if response.get("success"):
                    results["sent"] += 1
                    results["message_ids"].append(response.get("message_id"))
                else:
                    results["failed"] += 1
                    results["errors"].append(response.get("error"))

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))
                logger.error(f"Error sending to customer {customer.get('ma_khach_hang')}: {e}")

        logger.info(f"Campaign '{segment.value}' complete: {results['sent']} sent, {results['failed']} failed")
        return results

    def _format_recommendations(self, recommendations: Optional[List[str]]) -> str:
        """Format product recommendations for message"""
        if not recommendations:
            recommendations = ["Bánh mì", "Nước", "Gia vị"]

        return "\n".join([f"• {prod}" for prod in recommendations[:5]])

    # ========================================================================
    # PRODUCT RECOMMENDATIONS
    # ========================================================================

    def send_product_recommendation(
        self,
        customer_id: str,
        customer_phone: str,
        customer_name: str,
        products: List[Dict]
    ) -> Dict:
        """
        Send personalized product recommendation

        Args:
            customer_id: Customer ID
            customer_phone: Customer phone
            customer_name: Customer name
            products: List of product dicts with name, price, etc

        Returns:
            Send result
        """
        try:
            product_list = "\n".join([
                f"• {p['ten_hang']} - {p['gia_ban']:,.0f} VND"
                for p in products[:5]
            ])

            message = f"""Xin chào {customer_name}!

Dựa trên lịch sử mua hàng của bạn, chúng tôi gợi ý:

{product_list}

Hãy ghé cửa hàng hoặc nhắn tin để đặt hàng!

Smart Retail Team"""

            return self.send_message(customer_id, customer_phone, message)

        except Exception as e:
            logger.error(f"Error sending recommendations: {e}")
            return {"success": False, "error": str(e)}

    # ========================================================================
    # TRACKING & ANALYTICS
    # ========================================================================

    def track_campaign(
        self,
        campaign_id: str,
        segment: str,
        sent_count: int,
        success_count: int
    ) -> Dict:
        """
        Track campaign performance in database

        Args:
            campaign_id: Unique campaign ID
            segment: RFM segment
            sent_count: Total messages sent
            success_count: Successfully delivered

        Returns:
            Track result
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create campaigns table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    campaign_id TEXT PRIMARY KEY,
                    segment TEXT,
                    sent_at TIMESTAMP,
                    sent_count INTEGER,
                    success_count INTEGER,
                    failure_count INTEGER,
                    success_rate REAL
                )
            """)

            failure_count = sent_count - success_count
            success_rate = success_count / sent_count if sent_count > 0 else 0

            cursor.execute("""
                INSERT INTO campaigns
                (campaign_id, segment, sent_at, sent_count, success_count, failure_count, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                campaign_id,
                segment,
                datetime.now().isoformat(),
                sent_count,
                success_count,
                failure_count,
                success_rate
            ))

            conn.commit()
            conn.close()

            logger.info(f"Campaign {campaign_id} tracked: {success_rate:.0%} success")

            return {
                "success": True,
                "campaign_id": campaign_id,
                "success_rate": success_rate,
            }

        except Exception as e:
            logger.error(f"Error tracking campaign: {e}")
            return {"success": False, "error": str(e)}

    def get_campaign_stats(self) -> List[Dict]:
        """Get campaign statistics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT campaign_id, segment, sent_count, success_count, success_rate, sent_at
                FROM campaigns
                ORDER BY sent_at DESC
                LIMIT 10
            """)

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "campaign_id": row[0],
                    "segment": row[1],
                    "sent_count": row[2],
                    "success_count": row[3],
                    "success_rate": row[4],
                    "sent_at": row[5],
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Error getting campaign stats: {e}")
            return []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_zalo_messenger(
    access_token: str,
    db_path: str = "retail.db"
) -> ZaloMessenger:
    """Factory function to create Zalo messenger"""
    return ZaloMessenger(access_token, db_path)


def send_campaign_to_segment(
    access_token: str,
    segment: SegmentType,
    customers: List[Dict],
    products: Optional[List[str]] = None,
    db_path: str = "retail.db"
) -> Dict:
    """
    One-shot campaign send function

    Usage:
        result = send_campaign_to_segment(
            "your_zalo_token",
            SegmentType.CHAMPIONS,
            customers_list
        )
    """
    messenger = ZaloMessenger(access_token, db_path)
    result = messenger.send_segment_campaign(segment, customers, products)
    return result
