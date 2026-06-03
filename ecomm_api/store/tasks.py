from celery import shared_task
from django.core.mail import send_mail


@shared_task(name="ecomm_api.store.tasks.send_order_confirmation")
def send_order_confirmation(order_id, user_email, total):
    """
    Runs in background — sends confirmation email after order is placed.
    User gets instant response, this happens separately.
    """
    subject = f"Order #{order_id} Confirmed!"
    message = f"""
    Hi there!

    Your order has been confirmed.

    Order ID: #{order_id}
    Total: ₹{total}

    We'll notify you when it ships.

    Thanks for shopping with us!
    """

    send_mail(
        subject=subject,
        message=message,
        from_email="noreply@ecommapi.com",
        recipient_list=[user_email],
        fail_silently=True,  # don't crash if email fails
    )

    return f"Email sent for order #{order_id}"  # this shows in Celery logs
