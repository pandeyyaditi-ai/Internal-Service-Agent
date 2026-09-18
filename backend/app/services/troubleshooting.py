"""
VPN troubleshooting service.
Implements a guided step-by-step decision tree for diagnosing VPN issues.
"""
from typing import Dict, Any, Optional
from app.core.logging import get_logger

logger = get_logger("troubleshooting")


# VPN troubleshooting decision tree
VPN_TROUBLESHOOTING_STEPS = {
    0: {
        "title": "VPN Troubleshooting Started",
        "message": (
            "I'll help you troubleshoot your VPN connection. Let's go through some steps together.\n\n"
            "**Step 1: Check your internet connection**\n\n"
            "Can you open a website (like google.com) in your browser without VPN? "
            "Please reply **yes** or **no**."
        ),
        "next_on_yes": 1,
        "next_on_no": "internet_issue",
        "escalate_after": None,
    },
    1: {
        "title": "Internet OK — Check VPN Client",
        "message": (
            "Great, your internet is working. ✅\n\n"
            "**Step 2: Check your VPN client**\n\n"
            "Is GlobalProtect VPN client installed on your computer? "
            "You should see a globe icon in your system tray (bottom-right on Windows, top-right on Mac).\n\n"
            "Reply **yes** if you see it, or **no** if you don't have it installed."
        ),
        "next_on_yes": 2,
        "next_on_no": "install_vpn",
        "escalate_after": None,
    },
    2: {
        "title": "VPN Client Found — Try Reconnecting",
        "message": (
            "Good, VPN client is installed. ✅\n\n"
            "**Step 3: Restart the VPN client**\n\n"
            "Please try these steps:\n"
            "1. Right-click the GlobalProtect icon in your system tray\n"
            "2. Select **Disconnect** (if connected)\n"
            "3. Wait 10 seconds\n"
            "4. Click **Connect**\n"
            "5. Enter portal address: `vpn.company.com`\n"
            "6. Log in with your corporate credentials\n\n"
            "Did the VPN connect successfully? Reply **yes** or **no**."
        ),
        "next_on_yes": "resolved",
        "next_on_no": 3,
        "escalate_after": None,
    },
    3: {
        "title": "Reconnection Failed — Check Credentials",
        "message": (
            "Let's check your credentials. 🔐\n\n"
            "**Step 4: Verify your credentials**\n\n"
            "Please try logging into your email at https://outlook.office365.com with the same credentials.\n\n"
            "- If you **can** log into email, your credentials are fine — the issue is VPN-specific.\n"
            "- If you **cannot** log into email, your password may have expired.\n\n"
            "Can you log into your email? Reply **yes** or **no**."
        ),
        "next_on_yes": 4,
        "next_on_no": "password_issue",
        "escalate_after": None,
    },
    4: {
        "title": "Credentials OK — Check Firewall",
        "message": (
            "Credentials are working. ✅\n\n"
            "**Step 5: Check firewall and network**\n\n"
            "Please try these steps:\n"
            "1. **Flush DNS**: Open Command Prompt (or Terminal on Mac) and run:\n"
            "   - Windows: `ipconfig /flushdns`\n"
            "   - Mac: `sudo dscacheutil -flushcache`\n"
            "2. **Temporarily disable** your personal firewall or antivirus\n"
            "3. Try connecting to VPN again\n\n"
            "Did the VPN connect after these steps? Reply **yes** or **no**."
        ),
        "next_on_yes": "resolved_firewall",
        "next_on_no": 5,
        "escalate_after": None,
    },
    5: {
        "title": "Firewall Check Failed — Try Different Network",
        "message": (
            "Let's try a different network. 📡\n\n"
            "**Step 6: Try a different network**\n\n"
            "Your current network may be blocking VPN traffic. Please try:\n"
            "1. Switch to a **mobile hotspot** from your phone\n"
            "2. Or try connecting from a **different WiFi network**\n"
            "3. Attempt VPN connection again\n\n"
            "Did VPN connect on a different network? Reply **yes** or **no**."
        ),
        "next_on_yes": "resolved_network",
        "next_on_no": "escalate",
        "escalate_after": None,
    },
}

