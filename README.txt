This project implements a few of the many RPC calls to control SANs based on the LSI/Engenio/NetApp platform, since those only come with a graphical administration utility. It was specifically built against the Dell PowerVault MD3600i "MD Storage Manager" utility, but the RPC structure should be similar for other models.

If you want it to be of any use, you should implement the methods you need since this only provides a handful of examples. You will find useful information on the protocol itself, along with the different RPC structures in your SMClient distribution, especially in the following classes (both can be found in SMclient.jar).

- devmgr.v1125api15.sam.jal.SYMbolClient
- devmgr.v1125api15.symbol.SYMbolAPIClientV1