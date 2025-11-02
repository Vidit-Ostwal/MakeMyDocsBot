# MakeMyDocsBot

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 ███╗   ███╗ █████╗ ██╗  ██╗███████╗    ███╗   ███╗██╗   ██╗
 ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝    ████╗ ████║╚██╗ ██╔╝
 ██╔████╔██║███████║█████╔╝ █████╗      ██╔████╔██║ ╚████╔╝ 
 ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝      ██║╚██╔╝██║  ╚██╔╝  
 ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗    ██║ ╚═╝ ██║   ██║   
 ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝   ╚═╝   
                                                              
 ██████╗  ██████╗  ██████╗███████╗    ██████╗  ██████╗ ████████╗
 ██╔══██╗██╔═══██╗██╔════╝██╔════╝    ██╔══██╗██╔═══██╗╚══██╔══╝
 ██║  ██║██║   ██║██║     ███████╗    ██████╔╝██║   ██║   ██║   
 ██║  ██║██║   ██║██║     ╚════██║    ██╔══██╗██║   ██║   ██║   
 ██████╔╝╚██████╔╝╚██████╗███████║    ██████╔╝╚██████╔╝   ██║   
 ╚═════╝  ╚═════╝  ╚═════╝╚══════╝    ╚═════╝  ╚═════╝    ╚═╝   

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## What is MakeMyDocsBot?

**MakeMyDocsBot** is a smart documentation synchronization bot designed to help maintainers keep multi-language documentation up-to-date across feature branches.  
Built using **crewAI**, for crewai (currently) it automates the process of detecting documentation changes in English and synchronizing them into other supported languages — currently **Korean** and **Portuguese (Brazil)**.

The bot fits seamlessly into your workflow, ensuring that new features stay consistently documented across all supported locales — reducing manual overhead and improving release quality.

### 🎥 Overview Video  
See how MakeMyDocsBot works, how it fits into the ecosystem, and the agents & tasks that power it.

[![Architecture Overview](images/preview_video_1.png)](https://www.loom.com/share/a695e79df202473ab5acd3c6f6f8c585)

*MakeMyDocsBot — Overview & Architecture*
![AMP Platform](images/amp_platform.png)  


---
---

## DEMO

### DEMO #1 — PR->https://github.com/crewAIInc/crewAI/pull/3729

[![Demo 1](images/demo-1.png)](https://www.loom.com/share/61dd4f5fce544beaa565df6c0bd58517)

---

### DEMO #2 — PR->https://github.com/crewAIInc/crewAI/pull/3584

[![Demo 2](images/demo-2.png)](https://drive.google.com/file/d/17HElOx9ej-bdLOSlKrxBwimE65QiTxAw/view?usp=sharing)

---
---


## Installation

### Create and Activate a Virtual Environment

Use your installed Python version (e.g., Python 3.12):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### Install [UV](https://docs.astral.sh/uv/)

Install `uv` inside your virtual environment:

```bash
pip install uv
```

### Cloning the repository 

Fork this repository and clone it locally
```bash
git clone <clone-repo-name>
```

### Sync Dependencies

In your project root:

```bash
uv sync
```

This command:
- Reads dependencies from your `pyproject.toml` (and optionally `uv.lock`)
- Installs the exact versions specified
- Ensures consistency between environments

### Add the .env file in the cloned repository
Add the .env file with `OPENAI_API_KEY` and `OPENAI_MODEL_NAME`

```bash
OPENAI_API_KEY
OPENAI_MODEL_NAME
```

---

## Running the Project

We need to add the github hook pre-push script with which, whenever you try to push any feature branch, the pre-push script asks you to run the MAKE_MY_DOCS_BOT or not.

Make sure you are inside the crewAI repository and then run the following commands

```bash
cd .git/hooks
touch pre-push
```

Copy the entire content in the [pre-push-script](https://github.com/Vidit-Ostwal/MAKE_MY_DOCS_BOT/blob/main/pre-push-script) and paste that as it is in pre-push script.

Move the entire MAKE_MY_DOCS_BOT inside the CrewAI repository.
This is how it should look after moving it to CrewAI repository.

![Final Strucutre](images/Final_structure.png)

---

