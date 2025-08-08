### Requirements

Download Git: https://git-scm.com/downloads/mac (for cloning the repo)     
Download Python: https://www.python.org/downloads/macos/ (for running the program)    
Download VSCode: https://code.visualstudio.com/ (for viewing the files)

### Setup

1. Clone repository
```bash
git clone https://github.com/dernox47/RedditScraper.git
cd RedditScraper
```

2. Create a virtual environment
```bash
python -m venv venv
```

3. Activate the virtual environment
```bash
source venv/bin/activate
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

5. Run project
```bash
python3 program.py
```

### Configuration
In the `program.py`

- SUBREDDIT_NAME  
    Sets the subreddit by name

- POST_LIMIT  
    Sets the number of posts to get
