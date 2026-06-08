# 📚 Task #18: Final Documentation & Deployment Guide

**Task ID**: #18  
**Status**: Pending  
**Effort**: 12 hours  
**Priority**: MEDIUM (Knowledge transfer)  
**Owner**: Development Team  
**Start Date**: June 14, 2026  
**Target Completion**: June 15, 2026

---

## 🎯 Objective

Create comprehensive documentation for Smart Retail Analytics MVP Phase 4B enabling:
- **Operators**: Deploy and run the system in production
- **Developers**: Understand architecture and contribute
- **Users**: Use dashboards and send campaigns
- **Integrators**: Connect external systems

---

## 📋 Documentation Deliverables

### 1. README.md (Main Entry Point)
**Hours**: 1.5  
**Audience**: Everyone

```markdown
# Smart Retail Analytics MVP

AI-powered retail analytics dashboard with automated marketing via Zalo.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Kiotviet API credentials
- Zalo OA access token

### Installation

\`\`\`bash
git clone <repo>
cd smart-retail-code
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

### Configuration

\`\`\`bash
cp .env.example .env
# Edit .env with your credentials
\`\`\`

### Run

\`\`\`bash
streamlit run app.py
\`\`\`

## 📊 Features

- **RFM Segmentation**: Customer value analysis
- **Apriori Analysis**: Product bundle recommendations
- **Kiotviet Integration**: Real-time order sync
- **Zalo Campaigns**: Automated marketing messages
- **3 Role-based Dashboards**: Sales, Marketing, Manager views

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Production setup
- [API Integration](docs/API_INTEGRATION_GUIDE.md) - Kiotviet & Zalo
- [Architecture](docs/ARCHITECTURE.md) - System design
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues
- [Operations](docs/OPERATIONS_RUNBOOK.md) - Day-2 operations

## 🧪 Testing

\`\`\`bash
pytest tests/ -v
\`\`\`

## 📈 Metrics

- ✅ 100+ tests passing
- ✅ 4,500+ lines of production code
- ✅ 2 API integrations
- ✅ 3 role-based dashboards
- ✅ 99.5% target SLA

## 📞 Support

- Issue Tracker: [GitHub Issues]
- Documentation: [docs/](docs/)
- Contact: [contact info]

---

**Version**: 1.0  
**Last Updated**: June 15, 2026  
**Status**: Production Ready
```

---

### 2. DEPLOYMENT_GUIDE.md (Operations)
**Hours**: 3  
**Audience**: DevOps, System Administrators

#### Contents Structure

**1. Prerequisites Checklist**
```
- Python 3.10+ installed
- SQLite3 installed
- Network access to APIs
- 2GB disk space available
- Port 8501 available (Streamlit)
```

**2. Step-by-Step Deployment**

**Phase 1: Initial Setup** (30 min)
```bash
# 1. Clone code
git clone <repo>
cd smart-retail-code

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy configuration
cp .env.example .env
# Edit .env with your values
```

**Phase 2: Database Setup** (15 min)
```bash
# 1. Initialize database
python scripts/init_db.py

# 2. Load sample data (optional)
python scripts/load_sample_data.py

# 3. Verify schema
sqlite3 retail.db ".schema"
```

**Phase 3: API Configuration** (15 min)
```bash
# 1. Test Kiotviet API
python scripts/test_kiotviet.py

# 2. Test Zalo API
python scripts/test_zalo.py

# 3. Verify connectivity
curl https://api.kiotviet.vn/status
```

**Phase 4: Start Application** (5 min)
```bash
streamlit run app.py
# Access: http://localhost:8501
```

**Phase 5: Verification** (10 min)
- [ ] Dashboard loads
- [ ] Can select role
- [ ] Data displays
- [ ] Scheduler runs (check logs)

**3. Advanced Configuration**

- Connection pooling: `DB_MAX_CONNECTIONS`
- Cache backend: `CACHE_BACKEND` (memory/redis)
- Rate limits: `RATE_LIMIT_*`
- Log level: `LOG_LEVEL`
- Feature flags: `FEATURE_*`

**4. Monitoring & Logs**

