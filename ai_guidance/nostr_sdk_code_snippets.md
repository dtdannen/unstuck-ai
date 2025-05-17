## hello.py

```python
# ANCHOR: full
import asyncio
from nostr_sdk import Keys, Client, EventBuilder, NostrSigner


async def hello():
    # ANCHOR: client
    keys = Keys.generate()
    signer = NostrSigner.keys(keys)
    client = Client(signer)
    # ANCHOR_END: client

    # ANCHOR: connect
    await client.add_relay("wss://relay.damus.io")
    await client.connect()
    # ANCHOR_END: connect

    # ANCHOR: publish
    builder = EventBuilder.text_note("Hello, rust-nostr!")
    output = await client.send_event_builder(builder)
    # ANCHOR_END: publish

    # ANCHOR: output
    print(f"Event ID: {output.id.to_bech32()}")
    print(f"Sent to: {output.success}")
    print(f"Not send to: {output.failed}")
    # ANCHOR_END: output

if __name__ == '__main__':
   asyncio.run(hello())
# ANCHOR_END: full

```

## keys.py

```python
from nostr_sdk import Keys, SecretKey


# ANCHOR: generate
def generate():
    keys = Keys.generate()

    public_key = keys.public_key()
    secret_key = keys.secret_key()

    print(f"Public key (hex): {public_key.to_hex()}")
    print(f"Secret key (hex): {secret_key.to_hex()}")

    print(f"Public key (bech32): {public_key.to_bech32()}")
    print(f"Secret key (bech32): {secret_key.to_bech32()}")
# ANCHOR_END: generate

# ANCHOR: restore
def restore():
    keys = Keys.parse("nsec1j4c6269y9w0q2er2xjw8sv2ehyrtfxq3jwgdlxj6qfn8z4gjsq5qfvfk99")

    secret_key = SecretKey.parse("6b911fd37cdf5c81d4c0adb1ab7fa822ed253ab0ad9aa18d77257c88b29b718e")
    keys = Keys(secret_key)
# ANCHOR_END: restore

if __name__ == '__main__':
   generate()
   restore()
```

## nip01.py

```python
from nostr_sdk import Keys, Metadata, EventBuilder


def nip01():
    # Generate random keys
    keys = Keys.generate()

    # ANCHOR: create-event
    # Create metadata object with desired content
    metadata_content = Metadata()\
        .set_name("TestName")\
        .set_display_name("PyTestur")\
        .set_about("This is a Test Account for Rust Nostr Python Bindings")\
        .set_website("https://rust-nostr.org/")\
        .set_picture("https://avatars.githubusercontent.com/u/123304603?s=200&v=4")\
        .set_banner("https://nostr-resources.com/assets/images/cover.png")\
        .set_nip05("TestName@rustNostr.com")

    # Build metadata event and assign content
    builder = EventBuilder.metadata(metadata_content)

    # Signed event and print details
    print("Creating Metadata Event:")
    event = builder.sign_with_keys(keys)

    print(" Event Details:")
    print(f"     Author    : {event.author().to_bech32()}")
    print(f"     Kind      : {event.kind().as_u16()}")
    print(f"     Content   : {event.content()}")
    print(f"     Datetime  : {event.created_at().to_human_datetime()}")
    print(f"     Signature : {event.signature()}")
    print(f"     Verify    : {event.verify()}")
    print(f"     JSON      : {event.as_json()}")
    # ANCHOR_END: create-event

    # ANCHOR: create-metadata
    # Deserialize Metadata from event
    print("Deserializing Metadata Event:")
    metadata = Metadata().from_json(event.content())

    print(" Metadata Details:")
    print(f"     Name      : {metadata.get_name()}")
    print(f"     Display   : {metadata.get_display_name()}")
    print(f"     About     : {metadata.get_about()}")
    print(f"     Website   : {metadata.get_website()}")
    print(f"     Picture   : {metadata.get_picture()}")
    print(f"     Banner    : {metadata.get_banner()}")
    print(f"     NIP05     : {metadata.get_nip05()}")
    # ANCHOR_END: create-metadata

if __name__ == '__main__':
   nip01()
```

## nip05.py

```python
import asyncio
from nostr_sdk import Metadata, PublicKey, verify_nip05, get_nip05_profile


async def nip05():
    # ANCHOR: set-metadata
    # Create metadata object with name and NIP05
    metadata = Metadata() \
        .set_name("TestName") \
        .set_nip05("TestName@rustNostr.com")
    # ANCHOR_END: set-metadata

    # ANCHOR: verify-nip05
    print("Verify NIP-05:")
    nip_05 = "yuki@yukikishimoto.com"
    public_key = PublicKey.parse("npub1drvpzev3syqt0kjrls50050uzf25gehpz9vgdw08hvex7e0vgfeq0eseet")
    proxy = None
    if await verify_nip05(public_key, nip_05, proxy):
        print(f"     '{nip_05}' verified, for {public_key.to_bech32()}")
    else:
        print(f"     Unable to verify NIP-05, for {public_key.to_bech32()}")
    # ANCHOR_END: verify-nip05

    print()

    # ANCHOR: nip05-profile
    print("Profile NIP-05:")
    nip_05 = "yuki@yukikishimoto.com"
    profile = await get_nip05_profile(nip_05)
    print(f"     {nip_05} Public key: {profile.public_key().to_bech32()}")
    # ANCHOR_END: nip05-profile

if __name__ == '__main__':
   asyncio.run(nip05())
```

## nip06.py

