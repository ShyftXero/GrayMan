# Grayman
C2 framework trying to be sneaky
https://en.wikipedia.org/wiki/Everyday_carry#Grey_man_theory

## Objectives
- support multiple failover c2 mechanisms by leveraging a pluggable model. 
  - multiple randomly selected http channels
  - multiple dns channels
  - easily issue a migration to a new channel or deprecate a channel 
- payload keying and targeting
- c2 channels selected by degree of interactivity and data directionality
  - Long-haul servers for "aliveness"
  - burnable interactive servers
  - separate inbound and outbound traffic. 
- Leverage well-known and trusted platforms (twitter, facebook, amazon, discord, etc.) for c2 issuance
- e2e pluggable encryption
  - static aes keys 
  - random aes keys require all clients to use a brute-force decryption method. slow down analysis.  

