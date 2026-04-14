Daily Learning Tracker
This repository automates my daily technology research. It scrapes selected RSS feeds, appends findings to Daily-learn.txt, pushes to GitHub, and emails me the summary.
Automation: Managed via Systemd timer on EC2.

4. Why your WordPress Plugins don't interfere
The "Mailchimp for WordPress" and "CURCY" plugins you saw in your file system are user-space PHP applications. They use their own internal configuration files (usually in the /var/www/.../wp-content folders). They have nothing to do with your system-level Python scripts. Your Python script is a separate "worker" running on your OS, so you don't have to worry about them conflicting.

5. Deployment Recommendation
Since you are in a healthcare environment where "live intensive work" is rare, you have the perfect opportunity to keep your EC2 instance acting as your "Personal Assistant."

#How to run it from scratch (on your EC2/Production)
Setup Virtual Environment:

Bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Configure environment variables:
Add export GMAIL_APP_PASS='your-app-password' to your ~/.bashrc and source ~/.bashrc.
##NOTE:wE use it diffrent when running service files and the timer
Test the script:
python3 daily_learn.py
. Setting up SSH Authentication
Instead of using that HTTPS URL with the token, we will use the SSH URL.

Generate a Key (on your server/laptop):
ssh-keygen -t ed25519 -C "emiliohulbert2017@gmail.com"

Add to GitHub:

Copy the public key: cat ~/.ssh/id_ed25519.pub

Go to GitHub Settings > SSH and GPG keys > New SSH Key.

Update your repository remote:
Inside your project folder, run:

Bash
git remote remove origin
git remote add origin git@github.com:EmilioHulbert/AutoGitCommit.git
Now, when your script runs repo.remotes.origin.push(), it will use your SSH key automatically without needing a password or token.
1. Initialize and link to GitHub
Run these commands inside your ~/Desktop/daily-learn/ directory:
# Initialize the local repository
git init -b main

# Add all files to the staging area
git add .

# Make the first commit
git commit -m "Initial commit: Daily learning automation script"

# Tell git where your remote repository is (using SSH)
git remote add origin git@github.com:EmilioHulbert/AutoGitCommit.git

# Push your code to the 'main' branch on GitHub
git push -u origin main
The error src refspec main does not match any happened because, after you received the "Author identity unknown" error, the commit never actually finished. Git is still sitting there with no commit history, and since there is no commit, there is no main branch to push.

Here is the exact sequence to fix this and get it live on GitHub:

Set your identity and perform the commit
Since you already set the global config, you just need to commit the changes you staged earlier. Run these:

Bash
# Since you already ran git add ., the files are staged.
# Now commit them:
git commit -m "Initial commit: Daily learning automation script"

# Verify the commit was created:
git log
Push to GitHub
Now that you have a commit, the main branch exists locally and can be pushed:

Bash
# Push to the remote origin we added earlier
git push -u origin main


. Verification
After running these, check your repository on GitHub. You should see daily_learn.py, .gitignore, and README.md listed there.

3. Automating for Production (The Final Piece)
Now that your code is version-controlled and pushing via SSH, you need the Systemd files to make it run automatically on your EC2 instance without you doing anything.

Create the Service file (/etc/systemd/system/daily-learn.service):
┌─[✗]─[root@Intel5]─[/mnt]
└──╼ #cat /etc/systemd/system/daily-learn.service
[Unit]
Description=Run Daily Learning Auto-Commit

[Service]
Type=oneshot
WorkingDirectory=/home/hulbert/Desktop/daily-learn
# Add this line below, replacing 'your-app-password-here' with your actual 16-character code
Environment="GMAIL_APP_PASS=mejactwxibyuqesu"
ExecStart=/home/hulbert/Desktop/daily-learn/venv/bin/python /home/hulbert/Desktop/daily-learn/daily_learn.py
User=hulbert
┌─[root@Intel5]─[/mnt]
└──╼ #
Create the Timer file (/etc/systemd/system/daily-learn.timer):
──╼ #cat /etc/systemd/system/daily-learn.timer
#[Unit]
#Description=Run daily-learn every minute

#[Timer]
## Run every minute
#OnCalendar=*:0/1
#AccuracySec=1s
#Persistent=true

#[Install]
#WantedBy=timers.target

[Unit]

Description=Run daily-learn daily



[Timer]

