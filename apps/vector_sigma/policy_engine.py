import ipaddress
from urllib.parse import urlparse

class PolicyEngine:
    def __init__(self, allowed_scopes: list):
        self.allowed_domains = []
        self.allowed_cidrs = []
        
        for scope in allowed_scopes:
            try:
                # Try parsing as CIDR
                ipaddress.ip_network(scope)
                self.allowed_cidrs.append(scope)
            except ValueError:
                self.allowed_domains.append(scope)

    def validate_target(self, target_uri: str) -> bool:
        """
        Validates if a given target URI is within the strict programmatic scope.
        Returns True if authorized, False otherwise (triggers Drop & Log).
        """
        domain = target_uri
        if "://" in target_uri:
            parsed = urlparse(target_uri)
            domain = parsed.hostname or target_uri

        # Strip port if present
        if domain and ":" in domain:
            domain = domain.split(":")[0]

        if not domain:
            return False

        # IP check
        try:
            ip = ipaddress.ip_address(domain)
            for cidr in self.allowed_cidrs:
                if ip in ipaddress.ip_network(cidr):
                    return True
            return False
        except ValueError:
            pass # Not an IP, proceed to domain check

        # Domain wildcard match
        for allowed in self.allowed_domains:
            if allowed.startswith("*."):
                base = allowed[2:]
                if domain == base or domain.endswith("." + base):
                    return True
            else:
                if domain == allowed:
                    return True

        return False