```python
# Leverages Python-Mnemonic package (ref implementation of BIP39) https://github.com/trezor/python-mnemonic
from mnemonic import Mnemonic
from nostr_sdk import Keys

def nip06():
    print()
    # ANCHOR: keys-from-seed24
    # Generate random Seed Phrase (24 words e.g. 256 bits entropy)
    print("Keys from 24 word Seed Phrase:")
    words = Mnemonic("english").generate(strength=256)
    passphrase = ""

    # Use Seed Phrase to generate basic Nostr keys
    keys = Keys.from_mnemonic(words, passphrase)

    print(f" Seed Words (24)  : {words}")
    print(f" Public key bech32: {keys.public_key().to_bech32()}")
    print(f" Secret key bech32: {keys.secret_key().to_bech32()}")
    # ANCHOR_END: keys-from-seed24

    print()
    # ANCHOR: keys-from-seed12
    # Generate random Seed Phrase (12 words e.g. 128 bits entropy)
    print("Keys from 12 word Seed Phrase:")
    words = Mnemonic("english").generate(strength=128)
    passphrase = ""

    # Use Seed Phrase to generate basic Nostr keys
    keys = Keys.from_mnemonic(words, passphrase)

    print(f" Seed Words (12)  : {words}")
    print(f" Public key bech32: {keys.public_key().to_bech32()}")
    print(f" Secret key bech32: {keys.secret_key().to_bech32()}")
    # ANCHOR_END: keys-from-seed12

    print()
    # ANCHOR: keys-from-seed-accounts
    # Advanced (with accounts) from the example wordlist
    words = "leader monkey parrot ring guide accident before fence cannon height naive bean"
    passphrase = ""

    print("Accounts (0-5) from 12 word Seed Phrase (with passphrase):")
    print(f" Seed Words (12): {words}")
    print(" Accounts (0-5) :")

    # Use Seed Phrase and account to multiple Nostr keys
    for account in range(0,6):
        nsec = Keys.from_mnemonic(words, passphrase, account).secret_key().to_bech32()
        print(f"     Account #{account} bech32: {nsec}")
    # ANCHOR_END: keys-from-seed-accounts

    print()
    # ANCHOR: keys-from-seed-accounts-pass
    # Advanced (with accounts) from the same wordlist with in inclusion of passphrase
    words = "leader monkey parrot ring guide accident before fence cannon height naive bean"
    passphrase = "RustNostr"
    print("Accounts (0-5) from 12 word Seed Phrase (with passphrase):")
    print(f" Seed Words (12): {words}")
    print(f" Passphrase     : {passphrase}")
    print(" Accounts (0-5) :")

    # Use Seed Phrase and account to multiple Nostr keys
    for account in range(0,6):
        nsec = Keys.from_mnemonic(words, passphrase, account).secret_key().to_bech32()
        print(f"     Account #{account} bech32: {nsec}")
    # ANCHOR_END: keys-from-seed-accounts-pass

if __name__ == '__main__':
   nip06()
```

## nip19.py

```python
from nostr_sdk import Keys, EventBuilder, Nip19Profile, Nip19, Nip19Event, Coordinate, Kind, Nip19Coordinate


def nip19():
    keys = Keys.generate()

    print()
    print("Bare keys and ids (bech32):")
    # ANCHOR: nip19-npub
    print(f" Public key: {keys.public_key().to_bech32()}")
    # ANCHOR_END: nip19-npub

    # ANCHOR: nip19-nsec
    print(f" Secret key: {keys.secret_key().to_bech32()}")
    # ANCHOR_END: nip19-nsec

    # ANCHOR: nip19-note
    event = EventBuilder.text_note("Hello from rust-nostr Python bindings!").sign_with_keys(keys)
    print(f" Event     : {event.id().to_bech32()}")
    # ANCHOR_END: nip19-note

    print()
    print("Shareable identifiers with extra metadata (bech32):")
    # ANCHOR: nip19-nprofile-encode
    # Create NIP-19 profile including relays data
    relays = ["wss://relay.damus.io"]
    nprofile = Nip19Profile(keys.public_key(),relays)
    print(f" Profile (encoded): {nprofile.to_bech32()}")
    # ANCHOR_END: nip19-nprofile-encode

    # ANCHOR: nip19-nprofile-decode
    # Decode NIP-19 profile
    decode_nprofile = Nip19.from_bech32(nprofile.to_bech32())
    print(f" Profile (decoded): {decode_nprofile}")
    # ANCHOR_END: nip19-nprofile-decode

    print()
    # ANCHOR: nip19-nevent-encode
    # Create NIP-19 event including author and relays data
    nevent = Nip19Event(event.id(), keys.public_key(), kind=None, relays=relays)
    print(f" Event (encoded): {nevent.to_bech32()}")
    # ANCHOR_END: nip19-nevent-encode

    # ANCHOR: nip19-nevent-decode
    # Decode NIP-19 event
    decode_nevent = Nip19.from_bech32(nevent.to_bech32())
    print(f" Event (decoded): {decode_nevent}")
    # ANCHOR_END: nip19-nevent-decode

    print()
    # ANCHOR: nip19-naddr-encode
    # Create NIP-19 coordinate
    coord = Coordinate(Kind(0),keys.public_key())
    coordinate = Nip19Coordinate(coord, [])
    print(f" Coordinate (encoded): {coordinate.to_bech32()}")
    # ANCHOR_END: nip19-naddr-encode

    # ANCHOR: nip19-naddr-decode
    # Decode NIP-19 coordinate
    decode_coord = Nip19.from_bech32(coordinate.to_bech32())
    print(f" Coordinate (decoded): {decode_coord}")
    # ANCHOR_END: nip19-naddr-decode


if __name__ == '__main__':
   nip19()
```

## nip21.py

