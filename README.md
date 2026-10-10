# ACEest Fitness & Gym

Flask service for ACEest Fitness & Gym. It lists the baseline training programs, estimates daily calories from body weight, and stores client profiles in memory for the current process.

Calorie factors come from the supplied baseline:

| Program | Factor | Example |
|---|---|---|
| Fat Loss (FL) | 22 | 70 kg = 1540 kcal |
| Muscle Gain (MG) | 35 | 80 kg = 2800 kcal |
| Beginner (BG) | 26 | 60 kg = 1560 kcal |

Repository: https://github.com/2025tm93184/aceest-fitness

## Local setup and execution

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --host 0.0.0.0 --port 5001
```

The API listens on `http://127.0.0.1:5001`. Port 5000 is already in use on the lab machine, so the app is started on port 5001.

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Service name and gym capacity |
| GET | `/health` | Liveness check |
| GET | `/programs` | Fat Loss, Muscle Gain, and Beginner plans |
| POST | `/calories` | JSON `{"weight": 70, "program": "Fat Loss (FL)"}` |
| POST | `/clients` | JSON `{"name": "Ravi", "age": 28, "weight": 70, "program": "Fat Loss (FL)"}` |
| GET | `/clients` | Clients saved in this process |

Open `http://127.0.0.1:5001/health` to confirm the app is running.

## Run tests manually

Run Pytest from the project root, not from inside `tests/`:

```bash
source .venv/bin/activate
pytest -q
```

`pytest.ini` and `tests/conftest.py` add the project root to the Python path so the tests can import `app.py`.

## Docker

```bash
docker build -t aceest-fitness:local .
docker run --rm -p 5001:5000 aceest-fitness:local
```

The image uses `python:3.11-slim` and runs as the non-root user `appuser`. The process inside the container listens on port 5000. The host mapping `5001:5000` avoids the busy port on the lab machine.

## GitHub Actions

`.github/workflows/main.yml` runs on every `push` and `pull_request`. Each run has three stages:

1. **Lint.** `python -m py_compile app.py` checks that the application has no syntax errors.
2. **Docker image assembly.** `docker build -t aceest-fitness:ci .` builds the image from the Dockerfile.
3. **Automated testing.** `docker run` executes `pytest` inside that image, so tests use the same environment that will be deployed.

## Jenkins BUILD

Jenkins is a separate build gate. It pulls `main` from GitHub and repeats a clean install, syntax check, and test run.

On this lab machine Jenkins runs in Docker because ports 8080 and 5000 were already taken:

```bash
docker run -d --name jenkins -p 8081:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

The UI is `http://127.0.0.1:8081`. The official Jenkins image does not include Python, so Python is installed inside the container:

```bash
docker exec -u root jenkins bash -lc "apt-get update && apt-get install -y python3 python3-pip python3-venv"
```

Freestyle job `aceest-fitness-build`:

- Source Code Management: Git
- Repository URL: `https://github.com/2025tm93184/aceest-fitness.git`
- Branch: `*/main`
- Build step, Execute shell:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m py_compile app.py
pytest -q
```

**Build Now** checks out the latest `main` commit, creates a virtual environment in the Jenkins workspace, installs `requirements.txt`, compiles `app.py`, and runs Pytest. A blue build means that checkout and test run finished without errors.

The first build cloned `main` at commit `Rollback from v3.2.4 to v1.4.0` and then failed with `python3: not found`. That message comes from the Jenkins image, which does not ship Python. Run the `docker exec` install above once, then click **Build Now** again. Do not add `aceest_gui.py` to this shell step. The desktop window needs `tkinter`, and the Jenkins container does not have it.

`jenkins.desktop` on the lab machine only opens this UI. The job builds `https://github.com/2025tm93184/aceest-fitness.git`, not a folder on a laptop Desktop. Push `main` before **Build Now**.

GitHub Actions is the automated gate on every push and pull request. Jenkins is the controlled BUILD environment that fetches the same repository and validates it again.

## Versions and rollback

| Tag | What it is |
|---|---|
| `v1.4.0` | Flask app on `main`: `app.py`, Pytest, Docker, and GitHub Actions |
| `v3.2.4` | Desktop window in `aceest_gui.py`, with SQLite setup in `aceest_db.py` |

`aceest_gui.py` needs a display and the Tk library. On a Mac:

```bash
pip install matplotlib fpdf
python3 aceest_gui.py
```

Login is `admin` / `admin`. Charts need `matplotlib`. **Generate PDF Report** needs `fpdf`.

The lab host is Amazon Linux (`apt-get` is not installed there) and has no desktop. `python3 aceest_gui.py` fails with `ModuleNotFoundError: No module named 'tkinter'`. On that host, run the Flask service:

```bash
python3 app.py
```

`main` was restored with commit `Rollback from v3.2.4 to v1.4.0`. Tag `v3.2.4` stays in history. Tag `v1.4.0` is the Flask app the Jenkins job should build. The rollback is a new commit, not a force-push.