OnCalendar=daily

AccuracySec=1h

Persistent=true



[Install]

WantedBy=timers.target
┌─[root@Intel5]─[/mnt]
└──╼ #Activate the timer:

Bash
sudo systemctl daemon-reload
sudo systemctl enable daily-learn.timer
sudo systemctl start daily-learn.timer



##Fixing the gmail failed issue
It looks like your Git automation is running perfectly, but the email notification is failing because of an authentication error with Gmail. The `535 5.7.8` error specifically means Google is rejecting the credentials you provided via the `GMAIL_APP_PASS` environment variable.

### 1. Why this is happening
Even though you previously defined the environment variable, **systemd services do not inherit your user's shell environment (`~/.bashrc`)**. When the script runs as a service, `os.getenv("GMAIL_APP_PASS")` returns `None`, leading to the authentication failure.

### 2. The "Guru" Solution: Service Environment
You need to explicitly tell the systemd service where to find that password.

**Edit your service file:**
```bash
sudo vi /etc/systemd/system/daily-learn.service
```

**Update the `[Service]` section to include the environment variable:**
```ini
[Service]
Type=oneshot
WorkingDirectory=/home/hulbert/Desktop/daily-learn
# Add this line below, replacing 'your-app-password-here' with your actual 16-character code
Environment="GMAIL_APP_PASS=gmail_smtp_key_here"
ExecStart=/home/hulbert/Desktop/daily-learn/venv/bin/python /home/hulbert/Desktop/daily-learn/daily_learn.py
User=hulbert
```

*Note: Remove the spaces from the app password string in the service file (e.g., `mejactwxibyuqesu` instead of `meja ctwx ibyu qesu`).*

### 3. Apply the changes
After saving the file, you must tell systemd to refresh its configuration:

```bash
sudo systemctl daemon-reload
# Trigger the service manually to test it
sudo systemctl start daily-learn.service
```

### 4. Verify the fix
After running the start command, wait a few seconds and check the log again:

```bash
cat /home/hulbert/Desktop/daily-learn/app.log
```

If it says `Email sent successfully`, you have officially mastered the "Guru" way of local automation. Your script is now fully containerized in its behavior, Git is syncing via SSH, and your systemd timer is handling the scheduling reliably.

**One last pro-tip:** Since this script is now a background service, if you ever change your Gmail password or rotate your App Password, remember to update that `daily-learn.service` file and run `sudo systemctl daemon-reload`.

Are you ready to let this run on its own, or is there anything else you want to track in that `Daily-learn.txt` file?

#Fix some git remote issues 
This error confirms exactly why your script is currently failing: **Git is still trying to use HTTPS instead of SSH.**

Even though you ran `git remote add origin git@github.com:...` earlier, Git is still referencing the old **HTTPS URL** because you likely have a local `.git/config` file that is still pointing to the HTTPS path.

### 1. Fix the Remote URL
You need to force your local repository to use the SSH protocol. Run these commands in your project folder:

```bash
# Verify what it is currently pointing to
git remote -v

# Remove the faulty HTTPS remote
git remote remove origin

# Add the correct SSH remote
git remote add origin git@github.com:EmilioHulbert/AutoGitCommit.git
```

### 2. Verify the Change
Run `git remote -v` again. It **must** look like this:
```text
origin  git@github.com:EmilioHulbert/AutoGitCommit.git (fetch)
origin  git@github.com:EmilioHulbert/AutoGitCommit.git (push)
```
If you still see `https://github.com/...`, the fix didn't take.

### 3. Why did this happen? (The "Guru" Logic)


Your script uses `GitPython` to call `git push`. When you installed the repository or initialized it, it likely cached the HTTPS connection method. Because you are running the script as a `systemd` service, it doesn't have access to your personal Git credentials manager—it tries to "read" your username/password, fails because it's a headless background service, and crashes. By switching the remote to `git@github.com`, you force Git to use the **SSH protocol**, which uses your private keys instead of a username/password prompt.

### 4. Final Action
After verifying the remote URL is correct, trigger the service one last time to ensure it pushes successfully:

```bash
sudo systemctl start daily-learn.service
cat /home/hulbert/Desktop/daily-learn/app.log
```

If the logs show `Git push successful`, you have effectively "purged" the HTTPS credential request from your system.

**Did the `git remote -v` command show the correct SSH URL after you updated it?**

