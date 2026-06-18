import subprocess

class KeychainEscrow:
    """
    C5-REAL RAW ESCROW
    Retrieves secrets directly from macOS Keychain.
    Zero theatrical abstraction.
    """
    @staticmethod
    def get_secret(service: str, account: str = None) -> str:
        try:
            cmd = ["security", "find-generic-password", "-s", service, "-w"]
            if account:
                cmd.extend(["-a", account])
            return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()
        except subprocess.CalledProcessError:
            print(f"[ESCROW-FATAL] Missing vault: {service}")
            raise RuntimeError(f"Keychain access denied: {service}")

if __name__ == "__main__":
    try:
        if KeychainEscrow.get_secret("MOSKV-Vault"):
            print("[ESCROW] C5-REAL Vault Accessed.")
    except Exception as e:
        print(f"Test failed: {e}")