```bash
# View logs
tail -f logs/app.log

# Monitor performance
# [Show grafana/prometheus integration if available]

# Health checks
curl http://localhost:8501/health
```

**5. Backup & Recovery**

```bash
# Backup database
sqlite3 retail.db ".dump" > backup.sql

# Restore from backup
sqlite3 retail.db < backup.sql

# Backup schedule (automated)
0 2 * * * /path/to/backup.sh
```

**6. Scaling**

- Single instance: < 1000 users
- Multiple instances: use Redis cache + shared database
- Load balancer: reverse proxy (nginx)

---

### 3. API_INTEGRATION_GUIDE.md (Developers)
**Hours**: 2  
**Audience**: Developers integrating APIs

#### Contents Structure

**1. Kiotviet API Integration**

```python
from src.kiotviet_client import KiotvietClient

# Initialize
client = KiotvietClient(
    retail_id="your_retail_id",
    api_key="your_api_key"
)

# Fetch customers
customers = client.get_customers()

# Fetch products
products = client.get_products()

# Fetch orders
invoices, items = client.get_orders()

# Sync to SQLite
result = client.sync_to_sqlite(full_sync=False)
```

**API Endpoints Supported**:
- `GET /customers` - Get all customers
- `GET /products` - Get product catalog
- `GET /invoices` - Get orders with line items
- Custom fields mapping documented

**Error Handling**:
```python
try:
    customers = client.get_customers()
except ConnectionError:
    logger.error("API connection failed")
    customers = load_cached_customers()
```

**2. Zalo OA API Integration**

```python
from src.zalo_messenger import ZaloMessenger, SegmentType

# Initialize
messenger = ZaloMessenger(access_token="your_token")

# Send to segment
result = messenger.send_segment_campaign(
    segment=SegmentType.CHAMPIONS,
    customers=customers_list,
    recommendations=["Product A", "Product B"]
)

# Get campaign stats
stats = messenger.get_campaign_stats()
```

**Message Templates Supported**:
- Champions: VIP rewards
- Potential: New products
- Loyal: Win-back
- Lost: Reactivation

**3. Database Schema**

```sql
-- Customers
CREATE TABLE customers (
    ma_khach_hang TEXT PRIMARY KEY,
    ten_khach_hang TEXT,
    dien_thoai TEXT,
    dia_chi TEXT,
    email TEXT
);

-- Products
CREATE TABLE products (
    ma_hang TEXT PRIMARY KEY,
    ten_hang TEXT,
    gia_ban REAL,
    so_luong_ton INTEGER,
    mo_ta TEXT
);

-- Invoices
CREATE TABLE invoices (
    ma_hoa_don TEXT PRIMARY KEY,
    ma_khach_hang TEXT,
    thoi_gian TEXT,
    khach_da_tra REAL,
    thanh_tien REAL,
    ghi_chu TEXT
);

-- Invoice Items
CREATE TABLE invoice_items (
    ma_hoa_don TEXT,
    ma_hang TEXT,
    so_luong INTEGER,
    gia_ban REAL,
    thanh_tien REAL
);

-- Campaigns (tracking)
CREATE TABLE campaigns (
    campaign_id TEXT PRIMARY KEY,
    segment TEXT,
    sent_at TIMESTAMP,
    sent_count INTEGER,
    success_count INTEGER,
    failure_count INTEGER,
    success_rate REAL
);
```

**4. Configuration Options**

All configurable via `.env`:
```
API_TIMEOUT=10
RETRY_ATTEMPTS=3
RATE_LIMIT_KIOTVIET=100
RATE_LIMIT_ZALO=50
CACHE_TTL_RFM=300
...
```

---

### 4. ARCHITECTURE.md (System Design)
**Hours**: 2  
**Audience**: Architects, Senior developers

#### Contents Structure

**1. System Overview**

