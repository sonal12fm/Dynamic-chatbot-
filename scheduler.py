from apscheduler.schedulers.blocking import BlockingScheduler
from kb_updater.pipeline import run_once
import yaml

def load_config(cfg="config.yaml"):
    import yaml
    with open(cfg,"r") as f:
        return yaml.safe_load(f)

def start_scheduler(config_path="config.yaml"):
    cfg = load_config(config_path)
    interval = cfg.get("scheduler", {}).get("interval_minutes", 60)
    sched = BlockingScheduler()
    sched.add_job(lambda: run_once(config_path), 'interval', minutes=interval)
    print(f"Scheduler started: running every {interval} minutes.")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")
