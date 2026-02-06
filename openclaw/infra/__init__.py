"""Infrastructure modules"""

from .tailscale import TailscaleAuthProvider, read_tailscale_whois_identity

__all__ = ["TailscaleAuthProvider", "read_tailscale_whois_identity"]
