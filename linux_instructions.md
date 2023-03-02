## Intructions to give user sudo privilages and installing open ssh
Make sure that your user has sudo privileges, you need to know **root** pw to login as root run:
  > su - <br>
  > usermod -aG sudo (insert your user name here) <br>
  > reboot 

![Screen Shot 2023-03-01 at 11 33 58 PM](https://user-images.githubusercontent.com/58226151/222332358-84783db3-c3a6-4b15-a193-d6c3ef9d5f61.png)

After the vm rebooted you can add ssh ability to machine, this makes it so
you can ssh through your terminal making copying and pasting a bit easier, run:
>sudo apt-get install openssh-server<br>

Once this is done installing, you will have to go to your virtual box and click on settings <br>
![Screen Shot 2023-03-01 at 11 42 12 PM](https://user-images.githubusercontent.com/58226151/222333066-21b36554-03e2-42d2-8d01-04ec6d56e208.png)<br>
Go to Network<br>
Go to Adapter 2<br>
Expand the advanced settings<br>
Click on "Port Forwarding"<br>
There will be a green diamond and a plus sign button on the window that pops up, click it. <br>
![Screen Shot 2023-03-01 at 10 14 59 PM](https://user-images.githubusercontent.com/58226151/222333490-79559365-b4eb-470d-96ff-da6c5161831c.png) <br>

Under name add ssh <br>
Under protocol add TCP<br>
Under host port add 3022<br>
Under guest port add 22<br>
*All other boxes do not need text input*<br>
Click "OK" to save changes<br>
Now open the terminal in host machine, personal machine and run:<br>
>ssh -p 3022 (username)@127.0.0.1<br>

![Screen Shot 2023-03-01 at 11 53 03 PM](https://user-images.githubusercontent.com/58226151/222334424-b70324ff-a336-4f6a-a08d-463766b7cdb6.png)<br>

## Connecting your machine to github repository
###### GENERATING SSH KEY AND ADDING IT TO GITHUB ACCOUNT
Log into your vm and open up the terminal, if you want to ssh then you can also.
Generate an ssh key from the vm, run: <br>
>ssh-keygen -t rsa -b 4096 -C "email_connected_to_github_account@gmail.com"<br>

It will prompt you to save the key in a directory leave blank and just hit enter key<br>
It will prompt you to create a passphrase, you can hit enter twice or enter the passphrase you chose twice **(DONT FORGET THE PASSPHRASE)**<br>
If you're on a terminal and ssh'd into the vm then this will be simple. If not, you can do this from your vm machine.<br>
Either way log into your github account through a web browser and go to settings.<br>
Find "SSH and GPG keys" (should by in the "Access" section)<br>
Click on "New SSH key"<br>
Add title, I used "447VM"<br>
On the terminal run:<br>
>cat ~/.ssh/id_rsa.pub<br>

Copy the ssh key and paste it in the key section of github<br>
Click "Add SSH key"<br>

###### Now you're ready to clone the repository
In your terminal make sure you're in a directory you want to work on the repository, run:<br>
> git config --global user.email (insert email you use for github)<br>
> git config --global user.name "insert your name"<br>
> git clone git@github.com:oflore12/CMSC447Project.git<br>

This should add the project and its content to your directory<br>
You can run "ls" and see CMSC447Project folder in the directory, run:
>cd CMSC447Project<br>

You should now have access to the repository and its content.<br>