```python
from nostr_sdk import Keys, PublicKey, EventBuilder, EventId, Nip21, Nip19Profile, Nip19Event, Kind, Coordinate, \
    Nip19Coordinate


def nip21():
    print()
    print("Nostr URIs:")
    # ANCHOR: npub
    keys = Keys.generate()

    # URI npub
    pk_uri = keys.public_key().to_nostr_uri()
    print(f" Public key (URI):    {pk_uri}")

    # bech32 npub
    pk_parse = Nip21.parse(pk_uri)
    if pk_parse.as_enum().is_pubkey():
        pk_bech32 = PublicKey.parse(pk_uri).to_bech32()
        print(f" Public key (bech32): {pk_bech32}")
    # ANCHOR_END: npub

    print()

    # ANCHOR: note
    event = EventBuilder.text_note("Hello from rust-nostr Python bindings!").sign_with_keys(keys)

    # URI note
    note_uri = event.id().to_nostr_uri()
    print(f" Event (URI):    {note_uri}")

    # bech32 note
    note_pasre = Nip21.parse(note_uri)
    if note_pasre.as_enum().is_note():
        event_bech32 = EventId.parse(note_uri).to_bech32()
        print(f" Event (bech32): {event_bech32}")
    # ANCHOR_END: note

    print()

    # ANCHOR: nprofile
    relays = ["wss://relay.damus.io"]
    nprofile = Nip19Profile(keys.public_key(), relays)

    # URI nprofile
    nprofile_uri = nprofile.to_nostr_uri()
    print(f" Profile (URI):    {nprofile_uri}")

    # bech32 nprofile
    nprofile_parse = Nip21.parse(nprofile_uri)
    if nprofile_parse.as_enum().is_profile():
        nprofile_bech32 = Nip19Profile.from_nostr_uri(nprofile_uri).to_bech32()
        print(f" Profile (bech32): {nprofile_bech32}")
    # ANCHOR_END: nprofile

    print()

    # ANCHOR: nevent
    relays = ["wss://relay.damus.io"]
    nevent = Nip19Event(event.id(), keys.public_key(), kind=None, relays=relays)

    # URI nevent
    nevent_uri = nevent.to_nostr_uri()
    print(f" Event (URI):    {nevent_uri}")

    # bech32 nevent
    nevent_parse = Nip21.parse(nevent_uri)
    if nevent_parse.as_enum().is_event():
        nevent_bech32 = Nip19Event.from_nostr_uri(nevent_uri).to_bech32()
        print(f" Event (bech32): {nevent_bech32}")
    # ANCHOR_END: nevent

    print()

    # ANCHOR: naddr
    coord = Coordinate(Kind(0), keys.public_key())
    coordinate = Nip19Coordinate(coord, ["wss://relay.damus.io"])

    # URI naddr
    coord_uri = coordinate.to_nostr_uri()
    print(f" Coordinate (URI): {coord_uri}")
    # ANCHOR_END: naddr

if __name__ == '__main__':
   nip21()
```

## nip44.py

```python
from nostr_sdk import Keys, PublicKey, nip44_encrypt, nip44_decrypt, Nip44Version


def nip44():
    print("\nEncrypting and Decrypting Messages (NIP-44):")
    keys = Keys.generate()

    pk = PublicKey.parse("79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798")

    ciphertext = nip44_encrypt(keys.secret_key(), pk, "my message", Nip44Version.V2)
    print(f" Encrypted: {ciphertext}")

    plaintext = nip44_decrypt(keys.secret_key(), pk, ciphertext)
    print(f" Decrypted: {plaintext}")

if __name__ == '__main__':
   nip44()
```

## nip47.py

```python
# ANCHOR: full
import asyncio
from nostr_sdk import NostrWalletConnectUri, Nwc, PayInvoiceRequest, MakeInvoiceRequest


async def main():
    # Parse NWC uri
    uri = NostrWalletConnectUri.parse("nostr+walletconnect://..")

    # Initialize NWC client
    nwc = Nwc(uri)

    # Get info
    info = await nwc.get_info()
    print(info)

    # Get balance
    balance = await nwc.get_balance()
    print(f"Balance: {balance} mSAT")

    # Pay an invoice
    params = PayInvoiceRequest(invoice = "lnbc..", id = None, amount = None)
    await nwc.pay_invoice(params)

    # Make an invoice
    params = MakeInvoiceRequest(amount = 100, description = None, description_hash = None, expiry = None)
    result = await nwc.make_invoice(params)
    print(f"Invoice: {result.invoice}")


if __name__ == '__main__':
   asyncio.run(main())
# ANCHOR_END: full

```

## nip49.py

```python
# ANCHOR: full
from nostr_sdk import SecretKey, EncryptedSecretKey, KeySecurity

def encrypt():
    # ANCHOR: parse-secret-key
    secret_key = SecretKey.parse("3501454135014541350145413501453fefb02227e449e57cf4d3a3ce05378683")
    # ANCHOR_END: parse-secret-key

    # ANCHOR: encrypt-default
    password = "nostr"
    encrypted = secret_key.encrypt(password)
    # ANCHOR_END: encrypt-default

    print(f"Encrypted secret key: {encrypted.to_bech32()}")

    # ANCHOR: encrypt-custom
    encrypted_custom = EncryptedSecretKey(secret_key, password, 12, KeySecurity.WEAK)
    # ANCHOR_END: encrypt-custom

    print(f"Encrypted secret key (custom): {encrypted_custom.to_bech32()}")

def decrypt():
    # ANCHOR: parse-ncryptsec
    encrypted = EncryptedSecretKey.from_bech32("ncryptsec1qgg9947rlpvqu76pj5ecreduf9jxhselq2nae2kghhvd5g7dgjtcxfqtd67p9m0w57lspw8gsq6yphnm8623nsl8xn9j4jdzz84zm3frztj3z7s35vpzmqf6ksu8r89qk5z2zxfmu5gv8th8wclt0h4p")
    # ANCHOR_END: parse-ncryptsec

    # ANCHOR: decrypt
    secret_key = encrypted.decrypt("nostr")
    # ANCHOR_END: decrypt

    print(f"Decrypted secret key: {secret_key.to_bech32()}")


if __name__ == '__main__':
   encrypt()
   decrypt()
# ANCHOR_END: full

```

