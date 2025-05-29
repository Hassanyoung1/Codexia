from api.models.focus import BlockedApp, BlockedWebsite

class BlockingService:
    @staticmethod
    def enforce(user, hard_lock=False):
        """Generate blocking configuration for mobile clients"""
        allowed_apps = {"com.android.mms", "com.android.contacts"}
        
        blocked_apps = BlockedApp.objects.filter(user=user).exclude(
            package_name__in=allowed_apps
        )
        blocked_websites = BlockedWebsite.objects.filter(user=user)
        
        return {
            "block_apps": list(blocked_apps.values_list('package_name', flat=True)),
            "block_websites": list(blocked_websites.values_list('url', flat=True)),
            "hard_lock": hard_lock,
            "allowed_apps": list(allowed_apps)
        }