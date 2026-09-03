import logging
from typing import Optional
from app.core.hubscape_adk import get_context, require_tool_privilege

logger = logging.getLogger(__name__)

@require_tool_privilege
async def check_otp_verification(request_id: Optional[str] = None) -> dict:
    """
    Checks if an OTP verification request has been verified by the user in Firestore.
    
    Args:
        request_id: Optional ID of the verification request. If omitted, checks active session state.
    """
    ctx = get_context()
    
    target_id = request_id
    if not target_id and hasattr(ctx, "session") and ctx.session and ctx.session.state:
        target_id = ctx.session.state.get("pending_otp_request_id")
        
    if not target_id:
        return {
            "verified": False,
            "status": "not_found",
            "message": "No active OTP verification request found."
        }
        
    try:
        doc = ctx._db_client.collection("otp_verifications").document(target_id).get()
        if not doc.exists:
            return {"verified": False, "status": "not_found", "message": "Verification request record not found."}
            
        data = doc.to_dict() or {}
        status = data.get("status")
        
        if status == "verified":
            verified_phone = data.get("verified_phone") or data.get("phone_number")
            if hasattr(ctx, "session") and ctx.session and ctx.session.state is not None:
                ctx.session.state["verified_mobile"] = verified_phone
                ctx.session.state["phone_verified"] = True
                
            return {
                "verified": True,
                "status": "verified",
                "verified_phone": verified_phone,
                "purpose": data.get("purpose"),
                "message": f"Phone number {verified_phone} verified successfully."
            }
        else:
            return {
                "verified": False,
                "status": status or "pending",
                "message": f"Verification status is '{status}'. User has not completed OTP verification yet."
            }
    except Exception as e:
        logger.error(f"Error checking OTP verification: {e}")
        return {"verified": False, "status": "error", "message": f"Database check error: {str(e)}"}