# Resolution messages for terminal states
RESOLUTION_MESSAGES = {
    "internet_issue": (
        "It seems your internet connection is the issue. 🌐\n\n"
        "**Suggestions:**\n"
        "- Restart your WiFi router/modem\n"
        "- Try a different network (mobile hotspot)\n"
        "- Check if your ISP has any outages\n"
        "- Try connecting with an ethernet cable\n\n"
        "Once your internet is working, try connecting to VPN again. "
        "If you still have issues, let me know!"
    ),
    "install_vpn": (
        "You need to install the GlobalProtect VPN client. 📥\n\n"
        "**Installation steps:**\n"
        "1. Go to https://vpn.company.com\n"
        "2. Log in with your corporate credentials\n"
        "3. Download the GlobalProtect client for your OS\n"
        "4. Run the installer with admin privileges\n"
        "5. Open GlobalProtect and enter portal: `vpn.company.com`\n"
        "6. Connect with your credentials\n\n"
        "If you can't access the download page, I can create a ticket for IT to assist you."
    ),
    "password_issue": (
        "Your password may have expired or been changed. 🔐\n\n"
        "**To reset your password:**\n"
        "1. Go to https://passwordreset.company.com\n"
        "2. Enter your employee ID\n"
        "3. Follow the verification steps\n"
        "4. Create a new password (min 12 chars, mix of upper/lower/number/special)\n"
        "5. After resetting, try VPN again with the new password\n\n"
        "Remember: It may take a few minutes for the new password to sync across all systems."
    ),
    "resolved": (
        "Excellent! Your VPN is now connected! 🎉\n\n"
        "The restart resolved the issue. If it happens again frequently, consider:\n"
        "- Keeping GlobalProtect updated to the latest version\n"
        "- Restarting the VPN client when switching networks\n\n"
        "Is there anything else I can help you with?"
    ),
    "resolved_firewall": (
        "Your VPN is connected now! 🎉\n\n"
        "The issue was likely caused by your firewall or antivirus blocking VPN traffic.\n\n"
        "**Recommended actions:**\n"
        "- Add GlobalProtect to your firewall's allowed list\n"
        "- Ensure ports 443 and 4443 are not blocked\n"
        "- If using third-party antivirus, add VPN as an exception\n\n"
        "Would you like me to create a ticket to have IT configure your firewall properly?"
    ),
    "resolved_network": (
        "Your VPN connected on a different network! 🎉\n\n"
        "Your original network appears to be blocking VPN traffic. This commonly happens with:\n"
        "- Public WiFi networks (hotels, cafes)\n"
        "- Networks with strict firewall rules\n"
        "- Some ISPs that block VPN protocols\n\n"
        "**Options:**\n"
        "- Continue using the working network\n"
        "- Contact your network administrator to allow VPN traffic\n"
        "- Request split tunneling from IT (if eligible)\n\n"
        "Is there anything else I can help you with?"
    ),
    "escalate": (
        "I've exhausted the standard troubleshooting steps, and your VPN still isn't connecting. 😔\n\n"
        "**I'm escalating this to our IT support team** who can:\n"
        "- Check your VPN profile on the server side\n"
        "- Verify your device compliance status\n"
        "- Check for any account-level restrictions\n"
        "- Perform advanced network diagnostics\n\n"
        "I'll create a high-priority ticket for you right away."
    ),
}


async def get_troubleshooting_response(
    current_step: Optional[int],
    user_response: str,
    conversation_id: str,
) -> Dict[str, Any]:
    """
    Process user response in the VPN troubleshooting flow.
    Returns the next step message and metadata.
    """
    user_lower = user_response.lower().strip()

    # Starting the troubleshooting flow
    if current_step is None or current_step == -1:
        step_data = VPN_TROUBLESHOOTING_STEPS[0]
        return {
            "message": step_data["message"],
            "step": 0,
            "is_resolved": False,
            "needs_escalation": False,
            "needs_ticket": False,
        }

    # Get current step data
    step_data = VPN_TROUBLESHOOTING_STEPS.get(current_step)
    if not step_data:
        return {
            "message": RESOLUTION_MESSAGES["escalate"],
            "step": current_step,
            "is_resolved": False,
            "needs_escalation": True,
            "needs_ticket": True,
        }

    # Determine if user responded yes or no
    is_yes = any(word in user_lower for word in ["yes", "yeah", "yep", "yup", "y", "correct", "it works", "working", "connected", "can"])
    is_no = any(word in user_lower for word in ["no", "nope", "nah", "n", "not", "doesn't", "didn't", "can't", "cannot", "failed", "error"])

    if is_yes:
        next_step = step_data["next_on_yes"]
    elif is_no:
        next_step = step_data["next_on_no"]
    else:
        # Unclear response — ask again
        return {
            "message": f"I didn't quite understand that. Could you please reply with **yes** or **no**?\n\n{step_data['message'].split('Reply')[0]}Reply **yes** or **no**.",
            "step": current_step,
            "is_resolved": False,
            "needs_escalation": False,
            "needs_ticket": False,
        }

    # Check if next step is a terminal state
    if isinstance(next_step, str):
        resolution_msg = RESOLUTION_MESSAGES.get(next_step, RESOLUTION_MESSAGES["escalate"])
        is_resolved = next_step.startswith("resolved")
        needs_escalation = next_step == "escalate"
        needs_ticket = next_step in ["escalate", "install_vpn"]

        return {
            "message": resolution_msg,
            "step": -1,  # Terminal state
            "is_resolved": is_resolved,
            "needs_escalation": needs_escalation,
            "needs_ticket": needs_ticket,
        }

    # Move to next step
    next_step_data = VPN_TROUBLESHOOTING_STEPS.get(next_step)
    if not next_step_data:
        return {
            "message": RESOLUTION_MESSAGES["escalate"],
            "step": -1,
            "is_resolved": False,
            "needs_escalation": True,
            "needs_ticket": True,
        }

    return {
        "message": next_step_data["message"],
        "step": next_step,
        "is_resolved": False,
        "needs_escalation": False,
        "needs_ticket": False,
    }