## nip59.py

```python
import asyncio
from nostr_sdk import Keys, EventBuilder, Event, gift_wrap, UnwrappedGift, UnsignedEvent, NostrSigner


async def nip59():
    print("\nGift Wrapping (NIP-59):")
    # Sender Keys
    alice_keys = Keys.parse("5c0c523f52a5b6fad39ed2403092df8cebc36318b39383bca6c00808626fab3a")
    alice_signer = NostrSigner.keys(alice_keys)

    # Receiver Keys
    bob_keys = Keys.parse("nsec1j4c6269y9w0q2er2xjw8sv2ehyrtfxq3jwgdlxj6qfn8z4gjsq5qfvfk99")
    bob_signer = NostrSigner.keys(bob_keys)

    # Compose rumor
    rumor: UnsignedEvent = EventBuilder.text_note("Test").build(alice_keys.public_key())

    # Build gift wrap with sender keys
    gw: Event = await gift_wrap(alice_signer, bob_keys.public_key(), rumor)
    print(f" Gift Wrap:\n{gw.as_json()}")

    # Extract rumor from gift wrap with receiver keys
    print("\n Unwrapped Gift:")
    unwrapped_gift = await UnwrappedGift.from_gift_wrap(bob_signer, gw)
    sender = unwrapped_gift.sender()
    unwrapped_rumor: UnsignedEvent = unwrapped_gift.rumor()
    print(f"     Sender: {sender.to_bech32()}")
    print(f"     Rumor: {unwrapped_rumor.as_json()}")

if __name__ == '__main__':
   asyncio.run(nip59())
```

## nip65.py

```python
from nostr_sdk import EventBuilder, Tag, Kind, Keys, RelayMetadata


def nip65():
    # Get Keys
    keys = Keys.generate()

    print()
    print("Relay Metadata:")
    # ANCHOR: relay-metadata-simple
    # Create relay dictionary
    relays_dict = {
        "wss://relay.damus.io": RelayMetadata.READ,
        "wss://relay.primal.net": RelayMetadata.WRITE,
        "wss://relay.nostr.band": None
    }

    # Build/sign event
    builder = EventBuilder.relay_list(relays_dict)
    event = builder.sign_with_keys(keys)

    # Print event as json
    print(f" Event: {event.as_json()}")
    # ANCHOR_END: relay-metadata-simple

    print()

    # ANCHOR: relay-metadata-custom
    # Create relay metadata tags
    tag1 = Tag.relay_metadata("wss://relay.damus.io", RelayMetadata.READ)
    tag2 = Tag.relay_metadata("wss://relay.primal.net", RelayMetadata.WRITE)
    tag3 = Tag.relay_metadata("wss://relay.nostr.band", None)

    # Build/sign event
    kind = Kind(10002)
    builder = EventBuilder(kind = kind, content = "").tags([tag1, tag2, tag3])
    event = builder.sign_with_keys(keys)

    # Print event as json
    print(f" Event: {event.as_json()}")
    # ANCHOR_END: relay-metadata-custom

if __name__ == '__main__':
   nip65()
```

## timestamps.py

```python
from nostr_sdk import Timestamp, EventBuilder, Keys, Kind, gift_wrap, Tag


def timestamps():
    # Generate keys and Events
    alice_keys = Keys.generate()

    print()
    print("Timestamps:")

    # ANCHOR: timestamp-now
    print("  Simple timestamp (now):")
    timestamp = Timestamp.now()
    print(f"     As str: {timestamp.to_human_datetime()}")
    print(f"     As int: {timestamp.as_secs()}")
    # ANCHOR_END: timestamp-now

    print()
    # ANCHOR: timestamp-parse
    print("  Parse timestamp (sec):")
    timestamp = Timestamp.from_secs(1718737479)
    print(f"     {timestamp.to_human_datetime()}")
    # ANCHOR_END: timestamp-parse

    print()
    # ANCHOR: timestamp-created
    print("  Created at timestamp:")
    event = EventBuilder(Kind(1), "This is some event text.").custom_created_at(timestamp).sign_with_keys(alice_keys)
    print(f"     Created at: {event.created_at().to_human_datetime()}")
    # ANCHOR_END: timestamp-created

    print()
    # ANCHOR: timestamp-tag
    print("  Timestamp Tag:")
    tag = Tag.expiration(timestamp)
    print(f"     Tag: {tag.as_standardized()}")
    # ANCHOR_END: timestamp-tag

if __name__ == '__main__':
   timestamps()
```

## client.py

