# biauek

## Installation

```bash
python3 -m pip install biauek
```

## Usage

CLI:

```bash
biauek -i post "hej nocna" -f "/home/anon/anime.jpg"
```

Library:

```python
import asyncio
import biauek

async def main():
    LOGIN = "CT%3A%3A...fedcba9876543210deadbeef" 

    async with biauek.Session(LOGIN) as session:
        attachment = await session.attach_file("/home/anon/anime.jpg")
        await session.post("hej nocna", attachment)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
```