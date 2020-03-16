If you do not know the git CLI commands, recommend to use [sourcetree](https://www.sourcetreeapp.com/) or [gitkraren](https://www.gitkraken.com/).

# Setup

1. git clone https://github.com/pkgpkr/Package-Picker.git to your local folder 
2. create a branch locally for your small features.
3. start coding.
4. make commits frequently 

# Run

1. `cd webserver/pkgpkr`
2. `python3 manage.py runserver`

When the web server starts, open your browser to http://localhost:8000

# Pull Request

1. make your final commit for this branch
2. send a pull request from `your branch name` to `origin/dev`

# merge

1. need at least one peer to review code and approve the change
2. let Jenkins build and check tests(including lint) and do the merge if no error

