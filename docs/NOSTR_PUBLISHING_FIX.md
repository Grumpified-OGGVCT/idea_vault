# NOSTR Publishing Fix - November 2025

## Issue
The Daily Research Report workflow was failing at the "Publish to NOSTR" step due to a secret reference mismatch.

## Root Cause
The workflow was referencing `secrets.NOSTR_PRIVATE_KEY`, but the secret stored in the repository was named `secrets.NOSTR_PUBLIC_KEY`.

## Solution
Updated `.github/workflows/daily_report.yml` (line 49) to reference the correct secret:

```yaml
# Before:
NOSTR_PRIVATE_KEY: ${{ secrets.NOSTR_PRIVATE_KEY }}

# After:
NOSTR_PRIVATE_KEY: ${{ secrets.NOSTR_PUBLIC_KEY }}
```

## Important Notes

### Secret Naming Convention
- **Secret Name**: `NOSTR_PUBLIC_KEY` (in GitHub repository secrets)
- **Secret Value**: Contains the NOSTR **private key** in hex format (64-character hex string)
- **Environment Variable**: `NOSTR_PRIVATE_KEY` (as expected by `scripts/publish_nostr.py`)

The naming may be confusing, but:
- The secret is named `NOSTR_PUBLIC_KEY` in the repository
- The value it contains is actually the **private key** (required for signing NOSTR events)
- The publishing script correctly uses this private key to derive the public key

### How NOSTR Publishing Works
1. Workflow reads `secrets.NOSTR_PUBLIC_KEY` (which contains the private key value)
2. Passes it as `env.NOSTR_PRIVATE_KEY` to the publishing script
3. Script (`scripts/publish_nostr.py`) reads `NOSTR_PRIVATE_KEY` from environment
4. Creates a `NostrPublisher` instance with the private key
5. Automatically derives the public key from the private key
6. Signs and publishes reports to 48+ NOSTR relays using NIP-23

### Key Format
The NOSTR private key must be in **hex format** (64-character hex string), not bech32 format (nsec1...).

To convert from bech32 to hex:
```bash
# If you have a bech32 key (nsec1...)
nak key decode nsec1...
```

## Testing
The fix was verified with:
1. Local simulation of the workflow environment
2. Verification of pynostr library functionality
3. Test of key generation and derivation
4. Confirmation of report loading and publisher initialization

## Next Steps
When the workflow runs (either on schedule at 08:00/20:00 UTC or manually triggered):
1. The NOSTR publishing step will successfully read the secret
2. Reports will be published to 48+ NOSTR relays
3. Publication records will be saved to `data/nostr_publications/`
4. Events can be viewed on NOSTR clients (Damus, Snort, Iris, etc.)

## Related Files
- `.github/workflows/daily_report.yml` - Workflow configuration
- `scripts/publish_nostr.py` - NOSTR publishing script
- `DEPLOYMENT_GUIDE_ENHANCED.md` - Deployment instructions
- `TESTING_OLLAMA_NOSTR.md` - Testing guide
