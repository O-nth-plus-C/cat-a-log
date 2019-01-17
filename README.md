#Catalog Project
A web application which displays and allows management of items and categories
from a database, with edit and delete permissions limited to object creators.  

## How to Use
Install the following:
[Vagrant](https://www.vagrantup.com/)  
[VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
[git](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)

Check if vagrant is installed by running `vagrant --version` in git.

Download the VM configuration from either:
[github](https://github.com/udacity/fullstack-nanodegree-vm)
[direct](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip)

Navigate in git to the location where you downloaded the vagrant configuration.

Start the virtual machine using `vagrant up`.
(You may have to enable virtualization in your BIOS settings)

Once vagrant is finished starting the machine, log in using `vagrant ssh`.

Copy the `/catalog` folder to the vagrant shared folder, or use git clone to copy
the repository to your virtual machine.

Run `python views.py` to run the server at the address specified in the
`if __name__ =='__main__'` block (Local Port 8000 by default.)
