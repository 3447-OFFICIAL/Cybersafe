import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cysafe_project.settings')
django.setup()

from django.test import Client
from main.models import AdminUser

def run_tests():
    c = Client()
    # Define a helper to pass the host
    def client_get(path):
        return c.get(path, HTTP_HOST='127.0.0.1')

    print("1. Requesting admin dashboard (GET /admin/dashboard/) without login...")
    try:
        res = client_get('/admin/dashboard/')
        print(f"Response status: {res.status_code}")
        if res.status_code == 302:
            print(f"Redirects to: {res['Location']}")
        else:
            print(res.content.decode('utf-8', errors='ignore')[:1000])
    except Exception as e:
        print("EXCEPTION RAISED:")
        import traceback
        traceback.print_exc()

    print("\n2. Requesting admin crimes (GET /admin/crimes/) without login...")
    try:
        res = client_get('/admin/crimes/')
        print(f"Response status: {res.status_code}")
        if res.status_code == 302:
            print(f"Redirects to: {res['Location']}")
        else:
            print(res.content.decode('utf-8', errors='ignore')[:1000])
    except Exception as e:
        print("EXCEPTION RAISED:")
        import traceback
        traceback.print_exc()

    print("\n3. Logging in as superuser 'tanu'...")
    user = AdminUser.objects.filter(username='tanu').first()
    if not user:
        print("Superuser 'tanu' not found in database!")
        return
    c.force_login(user)
    print("Logged in successfully!")

    urls = [
        '/api/system/health/',
        '/api/system/uptime/',
        '/api/security/stats/',
        '/api/security/events/',
        '/admin/monitoring/'
    ]

    for url in urls:
        print(f"\nRequesting {url}...")
        try:
            res = client_get(url)
            print(f"Response status: {res.status_code}")
            if res.status_code == 500:
                print(res.content.decode('utf-8', errors='ignore')[:2000])
            elif res.status_code == 200 and 'json' in res.get('Content-Type', ''):
                print(f"Response data: {res.json()}")
        except Exception as e:
            print("EXCEPTION RAISED:")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    run_tests()
