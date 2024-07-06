# Deveba

Deveba is a simple wrapper around git and other tools to synchronize folders on multiple computers.

Supported tools:

- git
- svn
- rsync
- unison

## Setup

### Adding a folder to sync

Create a git repository in the folder you want to sync:

```
cd ~/my-folder
git init
# Optional: setup a .gitignore
git add .
git ci
# Publish the new repository to some server
git remote add origin git/url/for/my-folder.git
```

Create a configuration file for Deveba:

```
mkdir -p ~/.config/deveba
cat ~/.config/deveba/deveba.xml <<EOF
<config>
  <group name="daily">
    <repo path="~/my-folder"/>
    <!-- Add more repo here if needed -->
  </group>
</config>
EOF
```

Add a cron job calling Deveba with your group:

```
deveba daily
```

### Syncing an existing folder

Clone the folder from the server:

```
git clone git/url/for/my-folder.git
```

Create a configuration file for Deveba:

```
mkdir -p ~/.config/deveba
cat ~/.config/deveba/deveba.xml <<EOF
<config>
  <group name="daily">
    <repo path="~/my-folder"/>
    <!-- Add more repo here if needed -->
  </group>
</config>
EOF
```

Add a cron job calling Deveba with your group:

```
deveba daily
```

## Development

From within a virtualenv:

```
pip install -r requirements-dev.txt
pytest
```
