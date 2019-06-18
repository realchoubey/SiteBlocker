# SiteBlocker
This script will block the sites during working hours which are distracting you from working.

#### How to use this
Following steps needs to be follow:
	1. Move BlockWebSites.py and config.choubs to a folder you want.
	2. Change com.site.blocker.plist and config.choubs as required.
	3. Run following commands
		sudo launchctl load <folder>/com.site.blocker.plist
		sudo launchctl start com.site.blocker
	4. Unload using
		sudo launchctl unload <folder>/com.site.blocker.plist
