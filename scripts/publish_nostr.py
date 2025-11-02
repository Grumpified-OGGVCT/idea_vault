#!/usr/bin/env python3
"""
NOSTR Publishing for AI Research Daily
Publishes reports to 48+ NOSTR relays using NIP-23 (long-form content)
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

try:
    from nostr.event import Event
    from nostr.relay_manager import RelayManager
    from nostr.message_type import ClientMessageType
    from nostr.key import PrivateKey
    NOSTR_AVAILABLE = True
except ImportError:
    print("⚠️  nostr library not available - install with: pip install nostr")
    NOSTR_AVAILABLE = False


# Default relay list (48+ relays)
DEFAULT_RELAYS = [
    "wss://relay.damus.io",
    "wss://relay.nostr.band",
    "wss://nostr.wine",
    "wss://relay.snort.social",
    "wss://nos.lol",
    "wss://relay.current.fyi",
    "wss://nostr.mom",
    "wss://relay.nostr.bg",
    "wss://nostr-pub.wellorder.net",
    "wss://relay.orangepill.dev",
    "wss://nostr.zebedee.cloud",
    "wss://relay.nostrich.de",
    "wss://nostr.rocks",
    "wss://relay.nostrati.com",
    "wss://relay.minds.com/nostr/v1/ws",
    "wss://relay.CoinsureNF.com",
    "wss://nostr21.com",
    "wss://nostr.oxtr.dev",
    "wss://relay.mostr.pub",
    "wss://nostr.fmt.wiz.biz",
    "wss://relay.nostr.com.au",
    "wss://nostr.slothy.win",
    "wss://relay.minds.io",
    "wss://nostr.roundrockbitcoiners.com",
    "wss://nostr.developer.li",
    "wss://relay.nostr.info",
    "wss://nostr-relay.nokotaro.com",
    "wss://relay.nostrgraph.net",
    "wss://nostr.onsats.org",
    "wss://nostr.vulpem.com",
    "wss://relay.nostr.net",
    "wss://relay.nostr.vision",
    "wss://nostr.cheeserobot.org",
    "wss://relay.nostriches.org",
    "wss://nostr.fractalized.net",
    "wss://nostr.semisol.dev",
    "wss://relay.nostr.scot",
    "wss://relay.nostr.ch",
    "wss://relay.nostr.ro",
    "wss://nostr.koning-degraaf.nl",
    "wss://nostr.thesamecat.io",
    "wss://relay.nostrplebs.com",
    "wss://relay.nostr.wf",
    "wss://nostr-relay.alekberg.net",
    "wss://nostr.0x7e.xyz",
    "wss://relay.nostrified.org",
    "wss://relay.n057r.club",
    "wss://relay.nostr.nu",
]


class NostrPublisher:
    """Publish AI research reports to NOSTR network"""
    
    def __init__(self, private_key_hex: Optional[str] = None, relays: Optional[List[str]] = None):
        """
        Initialize NOSTR publisher
        
        Args:
            private_key_hex: Hex-encoded NOSTR private key (nsec format)
            relays: List of relay URLs (defaults to 48+ relays)
        """
        if not NOSTR_AVAILABLE:
            raise ImportError("nostr library not installed")
        
        self.private_key = PrivateKey(bytes.fromhex(private_key_hex)) if private_key_hex else PrivateKey()
        self.public_key = self.private_key.public_key
        self.relays = relays or DEFAULT_RELAYS
        self.relay_manager = RelayManager()
        
        print(f"📡 NOSTR Publisher initialized")
        print(f"   Public Key: {self.public_key.hex()}")
        print(f"   Relays: {len(self.relays)}")
    
    def connect_relays(self, max_relays: int = 48):
        """Connect to NOSTR relays"""
        print(f"🔗 Connecting to {min(max_relays, len(self.relays))} NOSTR relays...")
        
        connected = 0
        for relay_url in self.relays[:max_relays]:
            try:
                self.relay_manager.add_relay(relay_url)
                connected += 1
            except Exception as e:
                print(f"   ⚠️  Failed to add relay {relay_url}: {e}")
        
        self.relay_manager.open_connections({"cert_reqs": "CERT_NONE"})
        time.sleep(2)  # Give relays time to connect
        
        print(f"✅ Connected to {connected} relays")
        return connected
    
    def publish_report(
        self, 
        title: str, 
        content: str, 
        summary: str = "", 
        tags: Optional[List[str]] = None,
        image_url: Optional[str] = None
    ) -> Dict:
        """
        Publish report as NIP-23 long-form content
        
        Args:
            title: Report title
            content: Full markdown content
            summary: Short summary/excerpt
            tags: List of tags
            image_url: Optional header image URL
            
        Returns:
            Dict with publication results
        """
        print(f"📝 Publishing report: {title}")
        
        # Prepare NIP-23 event (kind 30023)
        event_tags = [
            ["d", f"ai-research-{datetime.now().strftime('%Y-%m-%d')}"],  # Unique identifier
            ["title", title],
            ["published_at", str(int(time.time()))],
            ["t", "ai"],
            ["t", "research"],
            ["t", "llm"],
        ]
        
        if summary:
            event_tags.append(["summary", summary[:200]])
        
        if image_url:
            event_tags.append(["image", image_url])
        
        if tags:
            for tag in tags:
                event_tags.append(["t", tag.lower()])
        
        # Create event
        event = Event(
            public_key=self.public_key.hex(),
            kind=30023,  # NIP-23: Long-form content
            content=content,
            tags=event_tags
        )
        
        # Sign event
        self.private_key.sign_event(event)
        
        # Publish to relays
        message = event.to_message()
        self.relay_manager.publish_message(message)
        time.sleep(3)  # Give relays time to process
        
        print(f"✅ Report published to NOSTR network")
        print(f"   Event ID: {event.id}")
        print(f"   Kind: 30023 (NIP-23 long-form)")
        print(f"   Relays: {len(self.relays)}")
        
        return {
            "event_id": event.id,
            "public_key": self.public_key.hex(),
            "kind": 30023,
            "title": title,
            "relays": len(self.relays),
            "published_at": datetime.now().isoformat()
        }
    
    def close(self):
        """Close relay connections"""
        self.relay_manager.close_connections()
        print("🔌 Closed NOSTR relay connections")


def load_latest_report() -> Optional[Dict[str, str]]:
    """Load the latest report from docs/reports/"""
    reports_dir = Path("docs/reports")
    
    if not reports_dir.exists():
        print("❌ Reports directory not found")
        return None
    
    # Find latest lab-*.md file
    lab_reports = sorted(reports_dir.glob("lab-*.md"), reverse=True)
    
    if not lab_reports:
        print("❌ No reports found")
        return None
    
    latest = lab_reports[0]
    print(f"📄 Loading report: {latest.name}")
    
    with open(latest, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title from first heading
    title = "AI Research Daily"
    for line in content.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    # Extract date from filename
    date_str = latest.stem.replace('lab-', '')
    
    return {
        "title": title,
        "content": content,
        "date": date_str,
        "filename": latest.name
    }


def main():
    """Main publishing function"""
    print("🚀 Starting NOSTR publishing...")
    
    if not NOSTR_AVAILABLE:
        print("❌ NOSTR library not available")
        print("   Install with: pip install nostr")
        return
    
    # Get private key from environment
    private_key_hex = os.getenv('NOSTR_PRIVATE_KEY')
    
    if not private_key_hex:
        print("⚠️  NOSTR_PRIVATE_KEY not set - generating temporary key")
        print("   Set NOSTR_PRIVATE_KEY environment variable for persistent publishing")
        private_key_hex = None  # Will generate new key
    
    # Load latest report
    report = load_latest_report()
    
    if not report:
        print("❌ No report to publish")
        return
    
    # Initialize publisher
    publisher = NostrPublisher(private_key_hex=private_key_hex)
    publisher.connect_relays(max_relays=48)
    
    # Publish report
    result = publisher.publish_report(
        title=report['title'],
        content=report['content'],
        summary=f"Daily AI research intelligence - {report['date']}",
        tags=['ai', 'research', 'daily', 'llm', 'machinelearning']
    )
    
    # Save publication record
    pub_record_file = Path(f"data/nostr_publications/{report['date']}.json")
    pub_record_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(pub_record_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"💾 Publication record saved to {pub_record_file}")
    
    # Close connections
    publisher.close()
    
    print("✅ NOSTR publishing complete!")


if __name__ == "__main__":
    main()