```
┌──────────────────────┐
│  Streamlit Dashboard │
│  (3 roles)           │
└──────────┬───────────┘
           │
    ┌──────▼──────────┐
    │  Cache Layer    │ ← RFM, Apriori, Products
    └──────┬──────────┘
           │
    ┌──────▼──────────────────┐
    │  Rate Limiting          │
    │  Circuit Breaker        │
    └──────┬───────────────────┘
           │
    ┌──────▼─────────────────────┐
    │  Data Processing          │
    │  • RFM Segmentation       │
    │  • Apriori Analysis       │
    │  • Recommendations        │
    └──────┬────────────────────┘
           │
    ┌──────▼──────────┐
    │  Data Layer     │
    │  • Connection   │
    │    Pool         │
    │  • SQLite (WAL) │
    └──────┬──────────┘
           │
    ┌──────▼─────────────────┐
    │  External APIs          │
    │  • Kiotviet (sales)     │
    │  • Zalo (marketing)     │
    └─────────────────────────┘
```

**2. Data Flow Diagram**

```
Every 5 minutes:
1. Scheduler triggers
2. Kiotviet API pulls orders
3. Transform to SQLite schema
4. Update SQLite via connection pool
5. Invalidate RFM cache
6. Recalculate RFM for all customers
7. Regenerate Apriori rules
8. Update Apriori cache
9. Log completion
10. Next cycle in 5 min

User sends campaign:
1. Marketing Manager selects segment + template
2. Preview shows (from template + products)
3. User clicks Send
4. Rate limiter checks
5. Zalo messenger sends to segment
6. Track campaign in database
7. Show success/error
```

**3. Component Diagram**

- **Frontend**: Streamlit (3 dashboards)
- **Analytics**: RFM Calculator + Apriori Miner
- **Integration**: Kiotviet Client + Zalo Messenger
- **Infrastructure**: Connection Pool, Cache, Rate Limiter
- **Storage**: SQLite with WAL mode
- **Reliability**: Circuit Breaker, Retry logic

**4. API Contracts**

```python
# Kiotviet API
GET /customers → [{'id', 'name', 'phone', 'address'}]
GET /products → [{'id', 'name', 'price', 'stock'}]
GET /invoices → [{'id', 'customer_id', 'total', 'items'}]

# Zalo API
POST /message/sendtext → {'error', 'data': {'message_id'}}
```

**5. Performance Characteristics**

- RFM calculation: O(n) where n = customers
- Apriori mining: O(2^m) where m = items (pruned)
- Zalo send: 50 msg/min (rate limited)
- Dashboard response: < 500ms (with cache)

**6. Security Architecture**

- API keys in `.env` (not in code)
- Input validation on all APIs
- SQL parameterization (no injection)
- Rate limiting (DDoS protection)
- No sensitive data in logs

---

### 5. TROUBLESHOOTING.md (Support)
**Hours**: 2  
**Audience**: Support team, operators

#### Problem/Solution Format

**Issue 1: Connection refused - Kiotviet API**

Symptoms:
- Error: "Connection refused to api.kiotviet.vn"
- Dashboard shows ⚠️ API Error

Solutions (in order):
1. Check internet connectivity: `ping api.kiotviet.vn`
2. Verify `KIOTVIET_RETAIL_ID` is set: `echo $KIOTVIET_RETAIL_ID`
3. Verify `KIOTVIET_API_KEY` is correct
4. Check API rate limit: decrease `RATE_LIMIT_KIOTVIET`
5. Contact Kiotviet support if still failing

---

**Issue 2: Zalo messages not sending**

Symptoms:
- "Failed to send: Invalid phone" errors
- Campaign history shows 0% success

Solutions:
1. Verify `ZALO_ACCESS_TOKEN` is valid
2. Verify customer phone numbers are formatted correctly (Vietnamese format)
3. Check Zalo OA status: is it active?
4. Check rate limit: `RATE_LIMIT_ZALO=50`
5. Retry failed messages via dashboard

---

**Issue 3: Dashboard is slow / 500ms timeout**

Symptoms:
- Streamlit dashboard sluggish
- "Timeout waiting for data"

Solutions:
1. Check cache is working: `grep "Cache hit" logs/app.log`
2. Monitor SQLite: `sqlite3 retail.db "SELECT COUNT(*) FROM invoices"`
3. If > 100k invoices: add index on date
4. Increase `DB_TIMEOUT` to 10 seconds
5. Check connection pool: `DB_MAX_CONNECTIONS=2` is optimal

