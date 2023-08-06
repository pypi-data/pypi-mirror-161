
# ao3-archivist
Reading list exporter for [AO3](https://ao3.org) reading history and Marked for Later.


## Installation
ao3-archivist is supported on Python 3.10 and above.

You can install ao3-archivist directly from [PyPI](https://pypi.org/project/realpython-reader/):
```bash
  pip install ao3-archivist
```

If you’d like, you can also install from source by downloading [the latest release](https://gitlab.com/fandomdotlove/ao3-archivist/-/releases/permalink/latest) and installing:
```bash
  pip install path/to/release/file.tar.gz
```

If you already have ao3-archivist installed, running either of these commands will update it.

## Usage

### Basic Usage
To export reading history, [export your AO3 cookies](#how-do-i-getpass-cookies-for-archivist) and run
```bash
  ao3-archivist --username [USERNAME] --cookies /path/to/cookies/file.txt
```
If you want to export your Marked for Later, run
```bash
  ao3-archivist --username [USERNAME] --cookies /path/to/cookies/file.txt --later
```

### Documentation
```bash
> ao3-archivist --help

  Usage: ao3-archivist [OPTIONS]

    Exports AO3 reading history to a CSV file.

  Options:
    --username TEXT  (required) The AO3 username to get history from.
    --cookies TEXT   (required) Path to the cookies file for the AO3 account.
    --out TEXT       Path to save the archive CSV to. (default: archivist-username-[history/markedforlater]-timestamp-pagerange.csv)
    --start INTEGER  Which page number to start from.
    --end INTEGER    Which page number to end on.
    --later          Flag to archive Marked for Later instead of History.
    --help           Show this message and exit.
```


## FAQ

#### How do I get/pass cookies for ao3-archivist?
First, log in to the AO3 account you wish to use with the script. You can then extract cookies from your browser using an extension such as [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid/) (Chrome) or [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) (for Firefox). The extracted cookies file must be in Mozilla/Netscape format. The first line should be either `# HTTP Cookie File` or `# Netscape HTTP Cookie File`.

Once you have it downloaded to your computer, pass in the path to it using the `--cookies` option:
```bash
  ao3-archivist --username [USERNAME] --cookies /path/to/cookies.txt.
```

Note that you must provide the cookies for the AO3 account matching the username. If you are archiving history multiple AO3 accounts, you will need to export cookies for each one separately, while logged in to the corresponding account.

#### How long will it take to export my history?
To prevent excess load to AO3 servers, ao3-archivist reads 30 pages of history per minute. Ex. If you have 300 pages of history, it will take about 10 minutes to run. This script gives the option of limiting which pages to export on each run.

#### Can ao3-archivist remember what was already exported?
No; ao3-archivist does not save any information about what was exported. If you’d like, you can clear your AO3 history after exporting to keep things neat. If you choose to keep the default filename, it includes the page range so you can keep track of how many new pages of history were added the next time you archive. (Please note that works may change order in your history if you revisit a work from later in your history.)

#### Who has access to my AO3 information if I use ao3-archivist?
Only you! Your cookies are only used to access the necessary AO3 pages for archiving (reading history and Marked for Later). Your information is only stored to your computer, and is not sent anywhere else at any time.
