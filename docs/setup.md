# Setup for Developer

## MacOS

1. Clone and deploy locally:
```bash
git clone https://github.com/Funnear/bio-rag-assistant.git; \
cd bio-rag-assistant; \
python3 -m venv venv; \
source venv/bin/activate; \
pip install --upgrade pip; \
pip install -r requirements.txt; \
```

2. Start the web app on localhost:

```bash
streamlit run src/main.py
```

## Windows

TBD

-----

# Setup for User

## MacOS

TBD

## Windows

1. Clone the project to your desired local parent directory:

Setup your GitHub authentication if not done yet. Use your <username> and <email> in the commands below:
```bash
git config --global credential. helper manager-core;
git config --global user.name <username>;
git config --global user.email <email>;
```

When you call git action for a certain repository for the first time, the helper will ask you for your password and will keep it for all your repos.

```bash
git clone https://github.com/Funnear/bio-rag-assistant.git &&
cd bio-rag-assistant
```

This will create a sub-folder "bio-rag-assistant" and your terminal will navigate inside it.

2. Create virtual environment and install dependencies:

```bash
python3 -m venv venv `
&& venv\Scripts\Activate.ps1 `
&& pip install --upgrade pip `
&& pip install -r requirements.txt
```

3. Anytime you want to use the assistant, run:

```bash
venv\Scripts\Activate.ps1 `
&& streamlit run src/main.py
```

------

# Placeholder

Delete me :)

```bash

```

```python

```