```python
from typing import cast
from nostr_sdk import Keys, EventBuilder, ClientMessage, Filter, ClientMessageEnum


def client_message():
    keys = Keys.generate()
    event = EventBuilder.text_note("TestTextNoTe").sign_with_keys(keys)

    print()
    print("Client Messages:")

    # ANCHOR: event-message
    # Event client message
    print("  Event Client Message:")
    message = ClientMessage.event(event)
    print(f"     - Event Message: {message.as_enum().is_event_msg()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: event-message

    print()
    # ANCHOR: req-message
    # Request client message
    print("  Request Client Message:")
    f = Filter().id(event.id())
    message = ClientMessage.req(subscription_id="ABC123", filter=f)
    print(f"     - Request Message: {message.as_enum().is_req()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: req-message

    print()
    # ANCHOR: close-message
    # Close client message
    print("  Close Client Message:")
    message = ClientMessage.close("ABC123")
    print(f"     - Close Message: {message.as_enum().is_close()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: close-message

    print()
    # ANCHOR: parse-message
    # Parse Messages from JSON and/or Enum
    print("  Parse Client Messages:")
    message = ClientMessage.from_json('["REQ","ABC123",{"#p":["421a4dd67be773903f805bcb7975b4d3377893e0e09d7563b8972ee41031f551"]}]')
    print(f"     - ENUM: {message.as_enum()}")
    f = Filter().pubkey(keys.public_key())
    message = ClientMessage.from_enum(cast(ClientMessageEnum, ClientMessageEnum.REQ("ABC123", filter=f)))
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: parse-message

    print()
    # ANCHOR: auth-message
    # Auth client message  (NIP42)
    print("  Auth Client Message:")
    message = ClientMessage.auth(event)
    print(f"     - Auth Message: {message.as_enum().is_auth()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: auth-message

    print()
    # ANCHOR: count-message
    # Count client message (NIP45)
    print("  Count Client Message:")
    f = Filter().pubkey(keys.public_key())
    message = ClientMessage.count(subscription_id="ABC123", filter=f)
    print(f"     - Count Message: {message.as_enum().is_count()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: count-message

    print()
    # ANCHOR: neg-open
    # Negative Open Message
    print("  Negative Client Message (open):")
    message = ClientMessage.from_enum(cast(ClientMessageEnum, ClientMessageEnum.NEG_OPEN("ABC123", filter=f, id_size=32, initial_message="<hex-msg>")))
    print(f"     - Negative Error Open: {message.as_enum().is_neg_open()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: neg-open

    print()
    # ANCHOR: neg-close
    # Negative Close Message
    print("  Negative Client Message (close):")
    message = ClientMessage.from_enum(cast(ClientMessageEnum, ClientMessageEnum.NEG_CLOSE("ABC123")))
    print(f"     - Negative Error Close: {message.as_enum().is_neg_close()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: neg-close

    print()
    # ANCHOR: neg-msg
    # Negative Error Message
    print("  Negative Client Message (message):")
    enum_msg = ClientMessageEnum.NEG_MSG("ABC123", message="This is not the message you are looking for")
    message = ClientMessage.from_enum(cast(ClientMessageEnum, enum_msg))
    print(f"     - JSON: {message.as_json()}")
    print(f"     - Negative Error Message: {message.as_enum().is_neg_msg()}")
    # ANCHOR_END: neg-msg

if __name__ == '__main__':
   client_message()
```

## filters.py

```python
from nostr_sdk import Filter, FilterRecord, Keys, Kind, EventBuilder, Timestamp, Tag
import time, datetime


def filters():
    # Generate keys and Events
    keys = Keys.generate()
    keys2 = Keys.generate()
    event = EventBuilder.text_note("Hello World!").sign_with_keys(keys)
    event2 = EventBuilder(Kind(1), "Goodbye World!").tags([Tag.identifier("Identification D Tag")]).sign_with_keys(keys2)

    print()
    print("Creating Filters:")

    # ANCHOR: create-filter-id
    # Filter for specific ID
    print("  Filter for specific Event ID:")
    f = Filter().id(event.id())
    print(f"     {f.as_json()}")
    # ANCHOR_END: create-filter-id

    print()
    # ANCHOR: create-filter-author
    # Filter for specific Author
    print("  Filter for specific Author:")
    f = Filter().author(keys.public_key())
    print(f"     {f.as_json()}")
    # ANCHOR_END: create-filter-author

    print()
    # ANCHOR: create-filter-kind-pk
    # Filter by PK and Kinds
    print("  Filter with PK and Kinds:")
    f = Filter()\
        .pubkey(keys.public_key())\
        .kind(Kind(1))
    print(f"     {f.as_json()}")
    # ANCHOR_END: create-filter-kind-pk

    print()
    # ANCHOR: create-filter-search
    # Filter for specific string
    print("  Filter for specific search string:")
    f = Filter().search("Ask Nostr Anything")
    print(f"     {f.as_json()}")
    # ANCHOR_END: create-filter-search

    print()
    # ANCHOR: create-filter-timeframe
    print("  Filter for events from specific public key within given timeframe:")
    # Create timestamps
    date = datetime.datetime(2009, 1, 3, 0, 0)
    timestamp = int(time.mktime(date.timetuple()))
    since_ts = Timestamp.from_secs(timestamp)
    until_ts = Timestamp.now()

    # Filter with timeframe
    f = Filter()\
        .pubkey(keys.public_key())\
        .since(since_ts)\
        .until(until_ts)
    print(f"     {f.as_json()}")
    # ANCHOR_END: create-filter-timeframe

    print()
    # ANCHOR: create-filter-limit
    # Filter for specific PK with limit
    print("  Filter for specific Author, limited to 10 Events:")
    f = Filter()\
        .author(keys.public_key())\
        .limit(10)
    print(f"     {f.as_json()}")
    # ANCHOR_END: create-filter-limit

    print()
    # ANCHOR: create-filter-hashtag
    # Filter for Hashtags
    print("  Filter for a list of Hashtags:")
    f = Filter().hashtags(["#Bitcoin", "#AskNostr", "#Meme"])
    print(f"     {f.as_json()}")
    # ANCHOR_END: create-filter-hashtag

    print()
    # ANCHOR: create-filter-reference
    # Filter for Reference
    print("  Filter for a Reference:")
    f = Filter().reference("This is my NIP-12 Reference")
    print(f"     {f.as_json()}")
    # ANCHOR_END: create-filter-reference

    print()
    # ANCHOR: create-filter-identifier
    # Filter for Identifier
    print("  Filter for a Identifier:")
    identifier = event2.tags().identifier()
    if identifier is not None:
        f = Filter().identifier(identifier)
        print(f"     {f.as_json()}")
    # ANCHOR_END: create-filter-identifier

    print()
    print("Modifying Filters:")
    # ANCHOR: modify-filter
    # Modifying Filters (adding/removing)
    f = Filter()\
        .pubkeys([keys.public_key(), keys2.public_key()])\
        .ids([event.id(), event2.id()])\
        .kinds([Kind(0), Kind(1)])\
        .author(keys.public_key())

    # Add an additional Kind to existing filter
    f = f.kinds([Kind(4)])

    # Print Results
    print("  Before:")
    print(f"     {f.as_json()}")
    print()

    # Remove PKs, Kinds and IDs from filter
    f = f.remove_pubkeys([keys2.public_key()])
    print(" After (remove pubkeys):")
    print(f"     {f.as_json()}")

    f = f.remove_kinds([Kind(0), Kind(4)])
    print("  After (remove kinds):")
    print(f"     {f.as_json()}")

    f = f.remove_ids([event2.id()])
    print("  After (remove IDs):")
    print(f"     {f.as_json()}")
    # ANCHOR_END: modify-filter

    print()
    print("Other Filter Operations:")
    # ANCHOR: other-parse
    # Parse filter
    print("  Parse Filter from Json:")
    f_json = f.as_json()
    f = Filter().from_json(f_json)
    print(f"     {f.as_record()}")
    # ANCHOR_END: other-parse

    print()
    # ANCHOR: other-record
    print("  Construct Filter Record and extract author:")
    # Filter Record
    fr = FilterRecord(ids=[event.id()],authors=[keys.public_key()], kinds=[Kind(0)], search="", since=None, until=None, limit=1, generic_tags=[])
    f = Filter().from_record(fr)
    print(f"     {f.as_json()}")
    # ANCHOR_END: other-record

    print()
    # ANCHOR: other-match
    print("  Logical tests:")
    f = Filter().author(keys.public_key()).kind(Kind(1))
    print(f"     Event match for filter: {f.match_event(event)}")
    print(f"     Event2 match for filter: {f.match_event(event2)}")
    # ANCHOR_END: other-match

if __name__ == '__main__':
   filters()
```

