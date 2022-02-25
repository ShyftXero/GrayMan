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
    -



## Separte C2 command distribution and collection channels
We should separate the distribution and collection to help obfuscate the flow of information. 

## Commands and responses
plaintext job 
```json
{
   "valid":true,
   "timestamp":1645804244,
   "target":"uuid_here",
   "targettags":[
      "tag1",
      "tag2"
   ],
   "jobid":"uuid_here",
   "comment_for_command":"command is hex-encoded",
   "command":"646174652626686f73746e616d652626696426266375726c206966636f6e6669672e6d65"
}
```
![image](https://user-images.githubusercontent.com/1275714/155760709-de7a6559-2ca2-49fd-9462-c8874db4a86e.png)



plaintext job issued encrypted with `1337deadbeefRAND` where `RAND` is four base16 chars
```
d77208cdbaf40a8e088bf4258f6338ff39d23bcb47eb7c4d8bfc74b895ab9c02a7ad0b91353f6e3f48ff90d0e729deae7f477b83e55f5449d5e114e9e5dc79745eaf1546eb7383d569f0be73539e6e597fa7a7090a166bbb2a2f5ebe23b1b7b356209d4a9f5f796d5b669d2016087d16f97f09d9b42a5efae9f1bf10b7c0e9ec1885f509941723f77bbe06729be08b927e2b4c7f4e76d2729d0194c29801cfb0c16b0ed4d41c62e23ec48ffdaf3019f118cb88fbd86172fe979489
```

plaintext response from agent
```json
{
   "valid":true,
   "timestamp":1645804244,
   "host":"uuid_here",
   "jobid":"uuid_here",
   "partid":1,
   "partcount":1337,
   "payload":"3e993a3e199713d975c569bc9b79e9dab7e3cb7d6e25131bf70d2655683015f1b4a8909890bc65bea5672e8c081b51bfe4f8539c83ed10b023630ce278f1e2ec6496daa951edcfb0593fc1a7ae4000d3"
}
```
![image](https://user-images.githubusercontent.com/1275714/155760894-548f21a3-55e2-48ea-a1fc-3a7ff570c98c.png)



All comms should be encrypted. 
Most of these should support bidirectional communications. 

There is an emphasis on http-based channels for ease of implementation but other mechanisms should be considered as well. 
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
