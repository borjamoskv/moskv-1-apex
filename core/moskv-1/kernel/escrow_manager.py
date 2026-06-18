#!/usr/bin/env python3
# Execution Level: C5-REAL
import subprocess
import sys
import shlex
import argparse

SERVICE_NAME = "MOSKV-1-CORTEX"

def set_key(account: str, value: str):
    cmd = f"security add-generic-password -U -a {shlex.quote(account)} -s {shlex.quote(SERVICE_NAME)} -w {shlex.quote(value)}"
    subprocess.run(cmd, shell=True, check=True)
    print(f"[ESCROW-OK] Secret {account} securely burned into macOS Keychain under {SERVICE_NAME}.")

def get_key(account: str) -> str:
    cmd = f"security find-generic-password -a {shlex.quote(account)} -s {shlex.quote(SERVICE_NAME)} -w"
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MOSKV-1 Keychain Escrow Manager")
    parser.add_argument("--set-stripe", dest="stripe_key", help="Set STRIPE_SECRET_KEY")
    parser.add_argument("--set-webhook", dest="webhook_key", help="Set STRIPE_WEBHOOK_SECRET")
    parser.add_argument("--get", dest="get_key", help="Retrieve a key (for testing)")
    
    args = parser.parse_args()
    
    if args.stripe_key:
        set_key("STRIPE_SECRET_KEY", args.stripe_key)
    if args.webhook_key:
        set_key("STRIPE_WEBHOOK_SECRET", args.webhook_key)
    if args.get_key:
        val = get_key(args.get_key)
        if val:
            print(f"[ESCROW] Key '{args.get_key}' exists in Secure Enclave.")
        else:
            print(f"[ESCROW] Key '{args.get_key}' NOT FOUND.")
