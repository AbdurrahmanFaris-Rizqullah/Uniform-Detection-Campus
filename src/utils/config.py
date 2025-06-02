import yaml

_config_cache = None

def load_config():
    global _config_cache
    if _config_cache is not None:
        return _config_cache
        
    config_path = "d:/1-kerja-2025/uniform-detection/config/config.yaml"
    try:
        with open(config_path, 'r') as file:
            _config_cache = yaml.safe_load(file)
            _config_cache['config_path'] = config_path
            return _config_cache
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def get_camera_config(camera_id):
    config = load_config()
    return config['cameras'][f'camera_{camera_id}']