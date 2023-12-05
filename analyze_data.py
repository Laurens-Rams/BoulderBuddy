import json

def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def analyze_for_tips(data):
    # This function should be adapted to analyze the bone data
    # For example, you can calculate the range of motion, speed of movements, etc.
    # Here, we'll just print out some basic data
    for bone_name, movements in data.items():
        print(f"Data for {bone_name}:")
        for movement in movements:
            print(f"  Frame {movement['frame']}: Position {movement['position']}, Rotation {movement['rotation']}")

def main():
    json_file_path = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/output.json'
    data = read_json(json_file_path)
    analyze_for_tips(data)

if __name__ == "__main__":
    main()