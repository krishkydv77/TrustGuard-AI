from sqlalchemy.orm import Session
from app.db.models import Order, RefundRequest, User
from logger import get_logger
from exception import CustomException

logger = get_logger(__name__)

def route_intent(intent: str, message: str, db: Session, user_id: int | None) -> str:
    try:
        if intent == "order_status":
            if not user_id:
                return "Please sign in first so I can securely check your order."
            order = db.query(Order).filter(Order.user_id == user_id).order_by(Order.id.desc()).first()
            if not order:
                return "I couldn't find an order linked to your account. Please verify your account or order number."
            return f"Your latest order {order.order_number} ({order.product_name}) is currently '{order.status}'."
        if intent == "refund":
            if not user_id:
                return "Please sign in first. Refund requests must be associated with your account."
            order = db.query(Order).filter(Order.user_id == user_id).order_by(Order.id.desc()).first()
            if not order:
                return "I couldn't find an order linked to your account, so I can't create a refund request yet."
            if order.status.lower() in {"refunded", "cancelled"}:
                return f"Order {order.order_number} is marked '{order.status}' and cannot be submitted for another refund."
            request = RefundRequest(order_id=order.id, user_id=user_id,
                                    reason="Customer requested refund via support chat", status="submitted")
            db.add(request)
            db.commit()
            db.refresh(request)
            logger.info("Refund request created id=%s order=%s user=%s", request.id, order.id, user_id)
            return f"Refund request #{request.id} has been submitted for order {order.order_number}. This is a request, not a completed payment reversal."
        if intent == "account":
            return "For account access, use the sign-in or password-reset flow. Never share your password or one-time code in chat."
        if intent == "product":
            return "I can help with product information. Please provide the product name or SKU you want to know about."
        if intent == "complaint":
            return "I'm sorry you're having trouble. Please describe what happened; I can log the details for support review."
        return "Hi! I can help with order status, refund requests, account access, and product questions. What would you like to do?"
    except Exception as exc:
        db.rollback()
        logger.exception("Intent agent failed: %s", intent)
        raise CustomException(f"Agent '{intent}' failed", exc)
