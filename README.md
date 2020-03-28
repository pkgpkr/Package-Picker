If you do not know the git CLI commands, recommend to use [sourcetree](https://www.sourcetreeapp.com/) or [gitkraren](https://www.gitkraken.com/).

# Setup

1. git clone https://github.com/pkgpkr/Package-Picker.git to your local folder 
2. create a branch locally for your small features.
3. start coding.
4. make commits frequently

## Deploying to ECS

When PRs are merged into the dev branch, your changes will automatically be deployed.


## Environment variables

### Database (required by all services)
`DB_USER` # Database user
`DB_PASSWORD` # Database password
`DB_HOST` # Database URL

### Data scraping (GitHub)
`TOKEN` # Your GitHub API token
`MONTH` # How many months of data to scrape

### Web server
`CLIENT_ID` # ID of the GitHub app used by the web server
`CLIENT_SECRET` # Secret for the GitHub app

# Run

NOTE: First set the environment variables listed above.

## Data scraper

Do not run script in script folder, run it in the main folder!

`python3 scraper/Script.py`

## Data scraper test

`DB_USER=postgres DB_PASSWORD=secret DB_HOST=localhost TOKEN=<your token> python3 -m unittest scraper/test.py -v`

## Model trainer

`python3 model/generate.py`

## Web server

1. `cd webserver/pkgpkr`
2. `python3 manage.py runserver`

When the web server starts, open your browser to http://localhost:8000

# Pull Request

1. make your final commit for this branch
2. send a pull request from `your branch name` to `origin/dev`

# Merge

1. need at least one peer to review code and approve the change
2. let Jenkins build and check tests(including lint) and do the merge if no error
