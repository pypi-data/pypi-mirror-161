Pure Fusion is fully API-driven. Most APIs which change the system (POST, PATCH, DELETE) return an Operation in status 'Pending' or 'Running';. You can poll (GET) the operation to check its status, waiting for it to change to 'Succeeded' or 'Failed'.


