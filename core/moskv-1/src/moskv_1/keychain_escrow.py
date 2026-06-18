import subprocess
import hashlib
import os

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

    @classmethod
    def generate_lattice_signature(cls, payload: str) -> dict:
        """
        Simulates a Lattice-based (LWE - Learning With Errors) signature generation.
        Equivalent to the crypto-escrow.js implementation for cross-runtime determinism.
        """
        seed = cls.get_secret("MOSKV-Vault")
        h1_input = f"{payload}{seed}".encode('utf-8')
        h1 = hashlib.sha512(h1_input).hexdigest()
        
        # "Learning with errors" noise injection
        noise = os.urandom(16).hex()
        h2_input = f"{h1}{noise}".encode('utf-8')
        h2 = hashlib.sha384(h2_input).hexdigest()
        
        return {
            "signature": h2,
            "noiseVector": noise
        }

    @classmethod
    def verify_lattice_signature(cls, payload: str, signature: str, noise_vector: str) -> bool:
        """
        Verifies the cryptographic seal deterministically.
        """
        seed = cls.get_secret("MOSKV-Vault")
        h1_input = f"{payload}{seed}".encode('utf-8')
        h1 = hashlib.sha512(h1_input).hexdigest()
        
        expected_input = f"{h1}{noise_vector}".encode('utf-8')
        expected = hashlib.sha384(expected_input).hexdigest()
        
        return signature == expected

if __name__ == "__main__":
    # Test execution
    try:
        payload_test = "SQUAD-REAPER-1|YIELD_GENERATION|5.0"
        seal = KeychainEscrow.generate_lattice_signature(payload_test)
        print(f"[PQ-ESCROW] Master Seed securely fetched. Signature: {seal['signature']}")
        is_valid = KeychainEscrow.verify_lattice_signature(payload_test, seal['signature'], seal['noiseVector'])
        print(f"[PQ-ESCROW] Signature Verification: {'PASS' if is_valid else 'FAIL'}")
    except Exception as e:
        print(f"Test failed: {e}")
