# Contributing

Table of Contents
=================
* [Initial Environment Setup](#initial-environment-setup)
* [Debugging](#debugging)
* [Testing](#testing)
* [Adding pip Dependencies to the Project](#adding-pip-dependencies-to-the-project)
* [Git Guidelines and Tips](#git-guidelines-and-tips)
   * [Avoid pushing changes to the master branch.](#avoid-pushing-changes-to-the-master-branch)
   * [Create a new branch for every task that involves committing code.](#create-a-new-branch-for-every-task-that-involves-committing-code)
      * [Branching in the terminal](#branching-in-the-terminal)
      * [Branching in GitLens](#branching-in-gitlens)
   * [Use Git stash.](#use-git-stash)
   * [Fix commits to the wrong branch with cherry-picking and reverting.](#fix-commits-to-the-wrong-branch-with-cherry-picking-and-reverting)


## Initial Environment Setup
1. Install [Git](https://git-scm.com/downloads) for your operating system. On Windows, [Git Bash](https://gitforwindows.org) is recommended.
2. `git clone https://github.com/jepeffer/Pantry-Raid.git`
3. Install the latest version of [Python 3](https://www.python.org/downloads/) (currently 3.7.3) for your operating system.
4. Update or install [pip](https://pip.pypa.io/en/stable/installing/), depending on your Python installation.
5. Install [VS Code](https://code.visualstudio.com/Download) for your operating system.
6. Create a [Python virtual environment](https://docs.python.org/3/library/venv.html) inside your local repo, named `.venv`:
```bash
cd pantry-raid
python -m venv .venv
```
7. Open VS Code and visit the Extensions marketplace (`Ctrl+Shift+X`). Install the Python extension from Microsoft. Open your local repository of the project in VS Code. Optional: install the GitLens extension for Git integration and any other desired extensions.
8. [Add the virtual environment as the Python interpreter for this project](https://code.visualstudio.com/docs/python/environments):
  - Windows users: You may need to set Git Bash as the default shell for VS Code to avoid script execution permission errors. Press `Ctrl+Shift+P` to open the Command Palette and begin typing in `shell` and select "Terminal: Select Default Shell," then pick Git Bash from the list.
  - Press `Ctrl+Shift+P` to open the Command Palette and begin typing in `python:sel`. As you type, the autocompletion will provide suggestions.

![select interpreter](https://code.visualstudio.com/assets/docs/python/environments/select-interpreters-command.png)
  - Select the `.venv: venv` folder. The path below it should read `.venv/bin/python`.
![select venv](https://code.visualstudio.com/assets/docs/python/environments/interpreters-list.png)
9. Open a terminal in VS Code by pressing `` Ctrl+Shift+` ``. You should see (.venv) with the terminal prompt, indicating that you are in the virtual environment. Install the required Python dependencies by entering `pip install -r requirements.txt`.

You should be ready to develop using VS Code now.


## Debugging
Debugging within VS Code is simple: launch the application locally via the VS Code launch task (`F5`). The launch task is preconfigured to support the debugger.

The main components of debugging within VS Code are found within the Debug View (`Ctrl+Shift+D`, or the bug icon on the left). The debugger side panel will open up, which contains the **Variables** section and the **Watch** section. There are a few other sections included, but they are not as useful in the scope of this project. In any view within VS Code, you have access to a vertical gutter to the left of line numbers, the **Breakpoint Gutter**. Click within the gutter to set a breakpoint at that line of code, indicated by a red dot in the gutter. When the application is running in debug mode, the application will automatically be paused immediately _before_ it executes that line of code and VS Code will be brought up.

![debugscr](https://i.imgur.com/zI8ZjzM.png)

Above, you can see the Debug View of a sample application. The **Variables** section will usually only list variables local to the currently executing function when the application is paused. Usually, this will be populated when a breakpoint is hit, if there are any local variables. The **Watch** section allows developers to specify a variable or something else to watch. For Flask, a useful object to watch is the `request` variable, which contains form data, HTTP headers, and other important information.

![debugscr2](https://i.imgur.com/bAMfhGH.png)

Here, the debugger has hit a breakpoint while executing code. The next line to be executed (where the breakpoint was set) is highlighted in yellow with this color scheme. In red, the local variables have been outlined. The `user` and `post` variables are set within the function, so they have appeared in the **Variables** section. Since the `request` variable is being watched, its data can be viewed in the **Watch** section.

![debugging](https://i.imgur.com/TMEY4OT.png)

You can see more of the debugger in action in this screenshot. The developer has set a breakpoint that will be hit some time after the "Post a Comment" button is clicked, and this breakpoint has been hit. In the **Watch** section on the left, you can see the innards of the `request` object, specifically, the `form` data that will be used to populate the `user` and `post` variables. You may also notice that you can hover over any variable or function while the debugged application is paused and see a popup window with information about the object, in this case, the `mongo` variable.

The debugger is a valuable tool for learning about how the application works and why it isn't working. Use the debugger frequently to understand what data is available and how the code is being executed. You can execute code step by step once the debugger is paused by pressing `F10`, and step into a function that is to be executed by pressing `F11` (and `Shift+F11` to step back out).

You can read more about debugging in VS Code [here](https://code.visualstudio.com/docs/editor/debugging).


## Testing
Tests are run through pytest. Once you've installed the `pip` dependencies and source the virtual environment, you can run `pytest` in the root directory in your terminal. Running `pytest` in a terminal will generate HTML coverage pages inside the `htmlcov` directory. Open up `index.html` in a browser to see coverage details overlaid on the source files. Missed statements and branches will be highlighted.

To run and debug tests within VS Code, you'll need to update your `settings.json` file. It should look something like this:

```
{
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.enabled": true,
    "python.pythonPath": ".venv/bin/python",
    "python.testing.pytestArgs": [
        "--no-cov",
        "-vv"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestEnabled": true
}
```

Your `python.pythonPath` may be different, but the rest should be the same, aside from any additional settings that you have configured. Unfortunately, coverage cannot be run at the same time as a debugger, so debug tests within VS Code, and then run `pytest` in a terminal to verify your coverage statistics.

Travis CI will run the tests and `flake8` on any branches pushed to the GitHub repo. It's recommended to run `flake8` and `pytest` locally before pushing changes to verify that your code adheres to good style conventions and that it doesn't break any tests. Travis CI will send out e-mails when your build fails, which could be for reasons as simple as trailing whitespace after some function.

You can run only integration or unit tests by taking advantage of `pytest.mark`. All modules (files) for a type of test should have a `pytestmark` declared at the top of the file. The two markers in use are `unit` and `int` for integration. Run one type of test by executing `pytest -m <mark>` in a terminal. Note that coverage statistics reported for running only marked tests will only include code covered by the tests that were run, not all tests, so do not use this as a way of checking coverage.


## Adding pip Dependencies to the Project
1. Enter the venv, either from a VS Code terminal (`` Ctrl+Shift+` ``), or by entering the venv in a real terminal (Bash: `source .venv/bin/activate`).
2. Ensure that you have pulled down any previous dependencies by running `pip install -r requirements.txt` before continuing. You should see "Requirement already satisfied" for every dependency.
3. Install your new dependency through pip: `pip install <module>`
4. Update the requirements.txt: `pip freeze > requirements.txt`
5. Commit and push any changes. Remind your fellow developers of the update so that they know to install it.


## Git Guidelines and Tips
### Avoid pushing changes to the `master` branch.
Pushing to the `master` branch makes it harder to track all changes related to your specific task. If you push only to your working branch, peer reviewing your changes can be done easily when you create a pull request to merge your changes into `master`.

You can create a Git pre-commit hook that prevents you from accidentally pushing to `master`. In the repository's `.git/hooks` folder, create a file named `pre-commit` with the following contents:
```bash
#!/bin/sh

branch="$(git rev-parse --abbrev-ref HEAD)"

if [ "$branch" = "master" ]; then
  printf "You shouldn't commit to the master branch!\n\
Please checkout the correct development branch instead.\n\n\
If you really need to commit directly to master, temporarily disable this script in .git/hooks/pre-commit.\n"
  exit 1
fi
```
On Linux, make the file executable with `chmod +x pre-commit`. This step is not necessary on Windows.

### Reference the related issue in your commit messages.
GitHub automatically links any commits whose messages contain the text `#n` where _n_ is an existing issue to the issue itself. This makes it easy to track the work done on an issue.

The first line of your commit message is interpreted as a summary, and additional lines can provide a more detailed description.
```bash
git commit -m "short summary" -m "longer description"
```

### Create a new branch for every task that involves committing code.
Instead of committing to a "personal branch," you should instead create a new branch for every discrete task that you work. This is recommended so that the scope of reviewing your code changes for that task is limited only to what you changed for that task. It also allows us to merge your completed work into the `master` branch as soon as the pull request is approved.

As long as you don't commit your code, your changes will follow you to whichever branch you checkout. So, you can forget to change your branch, make some changes and stage (`git add`) them, then realize you're on the wrong branch if you run `git status` before `git commit`. Simply checkout the correct branch (`git checkout <branch>`), then continue.

#### Branching in the terminal
```bash
# Create and switch to a new branch
git checkout -b new-branch

# Switch to an existing branch
git checkout existing-branch

# Make your changes to the project files, then add them
git status  # Check what files you changed before doing a mass add!
git add [files/directory]  # Use git add . if you only changed what needs to be committed
git commit -m "changed the thing"

# Push the new local branch to remote, creating it in remote
git push -u origin new-branch

# Push a changed local branch to remote
# The tracking information for the existing branch has already been set up, so there's no need for git push -u origin <branch>
git checkout changed-branch  # If it's not already checked out
git push
```

#### Branching in GitLens
1. Open the Source Control panel in VS Code (`Ctrl+Shift+G`).
2. Click on the three dots (`...`) next to the title bar for the project.
3. Select "Checkout to..." and type in your new branch name, then select "Create new branch."
4. Add your changes and commit them.
5. Push your changes.


### Use Git stash.
You can stash any changes that you've made and staged, but not committed. Maybe you've done a lot of work on one thing, but there's something else that needs immediate attention. By stashing your changes, you can return to a clean slate to make those changes, push them, and then get back to what you had been working on.

To use stashing in VS Code, open the Command Palette (`Ctrl+Shift+P`) and type in "stash" to see autocompletion options.

**Warning: Using `pop` as opposed to `apply` will delete the changeset from the stash after it's applied.**

```bash
# Show list of changesets in stash
git stash list

# Show files changes in stash (like git status)
git stash show

# Show diff of changes in stash (like git diff)
git stash show -p

# Add changes to stash
git stash

# Add changes to stash with a custom message/label
git stash save <message>

# Recover most recent changes from the stash, while still keeping them stashed
git stash apply

# Recover any changes in stash using the label from git stash list
git stash apply stash@{x}
```

### Fix commits to the wrong branch with cherry-picking and reverting.
Don't try any nonsense like rebasing or resetting. These actions erase change history and can break things if used wantonly. Everyone with the repository already cloned has to pull from a reset/rebase and things can get ugly very quick.

1. Stash any changes you don't want to commit: `git stash`
1. Checkout the branch with the commit.
2. Find the commit hash: `git log` or open the GitLens panel in VS Code and search for the commit.
3. **Checkout the branch to apply the commit to.**
4. Cherry-pick the commit: `git cherry-pick <hash>`. This automatically commits the change.
5. Push the change to the correct branch.
6. **Checkout the branch with the commit again.**
7. Revert your changes: `git revert <hash>`
8. Push the fix.
9. Checkout the branch you need to work on.
10. Pop any changes off the stash to continue working: `git stash apply`
