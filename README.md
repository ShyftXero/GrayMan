# GrayMan
C2 framework trying to be sneaky
https://en.wikipedia.org/wiki/Everyday_carry#Grey_man_theory

## Objectives
- support multiple failover c2 mechanisms by leveraging a pluggable model. 
  - multiple randomly selected http channels
  - multiple dns channels
  - easily issue a migration to a new channel or deprecate/demote a channel 
- time-based heirarchy of trust. (older agents/channels are more trust-worthy)
- payload keying and instruction targeting
- c2 channels selected by degree of interactivity and data directionality
  - Long-haul servers for "aliveness"
  - burnable interactive servers
  - separate inbound and outbound traffic. 
- Leverage well-known and trusted platforms (twitter, facebook, amazon, discord, etc.) for c2 issuance
- e2e pluggable encryption
  - static aes keys 
  - random aes keys require all clients to use a brute-force decryption method. slow down analysis.  
    - 65536 possible aes keys. 
    - ![image](https://user-images.githubusercontent.com/1275714/155751523-de60d4c5-dee5-4a95-81c5-c1ae84d3bbf1.png)



## command distribution and pickup channels (c2 command issuance and collection)
separate the distribution and collection
All comms should be encrypted 
Most of these should support bidirectional communications. 
- publicly shared/editable google docs/sheets/presentations   
- torpaste
  - https://torpastezr7464pevuvdjisbvaf4yqi4n7sgz7lkwgqwxznwy5duj4ad.onion (tor)
  
- anonfile - https://anonfiles.com/
- pastebin
  - https://paste.centos.org/
  - https://pastebin.mozilla.org/
  - https://justpaste.it/
  - https://pastebin.com
  - https://controlc.com/
  - https://rentry.co/
  - http://zerobinftagjpeeebbvyzjcqyjpmjvynj5qlexwyxe7l3vqejxnqv5qd.onion 
  - paste search site - https://pastebin.ga/
- telegraph - https://telegra.ph/