---

**Issue 4: RFM scores not updating**

Symptoms:
- RFM segments unchanged for hours
- Scheduler not running

Solutions:
1. Check scheduler is running: `ps aux | grep streamlit`
2. Check logs for errors: `tail -f logs/app.log | grep scheduler`
3. Verify sync is happening: `grep "Data refresh" logs/app.log`
4. Check cache TTL: should be 5 min for RFM

---

**Issue 5: High memory usage**

Symptoms:
- Process uses > 500MB RAM
- Dashboard becomes unresponsive

Solutions:
1. Reduce cache size: switch from memory to Redis
2. Check for memory leaks: `top -p <pid>`
3. Reduce customer/product list size if possible
4. Restart application: `systemctl restart retail-analytics`

---

**Issue 6: Database locked**

Symptoms:
- "Database is locked" error
- Campaigns can't send

Solutions:
1. Check running processes: `lsof | grep retail.db`
2. Kill stray process: `kill -9 <pid>`
3. Enable WAL mode: `PRAGMA journal_mode=WAL`
4. Increase lock timeout: `DB_TIMEOUT=10`
5. If persistent: restore from backup

---

**Common Configuration Issues**

| Config | Default | Issue | Fix |
|--------|---------|-------|-----|
| DB_MAX_CONNECTIONS | 2 | SQLite limitation | Don't increase > 2 |
| CACHE_BACKEND | memory | High memory usage | Use redis |
| LOG_LEVEL | INFO | Too verbose logs | Set to WARNING |
| RATE_LIMIT_ZALO | 50 | Campaigns slow | Increase to 100 |

---

### 6. OPERATIONS_RUNBOOK.md (Day-2 Operations)
**Hours**: 1.5  
**Audience**: Operations team

#### Daily Operations Checklist

**Morning (8:00 AM)**
```
□ Check system status: http://localhost:8501
□ Review logs for errors: tail -100 logs/app.log
□ Verify data sync working: SELECT COUNT(*) FROM invoices (should > last check)
□ Check disk space: df -h (should > 500MB available)
□ Verify Kiotviet connection: see last sync time in logs
```

**Afternoon (3:00 PM)**
```
□ Monitor performance: dashboard response time < 500ms
□ Check campaign history: any failures to investigate?
□ Review error rate: ERROR lines in logs
□ Verify rate limiting: any throttling occurring?
```

**Evening (5:00 PM)**
```
□ Prepare backup: sqlite3 retail.db ".dump" > backup.sql
□ Archive logs: gzip logs/app.log (if > 10MB)
□ Document any issues encountered
```

#### Weekly Operations (Every Friday)

```
□ Review week's metrics
  - Total campaigns sent
  - Success rate
  - API availability
  - Response time (p95)
  
□ Performance analysis
  - Cache hit rate (target > 80%)
  - Database size (alert if > 500MB)
  - Memory usage (alert if > 1GB)
  
□ Security review
  - Any unusual API calls?
  - Log for failed logins (future)
  - API key rotation schedule
```

#### Monthly Operations (First of month)

```
□ Full system health check
  - All APIs responding
  - Database integrity check: PRAGMA integrity_check
  - Backup restoration test
  - Disaster recovery plan review
  
□ Capacity planning
  - Growth rate: customers, orders, products
  - Current: X customers, Y orders/day
  - Projected in 3 months: ?
  - Any scaling needed?
  
□ Update documentation
  - Any configuration changes?
  - Any new APIs added?
  - Update runbook if process changed
```

#### Alert Procedures

**Alert: API Unavailable**
1. Check if temporary outage (Kiotviet/Zalo status)
2. Verify network connectivity
3. Check circuit breaker status (should recover after 60s)
4. If > 5 min: page on-call engineer

**Alert: High Error Rate**
1. Check logs for error pattern
2. Identify affected components
3. If Kiotviet: might be rate limited → increase timeout
4. If Zalo: might be token expired → refresh

