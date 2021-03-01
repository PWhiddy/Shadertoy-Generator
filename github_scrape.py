import requests
import json
import time
import sys
from tqdm import tqdm

def get_repos(page_count, page_size, query, filter_lang, file_filter, out_path, user, token):
    repo_count = 0
    used_repos = 0
    file_count = 0
    files_checked = 0
    with open(out_path, 'a') as out_f:
        for pc in tqdm(range(page_count)):
            base_url = f'https://api.github.com/search/repositories?q={query}&page={pc+1}&per_page={page_size}'
            dat = requests.get(base_url, auth=(user, token)).json()
            # filter to only specific lang
            if 'items' in dat.keys():
                for rep in dat['items']:
                    if (rep['language'] == filter_lang):
                        matching_files, checked = get_all_matching_files(
                            rep['contents_url'][:-8], file_filter, user, token)
                        files_checked += checked
                        if len(matching_files) > 0:
                            rep['matching_files'] = matching_files
                            out_f.write(json.dumps(rep) + '\n')
                            file_count += len(rep['matching_files'])
                            used_repos += 1
                    repo_count += 1
            else:
                print(dat)
            if (pc % 5 == 0):
                tqdm.write(f'{repo_count} {filter_lang} "{query}" repos checked, {file_count} files matching "{file_filter}" in {used_repos} repos. {files_checked} total files checked')

def get_all_matching_files(path, file_filter, user, token):
    matching_files = []
    files_checked = 0
    dat = requests.get(path, auth=(user, token)).json()
    for f in dat:
        fname = f['name']
        if f['type'] == 'dir':
            matches, checked = get_all_matching_files(f'{path}/{fname}', file_filter, user, token)
            matching_files.extend(matches)
            files_checked += checked
        else:
            if fname.endswith(file_filter):
                f_text = requests.get(f['download_url'], auth=(user, token)).text
                matching_files.append({'path': f['path'], 'contents': f_text})
            files_checked += 1
    return matching_files, files_checked

if __name__ == '__main__':
    toke = sys.argv[1]
    get_repos(2000, 50, 'shader', 'GLSL', '.glsl', 'shader_files.jsonl', 'PWhiddy', toke)