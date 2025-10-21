# 2025 SAINTCON AppSec Carnival Games

Each game is in a separate directory and language.

## Prerequisites
You must have a host with docker installed and the ability to run docker compose.


## Challenge process

1. Clone or download this repo and find the exploits in the games locally
2. Verify you can exploit against the games to win
3. Go to the AppSec Carnival Games booth to beat the game and win carnival prizes and points towards the challenge.
4. Fix the vulnerability you expoited
5. Create a submission zip: `python3 create_submission.py <challenge>`
6. Upload the zip file to the SAINTCON AppSec harness at https://appsec.saintcon.community
7. The harness will run automated tests and award points if all tests pass.

Note that you are are allowed to submit fixes before exploiting at the booth.


## Rules
See https://appsec.saintcon.community
TL;DR don't hack the infrastructure to run the challenges, and don't use paid tools (free/trial tools, including LLMS, are allowed).


## Local Testing

Each challenge can be run locally using Docker Compose in the directory for the challenge:

```bash
docker compose up --build
```

To run tests for the challenge:
```bash
docker compose --profile testing up --build
```

(Note that some older distros use `docker-compose` - use whatever works on your system)


## Creating Submissions

Use the `create_submission.py` script to package your solution files for submission to the harness.

### Usage

```bash
# List available challenges
python3 create_submission.py --list

# Create a submission for a specific challenge
python3 create_submission.py <challenge_name>

# Create submission with custom output directory
python3 create_submission.py <challenge_name> --output-dir ./submissions
```

### Important Notes

- **Only modify allowed files**: Each challenge has an `allowed_files.txt` that lists which files you can modify
- **Preserve structure**: Don't rename or move files - the submission script maintains the correct directory structure
- **Test locally**: Make sure your changes work in the challenge environment before submitting