# Deployment Guide

Professional deployment strategies for AlgoTrader Pro, from development to production.

## Deployment Environments

### 1. Local Development
- Testing and development
- Paper trading
- Strategy development

### 2. VPS/Cloud Production
- 24/7 operation
- Low latency
- Automated monitoring

### 3. Hedge Fund Infrastructure
- Institutional-grade setup
- High availability
- Compliance and reporting

## Local Deployment

### Development Setup

```bash
# Clone repository
git clone <your-repo>
cd algotrader-pro

# Setup Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r trading_bot/requirements.txt

# Setup Node environment
npm install

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Initialize database
python trading_bot/scripts/init_strategies.py

# Run tests
python trading_bot/scripts/run_backtest.py
```

### Running with Screen (Unix/Linux/Mac)

```bash
# Start bot in background
screen -S trading-bot
python trading_bot/main.py
# Press Ctrl+A then D to detach

# Start dashboard
screen -S dashboard
npm run dev
# Press Ctrl+A then D to detach

# List screens
screen -ls

# Reattach to screen
screen -r trading-bot

# Kill screen
screen -X -S trading-bot quit
```

## VPS Deployment (DigitalOcean/AWS/GCP)

### Server Requirements

**Minimum Specs:**
- 2 CPU cores
- 4GB RAM
- 25GB SSD
- Ubuntu 22.04 LTS

**Recommended Specs:**
- 4 CPU cores
- 8GB RAM
- 50GB SSD
- Ubuntu 22.04 LTS

### Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3-pip python3-venv -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install additional tools
sudo apt install git nginx certbot python3-certbot-nginx -y

# Setup firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Application Deployment

```bash
# Create application user
sudo useradd -m -s /bin/bash trading
sudo su - trading

# Clone repository
git clone <your-repo> /home/trading/algotrader
cd /home/trading/algotrader

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r trading_bot/requirements.txt

# Setup Node environment
npm install
npm run build

# Configure environment
nano .env
# Add your production credentials
```

### Systemd Service Setup

Create `/etc/systemd/system/trading-bot.service`:

```ini
[Unit]
Description=AlgoTrader Pro Trading Bot
After=network.target

[Service]
Type=simple
User=trading
WorkingDirectory=/home/trading/algotrader
Environment="PATH=/home/trading/algotrader/venv/bin"
ExecStart=/home/trading/algotrader/venv/bin/python trading_bot/main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/trading/algotrader/logs/bot.log
StandardError=append:/home/trading/algotrader/logs/error.log

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

### Nginx Configuration for Dashboard

Create `/etc/nginx/sites-available/trading-dashboard`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /home/trading/algotrader/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/trading-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate with Let's Encrypt

```bash
sudo certbot --nginx -d your-domain.com
sudo systemctl restart nginx
```

### Log Rotation

Create `/etc/logrotate.d/trading-bot`:

```
/home/trading/algotrader/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 trading trading
    sharedscripts
    postrotate
        systemctl reload trading-bot > /dev/null 2>&1 || true
    endscript
}
```

## Monitoring and Alerts

### System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor bot process
htop -p $(pgrep -f "python trading_bot/main.py")

# Monitor logs in real-time
tail -f /home/trading/algotrader/logs/bot.log
```

### Email Alerts (Optional)

Install and configure Postfix:

```bash
sudo apt install postfix mailutils -y
```

Add alert script `/home/trading/scripts/alert.py`:

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'bot@yourdomain.com'
    msg['To'] = 'you@email.com'

    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)
```

### Health Check Script

Create `/home/trading/scripts/health_check.sh`:

```bash
#!/bin/bash

# Check if bot is running
if ! pgrep -f "python trading_bot/main.py" > /dev/null; then
    echo "Trading bot is not running!"
    systemctl restart trading-bot
    # Send alert
fi

# Check CPU usage
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
if (( $(echo "$CPU > 80" | bc -l) )); then
    echo "High CPU usage: $CPU%"
fi

# Check memory usage
MEM=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
if (( $(echo "$MEM > 80" | bc -l) )); then
    echo "High memory usage: $MEM%"
fi
```

Add to crontab:
```bash
crontab -e
# Add line:
*/5 * * * * /home/trading/scripts/health_check.sh
```

## Docker Deployment (Advanced)

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY trading_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY trading_bot/ ./trading_bot/
COPY .env .

# Run bot
CMD ["python", "trading_bot/main.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  trading-bot:
    build: .
    restart: always
    environment:
      - PAPER_TRADING=false
    volumes:
      - ./logs:/app/logs
      - ./.env:/app/.env
    networks:
      - trading-network

  dashboard:
    image: node:18
    working_dir: /app
    command: npm run dev
    volumes:
      - ./:/app
    ports:
      - "5173:5173"
    networks:
      - trading-network

networks:
  trading-network:
    driver: bridge
```

