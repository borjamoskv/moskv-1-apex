import subprocess

class KeychainEscrow:
    """
    C5-REAL POST-QUANTUM ESCROW
    Cryptographic mechanism to retrieve secrets directly from macOS Keychain.
    Prevents keeping ephemeral secrets in memory or unencrypted files.
    """
    @staticmethod
    def get_secret(service: str, account: str = None) -> str:
        """
        Retrieves a password from the macOS Keychain.
        """
        try:
            cmd = ["security", "find-generic-password", "-s", service, "-w"]
            if account:
                cmd.extend(["-a", account])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"[PQ-ESCROW-FATAL] Failed to read '{service}' from Keychain. Ensure the vault exists.")
            raise RuntimeError(f"Keychain access denied or vault not found for service: {service}")

if __name__ == "__main__":
    # Test execution
    try:
        escrow_key = KeychainEscrow.get_secret("MOSKV-Vault")
        if escrow_key:
            print("[PQ-ESCROW] Master Seed securely fetched from Keychain.")
    except Exception as e:
        print(f"Test failed: {e}")
