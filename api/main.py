from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.app.cart.routes import router as cart_router
from api.app.common.database import create_db_and_tables
from api.app.company.routes import router as company_router
from api.app.gastronomy.routes import router as cuisine_router
from api.app.product.routes import router as product_router
from api.app.user.routes import router as users_router
from api.app.wishlist.routes import router as wishlist_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:  # type: ignore
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router, prefix="/users", tags=["user"])
app.include_router(cuisine_router, prefix="/gastronomy", tags=["gastronomy"])
app.include_router(company_router, prefix="/company", tags=["company"])
app.include_router(product_router, prefix="/product", tags=["product"])
app.include_router(cart_router, prefix="/cart", tags=["card"])
app.include_router(wishlist_router, prefix="/wishlist", tags=["wishlist"])


import stripe
from fastapi import FastAPI

app = FastAPI()

# Настройки
STRIPE_API_KEY = ""
STRIPE_WEBHOOK_SECRET = ""

stripe.api_key = STRIPE_API_KEY


# @app.post("/webhook")
# async def webhook(request: Request):
#     payload = await request.body()
#     sig_header = request.headers.get("stripe-signature")

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, STRIPE_WEBHOOK_SECRET
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail="Invalid payload")
#     except stripe.error.SignatureVerificationError as e:

#         raise HTTPException(status_code=400, detail="Invalid signature")

#     # Проверка успешной оплаты
#     if event["type"] == "checkout.session.completed":
#         session = event["data"]["object"]
#         user_id = session.get("client_reference_id")
#         if not user_id:
#             return {"status": "no user ID"}

#         await bot.send_message(user_id, "success")

#     return {"status": "success"}
