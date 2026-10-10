from app.db.session import Base, engine, SessionLocal
from app.db.models import User, Order
from app.core.security import hash_password, verify_password
from logger import get_logger
from exception import CustomException

logger = get_logger(__name__)

def main():
    demo_email = "demo@safeassist.com"
    legacy_email = "demo@safeassist.local"
    demo_password = "Demo@12345"
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(email=demo_email).first()
            legacy_user = db.query(User).filter_by(email=legacy_email).first()
            if user is None and legacy_user is not None:
                # Migrate the old demo account in-place so existing foreign keys/order IDs survive.
                legacy_user.email = demo_email
                user = legacy_user
                db.flush()
            elif user is None:
                user = User(email=demo_email, password_hash=hash_password(demo_password), is_active=True)
                db.add(user)
                db.flush()
            elif legacy_user is not None and legacy_user.id != user.id:
                # Keep the valid demo account canonical; order ownership is corrected below.
                logger.warning("Legacy demo account remains in database; canonical demo account is %s", demo_email)

            if not verify_password(demo_password, user.password_hash):
                user.password_hash = hash_password(demo_password)
            order = db.query(Order).filter_by(order_number="SA-10001").first()
            if not order:
                order = Order(order_number="SA-10001", user_id=user.id, product_name="Wireless Headphones",
                              status="shipped", amount=2499.0)
                db.add(order)
            else:
                # This seeded order belongs to the canonical demo account.
                order.user_id = user.id
            db.commit()
            print(f"Demo data ready. Demo login: {demo_email} / {demo_password} (user_id={user.id}).")
        finally:
            db.close()
    except Exception as exc:
        logger.exception("Could not seed demo data")
        raise CustomException("Demo data seeding failed", exc)

if __name__ == "__main__":
    main()
