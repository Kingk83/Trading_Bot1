# Access Guide - How to Use Your Trading System

## You Own This System Completely

This trading system is yours - you don't need Bolt to run it. Here's how to access and use it:

## Option 1: Download & Run on Your Computer

### Step 1: Download the Project
From Bolt, download all project files to your computer.

### Step 2: Install Prerequisites
```bash
# Install Python 3.9+ from python.org
# Install Node.js 18+ from nodejs.org
```

### Step 3: Setup Environment
```bash
# Navigate to project folder
cd /path/to/algotrader-pro

# Install Python dependencies
cd trading_bot
pip install -r requirements.txt

# Install Node dependencies
cd ..
npm install
```

### Step 4: Configure Your Environment
Edit the `.env` file with your credentials:
```env
# Your Supabase credentials (already configured)
VITE_SUPABASE_URL=your_url
VITE_SUPABASE_ANON_KEY=your_key

# Add exchange API keys for live trading
EXCHANGE=binance
API_KEY=your_api_key
API_SECRET=your_api_secret
PAPER_TRADING=true
```

### Step 5: Run the System
```bash
# Terminal 1: Start the dashboard
npm run dev
# Open browser to: http://localhost:5173

# Terminal 2: Initialize strategies
python trading_bot/scripts/init_strategies.py

# Terminal 3: Run the bot
python trading_bot/main.py
```

**That's it! You're running completely independently.**

## Option 2: Deploy to a Cloud Server (24/7 Operation)

For continuous trading, deploy to a VPS:

### Recommended: DigitalOcean Droplet

1. **Create a Droplet**
   - Go to digitalocean.com
   - Create $24/month droplet (4GB RAM, Ubuntu 22.04)
   - Note the IP address

2. **SSH into your server**
   ```bash
   ssh root@your-server-ip
   ```

3. **Setup the system**
   ```bash
   # Update system
   apt update && apt upgrade -y

   # Install Python & Node
   apt install python3.9 python3-pip nodejs npm git -y

   # Clone your project
   git clone <your-repo-url>
   cd algotrader-pro

   # Install dependencies
   pip install -r trading_bot/requirements.txt
   npm install
   npm run build

   # Setup environment
   nano .env  # Add your credentials

   # Initialize
   python trading_bot/scripts/init_strategies.py
   ```

4. **Run as a service** (keeps running 24/7)
   ```bash
   # Create systemd service
   nano /etc/systemd/system/trading-bot.service
   ```

   Paste:
   ```ini
   [Unit]
   Description=AlgoTrader Pro
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/algotrader-pro
   ExecStart=/usr/bin/python3 trading_bot/main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable:
   ```bash
   systemctl daemon-reload
   systemctl enable trading-bot
   systemctl start trading-bot
   systemctl status trading-bot
   ```

5. **Setup dashboard access**
   ```bash
   # Install nginx
   apt install nginx -y

   # Configure nginx (see DEPLOYMENT.md)
   # Access dashboard at: http://your-server-ip
   ```

### Other Cloud Options:
- **AWS EC2**: More scalable, slightly more expensive
- **Google Cloud**: Good for global deployment
- **Heroku**: Easy deployment but more expensive
- **Railway.app**: Simple deployment with free tier

## Option 3: Access Dashboard from Anywhere

### Your Dashboard is Already Live!

The Supabase database is accessible from anywhere. You can:

1. **Run bot on one machine** (your server)
2. **View dashboard from anywhere** (your laptop, phone, etc.)

```bash
# On your laptop (anywhere in the world)
cd algotrader-pro
npm run dev

# Dashboard connects to Supabase and shows all activity
# Even if bot is running on a server elsewhere
```

### Make Dashboard Accessible Online:

Deploy frontend to Vercel (free):
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd algotrader-pro
vercel

# You'll get a URL like: https://algotrader-xyz.vercel.app
# Access from any device!
```

Deploy to Netlify (free alternative):
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd algotrader-pro
npm run build
netlify deploy --prod --dir=dist

# Get your URL
```

## Option 4: Run in Docker (Most Portable)

If you have Docker installed:

```bash
# Build image
docker build -t trading-bot .

# Run bot
docker run -d --name trading-bot \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  trading-bot

# Run dashboard
docker run -d --name dashboard \
  -p 5173:5173 \
  -v $(pwd):/app \
  node:18 \
  sh -c "cd /app && npm run dev"

