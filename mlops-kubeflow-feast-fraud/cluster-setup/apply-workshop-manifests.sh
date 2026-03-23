#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NS="${WORKSHOP_NAMESPACE:-}"
if [[ -z "${NS}" ]]; then
  echo "Set WORKSHOP_NAMESPACE (e.g. export WORKSHOP_NAMESPACE=worshop-example)" >&2
  exit 1
fi

apply() {
  local f="$1"
  sed "s/REPLACE_NAMESPACE/${NS}/g" "${ROOT}/manifests/${f}" | oc apply -f -
}

apply "workshop-training-configmap.yaml"
apply "trainjob-fraud-workshop.yaml"

echo "Applied workshop manifests to namespace: ${NS}"
echo "Check: oc get configmap workshop-training -n ${NS}"
echo "Check: oc get trainjob -n ${NS} 2>/dev/null || echo 'TrainJob CRD not installed yet'"
