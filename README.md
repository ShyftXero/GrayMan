# PhantomJack
c2 framework
## Objectives
- support multiple failover c2 mechanisms by leveraging http redirectors
  - multiple randomly selected http channels
  - multiple dns channels
- c2 channels selected by degree of interactivity and data directionality
  - Long-haul servers for "aliveness"
  - burnable interactive servers
  - separate inbound and outbound traffic. 
- Leverage well-known and trusted platforms (twitter, etc.) for c2 issuance
