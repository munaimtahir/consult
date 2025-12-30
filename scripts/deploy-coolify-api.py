#!/usr/bin/env python3

"""
Coolify API Deployment Script (Python)
This script deploys the consult application to Coolify using the API
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, Optional, Any

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_colored(message: str, color: str = Colors.NC):
    """Print colored message"""
    print(f"{color}{message}{Colors.NC}")

def load_config(config_file: Path) -> Dict[str, str]:
    """Load configuration from .env file"""
    config = {}
    if not config_file.exists():
        print_colored(f"Error: Configuration file not found: {config_file}", Colors.RED)
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config

def load_env_vars(env_file: Path) -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}
    if not env_file.exists():
        print_colored(f"Error: Environment file not found: {env_file}", Colors.RED)
        sys.exit(1)
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    env_vars[key.strip()] = value
    
    return env_vars

class CoolifyAPI:
    """Coolify API client"""
    
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            
            # Try to parse JSON, return empty dict if not JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                return {'raw': response.text}
        
        except requests.exceptions.RequestException as e:
            print_colored(f"API Error: {e}", Colors.RED)
            if hasattr(e.response, 'text'):
                print_colored(f"Response: {e.response.text}", Colors.RED)
            raise
    
    def check_connectivity(self) -> bool:
        """Check API connectivity"""
        print_colored("Checking API connectivity...", Colors.YELLOW)
        try:
            response = self._request('GET', '/servers')
            print_colored("✓ API connection successful", Colors.GREEN)
            return True
        except Exception as e:
            print_colored(f"Error: API authentication failed: {e}", Colors.RED)
            return False
    
    def get_project(self, project_id: str) -> Optional[str]:
        """Get or create project"""
        print_colored(f"Getting project: {project_id}", Colors.YELLOW)
        try:
            response = self._request('GET', '/projects')
            
            # Try to find project
            if isinstance(response, list):
                for project in response:
                    if project.get('name') == project_id or project.get('uuid') == project_id:
                        print_colored(f"✓ Project found: {project.get('uuid')}", Colors.GREEN)
                        return project.get('uuid')
            
            # Create project if not found
            print_colored("Project not found, creating new project...", Colors.YELLOW)
            project_data = {'name': project_id}
            response = self._request('POST', '/projects', project_data)
            project_uuid = response.get('uuid', project_id)
            print_colored(f"✓ Project created: {project_uuid}", Colors.GREEN)
            return project_uuid
        
        except Exception as e:
            print_colored(f"Error getting/creating project: {e}", Colors.RED)
            return None
    
    def check_application(self, project_id: str, app_name: str = 'consult') -> Optional[str]:
        """Check if application exists"""
        print_colored("Checking if application exists...", Colors.YELLOW)
        try:
            response = self._request('GET', f'/projects/{project_id}/applications')
            
            if isinstance(response, list):
                for app in response:
                    if app.get('name') == app_name:
                        app_uuid = app.get('uuid')
                        print_colored(f"✓ Application found: {app_uuid}", Colors.GREEN)
                        return app_uuid
            
            print_colored("Application not found", Colors.YELLOW)
            return None
        
        except Exception as e:
            print_colored(f"Error checking application: {e}", Colors.YELLOW)
            return None
    
    def create_application(self, project_id: str, server_id: str) -> Optional[str]:
        """Create new Docker Compose application"""
        print_colored("Creating new Docker Compose application...", Colors.YELLOW)
        
        app_data = {
            'name': 'consult',
            'description': 'Hospital Consult System',
            'type': 'dockercompose',
            'git_repository': 'https://github.com/munaimtahir/consult',
            'git_branch': 'main',
            'docker_compose_file': 'docker-compose.coolify.yml',
            'server_id': server_id
        }
        
        try:
            response = self._request('POST', f'/projects/{project_id}/applications', app_data)
            app_uuid = response.get('uuid')
            if app_uuid:
                print_colored(f"✓ Application created: {app_uuid}", Colors.GREEN)
                return app_uuid
            else:
                print_colored(f"Warning: Response: {response}", Colors.YELLOW)
                return None
        except Exception as e:
            print_colored(f"Error creating application: {e}", Colors.RED)
            return None
    
    def set_environment_variables(self, app_uuid: str, env_vars: Dict[str, str]) -> bool:
        """Set environment variables"""
        print_colored("Setting environment variables...", Colors.YELLOW)
        
        try:
            # Coolify API may expect different format
            # Try different endpoint formats
            endpoints = [
                f'/applications/{app_uuid}/environment-variables',
                f'/applications/{app_uuid}/env',
                f'/applications/{app_uuid}/secrets'
            ]
            
            for endpoint in endpoints:
                try:
                    self._request('POST', endpoint, {'environment_variables': env_vars})
                    print_colored("✓ Environment variables set", Colors.GREEN)
                    return True
                except:
                    continue
            
            print_colored("Warning: May need to set environment variables manually in Coolify dashboard", Colors.YELLOW)
            return False
        
        except Exception as e:
            print_colored(f"Warning: {e}", Colors.YELLOW)
            return False
    
    def configure_domain(self, app_uuid: str, domain: str) -> bool:
        """Configure domain"""
        print_colored(f"Configuring domain: {domain}", Colors.YELLOW)
        
        domain_data = {
            'domain': domain,
            'enable_ssl': True,
            'force_https': True
        }
        
        try:
            self._request('POST', f'/applications/{app_uuid}/domains', domain_data)
            print_colored("✓ Domain configured", Colors.GREEN)
            return True
        except Exception as e:
            print_colored(f"Warning: Domain may need manual setup: {e}", Colors.YELLOW)
            return False
    
    def trigger_deployment(self, app_uuid: str, force_rebuild: bool = False) -> bool:
        """Trigger deployment"""
        print_colored("Triggering deployment...", Colors.YELLOW)
        
        deploy_data = {'force_rebuild': force_rebuild}
        
        try:
            # Try different endpoint formats
            endpoints = [
                f'/applications/{app_uuid}/deploy',
                f'/applications/{app_uuid}/deployment',
                f'/deploy/{app_uuid}'
            ]
            
            for endpoint in endpoints:
                try:
                    self._request('POST', endpoint, deploy_data)
                    print_colored("✓ Deployment triggered", Colors.GREEN)
                    return True
                except:
                    continue
            
            print_colored("Warning: May need to trigger deployment manually", Colors.YELLOW)
            return False
        
        except Exception as e:
            print_colored(f"Error triggering deployment: {e}", Colors.RED)
            return False

def validate_deployment(domain: str, public_ip: str):
    """Validate deployment"""
    print_colored("Waiting for deployment to initialize (30 seconds)...", Colors.YELLOW)
    time.sleep(30)
    
    print_colored("Validating deployment...", Colors.YELLOW)
    
    # Check domain
    try:
        response = requests.get(f"https://{domain}/api/v1/health/", timeout=10, verify=False)
        if response.status_code in [200, 301, 302]:
            print_colored("✓ Domain is accessible", Colors.GREEN)
        else:
            print_colored(f"⚠ Domain returned status {response.status_code}", Colors.YELLOW)
    except Exception as e:
        print_colored(f"⚠ Domain may not be ready yet: {e}", Colors.YELLOW)
    
    # Check public IP
    try:
        response = requests.get(f"http://{public_ip}/api/v1/health/", timeout=10)
        if response.status_code == 200:
            print_colored("✓ Public IP is accessible", Colors.GREEN)
        else:
            print_colored(f"⚠ Public IP returned status {response.status_code}", Colors.YELLOW)
    except Exception as e:
        print_colored(f"⚠ Public IP endpoint not ready yet: {e}", Colors.YELLOW)

def main():
    """Main deployment flow"""
    # Get script directory
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    # Load configuration
    config_file = repo_root / 'coolify-api-config.env'
    env_file = repo_root / 'coolify-deploy.env'
    
    config = load_config(config_file)
    env_vars = load_env_vars(env_file)
    
    # Initialize API client
    api = CoolifyAPI(
        api_url=config.get('COOLIFY_API_URL'),
        api_token=config.get('COOLIFY_API_TOKEN')
    )
    
    print_colored("========================================", Colors.BLUE)
    print_colored("Coolify API Deployment", Colors.BLUE)
    print_colored("========================================", Colors.BLUE)
    print()
    print_colored("Configuration:", Colors.GREEN)
    print(f"  API URL: {config.get('COOLIFY_API_URL')}")
    print(f"  Server ID: {config.get('COOLIFY_SERVER_ID')}")
    print(f"  Project ID: {config.get('COOLIFY_PROJECT_ID')}")
    print(f"  Domain: {config.get('COOLIFY_DOMAIN')}")
    print(f"  Public IP: {config.get('COOLIFY_PUBLIC_IP')}")
    print()
    
    # Check API connectivity
    if not api.check_connectivity():
        sys.exit(1)
    
    # Get or create project
    project_id = api.get_project(config.get('COOLIFY_PROJECT_ID'))
    if not project_id:
        print_colored("Error: Could not get/create project", Colors.RED)
        sys.exit(1)
    
    # Check if application exists
    app_uuid = api.check_application(project_id)
    
    # Create application if it doesn't exist
    if not app_uuid:
        app_uuid = api.create_application(project_id, config.get('COOLIFY_SERVER_ID'))
        if not app_uuid:
            print_colored("Error: Could not create application", Colors.RED)
            sys.exit(1)
    
    # Set environment variables
    api.set_environment_variables(app_uuid, env_vars)
    
    # Configure domain
    api.configure_domain(app_uuid, config.get('COOLIFY_DOMAIN'))
    
    # Trigger deployment
    if not api.trigger_deployment(app_uuid):
        print_colored("Note: You may need to trigger deployment manually from Coolify dashboard", Colors.YELLOW)
    
    # Validate deployment
    validate_deployment(
        config.get('COOLIFY_DOMAIN'),
        config.get('COOLIFY_PUBLIC_IP')
    )
    
    print()
    print_colored("========================================", Colors.GREEN)
    print_colored("Deployment process completed!", Colors.GREEN)
    print_colored("========================================", Colors.GREEN)
    print()
    print_colored("Next steps:", Colors.BLUE)
    print("1. Monitor deployment in Coolify dashboard")
    print("2. Check logs if any issues occur")
    print(f"3. Verify DNS has propagated: nslookup {config.get('COOLIFY_DOMAIN')}")
    print("4. Test endpoints after deployment completes")
    print()
    print_colored("Access points:", Colors.BLUE)
    print(f"  Domain: https://{config.get('COOLIFY_DOMAIN')}")
    print(f"  Public IP: http://{config.get('COOLIFY_PUBLIC_IP')}")
    print(f"  Dashboard: http://{config.get('COOLIFY_PUBLIC_IP')}:8000")

if __name__ == '__main__':
    main()

