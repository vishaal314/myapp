"""
Stripe Webhook Handler for Secure Payment Processing

This module handles Stripe webhooks to securely process payment events
and update the application state accordingly.
"""

import os
import json
import stripe
import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime

# Import database functions
try:
    from utils.database_manager import get_db_connection
except ImportError:
    # Fallback for development
    def get_db_connection():
        return None

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify Stripe webhook signature for security
    
    Args:
        payload: Raw webhook payload
        signature: Stripe signature from headers
        
    Returns:
        True if signature is valid, False otherwise
    """
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    if not endpoint_secret:
        st.warning("Webhook signature verification disabled - STRIPE_WEBHOOK_SECRET not configured")
        return True  # Allow for development, but warn
    
    try:
        stripe.Webhook.construct_event(payload, signature, endpoint_secret)
        return True
    except stripe.error.SignatureVerificationError:
        st.error("Invalid webhook signature")
        return False
    except Exception as e:
        st.error(f"Webhook signature verification failed: {str(e)}")
        return False

def handle_payment_succeeded(event_data: Dict[str, Any]) -> bool:
    """
    Handle successful payment webhook
    
    Args:
        event_data: Stripe event data
        
    Returns:
        True if handled successfully
    """
    try:
        payment_intent = event_data.get('object', {})
        session_id = payment_intent.get('metadata', {}).get('session_id')
        
        if not session_id:
            # Try to find session by payment intent
            sessions = stripe.checkout.Session.list(
                payment_intent=payment_intent.get('id'),
                limit=1
            )
            if sessions.data:
                session_id = sessions.data[0].id
        
        if session_id:
            # Update payment status in database
            update_payment_status(session_id, 'succeeded', payment_intent)
            
        return True
        
    except Exception as e:
        st.error(f"Error handling payment success: {str(e)}")
        return False

def handle_payment_failed(event_data: Dict[str, Any]) -> bool:
    """
    Handle failed payment webhook
    
    Args:
        event_data: Stripe event data
        
    Returns:
        True if handled successfully
    """
    try:
        payment_intent = event_data.get('object', {})
        session_id = payment_intent.get('metadata', {}).get('session_id')
        
        if session_id:
            # Update payment status in database
            update_payment_status(session_id, 'failed', payment_intent)
            
        return True
        
    except Exception as e:
        st.error(f"Error handling payment failure: {str(e)}")
        return False

def update_payment_status(session_id: str, status: str, payment_intent: Dict[str, Any]) -> bool:
    """
    Update payment status in database
    
    Args:
        session_id: Checkout session ID
        status: Payment status (succeeded, failed, etc.)
        payment_intent: Payment intent data
        
    Returns:
        True if updated successfully
    """
    try:
        conn = get_db_connection()
        if not conn:
            # Log to session state for development
            if 'webhook_logs' not in st.session_state:
                st.session_state.webhook_logs = []
            
            st.session_state.webhook_logs.append({
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id,
                'status': status,
                'amount': payment_intent.get('amount', 0) / 100,
                'currency': payment_intent.get('currency', 'eur')
            })
            return True
        
        cursor = conn.cursor()
        
        # Insert or update payment record
        cursor.execute("""
            INSERT INTO payments (
                session_id, status, amount, currency, 
                payment_intent_id, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (session_id) 
            DO UPDATE SET 
                status = EXCLUDED.status,
                updated_at = EXCLUDED.updated_at
        """, (
            session_id,
            status,
            payment_intent.get('amount', 0),
            payment_intent.get('currency', 'eur'),
            payment_intent.get('id'),
            datetime.now()
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error updating payment status: {str(e)}")
        return False

def process_webhook(payload: bytes, signature: str) -> Dict[str, Any]:
    """
    Process incoming Stripe webhook
    
    Args:
        payload: Raw webhook payload
        signature: Stripe signature
        
    Returns:
        Processing result
    """
    # Verify signature first
    if not verify_webhook_signature(payload, signature):
        return {"status": "error", "message": "Invalid signature"}
    
    try:
        # Parse event
        event = json.loads(payload.decode('utf-8'))
        event_type = event.get('type')
        event_data = event.get('data', {})
        
        # Handle different event types
        if event_type == 'payment_intent.succeeded':
            success = handle_payment_succeeded(event_data)
            return {"status": "success" if success else "error", "event_type": event_type}
            
        elif event_type == 'payment_intent.payment_failed':
            success = handle_payment_failed(event_data)
            return {"status": "success" if success else "error", "event_type": event_type}
            
        elif event_type == 'checkout.session.completed':
            # Handle checkout completion
            session = event_data.get('object', {})
            session_id = session.get('id')
            
            if session_id:
                # Mark session as completed
                update_payment_status(session_id, 'completed', session)
                
            return {"status": "success", "event_type": event_type}
            
        else:
            # Log unhandled events
            st.info(f"Received unhandled webhook event: {event_type}")
            return {"status": "ignored", "event_type": event_type}
            
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON payload"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_payment_status(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get payment status from database or session state
    
    Args:
        session_id: Checkout session ID
        
    Returns:
        Payment status information
    """
    try:
        conn = get_db_connection()
        if not conn:
            # Check session state for development
            webhook_logs = st.session_state.get('webhook_logs', [])
            for log in webhook_logs:
                if log.get('session_id') == session_id:
                    return log
            return None
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, status, amount, currency, 
                   payment_intent_id, updated_at 
            FROM payments 
            WHERE session_id = %s
        """, (session_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'session_id': result[0],
                'status': result[1],
                'amount': result[2],
                'currency': result[3],
                'payment_intent_id': result[4],
                'updated_at': result[5]
            }
        
        return None
        
    except Exception as e:
        st.error(f"Error getting payment status: {str(e)}")
        return None

def create_payment_tables():
    """
    Create payment tables if they don't exist
    """
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Create payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE,
                status VARCHAR(50),
                amount INTEGER,
                currency VARCHAR(3),
                payment_intent_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_payments_session_id 
            ON payments(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_payments_status 
            ON payments(status)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error creating payment tables: {str(e)}")
        return False

# Initialize payment tables on import
try:
    create_payment_tables()
except Exception:
    pass  # Ignore errors during import