## relay.py

```python
from typing import cast
from nostr_sdk import RelayMessage, RelayMessageEnum, EventBuilder, Keys


def relay_message():

    keys = Keys.generate()
    event = EventBuilder.text_note("TestTextNoTe").sign_with_keys(keys)

    print()
    print("Relay Messages:")

    # ANCHOR: event-message
    # Create Event relay message
    print("  Event Relay Message:")
    message = RelayMessage.event("subscription_ID_abc123", event)
    print(f"     - Event Message: {message.as_enum().is_event_msg()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: event-message

    print()
    # ANCHOR: ok-message
    # Create event acceptance relay message
    print("  Event Acceptance Relay Message:")
    message = RelayMessage.ok(event.id(), False, "You have no power here, Gandalf The Grey")
    print(f"     - Event Acceptance Message: {message.as_enum().is_ok()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: ok-message

    print()
    # ANCHOR: eose-message
    # Create End of Stored Events relay message
    print("  End of Stored Events Relay Message:")
    message = RelayMessage.eose("subscription_ID_abc123")
    print(f"     - End of Stored Events Message: {message.as_enum().is_end_of_stored_events()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: eose-message

    print()
    # ANCHOR: closed-message
    # Create Closed relay message
    print("  Closed Relay Message:")
    message = RelayMessage.closed("subscription_ID_abc123", "So long and thanks for all the fish")
    print(f"     - Closed Message: {message.as_enum().is_closed()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: closed-message

    print()
    # ANCHOR: notice-message
    # Create Notice relay message
    print("  Notice Relay Message:")
    message = RelayMessage.notice("You have been served")
    print(f"     - Notice Message: {message.as_enum().is_notice()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: notice-message

    print()
    # ANCHOR: parse-message
    # Parse Messages from JSON and/or Enum
    print("  Parse Relay Messages:")
    message = RelayMessage.from_json('["NOTICE","You have been served"]')
    print(f"     - ENUM: {message.as_enum()}")
    message = RelayMessage.from_enum(cast(RelayMessageEnum, RelayMessageEnum.NOTICE("You have been served")))
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: parse-message

    print()
    # ANCHOR: auth-message
    # Create Authorization relay message (NIP42)
    print("  Auth Relay Message:")
    message = RelayMessage.auth("I Challenge You To A Duel! (or some other challenge string)")
    print(f"     - Auth Message: {message.as_enum().is_auth()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: auth-message

    print()
    # ANCHOR: count-message
    # Create Count relay message (NIP45)
    print("  Count Relay Message:")
    message = RelayMessage.count("subscription_ID_abc123", 42)
    print(f"     - Count Message: {message.as_enum().is_count()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: count-message

    print()
    # ANCHOR: neg-code
    # Negative Error Code
    print("  Negative Relay Message (code):")
    relay_message_neg = RelayMessageEnum.NEG_ERR("subscription_ID_abc123", "404")
    message = RelayMessage.from_enum(cast(RelayMessageEnum, relay_message_neg))
    print(f"     - Negative Error Code: {message.as_enum().is_neg_err()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: neg-code

    print()
    # ANCHOR: neg-msg
    # Negative Error Message
    print("  Negative Relay Message (message):")
    relay_message_neg = RelayMessageEnum.NEG_MSG("subscription_ID_abc123", "This is not the message you are looking for")
    message = RelayMessage.from_enum(cast(RelayMessageEnum, relay_message_neg))
    print(f"     - Negative Error Message: {message.as_enum().is_neg_msg()}")
    print(f"     - JSON: {message.as_json()}")
    # ANCHOR_END: neg-msg

if __name__ == '__main__':
   relay_message()
```