##Fix after resetting remote origin
26-04-14 10:45:22,980 - INFO - Cycle complete.
2026-04-14 10:52:16,420 - INFO - Starting daily learning cycle.
2026-04-14 10:52:18,666 - ERROR - Critical failure in update_git: Cmd('git') failed due to: exit code(128)
  cmdline: git push --porcelain -- origin
  stderr: 'fatal: The current branch main has no upstream branch.'
2026-04-14 10:52:18,666 - INFO - Cycle complete.

You are extremely close! The error `fatal: The current branch main has no upstream branch` is the final hurdle.

When you ran `git remote remove origin` and re-added it, you effectively "reset" the link between your local `main` branch and the GitHub `main` branch. Git no longer knows that your local branch is supposed to sync with the remote one.

### The Fix: Set the Upstream Branch
Run this command once while in your project directory (`/opt/AutoGitCommit`):

```bash
git push -u origin main
```



### Why this is necessary:
* **`git push -u`**: This is the "upstream" flag. It tells Git: "From now on, whenever I type `git push` or `git pull` while on the `main` branch, automatically use `origin main` as the destination."
* **Why it failed in the script:** Your Python script calls `repo.remotes.origin.push()`. If the upstream isn't set, Git gets confused and halts.

### One important "Guru" check
Because you are running this as `root` (via the service), you need to make sure the **root user's SSH keys** are configured. 

1.  **Check if root has the key:**
    When you ran `ssh-keygen` earlier, you might have done it as user `hulbert`. But your service runs as `root` (or is executing from `/opt/AutoGitCommit`).
2.  **Verify Root's Keys:**
    Run: `sudo ls /root/.ssh/id_ed25519.pub`
    * If that file **does not exist**, the `root` user cannot authenticate with GitHub.
    * **The solution:** Either generate a key for root (`sudo ssh-keygen -t ed25519`) and add *that* public key to your GitHub account, **OR** (easier) change the `User=` line in your `daily-learn.service` to `User=hulbert`.

**Recommendation:** Change the service user to `hulbert` (the user who created the keys) to avoid managing two sets of SSH keys.

**After you run `git push -u origin main` and update the `User=` line in your service file to `User=hulbert`, restart the service again. Does the log show success?**

##Version control
This is the classic "Distributed Version Control" challenge. When you have two machines (Server and Laptop) modifying the same file, you must **pull before you push**. If you push blindly from your laptop, you will overwrite the server's work.

### 1. The "Guru" Sync Strategy
You need to follow this sequence whenever you work on your laptop so you don't lose the server's progress:

1.  **On your Laptop:**
    * Open your terminal in `~/Desktop/daily-learn/`.
    * Run `git pull origin main`. This downloads the latest `Daily-learn.txt` from the server (which the server pushed earlier).
    * *Now* you have the most up-to-date file.
    * Make your edits.
    * Run `git add Daily-learn.txt`, `git commit -m "Updated from laptop"`, and `git push`.

### 2. What if you get a "Merge Conflict"?
If you edit the same line on your laptop that the server just updated, Git will stop and warn you of a **Merge Conflict**.
* **The fix:** Open the file, keep the lines you want, delete the `<<<<<<< HEAD`, `=======`, and `>>>>>>>` markers that Git inserts, then `git add`, `git commit`, and `git push`.



### 3. Making this easier (The "Guru" Tip)
Since you want your laptop to be a "second home" for this repo:
* **Don't run the `systemd` timer on your laptop.** Only the server should have the automated timer.
* **Manual Pulling:** Create a simple shell alias on your laptop so you never forget to pull before you work. Add this to your `~/.bashrc`:
    ```bash
    alias sync-learn='git pull origin main && ./daily_learn.py'
    ```
    *Now, whenever you sit down to work, you just type `sync-learn`.*

### 4. Why this matters for "Green Squares"
GitHub's contribution graph is global for your account. It does not care *which* machine pushed the commit.
* If the server pushes at 09:00 AM, you get a green square.
* If you pull that work to your laptop, work on it, and push at 02:00 PM, the commit date is what matters. You will still have a green square for that day.

**Crucial Advice:** Since you are now working with two machines, ensure your **SSH keys** are unique to each device.
* The server has its own key (added to GitHub).
* Your laptop should have its own key (also added to GitHub).
* **Never copy the server's private key to your laptop.** They should be separate identities so you can revoke one if a device is ever stolen.

