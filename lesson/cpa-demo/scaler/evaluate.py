import json
import sys

def main():
    # Parse provided spec into a dict
    stdin = sys.stdin.read()
    spec = json.loads(stdin)
    # sys.stderr.write(f'evaluate input: {spec}')
    sys.stderr.write(stdin)
    evaluate(spec)
    
def evaluate(spec):
    try:
        value = int(spec["metrics"][0]["value"])

        # Get current replica count
        target_replica_count = int(spec["resource"]["spec"]["replicas"])

        sys.stderr.write(f'replica count before scale: {target_replica_count}')
        # # Decrease target replicas if more than 5 available
        # if target_replica_count > 5:
        #     target_replica_count -= 1
        # # Increase target replicas if none available
        # if target_replica_count <= 0:
        #     target_replica_count += 1

        # Build JSON dict with targetReplicas
        evaluation = {}
        evaluation["targetReplicas"] = value

        # Output JSON to stdout
        sys.stdout.write(json.dumps(evaluation))
    except ValueError as err:
        # If not an integer, output error
        sys.stderr.write(f"Invalid metric value: {err}")
        exit(1)

if __name__ == "__main__":
    main()