## builder.py

```python
# ANCHOR: full
import asyncio
from nostr_sdk import Keys, EventBuilder, Kind, Tag, NostrSigner, Timestamp


async def sign_and_print(signer: NostrSigner, builder: EventBuilder):
    # ANCHOR: sign
    event = await builder.sign(signer)
    # ANCHOR_END: sign

    print(event.as_json())


async def event_builder():
    keys = Keys.generate()
    signer = NostrSigner.keys(keys)

    # ANCHOR: standard
    builder1 = EventBuilder.text_note("Hello")
    # ANCHOR_END: standard

    await sign_and_print(signer, builder1)

    # ANCHOR: std-custom
    tag = Tag.alt("POW text-note")
    custom_timestamp = Timestamp.from_secs(1737976769)
    builder2 = EventBuilder.text_note("Hello with POW").tags([tag]).pow(20).custom_created_at(custom_timestamp)
    # ANCHOR_END: std-custom

    await sign_and_print(signer, builder2)

    # ANCHOR: custom
    kind = Kind(33001)
    builder3 = EventBuilder(kind, "My custom event")
    # ANCHOR_END: custom

    await sign_and_print(signer, builder3)

if __name__ == '__main__':
   asyncio.run(event_builder())
# ANCHOR_END: full

```

## id.py

```python
from nostr_sdk import EventId, Keys, Timestamp, Kind, EventBuilder, Tags


def event_id():
    keys = Keys.generate()

    print()
    print("Event ID:")

    # ANCHOR: build-event-id
    print("  Build Event ID:")
    event_id = EventId(keys.public_key(), Timestamp.now(), Kind(1), Tags(), "content")
    print(f"     - {event_id}")
    # ANCHOR_END: build-event-id

    print()
    # ANCHOR: format-parse-hex
    # To Hex and then Parse
    print("  Event ID (hex):")
    event_id_hex = event_id.to_hex()
    print(f"     - Hex: {event_id_hex}")
    print(f"     - Parse: {EventId.parse(event_id_hex)}")
    # ANCHOR_END: format-parse-hex

    print()
    # ANCHOR: format-parse-bech32
    # To Bech32 and then Parse
    print("  Event ID (bech32):")
    event_id_bech32 = event_id.to_bech32()
    print(f"     - Bech32: {event_id_bech32}")
    print(f"     - Parse: {EventId.parse(event_id_bech32)}")
    # ANCHOR_END: format-parse-bech32

    print()
    # ANCHOR: format-parse-nostr-uri
    # To Nostr URI and then Parse
    print("  Event ID (nostr uri):")
    event_id_nostr_uri = event_id.to_nostr_uri()
    print(f"     - Nostr URI: {event_id_nostr_uri}")
    print(f"     - Parse: {EventId.parse(event_id_nostr_uri)}")
    # ANCHOR_END: format-parse-nostr-uri

    print()
    # ANCHOR: format-parse-bytes
    # As Bytes and then Parse
    print("  Event ID (bytes):")
    event_id_bytes = event_id.as_bytes()
    print(f"     - Bytes: {event_id_bytes}")
    print(f"     - From Bytes: {EventId.from_bytes(event_id_bytes)}")
    # ANCHOR_END: format-parse-bytes

    print()
    # ANCHOR: access-verify
    # Event ID from Event & Verfiy
    print("  Event ID from Event & Verify:")
    event = EventBuilder.text_note("This is a note").sign_with_keys(keys)
    print(f"     - Event ID: {event.id()}")
    print(f"     - Verify the ID & Signature: {event.verify()}")
    # ANCHOR_END: access-verify

if __name__ == '__main__':
   event_id()
```

## json.py

```python
# ANCHOR: full
from nostr_sdk import Event

def event_json():
    json = '{"content":"uRuvYr585B80L6rSJiHocw==?iv=oh6LVqdsYYol3JfFnXTbPA==","created_at":1640839235,"id":"2be17aa3031bdcb006f0fce80c146dea9c1c0268b0af2398bb673365c6444d45","kind":4,"pubkey":"f86c44a2de95d9149b51c6a29afeabba264c18e2fa7c49de93424a0c56947785","sig":"a5d9290ef9659083c490b303eb7ee41356d8778ff19f2f91776c8dc4443388a64ffcf336e61af4c25c05ac3ae952d1ced889ed655b67790891222aaa15b99fdd","tags":[["p","13adc511de7e1cfcf1c6b7f6365fb5a03442d7bcacf565ea57fa7770912c023d"]]}'

    # ANCHOR: deserialize
    event = Event.from_json(json)
    # ANCHOR_END: deserialize

    # ANCHOR: serialize
    json = event.as_json()
    # ANCHOR_END: serialize

    print(json)

if __name__ == '__main__':
   event_json()
# ANCHOR_END: full

```

## kind.py

