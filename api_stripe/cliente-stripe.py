from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from key_config import URL_BASE, STRIPE_WEBHOOK_SECRET, API_KEY_STRIPE

app = FastAPI()

class PaymentRequest(BaseModel):
    email: str

@app.post("/create-payment-intent/")
async def create_payment_intent(payment_request: PaymentRequest):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=1957,  # Valor em centavos
            currency="brl",
            receipt_email=payment_request.email,
        )
        return {"client_secret": payment_intent["client_secret"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
