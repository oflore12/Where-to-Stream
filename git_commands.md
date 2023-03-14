# Cheatsheet for Git commands
If you have a file or directory that you do not want to push ever, there is a file
found in .git/info directory, to view it you have to use `ls -la` or `ls -a` which shows you hidden files. 

The file is called `exclude`, to easily comment in it you can run `nano .git/info/exclude`.
You will see a bunch of # comments, and then on one line `env/` and on the other `__pycache__`. 
To exclude a directory add a new line and add the "/" to the end.
To exclude a file just place the file name in a new line.


- `git status` (shows you all the new stuff you've added to the directory)
- `git add .` (adds all the files at once)
	- `git add file.txt` (adds only the file you specify, you can use it for folders too)
- `git commit -m "insert your message in the quotation marks"`
- `git push` (will push the changes youre adding)
- `git log` (will show you a log history of commits, usually there is a hash associated with every commit made)

**IF YOU WANT TO LINK/TAG A COMMIT TO AN ISSUE IN JIRA**
Instead of using `git commit -m "text"`:

- Go to the backlog and click on the issue, under "Details", theres a section 
called "Development", you can click on "Create commit" and copy the sample Git commit
it should look something like this "git commit -m "C447-18 <message>"
- Type your message where you see message, once you push it will show in Jira automatically
	- EX: `git commit -m "C447-18 <message>"`

**TO UPDATE YOUR LOCAL REPO WITH THE REMOTE REPO**
- 'git pull git@github.com:oflore12/CMSC447Project.git' (you might have to be in the CMSC447Project directory)
