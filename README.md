# Distributed Storage
## Description
An educational project with an aim to make a fault tolerant distributed file storage. 
File system supports file reading, writing, creation, deletion, copy, moving and info queries. 
It also supports certain directory operations - listing, creation, changing and deletion. 
Files are replicated on multiple storage servers.
The data is accessible even if some of the network nodes are offline.
## System architecture

The system is written using _**django**_ for the _**name server**_ and flask for _**storage servers**_.
The following diagram explains the architecture.

![](/images/architecture.jpg)

### Description of communication protocols
All the communication happens via HTTP. The endpoints of each server
shown on the diagram above.

### Upload file

Next, let's see example of how the system components interact to upload
the file to distributed storage. Here, we assume, that the maximum number
of replicas needed in the system is 2.

![](/images/file_upload.jpg)

Let's look closely at each request.

1. The _**client**_ wants to know an ip address of server on which it should upload 
the file. The _**client**_ makes a GET request to on /available.
2. The _**name sever**_ returns an ip of the available storage server, 
in this case, it's the ip of _**storage2**_.
By available we mean that, the storage is responding status checks. 
3. The next step is to send the file from _**client**_ to _**storage server**_.
The _**client**_ server sends POST request to storage server with the 
file it wants upload to distributed storage.
4. As soon as the _**storage server**_ received the file, it sends 
POST request to _**name server**_ with file path and file hash
to create an entry in the database.
5. When the _**name server**_ created an entry in the database, it 
checks whether there are enough copies of that file. In our case, 
the desired number of copies is 2, so the _**name server**_ chooses 
another storage to save the file. In the example it chooses _**storage1**_ and
sends POST request with _**storage1**_ ip and the file path
to /replicate on the _**storage2**_.
6. Finally, _**storage2**_ sends POST request to /file on the _**storage1**_ with 
the file, which file path it got from /replicate request.

### Storage server failure
_**Name server**_ periodically runs checks on _**storage servers**_.
It sends /status request to each of them and if one of them is not 
responding, the _**name server**_ marks it as not available. Let's 
see what happens if one of the _**storage servers**_ is not responding and 
it has a file, wich will have not enough replicas without this _**storage server**_.
In our case, _**storage1**_ is not responding to health checks.

![](/images/file_replicate.jpg)

1. _**Name server**_ sends POST /replicate request with file path and ip of the
_**storage1**_ to the _**storage server**_ wich has 
the file needed to be replicated, on the example it's _**storage2**_.
2. Then _**storage2**_ sends the file with the file path it received to 
_**storage3**_.
3. After the replication, _**name server**_ checks whether all files has enough replicas.
If not, then the replication process runs again.

That's all, the file has enough replicas now.

### Delete file
Let's see an example of deleting a file, assuming the file is on the 
_**storage1**_ and _**storage2**_.

![](/images/file_delete.jpg)

1. The client sends DELETE /file request to the _**name server**_. 
The request contains the file path of the file wich is to be deleted.
2. The _**name server**_ finds all the storage servers which has this 
file and sends DELETE /file request to _**storage1**_.
3. And the same request to _**storage2**_.

### Storage server restoration
There could be a situation when one of the not responding to health checks _**storage servers**_ 
became available again. So, this _**storage server**_ needs to be synced
with the system again. Let's see an example of _**storage1**_ restoration, assuming it has 
some outdated file which needs to be deleted.

![](/images/storage_restoration.jpg)

1. The _**name server**_ sends health check request to _**storage1**_.
2. _**Storage1**_ responds. But it was previously down, so it needs to be synced.
3. The _**name server**_ sends /dump_tree request to _**storage1**_ and gets back the files
and the hashes which are stored on the _**storage server**_.
4. The _**name server**_ compares the file hashes it has in the database and finds out that one 
of the files is outdated. So, it sends DELETE /file request to _**storage1**_ with the file path 
of the outdated file.
5. Before storage restoration there could be a situation when some files did not have enough copies.
So, such files have to be found and replicated. The mechanism is the same as replication on file upload.

## How to run 


## How to use