**Alert: Database Locked**
1. Check for stray processes: `lsof | grep retail.db`
2. Kill process if safe: `kill -9 <pid>`
3. Enable WAL mode if not already
4. If persists: restore from backup, investigate cause

---

### 7. ARCHITECTURE.md (Complete)
**Hours**: Additional detail

Includes:
- Data model diagram (ERD)
- API sequence diagrams
- State machine diagrams (circuit breaker)
- Deployment architecture
- Scaling strategies
- Disaster recovery plan

---

## 📝 Documentation Checklist

### Format & Quality
- [ ] All markdown files use proper formatting
- [ ] Code blocks are syntax highlighted
- [ ] Links are working (internal and external)
- [ ] Diagrams are clear and labeled
- [ ] No typos or grammatical errors
- [ ] Tone is consistent and professional
- [ ] Examples are tested and working

### Content Completeness
- [ ] README covers quick start
- [ ] Deployment guide is step-by-step
- [ ] API docs cover all endpoints
- [ ] Architecture explains design decisions
- [ ] Troubleshooting covers common issues
- [ ] Runbook covers daily operations
- [ ] All config options documented
- [ ] Security best practices included

### Audience Appropriateness
- [ ] Operators can deploy following guide
- [ ] Developers understand architecture
- [ ] Support can troubleshoot issues
- [ ] Users can use dashboards
- [ ] Integrators can use APIs

---

## 🎯 Implementation Timeline

**Day 1 (June 14)**
- Hours 0-3: README + Quick Start
- Hours 3-6: Deployment Guide (main sections)
- Hours 6-9: API Integration Guide

**Day 2 (June 15)**
- Hours 0-2: Architecture documentation
- Hours 2-4: Troubleshooting guide
- Hours 4-5: Operations runbook
- Hours 5-6: Final review & polish

---

## ✅ Acceptance Criteria

- [ ] README completed with quick start
- [ ] Deployment guide: anyone can follow step-by-step
- [ ] API integration: all endpoints documented
- [ ] Architecture: system design clearly explained
- [ ] Troubleshooting: covers 90% of issues
- [ ] Runbook: daily/weekly/monthly procedures
- [ ] All documents pass grammar/spelling check
- [ ] Links verified working
- [ ] Code examples tested
- [ ] Diagrams clear and helpful
- [ ] No broken references
- [ ] All config options documented
- [ ] Security best practices included

---

## 📦 Deliverables

```
docs/
├── README.md                          ← Main entry point
├── DEPLOYMENT_GUIDE.md                ← Production setup
├── API_INTEGRATION_GUIDE.md            ← Developer guide
├── ARCHITECTURE.md                    ← System design
├── TROUBLESHOOTING.md                 ← Support guide
├── OPERATIONS_RUNBOOK.md              ← Day-2 operations
├── CONFIGURATION.md                   ← All config options
├── diagrams/
│   ├── system_architecture.png
│   ├── data_flow.png
│   ├── deployment.png
│   └── api_sequence.png
└── images/                            ← Screenshots
    ├── dashboard_sales.png
    ├── dashboard_marketing.png
    └── dashboard_manager.png
```

---

## 📊 Documentation Metrics

- **Total Pages**: ~50 pages
- **Code Examples**: 20+ examples
- **Diagrams**: 5+ diagrams
- **Screenshots**: 3+ screenshots
- **Estimated Read Time**: 
  - Operators: 30 min
  - Developers: 45 min
  - Support: 1 hour
  - Full review: 2-3 hours

---

## 🚀 Documentation Publishing

**Internal** (GitLab/GitHub):
- ✅ In `docs/` folder
- ✅ Linked from README
- ✅ Searchable

**External** (if applicable):
- ReadTheDocs integration
- PDF generation
- HTML static site

---

## 🔄 Documentation Maintenance

- Review quarterly (update metrics, screenshots)
- Update when APIs change
- Update when configuration changes
- Update when procedures change
- Community contributions encouraged

---

**Task Owner**: Development Team  
**Last Updated**: June 8, 2026  
**Version**: 1.0  
**Status**: Ready for Implementation
