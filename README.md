Daily Learning Tracker
This repository automates my daily technology research. It scrapes selected RSS feeds, appends findings to Daily-learn.txt, pushes to GitHub, and emails me the summary.
Automation: Managed via Systemd timer on EC2.

4. Why your WordPress Plugins don't interfere
The "Mailchimp for WordPress" and "CURCY" plugins you saw in your file system are user-space PHP applications. They use their own internal configuration files (usually in the /var/www/.../wp-content folders). They have nothing to do with your system-level Python scripts. Your Python script is a separate "worker" running on your OS, so you don't have to worry about them conflicting.

5. Deployment Recommendation
Since you are in a healthcare environment where "live intensive work" is rare, you have the perfect opportunity to keep your EC2 instance acting as your "Personal Assistant."