**Are you going to be editing the `Daily-learn.txt` file manually on your laptop, or do you intend to use the same Python script there to generate the entries?**
##Fix for
──╼ $git pull origin main
remote: Enumerating objects: 17, done.
remote: Counting objects: 100% (17/17), done.
remote: Compressing objects: 100% (7/7), done.
remote: Total 15 (delta 10), reused 13 (delta 8), pack-reused 0 (from 0)
error: insufficient permission for adding an object to repository database .git/objects
fatal: failed to write object
fatal: unpack-objects failed
(venv) ┌─[✗]─[hulbert@Intel5]─[~/Desktop/daily-learn]
└──╼ $

**Do NOT use 777.** Using `777` permissions is a security "guru" anti-pattern—it gives every user on your system the ability to read, write, and execute your files, which is a massive vulnerability.

### Why you have this error
You performed some operations as `root` (like the service setup and the initial file creation on the server), and now you are trying to `git pull` as your standard user `hulbert`. Git is failing because the user `hulbert` does not have write permissions to the internal `.git/objects` folder that `root` created.

### The Correct Fix
You need to return ownership of the entire directory to your standard user (`hulbert`). Run these commands from the directory **above** your project:

```bash
# Navigate to the parent directory
cd ~/Desktop/

# Change the ownership of the entire project folder back to you
sudo chown -R hulbert:hulbert daily-learn/

# Set secure permissions (directories 755, files 644)
find daily-learn/ -type d -exec chmod 755 {} \;
find daily-learn/ -type f -exec chmod 644 {} \;
```



### Explanation of these commands:
1.  **`chown -R hulbert:hulbert`**: This recursively (`-R`) sets the owner and the group to `hulbert`. This is the single most important command to fix your permission issues.
2.  **`chmod 755` (for directories)**: Allows the owner to do everything, while others can only read and enter.
3.  **`chmod 644` (for files)**: Allows the owner to read/write, while others can only read.

### Now try the pull again
Once you have run those commands, your `git pull` will work perfectly as the user `hulbert`:

```bash
cd ~/Desktop/daily-learn/
git pull origin main
```

**Never use `777` on your `.git` folder.** If you ever find yourself needing `777` to fix a problem, it means you have an ownership issue (the wrong user owns the file), not a permission issue.

Does the `git pull` work for you now after fixing the ownership?
##Finally you may require 
This is a common "git lock" situation. Your local `daily_learn.py` on the server has diverged from what is on GitHub, so Git is protecting you from losing your local code.

Since you are sure the **Laptop is the Source of Truth** (you pushed your latest edits from the laptop), you want to force the server to match the laptop exactly.

### The "Guru" Reset (Force Sync)
Since you are okay with overwriting whatever is currently on the server, you don't need to merge—you need a **Hard Reset**. This will discard local server changes and make the server look *exactly* like GitHub.

Run these on the **server** (`/opt/AutoGitCommit`):

```bash
# 1. Fetch the latest metadata from GitHub
git fetch origin

# 2. Reset your local branch to match the remote exactly
git reset --hard origin/main

# 3. Verify it worked
git status
```



### Why this works:
* `git fetch origin` gets the latest "map" of what GitHub looks like.
* `git reset --hard origin/main` moves your local pointer to that exact spot, deleting any local modifications (like your local testing changes) that haven't been committed.

### Important: Permissions Check
Because you ran `git reset --hard` as `root`, you might trigger that "permission denied" error again when you try to use the script as user `hulbert`. After the reset, ensure you fix ownership:

```bash
# Fix ownership so your user 'hulbert' can actually use the script
chown -R hulbert:hulbert /opt/AutoGitCommit
```

### Pro-tip for the Future: `.gitignore`
To prevent this `daily_learn.py` conflict in the future, if you plan on having "Server-only" code and "Laptop-only" code, you should create a file called `config.py` that contains the variables (like `REPO_PATH`) and add `config.py` to your `.gitignore`. That way, the logic script stays the same on both machines, but the configuration remains machine-specific.

Once you run the `git reset --hard`, your server will be perfectly in sync with your laptop. You can then restart your service with `sudo systemctl start daily-learn.service`. Everything should run smoothly now. 

Does the script execute successfully without the overwrite error now?