```python
from nostr_sdk import Kind, KindStandard, EventBuilder, Keys, Metadata


def kind():
    print()
    keys = Keys.generate()
    print("Kind:")

    # ANCHOR: kind-int
    print("  Kind from integer:")
    kind = Kind(1)
    print(f"     - Kind 1: {kind.as_std()}")
    kind = Kind(0)
    print(f"     - Kind 0: {kind.as_std()}")
    kind = Kind(3)
    print(f"     - Kind 3: {kind.as_std()}")
    # ANCHOR_END: kind-int

    print()
    # ANCHOR: kind-enum
    print("  Kind from enum:")
    kind = Kind.from_std(KindStandard.TEXT_NOTE)
    print(f"     - Kind TEXT_NOTE: {kind.as_u16()}")
    kind = Kind.from_std(KindStandard.METADATA)
    print(f"     - Kind METADATA: {kind.as_u16()}")
    kind = Kind.from_std(KindStandard.CONTACT_LIST)
    print(f"     - Kind CONTRACT_LIST: {kind.as_u16()}")
    # ANCHOR_END: kind-enum

    print()
    # ANCHOR: kind-methods
    print("  Kind methods EventBuilder:")
    event  = EventBuilder.text_note("This is a note").sign_with_keys(keys)
    print(f"     - Kind text_note(): {event.kind().as_u16()} - {event.kind().as_std()}")
    event  = EventBuilder.metadata(Metadata()).sign_with_keys(keys)
    print(f"     - Kind metadata(): {event.kind().as_u16()} - {event.kind().as_std()}")
    event  = EventBuilder.contact_list([]).sign_with_keys(keys)
    print(f"     - Kind contact_list(): {event.kind().as_u16()} - {event.kind().as_std()}")
    # ANCHOR_END: kind-methods

    print()
    # ANCHOR: kind-representations
    kind = Kind(1337)
    print(f"Custom Event Kind: {kind.as_u16()} - {kind.as_std()}")
    # ANCHOR_END: kind-representations

    print()
    # ANCHOR: kind-tests
    print("  Kind Logical Tests:")
    kind = Kind(30001)
    print(f"     - Is {kind.as_u16()} addressable?: {kind.is_addressable()}")
    kind = Kind(20001)
    print(f"     - Is {kind.as_u16()} ephemeral?: {kind.is_ephemeral()}")
    kind = Kind(5001)
    print(f"     - Is {kind.as_u16()} job request?: {kind.is_job_request()}")
    kind = Kind(6001)
    print(f"     - Is {kind.as_u16()} job result?: {kind.is_job_result()}")
    kind = Kind(1)
    print(f"     - Is {kind.as_u16()} regular?: {kind.is_regular()}")
    kind = Kind(10001)
    print(f"     - Is {kind.as_u16()} relay replaceable?: {kind.is_replaceable()}")
    # ANCHOR_END: kind-tests

if __name__ == '__main__':
   kind()
```

## tags.py

```python
from typing import cast
from nostr_sdk import EventBuilder, Keys, Tag, Contact, Coordinate, Kind, RelayMetadata, TagKind


def tags():
    # Generate keys and events
    keys = Keys.generate()
    event = EventBuilder.contact_list([Contact(public_key=keys.public_key(), relay_url=None, alias=None)]).sign_with_keys(keys)

    print()
    print("Tags:")

    # ANCHOR: single-letter
    print("  Single Letter Tags:")
    # Event ID (hex)
    tag = Tag.event(event.id())
    print(f"     - Event ID (hex)     : {tag.as_vec()}")
    # Public Key (hex)
    tag = Tag.public_key(keys.public_key())
    print(f"     - Public Key (hex)   : {tag.as_vec()}")
    # Coordinate to event
    tag = Tag.coordinate(Coordinate(Kind(0), keys.public_key()))
    print(f"     - Coordinate to event: {tag.as_vec()}")
    # Identifier
    tag = Tag.identifier("This is an identifier value")
    print(f"     - Identifier         : {tag.as_vec()}")
    # Reference/Relay
    tag = Tag.relay_metadata("wss://relay.example.com",RelayMetadata.READ)
    print(f"     - Reference/Relays   : {tag.as_vec()}")
    # Hashtag
    tag = Tag.hashtag("#AskNostr")
    print(f"     - Hashtag            : {tag.as_vec()}")
    # ANCHOR_END: single-letter

    print()
    # ANCHOR: custom
    print("  Custom Tags:")
    tag = Tag.custom(cast(TagKind, TagKind.SUMMARY()), ["This is a summary"])
    print(f"     - Summary    : {tag.as_vec()}")
    tag = Tag.custom(cast(TagKind, TagKind.AMOUNT()), ["42"])
    print(f"     - Amount     : {tag.as_vec()}")
    tag = Tag.custom(cast(TagKind, TagKind.TITLE()), ["This is a title"])
    print(f"     - Title      : {tag.as_vec()}")
    tag = Tag.custom(cast(TagKind, TagKind.SUBJECT()), ["This is a subject"])
    print(f"     - Subject    : {tag.as_vec()}")
    tag = Tag.custom(cast(TagKind, TagKind.DESCRIPTION()), ["This is a description"])
    print(f"     - Description: {tag.as_vec()}")
    tag = Tag.custom(cast(TagKind, TagKind.URL()), ["https://example.com"])
    print(f"     - URL        : {tag.as_vec()}")
    # ANCHOR_END: custom

    print()
    # ANCHOR: parse
    print("  Parsing Tags:")
    tag = Tag.parse(["L","Label Namespace"])
    print(f"     - Label Namespace: {tag.as_vec()}")
    tag = Tag.parse(["l","Label Value"])
    print(f"     - Label Value    : {tag.as_vec()}")
    # ANCHOR_END: parse

    print()
    # ANCHOR: access
    print("  Working with Tags:")
    tag = Tag.public_key(keys.public_key())
    print(f"     - Kind     : {tag.kind()}")
    print(f"     - Letter   : {tag.single_letter_tag()}")
    print(f"     - Content  : {tag.content()}")
    print(f"     - As Std   : {tag.as_standardized()}")
    print(f"     - As Vector: {tag.as_vec()}")
    # ANCHOR_END: access

    print()
    # ANCHOR: logical
    print("  Logical Tests:")
    tag = Tag.custom(cast(TagKind, TagKind.SUMMARY()), ["This is a summary"])
    print(f"     - Tag1 (Title?)  : {tag.kind().is_title()}")
    print(f"     - Tag1 (Summary?): {tag.kind().is_summary()}")
    # ANCHOR_END: logical

if __name__ == '__main__':
   tags()
```

