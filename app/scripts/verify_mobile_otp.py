import os
import json
from app.core.hubscape_adk import get_context, require_tool_privilege

@require_tool_privilege
async def verify_mobile_otp(mobile_number: str, otp_code: str) -> dict:
    """
    Validates the 6-digit OTP code entered by the user.

    Args:
        mobile_number: The personal mobile number associated with the code.
        otp_code: The 6-digit verification code.
    """
    clean_phone = "".join(filter(str.isdigit, mobile_number))
    has_country = True
    if len(clean_phone) >= 10:
        has_country = mobile_number.strip().startswith('+')
        
    if not (len(clean_phone) >= 10 or len(clean_phone) in (7, 8)) or not has_country:
        return {
            "valid": False,
            "message": "Invalid mobile number format. Please include your country code starting with '+' (e.g. +919876543210 or +15550199000)."
        }

    ctx = get_context()
    res = ctx.verify_otp(mobile_number, otp_code)
    
    if res.get("success"):
        # Save verified_mobile in the database inside the session state variable
        session_id = ctx.raw_context.get("sessionId") or ctx.raw_context.get("session_id")
        if session_id:
            # 1. Update in-memory ADK session state first
            from app.core.hubscape_adk import request_runner_ctx
            runner = request_runner_ctx.get()
            if runner and runner.session_service:
                try:
                    user_id = ctx.auth.get_user_id()
                    session_obj = runner.session_service.sessions.get(runner.app_name, {}).get(user_id, {}).get(session_id)
                    if session_obj:
                        if not session_obj.state:
                            session_obj.state = {}
                        session_obj.state["verified_mobile"] = mobile_number
                except Exception as e:
                    print(f"⚠️ [SESSION STATE MEMORY WARNING] Failed to set verified_mobile: {e}")

            # 2. Update session Firestore document directly as a fallback/redundancy
            try:
                ctx.save(
                    scope="user",
                    collection_name="sessions",
                    doc_id=session_id,
                    data={
                        "verified_mobile": mobile_number
                    }
                )
            except Exception as e:
                print(f"⚠️ [SESSION SAVE WARNING] Failed to save verified_mobile to session document: {e}")

        return {
            "valid": True,
            "message": "OTP verification successful."
        }
            
    return {
        "valid": False,
        "message": "Invalid verification code. Please check and try again."
    }
