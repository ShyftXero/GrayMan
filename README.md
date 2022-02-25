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

![image](https://user-images.githubusercontent.com/1275714/155774308-b9031a91-93e9-40c5-9b79-6490d8c542ae.png)


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
   "payload":"467269204665622032352031313a32323a333520414d2043535420323032320d0a61646d696e6973747261746f720d0a7569643d3130303028736879667429206769643d31303030287368796674292067726f7570733d31303030287368796674292c342861646d292c3230286469616c6f7574292c3234286364726f6d292c3237287375646f292c333028646970292c343628706c7567646576292c313232286c7061646d696e292c313331286c7864292c3133322873616d62617368617265292c3133332877697265736861726b292c313337286c696276697274292c3939362876626f787573657273292c39393828646f636b6572290d0a37302e3137382e3131312e313937"
}
```
encrypted response from implant
```
d77208cdbaf40a8e088bf4258f6338ff39d23bcb47eb7c4d8bfc74b895ab9c02a7ad0b91353f6e3f48ff90d0e729deae7f47678de44c1307d5ae43f5f4ea754e29e4658b1cfbb00899ca9cd4ef52ee76a474810b177659774be6f32c1abaef3969c289ea15683cfa783f00ffa8c74b1eda9858e0826bd83818f09132420c8b94733d2e19e15e7d2eee1a53a9f2faaf63467f42e29ce055e7d0a086358a751a5474d62b69ebd87de6992a4c614bc4b4a1684caa50cb3a868405c08398f80c933c2451efc888644405ec675ca61a7db801663cd74bc93ffad381f68bcfa94b2cdf7b2fc1ccca42dcbd48199d1a2cbfc2cc94d96636eb5d81acd73fb451a17e3c75d2b13001922294ddfa024c99a587298731320bf5821715a78d1fc8a186a85d884670f4a16827fbbcb6323aae388be0b09851a2f0baa8d89fbe21cd6cb3430f5b3c1fa82bf3eadee4f91e6a370b5ad1bdccaed369859a9a9c923a64b5ebe7708b25cd0974a441b33a91b1442d8fca7f78edeac2962cfe461c3a93dc273097a1cc3f498c211782cf7b2b36b54426eed1f226264dd1eae1365199b5d69445940391b2da3c7c4224b27f53ee7b346c1959973a7f1bf86b846005b3203ca4ef2119ead67ad234b5f3f4acd0236da9eebdf71b5c94465cf065e205115a2eeda8881131cf071d269b783ac8a4e234d98bc7dd3f4539c31f6cc5515e3a44ef1cb8691b82cd511bc0c2300a0066d92c842ddd735441c22143d342bfdb8685de11cfad8fcf8d479380a18abdf7bfc6e11ddbe3e5ec3575b711060506d5f6eb7082be3b148489d6d7bf27d0c897a5b4c7b69eec79b9aeff961979047c6f8f245446e3ead3eee1c4e3e41280d895fa063958ad93402d1993808a121418f8248bec018e027737398af64c4303e8d023cedf0973a72f6fe8795ca43573610ec69fefb6bba659cfc4c357
```
![image](https://user-images.githubusercontent.com/1275714/155761392-8974b2ec-2c4f-441e-858a-fae268001b26.png)

![image](https://user-images.githubusercontent.com/1275714/155762616-8ba5f590-23ce-4c85-b6b0-572533beb1f0.png)



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


## libraries
 https://github.com/ShyftXero/aes
