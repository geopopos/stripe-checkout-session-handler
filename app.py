#! /usr/bin/env python3.6
# Python 3.6 or newer required.

import json
import os
import stripe
# This is your test secret API key.
stripe_api_key = os.environ.get("STRIPE_API_KEY")
stripe.api_key = stripe_api_key

# Replace this endpoint secret with your endpoint's unique secret
# If you are testing with the CLI, find the secret by running 'stripe listen'
# If you are using an endpoint defined with the API or dashboard, look in your webhook settings
# at https://dashboard.stripe.com/webhooks
endpoint_secret = os.environ.get('STRIPE_TEST_LOCAL_SECRET')
stripe_api_key = os.environ.get("STRIPE_API_KEY")
from flask import Flask, jsonify, request

app = Flask(__name__)

# check if serverless is running offline
if os.environ.get('IS_OFFLINE') == 'True' or os.environ.get('STAGE') == 'dev':
    # set stripe api key to stripe test api key
    stripe_api_key = os.environ.get("STRIPE_TEST_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data

    try:
        event = json.loads(payload)
    except:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=False)
    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

    # Handle the event
    if event and event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']  # contains a stripe.PaymentIntent
        print('Checkout Session for {} succeeded'.format(checkout_session))
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
    elif event['type'] == 'payment_method.attached':
        payment_method = event['data']['object']  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)