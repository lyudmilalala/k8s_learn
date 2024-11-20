import json
import sys

def main():
    # Parse spec into a dict
    stdin = sys.stdin.read()
    spec = json.loads(stdin)
    # sys.stderr.write(f'metrics gather input: {spec}')
    sys.stderr.write(stdin)
    metric(spec)

def metric(spec):
    # Get metadata from resource information provided
    metadata = spec["resource"]["metadata"]
    # Get labels from provided metdata
    labels = metadata["labels"]

    if "numPods" in labels:
        # If numPods label exists, output the value of the numPods
        # label back to the autoscaler
        sys.stdout.write(labels["numPods"])
    else:
        # If no label numPods, output an error and fail the metric gathering
        sys.stderr.write("No 'numPods' label on resource being managed")
        exit(1)

if __name__ == "__main__":
    main()