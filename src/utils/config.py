import yaml

def load_config():
    config_path = "d:/1-kerja-2025/uniform-detection/config/config.yaml"
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            config['config_path'] = config_path  # Tambahkan path ke dalam config
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def get_camera_config(camera_id):
    config = load_config()
    return config['cameras'][f'camera_{camera_id}']