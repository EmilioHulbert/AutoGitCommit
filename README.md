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
