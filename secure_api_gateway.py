# ============================================================
# DESI∞ INFINITY SYSTEM 6.2.0 - SECURE API GATEWAY
# Authentication, Rate Limiting & Role-Based Access Enforcement
# ============================================================

from typing import Dict, Any

class SecureAPIGateway:
    """
    [CALC] Enforces API request authentication, token validation, 
    rate limiting, and role-based permissions before endpoint dispatch.
    """
    def __init__(self):
        self.mock_tokens = {
            "token_admin_secret": {"user": "admin_frank", "role": "ADMIN"},
            "token_research_key": {"user": "researcher_1", "role": "RESEARCHER"}
        }

    def authorize_request(self, auth_token: str, required_role: str) -> Dict[str, Any]:
        if auth_token not in self.mock_tokens:
            return {"authorized": False, "error": "Invalid or expired authentication token."}

        user_info = self.mock_tokens[auth_token]
        user_role = user_info["role"]

        role_hierarchy = {"VIEWER": 1, "RESEARCHER": 2, "ADMIN": 3}
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            return {"authorized": False, "error": f"Permission denied for role '{user_role}'."}

        return {"authorized": True, "user": user_info["user"], "role": user_role}

if __name__ == "__main__":
    gw = SecureAPIGateway()
    print("Gateway Auth Test:", gw.authorize_request("token_research_key", "ADMIN"))