Run with Docker:

```bash
docker-compose up -d
docker-compose logs -f trading-bot
```

## Kubernetes Deployment (Enterprise)

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: trading-bot
  template:
    metadata:
      labels:
        app: trading-bot
    spec:
      containers:
      - name: trading-bot
        image: your-registry/trading-bot:latest
        env:
        - name: PAPER_TRADING
          value: "false"
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: trading-secrets
              key: supabase-url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

## Backup Strategy

### Database Backups

```bash
# Create backup directory
mkdir -p /home/trading/backups

# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
# Supabase handles database backups automatically
# Backup local logs
tar -czf /home/trading/backups/logs_$DATE.tar.gz /home/trading/algotrader/logs/
# Keep only last 30 days
find /home/trading/backups/ -name "*.tar.gz" -mtime +30 -delete
```

### Configuration Backups

```bash
# Backup .env and configs
cp /home/trading/algotrader/.env /home/trading/backups/.env.backup
cp /home/trading/algotrader/trading_bot/config.py /home/trading/backups/config.py.backup
```

## Security Best Practices

### API Key Security

1. **Never commit API keys to Git**
2. **Use environment variables**
3. **Rotate keys regularly**
4. **Use IP whitelisting on exchange**
5. **Enable 2FA on exchange account**

### Server Security

```bash
# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Use SSH keys instead of passwords
ssh-copy-id trading@your-server

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

### Application Security

1. **Run bot as non-root user**
2. **Use firewall (ufw)**
3. **Keep system updated**
4. **Monitor logs for suspicious activity**
5. **Use HTTPS for dashboard**

## Performance Optimization

### System Tuning

```bash
# Increase file descriptors
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize network
echo "net.core.somaxconn = 1024" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 2048" >> /etc/sysctl.conf
sudo sysctl -p
```

### Application Optimization

1. **Use connection pooling** for database
2. **Cache indicator calculations**
3. **Optimize data fetching intervals**
4. **Use WebSocket for real-time data**

## Disaster Recovery

### Recovery Plan

1. **Regular backups** (automated)
2. **Documented recovery procedures**
3. **Test recovery process monthly**
4. **Keep emergency contact list**

### Emergency Procedures

```bash
# Stop all trading immediately
sudo systemctl stop trading-bot

# Close all positions (manual via exchange)
# Check position status in dashboard

# Review logs for issues
tail -n 1000 /home/trading/algotrader/logs/bot.log

# Restore from backup if needed
tar -xzf /home/trading/backups/latest_backup.tar.gz

# Restart with paper trading
# Set PAPER_TRADING=true in .env
sudo systemctl start trading-bot
```

## Cost Estimation

### Monthly Costs

**VPS Hosting:**
- DigitalOcean: $24/month (4GB RAM)
- AWS EC2 t3.medium: ~$30/month
- Google Cloud e2-medium: ~$25/month

**Additional Services:**
- Domain: $12/year
- SSL Certificate: Free (Let's Encrypt)
- Monitoring: Free (self-hosted)

**Total: ~$25-35/month**

## Scaling Considerations

### From $10K to $1M Capital

**Infrastructure:**
- Upgrade to 8GB RAM server
- Add redundancy (backup server)
- Professional monitoring (DataDog, NewRelic)

**Development:**
- More strategies
- Better risk management
- Compliance reporting

**Team:**
- DevOps engineer
- Risk manager
- Compliance officer

## Compliance and Regulation

### Record Keeping

1. **Trade logs** - Keep all trades for 7 years
2. **Decision logs** - Document strategy decisions
3. **Risk events** - Track all risk limit breaches
4. **System changes** - Version control all code

### Reporting

- Daily P&L reports
- Monthly performance attribution
- Quarterly risk assessments
- Annual audits

## Support and Maintenance

### Regular Maintenance Tasks

**Daily:**
- Check bot status
- Review open positions
- Monitor risk metrics

**Weekly:**
- Review performance
- Check system logs
- Update strategies if needed

**Monthly:**
- System updates
- Security patches
- Backup verification
- Performance review

### Troubleshooting Checklist

1. Check bot is running: `systemctl status trading-bot`
2. Review recent logs: `tail -n 100 logs/bot.log`
3. Check disk space: `df -h`
4. Check memory: `free -h`
5. Test exchange connection
6. Verify database connection
7. Review risk events table

---

**Remember: Professional deployment requires careful planning, testing, and monitoring. Start small and scale gradually.**