# Access at: http://localhost:5173
```

## What You Get Without Bolt

### ✅ Full Access to Everything:
- Complete source code
- All strategies
- Dashboard
- Database access
- Documentation

### ✅ You Can:
- Run on your computer
- Deploy to any server
- Modify any code
- Add new strategies
- Scale to any size
- Use forever without Bolt

### ✅ No Dependencies on Bolt:
- Database is your Supabase account
- Code is standard Python + React
- Can run anywhere Python + Node runs
- No proprietary technology

## Your Data & Control

### Database (Supabase)
- **Your account**: You control it
- **Your data**: Stored in your Supabase project
- **Access**: Direct SQL access anytime
- **Backup**: Supabase handles backups
- **Cost**: Free tier includes everything you need

### Exchange APIs
- **Your keys**: You control them
- **Your capital**: In your exchange account
- **Direct access**: Bot connects to your account
- **Full control**: Can trade manually anytime

## Recommended Setup

For serious trading:

1. **Development** (Your Laptop)
   - Run backtests
   - Test strategies
   - Develop new features
   - View dashboard

2. **Production** (VPS/Cloud)
   - 24/7 bot operation
   - Ubuntu server
   - Systemd service
   - Nginx for dashboard
   - SSL certificate

3. **Monitoring** (Anywhere)
   - Dashboard on Vercel
   - Check phone/laptop
   - Email alerts
   - Performance tracking

## Getting Your Code

### From Bolt:
1. Click download/export
2. Get ZIP file with all code
3. Extract to your computer
4. Follow setup steps above

### To GitHub (Recommended):
```bash
# Create new repo on GitHub
# Then:
git init
git add .
git commit -m "Initial commit - AlgoTrader Pro"
git remote add origin https://github.com/yourusername/algotrader-pro.git
git push -u origin main

# Now you can clone anywhere:
git clone https://github.com/yourusername/algotrader-pro.git
```

## Cost Breakdown

### Free Option:
- Development: Your computer (free)
- Database: Supabase free tier (free)
- Dashboard: Vercel free tier (free)
- **Total: $0/month**

### Professional Option:
- VPS: DigitalOcean droplet ($24/month)
- Database: Supabase free tier (free)
- Domain: Namecheap ($12/year)
- SSL: Let's Encrypt (free)
- **Total: ~$25/month**

### Enterprise Option:
- AWS EC2 instances ($50-200/month)
- RDS database ($30/month)
- CloudWatch monitoring ($10/month)
- **Total: $90-240/month**

## Support After Leaving Bolt

### Self-Support:
- **README.md**: Complete documentation
- **QUICKSTART.md**: Setup guide
- **DEPLOYMENT.md**: Production guide
- **Code comments**: Extensive inline docs

### Community:
- GitHub issues
- Trading forums
- Python/React communities
- CCXT documentation

### Professional:
- Hire developer on Upwork
- Consulting services
- Trading system specialists

## Quick Reference Commands

```bash
# Run backtest
python trading_bot/scripts/run_backtest.py

# Start paper trading
python trading_bot/main.py

# Start live trading (after testing!)
# Set PAPER_TRADING=false in .env
python trading_bot/main.py

# Start dashboard
npm run dev

# Build for production
npm run build

# View logs
tail -f trading_bot/logs/bot.log

# Check bot status (on server)
systemctl status trading-bot

# Restart bot (on server)
systemctl restart trading-bot
```

## Next Steps

1. **Download the project** from Bolt
2. **Run locally** to verify everything works
3. **Test with backtests** to understand strategies
4. **Paper trade** for 30 days minimum
5. **Deploy to VPS** when ready for 24/7
6. **Start small** with real capital
7. **Scale gradually** as you gain confidence

## Important Notes

### You Own This 100%
- All code is yours
- No licensing restrictions
- Modify freely
- Use commercially
- No ongoing fees to Bolt

### Independence
- Runs without internet (except exchange APIs)
- No external dependencies on Bolt
- Standard technologies (Python, React)
- Can run offline for testing/development

### Data Privacy
- Your trades stay in your Supabase
- Your API keys stay with you
- No data sent to third parties
- Full control over everything

## Questions?

Check the documentation:
- **README.md** - General usage
- **QUICKSTART.md** - Fast setup
- **DEPLOYMENT.md** - Production deployment
- **SYSTEM_OVERVIEW.md** - Architecture details

The system is completely yours to use, modify, and deploy however you want!

---

**You are completely independent of Bolt. This is your trading system now.**
