import os
import subprocess
import shlex
from datetime import datetime
import PyPDF2
from typing import Union
import yaml
import re
# from celery_config import app

from openai import OpenAI

# region define constants and classes

MEMORY_DIR = os.path.join(os.path.dirname(__file__), 'databases', 'memory_files')
FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), 'databases', 'feedback.txt')
VISUALIZER_BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphrag-visualizer/build'))
VISUALIZER_DIR = os.path.join(os.path.dirname(__file__), 'databases', 'visualizer')
PARAMS = {
    "model": "gpt-3.5-turbo",
}
WORD_LIMIT = 2000
OVERLAP = 100

def run_command(command, return_output=False):
    if return_output:
        res = subprocess.run(shlex.split(command), capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception(res.stderr)
        return res.stdout
    else:
        if os.system(command) != 0:
            raise Exception(f"Failed to run command: {command}")

def modify_yml(yml_path, modifications):
    with open(yml_path, 'r') as file:
        config = yaml.safe_load(file)
    for key_path, new_value in modifications.items():
        current_level = config
        for key in key_path[:-1]:
            current_level = current_level[key]
        current_level[key_path[-1]] = new_value
    with open(yml_path, 'w') as file:
        yaml.safe_dump(config, file, default_flow_style=False)


class Memory:
    def __init__(self, rootpath) -> None:
        self.rootpath = rootpath
    
    def create(self) -> None:
        '''Create a folder for the memory, and prepare all necessary files.'''
        os.makedirs(self.rootpath, exist_ok=True)
        os.makedirs(os.path.join(self.rootpath, 'input'), exist_ok=True)
        run_command(f'cp -r {os.path.join(os.path.dirname(__file__), "graphrag_init/*")} {self.rootpath}')
        run_command(f'cp -r {os.path.join(os.path.dirname(__file__), "graphrag_init/.env")} {self.rootpath}')
    
    def delete(self) -> None:
        '''Delete the memory.'''
        run_command(f'rm -r {self.rootpath}')

    def configure_focus(self, entity_type: list) -> None:
        yml_path = os.path.join(self.rootpath, 'settings.yaml')
        modify_yml(yml_path, {('entity_extraction', 'entity_types'): entity_type})

    def add(self, input_data: str, file_name: str) -> None:
        '''Add a new file to the memory.'''
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        with open(os.path.join(self.rootpath, 'input', f"{file_name}.{timestamp}.txt"), 'w') as f:
            f.write(input_data)
        if os.path.exists(os.path.join(self.rootpath, 'output/create_final_documents.parquet')):
            # update the graph
            run_command(f'graphrag update --root {self.rootpath}')
            run_command(f'rm -r {os.path.join(self.rootpath, "output")}')
            run_command(f'mv {os.path.join(self.rootpath, "update_output")} {os.path.join(self.rootpath, "output")}')
        else:
            # create the graph
            run_command(f'graphrag index --root {self.rootpath}')
        
    def query(self, input_data: str, params=PARAMS):
        '''Query the memory.'''
        input_data = input_data.replace('"', '\\"').replace("'", "\\'")
        method = ask_llm("You are a helpful assistant. You will be provided with a query, "\
                         "and will need to determine which one of the following search method is likely to be the more appropriate one: \n"\
                         "#1 Global Search : for reasoning about holistic questions about the corpus by leveraging the community summaries. \n"\
                         "#2 Local Search : for reasoning about specific entities by fanning-out to their neighbors and associated concepts, with the added context of community information. \n"\
                         "Just return the name of the appropriate method as output, without any further explanation or other information.",
                         f"query: {input_data}", params=params)
        method = 'global' if 'global' in method.lower() else 'drift'
        command = f'graphrag query --root {self.rootpath} --query "{input_data}" --method {method}'
        raw_output = run_command(command, return_output=True)
        cleaned_output = re.split(r"^SUCCESS:.*", raw_output, maxsplit=1, flags=re.MULTILINE)
        if len(cleaned_output) > 1:
            return cleaned_output[1].strip()
        else:
            return raw_output
    
    def visualize(self, visual_path) -> None:
        '''Visualize the memory.'''
        user_build_dir = os.path.join(visual_path, 'build')
        if not os.path.exists(user_build_dir):
            run_command(f'cp -r {VISUALIZER_BUILD_DIR} {visual_path}')
        run_command(f'cp {os.path.join(self.rootpath, "output/*.parquet")} {os.path.join(user_build_dir, "artifacts/")}')
        # Now visualization is prepared. Just render the page in user_build_dir.
        return

# endregion

# region helper functions

def check_filename_validity(file_name: str) -> bool:
    if any(char in file_name for char in [' ', '/', '\\', ':', ';', '*', '?', '"', '\'', '<', '>', '[', ']', '{', '}' '|']):
        return False
    return True

def check_memory_files(user_id: str, memoryFiles: list) -> bool:
    for memoryFile in memoryFiles:
        if not os.path.exists(os.path.join(MEMORY_DIR, user_id, memoryFile)):
            return False
    return True

def read_pdf(file, params: dict = PARAMS) -> str:
    pdf = PyPDF2.PdfReader(file)
    text = []
    for page in pdf.pages:
        text.append(page.extract_text())
    return '\n\n'.join(text).strip()

def ask_llm(system_prompt: str, user_prompt: str, params: dict = PARAMS) -> Union[str, Exception]:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    try:
        response = client.chat.completions.create(
            model=PARAMS['model'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        result = response.choices[0].message.content
        return result
    except Exception as e:
        return e
    
def chunk_text(text: str) -> list:
    word_list = text.split()
    if len(word_list) > WORD_LIMIT:
        return [' '.join(word_list[i:i+WORD_LIMIT]) for i in range(0, len(word_list), WORD_LIMIT-OVERLAP)]
    else:
        return [text]

def summarize_material_from_llm(input_data_list, knowledge_type=[], entity_type=[], params=PARAMS) -> str:
    chunks = [chunk for text in input_data_list for chunk in chunk_text(text)]
    summaries = [ask_llm("You are an expert assistant tasked with summarizing material ** as concisely as possible **, yet keep the ** diversity ** of information if it's mixed. "\
                         "You will be provided with the material to summarize, and two lists specifying your summary focus - "\
                         "one is for the type(s) of knowledge we want your summary to focus on, "\
                         "and the other is for the type(s) of entities of which we want your summary to focus on the relationships or any information."\
                         "If the two lists are all empty, you can summarize the material without specific focus.",

                         f"knowledge type: {knowledge_type}\nentity type: {entity_type}\ncontent to summarize:\n{chunk}", 
                         params=params) for chunk in chunks]
    if any(isinstance(summary, Exception) for summary in summaries):
        raise Exception("An error occurred in summarizing material.")
    if len(summaries) == 1:
        return summaries[0]
    final_summary = ask_llm("You are an expert assistant tasked with summarizing the summaries of a material. "\
                            "You will be provided with a list of summaries derived from contiguous sections of the material. "\
                            "You need to integrate them into a single coherent and concise summary.",
                            '\n'.join(summaries), params=params)
    if isinstance(final_summary, Exception):
        raise Exception("An error occurred in summarizing material.")
    return final_summary

# endregion

# region for Add mode
def read_input(selected_tab, input_data, file, source, params=PARAMS):
    '''Read the input data in a way depending on the selected tab. If the input data is not valid, return None.'''
    if selected_tab == 'upload':
        if file is None or not source.endswith('.txt'):
            return
        try:
            input_data = file.read().decode('utf-8')
        except:
            return
    elif selected_tab == 'material':
        if file is None or not source.endswith('.pdf'):
            return
        try:
            input_data = read_pdf(file, params)
        except:
            return
    elif selected_tab != 'type-in':
        return
    return input_data.strip()

def configure_and_summarize(input_data, selected_tab, knowledge_type, entity_type, selected_memory_list, user_id, params=PARAMS):
    '''Configure the memory and summarize the input data (only for `material`).'''
    if selected_tab != 'material':
        # no focus
        return None
    else:
        summary = summarize_material_from_llm([input_data], knowledge_type, entity_type, params)
        if knowledge_type and not entity_type:
            # decide the entity type based on the knowledge type using LLM
            res = ask_llm("You are a helpful assistant that can analyze and process text materials following the instruction: "\
                                  "Based on provided summary of a text material and the specified knowledge realm, "\
                                  "determine the most relevant types of entities that can be used to construct a knowledge graph where entities are connected throught their relationships. "\
                                  "In other words, you should consider the types of entities that are most important for representing knowledge from the material within the knowledge realm. "\
                                  "As output, you should simply return a list of entity types capitalized, spaces replaced by underscores, and separated by commas, without any further explanation or other information, as the example shown. \n\n"\
                                  "####################\n"\
                                  "Example:\n"\
                                  "####################\n"\
                                  "knowledge realm: [gene regulation, scientific conclusion]\n"\
                                  "material summary: \nThe material discusses the regulation of gene expression during cancer progression, focusing on the role of transcription factors like p53 and NF-κB. \n"\
                                  "It highlights key genes such as BRCA1 and MYC that are upregulated in response to cellular stress, as well as metabolites like ROS that influence the signaling pathways. \n"\
                                  "The summary also describes biological processes such as apoptosis and cell cycle regulation, which are disrupted in cancer, and mentions interactions with pathways like the PI3K-Akt signaling pathway.\n"\
                                  "####################\n"\
                                  "Output: \nGENE, TRANSCRIPTION_FACTOR, METABOLITE, BIOLOGICAL_PROCESS, SIGNALING_PATHWAY\n",
                                  f"knowledge realm: {knowledge_type}\nmaterial summary:\n{summary}", params=params)
            if isinstance(res, Exception):
                raise res
            entity_type = [entity.strip().replace(' ', '_').upper() for entity in res.split(',')]
        if entity_type:
            for memory in selected_memory_list:
                memory_root = os.path.join(MEMORY_DIR, user_id, memory)
                memory_obj = Memory(memory_root)
                memory_obj.configure_focus(entity_type)
    return summary

def store_input(input_data, selected_memory_list, user_id, source):
    for memory in selected_memory_list:
        Memory(os.path.join(MEMORY_DIR, user_id, memory)).add(input_data, source)
    return

# endregion

# region for Query mode

def query_memory(input_data, selected_memory_list, user_id, params=PARAMS) -> list:
    return [Memory(os.path.join(MEMORY_DIR, user_id, memory)).query(input_data, params=params) for memory in selected_memory_list]

def query_llm(text: str, params: dict = PARAMS) -> str:
    system_prompt = "You are an expert assistant tasked with providing ** concise ** information relevant to the user query yet keeping ** diversity ** of the information if it's mixed, based on your knowledge base."
    user_prompt = text
    return ask_llm(system_prompt, user_prompt, params=params)

def query_internet(text: str, params: dict = PARAMS) -> str: #TODO
    return "Unimplemented for query_internet."

# endregion
