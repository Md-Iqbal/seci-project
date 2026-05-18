from django.core.management.utils import get_random_secret_key
import sys

def generate_secret_key():
    """Generate a new Django secret key"""
    secret_key = get_random_secret_key()
    print("=" * 80)
    print("NEW SECRET KEY GENERATED")
    print("=" * 80)
    print(f"\n{secret_key}\n")
    print("=" * 80)
    print("IMPORTANT: Copy this key to your .env file")
    print("SECRET_KEY=your-key-here")
    print("=" * 80)
    return secret_key

if __name__ == "__main__":
    generate_secret_key()