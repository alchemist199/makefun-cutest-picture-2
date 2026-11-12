# cutest-picture-01 entry

A tiny orange kitten with huge round amber eyes, wearing a hand-knitted
cream sweater, in soft warm morning light. The picture ships in the repo
as `entry.png` — a 1024x683 PNG of 865,343 bytes, inside the 1 MiB and
1024x1024 limits. `main.py` checks the image and copies it unchanged to
`/output/`.

Two runs produce byte-identical output. Standard library only, no network.

Revision 2: the program now also accepts a JPEG (`entry.jpg`) when no PNG
is present, and verifies the file is complete — a PNG must end with its
IEND chunk, a JPEG with its EOI marker — instead of trusting the header
alone.
