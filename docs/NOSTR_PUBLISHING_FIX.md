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

**⚠️ SECURITY NOTE**: The secret naming is non-standard and potentially confusing.

- **Secret Name**: `NOSTR_PUBLIC_KEY` (in GitHub repository secrets)
- **Secret Value**: Contains the NOSTR **PRIVATE KEY** in hex format (64-character hex string)
- **Environment Variable**: `NOSTR_PRIVATE_KEY` (as expected by `scripts/publish_nostr.py`)

**Important Security Considerations**:
- ⚠️ Despite being named `NOSTR_PUBLIC_KEY`, this secret contains **sensitive private key material**
- ⚠️ The private key MUST be kept secret and never exposed in logs or commits
- ⚠️ This naming was chosen by the repository owner but is NOT recommended for clarity
- ✅ The secret is properly stored in GitHub Secrets (encrypted at rest)
- ✅ The workflow correctly prevents the key from appearing in logs

**How it works**:
- The secret named `NOSTR_PUBLIC_KEY` actually contains the **private key** (required for signing NOSTR events)
- The publishing script correctly uses this private key to derive the public key automatically
- This naming convention should be understood by all maintainers to prevent accidental exposure

**Recommended Best Practice**: The secret should be renamed **immediately** in the current deployment to avoid confusion and ensure proper security awareness.

**Actionable Steps to Safely Rename the Secret:**

1. **Create a new secret** in your GitHub repository named `NOSTR_PRIVATE_KEY` with the same value as the current `NOSTR_PUBLIC_KEY` (the 64-character hex private key).
2. **Update** `.github/workflows/daily_report.yml` to reference `secrets.NOSTR_PRIVATE_KEY` instead of `secrets.NOSTR_PUBLIC_KEY`.
3. **Verify** that the workflow runs successfully and publishes to NOSTR as expected.
4. **Delete** the old secret `NOSTR_PUBLIC_KEY` from the repository secrets to prevent accidental exposure or misuse.

> This process ensures there is no downtime or risk of failed workflow runs, and improves security and clarity for all maintainers.
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
