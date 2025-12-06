# Google Cloud Platform - Firewall Setup Guide

## Quick Setup to Access from Your MacBook

### Step 1: Open Port 80 in Google Cloud Console

#### Option A: Using Google Cloud Console (Web UI)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select your project

2. **Navigate to Firewall Rules**
   - Go to: **VPC Network** → **Firewall** (or search "Firewall" in the search bar)
   - Or direct link: https://console.cloud.google.com/networking/firewalls

3. **Create New Firewall Rule**
   - Click **"CREATE FIREWALL RULE"** button
   - Fill in the details:
     - **Name**: `allow-http-traffic`
     - **Description**: `Allow HTTP traffic on port 80`
     - **Network**: Select your VPC network (usually `default`)
     - **Priority**: `1000` (default)
     - **Direction of traffic**: `Ingress`
     - **Action on match**: `Allow`
     - **Targets**: `All instances in the network` (or select specific tags)
     - **Source IP ranges**: `0.0.0.0/0` (allows from anywhere)
     - **Protocols and ports**: 
       - Check **TCP**
       - Enter port: `80`
   - Click **"CREATE"**

4. **Optional: Create HTTPS Rule (for SSL)**
   - Repeat above steps with:
     - **Name**: `allow-https-traffic`
     - **Port**: `443`

#### Option B: Using gcloud CLI (Command Line)

If you have `gcloud` CLI installed on your MacBook:

```bash
# Authenticate (if not already done)
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create firewall rule for HTTP
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP traffic from anywhere" \
    --direction INGRESS

# Create firewall rule for HTTPS (optional)
gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTPS traffic from anywhere" \
    --direction INGRESS
```

### Step 2: Verify Firewall Rules

Check if rules are created:

```bash
gcloud compute firewall-rules list | grep allow-http
```

Or check in the Console: https://console.cloud.google.com/networking/firewalls

### Step 3: Apply Firewall Rule to Your VM Instance

#### Option A: Using Tags (Recommended)

1. **Add Network Tag to Your VM**
   - Go to: **Compute Engine** → **VM instances**
   - Click on your VM instance name
   - Click **"EDIT"**
   - Under **"Network tags"**, add: `http-server`
   - Click **"SAVE"**

2. **Update Firewall Rule to Target Tag**
   - Go back to Firewall rules
   - Edit the `allow-http` rule
   - Change **Targets** to: `Specified target tags`
   - Enter tag: `http-server`
   - Save

#### Option B: Apply to All Instances

If you set the firewall rule to "All instances in the network", it will automatically apply.

### Step 4: Access from Your MacBook Browser

Once the firewall is configured, open your MacBook browser and visit:

**Frontend:**
```
http://34.93.19.177/
```

**Backend API:**
```
http://34.93.19.177/api/v1/
```

**Admin Panel:**
```
http://34.93.19.177/admin/
```

### Step 5: Verify External Access

Test from your MacBook terminal:

```bash
# Test if port 80 is accessible
curl -I http://34.93.19.177/

# Or use telnet
telnet 34.93.19.177 80
```

If you get a response, the firewall is configured correctly!

## Troubleshooting

### If you still can't access:

1. **Check VM Instance Status**
   ```bash
   gcloud compute instances list
   ```
   Make sure the instance is running.

2. **Check Firewall Rules**
   ```bash
   gcloud compute firewall-rules list
   ```
   Verify `allow-http` rule exists and allows `0.0.0.0/0`

3. **Check Instance Tags**
   ```bash
   gcloud compute instances describe INSTANCE_NAME --zone=ZONE --format="get(tags.items)"
   ```
   Make sure the instance has the correct tags if using tag-based rules.

4. **Check if Nginx is Running on Server**
   ```bash
   # SSH into your server
   ssh YOUR_USER@34.93.19.177
   
   # Check if nginx is listening
   sudo netstat -tlnp | grep :80
   ```

5. **Test from Server Itself**
   ```bash
   # On the server
   curl http://localhost/
   ```
   If this works but external doesn't, it's definitely a firewall issue.

### Common Issues

**Issue: "Connection timed out"**
- Firewall rule not applied to your instance
- Wrong source IP range
- Instance doesn't have the required network tag

**Issue: "Connection refused"**
- Service not running on the server
- Service listening on wrong interface (should be 0.0.0.0:80)

**Issue: "403 Forbidden" or "502 Bad Gateway"**
- Service is running but has configuration issues
- Check server logs: `sudo docker compose logs`

## Security Recommendations

For production, consider:

1. **Restrict Source IP** (instead of 0.0.0.0/0)
   - Only allow from specific IPs: `YOUR_OFFICE_IP/32`
   - Or use VPN/Cloud IAP for access

2. **Use HTTPS**
   - Set up SSL certificate (Let's Encrypt)
   - Only allow port 443
   - Redirect HTTP to HTTPS

3. **Use Load Balancer**
   - Google Cloud Load Balancer
   - Better security and scalability

## Quick Reference Commands

```bash
# List all firewall rules
gcloud compute firewall-rules list

# Describe a specific rule
gcloud compute firewall-rules describe allow-http

# Delete a firewall rule
gcloud compute firewall-rules delete allow-http

# Add tag to instance
gcloud compute instances add-tags INSTANCE_NAME \
    --tags http-server \
    --zone ZONE

# Remove tag from instance
gcloud compute instances remove-tags INSTANCE_NAME \
    --tags http-server \
    --zone ZONE
```

## Need Help?

If you're still having issues:
1. Check Google Cloud Console → Logging → View logs
2. Check server logs: `sudo docker compose logs`
3. Verify instance external IP: `gcloud compute instances list`

---

**Your Server IP:** `34.93.19.177`
**Port to Open:** `80` (and `443` for HTTPS)
