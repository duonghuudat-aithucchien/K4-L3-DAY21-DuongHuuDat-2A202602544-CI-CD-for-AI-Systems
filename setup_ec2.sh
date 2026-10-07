sudo apt update && sudo apt install -y python3-pip
pip3 install fastapi uvicorn scikit-learn joblib boto3

sudo tee /etc/systemd/system/income-api.service > /dev/null <<EOF
[Unit]
Description=Income Model Inference Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu
Environment="ARTIFACT_BUCKET=income-api-dat-2026-v2"
ExecStart=/usr/bin/python3 -m uvicorn src.serve:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now income-api

ssh-keygen -t ed25519 -f ~/.ssh/income_deploy -N "" -C "github-actions-deploy"
cat ~/.ssh/income_deploy.pub >> ~/.ssh/authorized_keys
echo "=== GITHUB ACTIONS PRIVATE KEY ==="
cat ~/.ssh/income_deploy
