# Optional: build and push to your registry if you do not use ConfigMap-mounted train.py + CSV.
# docker build -t <registry>/<project>/fraud-workshop-trainer:cpu -f trainer/Dockerfile trainer
FROM pytorch/pytorch:2.5.1-cpu
WORKDIR /workspace
COPY train.py /workspace/train.py
RUN mkdir -p /workspace/data /workspace/out
# COPY data/transactions.csv /workspace/data/transactions.csv
CMD ["python", "/workspace/train.py"]
