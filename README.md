# Vault of Digital Memories

Me:

> *Hey, my dear AI assistant!\
>\
> I'm planning to build a digital vault. The purpose of this project is to collect and package all digital memories, photos, videos, digitised documents into a digital vault so that my family can inherit it later in life. Please suggest methods, technologies, equipment that should be used. Also suggest digital formats that stand the test of time.*

AI:

> *Building a digital vault for preserving digital memories, photos, videos, and digitized documents is a thoughtful and lasting gift. Here are some methods, technologies, equipment, and digital formats that can help you ensure the longevity and accessibility of your digital vault: ...*

:)

Not so fast! Let's pause for a moment.

The REAL goal of this project is to build a `pre-processor` for the digital vault.

## What's a pre-processor, and why do we need one?

To be able to build a succesful digital vault, we need to ensure that the digital assets stored in the vault stand the test of time. Various DAM (Digital Asset Management) systems will come and go, instead of focusing on those, let's focus on the source.

*Always focus on the source!*

Similarly to some of the core Unix design principles and [philosophy](https://en.wikipedia.org/wiki/Unix_philosophy), like "[everything is a file](https://en.wikipedia.org/wiki/Everything_is_a_file)", or "make each program do one thing well", longevity can only be strengthened by focusing on the most basic formats:

- plain text (markdown is also fine)
- most popular and widespread image formats (JPEG, PNG, GIF, WebP)
- most popular and widespread video formats (MP4, WebM)
- most popular and widespread audio formats (MP3, FLAC)
- most popular and widespread document formats (PDF, DOCX, ODT)
- most popular and widespread archive formats (ZIP, TAR, 7Z)
- ...

The list goes on.

Will these formats be around in 100 years? I cannot tell.

Pre-processing is required to ensure that BEFORE a digital vault is built "inside" a DAM system, all digital assets are kept organized in the most basic formats. This also ensures portability (any DAM system can import these formats).

This is the goal of this project:

To

- collect
- organize
- deduplicate
- enrich (with metadata)
- rename
- package

digital files into a vault that can be easily imported into ANY DAM system.

As an end result, we will have a digital vault that's organized (based on time), deduplicated, all files renamed to have human-readable, understandable names, enriched with metadata, and ready to be imported into ANY DAM system.

---
