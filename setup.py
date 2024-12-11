import os
import json
from utils import VISUALIZER_BUILD_DIR, run_command
from dotenv import load_dotenv

def setup_build():
    cmd = f'cd {os.path.dirname(__file__)} && npm install && npm run build'
    try:
        run_command(cmd)
        print("🌈 Successfully built!")
    except:
        print("❌ Failed to build.")
        exit()

def setup_visualizer():
    # First, clone graphrag-visualizer
    visualizer_url = "https://github.com/noworneverev/graphrag-visualizer.git"
    visualizer_dir = os.path.abspath(os.path.join(VISUALIZER_BUILD_DIR, '../'))
    if not os.path.exists(visualizer_dir):
        print("Cloning graphrag-visualizer...")
        try:
            run_command(f'git clone {visualizer_url} {visualizer_dir}')
            print("🌈 Successfully cloned!")
        except:
            print("❌ Failed to clone graphrag-visualizer.")
            exit()
    else:
        print("🌈 Graphrag-visualizer already exists.")
    
    # Second, install dependencies for graphrag-visualizer
    print("Installing dependencies for graphrag-visualizer...")
    try:
        run_command(f'cd {visualizer_dir} && npm install')
        print("🌈 Successfully installed!")
    except:
        print("❌ Failed to install dependencies for graphrag-visualizer.")
        exit()
    
    # Third, edit files in graphrag-visualizer and run build
    if os.path.exists(VISUALIZER_BUILD_DIR):
        print("🌈 graphrag-visualizer is already built.")
    else:
        # edit graphrag-visualizer/package.json: homepage -> "."
        try:
            package_json_path = os.path.join(visualizer_dir, 'package.json')
            with open(package_json_path, 'r') as file:
                package_data = json.load(file)
            package_data['homepage'] = "."
            with open(package_json_path, 'w') as file:
                json.dump(package_data, file, indent=2)
            print("🌈 Successfully edited 1/2 files...", end='')
        except:
            print("❌ Failed to edit package.json.")
            exit()

        # edit graphrag-visualizer/src/app/components/GraphDataHandler.js: remove line 66&68
        try:
            graph_data_handler_path = os.path.join(visualizer_dir, 'src/app/components/GraphDataHandler.tsx')
            with open(graph_data_handler_path, 'r') as file:
                lines = file.readlines()
            for i in range(len(lines)-1):
                if 'loadDefaultFiles()' in lines[i+1]:
                    if 'if (process.env.NODE_ENV === "development")' in lines[i]:
                        lines[i] = lines[i].replace('if (process.env.NODE_ENV === "development")', 'if (true)')
                        break
                    elif 'if (true)' in lines[i]:
                        break
            else:
                print("❌ Failed to edit GraphDataHandler.js.")
                exit()
            with open(graph_data_handler_path, 'w') as file:
                file.writelines(lines)
            print("\r🌈 Successfully edited 2/2 files!  ")
        except:
            print("❌ Failed to edit GraphDataHandler.js.")
            exit()
        
        # `npm run build` in graphrag-visualizer
        try:
            run_command(f'cd {visualizer_dir} && npm run build')
            print("🌈 Successfully run build for graphrag-visualizer!")
        except:
            print("❌ Failed to run build for graphrag-visualizer.")
            exit()

        print("🌈 Successfully set up graphrag-visualizer!")

def setup_dotenv():
    rootdotenv = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(rootdotenv):
        print("❌ .env file not found. Please create one and include API key in it (OPENAI_API_KEY='...')")
        exit()
    graphragdotenv = os.path.join(os.path.dirname(__file__), 'graphrag_init/.env')
    if not os.path.exists(graphragdotenv):
        # GRAPHRAG_API_KEY = 
        with open(rootdotenv, 'r') as file:
            apikey = file.read().split('=')[1].strip()
        with open(graphragdotenv, 'w') as file:
            file.write(f"GRAPHRAG_API_KEY={apikey}")
    load_dotenv()
    print("🌈 Succesfully set up .env files!")

def setup():
    setup_build()
    setup_visualizer()
    setup_dotenv()
    print("🌈 Setup completed!")